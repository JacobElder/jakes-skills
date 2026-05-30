---
name: preference-choice-modeling
description: Advanced guidance for designing and analyzing preference and choice experiments — MaxDiff (sparse, anchored, Bandit variants), Choice-Based Conjoint (CBC), Adaptive CBC, Menu-Based Conjoint, and discrete choice models. Use this skill whenever the user is planning a MaxDiff or conjoint study, choosing between trade-off methods, deciding how many items / attributes / respondents / tasks they need, debating sparse vs. full design, troubleshooting D-efficiency or HB convergence, interpreting utilities and shares of preference, building market simulators, handling prohibitions, or critiquing a Qualtrics/Sawtooth study. Trigger even on casual mentions like "running a MaxDiff," "60 features to test," "conjoint sample size," "anchored MaxDiff," or "share of preference simulator" — platform defaults are often wrong for the user's actual decision and this skill exists to override them.
---

# Advanced Preference & Choice Modeling

This skill is the senior practitioner's reference for trade-off research. It assumes the user already knows what MaxDiff and CBC *are* — Qualtrics/Sawtooth/Conjoint.ly documentation covers the basics, and repeating them is not useful. The job here is to handle the questions where platform defaults are wrong, where the textbook answer is incomplete, and where bad choices silently destroy a study.

## When to use what — the decision that comes first

Before sample size, before design, before anything: confirm the method matches the decision. Wrong-method studies cannot be salvaged with more respondents.

| Decision the stakeholder needs to make | Recommended method | Why |
|---|---|---|
| Prioritize a long list of features/messages/benefits on a single dimension (importance, appeal) | **MaxDiff** (sparse if k > ~20–25) | Forces discrimination, defeats scale-use bias, no rating-scale ceiling |
| Predict choice / share when product is a bundle of attributes (price + features + brand) | **CBC (Choice-Based Conjoint)** | Models trade-offs across attributes; enables simulator |
| Optimize a single attribute with many levels (e.g., 40 price points, 30 flavors) | **MaxDiff over levels** or **partial-profile CBC** | Full-profile CBC explodes |
| User assembles their own bundle (add-ons, configurators) | **Menu-Based Conjoint** | Models actual configuration behavior, including "buy nothing" |
| Small number of well-understood attributes, want to model interactions cleanly | **CBC with covariates / interactions in HB** | |
| Ranking a small list (≤7) | Direct ranking or **best-worst Case 1** | MaxDiff is overkill |
| Volumetric forecast (units, not share) | **Volumetric CBC** or **Discrete Choice + calibration** | Standard share-of-preference is relative, not absolute |

**The most common mistake**: running MaxDiff to inform a *product configuration* decision. MaxDiff tells you item importance in isolation; it does not tell you how features trade off against price or against each other within a product. If the stakeholder will use the output to set a price, bundle features, or configure a SKU, push toward CBC.

**The second most common mistake**: running CBC when the real question is "which of these 30 messages resonates." Conjoint over messages is almost always a misuse — use MaxDiff.

---

## MaxDiff — advanced topics

For the full advanced treatment (design efficiency, sparse design math, anchoring methods, Bandit MaxDiff, individual-level estimation, common failure modes), read `references/maxdiff.md`. Highlights of what's in there:

- **Sparse MaxDiff** — when to use it, how sparse is too sparse, the math for design efficiency at different k (items) and showings-per-item
- **How many items can you actually test**: practical ceilings, what changes above 30 / 50 / 100
- **How many respondents you need**, derived from desired CI half-width on utility scores rather than rule-of-thumb "300"
- **Anchored MaxDiff** (direct binary anchor vs. dual-response anchor) — why unanchored scores mislead stakeholders and which anchoring method to use when
- **Bandit MaxDiff / Adaptive MaxDiff** — when adaptive designs help and when they bias results
- **Express MaxDiff** and other sparse variants — what Sawtooth means vs. what academics mean
- **HB estimation** for MaxDiff — priors, convergence diagnostics, why aggregate logit is almost never the right choice
- **Scale-use, response-time filtering, and other quality controls**

Default to reading the reference file whenever a MaxDiff question goes beyond "should I use MaxDiff."

---

## Conjoint analysis — advanced topics

For the full advanced treatment (D-efficiency, prohibitions, alternative-specific designs, dual-response None, ACBC's BYO/Screener/Tournament stages, HB priors, simulator math, calibration to known shares), read `references/conjoint.md`. Highlights:

- **CBC design efficiency** — D-efficiency vs. relative D-efficiency, why "balanced overlap" is the default, when to override it
- **How many tasks per respondent**, how many concepts per task, how many attributes — and the interactions between these
- **How many respondents you need**, derived from the precision needed for the *decision*, not the survey
- **Prohibitions and near-prohibitions** — why prohibitions destroy efficiency and what to do instead (alternative-specific designs, conditional pricing)
- **Adaptive CBC (ACBC)** — when the BYO + Screener + Choice Tournament stages actually pay off vs. when they introduce more bias than they remove
- **Menu-Based Conjoint** — design and estimation
- **Dual-response None vs. single None** — recommended default and exceptions
- **HB for CBC** — priors that matter, convergence, individual-level utilities, covariates
- **Simulators** — share of preference vs. first choice vs. randomized first choice (RFC), when each is appropriate, calibration to in-market shares
- **Common failure modes** — non-attendance, attribute non-linearity, reference-price effects, screening on price

---

## Sample size — the one section to actually read every time

The platform defaults (`Sawtooth: n ≥ 300 for CBC`, `Qualtrics: n ≥ 200 for MaxDiff`) are not derived from your study. They're floor-of-the-industry numbers. Derive sample size from the precision you need on the *decision*, not from a rule.

**For MaxDiff**, the relevant precision is the standard error on a single item's utility, which scales as roughly:

```
SE(utility) ≈ c / sqrt(n × showings_per_item)
```

where `c` depends on the design (typically ~1.0–1.5 in well-balanced designs). For a typical MaxDiff with 4 items per set, 5 showings per item, and n=400, individual-item SE on the rescaled (0–100) utility scale is usually 1–2 points. Whether that's enough depends entirely on whether your stakeholder needs to distinguish items that are 3 points apart or 15 points apart.

**For CBC**, the relevant precision is on the share-of-preference difference between simulated products. A robust rule (Orme, with caveats):

```
n × t × a / c ≥ 500
```

where `t` = tasks per respondent, `a` = alternatives per task (excluding None), `c` = analytical cells (largest number of levels on any one attribute when running aggregate logit; far less restrictive under HB). For HB CBC, focus instead on getting enough information per respondent: aim for `t × a ≥ 30` per person for stable individual-level utilities. With 10 tasks × 3 alternatives, that's 30 — borderline; 12 tasks × 4 alternatives (48) is solid.

**For subgroup analysis**, multiply by the inverse of the smallest subgroup's prevalence. If you need to read out for a segment that's 20% of the population, you need 5× the sample to get the same precision in that segment.

Whenever the user asks "how many respondents do I need," resist quoting a single number. Ask:
1. What's the smallest difference between items/products you need to detect?
2. Will you read out for subgroups? Which ones, and what's their prevalence?
3. Aggregate readout only, or individual-level (HB)?

Then derive from there. See the references for the underlying math.

---

## How many items / attributes / levels

**MaxDiff items (k):**
- ≤ 15: comfortable for full design (every respondent sees every item ~3–5 times)
- 16–30: full design still feasible; respondent burden becomes the constraint, not statistical
- 31–60: **sparse MaxDiff territory**. Each respondent sees a subset (typically 3–5 showings/item per respondent, designed so the *aggregate* design is balanced)
- 61–150: sparse MaxDiff or Bandit MaxDiff; individual-level utilities degrade — plan for aggregate or segment-level readout, not individual scores
- 150+: rethink the list. You're probably conflating multiple constructs. Cluster items first, then MaxDiff the clusters, then MaxDiff within clusters in a follow-up.

**CBC attributes:**
- Practical ceiling is around 6–8 attributes for full-profile CBC before respondents start simplifying heuristics (non-attendance). Above that, use partial-profile.
- Levels per attribute: 2–7 is the comfortable range. More levels means more parameters to estimate and more design space — adds respondents needed roughly linearly per added level on the constraining attribute.

**ACBC**: handles more attributes (10–12 comfortably) because the BYO and Screener stages narrow the design space before the Choice Tournament. But ACBC has its own failure modes — see `references/conjoint.md`.

---

## Output to stakeholders

Once analysis is done, the deliverable to stakeholders typically includes:

1. **Rescaled utilities or importance scores** — for MaxDiff, the zero-centered or 0–100 rescaled scores; for CBC, attribute importances + level utilities
2. **Anchored / probability-scaled scores** if appropriate — for MaxDiff, the share of items above the anchor; for CBC, share-of-preference simulations
3. **Simulator** (CBC) — share of preference for a defined set of products, ideally interactive
4. **Subgroup deltas** — where the segments diverge on what matters
5. **Confidence/uncertainty** — almost always missing from platform exports. Always include CIs or at least SDs around the key numbers. Stakeholders read point estimates as truth; the practitioner's job is to make uncertainty visible.

For uncertainty visualization specifically: prefer overlapping CI bars or gradient bars over single point estimates. Importance scores presented without uncertainty mislead readers into ranking items that are statistically tied.

---

## Common requests and how to handle them

**"Can you analyze this MaxDiff data?"** → Confirm: was it run with anchoring? If not, the utilities are relative-only and you cannot say "X is important in absolute terms" — only "X is more important than Y." Push back if the deck claims absolute importance from unanchored scores.

**"We want to test 80 messages"** → Sparse MaxDiff, not full. Walk through showings-per-item math. Warn that with 80 items, individual-level readout is weak — set expectations for aggregate or segment-level results.

**"How many respondents for a CBC?"** → Ask the subgroup question first. Then derive from required precision on the decision being made.

**"The HB utilities look weird"** → Almost always one of: (1) insufficient burn-in / iterations, (2) prohibitions that effectively created an unidentified design, (3) one attribute is causing reversal in a non-trivial fraction of respondents (and HB shrinkage is hiding it at the aggregate level), or (4) bad respondents weren't filtered. Check each.

**"Should we use ACBC instead of CBC?"** → Default no unless the product has many attributes (≥8) and a complex pricing structure. ACBC adds complexity and respondent fatigue; the gains are real but situation-dependent. See the references.

**"Can we use MaxDiff for pricing?"** → Almost never directly. MaxDiff on price points gives a relative preference among prices, which is not the same as willingness to pay or demand curve. Use CBC with price as an attribute, or Van Westendorp / Gabor-Granger for pure pricing.

---

## When stakeholders push back

Common pushback you'll need to handle:

- *"Why can't we just use a rating scale?"* — Scale-use bias, ceiling effects, no forced trade-off. You'll get 28 of 30 items rated "very important." Have a one-liner ready.
- *"300 respondents seems like a lot."* — Walk through what the precision will be at 150 and what decisions it can/can't support. Make the trade-off explicit.
- *"Can we add another 10 items?"* — Yes, but here's what happens to respondent fatigue and to each item's effective sample size. Show the trade-off, then let them choose.
- *"Why isn't the highest-utility item also the one with the highest market share in our actual product?"* — MaxDiff/CBC measure stated preference under controlled trade-offs. Real markets have distribution, awareness, switching costs, and brand effects that the experiment doesn't capture. This is not a bug; it's the boundary of the method. Calibrate the simulator if you need absolute shares.

---

## References

- `references/maxdiff.md` — MaxDiff design, sparse variants, anchoring, Bandit, HB estimation, sample size derivation, failure modes
- `references/conjoint.md` — CBC, ACBC, MBC, design efficiency, prohibitions, simulators, HB priors, calibration
- `references/sample-size.md` — Worked sample-size derivations for both methods with formulas and example calculations
- `references/hb-estimation.md` — Hierarchical Bayes specifics: priors, convergence, individual-level utilities, covariates, common pathologies
