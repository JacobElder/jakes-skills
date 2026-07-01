# Push-Your-Luck (Risk / Reward / Stop-or-Continue)

**The experience:** the table holding its breath. Greed vs. fear, made into a decision you actively own — when you bust, it's *your* fault for pushing, and that ownership is what makes it fun rather than arbitrary.

**Central decision:** bank what I have now (safe) vs. risk it for more (greed), with the bust probability rising the further I push. The skill is in reading the shifting odds and your opponents' positions.

## Why this is the antidote to bad randomness
Push-your-luck is the *right* way to use output randomness (SKILL.md conviction 6). Pure output randomness ("roll to see if your plan works") strips agency; push-your-luck hands the randomness back to the player as a *choice* — you decided how far to push, so the outcome feels earned even when the dice betray you. If a design needs swing and drama, convert "roll and hope" into "choose how much to risk."

## How it works
Players repeatedly choose to continue accumulating (rolling, drawing, flipping) or stop and bank. Continuing risks a "bust" that forfeits some or all of the at-risk gains. Can't Stop, Incan Gold/Diamant, Quacks of Quedlinburg, Cuphead-style press-your-luck, Port Royal, Welcome to the Dungeon.

## Design levers
- **Bust severity** = the whole tension dial. Lose *everything* this turn (Can't Stop — brutal, exciting) vs. lose only the *unbanked* portion vs. a soft penalty. Higher severity = higher tension but higher feel-bad; tune to game length (harsh busts are fine in short games — you're back in 30 seconds).
- **Rising vs. fixed odds.** The bust chance should usually *increase* as you push (more dice that can't improve, more dangerous cards drawn) so the decision sharpens each step. Fixed-odds pushing is a weaker, flatter decision.
- **Visible vs. hidden odds.** Can players *calculate* the risk (Incan Gold: known deck of hazards, countable) or only feel it? Calculable odds reward arithmetic and create a cleaner skill test; hidden odds create gut-feel drama. Both valid — different audiences.
- **Shared-fate pushing** (Incan Gold/Diamant): everyone's in the temple together; when others leave, the remaining treasure splits among fewer — so *others' decisions* change your odds and rewards. This adds a brilliant social/game-theory layer (do I leave now while the split is good?) for almost no rules cost. Strongly consider it.
- **Catch-up is built in and *non-controversial* here.** A trailing player can rationally push harder; a leader can play safe. The mechanic self-balances risk appetite to standing, sidestepping the catch-up-mechanic debate entirely — one reason designers love it as a seasoning.
- **Mitigation tools** (rerolls, "safe" symbols you can lock, insurance) let you soften busts without removing the decision.

## Balance math
This is the most *directly* mathematical family — expected value is the whole game, and it's a flagship `balance_sim.py` use case.
- **EV of pushing once more** = `P(safe) × (gain if safe) − P(bust) × (loss if bust)`. The interesting design target: tune values so the EV-optimal stopping point is *not obvious*, sits mid-push, and **shifts with game state** (so a trailing player's optimal push differs from a leader's). If pure EV says "always stop at exactly 3," you've built arithmetic homework, not a decision.
- **Bust-probability curve.** Plot P(bust) as a function of push depth. You want it gentle early (pushing feels safe and tempting) and steepening (so greed gets genuinely scary). Simulate it.
- **Variance, not just mean.** Two options with equal EV but different variance are a real decision for players of different risk appetite — lean into that. Report variance/distribution from the sim, not only the average.

## Failure modes
- **Dominant stopping point:** if math says always stop at N regardless of context, the decision is solved. Fix by making the reward/risk depend on board state, opponents, or what you still need.
- **Feel-bad spiral:** harsh busts in a *long* game where you're then sidelined → misery. Either shorten the loop or soften the bust.
- **Anticlimax:** if banking is almost always correct, no one pushes and the drama never fires. The temptation to push must be real — keep the marginal reward juicy relative to the risk.
- **Pure luck with no decision:** if you can't meaningfully affect the odds or choose when to stop, it's a slot machine, not push-your-luck.

## Digital implementation
Among the *easiest* families to prototype — the core loop is `while (player.pushes) { draw(); if (bust) break; }`. State is tiny. This makes it an ideal first digital build, and the EV math is so central that you should build the simulation *alongside* the prototype and tune the value tables from sim output. Animations/sound carry enormous weight digitally (the suspense of a reveal) — but the rules engine stays trivial.

## Physical transition
Transitions superbly — physical reveals (flipping a tile, the clatter of dice) deliver the suspense better than a screen, and the bookkeeping is minimal. This is a family where the physical version is often *better*. Main watch: make the at-risk vs. banked distinction physically unambiguous (separate zones/trays), and keep the push action fast so tension doesn't deflate.

## Canon
Can't Stop (the pure distillation — Sid Sackson), Incan Gold / Diamant (shared-fate social push, brilliant and tiny), Quacks of Quedlinburg (bag-building + push-your-luck, the modern masterclass), Port Royal (card-flip push), Welcome to the Dungeon (push + bluffing), Clank! (push-your-luck woven into a deckbuilder).
