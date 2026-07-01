# Player-Count Scaling & Solo / Automa Design

Two design axes the mechanic files only touch in passing, both make-or-break for a modern game: **does it work across its whole player-count range**, and **does it have a good solo mode**. A game that sings at 3 and dies at 5 — or has no 1-player option — is leaving most of its market and its review scores on the table.

---

## Part 1: Player-count scaling

The central truth: **player count changes the game's dynamics, not just its arithmetic.** Adding players changes downtime, interaction density, board contention, game length, and variance — and a count that's perfect for one of those can be broken for another. Design and test *every* supported count as if it were a different game, because experientially it is.

### What changes as player count rises
- **Downtime grows super-linearly.** More players = longer between your turns *and* often longer individual turns (more board state to read). The silent killer (SKILL.md conviction 4) scales with player count. A game that's tight at 2 can be agonizing at 5. This is the single biggest scaling risk.
- **Contention/interaction density changes.** Shared resources, action spaces, and map regions get more contested with more players. Worker placement is the canonical case: the worker-to-space ratio that's relaxed at 2 is cutthroat at 5 (`references/mechanics-worker-placement.md`). You must add spaces/resources per player or contention explodes.
- **Game length grows**, sometimes past the point of welcome. A 45-minute game at 2 can be a 2-hour slog at 5.
- **Variance and control shift.** More players between your turns = more board change you can't predict or prevent = less control, more swing. Long-horizon plans become unreliable.
- **"Take-that" and kingmaking get worse.** More players = more ganging-up, more distributed kingmaking, more pile-on (`references/mechanics-area-control.md`).

### Scaling techniques (the designer's toolkit)
- **Scale the components, not just the rules.** Add action spaces, market slots, resources, or board regions per player to hold contention and game length roughly constant. Most well-scaled euros do this (extra worker-placement spaces at higher counts).
- **Adjust the end-trigger by count.** Fewer rounds / lower point target at higher counts to hold game length.
- **Attack downtime structurally at high counts.** This is where **simultaneous action selection** (everyone decides at once), **drafting** (pick-and-pass), and **role selection with simultaneous execution** (Puerto Rico) earn their keep — they make the game *count-agnostic* on downtime. If you want to support 5–6 players well, lean on these patterns from the start; they are the proven answer.
- **The two-player problem** deserves its own attention: many interactive multiplayer games degrade at 2 (no third party to absorb conflict, kingmaking impossible but also no "gang up on the leader" self-balancing, area-majority becomes a knife fight). Common fixes: a **neutral "third player"** (dummy pieces, a neutral faction that blocks/scores), dedicated 2p rules, or simply designing the 2p mode as a distinct variant. Some games ship a separate 2p ruleset for exactly this reason.
- **Team/partnership modes** can rescue high counts (4 plays as 2v2) by cutting effective downtime and adding fellowship.
- **Modular/variable setup** can tune difficulty and length per count.

### The process implication
- **Pick your "sweet spot" count and design for it first**, then *scale outward* to the edges of your range, treating each edge as a balancing problem against the known-good center (same discipline as asymmetry, conviction 9).
- **Playtest every count, and weight the extremes** — the lowest and highest supported counts are where scaling breaks. Measure game length and downtime *by count* (`references/playtesting.md`); a count where length or downtime blows out is a count you should fix or drop.
- **It is honorable to narrow the range.** "Best at 2–4" is a better game than "supports 1–6, miserable at 6." Don't claim a count you can't make good.

---

## Part 2: Solo / Automa design

Solo play went from niche to mainstream; a good solo mode meaningfully expands a game's audience and shelf life, and during *design* a solo/bot mode is also a tireless playtester (`references/digital-implementation.md`). There are three broad approaches — pick consciously.

### The three solo archetypes
1. **Beat-your-own-score (puzzle/optimization solo).** No opponent; you play the multiplayer game against a target score or a clock. Cheapest to build; works when the game is fundamentally a personal-optimization puzzle (many engine/tableau games — Wingspan's Automa aside, the core is solitaire-friendly). Risk: feels flat if the multiplayer game's tension came *from* opponents.
2. **Scripted/automated opponent ("Automa" / bot).** A rules-driven non-player opponent that *simulates* a rival's pressure without a human brain. The dominant modern approach (Automa Factory popularized it: Scythe, Viticulture, Terraforming Mars all have acclaimed Automa decks). The design goal is to **reproduce the *pressure and presence* of an opponent — competition for resources, the ticking sense someone's racing you — without actually computing optimal play.** It fakes the *effect* of an opponent, not the opponent.
3. **Cooperative-game solo.** Co-op games are often naturally solo-able (you control one or more characters against the game's threat system). The threat engine *is* the opponent already; solo is just playing all the heroes (or one, at higher difficulty). Pandemic, Spirit Island, Gloomhaven solo well for this reason.

### Automa design principles (the hard one)
A good Automa is a *magic trick*: it must *feel* like a rival while being cheap to run and not requiring the solo player to play both sides honestly.
- **Simulate pressure, not cognition.** The bot doesn't need good decisions; it needs to *contest the things that matter* — take the resources/spaces/cards you wanted, advance toward the win condition at a credible pace, and create the "I need to hurry" feeling. Players forgive a bot that plays "wrong" far more than one that applies no pressure.
- **Low upkeep is non-negotiable.** Every second the solo player spends *running the bot* is friction with no payoff. Drive the Automa from a simple deck/dice/flowchart, not a decision tree the human must adjudicate. Card-driven Automas (flip a card → do exactly what it says) are the gold standard: no judgment calls, fast, opaque enough to feel alive.
- **Difficulty knobs.** Solo players want a ladder — tune the bot's speed/aggression/bonuses, not its (nonexistent) intelligence. Provide several clearly-labeled difficulty levels.
- **Avoid "play both sides honestly" traps.** If the solo player must make good decisions *for the bot*, immersion and challenge both collapse (you can't surprise yourself). The bot's behavior must be externally determined (cards/dice), not played by the human.
- **Hidden-ish behavior helps.** A bot whose next action is somewhat unpredictable (driven by a shuffled deck) recreates the uncertainty of a real opponent; a fully-deterministic bot gets "solved" and goes stale.

### Digital changes the solo calculus
This is a strong argument for digital-first when solo matters: digitally, the "Automa" can be an actual AI (MCTS/heuristic bot from `references/digital-implementation.md`) that genuinely plays, with **zero upkeep cost to the player** — the computer runs it. The painful part of physical solo design (low-friction bot operation) evaporates. A digital build can offer real AI opponents at multiple strengths for free off the same rules engine; the physical version then needs the card-driven Automa as its lower-fidelity stand-in. Designing digital-first lets you prototype solo viability immediately and decide whether a physical Automa is worth the considerable design effort.

### Process implication
- If solo is a goal, **decide the archetype in Phase 3** (it shapes the rules), and **prototype it digitally early** — the bot you build to playtest (`references/digital-implementation.md`) is the seed of your solo mode.
- Solo-test the same way you multiplayer-test: is the decision live? is there pressure? is the difficulty ladder real? A solo mode with no pressure or one dominant line is as broken as a multiplayer game with a dominant strategy.
