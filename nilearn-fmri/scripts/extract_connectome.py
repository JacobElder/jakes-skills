"""
Extract a functional connectome from one or more 4D BOLD files using an atlas.

Usage examples
--------------
# Single subject with Schaefer 400 atlas
python extract_connectome.py \
    --bold sub-01_rest.nii.gz \
    --t-r 2.0 \
    --atlas schaefer_400 \
    --kind correlation \
    --out-dir results/connectome_sub01

# Multiple subjects with fMRIPrep confounds, MSDL probabilistic atlas
python extract_connectome.py \
    --bold sub-01_rest.nii.gz sub-02_rest.nii.gz sub-03_rest.nii.gz \
    --t-r 2.0 \
    --atlas msdl \
    --kind tangent \
    --fmriprep-confounds-strategy simple \
    --out-dir results/connectome

Atlas choices: schaefer_400, schaefer_100, harvard_oxford, aal, msdl, difumo_64, smith
Kind choices: correlation, partial correlation, covariance, precision, tangent
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from nilearn import datasets
from nilearn.connectome import ConnectivityMeasure
from nilearn.maskers import NiftiLabelsMasker, NiftiMapsMasker
from nilearn.plotting import (
    find_parcellation_cut_coords,
    find_probabilistic_atlas_cut_coords,
    plot_connectome,
    plot_matrix,
)


def fetch_atlas(name, atlas_labels=None, is_probabilistic=False):
    """Return (maps_img, labels, is_probabilistic).

    If `name` is a file path, load that. Otherwise treat as a named nilearn fetcher.
    """
    if Path(name).exists():
        labels = None
        if atlas_labels is not None:
            sep = "\t" if atlas_labels.endswith(".tsv") else ","
            labels_df = pd.read_csv(atlas_labels, sep=sep)
            # Look for an obvious name column
            for col in ("name", "label_name", "region", "Difumo_names"):
                if col in labels_df.columns:
                    labels = labels_df[col].tolist()
                    break
            if labels is None:
                # Fall back to the first column
                labels = labels_df.iloc[:, 0].tolist()
        return name, labels, is_probabilistic
    if name == "schaefer_400":
        atlas = datasets.fetch_atlas_schaefer_2018(n_rois=400, yeo_networks=7)
        return atlas.maps, [l.decode() if isinstance(l, bytes) else l
                             for l in atlas.labels], False
    if name == "schaefer_100":
        atlas = datasets.fetch_atlas_schaefer_2018(n_rois=100, yeo_networks=7)
        return atlas.maps, [l.decode() if isinstance(l, bytes) else l
                             for l in atlas.labels], False
    if name == "harvard_oxford":
        atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
        return atlas.maps, atlas.labels, False
    if name == "aal":
        atlas = datasets.fetch_atlas_aal()
        return atlas.maps, atlas.labels, False
    if name == "msdl":
        atlas = datasets.fetch_atlas_msdl()
        return atlas.maps, atlas.labels, True
    if name.startswith("difumo_"):
        dim = int(name.split("_")[1])
        atlas = datasets.fetch_atlas_difumo(dimension=dim, resolution_mm=2)
        labels = atlas.labels["Difumo_names"].tolist() if hasattr(atlas.labels, "columns") \
                 else list(atlas.labels)
        return atlas.maps, labels, True
    if name == "smith":
        atlas = datasets.fetch_atlas_smith_2009()
        return atlas.rsn10, [f"RSN_{i}" for i in range(10)], True
    raise ValueError(f"Unknown atlas: {name}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bold", nargs="+", required=True, help="4D BOLD path(s)")
    p.add_argument("--t-r", type=float, required=True)
    p.add_argument("--atlas", required=True,
                   help="Either a named atlas (schaefer_400, schaefer_100, harvard_oxford, "
                        "aal, msdl, difumo_64, difumo_128, smith) OR a path to a NIfTI atlas file.")
    p.add_argument("--atlas-labels", default=None,
                   help="When --atlas is a path, optional CSV/TSV with a 'name' column "
                        "(one row per region in label order).")
    p.add_argument("--atlas-probabilistic", action="store_true",
                   help="When --atlas is a path, treat it as probabilistic (4D, use NiftiMapsMasker). "
                        "Default is deterministic (3D labels, use NiftiLabelsMasker).")
    p.add_argument("--kind", default="correlation",
                   choices=["correlation", "partial correlation", "covariance",
                            "precision", "tangent"])
    p.add_argument("--low-pass", type=float, default=0.1)
    p.add_argument("--high-pass", type=float, default=0.01)
    p.add_argument("--smoothing-fwhm", type=float, default=6.0)
    p.add_argument("--confounds", nargs="*", default=None,
                   help="One confounds TSV per BOLD, in matching order.")
    p.add_argument("--fmriprep-confounds-strategy", default=None,
                   choices=["simple", "scrubbing", "compcor", "ica_aroma"])
    p.add_argument("--out-dir", required=True)
    args = p.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    if args.kind == "tangent" and len(args.bold) < 3:
        print("WARNING: tangent space requires multiple subjects; falling back to correlation.")
        args.kind = "correlation"

    # Fetch atlas
    print(f"Loading atlas: {args.atlas}")
    maps_img, labels, is_prob = fetch_atlas(
        args.atlas, atlas_labels=args.atlas_labels,
        is_probabilistic=args.atlas_probabilistic,
    )
    n_regions = len(labels) if labels is not None else None
    print(f"Atlas has {n_regions} regions ({'probabilistic' if is_prob else 'deterministic'})")

    # Build masker
    masker_kwargs = dict(
        standardize="zscore_sample",
        detrend=True,
        low_pass=args.low_pass,
        high_pass=args.high_pass,
        smoothing_fwhm=args.smoothing_fwhm if args.smoothing_fwhm > 0 else None,
        t_r=args.t_r,
        verbose=0,
    )
    if is_prob:
        masker = NiftiMapsMasker(maps_img=maps_img, **masker_kwargs)
    else:
        masker = NiftiLabelsMasker(labels_img=maps_img, labels=labels, **masker_kwargs)

    # Extract timeseries
    all_ts = []
    for i, bold_path in enumerate(args.bold):
        print(f"[{i+1}/{len(args.bold)}] Extracting from {Path(bold_path).name}")
        conf = None
        sample_mask = None
        if args.fmriprep_confounds_strategy:
            from nilearn.interfaces.fmriprep import load_confounds_strategy
            conf, sample_mask = load_confounds_strategy(
                bold_path, denoise_strategy=args.fmriprep_confounds_strategy
            )
        elif args.confounds is not None:
            cp = args.confounds[i]
            sep = "\t" if cp.endswith(".tsv") else ","
            conf = pd.read_csv(cp, sep=sep)
        ts = masker.fit_transform(bold_path, confounds=conf, sample_mask=sample_mask)
        all_ts.append(ts)
        np.save(out / f"timeseries_sub{i:02d}.npy", ts)
        print(f"  shape: {ts.shape}")

    # Connectivity
    print(f"\nComputing connectivity ({args.kind})...")
    measure = ConnectivityMeasure(kind=args.kind)
    matrices = measure.fit_transform(all_ts)
    np.save(out / "connectivity_matrices.npy", matrices)
    print(f"Matrices shape: {matrices.shape}")

    # Mean matrix for visualization
    mean_matrix = matrices.mean(axis=0)
    np.fill_diagonal(mean_matrix, 0)
    np.save(out / "mean_connectivity_matrix.npy", mean_matrix)

    # Plot matrix
    if n_regions is not None and n_regions <= 50:
        plot_labels = labels
        figsize = (10, 10)
    else:
        plot_labels = None  # too many labels to display
        figsize = (12, 12)
    plot_matrix(mean_matrix, labels=plot_labels, vmax=0.8, vmin=-0.8,
                 reorder=True, figure=figsize)
    import matplotlib.pyplot as plt
    plt.savefig(out / "matrix.png", dpi=120, bbox_inches="tight")
    plt.close()

    # Plot connectome on glass brain
    print("Plotting connectome on glass brain...")
    if is_prob:
        coords = find_probabilistic_atlas_cut_coords(maps_img)
    else:
        coords = find_parcellation_cut_coords(maps_img)
    plot_connectome(mean_matrix, coords, edge_threshold="95%",
                     colorbar=True, node_size=20,
                     title=f"Group-mean connectome ({args.kind})",
                     output_file=str(out / "connectome_glass.png"))

    # Interactive HTML view
    from nilearn import plotting as nplotting
    view = nplotting.view_connectome(mean_matrix, coords, edge_threshold="95%")
    view.save_as_html(out / "connectome_interactive.html")

    # Save labels for reference
    if labels is not None:
        pd.Series(labels, name="region").to_csv(out / "region_labels.csv", index_label="index")

    print(f"\nDone. Outputs in: {out.resolve()}")


if __name__ == "__main__":
    main()
