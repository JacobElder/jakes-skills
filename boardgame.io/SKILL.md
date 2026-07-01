---
name: boardgame-io
description: Build, wire, and test turn-based games with boardgame.io 0.50.x (the `boardgame.io` npm package). Use when a developer is prototyping a turn-based or card/board game in the browser or Node and hits framework-specific traps — moves silently doing nothing, dice/shuffle returning undefined, INVALID_MOVE not rejecting a move, phases hiding moves, simultaneous play that never ends, a bot with no moves to try, or "how do I unit-test game logic without a DOM." Covers the 0.50.x move signature (a single `{ G, ctx, random, events, log, playerID }` context object), Immer-by-default state, the random/events plugin APIs, phases/turns/stages, Client-vs-Server wiring, MCTSBot/RandomBot enumerate, and headless testing. Not for general board-game design theory, Godot/Unity/Phaser, React UI beyond minimal wiring, or 0.39.x→0.50 migration.
---

# boardgame.io 0.50.x

Target: `boardgame.io@0.50.2` (one npm package named `boardgame.io`, with subpath exports). There is **no** `@boardgame.io/core` scoped package. Imports come from subpaths:

```
boardgame.io/core         INVALID_MOVE, Stage, TurnOrder, ActivePlayers, PlayerView
boardgame.io/client       Client (vanilla), LobbyClient
boardgame.io/react        Client (React HOC), Lobby
boardgame.io/server       Server, Origins, SocketIO, FlatFile
boardgame.io/ai           MCTSBot, RandomBot, Simulate, Step, Bot
boardgame.io/multiplayer  Local, SocketIO   (client transports)
boardgame.io/internal     InitializeGame, CreateGameReducer  (headless tooling)
```

## The core model

A game is a definition object. The whole runtime is a pure, deterministic reducer over `G`:

- **`G`** — your game state. You own it. It persists across turns. Put everything game-relevant here.
- **`ctx`** — framework-managed context (`currentPlayer`, `turn`, `phase`, `numPlayers`, `activePlayers`, `gameover`, …). **Read-only to you. Reset/managed by the framework.** Never store your own persistent data here.
- **moves / hooks** — pure functions of a single **context object**.

### The 0.50.x function signature (this is the #1 thing the base model gets wrong)

Every move and hook receives **one object** whose members include `G`, `ctx`, and the plugin APIs `random`, `events`, `log` at the **top level** — *not* under `ctx`.

```js
// CORRECT (0.50.x)
moves: {
  playCard: ({ G, ctx, random, events, playerID }, cardId) => { /* ... */ },
}

// WRONG — the pre-0.45 API the base model defaults to. ctx.random / ctx.events are undefined here.
moves: {
  playCard: (G, ctx, cardId) => { G.foo = ctx.random.D6(); }  // crashes / undefined
}
```

If a move's first parameter is `G` instead of `{ G }`, everything downstream is wrong. Destructure the context object. (Writing the game in TypeScript? See `references/typescript.md`.)

---

## Section 1 — The pitfalls

Each: the plausible-but-wrong version the base model emits, then the fix and *why*. All snippets are verified against 0.50.2.

### 1. `random` is a top-level plugin arg — `ctx.random` is `undefined`

The random plugin is **on by default**. There is **no `randomMethod` config key** — do not add one. `random.D6()`, `random.Die(n)`, `random.Shuffle(arr)`, `random.Number()` all work out of the box.

```js
// WRONG — ctx.random does not exist in 0.50.x → undefined → crash
moves: { roll: (G, ctx) => { G.roll = ctx.random.D6(); } }

// CORRECT — random is a top-level member of the context object
moves: { roll: ({ G, random }) => { G.roll = random.D6(); } }
```

Why: in 0.50.x randomness is a plugin surfaced on the context object, not a field of `ctx`. The base model's "tests pass but values are undefined" symptom comes from reading `ctx.random` (undefined), not from a missing config.

### 2. `INVALID_MOVE` must be imported and **returned** (not thrown, not undefined)

```js
import { INVALID_MOVE } from 'boardgame.io/core';

// WRONG — throwing crashes the reducer; returning undefined just commits a no-op (or commits partial mutations)
moves: { claim: ({ G }, i) => { if (G.cells[i]) throw new Error('taken'); /* ... */ } }

// CORRECT — return the sentinel; the framework rejects the move and rolls back
moves: { claim: ({ G, ctx }, i) => {
  if (G.cells[i] !== null) return INVALID_MOVE;
  G.cells[i] = ctx.currentPlayer;
} }
```

Why: `INVALID_MOVE` is the only signal that rejects a move and rolls back its mutations. Returning `undefined` is a legal no-op (it commits whatever you mutated), so an illegal move guarded by `return;` silently corrupts the board. `INVALID_MOVE` is exported from `boardgame.io/core` only (not `/client`).

### 3. A phase's `moves` **replace** the global `moves` for that phase

```js
const game = {
  moves: { draw: ({ G }) => { /* ... */ } },         // global
  phases: {
    play: { start: true, moves: { discard: ({ G }) => { /* ... */ } } },
  },
};
// During phase 'play', calling moves.draw() → runtime error "disallowed move: draw".
// Only 'discard' is callable. Global moves do NOT merge in.
```

Fix: re-declare any move you still need inside the phase's `moves`, **or omit the phase's `moves` key entirely** (a phase with no `moves` inherits the globals), **or** avoid phases and use `turn: { minMoves, maxMoves }` + `endIf` for simple turn structure.

### 4. Immer is the **default** — mutate *or* return, never both

The default is Immer-backed mutation. There is **no `immer: true` config key**. Both styles work:

```js
moves: {
  inc: ({ G }) => { G.count += 1; },               // mutate (no return) — OK
  inc2: ({ G }) => ({ ...G, count: G.count + 1 }), // return new state — also OK
}
```

The real trap — doing **both** in one move throws:

```js
// WRONG → Immer: "An immer producer returned a new value *and* modified its draft."
moves: { bad: ({ G }) => { G.count += 1; return { count: 99 }; } }
```

Fix: pick one style per move. Mutating the draft and returning a brand-new object is the error; mutate-with-no-return is the idiomatic default.

### 5. `events` is a top-level plugin arg, available **only inside moves/hooks**

```js
// WRONG — ctx.events does not exist
moves: { go: ({ G, ctx }) => { ctx.events.endTurn(); } }

// CORRECT
moves: { go: ({ G, events }) => { /* mutate G */ events.endTurn(); } }
```

`events.endTurn()`, `events.endPhase()`, `events.endGame(gameoverValue)`, `events.setActivePlayers(...)`, `events.endStage()` are all here. They are **not** available in `endIf` (see #6).

### 6. `endIf` is a pure predicate — it returns a value, it does not call `events`

```js
// WRONG — endIf must not drive events; it just reports whether the game is over
endIf: ({ G, ctx, events }) => { if (won(G)) events.endGame(); }

// CORRECT — return the gameover value; the framework ends the game
endIf: ({ G, ctx }) => { if (won(G)) return { winner: ctx.currentPlayer }; }
```

**Winner shape matters.** Whatever `endIf` returns becomes `ctx.gameover`:

```js
return { winner: '0' };  // ctx.gameover === { winner: '0' }
return { draw: true };   // ctx.gameover === { draw: true }
return true;             // ctx.gameover === true  (game ends, but no winner info)
```

Returning bare `true` ends the game but leaves you with no winner to display. Return the object you actually want in `ctx.gameover`. The same applies to `phase.endIf` (return `{ next: 'phaseName' }` to route) and `turn.endIf` (return `true`/`{ next: playerID }`).

### 7. Simultaneous play needs `activePlayers` **plus** stage definitions

`activePlayers: { all: Stage.NULL }` makes everyone active but gives them no stage-scoped moves and no per-stage exit. Use named stages with `minMoves`/`maxMoves` so the simultaneous window actually ends:

```js
import { Stage } from 'boardgame.io/core';

turn: {
  activePlayers: { all: 'pick', minMoves: 1, maxMoves: 1 },
  stages: {
    pick: { moves: { choose: ({ G, playerID }, x) => { G.picks[playerID] = x; } } },
  },
},
// With maxMoves:1 in the stage, each player's stage auto-completes after one move;
// when all active players finish, the turn advances. To end early/conditionally,
// call events.setActivePlayers(...) or events.endStage() from inside a move.
```

`Stage.NULL` (=== `null`) means "active, but in no named stage" — players fall back to the current phase's moves. Reach for a named stage whenever the simultaneous moves differ from the normal turn moves.

### Also true, frequently missed

- **`moveLimit` is deprecated** → use `turn: { minMoves, maxMoves }`. With `maxMoves: 1` the turn auto-ends after one move; do **not** also call `events.endTurn()` (double-ends / errors). For non-default turn order (reverse, fixed seating, one-turn drafts), see `references/turn-order.md`.
- **Persistent state lives in `G`, never `ctx`.** Anything you write onto `ctx` is ignored/overwritten by the framework.
- **Moves and hooks must be deterministic** — no `Date.now()`, `Math.random()`, `fetch()`, or other side effects. They break replay, undo, and multiplayer sync. Use the `random` plugin for chance; pass timestamps in as move args from the UI if you need them.
- **A hook (`onBegin`/`onEnd`/`onMove`) that *returns* a value replaces `G` with it.** An arrow body like `onBegin: ({ G }) => (G.round += 1)` returns a number and wipes your state. Use a block body and return nothing. Hook firing order and undo constraints are in `references/flow-lifecycle.md`.
- **`setup` vs `onBegin`.** Put initial randomized state (shuffled deck, starting hands) in `setup({ ctx, random }) => G`. `random` is also available in `turn.onBegin`/`phase.onBegin`, so use hooks for per-turn/per-phase setup. (Note: `setup` receives the context *without* `G` — it returns `G`.)

---

## Section 2 — Client vs Server wiring

The **Client** (browser/Node bundle, manages local state + transport) and the **Server** (Node process, authoritative state for networked play) are **separate imports and separate processes**. Server config never goes inside `Client()`.

```js
// --- Local single-player: Client alone, no server needed ---
import { Client } from 'boardgame.io/client';
const client = Client({ game: MyGame, numPlayers: 1 });
client.start();
client.moves.someMove();

// --- Two players on one device (hotseat) ---
import { Local } from 'boardgame.io/multiplayer';
const client = Client({ game: MyGame, numPlayers: 2, multiplayer: Local() });

// --- Networked multiplayer: client points at a server ---
import { SocketIO } from 'boardgame.io/multiplayer';
const client = Client({
  game: MyGame,
  multiplayer: SocketIO({ server: 'localhost:8000' }),
  playerID: '0',   // which seat THIS client controls
});
```

In networked play each client must be told its `playerID` (the seat it controls); a client with no `playerID` is a spectator and the authoritative server won't accept moves from it. In a real app you derive `playerID` (and credentials) from your lobby/login, not a hard-coded string.

```js
// server.js — a SEPARATE Node process
import { Server, Origins } from 'boardgame.io/server';
import { MyGame } from './game';
const server = Server({
  games: [MyGame],
  origins: [Origins.LOCALHOST],
});
server.run(8000);
```

React UI uses the HOC client: `import { Client } from 'boardgame.io/react'` and pass a `board` component. That is the boundary of UI coverage here. For networked lobbies, match creation/joining, and server-side persistence, see `references/lobby-and-server.md`.

---

## Section 3 — Bots

`MCTSBot` and `RandomBot` come from `boardgame.io/ai`. A bot needs to know the legal moves, supplied by an **`enumerate` function**.

**Quirk:** `enumerate` uses the **old positional** signature `(G, ctx, playerID)` — *not* the context-object signature that moves use. It returns `[{ move, args }, ...]` (or `{ event, args }`).

```js
const game = {
  // ...moves, endIf...
  ai: {
    enumerate: (G, ctx) =>            // positional! (G, ctx, playerID)
      G.cells.map((c, i) => (c === null ? { move: 'click', args: [i] } : null))
             .filter(Boolean),
  },
};
```

- **`RandomBot`** picks uniformly among enumerated moves. No objective needed. Good default for smoke-testing balance and for weak opponents.
- **`MCTSBot`** searches. Worth the complexity only when the game has real tactical depth and you want a competent opponent; tune `iterations`/`playoutDepth`. For most prototypes, start with `RandomBot`.

```js
import { MCTSBot, RandomBot, Simulate } from 'boardgame.io/ai';
import { InitializeGame } from 'boardgame.io/internal';

const state = InitializeGame({ game, numPlayers: 2 });
const { state: final } = await Simulate({
  game,
  bots: { '0': new MCTSBot({ game, enumerate: game.ai.enumerate, iterations: 200 }),
          '1': new RandomBot({ enumerate: game.ai.enumerate }) },
  state,
});
// final.ctx.gameover → { winner: ... }
```

`Simulate({ game, bots, state })` requires an explicit starting `state` (use `InitializeGame`) and returns a `Promise<{ state, metadata }>`.

---

## Section 4 — Testing (the biggest practical payoff)

boardgame.io games are pure reducers, so **logic tests need no browser/DOM**. The base model's instinct ("mock the DOM", "use jsdom", "render the board") is wrong. Drive the headless `Client` in Node:

```js
import { Client } from 'boardgame.io/client';
import { MyGame } from './game';

test('claiming an occupied cell is rejected', () => {
  const client = Client({ game: MyGame, numPlayers: 2 });
  client.moves.click(0);
  client.moves.click(0);                 // second claim on same cell
  expect(client.getState().G.cells[0]).toBe('0');   // unchanged
});

test('three in a row wins', () => {
  const client = Client({ game: MyGame, numPlayers: 2 });
  [0, 3, 1, 4, 2].forEach((i) => client.moves.click(i));
  expect(client.getState().ctx.gameover).toEqual({ winner: '0' });
});
```

`client.getState()` exposes `{ G, ctx, ... }`. Read `G` for your state and `ctx.gameover`, `ctx.currentPlayer`, `ctx.phase` for flow assertions. For lower-level tests, `InitializeGame` + `CreateGameReducer` from `boardgame.io/internal` let you dispatch actions directly. `boardgame.io/testing` exports only `MockRandom` (for forcing deterministic dice in a test); it is not a full harness.

For interactive debugging during development, the React `Client` renders a **debug panel** by default (`debug: true|false` to toggle) that lets you fire moves/events and inspect `G`/`ctx` live. The bundled `scripts/smoke-test.js` is the fastest way to confirm the framework itself behaves as documented in the installed version.

---

## Section 5 — Hidden information (card games)

Every connected client receives the **full** `G` unless you filter it. So "the other player can see my hand" is not a UI bug — the secret data is actually on their client. Filter it server-side with `playerView`.

The built-in `PlayerView.STRIP_SECRETS` enforces a convention (verified against 0.50.2):

- `G.secret` — stripped from **every** client (deck contents, unrevealed cards).
- `G.players[playerID]` — each client keeps only **its own** entry; other players' entries are removed.
- everything else stays public.

```js
import { PlayerView } from 'boardgame.io/core';

const game = {
  setup: () => ({
    secret: { deck: shuffledDeck() },          // hidden from all clients
    players: { '0': { hand: [] }, '1': { hand: [] } }, // each player sees only their own
    discard: [],                               // public
  }),
  playerView: PlayerView.STRIP_SECRETS,
  // ...
};
// Player '0' receives: { players: { '0': {...} }, discard: [...] }  — no `secret`, no players['1'].
```

A custom view is just a function: `playerView: ({ G, ctx, playerID }) => filteredG`.

**Hide move arguments too.** `playerView` filters `G`, but the move *log* still shows what each player did, including the args (e.g. which card they played face-down). Mark such a move `redact: true` (long-form) so its args are stripped from the log sent to other players:

```js
moves: { playFaceDown: { move: ({ G, playerID }, cardId) => { /* ... */ }, redact: true } }
```

**Pair secret state with `client: false` moves.** A move that reads `G.secret` or uses `random` can't be reproduced by the optimistic client (it doesn't have the secret, and would roll different dice). Mark such moves server-authoritative so they don't run optimistically and flicker:

```js
moves: {
  draw: {                                   // long-form move
    move: ({ G, playerID, random }) => {
      const card = G.secret.deck.pop();     // client can't see this
      G.players[playerID].hand.push(card);
    },
    client: false,                          // run only on the authoritative server
  },
}
```

## Section 6 — Scope boundary

This skill covers **boardgame.io 0.50.x** (`boardgame.io` npm package, client + server + ai). It does **not** cover:

- General board-game design (mechanics, balance philosophy, MDA) → that is a separate design concern.
- Godot / Unity / Unreal / Phaser / Kaboom / Three.js → different engines.
- React/Svelte UI beyond the minimal Client wiring above.
- Persistence/saving game state, accounts, matchmaking internals → server-side database concerns (the `Server` `db` adapters like `FlatFile`) are out of scope here beyond noting they exist.
- 0.39.x → 0.50 migration guides or version history.

---

## Common errors → cause

These exact messages/symptoms map to specific causes (the base model rarely connects them):

| Symptom / message | Cause | Fix |
|---|---|---|
| `disallowed move: X` | Move X isn't available in the current phase/stage (a phase defined its own `moves`, or the player is in a stage without X). | Re-declare X in the phase/stage `moves`, omit the phase `moves` to inherit globals, or check `activePlayers`. |
| `invalid move: X` (logged) | The move returned `INVALID_MOVE`. | Expected when a guard rejects an illegal move — not a bug. |
| `An immer producer returned a new value *and* modified its draft.` | A move/hook both mutated the draft and returned a new object. | One style per function: mutate (no return) **or** return new state. |
| Dice/shuffle is `undefined`; `G.foo` undefined in a move | Old `(G, ctx)` signature, or reading `ctx.random` / `ctx.events`. | Destructure the single context object: `({ G, random, events })`. |
| `G` becomes a number/string/garbage | A hook returned a value, replacing `G`. | Use a block body in hooks and return nothing (see `references/flow-lifecycle.md`). |
| Move "works" locally but is rejected online | Multiplayer client missing `playerID`/`credentials`, or a `random`/secret move ran optimistically. | Pass `playerID` (+ `credentials`); mark such moves `client: false`. |
| `No moves to undo` | `undo()` was called across a turn boundary. | Undo only reverts within the current turn. |

## Verify against the installed version

The bundled `scripts/smoke-test.js` asserts every behavior above against the project's actual installed boardgame.io (zero extra deps):

```
node scripts/smoke-test.js
```

A `FAIL` means the installed version differs from what this skill assumes — trust the failure and re-verify that pattern before relying on it.

## References

Load these only when the task calls for them:

- **`references/typescript.md`** — typing the game in TypeScript (`Game<G>`, `Move<G>`, the context type) and the required `skipLibCheck: true` tsconfig gotcha.
- **`references/turn-order.md`** — non-default turn order: built-in `TurnOrder` values (`RESET`/`CONTINUE`/`ONCE`), fixed/custom seating (`CUSTOM`/`CUSTOM_FROM`), and fully custom `first`/`next` order objects.
- **`references/flow-lifecycle.md`** — hook execution order, the hook-return-replaces-`G` gotcha, `onMove`, and undo/redo constraints.
- **`references/lobby-and-server.md`** — networked matches: `Server` config, persistence/DB adapters, the `LobbyClient` REST API and credential flow, and the React `Lobby`.

## Uncertainty note

The API facts above were verified by installing `boardgame.io@0.50.2` and running each pattern. If you are on a different 0.50.x patch and a signature differs, trust the installed package's `dist/types/src/types.d.ts` over this document, and confirm by running a one-line headless `Client` test rather than assuming.
