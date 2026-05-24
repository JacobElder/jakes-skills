"""
Fixtures for Tier 1–3 gap evals (9–16).

  space_mismatch/   — bold @4mm, atlas @2mm (different affine/shape)
  glm_multicontrast/ — two-condition event-related GLM (face + house)
  regression/        — continuous labels for DecoderRegressor
  bids_dataset/      — minimal BIDS tree for first_level_from_bids
  (tangent, cluster, interactive, clusters_table reuse existing fixtures)
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import nibabel as nib


def make_affine(voxel_size, origin=(-32, -32, -32)):
    a = np.eye(4) * voxel_size
    a[3, 3] = 1
    a[:3, 3] = origin
    return a


def write_nii(data, path, voxel_size=4.0, t_r=None, origin=(-32, -32, -32)):
    affine = make_affine(voxel_size, origin)
    img = nib.Nifti1Image(data.astype(np.float32), affine)
    if t_r is not None:
        img.header.set_zooms(list(img.header.get_zooms()[:3]) + [t_r])
    nib.save(img, path)


def gaussian_blob(shape, center, sigma):
    g = np.indices(shape).astype(float)
    sq = sum((g[i] - center[i]) ** 2 for i in range(3))
    return np.exp(-sq / (2 * sigma ** 2))


def make_hrf(t_r):
    from scipy.stats import gamma
    t = np.arange(0, 32, t_r)
    hrf = gamma.pdf(t, 6) - 0.35 * gamma.pdf(t, 12)
    return hrf / hrf.max()


# ─────────────────────────────────────────────────────────────────────────────
# E9: Atlas space mismatch
#   bold:  16×16×16, 4mm voxels, origin (-32,-32,-32)
#   atlas: 32×32×32, 2mm voxels, same origin → different affine/shape
# ─────────────────────────────────────────────────────────────────────────────
def make_space_mismatch_fixture(out_dir, seed=42):
    rng = np.random.default_rng(seed)
    bold_shape = (16, 16, 16)
    n_scans = 150
    t_r = 2.0

    brain_mask = gaussian_blob(bold_shape, (8, 8, 8), 5.5) > 0.1
    blob_centers_4mm = [(4,4,8),(12,4,8),(4,12,8),(12,12,8),(8,8,4),(8,8,12)]

    cov = np.eye(6)
    cov[0,1]=cov[1,0]=0.7; cov[2,3]=cov[3,2]=0.7; cov[4,5]=cov[5,4]=-0.7
    region_ts = rng.multivariate_normal(np.zeros(6), cov, size=n_scans)

    data = rng.normal(100, 3, bold_shape + (n_scans,))
    for i, c in enumerate(blob_centers_4mm):
        blob = gaussian_blob(bold_shape, c, 1.5)
        for t in range(n_scans):
            data[..., t] += blob * region_ts[t, i] * 5
    data *= brain_mask[..., None]
    write_nii(data, out_dir / "bold.nii.gz", voxel_size=4.0, t_r=t_r)
    write_nii(brain_mask.astype(float), out_dir / "brain_mask.nii.gz", voxel_size=4.0)

    # Atlas at 2mm — 32×32×32, same origin
    atlas_shape = (32, 32, 32)
    atlas = np.zeros(atlas_shape, dtype=np.int16)
    blob_centers_2mm = [(c[0]*2, c[1]*2, c[2]*2) for c in blob_centers_4mm]
    for i, c in enumerate(blob_centers_2mm, start=1):
        blob = gaussian_blob(atlas_shape, c, 3.0)
        atlas[blob > 0.3] = i
    write_nii(atlas.astype(float), out_dir / "atlas_2mm.nii.gz", voxel_size=2.0)

    pd.DataFrame({
        "label": range(1, 7),
        "name": [f"region_{i}" for i in range(1, 7)],
    }).to_csv(out_dir / "atlas_labels.csv", index=False)

    confounds = pd.DataFrame({f"trans_{ax}": rng.normal(0, 0.2, n_scans).cumsum()
                               for ax in "xyz"})
    for ax in "xyz":
        confounds[f"rot_{ax}"] = rng.normal(0, 0.002, n_scans).cumsum()
    confounds.to_csv(out_dir / "confounds.tsv", sep="\t", index=False)

    print(f"  Space-mismatch: bold {bold_shape+(n_scans,)} @4mm, atlas {atlas_shape} @2mm")


# ─────────────────────────────────────────────────────────────────────────────
# E10: Two-condition event-related GLM (face + house)
# ─────────────────────────────────────────────────────────────────────────────
def make_multicontrast_fixture(out_dir, seed=55):
    rng = np.random.default_rng(seed)
    shape = (16, 16, 16)
    n_scans = 120
    t_r = 2.0

    brain_mask = gaussian_blob(shape, (8, 8, 8), 5.5) > 0.1
    write_nii(brain_mask.astype(float), out_dir / "brain_mask.nii.gz", voxel_size=4.0)

    hrf = make_hrf(t_r)

    trial_types = ["face"] * 20 + ["house"] * 20
    rng.shuffle(trial_types)
    onsets = np.cumsum(rng.uniform(3, 7, 40)) - rng.uniform(3, 7)
    onsets = onsets[onsets + 2 < n_scans * t_r][:40]
    trial_types = trial_types[:len(onsets)]

    events = pd.DataFrame({
        "trial_type": trial_types,
        "onset": onsets,
        "duration": [1.0] * len(onsets),
    })
    events.to_csv(out_dir / "events.tsv", sep="\t", index=False)

    face_blob  = gaussian_blob(shape, (4,  8, 8), 1.5)
    house_blob = gaussian_blob(shape, (12, 8, 8), 1.5)

    face_stim  = np.zeros(n_scans)
    house_stim = np.zeros(n_scans)
    for o, tt in zip(onsets, trial_types):
        idx = int(o / t_r)
        if idx < n_scans:
            if tt == "face":   face_stim[idx]  = 1
            else:              house_stim[idx] = 1

    face_reg  = np.convolve(face_stim,  hrf)[:n_scans]
    house_reg = np.convolve(house_stim, hrf)[:n_scans]

    data = rng.normal(100, 4, shape + (n_scans,))
    for t_idx in range(n_scans):
        data[..., t_idx] += face_blob  * face_reg[t_idx]  * 7.0
        data[..., t_idx] += house_blob * house_reg[t_idx] * 7.0
    data *= brain_mask[..., None]
    write_nii(data, out_dir / "bold.nii.gz", voxel_size=4.0, t_r=t_r)

    n_face  = sum(t == "face"  for t in trial_types)
    n_house = sum(t == "house" for t in trial_types)
    print(f"  Multi-contrast: {len(onsets)} trials ({n_face} face, {n_house} house), "
          f"face→left blob, house→right blob")


# ─────────────────────────────────────────────────────────────────────────────
# E11: DecoderRegressor — continuous stimulus orientation
# ─────────────────────────────────────────────────────────────────────────────
def make_regression_fixture(out_dir, n_runs=5, trials_per_run=18, seed=88):
    rng = np.random.default_rng(seed)
    shape = (16, 16, 16)
    n_trials = n_runs * trials_per_run
    brain_mask = gaussian_blob(shape, (8, 8, 8), 5.5) > 0.1
    v1_mask    = gaussian_blob(shape, (8, 8, 3), 2.0) > 0.3

    write_nii(brain_mask.astype(float), out_dir / "brain_mask.nii.gz", voxel_size=4.0)
    write_nii(v1_mask.astype(float),    out_dir / "v1_mask.nii.gz",    voxel_size=4.0)

    angles = []
    runs   = []
    for run in range(n_runs):
        angles.extend(rng.uniform(0, 180, trials_per_run).tolist())
        runs.extend([run] * trials_per_run)
    angles = np.array(angles)

    blob_0  = gaussian_blob(shape, (8, 8, 2), 1.2) * v1_mask
    blob_90 = gaussian_blob(shape, (8, 8, 4), 1.2) * v1_mask

    data = rng.normal(100, 4, shape + (n_trials,))
    for i, ang in enumerate(angles):
        data[..., i] += blob_0  * np.cos(2 * np.deg2rad(ang)) * 5.0
        data[..., i] += blob_90 * np.sin(2 * np.deg2rad(ang)) * 5.0
    data *= brain_mask[..., None]
    write_nii(data, out_dir / "bold.nii.gz", voxel_size=4.0, t_r=2.0)

    pd.DataFrame({"angle": angles, "chunks": runs}).to_csv(
        out_dir / "labels.csv", index=False)

    print(f"  Regression: {n_trials} trials (angle 0–180°), {n_runs} runs, V1 mask")


# ─────────────────────────────────────────────────────────────────────────────
# E14: Minimal BIDS dataset for first_level_from_bids
# ─────────────────────────────────────────────────────────────────────────────
def make_bids_fixture(out_dir, n_subjects=3, seed=77):
    rng = np.random.default_rng(seed)
    shape = (16, 16, 16)
    n_scans = 80
    t_r = 2.0
    task = "visualloc"

    brain_mask = gaussian_blob(shape, (8, 8, 8), 5.5) > 0.1
    signal_blob = gaussian_blob(shape, (4, 8, 8), 1.5)
    hrf = make_hrf(t_r)

    onsets = [10.0, 30.0, 50.0, 70.0, 90.0, 110.0, 130.0, 150.0]
    onsets = [o for o in onsets if o + 6 < n_scans * t_r]
    events = pd.DataFrame({
        "trial_type": ["active"] * len(onsets),
        "onset": onsets,
        "duration": [6.0] * len(onsets),
    })

    stim = np.zeros(n_scans)
    for o in onsets:
        stim[int(o/t_r):int(o/t_r)+3] = 1.0
    stim_conv = np.convolve(stim, hrf)[:n_scans]
    stim_conv /= stim_conv.max() + 1e-9

    # dataset_description.json (required by BIDS validator / nilearn)
    desc = {
        "Name": "SyntheticVisualLoc",
        "BIDSVersion": "1.6.0",
        "DatasetType": "raw",
    }
    (out_dir).mkdir(parents=True, exist_ok=True)
    (out_dir / "dataset_description.json").write_text(json.dumps(desc, indent=2))

    for s in range(1, n_subjects + 1):
        sub_rng = np.random.default_rng(seed + s)
        func_dir = out_dir / f"sub-{s:02d}" / "func"
        func_dir.mkdir(parents=True, exist_ok=True)

        stem = f"sub-{s:02d}_task-{task}_bold"

        # BOLD
        data = sub_rng.normal(100, 5, shape + (n_scans,))
        for t_idx in range(n_scans):
            data[..., t_idx] += signal_blob * stim_conv[t_idx] * 8.0
        data *= brain_mask[..., None]
        write_nii(data, func_dir / f"{stem}.nii.gz", voxel_size=4.0, t_r=t_r)

        # Sidecar JSON (TR required by first_level_from_bids)
        sidecar = {"RepetitionTime": t_r, "TaskName": task}
        (func_dir / f"{stem}.json").write_text(json.dumps(sidecar, indent=2))

        # Events TSV
        events.to_csv(func_dir / f"sub-{s:02d}_task-{task}_events.tsv",
                      sep="\t", index=False)

    print(f"  BIDS dataset: {n_subjects} subjects, task={task}, {n_scans} vols, TR={t_r}s")


if __name__ == "__main__":
    base = Path(__file__).parent
    for sub in ("space_mismatch", "glm_multicontrast", "regression", "bids_dataset"):
        (base / sub).mkdir(parents=True, exist_ok=True)

    print("Generating space-mismatch fixture...")
    make_space_mismatch_fixture(base / "space_mismatch")
    print("Generating multi-contrast GLM fixture...")
    make_multicontrast_fixture(base / "glm_multicontrast")
    print("Generating regression decoding fixture...")
    make_regression_fixture(base / "regression")
    print("Generating BIDS dataset fixture...")
    make_bids_fixture(base / "bids_dataset")
    print("\nDone.")
