# Drafting

**The experience:** reading a shrinking pool of options, weighing what you want against what you're handing your neighbor, and watching a plan emerge from picks rather than building it up front.

**Central decision:** the *double optimization* — pick the card best for me **and** consider what I'm denying / passing to opponents. Great drafting decisions are rarely "take the best card"; they're "take the card whose value-to-me minus value-to-the-player-I'm-feeding is highest."

## How it works
Players make sequential selections from a common, depleting set. The pool shrinks as everyone picks, so later picks are constrained by earlier ones (yours and others'). 7 Wonders, Sushi Go!, Magic booster draft, Blood Rage, Fairytale, It's a Wonderful World.

## The draft formats (pick deliberately — they feel completely different)
- **Pack/booster draft (pick-and-pass):** everyone gets a hand, picks one, passes the rest; repeat until packs are empty. (7 Wonders, Sushi Go!, Magic.) **Near-zero downtime** because everyone picks simultaneously — a top-tier anti-downtime structure. Direction of passing alternates by round so you feed different neighbors.
- **Open/market draft (Rochester-lite):** a shared face-up market (a "river" or display); players take turns taking one. (Splendor's cards, Century, Sushi Go Party's menu.) More information, more interaction, more downtime (sequential), more denial-targeting.
- **Rochester draft:** an entire pack laid face-up and drafted one at a time in turn order — maximal information, maximal denial, maximal downtime. Rare in published games for the downtime reason; great for high-skill formats.
- **Snake/serpentine order** (1-2-3-3-2-1): equalizes pick advantage across rounds; standard for fairness in open drafts.

## Design levers
- **What's drafted.** Cards that go into an engine (7 Wonders — drafted cards build your tableau), into a deck (Magic — then you play the deck), into immediate scoring (Sushi Go — set collection resolved that round), or as actions. The *destination* of the pick determines the depth.
- **Wheel/return.** In small packs, will a card "wheel" (come back around to you)? Designing pack size vs. player count controls whether players can speculate on cards returning — a deep skill layer.
- **Signaling.** Good drafts let players read what's open ("this color is being cut") and pivot. This emergent communication is a major source of skill; preserve it by making archetypes legible.
- **Hate-drafting headroom.** Should taking a card purely to deny it ever be correct? A little = healthy interaction; a lot = feel-bad and sub-optimal boards. Tune the value gap between "best for me" and "best to deny."
- **Set-collection / combo payoffs** drafted toward (Sushi Go's maki/dumpling sets) create commitment and "do I stay my course or pivot" tension.

## Balance math
- **Pick equity (snake check):** in snake order, sum each seat's expected pick-quality to confirm no seat is systematically advantaged. Simulate with a card-value model.
- **Replacement value.** A card's draft value isn't its raw power — it's power *minus the best remaining alternative* you'd get on the wheel. This is why "best card in a vacuum" ≠ "best pick." Model it as the gap to the next-best available.
- **Archetype openness.** Simulate many drafts with greedy archetype-seeking agents; if one archetype wins regardless of contention, it's over-supported (everyone can draft it without competing). You want archetypes to be *contested* so signaling matters.

## Failure modes
- **The first-pick-decides problem:** if pick 1 dominates the whole game, the draft is a coin flip on pack contents. Flatten the top of the power curve.
- **Forced lanes:** if archetypes don't overlap, players never compete for the same cards and the "double optimization" collapses into solitaire. Ensure cards are wanted by multiple strategies.
- **Information overload downtime** in open/Rochester formats — mitigate with smaller markets or pick-and-pass instead.
- **Pivot punishment too harsh:** if committing early then being cut is fatal, players are punished for the signaling reads the game is supposedly rewarding. Leave pivot outs.

## Digital implementation
Pick-and-pass drafting is *much* easier digitally — no physical pack-passing logistics, and you can enforce simultaneous picks with a clean reveal, eliminating the table-management overhead that limits physical drafts. Model: a set of hands rotating between players; each "pick" move removes one card and the engine rotates hands when all have picked. boardgame.io's simultaneous-turn support fits perfectly. Hidden information (your picks) via `playerView`. Bots that draft by a value heuristic are easy and great for testing archetype balance.

## Physical transition
Pick-and-pass transitions well but has real table friction: simultaneous secret picks need everyone to choose before revealing (a "all pick, then pass" ritual), and pack-passing is fiddly with high player counts. Open-market drafts transition more smoothly (just a shared display) but reintroduce sequential downtime. Component watch: cards must be quickly readable since players evaluate a whole hand under time pressure.

## Canon
7 Wonders (draft → tableau engine, scales to 7 players via simultaneity), Sushi Go! / Sushi Go Party! (draft → set collection, the gateway), Magic booster draft (draft → constructed deck, the deepest), Blood Rage / Rising Sun (draft → area control), It's a Wonderful World (draft → engine), Fairytale, Canvas (draft + layering).
