# experimental-design

An agent skill for designing, critiquing, and sizing experiments. The core job is answering **"how do I learn whether X causes Y, in a way I'd trust enough to act on?"** — for A/B tests, randomized trials, field experiments, and quasi-experiments.

## Five principles

1. **Comparison / control.** An effect only means something against a counterfactual. Always ask: *compared to what?*
2. **Randomization.** Random assignment makes treatment and control exchangeable on everything — measured and unmeasured — except the treatment. Without it you have correlation, not causation.
3. **Replication.** One unit per condition tells you nothing about noise. Unit of analysis must match unit of randomization.
4. **Local control.** Variance you remove by design (blocking, stratification, within-subjects) is cheaper than variance you overpower with sample size.
5. **Pre-specification.** Decide the primary metric, test, stopping rule, and success threshold *before* seeing outcome data. The "garden of forking paths" manufactures false positives with no intent to cheat.

## Reference files

| File | When to load |
|---|---|
| `references/design-selection.md` | Choosing between designs (between/within, factorial, cluster, stepped-wedge) |
| `references/online-experiments.md` | A/B tests at scale: SRM, CUPED, peeking, interference in social/marketplace products |
| `references/behavioral-experiments.md` | Lab/field behavioral studies: within-subject, factorial, counterbalancing, UXR pitfalls |
| `references/quasi-experiments.md` | When randomization is impossible: DiD, RD, ITS, synthetic control, matching/IPW |
| `references/power-and-sample-size.md` | Power, MDE selection, ratio-metric variance (delta method), cluster design effects, runtime |
| `references/interpreting-results.md` | Reading results: CIs, statistical vs. practical significance, Bayesian vs. frequentist decisions |

## `power_analysis.py` — examples

Pure standard library, no third-party dependencies. Runs in any environment.

```bash
# 10% → 11% (1pp absolute MDE), α=.05, 80% power → 14,751 / arm
python scripts/power_analysis.py --solve n --type proportion \
  --baseline 0.10 --mde 0.01

# 22% → 24% (2pp absolute), same settings → 6,950 / arm
python scripts/power_analysis.py --solve n --type proportion \
  --baseline 0.22 --mde 0.02

# 4.2% baseline, 5% relative lift → ~146,642 / arm (~10 weeks at 4,600 sessions/day)
python scripts/power_analysis.py --solve n --type proportion \
  --baseline 0.042 --mde 0.05 --relative

# Continuous metric: mean diff 0.5, sd=4 → 1,005 / arm
python scripts/power_analysis.py --solve n --type mean \
  --mde 0.5 --sd 4

# What power do I have with 5,000 / arm at 1pp MDE on a 10% baseline?
python scripts/power_analysis.py --solve power --type proportion \
  --baseline 0.10 --mde 0.01 --n 5000

# What's the smallest detectable effect with 20,000 / arm on a 10% baseline?
python scripts/power_analysis.py --solve mde --type proportion \
  --baseline 0.10 --n 20000

# Cluster-randomized design (ICC=0.02, ~200 users/cluster)
python scripts/power_analysis.py --solve n --type proportion \
  --baseline 0.10 --mde 0.01 --icc 0.02 --cluster-size 200
```

Run the tests:

```bash
python -m unittest scripts/test_power_analysis.py -v
```

## Install

**Upload the `.skill` file** in any Claude interface that supports skills (claude.ai → Settings → Skills → Upload).

**Or drop the folder** into your local skills directory:

```
~/.claude/skills/experimental-design/
```

The `.skill` package excludes `evals/` — that directory stays in the repo for benchmarking and is not needed at runtime.

## License

MIT — see [LICENSE](LICENSE).
