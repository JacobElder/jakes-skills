# Production & Scope: Actually Shipping a Small Game

Most small games die from **scope**, not from a coding problem. The maker builds systems for a game whose core isn't proven fun, the work balloons, motivation drains, and it's abandoned at 30%. This file is the antidote: a process that front-loads the fun, ruthlessly limits scope, and gets to "done." For a lot of game-dev requests this matters *more* than the code — if someone says "I keep starting games and never finishing," lead with this, not with architecture.

## Contents
- Find the fun first
- The toy → prototype → vertical slice → production path
- Scope discipline
- Milestones and "done"
- Playtesting
- The last 20%: polish, juice, and shipping
- Practical scoping heuristics

## Find the fun first

The first thing you build is the **smallest interactive toy** that tests your core idea — the 10-second loop, stripped of everything else. Not a menu, not a save system, not three levels of inventory. A square that jumps. A ship that shoots. A grid you match tiles on. Play it. Is the raw interaction satisfying *before* art, story, and content? If yes, you have a game to build. If no, change the toy — because no quantity of content, art, or systems rescues a core loop that isn't fun. Designers call this "finding the fun," and doing it in week one saves you from polishing a corpse in month six.

## The toy → prototype → vertical slice → production path

Build a small game in escalating stages, each gated on the previous one working:

1. **Toy (days):** the core mechanic alone, ugly programmer art, no UI. Goal: prove the interaction is fun.
2. **Prototype (1–2 weeks):** the core *loop* — mechanic plus the immediate goal/feedback/failure that makes it a game (shoot → enemies die → you score → you can lose). Still ugly. Goal: prove the loop holds attention for a few minutes.
3. **Vertical slice (weeks):** one small piece of the *real* game built to near-final quality — one level, one enemy type, real(ish) art and sound, full game feel. Goal: prove what "good" looks like and that you can build it. This is also what you show people and post for wishlists.
4. **Production (the long middle):** make *more* of the proven thing — more levels, enemies, content — plus the unglamorous shipping work (menus, save, options, pause, controller support, localization). By now you're replicating a known-good template, which is the only phase where content-grinding is safe.

The discipline is the **gating**: don't enter production on an unproven loop, and don't build the vertical slice's polish into a loop you haven't validated.

## Scope discipline

Scope is the budget you're always overspending. Tactics that work:

- **Pick a tiny, finishable idea.** A first game should be completable in weeks, not years. Pong, Breakout, Flappy Bird, a one-screen arena shooter, a small puzzle set. "Finish small games" is a skill you build by finishing small games.
- **One core mechanic, done well.** The best small games are one idea explored deeply, not five ideas done shallowly. When a new feature tempts you, ask: does it serve the *one* mechanic, or is it a second game?
- **Treat every feature as a cost.** Each system is build + debug + tune + maintain + interact-with-everything-else. Default to "no." A cut feature ships; a half-built one doesn't.
- **Maintain a cut list, not just a TODO.** Explicitly park ideas in a "version 2 / not now" list. It quiets the urge to build them without losing them.
- **Account for the iceberg.** The visible mechanic is ~20% of the work; the other 80% is menus, save/load, options, pause, audio plumbing, controller support, edge cases, build/export, store pages. Budget for it — it's why "it's basically done" games take another three months.
- **Reskin over rebuild.** Get more game out of what exists (new enemy = new stats + sprite on the same AI) before writing new systems.

## Milestones and "done"

Define **done** concretely up front, or the game expands forever. A crisp target: "3 levels, 1 boss, 4 enemy types, a title and game-over screen, runs start to finish without crashing." Then break it into milestones with dates, and when a milestone is hit, ship/show it rather than gold-plating. **Timeboxing** (game jams especially) is a feature: a hard deadline forces scope decisions you'd otherwise dodge. Finishing — even something small and imperfect — teaches more than a perpetually-90% magnum opus.

## Playtesting

You stop being able to see your own game; you know where to walk and what to do, so you can't feel the confusion a new player feels. So **put it in front of other people early and often** — even one or two, even rough.

- **Watch, don't guide.** The most valuable signal is where they get stuck, confused, or bored. Resist explaining; the game has to explain itself.
- **Note behavior over opinions.** What players *do* (quit at level 2, never use the dash) is truer than what they *say* they like. When they propose a fix, treat the *problem* they hit as the real data, not their proposed solution.
- **Test the core loop's fun before content; test onboarding/clarity once there's a build.** New players reveal tutorial and readability gaps you're blind to.

## The last 20%: polish, juice, and shipping

The gap between "works" and "feels like a real game" is **juice** (`game-feel.md`) plus the shipping checklist. Reserve real time for both — they're not optional trim:

- **Feel pass:** sound on every action, tweens instead of snaps, screenshake/hitstop/particles on the moments that matter, a camera that eases. This is where the perceived quality jump happens.
- **Onboarding:** the first 60 seconds teach the game without a wall of text. Introduce one idea at a time.
- **Shipping checklist:** main menu, pause, options (at least volume + screenshake/accessibility toggles), save if needed, game-over/restart flow, controller support if relevant, clean quit, and an actual **build/export** to the target platform tested on a machine that isn't yours. Then the store/itch page: capsule art, GIFs of the *juicy* moments, a short clear description.

## Practical scoping heuristics

- **Estimate, then multiply by 2–3.** Game tasks have long tails (tuning and edge cases dominate). Your honest estimate is the optimistic case.
- **If it's not fun ugly, it won't be fun pretty.** Don't spend on art to rescue a weak loop.
- **Cut a feature before cutting the deadline.** Shipping less, done, beats shipping more, never.
- **The best engine/idea/feature is the one you finish with.** Bias every decision toward *completion*.
