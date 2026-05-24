"""
Generate additional synthetic fixtures for evals 4-8.

New outputs:
  - second_level/sub-{01..08}_zmap.nii.gz   (8 first-level z-maps for group GLM)
  - multirun/run-01_bold.nii.gz              (two short block-design runs)
  - multirun/run-02_bold.nii.gz
  - multirun/run-01_events.tsv
  - multirun/run-02_events.tsv
  - multirun/brain_mask.nii.gz
"""

from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib


def make_affine(voxel_size=4.0):
    affine = np.eye(4) * voxel_size
    affine[3, 3] = 1
    affine[:3, 3] = [-32, -32, -32]
    return affine


def write_nii(data, path, voxel_size=4.0, t_r=None):
    affine = make_affine(voxel_size)
    img = nib.Nifti1Image(data.astype(np.float32), affine)
    if t_r is not None:
        img.header.set_zooms(list(img.header.get_zooms()[:3]) + [t_r])
    nib.save(img, path)


def gaussian_blob(shape, center, sigma):
    grids = np.indices(shape).astype(float)
    sq_dist = sum((grids[i] - center[i]) ** 2 for i in range(3))
    return np.exp(-sq_dist / (2 * sigma ** 2))


# ─────────────────────────────────────────────────────────────────────────────
# Second-level fixture: 8 first-level z-maps with group-level signal
# ─────────────────────────────────────────────────────────────────────────────
def make_second_level_fixture(out_dir, n_subjects=8, seed=99):
    shape = (16, 16, 16)
    signal_blob = gaussian_blob(shape, (4, 8, 8), 2.0)

    for s in range(n_subjects):
        rng = np.random.default_rng(seed + s)
        # z-map: ~N(0,1) noise everywhere, signal blob at z≈3-5
        zmap = rng.normal(0, 1, shape)
        # Inject consistent activation — subjects vary in magnitude
        amplitude = rng.uniform(2.5, 5.0)
        zmap += signal_blob * amplitude
        write_nii(zmap, out_dir / f"sub-{s+1:02d}_zmap.nii.gz")

    # Brain mask used for masking
    brain_mask = gaussian_blob(shape, (8, 8, 8), 5.5) > 0.1
    write_nii(brain_mask.astype(float), out_dir / "brain_mask.nii.gz")

    print(f"  Second-level fixture: {n_subjects} z-maps, signal at left blob")


# ─────────────────────────────────────────────────────────────────────────────
# Multi-run fixture: 2 short runs (48 scans each) of the same block design
# ─────────────────────────────────────────────────────────────────────────────
def make_multirun_fixture(out_dir, seed=77):
    rng = np.random.default_rng(seed)
    shape = (16, 16, 16)
    n_scans = 48
    t_r = 7.0

    brain_mask = gaussian_blob(shape, (8, 8, 8), 5.5) > 0.1
    write_nii(brain_mask.astype(float), out_dir / "brain_mask.nii.gz")

    from scipy.stats import gamma
    t = np.arange(0, 32, t_r)
    hrf = gamma.pdf(t, 6) - 0.35 * gamma.pdf(t, 12)
    hrf = hrf / hrf.max()

    # Same block pattern for both runs: 2 on-blocks in 48 scans
    onsets = [6 * t_r, 30 * t_r]
    events = pd.DataFrame({
        "trial_type": ["active", "active"],
        "onset": onsets,
        "duration": [6 * t_r, 6 * t_r],
    })

    signal_blob = gaussian_blob(shape, (4, 8, 8), 1.5)

    for run_idx in range(2):
        run_rng = np.random.default_rng(seed + run_idx * 100)
        stim = np.zeros(n_scans)
        for o in onsets:
            start = int(o / t_r)
            stim[start:start + 6] = 1.0
        stim_conv = np.convolve(stim, hrf)[:n_scans]
        stim_conv = stim_conv / stim_conv.max()

        data = run_rng.normal(100, 5, shape + (n_scans,))
        for t_idx in range(n_scans):
            data[..., t_idx] += signal_blob * stim_conv[t_idx] * 8.0
        data = data * brain_mask[..., None]

        run_label = f"run-{run_idx + 1:02d}"
        write_nii(data, out_dir / f"{run_label}_bold.nii.gz", t_r=t_r)
        events.to_csv(out_dir / f"{run_label}_events.tsv", sep="\t", index=False)

    print(f"  Multi-run fixture: 2 runs × {n_scans} scans, t_r={t_r}, same block design")


if __name__ == "__main__":
    base = Path(__file__).parent

    print("Generating second-level fixture...")
    make_second_level_fixture(base / "second_level")

    print("Generating multi-run fixture...")
    make_multirun_fixture(base / "multirun")

    print("\nDone.")
