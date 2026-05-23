# nilearn-fmri skill

A Claude skill for running fMRI analyses with [nilearn](https://nilearn.github.io): GLM, functional connectivity, decoding/MVPA, and visualization.

## Structure

```
nilearn-fmri/
├── SKILL.md                      # Main skill: workflow + routing
├── references/                   # Loaded on demand for the workflow at hand
│   ├── datasets.md               #   built-in fetchers, BIDS, fMRIPrep, atlases
│   ├── glm.md                    #   first-level, second-level, contrasts, thresholding
│   ├── connectivity.md           #   maskers, ConnectivityMeasure, seed-based
│   ├── decoding.md               #   Decoder, MVPA, searchlight, weight maps
│   └── visualization.md          #   static plots, interactive views, reports
├── scripts/                      # Parameterized end-to-end helpers
│   ├── run_first_level_glm.py
│   ├── run_second_level_glm.py
│   ├── extract_connectome.py
│   ├── run_decoder.py
│   └── make_report.py
└── evals/
    ├── evals.json                # 3 tests covering GLM, connectivity, decoding
    └── files/
        ├── make_fixtures.py      # generates the synthetic NIfTIs below
        ├── glm/                  # bold + events + brain_mask
        ├── connectivity/         # 3 subjects + atlas + confounds
        └── decoding/             # bold + labels + vt_mask
```

## Requirements

```bash
pip install nilearn nibabel
```

Nilearn pulls in numpy, scipy, scikit-learn, pandas, joblib, matplotlib automatically.

## Why synthetic fixtures instead of nilearn's built-in fetchers?

The skill *recommends* nilearn's built-in fetchers (`fetch_haxby`, `fetch_adhd`, `fetch_development_fmri`, etc.) for end-user demos — they're the right tool. But the evals here are designed to run in Anthropic's sandbox, which doesn't allowlist the CDN hosts those fetchers use (`www.fil.ion.ucl.ac.uk`, `osf.io`, etc.). So `evals/files/make_fixtures.py` generates tiny (16×16×16) synthetic NIfTIs with known signal injected — a brain-mask sphere, six Gaussian-blob ROIs with known correlation structure, face/house patterns in a "ventral temporal" mask. These let the evals test the *workflow* (right APIs, right parameters, right outputs) without external downloads.

Each fixture has known ground truth:
- **GLM fixture**: 8 block-design events at TR=7s, signal blob on the left → contrast should give max |z| ≈ 8–10
- **Connectivity fixture**: 6 regions with r₁₂ = r₃₄ = 0.7, r₅₆ = -0.7, all others ~0 → mean correlation matrix should recover this
- **Decoding fixture**: face/house pattern in VT, 6 runs, 120 trials → SVC with leave-one-run-out should score ≈ 0.95 (chance = 0.5)

Generate fixtures:
```bash
cd evals/files && python make_fixtures.py
```

## Running the evals

The evals in `evals.json` are prompts a Claude session should be able to solve correctly given access to this skill. Each lists `expectations` — concrete behaviors that must appear in the response. To run an eval manually, set up a fresh Claude session, give it the skill, paste the prompt, supply the files, and grade against the expectations.

## Coverage

The skill covers all four core nilearn workflows:

| Workflow      | Covered scripts                           | Reference                |
|---------------|-------------------------------------------|--------------------------|
| GLM 1st-level | `run_first_level_glm.py`, `make_report.py`| `references/glm.md`      |
| GLM 2nd-level | `run_second_level_glm.py`                 | `references/glm.md`      |
| Connectivity  | `extract_connectome.py`                   | `references/connectivity.md` |
| Decoding/MVPA | `run_decoder.py`                          | `references/decoding.md` |
| Visualization | (used by all scripts)                     | `references/visualization.md` |
| Inputs        | (BIDS, raw, fetchers all handled)         | `references/datasets.md` |

Searchlight is documented in `references/decoding.md` but not wrapped as a script — it's slow and benefits from per-case parameterization.

## Known gotchas the skill warns about

- `standardize="zscore_sample"` (string) instead of deprecated `standardize=True` — removed in 0.15
- `model.generate_report()` instead of deprecated `make_glm_report()` — deprecated in 0.15
- `threshold` is display-only; use `threshold_stats_img` for statistical correction
- `t_r` must be explicit; if filtering or fitting GLMs without it, results are wrong
- `load_confounds_strategy` for fMRIPrep — never read confounds TSVs by hand
- Tangent-space connectivity needs ≥ ~3 subjects; falls back to correlation otherwise
- LeaveOneGroupOut CV in Decoder needs `groups=` passed to `.fit()` or it silently breaks
