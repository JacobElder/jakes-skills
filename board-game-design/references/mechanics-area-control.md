# Area Control / Area Majority / Influence

**The experience:** spatial contest — claiming, defending, and contesting territory on a shared map. The board *is* the scoreboard, and it's visibly fought over.

**Central decision:** commit force to *win* a region (and how much is enough?) vs. spread thin to contest many vs. concede a region to dominate elsewhere. It's a continuous economy-of-force problem under opponents who are solving the same problem against you.

## How it works
Players place/move units (cubes, armies, influence) into regions; controlling or holding a majority in a region grants points or powers, usually scored at intervals or game end. El Grande, Blood Rage, Scythe, Risk, Small World, Twilight Struggle (influence), Inis, Kemet, Cyclades.

## The two big sub-families (choose one consciously)
- **Combat area control** (Risk, Blood Rage, Kemet): units fight; you take regions by force; elimination and dice/cards resolve battles. High drama, high swing, high conflict, kingmaking risk.
- **Influence / majority** (El Grande, Twilight Struggle, Inis): you place influence and *count majorities*; often no direct unit destruction. More euro, more controllable, less feel-bad. The phrase "area majority" usually signals this bloodless variant.

Decide early — they have completely different feel, audience, and balance problems.

## Design levers
- **Scoring cadence.** Score continuously (every turn), at fixed intervals (El Grande's periodic scoring — creates tension spikes and "when to commit" timing), or only at game end (long-horizon). Interval scoring is the classic tension engine: players must peak at the right moment.
- **Majority resolution.** Plurality (most units wins all), threshold (need N), or graduated (1st/2nd/3rd get descending points — Blood Rage, El Grande). Graduated scoring dramatically reduces feel-bad: losing a region by one unit still pays something, so over-committing isn't all-or-nothing.
- **The over-commitment tax.** Good area control punishes *both* under- and over-committing. If 5 units beat 4 and also beat 1, players hoard; if winning by 1 is as good as winning by 5, players spread to exactly-one-more everywhere. Graduated rewards and "wasted" surplus units create the right tension.
- **Mobility & tempo.** Can you redeploy, or is placement sticky? High mobility = swingy, reactive; sticky placement = commitment matters, plan-ahead.
- **Combat resolution** (combat sub-family): deterministic (chess-like, no luck) vs. dice (swing) vs. card-driven (hand management, bluffing — Inis, A Game of Thrones). Card-driven is the modern euro-friendly answer: tension without pure dice swing.

## Balance math
- **Force-to-reward ratio per region.** Map each region's point value against the force needed to secure it. Outliers become the only region anyone fights for. `balance_sim.py` can help by simulating greedy allocation.
- **Marginal value of the Nth unit in a region.** Graduated scoring should make this curve diminish so spreading stays viable. Plot it.
- **First-strike / initiative advantage** in combat: simulate symmetric battles to measure how much the attacker (or higher-initiative player) is favored, then price initiative accordingly.

## Failure modes
- **Kingmaking** (the signature risk of the combat sub-family): a losing player chooses the winner by whom they attack. This is a *design* failure (SKILL.md conviction 8). Mitigate with simultaneous order resolution, hidden commitment, graduated scoring (so attacks are about points not spite), and limiting purely-destructive late actions.
- **Turtling / stalemate.** If defense strictly beats offense, nobody attacks and the board freezes. Ensure holding still has a cost (upkeep, decay) or that points require contesting.
- **Snowball.** Controlling regions grants power that helps control more regions → runaway. Add interval scoring (so leads are banked but the board resets pressure), region-specific bonuses that favor newcomers, or a cap.
- **The "everyone gangs the leader" pile-on**, which is just distributed kingmaking — same fixes.

## Digital implementation
Model the map as a graph of regions with adjacency; state tracks units-per-region-per-player. Majority scoring is a simple per-region count + sort. Combat resolution should be a pure function returning the new state + a log entry (so replays/animation can render it later). Hidden simultaneous orders (Inis-style) map cleanly to boardgame.io phases where all players submit moves before resolution — a strong anti-kingmaking, anti-downtime pattern that's *easier* to enforce digitally than physically. Bots that greedily maximize majorities quickly reveal dominant regions.

## Physical transition
The board self-documents control state beautifully (a key strength — no hidden bookkeeping). Watch: simultaneous-order systems need order-writing components (player screens, dials, programming cards) and a clean reveal ritual; combat with dice needs fast resolution to avoid downtime. Interval scoring needs an unmissable trigger so it isn't forgotten. Distinct, colorblind-safe unit colors are non-negotiable.

## Canon
El Grande (the area-majority urtext, interval scoring), Twilight Struggle (influence + card-driven, two-player), Blood Rage (graduated combat + drafting), Scythe (control + engine, mostly bloodless), Inis (card-driven, kingmaking-aware), Small World (asymmetric powers + decline timing), Kemet / Cyclades (combat + powers), Root (asymmetric area control — advanced).
