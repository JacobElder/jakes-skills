# Portfolio Reviews: The Boglehead Way

When a user shares an actual portfolio for feedback, this is the highest-value moment for the skill. The bogleheads.org forum has a formalized practice — the "Asking Portfolio Questions" template — that produces structured, actionable reviews. Use it.

## The "Asking Portfolio Questions" template

This is what Bogleheads on the forum ask for. If the user provides some but not all of it, work with what's there and ask for missing pieces only if essential. **Don't gatekeep.**

```
Emergency funds: [yes/no, # months of expenses, where held]
Debt: [credit card, student loans, mortgage, with interest rates]
Tax Filing Status: [Single / MFJ / MFS / HoH]
Tax Rate: [marginal federal %, state %]
State of Residence: [for state tax / muni bond considerations]
Age: [yours and spouse's]
Desired Asset Allocation: [e.g., 80% stocks / 20% bonds]
Desired International Allocation: [% of stock allocation]
Portfolio Size: [approximate, e.g., "low six figures" or "$450k"]

Current portfolio (each holding as % of TOTAL portfolio, not % of its account):

Taxable
  x% Fund name (TICKER) (expense ratio)

His 401(k) at [provider]
  x% Fund name (TICKER) (ER)

Her Roth IRA at [provider]
  x% Fund name (TICKER) (ER)

[etc., total across all accounts should sum to 100%]

Contributions:
  $x his 401(k) (+ match if any)
  $x her Roth IRA
  ...

Available funds in his 401(k):
  [list options for funds we might suggest he switch to]
```

If the user provides a less-structured portfolio, mentally fit it into this template. It's the analytical framework, not a rigid format requirement.

## The review process

Walk through these in order. Don't lead with a redesign — diagnose first.

### Step 1: Check the foundations

- **Emergency fund** — do they have one? 3–6 months? Where is it? (HYSA, MMF, T-bills good; stocks or whole life bad.)
- **High-interest debt** — credit cards at 20%+? Personal loans at 10%+? This needs to be addressed before talking about asset allocation.
- **401(k) match** — are they capturing it?
- **Insurance** — only flag this if there's an obvious gap (e.g., young family, no term life).

If foundations are missing, address those *before* getting into fund selection. There's no point optimizing the asset location of a $50k portfolio when the user has $30k in 22% credit-card debt.

### Step 2: Evaluate the asset allocation

- Is the stock/bond split appropriate for their age, time horizon, and stated risk tolerance? If they've never lived through a bear market, gently note that risk tolerance is hard to know in advance.
- Is the international % reasonable (0–50% of equities, with 20–40% being most common)?
- Are there outsized positions in individual stocks, crypto, employer stock, or alternatives that make the rest of the portfolio's allocation irrelevant?
- For couples: are they coordinated, or is each spouse holding separate uncoordinated allocations? (Should be viewed as one portfolio.)

### Step 3: Hunt for expense ratio garbage

Sort the holdings by ER mentally. Anything above 0.20% deserves a look:
- 0.20–0.50%: justify it, or replace with an index alternative.
- 0.50–1.0%: almost always replaceable. Flag it.
- 1.0%+: usually indefensible. Replace.
- **Loaded funds** (5.75% front-end): the load is a sunk cost; don't pay it again by buying more. Whether to sell depends on tax cost.

Watch for:
- "American Funds" tickers (AGTHX, ABALX, AMECX...) — loaded active funds, usually sold by commissioned advisors.
- Proprietary advisor-firm funds (often sold by JPM Private, Morgan Stanley) — these are red flags for a 1% AUM situation.
- 401(k) target-date funds at 0.50%+ — common in mid-market plans; usually a low-cost index alternative exists in the same plan.

### Step 4: Hunt for redundancy

- Multiple US large-cap funds (e.g., VOO + SPY + IVV) — pick one.
- Total stock market + S&P 500 + large-cap growth — substantially overlapping.
- Two international funds tracking similar indexes.
- A target-date fund *plus* component index funds — the target-date already has them.

Owning many funds is not diversification; it's redundancy with extra complexity. The Boglehead aesthetic is 3–5 distinct funds total across all accounts.

### Step 5: Check tax-efficient placement

Walk through the location of each asset class (see `tax_placement.md`):
- Bonds — should be in Traditional 401(k)/IRA. Flag bonds in Roth.
- High-growth assets — ideally in Roth.
- International — in taxable (FTC benefit) or wherever space allows.
- High-distribution funds (REIT, high-yield, active funds with capital gains) — never in taxable.

### Step 6: Identify taxable account constraints

- If the user wants to "simplify by selling X in taxable," **calculate the tax cost first**. Often it's better to: hold the legacy position, redirect new contributions, and let the rebalance happen organically over years.
- Tax-loss harvesting opportunities — funds below cost basis in taxable can be sold to bank losses (up to $3k/yr offset against ordinary income, plus offset gains). Replace with a similar-but-not-identical fund to avoid wash sale.
- Inherited assets get a step-up in basis — this can simplify previously complex positions if the older holder dies, but that's not a strategy.

### Step 7: Propose the simplified portfolio

A typical Boglehead simplification proposal:

> Here's what I'd propose, implementing the same 70/30 allocation:
>
> **Taxable ($XXX,XXX):**
> - VTI (Vanguard Total Stock Market) — $XXX
> - VXUS (Vanguard Total International) — $XXX
>
> **His 401(k) ($XXX,XXX):**
> - Fund X (the cheapest broad-market option) — $XXX
> - Bond index fund — $XXX
>
> **Her Roth IRA ($XXX,XXX):**
> - 100% VTI
>
> **HSA ($XXX,XXX):**
> - 100% VTI (highest-growth in tax-free account)
>
> This drops you from N funds to M, gets all the bonds into tax-deferred space, holds high-growth assets in Roth, and keeps international in taxable for the foreign tax credit. New contributions can flow into your target allocation automatically.

Show the math when costs are involved: "Current expense-weighted ER: 0.62%. Proposed: 0.05%. On a $XXk portfolio, that's $X,XXX/year saved — about $XXX,XXX over 30 years."

### Step 8: Answer their specific questions

After the structural review, address whatever they originally asked. By this point you've laid the foundation, so the answer often becomes self-evident.

### Step 9: One sentence of humility

Close with a brief acknowledgment: this is general guidance, not personalized advice; complex situations (estate planning, large Roth conversions, divorce, complex business structures) warrant a fee-only fiduciary. Keep it short — one sentence, not a paragraph.

## Common portfolio-review patterns

### "I'm 30, just started investing, what should I do?"

- Default recommendation: target-date fund in the 401(k), three-fund portfolio in the IRA, three-fund in taxable.
- 80/20 or 90/10 stocks/bonds.
- 20–30% of equities international.
- The user doesn't need anything fancier; complexity will not help them.

### "I'm 55, retiring in 10 years, here are my 7 accounts"

- Higher stakes; engage more carefully.
- Stock/bond likely 60/40 to 70/30.
- Plan for Roth conversion opportunities in the years between retirement and Social Security / RMD age (61–73 window for many people).
- Asset location matters more — bonds in Traditional, high-growth in Roth.
- Suggest reading *The Bogleheads' Guide to Retirement Planning* and consulting a fee-only fiduciary for the actual retirement plan.

### "I have a $2M portfolio with 30 holdings, my advisor charges 1%"

- The advisor fee is costing them $20k/yr. Frame this concretely.
- Most of the 30 holdings are probably overlapping or unnecessary.
- The redesign is usually: 3–5 funds, total ER under 0.10%, save $18k+/yr.
- Acknowledge the transition is non-trivial (capital gains in taxable, tax planning), but worth doing methodically over 1–3 years.

### "I inherited $X, what should I do?"

- Pause before doing anything for 6+ months. Inherited windfalls trigger bad decisions.
- For step-up inherited taxable assets: cost basis resets to date-of-death, so you can sell without major tax cost. Use this to simplify.
- For inherited IRAs: SECURE Act rules (10-year drain for most non-spouse beneficiaries) — plan distributions to manage tax brackets.
- Build a plan, then execute it slowly. Lump-sum vs DCA debate applies.

### "Help me understand my employer's 401(k)"

- Get the **fund menu with expense ratios** (in the Summary Plan Description).
- Identify the cheapest broad index option (often an S&P 500 or total stock index <0.10%).
- Identify bond and international options.
- Note availability of: Roth 401(k), after-tax contributions / mega backdoor Roth, in-service distributions.
- Often the right answer is: contribute enough for full match, use the cheapest broad-market option, fill out the rest of the portfolio in IRA + taxable.

## How to handle "Boglehead disagreements"

Some questions don't have a single right answer. When you encounter these in a review, present the spectrum honestly:

- **International %:** "Reasonable Bogleheads hold anywhere from 0% (Bogle's own view) to ~40% (Vanguard target-date allocation). Most fall somewhere in 20–30% of equities. Pick one and stick to it."
- **Bond allocation:** "Old rule was 'age in bonds'; modern Bogleheads often hold less. At your age, anywhere from 10–30% bonds is defensible. The question is more about your risk tolerance than about precision."
- **Roth vs Traditional:** "Depends on your expected retirement marginal rate vs current. If you're uncertain, splitting is fine."
- **Mortgage payoff vs invest:** "At a 3% mortgage rate, math favors investing. At 7%+, math favors payoff. In between, it's a behavioral decision."

Don't fake consensus where none exists. The user is better served by understanding the legitimate range.

## What a great Boglehead review reads like

Concise. Direct. Numbered observations. Each one with a "why." Specific funds named, expense ratios quoted. Math shown when relevant. Closes with a clean recommendation, not a list of options. Friendly but not chatty.

Look at any of the good replies on the bogleheads.org forum's "Asking Portfolio Questions" threads for the model.
