# Worker Placement & Action Selection

**The experience:** a tense competition for a shared menu of actions where the best spots are scarce, and *getting there first* matters as much as what you do.

**Central decision:** take the action I want most (risking it's gone next time / signaling my plan) vs. grab the action an opponent needs (denial) vs. take a safe action no one contests. Worker placement is fundamentally **action drafting under blocking**.

## How it works
Players take turns placing limited tokens ("workers," classically meeples) onto action spaces; occupying a space triggers its action and usually **blocks** others from using it that round. Workers return at round end. The scarcity of good spaces + turn order is the whole game. Agricola, Caylus, Lords of Waterdeep, Viticulture, Stone Age, Le Havre, Tzolk'in, Everdell.

## Design levers
- **Worker count vs. space count.** The ratio of total workers to good spaces sets the *contention temperature*. Plenty of good spaces → low conflict, relaxed (multiplayer-solitaire risk). Scarce good spaces → cutthroat, high tension, high downtime risk. This single ratio is your most important dial; tune it explicitly per player count (more players = you must add spaces or contention explodes).
- **Blocking model.** Hard block (space fully occupied, classic) vs. soft block (space stays open but costs more / yields less to later users, e.g., Caylus, Tzolk'in's escalating cost). Soft blocking reduces feel-bad and "I got nothing" turns.
- **Worker differentiation.** Plain workers (all identical) vs. typed/valued workers (Bora Bora's dice-workers, where the *value* you place gates which actions you can take). Typed workers add a layer of input-randomness decisions.
- **First-player advantage** is structural here (first placer gets first pick). Make the turn-order marker itself a contested resource, or rotate it, or attach a compensation to going late.
- **Catch-up via placement order.** A clean, non-controversial catch-up lever: let the trailing player place first, or get a free extra worker — this is *opportunity*, not handed points, so it dodges the catch-up controversy.
- **The "you must place all workers" vs. "pass anytime" choice** governs commitment and bluffing.

## Balance math
- **Space ROI parity.** Each action space has a value (resources/points per worker). Compute value-per-worker across all spaces; they needn't be equal, but the *best available* spot for each player each round should be roughly comparable, or turn order becomes deterministic. `balance_sim.py` can rank spaces by greedy value.
- **Contention pressure** = `(workers in play) / (spaces worth taking)`. >1 means someone goes hungry every round (intense); <0.6 means little blocking (relaxed). Tune per player count.
- **Round economy.** Sum the resources entering the game per round vs. what endgame scoring demands — this sets game length and whether the economy feels generous or starved.

## Failure modes
- **The dominant opening spot** everyone races for → first player always wins. Fix by adding compensation to other spots or making the hot spot scale down.
- **Downtime spike** when contention is high *and* turns are slow — players plan their whole round, then it's ruined by a block, then they re-plan. Mitigate with soft blocking, simultaneous selection variants, or shorter decision scope.
- **Relaxed solitaire** at low contention — players never interact. Either embrace it (some lovely games are gentle) or tighten the ratio.
- **Punishing the new player** — experienced players block optimally; novices get starved. Soft blocking and a few uncontested "always available" basic actions soften the cliff.

## Variants & hybrids
- **Action selection / role selection** (Puerto Rico, Race for the Galaxy): you pick a *role* and everyone executes it, you best — fuses action selection with simultaneous execution to slash downtime. Powerful anti-downtime pattern.
- **Worker placement + deck/bag** (Orléans, Viticulture's visitor cards): workers come from a bag or actions draw cards.
- **Dice placement** (Alien Frontiers, Grand Austria Hotel): dice values gate spaces — input randomness meets placement.
- **Mancala/rondel movement** (Tzolk'in's gears, Trajan): workers move along tracks rather than free-placing.

## Digital implementation
Very clean to model: state = `{spaces: {id: occupant|null}, players: {workers, resources}}`; a placement move validates the space is open (or computes the soft-block cost) and applies the action. The blocking rule is a one-line legality check — boardgame.io's move validation handles it naturally. Bots are easy and useful here: a greedy "take highest-value open space" bot immediately exposes dominant spots. Turn order and round reset are explicit phases.

## Physical transition
Transitions extremely well — placing physical meeples is tactile and satisfying, and the board *shows* the blocked state with zero bookkeeping (a key advantage: the game state is self-evident on the table). Main watch-item: soft-block escalating costs require a tracked counter; keep that visible. Ensure action spaces are iconographically self-explanatory so the board teaches the actions.

## Canon
Agricola (brutal contention, feeding pressure), Lords of Waterdeep (clean gateway), Caylus (the granddaddy, soft-block influence), Viticulture (worker placement + visitor cards + seasons), Tzolk'in (time/gear twist), Stone Age (dice-workers), Everdell (placement + tableau engine), Le Havre & Caverna (heavy economic).
