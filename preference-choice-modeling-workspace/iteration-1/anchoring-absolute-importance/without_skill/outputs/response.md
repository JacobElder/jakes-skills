# Getting to Absolute Importance from MaxDiff

Your stakeholder is asking a genuinely different question than what standard MaxDiff answers. Standard MaxDiff gives you *relative* importance — feature A is preferred over feature B — but it doesn't tell you whether feature A is actually *important* in any absolute sense. Here's how to get there.

---

## The Core Problem

MaxDiff scores (raw or probability-scaled) are ipsative: they sum to a constant across all features. Every item gets a score, and those scores only have meaning relative to each other. Even a feature with a "high" score might be something nobody actually cares about — it just happened to beat even-weaker alternatives.

This means you cannot read absolute importance directly from the raw output.

---

## Method 1: Anchored MaxDiff (The Gold Standard)

The cleanest solution is to run **anchored MaxDiff** (also called "anchored best-worst scaling"). This adds a follow-up question after each MaxDiff task asking respondents whether the "best" item they selected actually matters to them at all, or whether they would be satisfied without any of the items shown.

**How it works:**
- After selecting best and worst from a set, respondents see the item they chose as "best" and answer: "Would you be satisfied with a product that has this feature?" or "Does this feature actually matter to you?" (yes/no, or a rating).
- This anchor response lets you estimate an *absolute* zero point on the importance scale.
- Items that win head-to-head comparisons but consistently fail the anchor check are revealed as "relatively preferred but not actually important."

**Output:** A rescaled importance score where items scoring below the anchor threshold are classified as "not important," regardless of how they rank relative to each other.

---

## Method 2: Scale Factor / Probability Rescaling

Without anchoring, you can still make relative scores more interpretable by converting them to **probability-scaled scores** (also called "share of preference" scaling):

- Transform raw logit scores using the softmax/exponential formula so they sum to 100 (or 1.0).
- A feature with a score of, say, 5% is chosen best roughly 5% of the time in a random 5-item set — which gives it a more concrete, communicable meaning.

**Limitation:** This still doesn't answer the absolute question. A feature with 5% share of preference might still be something people genuinely care about, or might not — the scale is still relative.

---

## Method 3: External Benchmarking

Add a calibration item — something with a known, agreed-upon level of importance — to your MaxDiff item set. For example:

- "Price is within my budget" (nearly everyone cares)
- "Product is available in my country" (a hygiene factor)

If you include a feature like "product is available in my preferred color" (low stakes) and "product doesn't break within a year" (high stakes), you can use these as informal anchors to interpret where your other features fall on a practical importance scale.

**Limitation:** Relies on your judgment about the calibration items, and calibration items consume set space.

---

## Method 4: Supplementary Direct Rating

After the MaxDiff exercise, ask respondents to rate each feature on a traditional importance scale (e.g., 1–7 "not at all important" to "extremely important"). This is sometimes called a "chip allocation" or "constant-sum" follow-up, or simply a Likert-style battery.

Then correlate the MaxDiff scores with the direct ratings to identify:
- Features that are high in MaxDiff rank *and* high in direct importance ratings → truly important
- Features high in MaxDiff rank but low in direct importance → relatively preferred but not genuinely important
- Features low in MaxDiff but high in direct importance → potentially a floor issue in your design

**Limitation:** Direct ratings suffer from acquiescence bias (people rate everything as important), which is exactly why you ran MaxDiff in the first place. Use the direct ratings to *qualify* rather than replace the MaxDiff results.

---

## Method 5: Count-Based "Never Best" Analysis

A quick diagnostic: look at how often each feature is *never chosen as best* across all tasks. A feature that is never selected as best by a respondent is, at minimum, not important to that person.

Segment respondents into "this feature matters to me" vs. "this feature never beats anything for me" groups. The proportion of respondents for whom a feature is always bottom-ranked gives you a rough absolute read on how many people the feature is irrelevant to.

---

## Recommended Approach

If you're still in design:
1. **Redesign as anchored MaxDiff** — this is the correct tool for the question your stakeholder is asking.

If the data is already collected:
1. Use **probability-scaled scores** to communicate magnitude more concretely.
2. Pair with any **direct importance ratings** you collected.
3. Run a **"never best" analysis** to identify features that large segments consistently deprioritize.
4. Be honest with your stakeholder: standard MaxDiff tells you rank order, not absolute importance. If the decision requires absolute importance, flag that the study design should be revisited for the next wave.

---

## Key Talking Point for Your Stakeholder

> "MaxDiff tells us which features people prefer over others, but it can't tell us whether any of them actually matter. To answer your question, we either need to rerun this as an anchored study, or use the MaxDiff scores alongside direct ratings. Here's what we can say from the current data, and here's what we'd need to be more confident..."

That framing sets appropriate expectations and gives a clear path forward.
