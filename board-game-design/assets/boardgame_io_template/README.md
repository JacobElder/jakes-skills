# boardgame.io game-logic template

A minimal, heavily-commented **rules engine** (`game.js`) showing the patterns that matter for board game design — pure moves, phases/turns, simultaneous actions, hidden information, injected RNG, an end condition, and bot enumeration. The toy game ("Gem Grab": draft → set collection) exists only to demonstrate the wiring. **Replace the rules; keep the structure.**

## Why this structure
`game.js` is a pure `(G, ctx, move) → G'` state machine with **no UI**. That separation is the whole point (see `references/digital-implementation.md`):
- it's directly testable and reproducible,
- the same engine runs your game, your simulations, and your bots,
- `ai.enumerate` simultaneously powers the bot and documents your legal-move space — the seed of your physical rulebook.

## Setup
```bash
npm init -y
npm install boardgame.io
# (ESM) ensure "type": "module" in package.json, or use a bundler/ts-node
```

## Play it locally with a UI
boardgame.io ships React bindings and a Debug Panel. A minimal client:
```js
import { Client } from 'boardgame.io/react';
import { GemGrab } from './game.js';
const App = Client({ game: GemGrab });   // renders with the built-in Debug Panel
export default App;
```
The Debug Panel lets you fire moves and time-travel state **before you build any real UI** — start here.

## Headless self-play for correctness + gross balance
The highest-leverage testing you can do early: drive the engine with bots, no UI, thousands of games, to flush crashes/softlocks and expose dominant lines.

**Reality check from testing this template (boardgame.io 0.50.2):** driving a game that uses **simultaneous turns** (`activePlayers`) with the built-in `RandomBot` is fiddly — you must dispatch a move for *each* active player each step, not just `currentPlayer`, and the client-side bot loop doesn't do that for you. Two robust options:

1. **Easiest: make the loop you test sequential.** For headless balance runs, a sequential turn model drives cleanly:
   ```js
   import { Client } from 'boardgame.io/client';
   import { RandomBot } from 'boardgame.io/ai';
   import { GemGrab } from './game.js';

   async function playOne(seed) {
     const client = Client({ game: GemGrab, numPlayers: 3, seed });
     client.start();
     const bots = Object.fromEntries(['0','1','2'].map(p =>
       [p, new RandomBot({ enumerate: GemGrab.ai.enumerate, seed, playerID: p })]));
     let guard = 0;
     while (!client.getState().ctx.gameover && guard++ < 5000) {
       const s = client.getState();
       const p = s.ctx.currentPlayer;
       const { action } = await bots[p].play(s, p);
       if (!action) break;                       // no legal move
       client.moves[action.payload.type](...(action.payload.args || []));
     }
     return client.getState().ctx.gameover;       // { winner } or undefined
   }
   ```
2. **Keep simultaneous turns** (the anti-downtime pattern is worth it) but, for the headless harness, loop over `Object.keys(ctx.activePlayers)` and dispatch each player's bot move before re-reading state. Expect to consult the boardgame.io "Bots" + "Simultaneous Moves" docs — this is the one place the API friction is real.

Either way, aggregate `gameover.winner` across thousands of seeds → **win-rate by seat** (structural first-player advantage) and, by swapping in greedy bots, **win-rate by strategy** (dominant-line detection). Pair with `scripts/balance_sim.py` for the closed-form subsystem questions. Remember: bots reveal *mechanical* dominance, not fun or human-meta balance — that's playtesting (`references/playtesting.md`).

> **Tested gotcha baked into `game.js`:** the draft phase's `endIf` guards `G.market.length > 0` because `[].every()` returns `true` and would otherwise skip the phase before the market is dealt. Watch for empty-collection `.every()`/`.some()` traps in your own `endIf`s.

## Transition notes
Because the engine is pure and content is data, your rulebook is a transcription of `setup` + the phase/turn structure + `ai.enumerate` (legal moves) + `endIf` (game over). See `references/physical-transition.md` for converting the engine's invisible work (shuffling, hidden info, legality, scoring) into human-ergonomic physical apparatus.
