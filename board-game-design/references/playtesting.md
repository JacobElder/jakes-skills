# Playtesting

The only thing that answers "is it balanced overall, and is it fun." Simulation finds the obvious holes cheaply (`balance-and-simulation.md`); playtesting answers everything that depends on real, adaptive, feeling humans. Run it as a staged process — each stage answers different questions and catches different bugs.

## The stages (in order)

### 1. Solo / self-play (you, both/all sides)
**Answers:** Does it function? Are there softlocks, infinite loops, obvious dominant lines, dead turns? Earliest, cheapest, do it constantly.
Play all sides honestly *and* play all sides adversarially (try to break it). You'll catch most rules holes and the most blatant dominant strategies here. Digital advantage: your headless bot self-play (below) does this faster and without self-deception.

### 2. Bot / simulated self-play (if digital)
**Answers:** Correctness at scale and gross imbalance. Run thousands of random-legal games headless to flush crashes, illegal states, and softlocks; run greedy/single-strategy bots to expose dominant strategies and spots/cards. See `digital-implementation.md` (bots) and `balance-and-simulation.md`. Caveat: bots reveal *mechanical* dominance, not human-meta balance or fun — it's a filter, not a verdict.

### 3. Friendly table (people who know you)
**Answers:** Does the core loop engage real people? Where's the downtime? What's confusing? Is it *fun*?
You may teach and answer questions here. Watch faces, not just scores — boredom, confusion, and the "ohh!" moment are the data. Ask afterward: when were you bored? when was your decision obvious? what would you do differently next game? (The last one tests for replay pull.) **Take notes on what they *do*, which is more honest than what they *say*.**

### 4. Blind playtesting (strangers, rulebook only, no designer present)
**Answers:** Can the game be learned and played *without you*? Is the rulebook correct? This is the single most important and most-skipped stage.
You are not allowed to talk. Every question they ask is a rulebook or design bug you must fix. Designers are catastrophically blind to their own game's assumptions; blind testing is the only cure. Do this before any manufacturing commitment. (For physical: hand them the box and rulebook and leave. For digital: ship a build to testers with only the in-game tutorial.)

### 5. Targeted / adversarial testing
**Answers:** Does a known-suspect strategy break it? Recruit your most competitive, rules-lawyer testers and *tell* them to break a specific thing (the engine that looks too strong, the combo you're worried about). Players optimize harder than any bot at finding the fun-killing degenerate line.

## What to measure (instrument it like an experiment)
Don't just collect vibes — collect data, especially if you're quantitatively inclined:
- **Win rate by strategy/faction/archetype.** Target: no archetype dominating; all viable. Skew = a balance problem.
- **Win rate by seat / turn order.** Structural first-player advantage. A few points is normal; large skew needs a compensation mechanism.
- **Game length** (distribution, not just mean) vs. your target. Long tails = a stalling problem.
- **Decision diversity:** are players making *different* choices game to game, or converging on one line? Convergence = a dominant strategy or too-thin a decision space.
- **Downtime:** time per turn, and how engaged players are off-turn. The silent killer (SKILL.md conviction 4) — measure it explicitly; long off-turns are a redesign signal.
- **Score spread at end.** Blowouts every time → runaway-leader issue (or working-as-intended, depending on your stance — see the catch-up disagreement). Always-ties → maybe decisions don't matter enough.
- **Where people quit / disengage** (digital: drop-off analytics; physical: who checks their phone).

Digital instrumentation makes all of this nearly free — log every game's outcome, length, and move history, and you have a dataset. This is a real advantage of digital-first for a data-minded designer: you can do actual statistics on hundreds of games instead of eyeballing a dozen.

## Reading the results (don't over-fit)
- **Separate "this specific group" from "the game."** One table's quirk isn't a trend; a pattern across many tables is. (Same generalization discipline as not over-fitting a model to one dataset.)
- **Listen to the problem, distrust the proposed solution.** Players are excellent at locating *where* something feels bad and unreliable at prescribing the fix. "This card is overpowered" might really mean "I had no answer to it" — the fix could be more answers, not nerfing the card.
- **Change one thing at a time** between test sessions, or you can't attribute the effect. Version your changes and the reasoning (you already keep the engine in source control — keep balance changes there too, with rationale).
- **Distinguish "not fun" from "not balanced."** A perfectly balanced game can be boring; a slightly unbalanced one can be a blast. Fix the right problem.

## How much is enough?
More than you think, and blind tests matter more than friendly ones. A rough heuristic from the field: dozens of plays before you trust the core, *many* more (and across groups you don't know) before it's ship-ready, and the bulk of late-stage testing should be **blind**. Digital lets you front-load thousands of bot games for correctness/gross-balance so the human hours concentrate on fun and human-meta balance — the questions only people can answer.

## The mindset
Playtesting is hypothesis-testing, not validation-seeking. You are trying to *falsify* "my game is good," not collect compliments. The most valuable tester is the one who didn't enjoy it and can tell you precisely when they checked out. Design the sessions to surface bad news early, while it's cheap to act on.
