# Tax-Efficient Fund Placement (Asset Location)

When you have money across multiple account types — taxable brokerage, Traditional 401(k)/IRA, Roth IRA/401(k), HSA — the *location* of each fund matters for tax efficiency. This is "asset location" (distinct from "asset allocation," which is the stock/bond ratio).

Source: bogleheads.org/wiki/Tax-efficient_fund_placement.

**Important caveat upfront:** asset location is a second-order optimization. Getting the asset *allocation* right matters far more. Don't tie yourself in knots over location.

## The general rule

| Tax efficiency | Asset class | Best account |
|---|---|---|
| Very efficient | Broad US stock index funds | Taxable or any |
| Efficient | Total international stock | Taxable (for foreign tax credit) — but debated |
| Inefficient | Bonds (high-yield esp.) | Tax-deferred (Traditional 401k/IRA) |
| Inefficient | REITs | Tax-advantaged (Roth ideal) |
| Highest-growth expected | Stocks with high return expectations | Roth (never pay tax on gains) |

## Why bonds belong in tax-deferred

- Bond interest is taxed as **ordinary income** at your full marginal rate.
- In a Traditional 401(k)/IRA, you defer that tax until withdrawal.
- Equivalent stock dividends are taxed at the lower **qualified dividend / LTCG rate** (0%, 15%, or 20% depending on bracket).
- So bonds in taxable lose more to taxes per year than stocks in taxable.

Example: A 4% yield bond fund held in taxable at 32% federal + 6% state rate loses 1.52% to taxes annually. A 2% qualified-dividend stock fund at 15% federal LTCG loses only 0.30% — and most of the stock return is unrealized appreciation that isn't taxed at all until sale (or never, with step-up at death).

## Why stocks belong in Roth (when there's room)

- Roth grows tax-free forever and withdrawals are tax-free.
- You want the highest-expected-return asset in Roth so the maximum amount of growth is sheltered.
- Stocks have higher expected returns than bonds → stocks in Roth ideally.
- **Counter-intuitive corollary:** putting bonds in Roth is "wasting" Roth space on a low-growth asset.

## The bonds-in-taxable exception

The general rule has wrinkles. **Bonds in taxable can make sense if:**

- **You're in a low tax bracket.** A retiree in the 12% federal bracket may pay less tax on bond interest than they'd pay opportunity cost by displacing stocks from Roth.
- **You hold municipal bonds.** Munis are federally tax-free (and state-tax-free in your home state) — purpose-built for taxable accounts. Useful for high earners in high-tax states (CA, NY, NJ) — check that the after-tax yield exceeds taxable bond yields. Common choices: VTEB (Vanguard Tax-Exempt Bond ETF), VWITX (Intermediate-Term Tax-Exempt mutual fund), state-specific funds like VCAIX (CA).
- **You hold Treasuries in a high-state-tax state.** Treasury interest is exempt from state income tax. In California (13.3% top rate), this matters.
- **You want easy access to your bonds.** If your bond allocation is your "ballast" you might sell in a crash to rebalance into stocks, keeping it in taxable lets you avoid having to do a coordinated transaction across accounts. (You can also do that with the in-kind transfer trick — sell stocks in taxable, buy stocks in tax-advantaged with bond proceeds — but it's more steps.)
- **You're out of tax-advantaged space.** Sometimes you just don't have room.

## International stocks in taxable: the foreign tax credit debate

International stock funds pay foreign withholding tax on dividends. If held in a **taxable account**, you can claim a **foreign tax credit** to recover most of it. If held in a **tax-advantaged account** (IRA, 401(k), Roth), you cannot — the foreign tax is lost.

Estimated FTC benefit: ~0.20% of international fund value per year. Small but real.

**Counter-argument:** at modern tax rates and dividend yields, holding international in tax-deferred (and stuffing it with a US bond fund instead) can be more tax-efficient over time. The foreign tax credit benefit is small enough that other considerations often dominate.

Practical guidance:
- If you have lots of taxable space: holding international in taxable is fine. Capture the FTC.
- If your tax-advantaged accounts have great international options (low ER): put international there if it makes the rest of the portfolio simpler.
- Don't agonize. The difference is small.

## The "tax-adjusted asset allocation" idea

A more advanced concept: $10k in a Traditional 401(k) isn't really $10k — it's $10k minus future taxes. If you'll withdraw at 22%, that $10k is "worth" $7,800 after-tax. $10k in a Roth or taxable (without unrealized gains) is worth $10k.

If you "tax-adjust" your portfolio, the right asset allocation in *real* terms may differ from the nominal one. Most Bogleheads don't bother with this except in edge cases — it adds complexity for marginal benefit. Mention it as a concept; don't push it as a default.

## A practical worked example

Say you have:
- $400k Traditional 401(k)
- $200k Roth IRA
- $200k Taxable brokerage
- $200k HSA
- Total: $1M
- Target allocation: 70% stocks / 30% bonds (so $700k stocks, $300k bonds), with 30% of stocks international (so $210k international, $490k US).

**Tax-efficient placement (one good arrangement):**

| Account | Holdings | Reasoning |
|---|---|---|
| Traditional 401(k) ($400k) | $300k US bond + $100k US stock | All bonds here; surplus US stock |
| Roth IRA ($200k) | $200k US stock | Highest-growth asset in Roth |
| HSA ($200k) | $190k US stock + $10k US stock | Highest-growth in tax-free account |
| Taxable ($200k) | $210k international + (-$10k? no, you'd hold less intl) | International for FTC; tax-efficient |

(Adjust the exact numbers; the point is the principle.)

In practice you adjust between accounts based on what funds are *available* in each account. A 401(k) with only a high-cost international option might steer you toward holding international elsewhere.

## What to do if your 401(k) is bad

A 401(k) with only high-expense-ratio active funds is a common problem. Approach:

1. Still capture the match (the match >> the cost).
2. Pick the least-bad option (often a low-cost S&P 500 fund — call it "US large-cap").
3. Use your IRA and taxable space to *complete* the portfolio — add international, small-cap exposure, bonds — at lower cost.
4. When you leave the job, roll the 401(k) to an IRA (or to a new employer's better plan) so you can access better funds.

## Common mistakes to flag in portfolio reviews

- **Bonds in Roth IRA** while stocks sit in Traditional 401(k). Almost always backwards.
- **REITs in taxable.** REIT dividends are not qualified → taxed as ordinary income → throw it in tax-deferred.
- **High-dividend stock funds in taxable** (e.g., VYM, SCHD). Defeat the tax-efficiency advantage of holding stocks in taxable.
- **Holding the same target-date fund in taxable + tax-advantaged.** Target-date funds aren't optimized for tax efficiency; in taxable they bleed via distributions.
- **Active mutual funds with high turnover in taxable.** Capital gains distributions kill the tax efficiency.
- **Same fund in multiple accounts can complicate tax-loss harvesting** — selling at a loss in taxable while buying in IRA triggers a wash sale and disallows the loss. Use *similar but not substantially identical* funds across accounts (e.g., VTI in taxable, FSKAX in IRA).

## When to NOT optimize for placement

- If the user has $20k total across all accounts, location is irrelevant. Get them invested first.
- If optimal placement requires selling something in taxable with large unrealized gains, the tax cost of moving usually outweighs the benefit. Hold the existing position and direct *new* contributions to the optimal location.
- If a 401(k) has no decent bond option, just hold whatever's best available there and don't sweat it.

## A note on Roth conversion and asset location interaction

When doing a Roth conversion (Traditional → Roth), think about which assets you're converting. Converting bonds is "cheaper" (lower future expected growth → smaller tax base in the future); converting stocks "locks in" tax-free growth on the higher-return asset. Some Bogleheads do **opportunistic Roth conversions** during market downturns specifically to convert depressed stock prices. Beyond scope here, but flag it as a consideration if the user is in a position to do conversions.
