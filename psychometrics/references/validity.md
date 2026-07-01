# Validity — deep reference

The single most important conceptual shift to internalize: **validity is a property of score interpretations and uses, not of a test.** "The scale is valid" is a category error. "Scores from this scale support interpretation as depression severity for clinical screening in adult primary-care samples" is a validity claim.

This is the modern unified view (Messick, 1989, 1995; AERA/APA/NCME *Standards*, 2014).

## The old "three Cs" view (do not use this framing)

Historically validity was carved into:

- **Content validity** — items represent the domain
- **Criterion validity** — predictive or concurrent correlation with a criterion
- **Construct validity** — measures the intended theoretical construct

This framework was retired by Messick and the *Standards* because (1) construct validity subsumes the others — content and criterion evidence are *sources* of construct validity — and (2) the framing encouraged people to "check off" types of validity rather than building an argument.

You will still see these terms in older papers. Translate them into the unified view when you encounter them.

## The unified view: sources of validity evidence

The 2014 *Standards* identify five sources of validity evidence. A validation effort builds an **argument** drawing on multiple sources appropriate to the intended interpretation and use.

### 1. Evidence based on test content

Does the content of the items reflect the construct domain?

Methods:
- **Subject-matter expert (SME) review** of items for relevance and representativeness.
- **Content validity ratio** (Lawshe, 1975): for each item, what proportion of SMEs rate it "essential"?
- **Two-way mapping**: items × construct facets, ensuring each facet is covered without overrepresentation.
- For ability tests: item-by-objective alignment with a specified blueprint.

What it doesn't establish: that respondents actually engage with items the way SMEs assume. That's response process evidence.

### 2. Evidence based on response processes

Are test-takers actually doing the cognitive (or affective) work the construct calls for?

Methods:
- **Think-aloud protocols** during item response (Ericsson & Simon).
- **Cognitive interviews** post-response on why respondents chose options.
- **Eye-tracking, response-time analysis** for cognitive tests.
- For self-report: how respondents interpret items (Tourangeau, Rips & Rasinski model — comprehension, retrieval, judgment, response).

This source is **chronically underreported** and is where many "valid" scales fail. Items that SMEs approved can be interpreted entirely differently by respondents.

### 3. Evidence based on internal structure

Does the internal structure of item responses match the theoretical structure of the construct?

Methods:
- **Factor analysis** (EFA, CFA) — see `factor_analysis.md` and `cfa_sem.md`.
- **IRT model fit** — does a unidimensional IRT model fit, or do items load on different dimensions?
- **Reliability** — internal consistency is a special case of internal structure evidence (consistent items → unidimensional → supports interpretation as one construct).
- **Measurement invariance** across groups — does the structure hold across subgroups for which the construct is presumed to mean the same thing? See `invariance_dif.md`.
- **Differential item functioning** — items that perform differently across groups beyond what the construct would predict.

### 4. Evidence based on relations to other variables

This is the empirical heart of construct validation — does the score behave the way the construct's theory says it should?

Sub-types:

- **Convergent validity**: correlates with other measures of the same construct (especially using different methods).
- **Discriminant validity**: doesn't correlate (or correlates less) with measures of related-but-distinct constructs.
- **Concurrent validity**: correlates with a criterion measured at the same time.
- **Predictive validity**: predicts a future criterion.
- **Incremental validity**: predicts the criterion above and beyond existing measures.

The most rigorous design for convergent + discriminant evidence is the **multitrait-multimethod (MTMM) matrix** (Campbell & Fiske, 1959):

- Multiple traits × multiple methods, all crossed.
- Monotrait-heteromethod correlations (same trait, different methods) should be **high** = convergent validity.
- Heterotrait-monomethod (different traits, same method) should be **lower** than monotrait-heteromethod = discriminant validity, and shows method variance isn't inflating things.
- Heterotrait-heteromethod should be lowest.

MTMM is hard to execute (you need multiple validated methods per construct), which is why it's rarely done — but its logic should inform any convergent/discriminant claim. CFA models for MTMM (correlated traits–correlated methods, correlated traits–correlated uniquenesses) formalize it.

### 5. Evidence based on consequences of testing

Messick's most controversial contribution: the *intended and unintended* consequences of test use are part of validity. A test that produces accurate scores but, when used for placement decisions, systematically disadvantages a group it shouldn't — that's a validity problem, not just a fairness problem.

This source is contested. Some methodologists (e.g., Borsboom et al., 2004) argue consequences belong to ethics and policy, not validity per se. The *Standards* include it. Pragmatically: if a paper proposes a high-stakes use of a test, expect reviewers to ask about consequences.

## The validation argument (Kane)

Kane (1992, 2006, 2013) reframed validation as building and evaluating an **interpretation/use argument** (IUA):

1. **Specify the proposed interpretation and use** clearly.
2. **Lay out the inferential chain** from observed responses → scored data → trait interpretation → decision/use.
3. **Each inference has assumptions** that need empirical or logical support.
4. **The strongest objection to each assumption** should be identified and addressed.

This is more disciplined than "we found r = .50 with another scale, validity established." It forces you to be specific about *what* you claim the scores mean and *how* you'll use them.

Practical workflow for a new instrument:
1. Define the construct boundaries (what's in, what's out).
2. Specify intended interpretation and use(s).
3. List the inferences and assumptions required.
4. Plan studies (content review, response processes, internal structure, external relations) that test those assumptions.
5. Report the assumptions that are well-supported, partially supported, and untested.

## Face validity

**Face validity is not validity.** "Looks like it measures X" is a perception, useful for test-taker buy-in and political acceptability, but provides no evidence about score interpretation. Don't list face validity as evidence; you can mention it separately as a usability consideration.

## Specific things to flag in critiques

- **"We used a validated scale" without sample-specific evidence** — validation is contextual; evidence in one sample doesn't transfer automatically to a different population.
- **A single correlation cited as "construct validity"** — construct validity is a body of evidence, not one number.
- **Confounded convergent evidence** — if the "different measure" you correlate with shares methods (both are self-report, both administered together), the correlation may reflect method variance, not construct overlap.
- **Predictive validity with restriction of range** — if the sample is selected on the predictor, r underestimates true validity; correction formulas exist.
- **Criterion contamination** — if the criterion was influenced by the predictor (raters who knew test scores), the validity coefficient is inflated.
- **Validity-reliability paradox** — the reliability ceiling on validity: r_xy ≤ √(ρ_x × ρ_y). A low-reliability test cannot have high validity. Correction for attenuation can be reported but with care (it's an estimate of theoretical maximum, not a sample claim).

## Quick R notes

- MTMM correlations: just compute a labeled correlation matrix and inspect the pattern; CFA-MTMM via `lavaan`.
- Convergent/discriminant in CFA: compare **average variance extracted (AVE)** to **squared inter-factor correlation** (Fornell & Larcker, 1981). AVE > squared r supports discriminant validity. The Heterotrait-Monotrait ratio (HTMT; Henseler et al., 2015) is now often preferred over Fornell-Larcker.
- `semTools::discriminantValidity()` computes both Fornell-Larcker and HTMT from a fitted CFA model.

## Recommended reading

- Messick (1989) chapter in Linn (ed.), *Educational Measurement* (3rd ed.) — the foundational unified-validity statement.
- Kane (2013) "Validating the interpretations and uses of test scores" — the IUA framework.
- AERA/APA/NCME (2014) *Standards for Educational and Psychological Testing* — the authoritative reference.
- Borsboom, Mellenbergh & van Heerden (2004) "The concept of validity" — the critique of consequential validity worth engaging with.
