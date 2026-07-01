# Scale development — deep reference

A pipeline based on Bandalos (2018), DeVellis (2017), Crocker & Algina (1986), and current best practice. The order matters; skipping early steps cannot be compensated for by sophisticated analyses later.

## Step 1: Define the construct

The single highest-leverage step. Items written before the construct is bounded measure "vibes about X" rather than X.

Components of a good construct definition:

- **A clear conceptual statement** of what the construct is.
- **Boundaries**: what it is *not* — related but distinct constructs that should be discriminable.
- **Dimensionality**: do you expect one factor or several? Why?
- **Domain map**: the facets or sub-areas of content the construct covers. Often presented as an outline or table.
- **Population**: for whom is this construct meaningful? (Some constructs don't generalize across ages, cultures.)
- **Variability**: what kind of differences across respondents are expected (continuous trait, categorical types, threshold effects)?

This becomes the **table of specifications** for item writing: items are sampled to cover the domain map, not whatever comes to mind first.

## Step 2: Check whether an instrument already exists

Search Mental Measurements Yearbook (MMY), Tests in Print, PsycTESTS, ERIC. Reasons to use an existing one:

- Established reliability and validity evidence.
- Comparability with prior research.
- Norms.

Reasons to build new:

- No existing measure for your specific construct or population.
- Existing measures are too long, copyrighted, or behind paywalls.
- Existing measures' theoretical foundation conflicts with yours.

Most "new" scales in the literature should not exist. Re-using a validated instrument with proper citation beats inventing a 5-item ad hoc scale.

## Step 3: Decide the item format

| Format | Use when |
|---|---|
| Multiple-choice | Knowledge/ability with discrete right answer; mass testing |
| True-false | Quick screening, limited use |
| Likert (agree-disagree, ordered) | Attitudes, beliefs, self-reported behaviors |
| Frequency (never→always) | Behaviors over a period |
| Semantic differential | Affective associations |
| Constructed response | Performance assessment, depth of understanding |
| Forced choice (ipsative) | Reduce social desirability; comparative judgments |

Format constrains analysis. Forced-choice scales are ipsative (within-person ranks), which complicates standard IRT/CFA — special methods like Thurstonian IRT (Brown & Maydeu-Olivares) are needed.

For detailed guidance on choosing between agree/disagree vs item-specific rating scales, forced-choice grids vs select-all-that-apply, bipolar vs unipolar structure, and the branching (two-step) alternative, see the **survey-design skill** — it owns response-format decisions at the design stage.

## Step 4: Write items — guidelines

For a full treatment of item-wording rules — double-barreled questions, leading/loaded
wording, negations, vague quantifiers, sensitive topics, and demographic/identity item
conventions — see the **survey-design skill**, which owns question wording at the design
stage. The guidelines below summarize the psychometrically critical subset.

### Universal guidelines

- **One idea per item** (no double-barreled: "I am happy and energetic" → split).
- **Simple, unambiguous language**. Aim for ~6th-grade reading level unless your population is specialized.
- **Avoid negatives** (especially double negatives): "I don't disagree that..." is a comprehension test, not an attitude measure.
- **Avoid universals** when not literally meant ("never", "always") — they produce ceiling/floor effects.
- **Avoid jargon** unless the population uses it.
- **Avoid leading wording** ("Don't you think...?", "Most experts agree...").
- **Cover the construct domain** per your table of specifications — not just convenient examples.

### For Likert items

- **5 or 7 categories** is the common range. 5 captures most variance, 7 gives slightly more precision; fewer than 5 loses information, more than 7 gets noisy.
- **Anchor extremes and (optionally) the midpoint**. All-anchored ("strongly disagree, disagree, neither, agree, strongly agree") is more standard than only endpoints.
- **Neutral midpoint** — controversial. Including it allows expression of true neutrality but invites it as a refuge ("not sure / can't be bothered"). Forcing a choice may pull responses to weak agreement/disagreement. Depends on the construct.
- **Time frame** if applicable: "in the past two weeks", "usually". Without it, respondents pick their own frame.

### Reverse-coded items — a critique

A long-standing recommendation: include "reverse-worded" items to detect acquiescent responding (people who agree with everything).

The problem (empirically established many times over): reverse-worded items often misbehave psychometrically — they tend to form a separate **method factor**, have lower discrimination, and produce worse fit. Items like "I am sad" reverse-keyed to "I am happy" don't map onto the same underlying continuum for many respondents.

Modern view: include reverse-worded items only if you have a substantive reason and have piloted them carefully. Use planned missingness and balanced item construction as alternative strategies for acquiescence.

### For cognitive items

- **Multiple-choice distractors** should be plausible to those who don't know — based on common misconceptions, not random wrong answers.
- **Item difficulty (p-value)** should range across the test, centered around .50 for maximum discrimination at the mean.
- **Avoid grammatical clues** in stem (e.g., "an" before only one option).
- **All options similar in length** — longer options get chosen.

## Step 5: Build the initial item pool

Aim for **2–3x the final number of items**. You will lose items to:

- Low discrimination (everyone responds the same way).
- Low item-total correlation.
- Cross-loading or unclear factor membership.
- Negative findings in cognitive interviews.
- Translation problems (if multi-language).

Starting with too few items means you have nothing to cut and must retrofit a too-short scale.

## Step 6: Initial item review

Two types of review before you collect any data:

### Expert content review

Send the item pool to 5–10 subject-matter experts. Ask them to:

- Rate each item for **relevance** to the construct (e.g., 1–5).
- Rate each item for **clarity / unambiguousness**.
- Suggest items that may be missing from the domain.

Aggregate: drop items with low relevance ratings; revise items with low clarity. The **content validity ratio (Lawshe, 1975)** formalizes the relevance review.

### Cognitive interviews

5–10 respondents from the target population. Think-aloud or retrospective probing on every item:

- "What did you think about when you answered this?"
- "What does X mean to you here?"
- "Why did you choose that option?"

This catches problems no statistic will reveal: items interpreted differently than intended, items recalling specific past events instead of general patterns, items missing relevant content from the respondent's perspective.

**Skipping cognitive interviews is the most common single failure point in scale construction.** It's also the cheapest to do (a single afternoon).

For a detailed protocol on running cognitive interviews, expert review, split-ballot experiments, and SQP-based pre-fielding evaluation, see the **survey-design skill** — those pretesting techniques are instrument-design work, not psychometric analysis.

## Step 7: Pilot study

Small sample (N = 30–100) for:

- Item distributions: skew, ceiling/floor, missing data per item.
- Item-total correlations (corrected for the item itself).
- Inter-item correlations.
- Rough internal consistency.

Items with extreme skew, very low corrected item-total correlation (r < .15 or so), or zero variance go to revise or drop.

Don't run EFA on N = 30 — wait for the field test. The pilot is for cleaning, not structure.

## Step 8: Field test — the main calibration study

Sample size depends on planned analyses:

| Analysis | Approximate minimum N |
|---|---|
| Item analysis, CTT reliability | 100–200 |
| EFA with strong factors | 200–300 |
| EFA with weak factors / many items | 500+ |
| CFA | 200+ for moderate complexity; 500+ for ordinal WLSMV |
| 2PL IRT | 500 |
| GRM | 500 |
| Measurement invariance | 200+ per group |

Real practice: oversample. Sample diversity (across the construct's relevant variables) matters as much as raw N.

Decisions to make in advance:

- **Sampling frame**: who you actually need, not just convenience.
- **Mode**: online, paper, interview. Mode affects responses (web vs. phone, e.g., social desirability differs).
- **Order randomization**: randomize item order across respondents to avoid order effects on item statistics.
- **Attention checks**: items like "Please select 'Strongly Disagree' for this item". Use sparingly; some research suggests they degrade data quality among compliant respondents.
- **Demographics**: collect what you need for invariance testing and norming.

## Step 9: Item analysis and dimensionality

For each item:

- **Distribution**: histogram, response frequencies per option.
- **Item difficulty** (for cognitive items): p-value, proportion correct.
- **Item discrimination**: corrected item-total correlation, or point-biserial for cognitive items. Items with low discrimination drop.
- **Distractor analysis** (multiple-choice): each distractor should be chosen by some, especially low-θ respondents.

Then dimensionality:

- Parallel analysis to estimate # of factors.
- EFA with polychoric correlations (for Likert).
- Inspect loadings, cross-loadings, communalities.
- Iteratively refine: drop poor items, refine factor structure.

This is where you find out if your construct definition matches the empirical structure. Often it doesn't — some "facets" you thought were distinct merge; some items end up loading where you didn't expect. Treat these as substantive feedback, not failures.

## Step 10: CFA on independent sample

Take your refined model from EFA and confirm on a *separate* sample. Without this, your "confirmed" structure is overfit to noise.

Conventional designs:

- **Random split of one large sample**: 50/50 or 60/40. Cheaper; same population.
- **Two independent samples**: stronger; ensures cross-sample generalizability.

CFA gives you fit indices, modification indices (use sparingly), and a cleaner reliability estimate via omega (`semTools::compRelSEM(fit)`).

## Step 11: Reliability and validity evidence

- Internal consistency: omega-total and alpha, per scale/subscale.
- Test-retest (if a trait — schedule a subsample to re-take after 2–6 weeks).
- Convergent/discriminant evidence: correlate with related measures and presumed-distinct measures.
- Criterion / predictive evidence: correlate with outcomes the construct should predict.
- Group differences where theory predicts them.

See `validity.md` for the full source-of-evidence framework.

## Step 12: Norms (if you'll interpret individual scores)

For norm-referenced interpretation, you need:

- A **representative norming sample** for the population in which scores will be interpreted.
- **Sample size** scaling with the granularity of norms (overall norms: ~1000; norms by age/sex/region: many more).
- **Transformation table**: raw scores → percentiles, T-scores, NCEs, etc.
- **Updated norms** periodically — Flynn effects (for cognitive tests), generational shifts (for attitudes) make old norms misleading.

If you'll only interpret scores in *relative* terms (within-group comparison, change over time), you don't need norms.

## Step 13: Documentation

A scale isn't done when items are finalized. Document:

- Construct definition and theoretical basis.
- Item development process and decisions.
- Sample characteristics for all calibration studies.
- Recommended scoring (sum, average, factor scores, IRT scoring).
- Reliability estimates (with samples).
- Validity evidence (with sources).
- Measurement invariance results.
- Norms (if applicable).
- Recommended interpretations, ranges, cutoffs.
- **Limitations** — populations where the scale is not validated, languages not tested, etc.

A manual or technical report is the deliverable. "Use this 12-item scale" without the supporting documentation just propagates ad-hoc measures.

## Common scale-construction mistakes

- **Skipping the construct definition step** — items chase intuition.
- **Writing too few items in the initial pool** — no slack for revision.
- **Skipping cognitive interviews** — wording problems carry through forever.
- **Treating the development sample as the validation sample** — overfit; needs replication.
- **Using only EFA, never confirming** — exploratory structure presented as definitive.
- **Reporting alpha as if it's sufficient evidence** — alpha alone tells you almost nothing about whether the scale measures the construct.
- **Failing to test invariance before applying across groups** — implicit assumption of comparability.
- **Continuing to reverse-code items by reflex** — often hurts more than it helps.
- **Adding items late based on reviewer comments without re-piloting** — destabilizes the established structure.

## Quick R workflow for a calibration sample

```r
library(psych); library(lavaan); library(semTools)

# Step 1: Inspect
describe(d)
response.frequencies(d)
cor.plot(polychoric(d)$rho)

# Step 2: How many factors?
fa.parallel(d, fa = "fa", cor = "poly")

# Step 3: EFA
efa <- fa(d, nfactors = 3, fm = "minres", rotate = "oblimin", cor = "poly")
print(efa, cut = .30, sort = TRUE)

# Step 4: Reliability per provisional scale
alpha(d[, scale1_items])
omega(d[, scale1_items], poly = TRUE)

# Step 5 (on holdout): CFA
model <- 'F1 =~ x1 + x2 + x3 + x4
          F2 =~ x5 + x6 + x7 + x8
          F3 =~ x9 + x10 + x11 + x12'
fit <- cfa(model, data = d_holdout, ordered = names(d_holdout), 
           estimator = "WLSMV")
summary(fit, fit.measures = TRUE, standardized = TRUE)
compRelSEM(fit)
```

That's the skeleton. The art is in the decisions between steps — which items to drop, what to do about a stubbornly multidimensional scale, when to call it good enough.
