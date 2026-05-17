# Boglehead Portfolios

The full menu of Boglehead-approved portfolios, from the canonical three-fund to the legitimate one-fund and four-fund variants.

## The three-fund portfolio (the default)

Three broad index funds, in your target stock/bond ratio:
1. **US Total Stock Market** — every publicly traded US stock, weighted by market cap (~4,000 holdings)
2. **Total International Stock Market** — developed + emerging markets outside the US (~8,000 holdings)
3. **US Total Bond Market** — investment-grade US bonds (~10,000 holdings)

Origin: Taylor Larimore, longtime Boglehead forum member, who simplified his own portfolio from 16 funds to 3 after reading Bogle. Written up in his book *The Bogleheads' Guide to the Three-Fund Portfolio*.

### Why three?

Not magic. The three asset classes (US stocks, international stocks, US bonds) cover the bulk of investable global equity and high-quality fixed income at near-zero cost. Adding more funds (REITs, small-cap value, emerging markets, gold) is allowed but rarely meaningfully improves outcomes after costs and complexity.

### Allocations

Pick stock/bond based on age, risk tolerance, and goals (see `principles.md` #3). Pick international % within equities — common Boglehead positions:

- **0% international** — Bogle's late-career view; US stocks already get ~40%+ revenue from abroad. Defensible if minimalist.
- **20% of equities international** — Taylor Larimore's recommendation in his book.
- **30% of equities international** — common compromise.
- **~40% of equities international** — Vanguard's target-date fund allocation, close to global market cap weighting.
- **Market-cap weight (~58/42 US/intl as of 2024)** — Burton Malkiel and Charles Ellis in *The Elements of Investing*.

Example allocations:
- **80/20 stocks/bonds, 30% intl:** 56% US stock + 24% intl stock + 20% US bond
- **70/30, 30% intl:** 49% US stock + 21% intl stock + 30% US bond
- **60/40, 30% intl:** 42% US stock + 18% intl stock + 40% US bond — this is the textbook three-fund example

## Fund equivalents across brokerages

The three-fund portfolio is brokerage-agnostic. Use whichever ecosystem you're already in.

### Vanguard

| Asset | Mutual fund (Admiral) | ETF | Expense ratio |
|---|---|---|---|
| US Total Stock | VTSAX | VTI | 0.03–0.04% |
| Total International Stock | VTIAX | VXUS | 0.05–0.12% |
| US Total Bond | VBTLX | BND | 0.03–0.04% |
| Total International Bond (4-fund only) | VTABX | BNDX | 0.07% |
| **All-in-one Total World Stock** | VTWAX | VT | 0.07% |

VTSAX and VTI are literally the same fund in different share classes (Vanguard's patented structure). At Vanguard, no meaningful difference. At other brokerages, VTI is more portable.

### Fidelity

| Asset | Premium index fund | ZERO fund | Bond/intl ETF alt |
|---|---|---|---|
| US Total Stock | FSKAX (0.015%) | FZROX (0.00%) | ITOT (iShares, 0.03%) |
| Total International | FTIHX (0.06%) | FZILX (0.00%) | IXUS (iShares, 0.07%) |
| US Total Bond | FXNAX (0.025%) | — | AGG (iShares, 0.03%) |

**Caveat on FZROX / FZILX:** They have zero expense ratios but are *not portable* — Fidelity owns the index, so transferring to another brokerage requires liquidation (a taxable event in a taxable account). **Use them in IRAs/401(k)s only, never in a taxable brokerage account.** This is one of the most common Boglehead corrections to give.

Also: FZILX does not include international small-caps. Minor.

### Schwab

| Asset | Mutual fund | ETF |
|---|---|---|
| US Total Stock | SWTSX (0.03%) | SCHB (0.03%) |
| International | SWISX (0.06%) — **EAFE only, no EM** | SCHF (0.06%) — also EAFE; SCHE (0.11%) for EM |
| US Total Bond | SWAGX (0.04%) | SCHZ (0.03%) |

**Caveat on SWISX/SCHF:** Track the MSCI EAFE index, which excludes emerging markets, Canada, and most international small-caps. If you want full international exposure at Schwab, pair SWISX/SCHF with SCHE (emerging markets) at roughly 80/20 — or just use VXUS (iShares IXUS) which Schwab will hold commission-free.

### iShares / Generic ETFs (works anywhere)

| Asset | iShares ETF | Expense ratio |
|---|---|---|
| US Total Stock | ITOT | 0.03% |
| Total International | IXUS | 0.07% |
| US Total Bond | AGG | 0.03% |

A universally portable solution.

### TSP (Federal Thrift Savings Plan)

- C Fund (S&P 500), S Fund (small/mid-cap completion), and I Fund (international developed) approximate a total-market split. C + S in roughly 80/20 ratio mimics total US market.
- G Fund (special government securities) for safe bonds; F Fund for total bond market.
- TSP has the lowest expense ratios on Earth (~0.05%). If you have access, use it.

## The two-fund portfolio (even simpler)

Same idea, fewer funds:
- **VT** (Vanguard Total World Stock) — every publicly traded company on Earth, in market-cap proportion (~60% US, 40% intl)
- **BND** or **BNDW** (Vanguard Total World Bond)

Allocation: just pick stocks/bonds. Done. International % is set by global market cap, so it auto-adjusts as markets shift.

Drawback: BND vs international bonds question becomes implicit; the foreign tax credit benefit of VT held in taxable is smaller than separate US/intl funds.

## The one-fund portfolio (target-date funds)

For someone who doesn't want to manage allocations at all:

- **Vanguard Target Retirement [Year]** — e.g., VFFVX for 2055. Holds a four-fund portfolio internally (Total US Stock, Total Intl Stock, Total US Bond, Total Intl Bond), and automatically glides from stock-heavy to bond-heavy as the target year approaches. ~0.08% ER.
- **Fidelity Freedom Index** series — same idea. ~0.12% ER.
- **Schwab Target Index** series — ~0.08% ER.

This is a legitimate Boglehead solution, especially in a 401(k) or for someone with no taste for portfolio management. Bogle himself endorsed target-date funds for the right investor.

**Caveats:**
- Don't hold a target-date fund in a *taxable* account — they distribute capital gains and you can't separate the bond and stock placement for tax purposes. Use in 401(k) / IRA only.
- The bond glide path may not match your preference. A 2055 fund might be ~10% bonds in 2024; some young investors want 0%.
- Vanguard's target-date funds had a one-time capital-gains-distribution event in 2021 (an institutional/retail share-class merger) that surprised some taxable holders. Resolved, unlikely to recur.

## The four-fund portfolio

Adds international bonds:
- US Total Stock + Total International Stock + US Total Bond + **Total International Bond (BNDX / VTABX)**

This is what Vanguard's target-date funds use (70% US bond / 30% intl bond split on the fixed-income side). The Bogleheads wiki three-fund portfolio doesn't include it, but reasonable people do.

The case *for* international bonds: diversification across central bank policies and currencies (international bond funds are typically currency-hedged).

The case *against*: the global bond market is highly correlated; currency hedging adds cost; for most investors it doesn't meaningfully change outcomes vs pure US bonds; and it complicates the portfolio.

## "Lazy portfolios" — other Boglehead-approved variants

These are catalogued on the bogleheads wiki under "Lazy portfolios":

- **Coffeehouse portfolio (Bill Schultheis):** 7 funds — total bond + large-cap blend + large-cap value + small-cap blend + small-cap value + REIT + international.
- **Core Four (Rick Ferri):** total US stock + total intl stock + REIT + total bond. Adds REIT exposure.
- **Larry Swedroe portfolio:** small-cap value tilted, with safe bonds (treasuries/TIPS only). Embodies a factor-tilted Boglehead approach.
- **Permanent Portfolio (Harry Browne):** 25% stocks / 25% LT bonds / 25% gold / 25% cash. Not strictly Boglehead — most Bogleheads consider it overdiversified into low-return assets — but appears in the wiki.

If a user asks about "slice and dice" or factor tilts, point them at the Core Four or Swedroe versions, but note that the three-fund portfolio is still the wiki default and Larimore/Bogle preferred it.

## A note on Bogle's own portfolio

Bogle himself, in his last years, ran roughly 50/50 stocks/bonds, 100% US equity (no international), with the bond side in intermediate-term and TIPS funds. He explicitly disagreed with the conventional Boglehead wisdom on international.

The point: even Bogle didn't follow "the Boglehead portfolio" exactly. Reasonable people disagree on edges. The core (low-cost, broad-market, buy-and-hold, stay-the-course) is the part everyone shares.

## What to recommend when asked "what funds should I buy?"

The default answer:
1. Tell them the asset allocation question is more important than the fund choice.
2. Recommend a three-fund or target-date portfolio using whichever brokerage they're at.
3. Quote expense ratios.
4. Flag the FZROX-in-taxable and SWISX-no-EM caveats if relevant.
5. Tell them to set it up and stop checking it.

That's a complete answer. Don't over-engineer it.
