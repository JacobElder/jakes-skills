# Simpson's Paradox in Your A/B Test

## What you're seeing has a name

This is a textbook instance of **Simpson's Paradox**: a relationship that holds in the aggregate reverses (or vanishes) in every subgroup. In your case, the new feature appears to lift conversion by +2.1% overall, but is negative in both the mobile segment and the desktop segment.

The result is not a data error or a fluke. It is a structural property of how the data were generated — and the DAG tells you which number to trust.

---

## The causal question (naming the rung)

You are asking a **Rung 2 (intervention)** question: "If I ship this feature, will conversion go up?" Since this is an A/B test with random assignment to treatment and control, randomization handles confounding of the treatment assignment itself. The paradox arises not from a flaw in randomization, but from the relationship between the **segment variable** (mobile vs. desktop), the **treatment** (new feature), and the **outcome** (conversion).

---

## Why this is possible: a concrete mechanism

Here is the simplest DAG that produces the pattern you observed:

```
  Device type (mobile/desktop)
        |              |
        v              v
   Treatment        Conversion
   assignment        (Y)
   (X, randomized)
```

More precisely, the mechanism requires **two simultaneous facts**:

1. **The treatment group and control group have different compositions of mobile vs. desktop users.** Even with randomization at the user level, if mobile users are a larger share of the treatment arm than the control arm (or vice versa), the aggregate numbers will be "weighted" differently across arms.

2. **Mobile and desktop users have very different baseline conversion rates.** If, say, desktop users convert at 10% and mobile users convert at 2%, then whichever arm has more desktop users will look better in the aggregate — independent of the feature's true effect.

### Worked example

Suppose:
- Desktop: 1,000 users in treatment, 100 in control. Feature has −1% effect on desktop.
- Mobile: 100 users in treatment, 1,000 in control. Feature has −1% effect on mobile.
- Desktop baseline conversion: 10%, mobile: 2%.

| Arm | Desktop conversions | Mobile conversions | Total rate |
|-----|--------------------|--------------------|------------|
| Treatment | 1,000 × 9% = 90 / 1,000 | 100 × 1% = 1 / 100 | 91/1,100 = **8.3%** |
| Control | 100 × 10% = 10 / 100 | 1,000 × 2% = 20 / 1,000 | 30/1,100 = **2.7%** |

Aggregate lift: +5.6% (fabricated numbers, but the direction is real). Segment-specific effect: negative in both. The treatment arm happens to be dominated by high-converting desktop users, making it look good in aggregate — while the feature itself is harming both groups.

This is the mechanical cause of Simpson's Paradox: **segment is acting as a confounder in the aggregate comparison**, even though treatment was randomized, because it is not evenly distributed across arms.

---

## The DAG-based resolution: confounder case vs. mediator case

The SKILL.md framework is explicit:

> **Simpson's paradox.** A trend reverses when you slice the data differently. The DAG decides whether to use the disaggregated or aggregated view: **confounder → disaggregate; mediator → aggregate.**

You need to determine which structural role "device type" plays:

### Case 1: Device type is a confounder (fork)

```
  Device type
   ↙         ↘
Treatment    Conversion
```

Device type causes both *which arm users land in* (because randomization was not balanced across segments) and *the baseline conversion rate*. This is a **fork** — a classic confounder.

**Verdict: trust the disaggregated (segment-level) numbers.** The aggregate +2.1% is a weighted artifact driven by imbalanced segment composition across arms, not by the feature's true effect. The within-segment negative effects are the real signal.

### Case 2: Device type is a mediator (chain)

```
Treatment → Device type → Conversion
```

This would mean the feature *causes* users to switch devices (e.g., a mobile-only feature drives desktop users to mobile), and the downstream conversion change flows through that device-shift. In this case, conditioning on device type **blocks the causal path** you care about — the total effect includes the device-switching mechanism.

**Verdict: trust the aggregate number.** If the feature's effect on conversion partly operates by changing device behavior, removing that channel by stratifying on device type removes part of the effect you want to measure.

### Case 3: Device type is a collider

```
Treatment → Device type ← Conversion
```

Unlikely in this scenario, but if device type were caused by both treatment assignment and conversion (which would require a strange feedback loop), conditioning on it would open a spurious path. Don't stratify in this case either.

---

## Which case are you actually in?

Ask yourself one diagnostic question: **Did randomization produce balanced device-type distributions across treatment and control arms?**

Check this immediately:

```
treatment_arm_pct_mobile = mobile_users_in_treatment / total_treatment_users
control_arm_pct_mobile   = mobile_users_in_control   / total_control_users
```

If these numbers are materially different (more than a few percentage points), you have a **confounder case** — the aggregate +2.1% is misleading and you should trust the segment-level negatives.

If they are essentially equal (good balance), then the paradox has a different explanation and you should think harder about whether device type is on the causal pathway (mediator case).

**In the vast majority of real A/B tests, this is the confounder case.** Randomization ensures treatment assignment is independent of device type at the population level, but sample imbalance — especially with smaller experiments or if users were bucketed in a way that correlated with device — can produce meaningful compositional differences.

---

## What to do

1. **Run a balance check.** Compare device-type distribution across treatment and control. This is the decisive empirical question.

2. **If imbalanced (confounder case):** Use the segment-specific estimates. Alternatively, compute a properly weighted average treatment effect: compute the effect within each segment, then weight by the segment's share of the overall user population (not the share in each arm). This gives an unbiased aggregate estimate.

3. **If balanced (mediator case):** The aggregate +2.1% is likely the right number. Stratifying on device type is removing a real mechanism. Confirm by checking whether the feature changes device-usage patterns.

4. **Report both numbers with context.** Even in the confounder case, segment-specific effects (CATE — conditional average treatment effects) are often more actionable than a single aggregate number. Knowing the feature harms mobile users more than desktop users may matter for rollout decisions.

---

## What would change this answer

- **If the experiment had pre-stratified randomization by device type**, you'd be guaranteed balance and the confounder explanation would be ruled out. The aggregate would still be wrong if device is a mediator, but the confounder story wouldn't apply.
- **If "device type" is defined by post-treatment behavior** (i.e., device used during the experiment period, which the feature could influence), it is more likely a mediator or collider than a pre-treatment confounder. Don't stratify on it without thinking carefully.
- **If the sample is tiny**, the paradox could be noise. Check whether the segment-level effects are statistically meaningful before over-interpreting.

---

## Summary

| | Confounder case | Mediator case |
|--|--|--|
| Structure | Device type → Treatment AND Device type → Conversion | Treatment → Device type → Conversion |
| Segment imbalance? | Yes (or plausible) | No |
| Trust which number | Segment-level negatives | Aggregate +2.1% |
| Fix | Weight segments by population share | Do not stratify on device type |

The +2.1% aggregate and the negative segment effects are not contradictory — they are both mathematically consistent with the same data. The DAG tells you which one answers your actual causal question. Start with the balance check; it will almost certainly point to the confounder resolution and the segment-level negatives as the truth.
