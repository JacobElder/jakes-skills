# Worked Example: One Design, All Eight Phases

This walks a single small design through the SKILL.md pipeline end to end, so the phases are concrete rather than abstract. The game is deliberately tiny — the point is the *process*, not the design. Read this when you want to see how the pieces connect; imitate the sequence, not the specifics.

> The design we'll build: **"Deepdelve"** — a 30-minute, 2–4 player press-your-luck game about rival treasure-hunters descending into a collapsing tomb. We'll discover its problems *through the process* and fix them, because that's what the process is for.

---

## Phase 1 — Define the experience (not the mechanic)
Two sentences, no mechanics yet:
- **Fantasy/feeling:** the greedy thrill and dread of going one room deeper into a place that's trying to kill you, while rivals watch and hope you overreach.
- **Central decision:** *press on for richer loot, or bank what I have and get out* — sharpened by the fact that my rivals are making the same call and our fates are partly linked.

Notice we have NOT said "press-your-luck" as a foregone conclusion — but the central decision is a risk/reward stop-or-go, so push-your-luck is the natural family (we'll confirm in Phase 3). We resisted starting from "I want to make a dice game."

## Phase 2 — Core loop and engine of progress
**Smallest repeated unit:** on your turn you descend one room: flip the top tomb tile. Most tiles add treasure to your run; some are *hazards*. Then you decide — descend again (push) or climb out (bank this run's treasure as points). Two matching hazards on your run and you collapse: you lose this run's treasure and your turn ends.

**Why interesting in isolation?** Each flip changes the odds and the stakes — the decision to push is fresh every time and never auto-correct (we'll verify with math in Phase 6 that there's no fixed "always stop at N"). 

**Progress/end:** first to a treasure-point target (say 30) triggers the end; finish the round so everyone's had equal turns. Tension rises because the tomb deck thins and hazards concentrate as the game goes on.

We sketch the **bare loop on paper** (a deck of index cards: treasures and hazards) and play it solo ten times. It's tense — good. But we notice a problem: **other players are bored while one person pushes.** That's downtime (SKILL.md conviction 4), the silent killer, surfacing exactly where the process predicts. Flag it; we'll fix it in Phase 3.

## Phase 3 — Select mechanic families (read the references)
The core decision confirms **push-your-luck** as the primary family → read `references/mechanics-push-your-luck.md`. From it, two ideas directly address our Phase-2 downtime problem and our "fates are linked" fantasy:
- **Shared-fate / leave-timing** (the Incan Gold pattern): instead of one player descending alone, *all* players descend the same tomb together each round, and each *secretly and simultaneously* decides each step whether to continue or climb out. Players who climb out split the treasure left behind by those still below. This **annihilates the downtime** (everyone decides at once — simultaneous action), adds a social/game-theory layer (leave while the split is good?), and *is* the "linked fates" fantasy. 
- The reference also warns: make the bust *severity* match game length and keep the optimal stopping point *non-obvious and state-dependent*. We note both as Phase-6 targets.

We add a light **set-collection** layer (`references/tradition-euro-and-families.md`, set-collection entry): treasures come in types, and matching sets cash for bonus points — giving a reason to push for a *specific* treasure, not just "more," which deepens the decision beyond raw EV.

Decision: **push-your-luck (shared-fate) + light set collection.** Two families, fused around one currency (treasure) and one tension (greed vs. exit). We explicitly did *not* bolt on a third system.

## Phase 4 — Specify the rules as a state machine
The spec that doubles as data model and rulebook skeleton:
- **Components/state:** a tomb deck (treasure tiles by type + hazard tiles); each player's `inRun` flag, `runTreasure` (this descent), `bankedPoints`; the `revealed` tiles this round; a `hazardsShown` counter.
- **Legal moves:** during a descent step, each still-in player simultaneously chooses `continue` or `exit`. (That's the whole move set — radically compressed, conviction 5.)
- **Turn/phase structure:** Round = repeated *descent steps*. Each step: reveal next tile → resolve hazard/treasure → all in-players simultaneously pick continue/exit → players who exit bank `runTreasure` + their cut of abandoned treasure. A *second matching hazard* collapses the tomb: everyone still in loses their `runTreasure`. Round ends when the tomb collapses or all players have exited; reshuffle a fresh tomb for next round.
- **End/scoring:** game ends after the round in which someone reaches 30 banked points; highest total (banked + set bonuses) wins.

This spec is the formal rulebook in miniature and the exact shape we'll implement.

## Phase 5 — Build the digital prototype
Copy `assets/boardgame_io_template/`. The shared-fate simultaneous decision maps directly onto boardgame.io's `activePlayers: { all: 'deciding' }` (the template's draft phase is the same pattern). Model the tomb as injected-random shuffled state (`random.Shuffle` in `onBegin`), keep each player's `runTreasure` separate, and resolve all `continue/exit` choices when every in-player has submitted. Build the **engine + a debug/CLI front end first** — no art. Within an hour you can play it and, crucially, *simulate* it.

## Phase 6 — Balance the subsystems with math + simulation
Now the quantitatively-sharp questions (conviction 10; `references/balance-and-simulation.md`). The flagship one: **is the optimal stopping depth fixed and obvious?** If so, the central decision is solved and the game is dead. We adapt `scripts/balance_sim.py`'s push-your-luck analyzer to our tomb composition and get an EV-by-stopping-depth curve and a bust-probability curve. Suppose it reports something like:

```
 k |      EV |  P(bust)
 1 |   1.35  |    0.36
 2 |   1.68  |    0.60   <- EV-optimal under THIS model
 3 |   1.46  |    0.77
 4 |   1.07  |    0.87
```

A flat "always stop at 2" would be a red flag. We *deliberately* break the fixedness using levers from the push-your-luck reference: (a) the **set-collection** payoff means a trailing player chasing a specific treasure rationally pushes past the EV-optimal depth; (b) the **shared-fate split** means optimal exit timing depends on *how many rivals are still below* — state the sim can't fully capture, which is exactly the point: we've made the decision depend on board state and opponents, so no single k dominates. We tune hazard counts so the bust curve *steepens* (gentle early, scary late) rather than being linear. We also sim **game length** to confirm ~30 points lands near our 30-minute target.

What we explicitly do NOT claim: that the sim proves the game is balanced or fun. It proved the *stopping decision isn't trivially solved in isolation* and sized the economy. The rest is Phase 7.

## Phase 7 — Playtest the system
Staged, per `references/playtesting.md`:
- **Solo / bot self-play:** thousands of random-legal headless games flush a softlock (a tomb that collapses with all players still in on step 1 — we add a "first step is always safe" rule). Greedy "always push" bots reveal that pure greed loses to disciplined exits — good, the decision matters.
- **Friendly table:** real people love the shared gasp when the tomb collapses — the *experience* (Phase 1) is landing. But two quiet players just always exit early and it's a bit flat for them; the set-collection bonus isn't pulling enough weight. We bump set rewards.
- **Blind table (rulebook only, no us):** they misread how the abandoned-treasure split works — a **rulebook bug**, not a player error. We rewrite that section with a worked example. (This is why blind testing is non-negotiable.)
- **Measure:** win-rate by seat (slight first-player edge → we give later players a tiny starting bonus), game length distribution (on target), and *decision diversity* (are players exiting at varied depths? yes → the decision is live).

## Phase 8 — Transition to physical (deliberately)
The design is locked; now the **invisible-work audit** (`references/physical-transition.md`). The computer was: shuffling the tomb (fine — players shuffle tiles), tracking each player's `runTreasure` (needs a physical tray per player so banked vs. at-risk treasure is unambiguous), computing the abandoned-treasure split (a human arithmetic chore — we redesign the split to a simple "divide the revealed treasure tiles among those who left this step" that needs no math), and resolving simultaneous choices (needs hidden-commit components: each player gets a two-sided "continue/exit" token revealed at once). We design **iconography** for treasure types and hazards so no text is needed, keep the at-risk/banked zones physically separate, and write the rulebook from the Phase-4 spec, leading with the goal and a worked split example. Print-and-play first; only then consider manufacturing.

---

## The point of the walkthrough
Every problem we hit — downtime, a possibly-solved stopping point, a rulebook ambiguity, a fiddly split, first-player advantage — was *predicted and located by the process*, and the references told us the fix. That's what the pipeline buys you: not a guarantee of a great game, but a systematic way to surface and resolve the failures early, cheaply, in the order that matters. Run your own design through these eight phases and the same machinery will catch your problems too.
