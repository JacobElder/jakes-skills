# The 10 Boglehead Principles

The canonical Boglehead investment philosophy, as taught at Bogleheads University and codified in the bogleheads.org wiki. These ten principles originate from John Bogle's writing and have been distilled into the form below by Bogleheads University presenters (Jim Dahle, Christine Benz, Allan Roth, Rick Ferri, Mike Piper, and others).

Source: bogleheads.org/wiki/Bogleheads%C2%AE_investment_philosophy and the Bogleheads University video course.

## 1. Develop a workable plan

Before picking funds, get the foundations right:
- Spend less than you earn ("live below your means").
- Establish a household budget.
- Maintain an emergency fund (3–6 months of expenses, typically; more for variable income or single earners).
- Pay off high-interest debt before investing in anything beyond the 401(k) match.
- Write down an **Investment Policy Statement (IPS)** — a brief, plain-English document stating goals, asset allocation, contribution plan, and the rules you'll follow in a downturn. The IPS is the antidote to panic-driven decisions.
- Get appropriate insurance: term life (if dependents), disability (if working), umbrella liability, health.

Bogle's framing: "The greatest enemy of a good plan is the dream of a perfect plan."

## 2. Invest early and often

- The earlier you start, the more compounding does the work. A 25-year-old saving $500/month at 7% has ~$1.2M at 65; a 35-year-old needs ~$1,000/month to match.
- Make investing automatic. Payroll deduction into a 401(k); auto-transfers into an IRA.
- "Pay yourself first."
- **Lump sum vs DCA on a windfall:** Vanguard's research shows lump-sum beats DCA roughly two-thirds of the time historically (because markets rise more often than not). But DCA over 3–12 months is a behaviorally reasonable compromise if the user can't stomach the risk of buying right before a drop.

## 3. Never bear too much or too little risk

- Asset allocation (the stock/bond ratio) is the single most important portfolio decision. It dwarfs fund selection.
- Risk tolerance has two components: **need** (how much risk does your goal require?) and **ability + willingness** (can you afford the loss, and can you actually sit through it without selling?).
- Rules of thumb that exist in the wild:
  - "Age in bonds" (a 40-year-old holds 40% bonds). Conservative; popularized by Bogle in earlier eras.
  - "Age minus 20" or "age minus 10" in bonds — common modern variant.
  - Just pick a number (e.g., 80/20 until age 50, then glide to 60/40 by retirement).
  - Use a target-date fund's glide path as a reasonable default.
- The honest test: if your stock-heavy portfolio dropped 50% tomorrow, would you sell? If yes, you have too much in stocks. People consistently overestimate their risk tolerance until they experience a real bear market.

## 4. Diversify

- Own thousands of companies, not dozens. The cleanest way: total-market index funds.
- Hold both stocks and bonds — they have different risk profiles and tend to be uncorrelated (especially in normal times). When stocks crash, high-quality bonds often hold up or appreciate.
- International diversification: holding non-US stocks reduces single-country risk. How much is a matter of debate (see SKILL.md), but anywhere from 20% to global-cap-weight (~40%+) of equities is reasonable.
- **What diversification doesn't mean:** owning many funds. Holding ten different US large-cap funds is not diversification — it's redundancy with extra fees.

## 5. Never try to time the market

- Investors as a group earn the market's return *before* costs and timing mistakes. Net of those, the average investor underperforms — sometimes by a lot.
- Dichev's research (NYSE/AMEX 1926–2002): dollar-weighted investor returns trailed buy-and-hold returns by ~1.3% annually. Worse for Nasdaq.
- "Time in the market beats timing the market" is a cliché because it's true.
- This applies to your gut, to talking heads on TV, to your brother-in-law, and to fancy "tactical asset allocation" funds. None of them reliably predict.
- **Corollary:** ignore predictions of crashes. Even when they happen, you usually can't take advantage. Peter Lynch: "Far more money has been lost by investors preparing for corrections than has been lost in corrections themselves."

## 6. Use index funds when possible

- Bogle's central insight: in aggregate, active managers can't outperform the market they collectively *are*, after fees. Some win; most lose; you can't reliably pick the winners in advance.
- SPIVA scorecards (S&P) show 80%+ of active US large-cap funds underperform the S&P 500 over 15-year periods. Similar pictures in most categories.
- Index funds also have low turnover → low capital-gains distributions → tax efficiency in taxable accounts.
- **Exception that proves the rule:** in some 401(k) plans, the only options are active funds. Pick the lowest-cost, broadest-market option (e.g., a low-cost S&P 500 fund), accept it, and tilt your IRA and taxable accounts to compensate.

## 7. Keep costs low

The big one. Bogle's *Little Book of Common Sense Investing* hammers this for 250 pages.

- "In investing, you get what you don't pay for."
- "The two greatest enemies of the equity fund investor are expenses and emotions."
- "Where returns are concerned, time is your friend. But where costs are concerned, time is your enemy."

Concrete cost categories to scrutinize:
- **Expense ratios.** Aim for <0.10% on core funds; <0.20% acceptable; flag anything 0.50%+ as expensive; 1%+ is usually unjustifiable for a vanilla mutual fund.
- **Loads / sales charges.** Never pay a load. No-load funds are everywhere.
- **Advisory fees.** A 1% AUM advisor on a $1M portfolio costs $10,000/year forever; compounded, that's enormous. Consider advice-only ($1,500–$5,000 flat fee for a plan) or fee-only fiduciary alternatives.
- **Transaction costs / spreads.** Mostly negligible at modern brokerages; matters for thinly-traded ETFs.
- **Tax costs.** Often the largest "cost" in taxable accounts. Place assets thoughtfully, harvest losses, hold for long-term gains.
- **Behavioral costs.** Performance-chasing, panic-selling, and "I'll just check my portfolio one more time" all cost money.

**The math example to use:** $500k portfolio, 1% expense difference, 30 years at 7% nominal returns. The 1% drag compounds to roughly 25% less terminal wealth. Run a quick calculation if the user is on the fence.

## 8. Minimize taxes

- Use tax-advantaged accounts first (see funding waterfall in `account_priority.md`).
- Place tax-inefficient assets (bonds, REITs) in tax-advantaged accounts; tax-efficient assets (broad-market stock index funds) can live in taxable.
- Hold for >1 year to qualify for long-term capital gains rates.
- **Tax-loss harvesting** in taxable accounts: when a fund is below its purchase price, sell and buy a similar-but-not-identical fund (avoid wash sale). Bank the loss to offset gains or up to $3,000 of ordinary income annually; carry remainder forward.
- **Avoid mutual fund capital gains distributions** in taxable accounts — prefer ETFs (which rarely distribute gains) or Vanguard mutual funds with an ETF share class (same effect via patent structure).
- **Backdoor Roth IRA** for high earners above the direct contribution limit.
- **Mega backdoor Roth** if the 401(k) plan supports after-tax contributions + in-plan conversions.
- **Roth vs Traditional:** depends on current vs expected retirement marginal rate. Common framework: high current rate + lower expected retirement rate → Traditional; the reverse → Roth; uncertain → mix.

## 9. Invest with simplicity

"Simplicity is the master key to financial success." — Bogle

- A three-fund portfolio of total-market index funds outperforms most professionally-managed portfolios over long periods, net of fees.
- Avoid sector funds, factor tilts, alternative investments, and complex strategies unless you have a specific, well-articulated reason.
- A target-date fund is a perfectly legitimate, fully Boglehead one-fund solution for someone who doesn't want to manage allocations.
- **Test for unnecessary complexity:** can you explain, in one sentence each, why each fund in your portfolio is there? If not, simplify.

## 10. Stay the course

The hardest principle.

- "Stay the course" is the Boglehead rallying cry. Bogle: "I've said 'Stay the course' a thousand times, and I meant it every time."
- A good plan executed mediocrely beats a perfect plan abandoned in a downturn.
- The market will fall 30%+ a few times in your investing life. The plan must survive that, including the temptation to "sit out until things calm down."
- Rebalancing is the disciplined version of staying the course: when stocks fall, you buy more; when they rise, you trim. Either by calendar (annually) or by threshold (e.g., rebalance when any asset class is >5 percentage points off target).

## A note on attribution

These ten principles are the codified Bogleheads University curriculum, but the underlying ideas span Bogle's full body of work — *Common Sense on Mutual Funds*, *The Little Book of Common Sense Investing*, *Enough.*, *The Clash of the Cultures* — and they reflect the consensus of decades of forum discussion at bogleheads.org. Larry Swedroe, Rick Ferri, Burton Malkiel, William Bernstein, and Mike Piper have all extended or refined specific aspects, but the core remains Bogle's.

## Key Bogle one-liners worth memorizing

Use sparingly, never as a substitute for reasoning:

- "Don't look for the needle in the haystack. Just buy the haystack."
- "Stay the course."
- "Simplicity is the master key to financial success."
- "When there are multiple solutions to a problem, choose the simplest one."
- "In investing, you get what you don't pay for. Costs matter."
- "The two greatest enemies of the equity fund investor are expenses and emotions."
- "Where returns are concerned, time is your friend. But where costs are concerned, time is your enemy."
- "Owning the stock market over the long term is a winner's game; attempting to beat the market is a loser's game."
- "The grim irony of investing: we get precisely what we don't pay for."
- "The greatest enemy of a good plan is the dream of a perfect plan."
- "Gunning for average is your best shot at finishing above average."
