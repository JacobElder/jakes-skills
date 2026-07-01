# Design Traditions & the Rest of the Mechanic Catalog

Two jobs here: (1) explain the **euro vs. thematic** traditions as design *philosophies* (not mechanics), since "euro game" names a worldview; and (2) give working coverage of the **major mechanics that don't have their own file**, so the skill is comprehensive. Read the dedicated files for the headline families; read here for everything else and for the big-picture stylistic choice.

---

## Part 1: The traditions (a philosophy choice, not a mechanic)

### The Euro tradition ("German-style")
A design *value system*, characterized by: **low/input-only randomness**, **no player elimination**, **indirect interaction** (you compete for resources and positions, you rarely attack), **multiple paths to victory** ("point salad"), **resource conversion engines**, and **tight, dry, well-balanced systems** where skill dominates. The aesthetic prizes elegance and fairness. Agricola, Caylus, Terra Mystica, Brass, Puerto Rico, most worker-placement and engine games.

Euro design convictions: minimize feel-bad and king-making; keep everyone in until the end; make every decision matter; let the math be tight. The critique of euros (from the other camp): they can feel like solitaire-in-parallel, "multiplayer solitaire," with thin interaction and no story — abstract optimization wearing a thin theme.

### The Thematic / "Ameritrash" tradition
The opposite value system: **embrace randomness as drama**, **direct conflict and player elimination are fine**, **strong narrative and theme** drive everything, **dice and cards create swing and story**, **asymmetry and special powers** abound. The point is the *experience and the story it generates*, not optimization. Twilight Imperium, Blood Rage, Dead of Winter, most Fantasy Flight games, Cosmic Encounter.

Thematic convictions: a great *moment* beats a balanced spreadsheet; swing and comebacks make stories; theme should saturate every rule. The critique (from euros): swingy, long, sometimes decided by luck or politics rather than play.

### The point that matters for *your* design
Neither is better — they optimize for different fun (SKILL.md disagreements list). The failure is **incoherence**: a game that wants euro tightness *and* thematic swing usually delivers neither. Pick a center of gravity. The modern "hybrid" / "Euro-American" space (Scythe, Root, Brass, Spirit Island, Lisboa) is real and fertile, but those games still have a clear primary allegiance — they borrow from the other side around a committed core. Know yours.

---

## Part 2: Catalog of remaining mechanics

For each: the experience, the central decision, key levers, and the headline failure mode. Combine freely with the headline families.

### Auction / Bidding
- **Experience / decision:** price discovery under uncertainty — what is this *worth to me*, and what will others pay? Bidding is the purest "reveal your valuation" mechanic.
- **Levers:** open vs. blind bid; once-around vs. multi-round; English (ascending) vs. Dutch (descending, Medici/Modern Art) vs. sealed vs. fixed-turn-order. **Closing rule** is everything (when does bidding stop?).
- **Failure mode:** *count-up auctions* (slow, +1, +1, +1 — high downtime, low decision); the **winner's curse** (winner systematically overpays). Fix slowness with simultaneous/sealed bids; fix winner's curse with information or compensation to losers. Money/auction games risk the player with the most cash snowballing.
- **Canon:** Modern Art, Ra, Medici, Power Grid (market auction), High Society, For Sale.

### Trick-taking
- **Experience / decision:** play a card to a trick under follow-suit constraints, reading what's been played and managing your hand's arc across the round. A 400-year-old skeleton with endless modern reskins.
- **Levers:** trump rules; **bid/contract** (predict your tricks — Spades, Wizard) vs. evasion (avoid tricks — Hearts) vs. "exactly N" (the most interesting — over- and under-perform both punish); partnerships; card-passing.
- **Failure mode:** randomness of the deal dominating skill (mitigate with passing, bidding, or hand selection); a "void" snowballing one player. Modern designs (The Crew, cooperative trick-taking) reinvent the space — a hot area.
- **Canon:** Hearts, Spades, Wizard, The Crew (co-op), Tichu, Cabo-adjacent, The Fox in the Forest (2p).

### Tile-laying / Pattern-building
- **Experience / decision:** spatial puzzle — place a piece to optimize adjacency/pattern now while shaping future placements. Tactile and visible.
- **Levers:** open drafting of tiles (Azul) vs. blind draw (Carcassonne); scoring on adjacency, enclosure, sets, or patterns; shared board (interactive — Carcassonne) vs. personal board (parallel — Azul, Patchwork).
- **Failure mode:** draw luck swinging personal-board games; runaway spatial advantage. Drafting the tiles (Azul) converts draw luck into a decision — a strong fix.
- **Canon:** Carcassonne, Azul, Patchwork, Cascadia, Kingdomino, Bärenpark.

### Set collection
- **Experience / decision:** gather combinations for escalating rewards; commit to a set vs. stay flexible. Rarely a whole game — a *scoring layer* bolted onto drafting, tile-laying, etc.
- **Levers:** linear vs. exponential set rewards (exponential = high commitment, swingy); diversity sets (one of each) vs. quantity sets (many of one); public vs. hidden collections.
- **Failure mode:** one set type dominating; "I can't complete it" dead-ends. Pair with a flexible acquisition mechanic so pivots stay possible.
- **Canon:** Ticket to Ride (route sets), Sushi Go!, Splendor (gem sets → cards), Ticket to Ride, Wingspan (bonus sets).

### Route / Network building
- **Experience / decision:** connect points across a map efficiently, racing opponents for shared edges/nodes. Spatial optimization + denial.
- **Levers:** shared edges (blocking, tension — Ticket to Ride) vs. private networks; demand/contract fulfillment; the classic *Brass*-style "build the network, then flow goods through it."
- **Failure mode:** a single optimal route being obvious; blocking creating kingmaking. Hidden objectives (TtR's secret tickets) add tension and reduce solved play.
- **Canon:** Ticket to Ride, Brass: Birmingham/Lancashire, Power Grid (network + auction + engine), Age of Steam.

### Dice placement / Roll-and-write / Flip-and-write
- **Experience / decision:** input randomness (the roll/flip) hands everyone a shared puzzle; allocate the results onto your sheet/board optimally. Simultaneous resolution = near-zero downtime, which is why roll-and-writes exploded.
- **Levers:** shared dice everyone uses (Railroad Ink, Welcome To) vs. drafted dice; "use the value" vs. "use the placement"; combo sheets that reward sequencing.
- **Failure mode:** a sheet with a dominant filling order; players with no agency over the randomness. Drafting or a choice of *which* die to use restores agency.
- **Canon:** Qwixx, Railroad Ink, Welcome To..., Ganz schön clever ("That's Pretty Clever"), Cartographers.

### Cooperative
- **Experience / decision:** the table vs. the game; shared problem-solving against an automated, escalating threat. The opponent is a *system*, which you (the designer) play via rules.
- **Levers:** the AI/threat engine (how the game "plays itself" against you — Pandemic's outbreak cascade); information asymmetry (Hanabi: you see others' hands, not yours — the anti-quarterbacking masterstroke); difficulty knobs.
- **Failure mode — the cardinal one:** **quarterbacking** (one dominant player solves everyone's turns; others are spectators). Combat it with **hidden information** (private hands/roles no one else may fully see — Hanabi, The Crew), simultaneous action, or per-player secret objectives. A solvable co-op (an optimal line exists and the table finds it) dies once "solved" — build in variance and hidden info so each game is a fresh puzzle.
- **Canon:** Pandemic, Hanabi (information-restriction genius), Spirit Island (deep, anti-quarterback via complexity), The Crew, Gloomhaven (co-op campaign), Forbidden Island/Desert.

### Hidden movement / Deduction
- **Experience / decision:** one hidden player evades; seekers triangulate from clues. Asymmetric cat-and-mouse; the tension is *partial information*.
- **Levers:** the clue/reveal cadence (how much the hunters learn each turn); the hidden player's bluffing options; the map's chokepoints.
- **Failure mode:** the hidden player being un-catchable or doomed (tune the information rate); seeker downtime while the hidden player plots. Apps now often run the hidden side, fixing logistics.
- **Canon:** Scotland Yard, Fury of Dracula, Letters from Whitechapel, Specter Ops.

### Social deduction / Hidden roles
- **Experience / decision:** who is lying? Hidden teams; reading faces and contradictions; persuasion. The "game" is mostly *the conversation*; the rules are scaffolding for social play.
- **Levers:** information distribution at setup (who knows what — the heart of the design); accusation/voting structure; whether eliminated players stay engaged.
- **Failure mode:** **player elimination boredom** (dead players watch — fix with short rounds or post-death roles); first-night randomness deciding the game; "quiet players lose unfairly." Best modern designs (Secret Hitler, Avalon) give *everyone* actionable information so silence isn't a strategy.
- **Canon:** Werewolf/Mafia, The Resistance / Avalon, Secret Hitler, Blood on the Clocktower (the modern gold standard — eliminated players keep playing), One Night Ultimate Werewolf (no elimination).

### Negotiation / Trading / Diplomacy
- **Experience / decision:** the deal — what's this worth to me, to them, and can I get a better split? The mechanics create *reasons to talk*; the game is largely played in the conversation and the broken (or kept) promise.
- **Levers:** what's tradeable and how unequal players' needs are (asymmetric needs drive deals — you have what I need); whether deals are **binding** (enforced by rules) or **non-binding** (promises can be broken — Diplomacy's signature cruelty); turn structure that creates trade windows; whether the table negotiates openly or in private.
- **Failure modes:** **kingmaking and pile-on** (negotiation is distributed kingmaking by nature — `references/mechanics-area-control.md` fixes apply); **the dominant trader / table politics** deciding the game over play; **feel-bad** from broken promises souring the group (match to audience — some tables love the betrayal, others are wrecked by it); the **two-player collapse** (negotiation needs 3+ to have leverage and triangulation — at 2 it's just an ultimatum). Scales interaction up dramatically but is the *least* simulable family (it's pure human modeling — `references/balance-and-simulation.md`: playtest, don't sim).
- **Canon:** Catan (gateway trading), Sidereal Confluence (the negotiation-engine masterclass, near-zero downtime via simultaneous trading), Bohnanza (trading + hand-order), Chinatown, A Game of Thrones / Diplomacy (non-binding deals, betrayal), Monopoly (cautionary: trading bolted onto a roll-and-move).

### Abstract strategy (perfect-information, little/no theme or luck)
- **Experience / decision:** pure positional calculation — no hidden info, no randomness, the whole state on the table. Mastery and depth from simple rules. Chess, Go, Hive, Azul-as-abstract, Santorini, Onitama, GIPF series.
- **Levers:** rules **compression** is the entire game (conviction 5 in its purest form — Go's handful of rules generate unbounded depth); the **branching factor / decision space** (too low = solved/shallow, too high = AP and opacity); **first-player advantage** is acute with no luck to mask it — mitigate with a compensation rule (komi in Go), a balancing/pie rule (one player divides, the other chooses sides/first move), or simultaneous setup; **draw/stalemate avoidance** (a tie-prone abstract feels unresolved — add a tiebreak or a forced-progress rule); the **repetition/loop problem** (ko-style rules to prevent infinite cycles).
- **Failure modes:** **solvability** (a small abstract that a player "solves" dies — needs enough depth/branching to resist); **runaway from a single early mistake** (no luck to claw back — design so leads can be contested, or keep games short); **opacity** (deep but illegible = nobody can evaluate a position = no fun). Abstracts opt out of the theme ladder entirely (`references/experience-and-aesthetics.md`) and that's elegant, not lazy — but you forgo theme's teaching and memorability aids, so the *systems* must carry all the appeal. Digital is a natural fit (perfect info + no hidden state = trivial to implement and to give a strong AI), and abstracts are where classical game-tree AI (minimax/MCTS) genuinely plays well, unlike most board games.
- **Canon:** Chess, Go, Hive, Onitama, Santorini, Azul, Yinsh/Dvonn (GIPF project), Quoridor, Hex (famous for the pie rule).

---

## Combining mechanics (the real craft)
Most published games are **2–4 families fused around one core loop.** The skill is choosing families whose decisions *reinforce* rather than compete for the player's attention. Good fusions share a currency or a tension:
- Worker placement **+** engine building (Everdell, Viticulture) — placement feeds the engine.
- Drafting **+** set collection (Sushi Go, 7 Wonders) — the draft IS how you build sets.
- Deck building **+** push-your-luck (Clank!, Quacks) — the deck/bag is the risk source.
- Area control **+** card-driven hand management (Twilight Struggle, Inis) — cards launder the randomness.

The anti-pattern: bolting on a second full mechanic that demands its own separate attention budget, doubling rules overhead without deepening the core decision. If a mechanic doesn't feed or tension the core loop, cut it (SKILL.md conviction 5 — compression).
