# Physical Transition

Taking a locked digital design to a physical product. This is a *deliberate phase*, run only once the digital design is stable (rules engine settled, balance passes done, the game is fun in playtests). The core job is unusual and easy to underestimate:

> **Re-surface everything the computer was doing invisibly, and make it ergonomic for humans.**

A computer silently shuffles, enforces legality, tracks hidden information, computes scores, resolves every trigger, and remembers every rule. Humans do none of that for free. A design that's elegant on screen can be a fiddly, error-prone chore on a table — and catching that is the entire point of this phase.

## The invisible-work audit (do this first)
Go through your reducer and list every operation the engine performs automatically. For each, decide how a human will do it — or whether to redesign it away:

- **Shuffling / randomization:** fine for cards (people shuffle) and bags (great — the bag *is* the RNG); painful for "shuffle this 60-card deck every round." Reduce shuffle frequency or use bags/dice.
- **Legal-move enforcement:** the engine rejected illegal moves silently; now players can make them by accident. Rules and iconography must make illegal moves *obviously* illegal, or you'll get rules disputes. This is a major argument for **rules compression** (SKILL.md conviction 5) — fewer, more general rules are self-enforcing.
- **Upkeep & passive triggers:** the engine never forgets "each turn, gain 1 if you have ≥3 X." Humans forget constantly. **Convert push triggers to pull triggers** wherever possible: make effects resolve *when the player takes an action* rather than as background upkeep. Missed-trigger-proofing is one of the biggest physical-design wins.
- **Scoring:** continuous digital scoretracking becomes either a score track (good, visible) or end-game counting (slow, error-prone — minimize the number of distinct scoring categories, the "point salad tax").
- **Hidden information:** the screen hid opponents' hands automatically; physically you need player screens, careful card-back design, and "don't flash your cards" ergonomics.
- **State you can see at a glance:** the screen could show derived info; physically, prefer game state that's **self-evident on the table** (placed meeples show blocking; cubes in regions show control). Designs whose state is physically legible need far less bookkeeping.

## Component design
- **Component budget = cost.** Every unique component type adds tooling and manufacturing cost. Consolidate: can two token types be one? Can a board zone replace a card? Publishers think in component counts; so should you.
- **Iconography over text.** Physical games can't afford reminder text on everything, and language-independent iconography widens the market. Build an icon language; test that it's learnable. Text-heavy cards are a translation and a teaching burden.
- **Bits should afford their use.** Tactile, distinct, colorblind-safe (never rely on color alone — add shape/pattern). Insert/storage solutions matter for the play experience (setup/teardown time is real friction).
- **Table footprint & ergonomics:** reach, shared-area access, how the board reads from each seat. A digital layout has no physical reach constraints; a table does.

## The rulebook (it's a deliverable, not an afterthought)
Because you built the rules engine first, the rulebook is largely a *transcription*, but a real craft:
- **Structure:** overview/goal → components → setup → turn structure → end & scoring → edge cases/FAQ → reference card. Lead with the *goal* (players need the "why am I doing this" before the "how").
- **Teach in the order of play**, not the order of the codebase. The reducer's structure is logical; the rulebook's structure is pedagogical.
- **A one-page player aid / reference card** carries the turn structure and icon key. If your game needs one and you can't fit it on a card, the game may be over-complex (conviction 5 again).
- **Worked example of a turn** beats paragraphs of prose.
- **Test the rulebook the way you test the game: blind.** Hand it to strangers with no designer present (see `playtesting.md` — blind playtesting). Every question they ask is a rulebook bug. This is non-negotiable and catches what you're too close to see.

## Manufacturing & production realities
- **Standard component formats are cheaper** (poker/bridge card sizes, standard meeple/cube/die shapes, standard board folds). Custom shapes/plastics cost real money and lead time.
- **Print-and-play first.** Before any manufacturing, your physical prototype is paper, hand-written cards, and borrowed bits from other games. Iterate there; it's nearly free.
- **Card count, board size, and minis are the big cost drivers.** A wall of unique minis looks great and prices you out of many buyers' hands; know your market tier.
- **Legacy/campaign consumables** (stickers, sealed boxes, destructible components) are a distinct production cost and logistics problem — budget them explicitly (see `mechanics-campaign-legacy.md`).
- **Accessibility:** colorblind-safe palettes, readable type sizes, and not relying on a single sensory channel aren't just ethics — they're market reach.

## When the physical version should *lead*
Sometimes physical is the better medium and you should let it shape the design:
- **Push-your-luck and dexterity**: the tactile reveal/clatter beats a screen.
- **Bag building**: the bag enforces hidden randomness for free and feels great.
- **Social deduction / negotiation**: the *table talk* is the game; digital often weakens it.
- **Self-evident spatial state** (area control, tile-laying): the board carries the bookkeeping at no cost.
If your game is one of these, don't over-invest in the digital client — use digital for *design iteration and simulation*, but plan for physical as the shipping medium.

## The hybrid escape hatch
For designs drowning in bookkeeping (heavy engines, legacy, complex upkeep), an **app-assisted physical game** keeps the tactile play while offloading the invisible work to a companion app (setup, scoring, AI opponent, legacy state, campaign logic). This is a legitimate and growing category, and it's the natural endpoint of digital-first design — you already *have* the rules engine; ship it as the app and let the table hold the bits. Decide consciously whether you're making a pure-physical game, a pure-digital game, or a hybrid — each is a different product.
