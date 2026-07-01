# Deck Systems: Deck Building, Deck Construction, Bag Building

These three are siblings: in all of them you **shape a randomized pool that you then draw from**, so the act of improving the pool is itself the strategic layer. But they differ in *when* you shape it, and that difference drives everything.

| | When you build | The decision | Archetype |
|---|---|---|---|
| **Deck building** | During play, repeatedly | Which card to add *now*, given my current deck | Dominion, Clank!, Star Realms |
| **Deck construction** | Before play (often a metagame) | Which 40–60 cards form a coherent strategy | Magic, Netrunner, KeyForge (auto-built) |
| **Bag building** | During play, with physical tokens | Same as deck-building but with bag-pull randomness | Orléans, Altiplano, Quacks of Quedlinburg |

## Deck building (evolving during play)
**Central decision:** every card you add is permanent and dilutes your draw. Adding a powerful card is good; adding a card that clutters your hand when you don't want it is bad. The decision is *deck thinning and consistency*, not just power.

Design levers:
- **The trash/cull mechanism is as important as the gain mechanism.** Without a way to remove weak starting cards, decks only ever get more diluted. Whether, how fast, and at what cost players can thin their decks is the central balance dial. Dominion's Chapel (cheap mass-trashing) is so strong it warps every game it's in — a lesson in how powerful culling is.
- **Starting deck = the tutorial.** The 10-card starter teaches the economy. Make it deliberately mediocre so improvement is felt.
- **Shuffle frequency and deck size** control how often a bought card actually shows up. A 40-card deck buries your bombs; a 15-card deck plays them constantly. This is the consistency dial and it's quantifiable (see math).
- **Trash-for-value and on-trash effects** turn the dilution problem into a resource, adding depth.

Balance math (a `balance_sim.py` natural):
- **Probability a card shows up next hand** ≈ hypergeometric: drawing a hand of `h` from a deck of `n` with `k` copies of the card, P(at least one) = `1 - C(n-k, h) / C(n, h)`. This tells you whether a "combo piece" is reliable enough to build around.
- **Expected economy per turn** under a buying strategy → simulate the deck cycling to compare strategies' ramp.
- **Deck velocity**: turns per full cycle ≈ `deck_size / cards_drawn_per_turn`. Card draw effects are powerful precisely because they raise velocity *and* dig for combos.

Failure modes: **the dominant buy** (one card always correct — fix its cost or effect, not the player); **diluted death spiral** (no culling, decks become unplayable mush); **deck-building solitaire** (no interaction — add attacks, a shared diminishing market, or a race).

## Deck construction (pre-built, the CCG/LCG family)
**Central decision:** before you ever sit down, choose ~40–60 cards that form a *coherent engine* with a consistent game plan, then pilot it against unknown opponents. The metagame (what everyone else is building) is part of the design surface.

Design levers:
- **The mana/resource curve is the spine.** Players need a smooth cost curve so they have plays every turn. Your card set must *support* good curves at every archetype, or one archetype dominates.
- **Color/faction pie + restrictions** create deckbuilding tension: access to everything = no decisions. Restrictions (color identity, faction loyalty, deck-size minimums, copy limits) are what make construction a puzzle.
- **Answers must exist for threats.** A healthy constructed environment has counterplay: removal, disruption, defensive options. A format with threats but no answers degenerates into a race.
- **Rarity ≠ power (resist pay-to-win).** If rare cards are strictly stronger, you've designed a wallet-measuring contest, not a game. The LCG model (Netrunner, Arkham) fixes the card pool per box specifically to decouple money from power — a defensible ethical and design stance.
- **Variance is a feature here**, not a bug: the draw order of a constructed deck is the game's drama. But give consistency tools (card selection, tutors, mulligans) so games aren't decided purely by draw.

Balance: this is the hardest family to balance because the design space is the *combinatorial space of decks*, not individual cards. You cannot simulate it fully. Tools: cost-to-effect "rate" curves per card, mana-curve analysis, and heavy human metagame playtesting. Power creep across releases is the chronic disease — each new set must be *interesting* without being strictly stronger, or you obsolete your own back catalog.

## Bag building (deck building with token pulls)
Mechanically deck building, but you draw tokens/cubes from a bag rather than cards from a deck. The differences that matter:
- **Pull-then-act** (Quacks: push your luck on each pull) vs. **pull-a-hand** (Orléans: draw several, place as workers). The first fuses bag building with push-your-luck (see that reference).
- Bags are **harder to thin** physically (you can't easily search a bag), so removal mechanics feel different and "bag pollution" (bad tokens you're forced to keep) is a sharper tension.
- Tokens carry less information than cards (no rules text), so complexity must live in the board, not the token.

## Digital implementation
All three are trivially better digitally for the bookkeeping: shuffling, drawing, and discard-pile tracking are free and bulletproof. Model the deck/bag as an ordered/multiset collection in game state; **keep it in hidden state and expose only the player's hand via `playerView`** (boardgame.io) so clients can't peek. The shuffle must be server-side for any competitive multiplayer. This family is the single best place to start a digital prototype because the rules engine is small and the simulation payoff (hypergeometric questions, strategy win-rates) is immediate.

## Physical transition
Card-based versions transition cleanly (people are used to shuffling). Watch for: shuffle fatigue (small evolving decks get shuffled constantly — annoying), and the deck-tracking burden of on-trash/peek effects. Bag builders are very physical-friendly *because* the bag enforces hidden randomness for free — sometimes the physical version is the better one.

## Canon
Dominion (the urtext), Star Realms / Hero Realms (combat deckbuilder), Clank! (deckbuilder + push-your-luck + area movement), Slay the Spire (digital deckbuilder, roguelike — study the run structure), Magic: the Gathering & Netrunner (construction), Arkham Horror LCG (co-op construction), Orléans & Quacks of Quedlinburg (bag building).
