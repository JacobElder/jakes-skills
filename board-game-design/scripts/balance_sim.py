#!/usr/bin/env python3
"""
balance_sim.py — a Monte Carlo / expected-value harness for SUBSYSTEM balance
questions in board game design.

Scope discipline (read references/balance-and-simulation.md):
  Use this for ISOLATED questions with a clear source of randomness — a die, a
  deck, a curve, a flow rate. Do NOT use it to claim a whole game is "balanced"
  or "fun"; those depend on adaptive strategic players and must be playtested.
  Every number this prints is conditional on the model you give it. Report the
  model alongside the number, always.

Stdlib only (no numpy). Meant to be COPIED AND ADAPTED per game, not used as a
black box. The generic `simulate()` is the workhorse; the rest are worked
examples you can lift and modify.

Quick start:
    python balance_sim.py --demo        # run all worked examples
    python balance_sim.py --help
"""

import argparse
import math
import random
import statistics
from collections import Counter
from typing import Callable, List, Sequence, Tuple


# ----------------------------------------------------------------------------
# The workhorse: generic Monte Carlo with proper reporting.
# ----------------------------------------------------------------------------
def simulate(trial_fn: Callable[[random.Random], float],
             n: int = 100_000,
             seed: int = 0) -> dict:
    """Run trial_fn(rng) n times; return summary stats of the returned numbers.

    trial_fn receives a seeded Random instance (use it for ALL randomness so
    results are reproducible) and returns one numeric outcome per trial.

    Returns mean, stdev, a 95% CI on the mean, min/max, and key percentiles.
    Percentiles and the full distribution matter as much as the mean: two
    options with equal EV but different variance are a real player decision.
    """
    rng = random.Random(seed)
    results = [float(trial_fn(rng)) for _ in range(n)]
    results_sorted = sorted(results)
    mean = statistics.fmean(results)
    stdev = statistics.pstdev(results) if n > 1 else 0.0
    # 95% CI on the MEAN (standard error based), not a percentile interval.
    se = stdev / math.sqrt(n) if n > 0 else 0.0
    ci95 = (mean - 1.96 * se, mean + 1.96 * se)

    def pct(p: float) -> float:
        if not results_sorted:
            return float("nan")
        k = min(len(results_sorted) - 1, max(0, int(round(p * (len(results_sorted) - 1)))))
        return results_sorted[k]

    return {
        "n": n,
        "mean": mean,
        "stdev": stdev,
        "ci95_mean": ci95,
        "min": results_sorted[0] if results_sorted else float("nan"),
        "p05": pct(0.05),
        "p25": pct(0.25),
        "median": pct(0.50),
        "p75": pct(0.75),
        "p95": pct(0.95),
        "max": results_sorted[-1] if results_sorted else float("nan"),
        "_results": results,  # kept for histogramming / further analysis
    }


def print_summary(label: str, s: dict, hist: bool = False) -> None:
    lo, hi = s["ci95_mean"]
    print(f"\n{label}")
    print(f"  n={s['n']:,}  mean={s['mean']:.4f}  (95% CI {lo:.4f}–{hi:.4f})  stdev={s['stdev']:.4f}")
    print(f"  min={s['min']:.3f}  p05={s['p05']:.3f}  p25={s['p25']:.3f}  "
          f"median={s['median']:.3f}  p75={s['p75']:.3f}  p95={s['p95']:.3f}  max={s['max']:.3f}")
    if hist:
        _ascii_hist(s["_results"])


def _ascii_hist(results: Sequence[float], width: int = 40) -> None:
    counts = Counter(round(r) for r in results)
    if not counts:
        return
    peak = max(counts.values())
    for k in range(min(counts), max(counts) + 1):
        c = counts.get(k, 0)
        bar = "#" * int(round(width * c / peak))
        print(f"    {k:>4} | {bar} {c}")


# ----------------------------------------------------------------------------
# Closed-form helpers (use these to CHECK your simulation — they should agree).
# ----------------------------------------------------------------------------
def hypergeometric_at_least_one(n: int, k: int, h: int) -> float:
    """P(>=1 target in a hand of h drawn from n cards containing k targets).

    The 'will I draw my combo piece?' calculation. Closed form, no simulation
    needed — but great for validating a deck-draw sim.
    """
    if k <= 0 or h <= 0 or n <= 0:
        return 0.0
    if h >= n:
        return 1.0
    # P(zero targets) = C(n-k, h) / C(n, h)
    p_zero = math.comb(n - k, h) / math.comb(n, h) if (n - k) >= h else 0.0
    return 1.0 - p_zero


def binomial_at_least(n: int, p: float, j: int) -> float:
    """P(>= j successes in n independent trials at success rate p)."""
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(j, n + 1))


# ----------------------------------------------------------------------------
# Worked example 1: dice-pool outcome (EV, variance, distribution).
# ----------------------------------------------------------------------------
def demo_dice_pool() -> None:
    """How many successes from a pool? e.g. roll 5d6, a 5+ is a success."""
    pool, sides, success_on = 5, 6, 5  # 5d6, success on 5 or 6

    def trial(rng: random.Random) -> float:
        return sum(1 for _ in range(pool) if rng.randint(1, sides) >= success_on)

    s = simulate(trial, n=200_000)
    p_succ = (sides - success_on + 1) / sides
    print_summary(f"[Dice pool] {pool}d{sides}, success on {success_on}+  "
                  f"(per-die p={p_succ:.3f})", s, hist=True)
    # Validate against closed form:
    print(f"  check: closed-form mean = {pool * p_succ:.4f}; "
          f"P(>=3 successes) sim={sum(1 for r in s['_results'] if r>=3)/s['n']:.4f}, "
          f"closed={binomial_at_least(pool, p_succ, 3):.4f}")


# ----------------------------------------------------------------------------
# Worked example 2: deck-draw combo reliability (sim + closed-form check).
# ----------------------------------------------------------------------------
def demo_combo_draw() -> None:
    """P(opening hand contains >=1 of my combo piece)."""
    deck_size, copies, hand = 40, 3, 7

    def trial(rng: random.Random) -> float:
        deck = [1] * copies + [0] * (deck_size - copies)
        rng.shuffle(deck)
        return 1.0 if sum(deck[:hand]) >= 1 else 0.0

    s = simulate(trial, n=200_000)
    closed = hypergeometric_at_least_one(deck_size, copies, hand)
    print(f"\n[Combo draw] {copies} copies in a {deck_size}-card deck, opening hand {hand}")
    print(f"  P(>=1 in opening hand): sim={s['mean']:.4f}  closed-form={closed:.4f}")
    print(f"  -> design read: if your strategy NEEDS this piece turn 1, "
          f"{closed:.0%} reliability is {'probably too swingy' if closed < 0.5 else 'workable'}.")


# ----------------------------------------------------------------------------
# Worked example 3: push-your-luck optimal stopping (EV curve + bust curve).
# ----------------------------------------------------------------------------
def demo_push_your_luck() -> None:
    """A simple press-your-luck: each push draws a chip. Most chips add points,
    but 'bomb' chips bust you (lose everything banked this turn). Find the EV
    of a 'stop after k pushes' policy and the bust curve. The DESIGN GOAL is for
    the EV-optimal stopping depth to be mid-push and non-obvious."""
    # Bag: chips worth 1..4 points, plus some bombs.
    chips = [1, 1, 1, 2, 2, 2, 3, 3, 4]
    bombs = 5
    bag = chips + ["BOMB"] * bombs

    def policy_value(stop_after: int):
        def trial(rng: random.Random) -> float:
            local = list(bag)
            rng.shuffle(local)
            total = 0
            for i in range(stop_after):
                if i >= len(local):
                    break
                c = local[i]
                if c == "BOMB":
                    return 0.0          # busted: lose this turn's gains
                total += c
            return float(total)
        return trial

    print(f"\n[Push-your-luck] bag = {len(chips)} value chips + {bombs} bombs. "
          f"Policy: 'stop after k pushes'.")
    print(f"  {'k':>2} | {'EV':>7} | {'P(bust)':>8} | {'stdev':>7}")
    best_k, best_ev = 0, -1.0
    for k in range(1, len(bag) + 1):
        s = simulate(policy_value(k), n=80_000, seed=k)
        p_bust = sum(1 for r in s["_results"] if r == 0.0) / s["n"]
        print(f"  {k:>2} | {s['mean']:>7.3f} | {p_bust:>8.3f} | {s['stdev']:>7.3f}")
        if s["mean"] > best_ev:
            best_ev, best_k = s["mean"], k
    print(f"  -> EV-optimal stop ~ k={best_k} (EV={best_ev:.2f}). "
          f"If that's a flat/obvious cliff, the decision is 'solved' — add "
          f"state-dependence (board/opponents) so optimal push shifts per player.")


# ----------------------------------------------------------------------------
# Worked example 4: deck-cycling economy (compare two buying strategies' ramp).
# ----------------------------------------------------------------------------
def demo_deck_economy() -> None:
    """Tiny deckbuilder economy: start with 7 'coin(1)' + 3 'estate(0)'. Each
    turn draw 5, spend coins. Strategy A buys 'silver(2 coins, costs 3)';
    strategy B buys 'gold(3 coins, costs 5)' but can only afford it later.
    Which ramps total spending power faster over T turns? Classic 'cheap-and-
    early vs expensive-and-late' tension. (Illustrative — adapt to real cards.)"""
    def run_strategy(buy_gold: bool, turns: int):
        def trial(rng: random.Random) -> float:
            deck = [1] * 7 + [0] * 3          # coin value of each card
            discard: List[int] = []
            total_spent = 0
            for _ in range(turns):
                hand = []
                for _ in range(5):
                    if not deck:
                        deck, discard = discard, []
                        rng.shuffle(deck)
                    if deck:
                        hand.append(deck.pop())
                coins = sum(hand)
                total_spent += coins
                discard.extend(hand)
                # buy the best card affordable this turn under the strategy
                if buy_gold and coins >= 5:
                    discard.append(3)        # gold: pricier, bigger payoff
                elif (not buy_gold) and coins >= 3:
                    discard.append(2)        # silver: cheaper, steadier ramp
            return float(total_spent)
        return trial

    turns = 12
    sa = simulate(run_strategy(False, turns), n=40_000, seed=1)   # silver (cheap/early)
    sb = simulate(run_strategy(True, turns), n=40_000, seed=2)    # gold (pricey/late)
    print(f"\n[Deck economy] total coins generated over {turns} turns")
    print(f"  Strategy A (cheap silver, buys early): mean={sa['mean']:.2f}  stdev={sa['stdev']:.2f}")
    print(f"  Strategy B (pricey gold, buys later):  mean={sb['mean']:.2f}  stdev={sb['stdev']:.2f}")
    print(f"  -> if one strategy dominates across turn counts, you may have a "
          f"dominant buy. Vary `turns` (short vs long game) and re-check; confirm "
          f"with playtest vs adaptive humans.")


def run_all_demos() -> None:
    print("=" * 74)
    print("balance_sim.py worked examples — each is ISOLATED-SUBSYSTEM analysis.")
    print("Numbers are conditional on these toy models. Adapt to your game, then")
    print("confirm anything about WHOLE-GAME balance or fun via playtesting.")
    print("=" * 74)
    demo_dice_pool()
    demo_combo_draw()
    demo_push_your_luck()
    demo_deck_economy()
    print("\n" + "=" * 74)
    print("Done. Copy the relevant trial_fn, adapt it to your subsystem, and keep")
    print("the scope caveat attached to every result you report.")
    print("=" * 74)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--demo", action="store_true", help="run all worked examples")
    ap.add_argument("--dice", action="store_true", help="run the dice-pool example")
    ap.add_argument("--combo", action="store_true", help="run the deck-draw example")
    ap.add_argument("--push", action="store_true", help="run the push-your-luck example")
    ap.add_argument("--economy", action="store_true", help="run the deck-economy example")
    args = ap.parse_args()

    if args.demo or not any([args.dice, args.combo, args.push, args.economy]):
        run_all_demos()
        return
    if args.dice:
        demo_dice_pool()
    if args.combo:
        demo_combo_draw()
    if args.push:
        demo_push_your_luck()
    if args.economy:
        demo_deck_economy()


if __name__ == "__main__":
    main()
