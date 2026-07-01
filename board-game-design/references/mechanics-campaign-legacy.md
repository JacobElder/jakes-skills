# Campaign / Legacy / Persistence

**The experience:** consequence that *carries*. Your choices don't reset at game end — they scar the board, unlock new content, kill characters permanently, and accumulate into a story only your group has lived. The investment of memory and attachment is the payoff.

**Central decision (design-level):** how much permanence, and how reversible? This family is defined by a spectrum, not a single mechanic — locate your design on it deliberately.

## The persistence spectrum (pick your point consciously)
- **Campaign (resettable):** a fixed sequence of scenarios with carried progress (XP, gear, unlocks), but the components are reusable and the box resets for the next group. (Gloomhaven, Spirit Island campaigns, most co-op campaigns, app-driven campaigns.)
- **Legacy (permanent):** the game *physically and permanently changes* — you write on the board, tear up cards, place stickers, open sealed boxes, destroy components. One group, one playthrough; the game is consumed as it's played. (Risk Legacy, Pandemic Legacy, SeaFall, Charterstone — Rob Daviau invented the form.)
- **Hybrid / app-persistent:** persistence lives in an app or save file, so the physical box is reusable but progress is durable. (Many modern legacy-lites; almost all *digital* implementations land here naturally.)

Digital implementation collapses much of this distinction — a save file is trivially permanent *and* resettable — which is a major argument for **prototyping legacy designs digitally first** (below).

## Design levers
- **The unlock graph.** The spine of a campaign is the tree/graph of what unlocks what. Design it as an actual graph: nodes (content, rules, components) with prerequisite edges. Pacing = the rate of new-thing introduction. Front-load too much → overwhelming; back-load → boring middle. The Gloomhaven model: a steady drip of new classes, items, and rules keeps each session introducing *one* new thing.
- **Ratchet vs. branch.** Pure ratchet (everyone progresses through the same nodes, just at different speeds) is easy to balance and write. Branching (choices lock out other paths) creates ownership and replay-curiosity but multiplies content cost and balancing surface enormously. Branch only where the *choice* is meaningful and you can afford the content.
- **Escalating difficulty curve** must track the players' escalating power (their evolving decks/characters/engine). This is a *moving-target balance problem*: you're balancing content against a power level that the players themselves are increasing. Get the power-progression curve right first, then tune encounters against it.
- **Legacy "permanence" must feel momentous, not punishing.** Permanently destroying a component is thrilling when it's the player's *choice* and *gain* ("I permanently upgrade this city"), grim-but-earned when it's a consequence ("this character dies"), and infuriating when it's arbitrary. Reserve permanence for moments the player will remember.
- **The reset/onboarding problem.** A new player joining at session 8 is hopeless. Co-op campaigns handle this better than competitive legacy. Decide your stance on drop-in/drop-out early.
- **The ending.** Legacy games are *consumed*; design a real finale, and ideally a satisfying "free play / final state" mode so the box isn't dead after the campaign.

## Balance math
- **Power-progression curve.** Plot player/party power vs. session number; plot intended challenge vs. session number; they should track with a small, intentional gap (challenge slightly ahead = tension). This is the master curve; `balance_sim.py` can simulate party power growth under different upgrade strategies.
- **Per-scenario difficulty** is balanced *against the expected party state at that point*, not in a vacuum — a trap that catches many designers. Carry the simulated party state forward between scenarios.
- **Content budget vs. branching.** Estimate `nodes × variants` of content; branching can 3–5× your authoring load. Sim/spreadsheet this before committing to a branch structure.

## Failure modes
- **Difficulty decoupling:** content balanced in isolation becomes trivial (party out-leveled it) or brutal (party under-geared). Always balance against carried state.
- **Pacing dead zones:** stretches with no new unlock feel like grinding. Audit the unlock graph for gaps.
- **Permanence regret / gridefing:** in *competitive* legacy, permanent changes can lock in an early leader's advantage for the rest of the campaign — a runaway-leader problem stretched across sessions. Build per-session catch-up and avoid permanent power gaps.
- **The unkillable save:** if mistakes are permanent and punishing, anxious players net-loss fun. Allow some reversibility or "scarring without crippling."
- **Abandonment:** campaigns that demand 15 consecutive sessions with the same group often die mid-campaign in the real world. Design sessions to be satisfying individually and the campaign to survive a missing player.

## Digital implementation
This is the family where **digital-first is most strongly recommended**, for several reasons: (1) a save file makes persistence trivial *and* lets you reset to re-test a mid-campaign scenario instantly — invaluable, since physically you can only play a legacy game once; (2) the unlock graph, carried state, and difficulty scaling are exactly the bookkeeping computers excel at and humans hate; (3) you can simulate the *whole campaign arc* with bot parties to find pacing dead zones and difficulty cliffs before any human plays. Model: a persistent profile (unlocks, party state, flags) separate from per-session game state; scenarios are data (setup + objectives + rewards) gated by unlock flags. Keep the unlock graph as data, not code, so you can re-pace by editing it.

## Physical transition
The hard part. Everything the save file did invisibly must become physical apparatus: legacy decks, sealed envelopes/boxes, sticker sheets, a campaign log/legacy-deck, a "reminder" system for carried rules changes. The irreversibility that's free digitally (just don't reset) becomes a *manufacturing and trust* matter physically (you're asking players to destroy components — the packaging must signal "this is intended and exciting"). Strongly consider an app-assisted hybrid to offload bookkeeping while keeping the physical legacy *moments* (the sticker, the torn card) that make the form special. Plan the production cost of consumable/one-use components explicitly.

## Canon
Pandemic Legacy: Season 1 (the co-op legacy benchmark — Daviau & Leacock), Risk Legacy (the original), Gloomhaven / Frosthaven (the campaign + engine + content-budget masterclass), Charterstone (competitive legacy), SeaFall (ambitious, instructive failure on pacing/length), Spirit Island (co-op with campaign content), Slay the Spire / Hades (digital roguelike persistence — study run-to-run meta-progression).
