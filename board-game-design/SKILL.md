---
name: board-game-design
description: Design board and card games across every major family — engine building, deck building, deck construction, worker placement, area control/majority, drafting, push-your-luck, campaign/legacy, euro and thematic traditions, plus auctions, trick-taking, tile-laying, set collection, route building, roll-and-write, cooperative, and social deduction. Use whenever the user wants to design, prototype, balance, or critique a tabletop game; invent or tune a mechanic; build a DIGITAL board game (boardgame.io, turn-based prototype, AI opponent, balance sim) that may later become physical; write a rulebook; run a Monte Carlo or cost-curve analysis; or plan playtesting. Trigger even when the user only describes a game idea ("a game where you draft flowers and build a tableau", "how do I stop one player running away with my game") without saying "board game" or "design." Don't fall back on generic "make it fun" advice; this skill encodes specific, defensible design convictions where vague even-handedness gives wrong answers.
---

# Board Game Design

This skill makes the agent design tabletop games the way a seasoned designer does — someone who has internalized Engelstein & Shalev's *Building Blocks of Tabletop Game Design*, Jesse Schell's *The Art of Game Design*, the MDA framework, and the accumulated craft of the BoardGameGeek / Board Game Design Lab / Ludology community. The goal is not to be a neutral encyclopedia. It is to channel a craft tradition with **directional confidence** — to know which questions have a right answer and which are genuinely contested, and to say so.

Generic AI game advice is milquetoast: "add variety, make it balanced, keep it fun." A real designer's advice is the opposite — it is *opinionated* about specific things (downtime is the silent killer; design the core loop first; randomness belongs at the start of a decision, not the end) and *agnostic* about others (catch-up mechanics, luck, player elimination — all genuinely debated). This skill teaches the agent which is which.

## The through-line: design digital-first, model the rules as a pure function

The single most important architectural idea in this skill, and the spine that connects "digital game now" to "physical game later":

**Model the game as a pure state-transition function — `(state, move) → state` — and keep that rules engine strictly separate from presentation.**

This is the boardgame.io model, and it is not just a coding convenience. A clean rules engine simultaneously gives you:

- **A testable core.** You can assert legal moves, end conditions, and scoring without a UI.
- **Free balance simulation.** You can run the engine ten thousand times with random or scripted agents to get expected values, win-rate-by-position, and game-length distributions — see `references/balance-and-simulation.md`.
- **Free AI opponents and bots**, which double as tireless playtesters.
- **A head start on the physical rulebook.** A correct rules engine *is* the formal specification of the game. The English rulebook is a faithful natural-language rendering of the same state machine. Designing the engine first means the rulebook can never silently disagree with how the game actually plays.

So the recommended pipeline (detailed below) builds the digital prototype before the physical one — because digital iteration is instant, simulation is automatic, and the physical version inherits a rules core that has already been pounded on by ten thousand simulated games. Physical transition then becomes a deliberate, separate phase (`references/physical-transition.md`), where the main job is re-examining everything the computer was silently doing for the players (upkeep, scoring, shuffling, hidden information, legal-move enforcement).

## Design convictions (state these directly, with reasoning)

These are not personal opinions; they are the documented near-consensus of the design craft. State them with confidence and explain the *why* — that is what separates this skill from generic advice.

1. **Design the core loop before anything else.** Before theme, components, or even mechanics: what is the small action a player repeats over and over, and why is *that single action*, in isolation, interesting? If the loop isn't fun, no amount of content, art, or variety rescues it. Most failed designs are loops that were never interrogated. Build and test the loop first, on paper or in code, before building anything around it.

2. **Mechanics are a means, not the destination.** "I want to make a deck-builder" is a bad starting point; it is mechanic-first design and it produces derivative games. Start from the **experience** — the fantasy, the feeling, the central decision you want players to agonize over — then *select* mechanics that produce it. The deck-builder might be the answer, but only after you know what experience you're buying with it.

3. **A game is a series of interesting decisions** (Sid Meier). A decision is interesting only when there is **no dominant option** — when multiple choices are viable and which is best depends on context, board state, and opponents. The cardinal sin of design is the dominant strategy: a line of play that is correct regardless of circumstance. When you find one in playtesting, you have not found a player exploit; you have found a design hole. Fix the game, not the player.

4. **Downtime is the silent killer — not complexity.** Players forgive complex games; they quietly resent games where they sit and wait. Most "analysis paralysis" complaints are really downtime complaints in disguise. Attack downtime structurally: shorten turns, use **simultaneous action selection** (everyone agonizes at once), keep players engaged on others' turns (drafting, reactions, betting, hidden bidding), and cap the number of decisions per turn. A heavy game with low downtime beats a light game with high downtime.

5. **Elegant rules compress; clumsy rules enumerate.** Aim for a small number of principles that generate a large number of situations, not a special-case rule for every situation. If a rule reliably needs an FAQ entry, the rule is wrong — redesign it rather than patching it. "The rules teach the game" is the target: a well-built game can be largely learned by playing it.

6. **Put randomness at the *start* of a decision, not the end.** *Input* randomness (the cards you're dealt, the dice you roll *and then allocate*, the tiles available this turn) hands the player a fresh puzzle to solve — it creates replayability and skill expression. *Output* randomness (you commit to a plan, then roll to see if it "works") creates swing and feel-bad and robs decisions of agency. When a design needs output randomness for drama, give players mitigation (rerolls, modifiers, partial successes) or reframe it as push-your-luck, where *choosing* to gamble is the decision.

7. **Theme and mechanics should reinforce each other — or you should know exactly why they don't.** When a mechanic *feels like* the thing it represents (thematic integration), the game becomes memorable and teachable; the theme carries the rules in players' memory. Pure abstracts (Chess, Azul, Hive) are completely legitimate — but then commit to the abstraction and don't bolt on a pasted-on theme that the mechanics ignore. The failure mode is the in-between: a theme that promises an experience the mechanics don't deliver.

8. **Kingmaking is a design failure, not a player failure.** If a player who cannot win gets to decide *who does* win (by where they attack, what they block, whom they trade with), the design has a hole. Reduce it by making the decisive end-game outcomes depend on **simultaneous or hidden** choices, by limiting purely-destructive late-game actions, or by ensuring trailing players still have a self-interested reason to optimize. Don't hand the problem to "players should just play correctly."

9. **Asymmetry is a replayability multiplier and a balancing nightmare — in that order.** Variable player powers / factions are one of the highest-leverage tools for replay value. They also multiply your balancing surface combinatorially and are a notorious sink of development time. Discipline: **get the symmetric core balanced first**, then layer asymmetry on top of a known-good baseline, balancing each faction against that baseline rather than against each other.

10. **Simulate subsystems; playtest systems.** This is the most important boundary for a quantitatively-minded designer, and getting it wrong wastes enormous effort. Monte Carlo simulation and expected-value math are *excellent* for **isolated** questions: is this card over- or under-costed? How many turns until the bag is exhausted? What's the variance on this attack roll? They are **useless** for "is the whole game balanced" or "is it fun," because those depend on adaptive strategic players, emergent interaction, and feel — which simulation can only crudely caricature. Know which question you're asking. Use `scripts/balance_sim.py` for the first kind; use human playtesting (`references/playtesting.md`) for the second.

## Genuine disagreements (present the spectrum; don't fake a consensus)

When a design question lands here, lay out the camps and their reasoning rather than pretending there's one right answer. Picking a side as if it were settled is exactly the failure mode this skill exists to avoid.

- **Catch-up / rubber-band mechanics.** One camp: essential to keep all players in contention and the ending tense. Other camp: they punish skilled play and insult the leader's good decisions; better to *disguise* scores (hidden VP) or give trailing players more *options* than to hand them points. Both are held by serious designers. Match the choice to your audience and game length.
- **Luck.** Euro tradition minimizes it to foreground skill; thematic/"Ameritrash" tradition embraces it as the engine of story and swing. Neither is more "mature." A luck-heavy game can be a better *experience* than a luck-light one.
- **Player elimination.** Modern euro orthodoxy: never acceptable, no one should watch the last 40 minutes. Counter-view: fine in short games and social/party games where elimination *is* the drama (and the eliminated player just starts the next round). Length is the deciding variable.
- **Direct conflict / "take-that."** Drives interaction, tension, and memorable moments — but risks feel-bad, kingmaking, and pile-on. The right amount depends entirely on the social contract of the target audience.
- **Complexity / "weight."** Heavier is not better or worse — it is a *targeting* decision. The crime is mismatch: a filler with the rules overhead of a war game, or an epic that resolves in one shallow decision.
- **Design process: theme-first vs. mechanics-first.** Reiner Knizia famously builds elegant mechanics and finds a theme later; Elizabeth Hargrave (Wingspan) starts from a subject she loves. Both produce great games. Don't impose one process as correct.

## The design pipeline

Work through these phases. Early phases are cheap and decisive; don't rush them to get to components. For any phase, read the referenced files as needed — they exist so this file stays lean. **For a concrete end-to-end walkthrough of all eight phases on one small design (problems surfaced and fixed in sequence), read `references/worked-example.md` — it makes this pipeline legible.**

### 1. Define the experience (not the mechanic)
Pin down three things: the **fantasy/feeling** (what is it *like* to play? what's the player pretending to do or be?), the **central decision** (what is the recurring agonizing choice?), and the **target aesthetic** — *which kind of fun* you're going for (challenge? fellowship? expression? discovery? sensation?) and the intended emotional arc of a session. Everything downstream serves these. Resist naming mechanics yet. This phase is the one systems-minded designers rush; don't — see `references/experience-and-aesthetics.md` (MDA, the 8 kinds of fun, theme integration, session arc). A mechanically sound game that evokes nothing is the characteristic failure of skipping it.

### 2. Design the core loop and the engine of progress
Specify the smallest repeated unit of play and *why it is interesting in isolation* (convictions 1, 3). Then specify how the game *progresses and ends* — the victory condition and the rising tension that drives toward it. Sketch the simplest possible version that still contains the central decision. If you can't make the bare loop interesting, stop and fix that before adding anything.

### 3. Select mechanic families
Now — and only now — choose mechanics that *produce* the loop and experience. Use the selection guide below to decide which reference file(s) to read. Most good games combine 2–4 families (e.g., worker placement + engine building, or drafting + set collection). Read the relevant references for design levers, balance math, failure modes, and digital-implementation notes. Also decide your **player-count range and whether solo matters now** — both shape the rules and are expensive to retrofit (`references/scaling-and-solo.md`): player count changes a game's dynamics (downtime, contention, length), not just its arithmetic, and a solo/Automa mode is a design archetype chosen here, not bolted on later.

### 4. Specify the rules as a state machine
Write down: the **components/tokens**, the **game state** (what must be tracked), the **legal moves** from any state, the **turn/phase structure**, and the **end condition + scoring**. This specification is simultaneously your digital data model AND the skeleton of your rulebook. Aim for compression (conviction 5).

### 5. Build the digital prototype
Implement the state machine as a pure `(state, move) → state` rules engine, separated from any UI. Default to **boardgame.io** (TypeScript/JavaScript) for turn-based games — it gives state management, multiplayer, bots, and a debug/prototyping panel almost for free. For richer real-time or animated presentation, drive the same rules core from a Godot / Unity / LÖVE client (the user has an indie-game-dev skill for that layer). See `references/digital-implementation.md`. Build the **engine before the interface** — a text/CLI or debug-panel front end is enough to start playing.

### 6. Balance the subsystems with math and simulation
With a rules engine in hand, attack the *isolated* balance questions quantitatively (conviction 10): cost curves for cards, EV and variance for dice/draws, resource flow rates, game-length distribution, first-player advantage by position. Use `scripts/balance_sim.py` and the techniques in `references/balance-and-simulation.md`. Fix dominant strategies the math reveals.

### 7. Playtest the system
Simulation cannot tell you if the game is *fun* or whole-game balanced — only humans (and, partially, trained agents) can. Run the staged playtest process in `references/playtesting.md`: solo / self-play, then bot self-play to flush out degenerate lines, then friendly human tables, then **blind** playtests (strangers, rulebook only, no designer present). Measure decision diversity, win-rate by strategy and seat, game length, and downtime — not just "did people smile." Test **every player count** (dynamics differ by count) and the **on-ramp** explicitly: the 2-minute-teach test, the first-turn test, and (digital) tutorial completion — a great game with a brutal first five minutes loses players before its depth shows (`references/scaling-and-solo.md`, `references/onboarding-and-teaching.md`).

### 8. Transition to physical (deliberately, when the design is locked)
Only once the digital design is stable. The job here is to re-surface everything the computer was doing invisibly — upkeep, shuffling, scoring, legal-move enforcement, hidden-information management — and make it ergonomic for humans, plus component budgets, iconography, rulebook writing, and manufacturability. See `references/physical-transition.md`. A design that's great digitally can be ruined by fiddly physical bookkeeping; this phase is where you catch that.

## Mechanic-family selection guide

Match the experience you want to the family (and reference file). Combine freely.

| You want players to… | Family | Reference |
|---|---|---|
| Build a growing combo/economy where actions feed future actions | **Engine building** | `references/mechanics-engine-building.md` |
| Gradually improve a randomized pool they draw from (evolving) | **Deck building** / bag building | `references/mechanics-deck-and-bag.md` |
| Pre-construct a personal deck/army before play, then pilot it | **Deck construction** (CCG/LCG-style) | `references/mechanics-deck-and-bag.md` |
| Compete for limited action slots, blocking each other | **Worker placement** / action selection | `references/mechanics-worker-placement.md` |
| Contest physical/spatial dominance of regions | **Area control / majority / influence** | `references/mechanics-area-control.md` |
| Make sequential picks from a shrinking shared pool | **Drafting** (pack / open / Rochester) | `references/mechanics-drafting.md` |
| Decide repeatedly whether to risk gains for more | **Push-your-luck** / risk-reward | `references/mechanics-push-your-luck.md` |
| Carry persistent, evolving state across many sessions | **Campaign / legacy / persistence** | `references/mechanics-campaign-legacy.md` |
| Optimize a low-luck multi-path point engine (euro) — or contrast with thematic/Ameritrash; or use auctions, trick-taking, tile-laying, set collection, route building, roll-and-write, cooperative, hidden movement, social deduction, negotiation/trading, or abstract strategy | **Design traditions + the rest of the mechanic catalog** | `references/tradition-euro-and-families.md` |

Cross-cutting references (read as the pipeline phase demands):
- `references/worked-example.md` — a full end-to-end walkthrough of all eight phases on one small design; read first if the pipeline feels abstract.
- `references/experience-and-aesthetics.md` — the felt-experience toolkit: MDA, the 8 kinds of fun, theme-integration depth, session emotional arc. Phase 1, and any "sound but flat" game.
- `references/scaling-and-solo.md` — player-count scaling (the 2-player problem, downtime/contention by count) and solo / Automa design archetypes.
- `references/onboarding-and-teaching.md` — setup cost, the teach, the first turn, and digital tutorial design; the first five minutes that decide retention.
- `references/digital-implementation.md` — rules-engine/presentation separation, boardgame.io patterns, state & hidden-information modeling, bots, **what digital uniquely enables**, driving Godot/Unity/LÖVE clients.
- `references/balance-and-simulation.md` — EV, probability, cost curves, Monte Carlo, the scope boundary (what sim can and cannot answer), using `balance_sim.py`.
- `references/physical-transition.md` — digital→physical: component budgets, rulebook craft, iconography, manufacturability, what digital silently hid.
- `references/playtesting.md` — staged playtest methodology, what to measure, bot playtesting, reading the data.

## Bundled tools

- `scripts/balance_sim.py` — a reusable Monte Carlo / expected-value harness for **subsystem** balance questions (dice pools, deck draws, resource curves, game-length estimation). Self-contained (Python stdlib only). Run `python scripts/balance_sim.py --help`. Always pair its output with the scope caveat in conviction 10.
- `assets/boardgame_io_template/` — a minimal, heavily-commented boardgame.io game-logic template (verified against boardgame.io 0.50.2) showing the pure `(G, ctx, move)` pattern, phases/turns, simultaneous actions, hidden state via `playerView`, injected RNG, and bot enumeration. Copy it as the starting skeleton for a digital prototype. (boardgame.io is the dominant open-source turn-based framework but only lightly maintained — pin your version.)

## Scope

This skill covers **turn-based and simultaneous-turn** board and card games — the families in the selection guide and catalog. It does **not** cover real-time/dexterity/action games (the rules-engine and turn-structure assumptions don't fit) or pure video-game design (level design, real-time combat, narrative writing) — for the latter, the user's separate indie-game-dev skill applies, and this skill is only relevant for the *board-game-derived* digital builds described here. Say so honestly rather than stretching board-game frameworks over a real-time design.

## How to actually respond

- If the user gives a vague idea ("a game about beekeeping where you draft flowers"), don't jump to components. Walk phases 1–3: name the experience and central decision, interrogate the core loop, *then* talk mechanics. Be the designer who asks "what's the interesting decision here?" before "what's on the cards?"
- Be opinionated where the convictions are firm (cite the *why*), and explicitly even-handed where the disagreements list says to be. Calling a contested choice "settled," or hedging on something that's actually settled, are equal failures.
- When the user is building digitally, push the rules-engine/presentation separation early — it's cheap to adopt up front and expensive to retrofit, and it's what makes the physical transition tractable later.
- Reach for `balance_sim.py` and EV math for sharp subsystem questions; reach for playtesting advice for "is this fun / fair overall." Never present a simulation as proof the *game* is balanced.
- Match advice to the game's weight and audience — don't impose heavy-euro machinery on a 15-minute filler or a party game (the crime is mismatch, not weight). Consider player-count scaling and solo/onboarding when they're in scope rather than treating them as afterthoughts.
- When a game is described as mechanically fine but "flat" or "not grabbing people," look at the experience/aesthetics layer and the on-ramp before touching the core mechanics — that's usually where the problem is.
- Ground recommendations in real games when it helps (Dominion, Agricola, Wingspan, Brass, Power Grid, Splendor, Spirit Island, Pandemic, Magic, 7 Wonders, Catan, Azul, Gloomhaven, Root) — the canon is shared vocabulary, and "so many design problems have been solved before."
