# Onboarding & Teaching: The First Five Minutes

SKILL.md conviction 5 says "the rules teach the game," but treats teachability as a property of elegant rules. It's also a *designable experience* in its own right — the setup, the teach, the first turn, and (digitally) the tutorial. Most players' verdict on a game is formed in the first five minutes, and a brilliant game with a brutal onboarding loses players before its depth ever shows. Design the on-ramp deliberately.

## Why this is its own concern
A game is learned before it is played, and the learning experience is where you lose people. Two distinct failure modes:
- **The teach is too hard** → the game never gets to the table a second time, or new players bounce.
- **The first turns are unrewarding** → even players who learn the rules disengage before the depth emerges.
These are not the same as "is the game good." A deep, balanced game can have a terrible on-ramp, and fixing the on-ramp is a separate design task from fixing the game.

## Setup cost is part of the experience
Setup is friction the player pays *before* any fun. Long, fiddly setup (sorting decks, seeding boards, distributing dozens of components) suppresses how often a game hits the table — and table frequency is the real measure of a game's success in someone's life.
- **Minimize and parallelize setup.** Can setup steps be done by multiple players at once? Can a component be pre-sorted into a tray/insert? Can a "setup card" replace a page of instructions?
- **Variable setup is a double-edged sword:** it boosts replayability (Discovery, per `references/experience-and-aesthetics.md`) but can balloon setup time and decision overhead. Worth it when the variability *is* the replay value; not worth it when it's just fiddliness.
- **Teardown counts too** — a game that's a pain to put away gets played less.

## Teachability: design the teach, not just the rules
The teach is a performance you're designing for, even if you're not in the room (blind play, digital tutorial).
- **Lead with the goal and the core loop, not the exceptions.** A player needs "here's what you're trying to do and what you'll do on your turn" before any edge case. Teach the 80% that covers most turns; defer the 20% of special cases to when they come up. (This is also why rulebooks should teach in play-order, not codebase-order — `references/physical-transition.md`.)
- **Theme is a teaching tool.** Integrated theme (`references/experience-and-aesthetics.md`) lets players *infer* rules from the fiction ("of course the river flows downhill"), slashing what they must memorize. A well-themed rule teaches itself.
- **The "first turn" test.** Can a new player take a *reasonable* first turn after a 2-minute teach, learning the rest by playing? If yes, your on-ramp is good. If a player is paralyzed on turn 1 because they must understand the whole system first, the on-ramp is too steep — find a way to let them act early and deepen as they go.
- **Reference/player aid cards** carry the turn structure and iconography so players aren't re-reading the rulebook. If you *can't* fit the core turn on a player aid, that's a signal the turn is too complex (conviction 5).
- **Progressive complexity / "learning scenarios."** Many great games introduce systems gradually: a basic-game variant, a first-scenario that uses a subset of rules, or campaign pacing that adds one new thing per session (`references/mechanics-campaign-legacy.md`). Front-loading every rule is the enemy; revealing them in a designed order is the friend.

## Digital onboarding: the tutorial is make-or-break
A digital board game's tutorial often determines retention more than the game's depth — players who don't "get it" in the first session don't return. Digital onboarding has tools physical can't use, and obligations physical doesn't carry.
- **Teach by doing, gated.** The best digital tutorials don't show a wall of text — they let the player take *real actions* with the interface constrained to the right next move, revealing systems one at a time. Learning-by-doing beats reading.
- **The interface can hide complexity until needed.** Digitally you can disclose rules progressively (grey out illegal moves, surface only relevant options, pop a hint the first time a system appears) — an onboarding superpower physical lacks. Use it: a complex game can *feel* simple early because the UI only shows what's currently relevant.
- **But beware the dependency.** If the digital version's UI does all the teaching (and all the rules-enforcement and bookkeeping), the design's *inherent* teachability can rot unnoticed — which becomes a crisis if you later port to physical (`references/physical-transition.md`), where there's no UI to lean on. Keep the underlying rules teachable even while the UI smooths the on-ramp. The clean rules engine (`references/digital-implementation.md`) helps: if the *rules* are elegant, both the tutorial and the eventual rulebook have less to explain.
- **First-session reward.** Digital players especially expect an early sense of progress/agency. Ensure the first few minutes contain a real, satisfying decision and a visible payoff — not ten minutes of setup-equivalent menus before anything happens.

## Process implication
- Treat onboarding as a **Phase 7 (playtesting) and Phase 8 (physical) concern with its own tests**: the 2-minute-teach test, the first-turn test, blind-rulebook teaching (physical), and tutorial-completion / first-session-retention (digital).
- When playtesters say a good game "didn't grab them," check the on-ramp before you touch the core — the problem is often the first five minutes, not the game.
- The cheapest onboarding win is almost always **integrated theme + a clean player aid + a fast, meaningful first decision.** Reach for those before adding tutorial machinery.
