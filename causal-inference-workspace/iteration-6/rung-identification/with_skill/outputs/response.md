# Causal Analysis: Sequential User ID Assignment as Quasi-Experiment

## Rung Identification

The question being asked is **Rung 2 (Intervention)**: does the new checkout flow causally increase conversion rates? The junior analyst is implicitly treating the data as supporting a causal estimate (do-operator reasoning), while the senior engineer is questioning whether the assignment mechanism supports that inference.

This is not a Rung 1 (association) question — we're not just asking "are new_checkout users converting more?" We're asking: "If we deploy new_checkout to everyone, will conversion go up by ~4.2 percentage points?" That's a causal, interventional question.

---

## Who Is Right?

**The senior engineer is right. The junior analyst is wrong.**

The validity of any causal estimate from an A/B test rests on a single foundational requirement: treatment assignment must be independent of potential outcomes. "Arbitrary" user IDs don't guarantee this. The question is whether the mechanism that generates user IDs creates independence — and it doesn't here.

---

## The DAG

Let's make the structure explicit:

```
   Account Age / User Cohort (U)
          ↙              ↘
   Treatment (T)      Outcome (Y)
   [new vs old         [conversion
    checkout]           rate]
```

Where:
- **U** = user cohort / account age (proxied by user ID magnitude)
- **T** = checkout version assigned (determined by last digit of user ID)
- **Y** = conversion

**Sequential ID assignment means user ID magnitude is a direct proxy for account age.** Low-digit users registered early; high-digit users registered recently. The last digit is not independent of the user ID magnitude — it's merely the modular residue of a monotonically increasing counter.

The key insight: **last digit is not independent of account age.** If IDs are assigned as 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12... the last digit cycles 1–9, 0, 1–9, 0... This cycling is uniform across cohorts *within each group of 10*, but if users were assigned to treatment strictly as "digits 0–4 get new_checkout, digits 5–9 get old_checkout," this does create a roughly 50/50 split within any 10-consecutive-ID block — which sounds balanced. However, the critical failure is **not about the 50/50 split**; it's about what else correlates with being an older vs. newer user.

More precisely: within each block of 10 consecutive IDs, there is balance. But users are not randomly ordered in time. If user behavior, purchase maturity, or platform familiarity correlates with **cohort** (when they joined), and **cohort** correlates with **user ID range** (not just last digit), then the concern is whether last-digit-based assignment inadvertently captures any systematic variation across the sequential ordering.

The back-door path is:

```
User Cohort (U) → T (via last digit of sequential ID)
User Cohort (U) → Y (older/newer users differ in conversion)
```

The question is whether this back-door path is actually open.

---

## Analyzing the Senior Engineer's Claim

The senior engineer's claim is precise and worth unpacking carefully.

**Claim:** "User IDs are assigned sequentially, so this just compares newer users to older users."

**Is this strictly true?** Let's think through it:

- IDs 0–4 (last digit) and IDs 5–9 (last digit) are interleaved throughout the full ID space. For any contiguous block of 10 IDs (e.g., users 1000–1009), digits 0–4 and 5–9 appear in equal numbers and in the same cohort.
- So within any cohort (time period), the split is balanced.
- **However:** if the full user base spans a wide range of cohorts, and conversion behavior has shifted over time (newer users convert differently than older users due to product changes, seasonal effects, marketing changes, etc.), then the average behavior of "all users with last digit 0–4" vs. "all users with last digit 5–9" could still be confounded if the ID space is not densely and uniformly sampled.

**The stronger version of the engineer's concern:** In practice, sequential IDs don't just mean the last digit alternates cleanly. It means:
1. User ID encodes registration time.
2. Registration time predicts user characteristics (engagement patterns, LTV, product familiarity, cohort-specific onboarding experience).
3. Last digit does cycle through all values within each cohort, producing *within-cohort* balance — but *aggregate* estimates may still be biased if the sample has unequal representation across cohorts for the two groups. This is unlikely to be severe with a pure last-digit split, but there's a subtler issue.

**The subtler, more important point the engineer may be gesturing at:** If user IDs are sequential and the product has changed over time, the *treatment is confounded with cohort* only if last-digit assignment was not uniformly applied. But with a simple last-digit rule, it is uniformly applied across all cohorts by construction. So the engineer's literal claim — "this just compares newer users to older users" — is **overstated as a strict logical statement**.

**However, the engineer is right in spirit** because the analyst's argument is wrong. The analyst claims "user IDs are arbitrary, so the assignment is essentially random." This is the error. "Arbitrary" does not mean "random." The last digit of a sequential counter is deterministic, not random. Whether it produces valid causal identification depends on whether the last digit is independent of potential outcomes — not on whether IDs "feel" arbitrary.

---

## The Correct Identification Analysis

For the +4.2% to be a valid causal estimate, we need treatment assignment (T = last_digit ∈ {0,1,2,3,4}) to be independent of potential outcomes Y(0) and Y(1). This requires no open back-door paths from T to Y.

**What would make this valid:** If last digit is independent of all other user characteristics that affect conversion, conditional or unconditional. Within a block of 10 consecutive IDs, this is approximately true. Across the full user base, it is approximately true if:
- The full ID range is densely populated (no large gaps that correspond to specific cohort features)
- Conversion behavior has not systematically shifted over calendar time in a way that would be differentially captured by the last-digit split

**What makes this invalid or suspect:**
1. **Non-uniform ID distribution:** If certain ID ranges (cohorts) are over-represented in one last-digit bucket due to gaps in ID assignment (e.g., IDs 5000–5004 were never issued, or a bulk import of B2B accounts all got IDs ending in 6–9), the balance breaks.
2. **Cohort effects interacting with the bug:** The bug that caused this assignment may have been introduced at a specific point in time. If the bug was active only for a certain ID range, the "new_checkout" group is precisely a specific cohort, not a cross-cohort last-digit sample.
3. **User ID reuse or non-sequential gaps:** Many production systems don't assign IDs as a perfect dense sequence. UUIDs, hash-based IDs, or IDs with gaps from deletions could make the last digit non-uniform across time.
4. **Self-selection into conversion funnel:** If older users (lower IDs) are more or less likely to reach the checkout page at all, the *conditioning on reaching checkout* is itself a collider, and the 4.2% is measured in a selected sample, not the full user base.

---

## The Analyst's Specific Error

The analyst's logical error is: **"User IDs are assigned by an arbitrary process → last digit is essentially random."**

This is wrong. "Arbitrary" (meaning: assigned without intentional regard to user characteristics) does not imply "random" (meaning: independent of all other variables). A sequential counter is deterministic and predictable. The last digit of a sequential counter is uniform in distribution (each digit 0–9 appears equally often), but that's uniformity of the marginal distribution of treatment assignment — not independence from potential outcomes.

True randomization requires that assignment be independent of all other variables that affect the outcome. Uniform marginal distribution of assignment does not guarantee this. A perfectly uniform assignment that is entirely deterministic based on user ID can still be confounded if user ID itself correlates with outcome-relevant characteristics.

To use the Pearl framework: we cannot replace P(Y | T) with P(Y | do(T)) just because the assignment rule happens to produce a 50/50 split. The do-operator severs all incoming arrows to T. To claim that, we'd need to argue there are no arrows from U into T — and "last digit of sequential ID" is an arrow from sequential-ordering into T, which means anything that predicts sequential-ordering (cohort, account age, product-era) also predicts T.

---

## Can We Salvage a Causal Estimate?

Possibly, but only with additional work:

1. **Check for cohort imbalance.** Compare distributions of account age, registration date, product tier, and other pre-treatment covariates between the two groups. If they are balanced on all observable characteristics, the threat is reduced (though not eliminated).

2. **Control for account cohort.** If cohort is measured, include registration date (or ID range as a proxy) as a control. This closes the back-door path U → T and U → Y if U is fully captured. But this requires believing no other unmeasured cohort characteristics remain.

3. **Restrict to a narrow ID range.** If you analyze only users within a contiguous block of IDs (e.g., the last 10,000 users assigned before the bug was fixed), the within-block balance is much stronger and cohort effects are minimized by construction.

4. **Treat this as a natural experiment with scrutiny.** The last-digit rule could be argued as a "near-natural experiment" if balance checks pass. This is analogous to RDD logic applied to modular arithmetic — within each decade of IDs, the assignment is as-if-random. The overall estimate pools these within-decade comparisons and should be consistent with them.

5. **Run a formal balance test.** Pre-treatment covariates should be indistinguishable between groups if the assignment is truly as-if-random. Significant imbalance in observable covariates is prima facie evidence that unobservable confounds are also present.

---

## Summary Verdict

| Claim | Assessment |
|-------|------------|
| "User IDs are arbitrary, so the +4.2% is causal" (analyst) | **Wrong.** Arbitrary assignment ≠ random assignment. The last digit of a sequential ID is not independent of cohort or account age. |
| "This just compares newer users to older users" (engineer) | **Mostly right in spirit, overstated literally.** The last-digit split does produce within-cohort balance, but the analyst's premise is still wrong, and cohort confounding is a genuine threat that requires empirical verification. |
| "Can we use +4.2% as a valid causal estimate?" | **Not without additional analysis.** Balance checks, cohort controls, and narrowing the ID window can potentially salvage a credible estimate, but the raw +4.2% is not automatically valid. |

The senior engineer wins this argument — not because the mechanism is necessarily as severe as claimed, but because the analyst's justification is logically flawed. The burden of proof is on demonstrating balance and independence, not on assuming it because the ID scheme "feels" arbitrary.
