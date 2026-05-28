# Transcript: ERGM Degeneracy Triangle — With Skill

## Task

User asked whether they should report results from an ERGM fitted to a 180-student friendship network with the specification:

```r
library(statnet)
fit <- ergm(net ~ edges + triangle + kstar(2) + nodematch('gender'))
summary(fit)
```

They reported a significant triangle coefficient of 0.85 (p < 0.001) and asked if the results were valid.

---

## Steps taken

### Step 1: Read SKILL.md
Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md` in full.

Key finding: Section "3. Statistical network models require care: ERGM degeneracy is real" explicitly flags that `triangle` and `kstar(2)` are "almost always degenerate" and directs to `references/ergm_saom.md`. The common mistakes list includes: "Using `triangle` in an ERGM. Almost always degenerate. Use `gwesp` (decay typically 0.25–0.75; estimate it if data permit)."

### Step 2: Read references/ergm_saom.md
Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/ergm_saom.md` in full.

Key findings:
- The degeneracy problem section confirms `triangle` and `kstar(2)` are the primary degenerate terms.
- The fix is GWESP (replaces triangle) and GWDEGREE (replaces kstar) — geometrically weighted statistics from Snijders et al. (2006) and Hunter & Handcock (2006).
- Diagnostics (`mcmc.diagnostics()` and `gof()`) are explicitly "not optional."
- The practical workflow section provides a step-by-step incremental build approach.

### Step 3: Verified output directories exist
Confirmed `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis-workspace/iteration-1/ergm-degeneracy-triangle/with_skill/outputs/` exists and is empty.

### Step 4: Drafted and wrote response
Wrote full response to `outputs/response.md`. Response covers:
- Clear "No, do not report" verdict
- Mechanistic explanation of why degeneracy occurs with triangle/kstar
- How to detect degeneracy in the existing fit via mcmc.diagnostics() and gof()
- Corrected R code using gwesp + gwdegree
- Term-by-term substitution table
- Incremental build workflow
- What to report once the model is clean
- Single-wave causal inference caveat
- Pre-submission checklist
- Canonical references

### Step 5: Wrote metrics.json and transcript.md

---

## Skill application notes

The skill's core principle 3 ("ERGM degeneracy is real") was the primary guide. The reference file confirmed the mechanism, provided the correct R syntax, and supplied the canonical citations (Snijders et al. 2006; Hunter & Handcock 2006). The response follows the skill's "common mistakes" list explicitly and uses the recommended workflow from `ergm_saom.md` section "Practical workflow for an ERGM analysis."
