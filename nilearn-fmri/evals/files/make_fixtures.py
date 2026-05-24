"""
Generate small synthetic neuroimaging fixtures for skill evals.

These are NOT realistic brain data — they're tiny (16×16×16) volumes with
known signal injected at known locations so that:
  - GLM analyses produce non-trivial z-maps
  - Connectivity matrices have detectable structure
  - Decoders score above chance

The goal is to test the SKILL workflow (right APIs, right argument names,
right output files), not the science.

Outputs (written next to this script in evals/files/):
  - glm/bold.nii.gz, glm/events.tsv, glm/anat.nii.gz
  - connectivity/sub-01_bold.nii.gz ... sub-03_bold.nii.gz, atlas.nii.gz, atlas_labels.csv
  - decoding/bold.nii.gz, decoding/labels.csv, decoding/mask.nii.gz
"""

from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib


def make_affine(voxel_size=4.0):
    """Standard affine with given isotropic voxel size, MNI-ish origin."""
    affine = np.eye(4) * voxel_size
    affine[3, 3] = 1
    affine[:3, 3] = [-32, -32, -32]  # center origin
    return affine


def write_nii(data, path, voxel_size=4.0, t_r=None):
    affine = make_affine(voxel_size)
    img = nib.Nifti1Image(data.astype(np.float32), affine)
    if t_r is not None:
        img.header.set_zooms(list(img.header.get_zooms()[:3]) + [t_r])
    nib.save(img, path)


def gaussian_blob(shape, center, sigma):
    """A 3D Gaussian centered at `center` with std `sigma`."""
    grids = np.indices(shape).astype(float)
    sq_dist = sum((grids[i] - center[i]) ** 2 for i in range(3))
    return np.exp(-sq_dist / (2 * sigma ** 2))


# ─────────────────────────────────────────────────────────────────────────────
# GLM fixture: a block-design "auditory" task on a 16×16×16 brain
# ─────────────────────────────────────────────────────────────────────────────
def make_glm_fixture(out_dir, seed=42):
    rng = np.random.default_rng(seed)
    shape = (16, 16, 16)
    n_scans = 96
    t_r = 7.0

    # Build a brain mask (sphere of radius 7 voxels)
    brain_mask = gaussian_blob(shape, (8, 8, 8), 5.5) > 0.1

    # Anatomical: just the brain mask scaled to T1-ish values
    anat = brain_mask.astype(float) * 1000 + rng.normal(0, 30, shape)
    write_nii(anat, out_dir / "anat.nii.gz", voxel_size=4.0)

    # Events: 8 blocks, 6 scans long, every 12 scans starting at scan 6
    onsets = [6 * t_r + i * 12 * t_r for i in range(8)]
    events = pd.DataFrame({
        "trial_type": ["active"] * 8,
        "onset": onsets,
        "duration": [6 * t_r] * 8,
    })
    events.to_csv(out_dir / "events.tsv", sep="\t", index=False)

    # Block stimulus regressor (boxcar)
    stim = np.zeros(n_scans)
    for o in onsets:
        start = int(o / t_r)
        stim[start:start + 6] = 1.0

    # Convolve with a simple double-gamma HRF
    from scipy.stats import gamma
    t = np.arange(0, 32, t_r)
    hrf = gamma.pdf(t, 6) - 0.35 * gamma.pdf(t, 12)
    hrf = hrf / hrf.max()
    stim_conv = np.convolve(stim, hrf)[:n_scans]
    stim_conv = stim_conv / stim_conv.max()

    # Build 4D data: baseline + noise + signal at one region (left "auditory cortex")
    data = rng.normal(100, 5, shape + (n_scans,))  # baseline + thermal noise
    # Inject signal: a Gaussian blob on the left side
    signal_blob = gaussian_blob(shape, (4, 8, 8), 1.5)  # left-lateral blob
    for t_idx in range(n_scans):
        data[..., t_idx] += signal_blob * stim_conv[t_idx] * 8.0  # ~8% signal change
    # Mask data to brain
    data = data * brain_mask[..., None]
    write_nii(data, out_dir / "bold.nii.gz", voxel_size=4.0, t_r=t_r)

    # Brain mask file
    write_nii(brain_mask.astype(float), out_dir / "brain_mask.nii.gz", voxel_size=4.0)

    print(f"  GLM fixture: bold {data.shape}, t_r={t_r}, "
          f"{len(events)} events, signal at left blob")


# ─────────────────────────────────────────────────────────────────────────────
# Connectivity fixture: 3 subjects of resting-state data with known structure
# ─────────────────────────────────────────────────────────────────────────────
def make_connectivity_fixture(out_dir, n_subjects=3, seed=42):
    rng = np.random.default_rng(seed)
    shape = (16, 16, 16)
    n_scans = 150
    t_r = 2.0

    brain_mask = gaussian_blob(shape, (8, 8, 8), 5.5) > 0.1

    # Build a 6-region atlas — 6 Gaussian blobs at known coords
    blob_centers = [
        (4, 4, 8),    # region 1
        (12, 4, 8),   # region 2
        (4, 12, 8),   # region 3
        (12, 12, 8),  # region 4
        (8, 8, 4),    # region 5
        (8, 8, 12),   # region 6
    ]
    atlas = np.zeros(shape, dtype=np.int16)
    for i, c in enumerate(blob_centers, start=1):
        blob = gaussian_blob(shape, c, 1.5)
        atlas[blob > 0.3] = i
    write_nii(atlas.astype(np.float32), out_dir / "atlas.nii.gz", voxel_size=4.0)
    pd.DataFrame({
        "label": list(range(1, 7)),
        "name": [f"region_{i}" for i in range(1, 7)],
    }).to_csv(out_dir / "atlas_labels.csv", index=False)

    # Per-subject BOLD with known connectivity: regions 1+2 correlated,
    # regions 3+4 correlated, region 5 anticorrelated with region 6.
    for s in range(n_subjects):
        # Generate 6 timeseries with a known covariance
        cov = np.eye(6)
        cov[0, 1] = cov[1, 0] = 0.7    # region 1 ↔ 2
        cov[2, 3] = cov[3, 2] = 0.7    # region 3 ↔ 4
        cov[4, 5] = cov[5, 4] = -0.7   # region 5 ↔ 6 anticorrelated
        # Ensure positive-semi-definite
        eigs = np.linalg.eigvalsh(cov)
        if eigs.min() < 0:
            cov += np.eye(6) * (abs(eigs.min()) + 0.1)
        sub_rng = np.random.default_rng(seed + s)
        region_ts = sub_rng.multivariate_normal(np.zeros(6), cov, size=n_scans)

        # Build 4D data: project region timeseries onto blobs
        data = sub_rng.normal(100, 3, shape + (n_scans,))
        for i, c in enumerate(blob_centers):
            blob = gaussian_blob(shape, c, 1.5)
            for t_idx in range(n_scans):
                data[..., t_idx] += blob * region_ts[t_idx, i] * 5
        data = data * brain_mask[..., None]

        write_nii(data, out_dir / f"sub-{s+1:02d}_bold.nii.gz",
                  voxel_size=4.0, t_r=t_r)

        # Synthetic confounds (motion-like)
        confounds = pd.DataFrame({
            f"trans_{ax}": sub_rng.normal(0, 0.2, n_scans).cumsum()
            for ax in "xyz"
        })
        for ax in "xyz":
            confounds[f"rot_{ax}"] = sub_rng.normal(0, 0.002, n_scans).cumsum()
        confounds.to_csv(out_dir / f"sub-{s+1:02d}_confounds.tsv",
                          sep="\t", index=False)

    print(f"  Connectivity fixture: {n_subjects} subjects, "
          f"6-region atlas, known structure (1↔2, 3↔4, 5↔-6)")


# ─────────────────────────────────────────────────────────────────────────────
# Decoding fixture: face vs house in a tiny "ventral temporal" ROI
# ─────────────────────────────────────────────────────────────────────────────
def make_decoding_fixture(out_dir, n_runs=6, trials_per_run=20, seed=42):
    rng = np.random.default_rng(seed)
    shape = (16, 16, 16)
    n_scans = n_runs * trials_per_run   # one volume = one trial (beta map style)
    brain_mask = gaussian_blob(shape, (8, 8, 8), 5.5) > 0.1

    # VT mask: a smaller region (right ventral)
    vt_mask = gaussian_blob(shape, (11, 5, 5), 1.8) > 0.3
    write_nii(brain_mask.astype(float), out_dir / "brain_mask.nii.gz", voxel_size=4.0)
    write_nii(vt_mask.astype(float), out_dir / "vt_mask.nii.gz", voxel_size=4.0)

    # Generate trial labels: alternate face/house within each run, with some randomness
    labels = []
    runs = []
    for run in range(n_runs):
        run_labels = ["face"] * (trials_per_run // 2) + ["house"] * (trials_per_run // 2)
        rng.shuffle(run_labels)
        labels.extend(run_labels)
        runs.extend([run] * trials_per_run)

    # Build 4D: each "volume" is a trial. Faces activate a sub-region; houses another.
    # Within VT, faces light up the upper-half voxels, houses the lower-half.
    face_pattern = gaussian_blob(shape, (11, 5, 6), 1.0) * vt_mask
    house_pattern = gaussian_blob(shape, (11, 5, 4), 1.0) * vt_mask

    data = rng.normal(100, 4, shape + (n_scans,))
    for i, label in enumerate(labels):
        pattern = face_pattern if label == "face" else house_pattern
        data[..., i] += pattern * 6.0   # signal magnitude
    data = data * brain_mask[..., None]

    write_nii(data, out_dir / "bold.nii.gz", voxel_size=4.0, t_r=2.0)

    pd.DataFrame({
        "labels": labels,
        "chunks": runs,
    }).to_csv(out_dir / "labels.csv", index=False)

    print(f"  Decoding fixture: {n_scans} trials across {n_runs} runs, "
          f"face vs house, VT mask")


if __name__ == "__main__":
    base = Path(__file__).parent
    for sub in ("glm", "connectivity", "decoding"):
        (base / sub).mkdir(parents=True, exist_ok=True)

    print("Generating GLM fixture...")
    make_glm_fixture(base / "glm")
    print("Generating connectivity fixture...")
    make_connectivity_fixture(base / "connectivity")
    print("Generating decoding fixture...")
    make_decoding_fixture(base / "decoding")
    print("\nDone.")
