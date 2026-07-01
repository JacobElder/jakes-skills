# Engine Building

**The experience:** the satisfaction of a machine you built starting to hum — early turns feel slow and deliberate, late turns produce cascades where one action triggers five. The dopamine is in the *acceleration*.

**Central decision:** invest now (build capacity, sacrifice immediate output) vs. harvest now (convert capacity to points/resources). The tension between *getting better at the game* and *winning the game*.

## How it works
Players acquire components (cards, tiles, buildings, upgrades) that modify the rules in their favor — granting resources, discounts, extra actions, or conversions. Components combo: the value of acquiring X depends on what you already own. The "engine" is the accumulated set of self-reinforcing effects. Power Grid, Splendor, Wingspan, Gizmos, Race for the Galaxy, Terraforming Mars, and most heavy euros are engine builders at heart.

## Design levers
- **Ramp curve.** How fast can the engine accelerate? Too fast → the game is decided by turn 3 and the rest is bookkeeping (runaway leader, conviction 8 in SKILL.md). Too slow → players never feel the payoff. Aim for the engine to come online around 50–70% through the game, leaving a satisfying harvest phase.
- **Combo depth vs. legibility.** Deep combos reward system mastery but punish new players and invite analysis paralysis. Shallow, visible synergies (Splendor: card discounts cards) onboard fast. Choose deliberately for your audience.
- **Engine *types* as strategic identities.** Offer multiple distinct engine archetypes (a "wide" many-cheap-pieces engine vs. a "tall" few-expensive-pieces engine; a resource engine vs. a points engine). This is where replayability and the "no dominant strategy" mandate live.
- **Convergence vs. divergence.** Do all players draw from a shared market (convergent, interactive, blockable) or build privately (divergent, multiplayer-solitaire risk)? Shared markets create interaction but also drafting/denial dynamics.
- **A hard stop.** Engines want to grow forever; the game must end before the engine trivializes everything. Use a fixed round count, a depleting supply, or an endgame trigger that fires while engines are still interesting, not after they've maxed out.

## Balance math
- **Payback period.** For each investment, compute turns-to-recoup: `cost / per-turn-benefit`. An upgrade that pays for itself in 2 turns in an 8-turn game is strong; one that pays back in 7 turns is a trap. Plot payback across all engine pieces — outliers are balance bugs. This is a textbook `balance_sim.py` use case.
- **Marginal value curves.** The Nth copy of an effect should usually be worth less than the first (diminishing returns) or the design risks a single dominant engine. If the Nth copy is worth *more* (snowball), you must cap N or end the game fast.
- **Opportunity cost is the real cost.** A card's printed cost is only half its cost; the other half is the action/turn spent acquiring it instead of harvesting. Price accordingly.

## Failure modes
- **Solved opener.** If one early purchase is always correct, the first few turns are scripted. Test by simulating greedy single-strategy agents; if one opening dominates win rate, you have a hole.
- **The runaway snowball.** Self-reinforcing engines naturally produce runaway leaders. Mitigate with shared-market denial, catch-up *options* (not handouts — see the disagreements list), or a short clock.
- **Multiplayer solitaire.** Private divergent engines with no shared resource → players ignore each other. Add at least one contested axis (shared market, turn order, a tempo race) if interaction matters to you.
- **Anticlimactic harvest.** If the last few turns are pure mechanical point-conversion with no decisions, trim them — end the game one beat earlier.

## Digital implementation
Engines are *bookkeeping-heavy*, which is exactly what computers excel at — making engine builders one of the best families to start digital. Model each engine piece as a data-driven effect (a list of triggers/modifiers) rather than bespoke code; this lets you add/retune pieces by editing data, and lets `balance_sim.py` enumerate them. Represent the player's engine as the accumulated set of active effects applied during the relevant phase. boardgame.io's pure-reducer model handles cascading triggers cleanly if you resolve effects in a well-defined order (declare the resolution order explicitly — ambiguous trigger order is a classic rules bug).

## Physical transition
Engines that compute effortlessly on a screen can become upkeep nightmares on a table. Audit every per-turn trigger: a card that says "each turn, if you have ≥3 birds, gain 1 food" is free digitally but a missed-trigger magnet physically. Prefer effects players resolve *when they act* (pull-based) over passive "each turn" effects (push-based) the human must remember. Iconography must make combos legible at a glance.

## Canon to study
Splendor (minimalist, legible), Wingspan (engine + tableau + theme), Race for the Galaxy / Roll for the Galaxy (dense combo), Power Grid (engine + auction + market), Gizmos (visible cascade), Terraforming Mars (sprawling), Everdell, Dominion (engine-via-deck — see deck-and-bag).
