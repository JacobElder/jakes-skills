# Balance & Simulation

The quantitative side of design. The governing principle (SKILL.md conviction 10) bears repeating because it determines whether your analysis is worth anything:

> **Simulate subsystems. Playtest systems.** Monte Carlo and EV math are sharp tools for *isolated* questions with a clear source of randomness. They are the wrong tool for "is the whole game balanced" or "is it fun," which depend on adaptive strategic players and emergent interaction that simulation can only caricature.

Stated as a test: **if answering the question requires modeling how a smart opponent would adapt, simulation will mislead you — go playtest.** If the question is about a die, a deck, a curve, or a flow rate in isolation, simulate it.

## What simulation answers well (use `scripts/balance_sim.py`)
- **Card/component cost-vs-effect ("rate") outliers.** Compute value-per-cost across a set; flag outliers. The classic way to find the over-/under-costed card before a human ever notices.
- **Probability questions.** "What's the chance my combo piece is in my opening hand?" (hypergeometric). "P(bust) at push depth k?" "Odds of rolling ≥3 successes on this dice pool?"
- **Distributions, not just means.** Two options with equal EV but different *variance* are a genuine player decision — always look at the spread, not only the average. Report min/max/percentiles.
- **Resource flow & game length.** Turns until a supply depletes, expected total points, expected round count → sets pacing and confirms the game ends when you intend.
- **First-player / seat advantage** in a *fixed-strategy* model — a lower bound on structural positional bias.
- **Degenerate-line detection** via greedy/single-strategy bots: if one mechanical strategy wins disproportionately *against non-adaptive opposition*, you've found a dominant strategy (a design hole), not a clever play.

## What simulation does NOT answer (go to `playtesting.md`)
- "Is my game balanced overall?" — depends on adaptive players; a strategy that crushes dumb bots may be counterable by humans, and vice versa.
- "Is it fun? Is there enough tension? Does the theme land?" — unmeasurable by sim.
- "Are the *interesting decisions* actually interesting?" — requires humans choosing under real stakes.
- Anything dominated by **player modeling**: bluffing, negotiation, politics, reading opponents. (You can train strong agents — MCTS/RL — to approximate this, but that's a research project, not a tuning pass, and even then it tells you about *optimal* play, not *human* play.)

## Core math toolkit
- **Expected value:** `EV = Σ P(outcome) × value(outcome)`. The backbone of risk/reward and cost analysis.
- **Variance / standard deviation:** the swing. High-variance options favor trailing players (they need swing); low-variance favors leaders. This is *design-relevant*, not just statistical.
- **Hypergeometric** (drawing without replacement — decks, bags): P(≥1 of k targets in a hand of h from n cards) = `1 − C(n−k, h)/C(n, h)`. Use for combo reliability and "will I draw what I need."
- **Binomial** (independent trials — repeated dice/coin): P(exactly j successes in n trials at rate p). Use for dice pools.
- **Cost curves:** plot effect-power against printed cost; the trend line is your "fair rate," and deviations are your design knobs (a deliberately under-priced card is a "build-around"; an accidental one is a bug).
- **Markov chains** for positional games (Snakes & Ladders-type movement, track games): expected turns to reach an absorbing state. Often a clean closed form *or* a quick simulation.

## How to actually run a balance pass
1. **Isolate the question.** Write it as one sentence about one subsystem. ("Is the 4-cost card worth a card slot vs. the 3-cost?" not "is my game fair?")
2. **Model only that subsystem.** Strip everything else. Fix opponents' behavior or remove them.
3. **Choose the agent model and state its assumptions.** Random? Greedy? Fixed strategy? Every result is *conditional on this model* — report it alongside the numbers, always. A balance claim without its agent model is meaningless.
4. **Run enough trials** for stable estimates (10k+ for rare events; check that the estimate stops moving). Report a confidence interval, not a point estimate.
5. **Report the distribution + the caveat.** Never present a sim result as "the game is balanced." Present it as "under [model], in isolation, this subsystem behaves like [distribution]; verify in playtest."

## Using `scripts/balance_sim.py`
A self-contained (stdlib-only) Monte Carlo harness for subsystem questions. It ships with worked examples and is meant to be *copied and adapted* per game, not used as a black box. Run `python scripts/balance_sim.py --help` and `--demo` to see:
- a dice-pool EV/variance/distribution calculator,
- a hypergeometric "P(draw my combo)" calculator,
- a push-your-luck optimal-stopping analyzer (EV curve + bust curve by push depth),
- a deck-cycling economy simulator (compare buying strategies' ramp),
- a generic `simulate(trial_fn, n)` that returns mean, stdev, and percentiles for any trial function you write.

Adapt the `trial_fn` to your subsystem; let the harness handle the statistics and reporting. Pair every output with the scope caveat above.

## The honest summary to give users
Quantitative balance is a **flashlight, not a verdict.** It finds the obvious holes fast and cheap — the dominant card, the dead strategy, the game that ends three turns too late — so your scarce human-playtest hours go to the questions only humans can answer. A designer who simulates subsystems *and* playtests systems is using both tools for what they're good at. A designer who simulates the whole game and trusts the number is fooling themselves; a designer who refuses to simulate is doing arithmetic homework at the table that a script could have done in seconds.
