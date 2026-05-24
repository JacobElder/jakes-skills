"""
Run a nilearn Decoder (classification or regression) with cross-validation.

Usage examples
--------------
# Haxby face vs house demo (classification)
python run_decoder.py \
    --fmri bold.nii.gz \
    --labels labels.csv \
    --label-col labels \
    --groups-col chunks \
    --mask vt_mask.nii.gz \
    --restrict face house \
    --estimator svc \
    --cv leave_one_group_out \
    --out-dir results/decoder

# Whole-brain logistic with k-fold
python run_decoder.py \
    --fmri bold.nii.gz \
    --labels labels.csv \
    --label-col labels \
    --estimator logistic \
    --cv kfold:5 \
    --screening-percentile 5 \
    --out-dir results/decoder

# Regression (predict continuous values)
python run_decoder.py \
    --fmri bold.nii.gz \
    --labels labels.csv \
    --label-col rt \
    --task regression \
    --estimator ridge \
    --out-dir results/decoder
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from nilearn.decoding import Decoder, DecoderRegressor
from nilearn.image import index_img
from nilearn.plotting import plot_stat_map


def make_cv(spec, groups):
    """Parse a CV spec like 'kfold:5' or 'leave_one_group_out'."""
    if spec == "leave_one_group_out":
        if groups is None:
            raise ValueError("leave_one_group_out needs --groups-col")
        from sklearn.model_selection import LeaveOneGroupOut
        return LeaveOneGroupOut()
    if spec.startswith("kfold:"):
        from sklearn.model_selection import StratifiedKFold
        k = int(spec.split(":")[1])
        return StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
    if spec.startswith("group_kfold:"):
        from sklearn.model_selection import GroupKFold
        k = int(spec.split(":")[1])
        return GroupKFold(n_splits=k)
    raise ValueError(f"Unknown cv spec: {spec}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fmri", required=True,
                   help="4D NIfTI where each volume = one sample (trial or beta map)")
    p.add_argument("--labels", required=True,
                   help="CSV/TSV with one row per volume; must have --label-col")
    p.add_argument("--label-col", required=True, help="Column with the target label/value")
    p.add_argument("--groups-col", default=None,
                   help="Column with grouping variable (e.g. run number for LOGO)")
    p.add_argument("--task", choices=["classification", "regression"],
                   default="classification")
    p.add_argument("--mask", default=None, help="Brain or ROI mask NIfTI")
    p.add_argument("--restrict", nargs="+", default=None,
                   help="Keep only samples whose label is in this list "
                        "(classification only)")
    p.add_argument("--estimator", default="svc",
                   help="Classifier: svc, svc_l1, logistic, logistic_l1, "
                        "ridge_classifier, dummy_classifier. "
                        "Regressor: ridge, svr, lasso, dummy_regressor.")
    p.add_argument("--cv", default="kfold:5",
                   help="CV spec: 'kfold:5', 'group_kfold:5', 'leave_one_group_out'")
    p.add_argument("--scoring", default=None,
                   help="Default: accuracy (class) / r2 (regression)")
    p.add_argument("--screening-percentile", type=float, default=20)
    p.add_argument("--smoothing-fwhm", type=float, default=4.0)
    p.add_argument("--n-jobs", type=int, default=1)
    p.add_argument("--out-dir", required=True)
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Labels
    sep = "\t" if args.labels.endswith(".tsv") else (
        " " if args.labels.endswith(".txt") else ",")
    # Try multiple seps
    try:
        labels_df = pd.read_csv(args.labels, sep=sep)
    except Exception:
        labels_df = pd.read_csv(args.labels, sep=None, engine="python")
    if args.label_col not in labels_df.columns:
        raise ValueError(f"--label-col '{args.label_col}' not in {list(labels_df.columns)}")

    y = labels_df[args.label_col]
    groups = labels_df[args.groups_col].values if args.groups_col else None

    # Restrict
    if args.restrict:
        mask = y.isin(args.restrict)
        keep_idx = np.where(mask.values)[0]
        print(f"Restricting to {args.restrict}: {len(keep_idx)} / {len(y)} samples")
        fmri = index_img(args.fmri, keep_idx)
        y = y[mask].values
        if groups is not None:
            groups = groups[mask.values]
    else:
        fmri = args.fmri
        y = y.values

    # CV
    cv = make_cv(args.cv, groups)

    # Fit
    common = dict(
        estimator=args.estimator,
        mask=args.mask,
        cv=cv,
        screening_percentile=args.screening_percentile,
        smoothing_fwhm=args.smoothing_fwhm,
        standardize="zscore_sample",
        n_jobs=args.n_jobs,
        verbose=1,
    )
    if args.task == "classification":
        common["scoring"] = args.scoring or "accuracy"
        decoder = Decoder(**common)
    else:
        common["scoring"] = args.scoring or "r2"
        decoder = DecoderRegressor(**common)

    print(f"Fitting {args.task} Decoder (estimator={args.estimator}, cv={args.cv})...")
    fit_kwargs = {"y": y}
    if groups is not None:
        fit_kwargs["groups"] = groups
    decoder.fit(fmri, **fit_kwargs)

    # Scores
    results = {}
    for label, scores in decoder.cv_scores_.items():
        mean = float(np.mean(scores))
        std = float(np.std(scores))
        results[str(label)] = {
            "mean": mean,
            "std": std,
            "scores": [float(s) for s in scores],
        }
        print(f"  {label}: {mean:.3f} ± {std:.3f}")

    # Chance level (classification only)
    if args.task == "classification":
        unique_y = np.unique(y)
        chance = 1.0 / len(unique_y)
        results["_chance_level"] = chance
        print(f"  chance level: {chance:.3f}")

    with open(out / "cv_scores.json", "w") as f:
        json.dump(results, f, indent=2)

    # Weight maps
    for class_label, weight_img in decoder.coef_img_.items():
        safe = str(class_label).replace("/", "_")
        weight_img.to_filename(out / f"weights_{safe}.nii.gz")
        plot_stat_map(weight_img, threshold=1e-4,
                       title=f"Decoder weights: {class_label}",
                       output_file=str(out / f"weights_{safe}.png"))

    # Summary text
    with open(out / "summary.txt", "w") as f:
        f.write(f"Task: {args.task}\n")
        f.write(f"Estimator: {args.estimator}\n")
        f.write(f"CV: {args.cv}\n")
        f.write(f"Screening percentile: {args.screening_percentile}\n")
        f.write(f"N samples: {len(y)}\n")
        if args.task == "classification":
            f.write(f"Classes: {sorted(np.unique(y).tolist())}\n")
            f.write(f"Chance level: {chance:.3f}\n")
        f.write("\nPer-class/overall results:\n")
        for k, v in results.items():
            if k == "_chance_level":
                continue
            f.write(f"  {k}: {v['mean']:.3f} ± {v['std']:.3f}\n")

    print(f"\nDone. Outputs in: {out.resolve()}")


if __name__ == "__main__":
    main()
