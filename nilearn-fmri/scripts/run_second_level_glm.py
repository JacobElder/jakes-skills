"""
Run a second-level (group) GLM from a list of per-subject contrast maps.

Usage examples
--------------
# One-sample t-test (group mean)
python run_second_level_glm.py \
    --maps subj1_contrast.nii.gz subj2_contrast.nii.gz subj3_contrast.nii.gz \
    --design one_sample \
    --out-dir results/group

# Two-sample t-test (group A vs group B)
python run_second_level_glm.py \
    --maps "patient*_contrast.nii.gz" "control*_contrast.nii.gz" \
    --design two_sample \
    --group-labels patient patient patient control control control \
    --out-dir results/group

# With covariates (CSV with one column per regressor, one row per subject)
python run_second_level_glm.py \
    --maps subj*_contrast.nii.gz \
    --design-csv group_design.csv \
    --contrast "intercept" \
    --out-dir results/group
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img
from nilearn.plotting import plot_glass_brain, plot_stat_map
from nilearn.reporting import get_clusters_table


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--maps", nargs="+", required=True,
                   help="Per-subject contrast map paths (effect-size or z-score)")
    p.add_argument("--design", choices=["one_sample", "two_sample"], default=None,
                   help="Quick design preset. Mutually exclusive with --design-csv.")
    p.add_argument("--design-csv", default=None,
                   help="CSV file: one row per subject, columns = regressors.")
    p.add_argument("--group-labels", nargs="+", default=None,
                   help="For --design two_sample: one label per subject, e.g. "
                        "'patient patient control control'.")
    p.add_argument("--contrast", default=None,
                   help="Contrast expression or column name. "
                        "Defaults to 'intercept' for one_sample, 'g1 - g2' for two_sample.")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--alpha", type=float, default=0.05,
                   help="Significance level for FDR/Bonferroni (default 0.05)")
    p.add_argument("--height-control", default="fdr",
                   choices=["fpr", "fdr", "bonferroni"])
    p.add_argument("--cluster-threshold", type=int, default=10,
                   help="Minimum cluster size (voxels)")
    p.add_argument("--display-threshold", type=float, default=3.1)
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    n = len(args.maps)
    print(f"Group analysis on {n} subjects")

    # Build design matrix
    if args.design_csv:
        design = pd.read_csv(args.design_csv)
        if len(design) != n:
            raise ValueError(f"Design CSV has {len(design)} rows but {n} maps")
        if args.contrast is None:
            args.contrast = design.columns[0]
    elif args.design == "one_sample":
        design = pd.DataFrame({"intercept": [1] * n})
        if args.contrast is None:
            args.contrast = "intercept"
    elif args.design == "two_sample":
        if args.group_labels is None or len(args.group_labels) != n:
            raise ValueError("--group-labels must list one label per subject")
        labels = args.group_labels
        unique = sorted(set(labels))
        if len(unique) != 2:
            raise ValueError(f"Two-sample design needs exactly 2 groups, got {unique}")
        g1, g2 = unique
        design = pd.DataFrame({
            g1: [1 if l == g1 else 0 for l in labels],
            g2: [1 if l == g2 else 0 for l in labels],
        })
        if args.contrast is None:
            args.contrast = f"{g1} - {g2}"
    else:
        raise ValueError("Specify either --design or --design-csv")

    print("Design matrix:")
    print(design)
    design.to_csv(out / "group_design.csv", index=False)

    # Fit
    model = SecondLevelModel()
    model.fit(list(args.maps), design_matrix=design)

    # Contrast
    print(f"Contrast: {args.contrast}")
    z_map = model.compute_contrast(args.contrast, output_type="z_score")
    z_map.to_filename(out / "group_z_map.nii.gz")

    # Uncorrected plot
    plot_glass_brain(z_map, threshold=args.display_threshold, plot_abs=False,
                      colorbar=True, title=f"Group: {args.contrast} (z>{args.display_threshold})",
                      output_file=str(out / "glass_uncorrected.png"))

    # Corrected
    thresholded, threshold = threshold_stats_img(
        z_map,
        alpha=args.alpha,
        height_control=args.height_control,
        cluster_threshold=args.cluster_threshold,
        two_sided=True,
    )
    print(f"{args.height_control.upper()} threshold at alpha={args.alpha}: z = {threshold:.2f}")
    thresholded.to_filename(out / f"group_z_thresh_{args.height_control}.nii.gz")
    plot_glass_brain(thresholded, threshold=threshold, plot_abs=False,
                      colorbar=True,
                      title=f"Group {args.contrast} ({args.height_control} p<{args.alpha})",
                      output_file=str(out / f"glass_{args.height_control}.png"))
    plot_stat_map(thresholded, threshold=threshold, display_mode="ortho",
                   title=f"Group {args.contrast} ({args.height_control})",
                   output_file=str(out / f"stat_{args.height_control}.png"))

    # Clusters table
    table = get_clusters_table(thresholded, stat_threshold=threshold,
                                cluster_threshold=args.cluster_threshold,
                                two_sided=True)
    table.to_csv(out / "clusters.csv", index=False)
    print("\nClusters:")
    print(table)

    # Report (using model.generate_report)
    report = model.generate_report(
        contrasts={args.contrast: args.contrast},
        height_control=args.height_control,
        alpha=args.alpha,
        cluster_threshold=args.cluster_threshold,
    )
    report.save_as_html(out / "group_report.html")
    print(f"\nDone. Outputs in: {out.resolve()}")


if __name__ == "__main__":
    main()
