# Multiverse Analysis Skill

A skill that makes the agent *perform* a multiverse / specification-curve analysis, not just describe one. It front-loads decision elicitation and honest framing, then executes: enumerate the decision grid, run every universe, plot the specification curve, quantify which choices drive the variance, and do joint permutation inference.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/multiverse-analysis
```

Or manually:

```bash
cp -r jakes-skills/multiverse-analysis ~/.claude/skills/multiverse-analysis
```

Once installed, the skill applies automatically whenever you ask about multiverse analysis, specification curve analysis, researcher degrees of freedom, the garden of forking paths, vibration of effects, or robustness to analytic choices — including when you are anxious that your result "might just be an artifact of how I set up the analysis," even without knowing those terms.

---

## What it does

The 7-step workflow: **pin the estimand → elicit decisions → flag nonsensical cells → run every universe → describe the distribution → quantify which decisions matter → do joint inference**.

Steps 1–3 are judgment and reasoning with you. Steps 4–7 are execution using the bundled `scripts/multiverse.py` engine (pandas / numpy / matplotlib only) or R's `multiverse` / `specr` packages. The skill ships with both a Python engine and R snippets; the R examples have been executed against `multiverse` 0.6.2 and `specr` 1.0.0.

---

## Worked example (15 lines)

```python
import sys; sys.path.insert(0, "~/.claude/skills/multiverse-analysis/scripts")
from multiverse import Multiverse, specification_curve, decision_importance, permutation_test
import pandas as pd

data = pd.read_csv("study.csv")   # columns: group (0/1), outcome, baseline

def analyze(data, c):
    df = data.copy()
    if c["outliers"]:
        z = (df["outcome"] - df["outcome"].mean()) / df["outcome"].std()
        df = df[z.abs() <= c["outliers"]]
    import statsmodels.formula.api as smf
    rhs = "group + baseline" if c["covariate"] else "group"
    m = smf.ols(f"outcome ~ {rhs}", data=df).fit()
    return {"estimate": m.params["group"], "p_value": m.pvalues["group"],
            "ci_low": m.conf_int().loc["group", 0], "ci_high": m.conf_int().loc["group", 1]}

mv = Multiverse(decisions={
    "outliers":  {"none": None, "3sd": 3.0, "2sd": 2.0},
    "covariate": {"no": False, "yes": True},
})
res = mv.run(analyze, data)
specification_curve(res, outfile="curve.png")
print(decision_importance(res))
permutation_test(mv, analyze, data, shuffle="group", n_perm=500)
```

---

## Honest framing enforced

The skill is opinionated — deliberately so. It will tell you when your effect is fragile, warn against using the multiverse to cherry-pick a preferred specification, flag when mixing DVs on different scales makes the specification curve meaningless, and apply the "reasonable specification" criteria to curate the decision set rather than pad it.

---

## References

- Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science*, 11(5), 702–712.
- Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. *Nature Human Behaviour*, 4(11), 1208–1214.
- Sarma, A., & Kay, M. (2020). Prior setting in practice: Strategies and rationales used in choosing prior distributions for Bayesian analysis. *CHI 2020*. (multiverse R package)
- Schweinsberg, M., et al. (2021). Same data, different conclusions. *Organizational Behavior and Human Decision Processes*, 165, 228–249.
