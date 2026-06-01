# Response: Should We Omit the None Option in a B2B CBC?

**Short answer: No — and the reasoning your PM is using is a known error in conjoint design.**

---

## The PM's argument, and why it's wrong

The argument is: "this is an existing market, so everyone will choose *something*, therefore we can omit the None option."

This conflates two different questions:

1. Will respondents pick *one of the available alternatives* from the presented task?
2. Does "None" in a CBC task mean "no-purchase in the real market"?

These are not the same thing. In a CBC task, the None alternative captures a distinct signal: "I wouldn't choose any of the specific bundles shown to me, even though I'd still use *some* product in real life." That signal is meaningful even in markets with near-100% adoption, because:

- The specific profiles in any given task may not span the respondent's acceptable range. Forcing a choice produces a distorted utility for the "least bad" option, not the utility for any real product.
- Omitting None inflates all simulated share-of-preference values. When you run the simulator, every respondent's probability must be distributed across the shown alternatives — there is no outside-good absorbing the "I'd pick something else in the real market" cases.
- B2B software is not a forced-choice environment. A buyer who sees none of the three shown configurations as a good fit will not sign a contract for the worst option. They'll keep using their current vendor, or wait, or issue a new RFP. That behavior has to go somewhere in the model.

---

## What the correct approach looks like

The recommended default for most CBC studies is **dual-response None**, not single explicit None and not no-None.

**How dual-response None works:**

1. Respondent sees the task (typically 3–4 alternatives).
2. They pick their preferred alternative — no None option shown. This is a forced relative-preference choice.
3. Immediately after, a second question asks: "Would you actually purchase/adopt this solution?" Yes / No.

**Why this design is better than both alternatives:**

- It separates two analytically distinct signals: *relative preference* (step 1) and *purchase likelihood* (step 2). An explicit None conflates them.
- It captures the full comparison task while still generating a purchase-likelihood model.
- It reduces the cognitive shortcut of always clicking None when tasks get difficult ("None" abuse), which is a real problem in B2B studies where respondents are busy and have opinions about vendor offerings.
- Simulator output from dual-response None yields realistic share-of-purchase estimates, not inflated share-of-preference figures.

**Estimation**: the two-stage response generates two likelihood functions — a multinomial logit over alternatives in stage 1, and a binary logit (buy vs. not buy) in stage 2. Sawtooth and R's `apollo` package both support this directly.

---

## When no-None *is* appropriate

The references are clear: omit None only "when you genuinely know everyone in the population buys one of the alternatives — uncommon." There are legitimate use cases:

- **Forced-choice competitive displacement simulation**: you are literally simulating "given only these three vendors, which one gets the deal?" and you have strong external evidence that one of them will be selected. If the study is for a pitch scenario where the finalist set is fixed and a vendor must be chosen, no-None may be appropriate.
- **Plan or coverage mandate contexts**: health insurance open enrollment, benefits elections, or similar, where not choosing is legally or contractually not an option.

A typical B2B software purchase does not qualify. The buyer always has the option to renew with their incumbent, delay the evaluation, or walk away from a specific set of products. Your PM's assumption is convenient for making the survey feel simpler, but it produces a worse model.

---

## The practical cost of omitting None in this scenario

If you run with no None option:

1. **Inflated shares**: your simulator will overstate adoption likelihood for every profile because there is no outside-good. Stakeholders will set pricing and feature priorities based on shares that are unrealistically high.
2. **Missing segment signal**: buyers who are on the fence — the ones you most need to understand for pricing and bundling decisions — will show up as artificially distributed across alternatives rather than identifiably clustered near the "no-purchase" boundary.
3. **Non-monotonic price utilities**: without an outside good, the relative price disutility estimates are compressed. This is especially harmful for B2B software where pricing is a primary decision lever.

---

## Recommendation

Use **dual-response None**. Keep the task itself as a forced relative-preference choice (which satisfies the PM's underlying intuition that respondents will have a preference among the options), and add the purchase-confirmation follow-up. This gives you a cleaner separation of relative preference and purchase likelihood, produces a correctly calibrated simulator, and does not require any additional respondent effort beyond one extra click per task.

If the PM pushes back on the added complexity: the estimation complexity is on the analyst side, not the respondent side. The respondent experience is nearly identical to a standard CBC task.
