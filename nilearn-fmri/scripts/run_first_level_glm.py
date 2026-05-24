"""
Run a first-level GLM for a single subject.

Usage examples
--------------
# With explicit args
python run_first_level_glm.py \
    --bold sub-01_bold.nii.gz \
    --events events.tsv \
    --t-r 2.0 \
    --contrasts "face - house" "face" "house" \
    --out-dir results/sub-01

# With confounds (e.g. fMRIPrep output)
python run_first_level_glm.py \
    --bold sub-01_desc-preproc_bold.nii.gz \
    --events events.tsv \
    --t-r 2.0 \
    --fmriprep-confounds-strategy simple \
    --contrasts "face - house" \
    --out-dir results/sub-01

This script saves: design_matrix.png, one z-map .nii.gz per contrast,
one glass-brain .png per contrast, and an HTML report.
"""

import argparse
from pathlib import Path

import pandas as pd
from nilearn.glm.first_level import FirstLevelModel
from nilearn.plotting import plot_design_matrix, plot_glass_brain


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bold", required=True, help="4D BOLD NIfTI path")
    p.add_argument("--events", required=True,
                   help="Events TSV/CSV with onset, duration, trial_type")
    p.add_argument("--t-r", type=float, required=True, help="Repetition time (s)")
    p.add_argument("--contrasts", nargs="+", required=True,
                   help="Contrast expressions, e.g. 'face - house' 'face'")
    p.add_argument("--out-dir", required=True, help="Where to save outputs")
    p.add_argument("--hrf-model", default="glover + derivative",
                   help="HRF model (default: glover + derivative)")
    p.add_argument("--high-pass", type=float, default=1/128,
                   help="High-pass cutoff in Hz (default: ~0.008)")
    p.add_argument("--smoothing-fwhm", type=float, default=5.0,
                   help="Smoothing FWHM in mm (default: 5; set 0 if already smoothed)")
    p.add_argument("--drift-model", default="cosine")
    p.add_argument("--confounds", default=None,
                   help="Path to a confounds TSV/CSV (one row per volume)")
    p.add_argument("--fmriprep-confounds-strategy", default=None,
                   choices=["simple", "scrubbing", "compcor", "ica_aroma"],
                   help="If set, use load_confounds_strategy on the BOLD path "
                        "to get fMRIPrep confounds.")
    p.add_argument("--threshold", type=float, default=3.1,
                   help="Display z threshold (default: 3.1, ~p<.001 uncorr)")
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load events
    sep = "\t" if args.events.endswith(".tsv") else ","
    events = pd.read_csv(args.events, sep=sep)
    required = {"onset", "duration", "trial_type"}
    if not required.issubset(events.columns):
        raise ValueError(f"Events file must have columns {required}, "
                         f"got {set(events.columns)}")

    # Load confounds
    confounds = None
    sample_mask = None
    if args.fmriprep_confounds_strategy is not None:
        from nilearn.interfaces.fmriprep import load_confounds_strategy
        confounds, sample_mask = load_confounds_strategy(
            args.bold, denoise_strategy=args.fmriprep_confounds_strategy
        )
        print(f"Loaded {confounds.shape[1]} fMRIPrep confounds; "
              f"sample_mask: {'set' if sample_mask is not None else 'none'}")
    elif args.confounds is not None:
        sep = "\t" if args.confounds.endswith(".tsv") else ","
        confounds = pd.read_csv(args.confounds, sep=sep)

    # Fit model
    print(f"Fitting FirstLevelModel (t_r={args.t_r}, hrf={args.hrf_model})...")
    model = FirstLevelModel(
        t_r=args.t_r,
        hrf_model=args.hrf_model,
        drift_model=args.drift_model,
        high_pass=args.high_pass,
        smoothing_fwhm=args.smoothing_fwhm if args.smoothing_fwhm > 0 else None,
        standardize=False,
        noise_model="ar1",
        minimize_memory=True,
    )
    fit_kwargs = {"events": events}
    if confounds is not None:
        fit_kwargs["confounds"] = confounds
    if sample_mask is not None:
        fit_kwargs["sample_masks"] = sample_mask
    model.fit(args.bold, **fit_kwargs)

    # Save design matrix
    dm = model.design_matrices_[0]
    plot_design_matrix(dm, output_file=str(out / "design_matrix.png"))
    dm.to_csv(out / "design_matrix.csv")
    print(f"Design matrix: {dm.shape[0]} volumes × {dm.shape[1]} regressors")
    print(f"Regressors: {list(dm.columns)}")

    # Compute each contrast
    contrast_dict = {}
    for c in args.contrasts:
        print(f"Contrast: {c}")
        z_map = model.compute_contrast(c, output_type="z_score")
        safe = c.replace(" ", "").replace("-", "_minus_").replace("+", "_plus_")\
                .replace("(", "").replace(")", "").replace("/", "_over_")
        z_path = out / f"z_{safe}.nii.gz"
        z_map.to_filename(z_path)
        plot_glass_brain(z_map, threshold=args.threshold, plot_abs=False,
                          colorbar=True, title=c,
                          output_file=str(out / f"glass_{safe}.png"))
        contrast_dict[c] = c

    # HTML report (use model.generate_report; make_glm_report deprecated in 0.15)
    # When height_control != None, the report ignores `threshold` and uses alpha-derived one.
    report = model.generate_report(
        contrasts=contrast_dict,
        threshold=args.threshold,
        height_control=None,        # use the explicit threshold
        cluster_threshold=10,
    )
    report.save_as_html(out / "report.html")
    print(f"\nDone. Outputs in: {out.resolve()}")


if __name__ == "__main__":
    main()
