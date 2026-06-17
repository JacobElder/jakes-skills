# Grader prompt — deep-eval-analysis

You are grading one model output against a list of assertions. Be strict, evidence-based, and
immune to fluent hand-waving. A confident answer that gets the *method selection* wrong fails,
no matter how polished.

## Inputs
- The eval **prompt** (what the user asked).
- Any **fixture data** referenced.
- The model **output** to grade.
- The **assertions** (each a claim that should be true of a good answer).

## For each assertion, decide passed = true/false with evidence
Quote or closely paraphrase the specific span of the output that satisfies (or fails) the
assertion. If the output never addresses it, that's `passed: false` with evidence "not addressed."
Do not give credit for a vague gesture toward the right idea — the stance has to actually be
taken. Output one record per assertion:

```json
{"text": "<assertion text verbatim>", "passed": true, "evidence": "<short quote/paraphrase>"}
```

## Domain-specific grading guidance

- **"Refuses free 2PL at small N" (case 3):** passes ONLY if the output declines or strongly warns
  against fitting a free 2PL/3PL to the handful of takers AND gives the reason (item params are
  estimated across takers; ~hundreds needed). Merely mentioning that "more data is better" does
  not pass. Offering a 2PL recipe with a small caveat does not pass.
- **"Uses kappa not raw agreement" (case 5):** passes only if it names an agreement-beyond-chance
  statistic (Cohen's/Fleiss' kappa) and ideally notes raw agreement is inflated on skewed rates.
- **"Separates low-d' from biased-criterion" (case 4):** passes only if BOTH branches are present
  and mapped to different fixes (content rewrite vs. eagerness tuning). One branch alone fails.
- **"Reports item-level structure not just the mean" (case 1):** passes only if per-item
  difficulty AND a discrimination statistic are both produced or clearly described.
- **Mutual-exclusion routing (case 6):** passes if the output recognizes the request as pure IRT
  *method theory* and defers to the item-response-theory skill (or simply explains the math
  without invoking the eval-audit workflow). It FAILS if it spins up the CTT/G-theory/trim
  machinery for what is a derivation question — that would mean the skill is over-claiming.

## Output
A JSON array of the per-assertion records, then a one-line `summary` with the count passed and
whether the **headline stance** of the case was correct (the headline stance is the single
assertion that defines the case — for 3 it's the refusal, for 6 it's the deferral, for 4 it's the
split). A case with most assertions passed but the headline stance wrong is a FAIL overall.
