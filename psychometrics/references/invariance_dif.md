# Measurement invariance & DIF — deep reference

If you're comparing groups (gender, country, age cohort, intervention condition) on a latent construct, you need to first establish that the measurement model is **invariant** across those groups. Otherwise, observed group differences in scores conflate true differences in the construct with differences in how the instrument behaves.

This is the most underused critical step in applied measurement work.

## What invariance means

The construct has the **same meaning and metric** across groups. Specifically: a person at θ = 1 in group A and a person at θ = 1 in group B should have the same expected item responses.

When invariance fails, scores can't be compared between groups in the way most readers assume.

## Levels of invariance (CFA framework)

Tested as a sequence of nested models with progressively stronger constraints:

### 1. Configural invariance

Same factor structure (same items load on same factors) across groups, but all parameters free.

- *Tests*: same conceptual structure.
- *If it fails*: the construct is structurally different across groups — comparison isn't meaningful at any level.

### 2. Metric (weak) invariance

Configural + **factor loadings constrained equal** across groups.

- *Tests*: items relate to the latent factor with the same strength in each group. The construct is on the same metric.
- *If it holds*: you can compare relations among constructs across groups (e.g., the structural path from F1 → F2). You cannot yet compare means.
- *If it fails*: items measure the construct with different sensitivity across groups.

### 3. Scalar (strong) invariance

Metric + **item intercepts constrained equal** across groups.

- *Tests*: items have the same expected score at the same θ across groups.
- *If it holds*: **observed mean differences can be interpreted as latent mean differences**. This is the level you need for cross-group mean comparison.
- *If it fails*: groups differ in baseline item responses at the same construct level. Observed differences conflate true differences with intercept biases.

### 4. Strict (residual) invariance

Scalar + **item residual variances constrained equal** across groups.

- *Tests*: measurement error variance is the same across groups.
- *If it holds*: you can compare observed score reliabilities across groups directly.
- Often not required for substantive comparisons; getting to scalar is usually enough.

### 5. (Optional) Structural invariance

Equal latent variances, latent covariances, and/or latent means across groups. These are usually the *hypotheses you're testing*, not constraints you impose for invariance.

## The standard workflow

```r
library(lavaan)
library(semTools)

model <- 'F1 =~ x1 + x2 + x3 + x4
          F2 =~ x5 + x6 + x7 + x8'

# Sequential testing
fit_config <- cfa(model, data = d, group = "country")
fit_metric <- cfa(model, data = d, group = "country",
                  group.equal = "loadings")
fit_scalar <- cfa(model, data = d, group = "country",
                  group.equal = c("loadings", "intercepts"))
fit_strict <- cfa(model, data = d, group = "country",
                  group.equal = c("loadings", "intercepts", "residuals"))

# Compare nested models
lavTestLRT(fit_config, fit_metric, fit_scalar, fit_strict)
# Or use the modern wrapper
measurementInvariance(model = model, data = d, group = "country")  # older, still works
```

For ordinal data (Likert items), the workflow needs care because intercepts → thresholds, and the parameterization (delta vs. theta) matters. Use `semTools::measEq.syntax()`:

```r
syntax_scalar <- measEq.syntax(
  configural.model = model,
  data = d,
  ordered = ord_items,
  parameterization = "theta",
  ID.fac = "std.lv",
  ID.cat = "Wu.Estabrook.2016",
  group = "country",
  group.equal = c("thresholds", "loadings", "intercepts")
)
fit_scalar <- cfa(as.character(syntax_scalar), data = d, ordered = ord_items, 
                  parameterization = "theta", group = "country")
```

Wu & Estabrook (2016) is the standard treatment for ordinal invariance.

## How to judge whether invariance holds

Two approaches; report both:

### 1. Chi-square difference test

Strict: a significant Δχ² means invariance is rejected at that level.

Problem: Δχ² is sensitive to large N. Reject with N = 5000 even when the misfit is trivial.

For MLR/WLSMV, use **scaled** chi-square difference (Satorra-Bentler 2001 or 2010). `lavTestLRT(..., method = "satorra.bentler.2010")`.

### 2. Change in approximate fit indices

Cheung & Rensvold (2002) and Chen (2007) proposed cutoffs based on practical significance:

- **ΔCFI ≤ −.010** (often −.010 to −.020): invariance untenable.
- **ΔRMSEA ≥ .015**: invariance untenable.
- **ΔSRMR ≥ .030** (metric) or **.010** (scalar/strict).

These are guidelines, not laws. Report both Δχ² and ΔCFI/ΔRMSEA; if they conflict, discuss.

## Partial invariance

If scalar invariance fails at the omnibus level, you can identify which item(s) drive the failure and free those parameters while constraining the rest. This is **partial scalar invariance**.

The procedure (Byrne, Shavelson & Muthén, 1989):

1. Establish metric invariance.
2. Add intercept constraints one at a time, or all at once and release based on modification indices.
3. Identify items with the largest intercept differences (largest MIs).
4. Free those item intercepts; require at least 2 items per factor to remain invariant (for identification + interpretation).
5. Test the partially invariant model.

**When is partial invariance acceptable?**

- If you can defend the released items substantively (translation differences, cultural variation in item interpretation) — yes.
- If you've released > ~20% of loadings or intercepts — red flag; the construct may not be comparable.
- For binary group comparison of means: at least 2 invariant intercepts per factor are needed (Steenkamp & Baumgartner, 1998).

Partial invariance is a pragmatic compromise, not a clean victory. Report what you released and why.

## Differential item functioning (DIF)

DIF is the item-level analog of scalar invariance failure: an item's response probability differs across groups for respondents at the same θ.

### DIF detection methods

#### Mantel-Haenszel (Holland & Thayer, 1988)

Stratify respondents by total score; test whether the odds of correct response differ across groups within strata.

```r
library(difR)
difMH(data, group = group_var, focal.name = "F")
```

- Pro: nonparametric, well-understood, includes effect size (MH D-DIF — ETS classification A/B/C for negligible/moderate/large).
- Con: works best for dichotomous items; uses observed score as a proxy for θ, which can be biased.

#### Logistic regression (Swaminathan & Rogers, 1990)

Regress item response on (1) total score, (2) group, (3) group × score interaction.

- Significant group effect → **uniform DIF** (item harder for one group at all θ levels).
- Significant interaction → **non-uniform DIF** (DIF differs across θ).

```r
difLogistic(data, group = group_var, focal.name = "F", type = "both")
```

Handles ordinal items with ordinal regression (`difLogistic` with appropriate options or `difORD`).

#### IRT-based DIF

Compare item parameters (a, b for 2PL) across groups directly. Lord's chi-square or likelihood-ratio test (Thissen, Steinberg, & Wainer, 1988).

```r
library(mirt)
fit_multi <- multipleGroup(data, 1, group = group_var)
DIF(fit_multi, which.par = c("a1", "d"), scheme = "drop")
```

- Pro: full IRT framework, accounts for θ properly.
- Con: needs IRT-appropriate sample sizes — **minimum ~200 per group for 2PL-based DIF**; below this, parameter estimates are unstable and DIF tests are unreliable. Mantel-Haenszel and logistic regression methods work with smaller samples (~100 per group minimum).

#### Ordinal DIF (polytomous items): `lordif`

For Likert/polytomous items, use ordinal logistic regression with IRT-based matching:

```r
library(lordif)
out <- lordif(data_matrix, group_vector,
              criterion = "R2",  # Nagelkerke R2 change
              alpha = 0.01,
              beta.change = 0.035)  # moderate DIF threshold (Jodoin & Gierl 2001)
plot(out)  # item-level DIF plots
```

Jodoin & Gierl (2001) ΔR² thresholds (Nagelkerke):
- < .035: **negligible** DIF
- .035–.070: **moderate** DIF — review item
- > .070: **large** DIF — strong candidate for removal or revision

### Uniform vs. non-uniform DIF

- **Uniform**: item consistently advantages one group across all θ. Corresponds to intercept differences in CFA (scalar non-invariance).
- **Non-uniform**: item advantages different groups at different θ levels. Corresponds to loading differences in CFA (metric non-invariance).

Both are detected by logistic regression and IRT methods; Mantel-Haenszel detects uniform only.

### Effect size matters

A statistical DIF test with N = 10,000 will flag tiny, practically irrelevant differences. Always report effect sizes:

- Mantel-Haenszel D-DIF (ETS classification A/B/C).
- Standardized P-DIF (proportion difference standardized).
- For logistic regression: ΔR² (Nagelkerke); Jodoin & Gierl thresholds.

Small effect, statistically significant → probably not worth acting on.

## DIF ≠ bias

DIF is a statistical finding. Bias requires showing the DIF is **construct-irrelevant**.

Example: a math word problem with culturally specific references (baseball) shows DIF favoring respondents from baseball-cultures. This is bias because baseball familiarity is construct-irrelevant for math.

A different example: an item testing knowledge of post-1990s technology shows DIF favoring younger respondents. This is *not* bias if the construct is "current technology familiarity"; younger people do know more about it, and the DIF reflects a true construct difference.

**The DIF investigation has two steps**:

1. Statistical detection: does this item function differently?
2. Substantive review: is the difference attributable to a construct-irrelevant feature of the item?

Sensitivity reviews by content experts familiar with both groups are how step 2 is typically done.

## Anchor items

DIF testing requires that *some* items be assumed DIF-free (anchors) to put both groups on a common scale. Approaches:

- **All-other-as-anchor**: test each item with all others as anchor. Subject to DIF contamination if many items have DIF.
- **Iterative purification**: start with all items, identify DIF, drop suspected DIF items from anchor, retest. `difR` and `lordif` support this.
- **Pre-designated anchors**: based on prior research or theory.

Anchor choice can substantially affect DIF detection — be explicit about how you chose them.

## Practical guidance

- **Before any cross-group comparison of means**: test invariance through scalar.
- **For published cross-cultural scales**: invariance is rarely established at scalar across many countries — partial scalar is often the realistic ceiling.
- **For longitudinal designs**: test invariance across time (same items, same people, different occasions). Failure means observed change confounds construct change with measurement change.
- **For interventions**: test invariance across treatment and control if comparing post-intervention means. Some interventions can shift item interpretation (response shift).
- **Report invariance results before interpreting group means**. Reviewers increasingly expect this.

## Common mistakes

- **Comparing group means without testing invariance** — the dominant mistake in applied work.
- **Stopping at metric invariance and comparing means** — metric is for comparing relations, not means.
- **Treating Δχ² as the only criterion** — too sensitive with large N.
- **Treating ΔCFI ≤ .010 as the only criterion** — too lax with very large differences in small parts of the model.
- **Releasing intercepts via MI-chasing without substantive justification** — partial invariance becomes a fitting exercise.
- **Confusing DIF with bias** — automatic action on DIF without substantive review.

## Software summary

- **lavaan + semTools** for CFA-based invariance (continuous + ordinal).
- **mirt** for IRT-based invariance and DIF (`multipleGroup`, `DIF`).
- **difR** for classic dichotomous DIF (MH, logistic, Lord's chi-square, BD, GMH).
- **lordif** for ordinal DIF using ordinal logistic regression with IRT linking.
