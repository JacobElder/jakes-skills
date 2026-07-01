# Digital Implementation

This is the technical spine of the skill: how to build the digital game so that (a) it's clean to iterate, (b) you get simulation and bots for free, and (c) it sets up a smooth physical transition rather than fighting it.

## The one rule: separate the rules engine from presentation

Model the game as a **pure state-transition function**: `reducer(state, move) → newState`, with `move` validated against `state` by a `isLegal(state, move)` predicate. The reducer has **no UI, no randomness side-effects** (inject the RNG), and **no I/O**. Everything the game *is* lives here; everything the player *sees* lives in a separate presentation layer that reads state and dispatches moves.

Why this matters more than it looks:
- **Testability:** you assert on `(state, move) → newState` directly. No clicking.
- **Determinism & replay:** given a seed and a move list, you reproduce any game exactly — essential for debugging "what happened on turn 14" and for replay/animation later.
- **Free simulation:** the same reducer that runs the game runs ten thousand simulated games (see `balance-and-simulation.md` and `scripts/balance_sim.py`).
- **Free bots:** a bot is just a function `state → move`. Plug it into the same engine.
- **The physical rulebook falls out of it.** A correct reducer is the *formal specification* of the rules. The English rulebook is a faithful natural-language rendering of `isLegal` + the turn/phase structure + the end condition. Build the reducer first and the rulebook can never silently disagree with the game.

If you take one thing from this skill for a digital build, it's this separation. It is cheap to adopt on day one and expensive to retrofit.

## Default stack: boardgame.io (turn-based)

For turn-based board/card games, **boardgame.io** (TypeScript/JavaScript, MIT-licensed) is the recommended default. You "translate the rules of a game to a series of simple functions that describe how the game state changes when a move is made," and it provides — without you writing networking or storage:

- **State management** synced across clients/server/storage.
- **Multiplayer** in real time.
- **Bots** (random + MCTS) generated from your move definitions — instant tireless playtesters.
- **Game phases & turns** with per-phase rules and custom turn orders (incl. simultaneous turns — the anti-downtime pattern from several mechanic files).
- **Secret state** via `playerView` — hide opponents' hands/decks from each client (do this server-side for anything competitive).
- **A prototyping/debug panel** to fire moves and inspect/time-travel state before any UI exists.
- **View-layer agnostic:** plain JS, React, or React Native bindings.

Minimal shape (see `assets/boardgame_io_template/` for the full commented skeleton):

```js
const Game = {
  setup: (ctx) => ({ /* initial G: decks, board, player areas */ }),
  moves: {
    playCard: ({ G, ctx, playerID }, cardId) => {
      // validate; mutate a draft of G (immer under the hood); illegal → return INVALID_MOVE
    },
  },
  turn: { order: /* ... */ },
  phases: { /* draft phase, action phase, ... */ },
  endIf: ({ G, ctx }) => { /* return winner / draw when end condition met */ },
  playerView: PlayerView.STRIP_SECRETS, // hide hidden state per player
  ai: { enumerate: (G, ctx) => /* list legal moves for the bot */ },
};
```

The `ai.enumerate` function is doing double duty: it powers the built-in bot **and** documents your legal-move space (which is exactly your `isLegal` predicate and the seed of your rulebook's "on your turn you may…" section).

### When *not* to use boardgame.io
- **Real-time / dexterity / heavy animation** games: boardgame.io is turn-based at heart. Keep the *rules core* as a pure module anyway, and drive a richer client.
- **You want a console/Steam/mobile presentation** with juice (animation, sound, particle feedback — which matters enormously for push-your-luck reveals, etc.): build the rules engine as a portable pure module and render it in **Godot, Unity, or LÖVE** (the user's indie-game-dev skill covers this layer). The discipline is identical — the engine stays pure; the game framework is *only* presentation + input. A push-your-luck or legacy game especially benefits from a juicy client over the same clean engine.

## Modeling state well

- **Single source of truth.** All game state in one serializable object (`G`). No state hiding in the UI. Serializable = saveable = the persistence you need for campaign/legacy for free.
- **Separate persistent from per-session state** (campaign/legacy): a durable profile (unlocks, party, flags) vs. the current game's `G`. Scenarios are *data* gated by flags.
- **Data-drive your content.** Cards, action spaces, tiles, faction powers → data (JSON/objects with declarative effects), not bespoke functions. This lets you retune by editing data, lets `balance_sim.py` enumerate content, and lets non-coders contribute to balance. Bespoke per-card code is a balancing tar pit.
- **Make effect resolution order explicit.** Cascading triggers (engine builders!) need a defined order or you get nondeterministic, un-debuggable rules. Declare it.
- **Inject randomness.** Use boardgame.io's `random` API (or a seeded RNG you pass in) — never `Math.random()` in the reducer — so games are reproducible and server-authoritative.

## Hidden information & cheating
For competitive multiplayer, the server is authoritative and `playerView` strips secrets per client — a client must never receive data it could use to cheat (opponent hands, deck order). This is *easier and more reliable digitally than physically* (no accidental card flashing), and it's one place the digital version is strictly fairer. Design your state so secrets are cleanly separable (a `secret` sub-object) from day one.

## Bots as first-class development tools
A `state → move` bot is the highest-leverage testing asset you'll build:
- A **random-legal** bot flushes out crashes, illegal-state bugs, and softlocks (run thousands of games headless).
- A **greedy** bot (maximize immediate value) exposes dominant strategies and dominant spots/cards — if greedy-one-strategy wins disproportionately, you have a design hole, not a bot.
- **MCTS / heuristic** bots approximate decent play for first-pass balance and as single-player opponents.
- Bots can't tell you if the game is *fun* — that's still humans (`playtesting.md`) — but they're unmatched for correctness and gross-imbalance detection.

## What digital *uniquely* enables (not just "physical, faster")

Most of this file frames digital as a cleaner path to iterate and simulate a game that could be physical. But digital board games can do things physical fundamentally *cannot*, and treating digital as merely "physical with instant setup" leaves the medium's real power unused. When you're building digital-first, ask which of these your design should actively exploit:

- **Hidden information and fog of war, for free and perfectly.** The screen enforces secrecy with zero ergonomics cost — no screens, no accidental flashing, no "everyone close your eyes." This makes whole genres better digitally (hidden movement, simultaneous secret orders, traitor games) and enables information structures impractical physically (true fog of war, per-player asymmetric info at scale, simultaneous hidden programming with instant reveal).
- **Heavy/continuous upkeep and fiddly bookkeeping become invisible.** The exact thing that kills engine games and legacy games physically (passive per-turn triggers, complex scoring, resource cascades) is *free* digitally. This means digital can support **deeper, more interconnected systems** than a physical game could ask humans to maintain — a real expansion of the design space, not just a convenience.
- **Real-time, timers, and dexterity** layered onto turn-based structures (action queues, simultaneous real-time phases, pressure timers) that are clumsy or impossible on a table.
- **Asynchronous and remote play.** Play-by-cloud over days, matchmaking with strangers, cross-table play — community structures physical can't offer. This changes *what kind of game* makes sense (bite-sized async turns vs. one long session).
- **Dynamic difficulty and adaptive content.** The system can scale challenge to the player in real time, generate/seed content procedurally, and personalize — impossible with static physical components. (Relates to solo/Automa design — `references/scaling-and-solo.md`.)
- **Persistent and evolving worlds.** Save state makes campaign/legacy trivially persistent *and* resettable (`references/mechanics-campaign-legacy.md`), and enables living/seasonal content, leaderboards, and meta-progression a box can't hold.
- **Content volume and variability** beyond what fits (and what humans can shuffle/manage) in a physical box — huge card pools, deep variant trees, frequent updates/patches.
- **The AI opponent as a player-facing *feature*, not just a test tool.** Elsewhere in this file bots are framed as playtesters; digitally they're also the product — single-player and fill-in opponents at multiple strengths, available instantly, off the same rules engine. For many digital board games this is the headline reason to play digitally at all.

The flip side — digital realities physical doesn't have — is also worth naming so you design for them: **onboarding/tutorial is make-or-break** (`references/onboarding-and-teaching.md`); **the UI now carries teaching, legibility, and game-feel** (animation/sound do real emotional work — `references/experience-and-aesthetics.md`, Sensation); and **distribution/monetization/platform** (storefronts, updates, multiplayer servers, monetization model) become design-adjacent concerns a physical designer never faces. A digital board game is a *software product*, with that genre's obligations, not just a board game on a screen.

The design judgment: if your game's appeal depends on table talk, tactile bits, or social presence in a room (negotiation, party, dexterity, the haptics of push-your-luck), physical may be the better medium and digital is mainly for *iteration and simulation* (`references/physical-transition.md`, "when physical should lead"). If your appeal depends on hidden info, heavy systems, async play, persistent worlds, or AI opponents, digital isn't a stepping-stone to physical — it's the destination, and you should design *for* what only it can do.

## The path that keeps physical open
Build in this order and physical stays cheap to reach: **pure rules engine → headless tests + sim + bots → minimal debug UI → playable thin client → (only now) juicy presentation**. Because the engine is pure and the content is data, the eventual rulebook is a transcription job, not a reverse-engineering project. See `physical-transition.md`.
