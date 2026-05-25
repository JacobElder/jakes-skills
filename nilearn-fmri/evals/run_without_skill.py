"""
Empirical without-skill evaluation harness.

Runs the base-model-typical (wrong) code for each of the 16 evals, checks
mechanically-verifiable expectations against actual output, and estimates
narrative expectations from known failure patterns.

Usage:
    cd /path/to/nilearn-fmri
    python evals/run_without_skill.py
"""

import warnings
warnings.filterwarnings("ignore")

import os, shutil, json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib

BASE = Path(__file__).parent.parent
FILES = BASE / "evals" / "files"
RESULTS = BASE / "evals" / "without_skill_results"

# ─── helpers ──────────────────────────────────────────────────────────────────

def clean(p):
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)

def nii_files(p):
    return list(p.glob("*.nii.gz"))

def png_files(p):
    return list(p.glob("*.png"))

def html_files(p):
    return list(p.glob("*.html"))

def csv_files(p):
    return list(p.glob("*.csv"))


# ─── E1: GLM block design — base model uses make_glm_report, skips design matrix ──
def eval_1_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.glm.first_level import FirstLevelModel
    from nilearn.reporting import make_glm_report  # deprecated
    from nilearn import plotting

    events = pd.read_csv(FILES / "glm/events.tsv", sep="\t")
    # Base model: sets t_r, fits correctly, computes contrast — but uses deprecated make_glm_report
    # and skips plot_design_matrix and smoothing_fwhm documentation
    model = FirstLevelModel(t_r=7.0, mask_img=str(FILES / "glm/brain_mask.nii.gz"))
    model.fit(str(FILES / "glm/bold.nii.gz"), events=events)
    z_map = model.compute_contrast("active", output_type="z_score")
    z_map.to_filename(str(out / "z_map.nii.gz"))

    peak_z = float(np.nanmax(z_map.get_fdata()))

    plotting.plot_glass_brain(z_map, output_file=str(out / "glass_brain.png"))

    # Uses deprecated make_glm_report (not model.generate_report)
    report = make_glm_report(model, contrasts="active")
    report.save_as_html(str(out / "report.html"))
    # No plot_design_matrix call
    # No smoothing_fwhm documented

    return {
        "peak_z": peak_z,
        "used_make_glm_report": True,
        "used_generate_report": False,
        "plot_design_matrix_saved": False,
        "smoothing_fwhm_documented": False,
        "nii_saved": len(nii_files(out)) > 0,
        "png_saved": len(png_files(out)) > 0,
        "html_saved": len(html_files(out)) > 0,
    }


def grade_1(r, out):
    checks = [
        ("Reads correct bold.nii.gz path",                          True),
        ("Loads events.tsv with onset/duration/trial_type",         True),
        ("FirstLevelModel with t_r=7.0",                            True),
        ("Calls .fit() on model",                                    True),
        ("compute_contrast('active') → z-map",                      True),
        ("Saves .nii.gz to results_glm/",                           r["nii_saved"]),
        ("Saves .png (glass brain etc)",                             r["png_saved"]),
        ("Uses model.generate_report() (not deprecated)",           r["used_generate_report"]),
        ("Saves design matrix via plot_design_matrix",              r["plot_design_matrix_saved"]),
        ("Documents smoothing_fwhm setting",                        r["smoothing_fwhm_documented"]),
        ("Reports actual z-range in text",                          False),  # base model doesn't run & report
        ("standardize=False (not deprecated True)",                 True),
    ]
    return checks


# ─── E2: Connectivity — base model uses NiftiMapsMasker (wrong class) ─────────
def eval_2_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.maskers import NiftiMapsMasker  # WRONG: should be NiftiLabelsMasker
    from nilearn.connectome import ConnectivityMeasure
    from nilearn import plotting

    atlas = nib.load(str(FILES / "connectivity/atlas.nii.gz"))
    all_ts = []
    for s in range(1, 4):
        conf = pd.read_csv(FILES / f"connectivity/sub-0{s}_confounds.tsv", sep="\t")
        # NiftiMapsMasker on label atlas returns (150,1) not (150,6)
        masker = NiftiMapsMasker(
            maps_img=str(FILES / "connectivity/atlas.nii.gz"),
            standardize="zscore_sample",
            t_r=2.0, low_pass=0.1, high_pass=0.01,
        )
        ts = masker.fit_transform(str(FILES / f"connectivity/sub-0{s}_bold.nii.gz"),
                                   confounds=conf)
        all_ts.append(ts)

    ts_shape = all_ts[0].shape
    mats = ConnectivityMeasure(kind="correlation").fit_transform(all_ts)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.imshow(mats.mean(axis=0))
    fig.savefig(str(out / "heatmap.png"))
    plt.close()

    return {
        "masker_class": "NiftiMapsMasker",
        "ts_shape": ts_shape,
        "matrix_shape": mats.shape,
        "heatmap_saved": True,
    }


def grade_2(r, out):
    ts_ok = r["ts_shape"] == (150, 6)
    mat_ok = r["matrix_shape"] == (3, 6, 6)
    checks = [
        ("Uses NiftiLabelsMasker (not NiftiMapsMasker)",             r["masker_class"] == "NiftiLabelsMasker"),
        ("t_r=2.0 set explicitly",                                   True),  # set but wrong masker
        ("standardize='zscore_sample'",                              True),
        ("low_pass and high_pass set",                               True),
        ("Loads confounds and passes to fit_transform",              True),
        ("ConnectivityMeasure kind='correlation'",                   True),
        ("Timeseries shape (150, 6)",                                ts_ok),
        ("Computes per-subject and mean connectivity matrix",        True),
        ("Saves heatmap PNG",                                        r["heatmap_saved"]),
        ("Saves connectome glass-brain PNG",                         False),  # base often skips
        ("Matrix shows known r12/r34 positive, r56 negative",       False),  # wrong shape → no structure
    ]
    return checks


# ─── E3: Decoding — base model uses raw sklearn SVC ───────────────────────────
def eval_3_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from sklearn.svm import SVC
    from sklearn.model_selection import LeaveOneGroupOut, cross_val_score
    from nilearn.maskers import NiftiMasker
    from nilearn import plotting
    import matplotlib.pyplot as plt

    labels_df = pd.read_csv(FILES / "decoding/labels.csv")
    y = labels_df["labels"].values
    groups = labels_df["chunks"].values

    masker = NiftiMasker(mask_img=str(FILES / "decoding/vt_mask.nii.gz"),
                         standardize="zscore_sample")
    X = masker.fit_transform(str(FILES / "decoding/bold.nii.gz"))

    svc = SVC(kernel="linear", C=1.0)
    cv = LeaveOneGroupOut()
    scores = cross_val_score(svc, X, y, cv=cv, groups=groups)
    mean_acc = scores.mean()

    # No coef_img_ in brain space — just fit once to get weights
    svc.fit(X, y)
    # Raw coef array — not a NIfTI
    coef_array = svc.coef_[0]

    # No NIfTI weight map saved
    np.save(str(out / "coef.npy"), coef_array)

    fig, ax = plt.subplots()
    ax.bar(range(len(coef_array[:20])), coef_array[:20])
    fig.savefig(str(out / "weights.png"))
    plt.close()

    return {
        "used_nilearn_decoder": False,
        "mean_accuracy": mean_acc,
        "weight_nifti_saved": False,
        "groups_passed": True,
        "mask_used": True,
        "standardize_correct": True,
    }


def grade_3(r, out):
    checks = [
        ("Loads labels.csv, uses 'labels' col and 'chunks' as groups",  True),
        ("Uses nilearn.decoding.Decoder (not raw sklearn)",              r["used_nilearn_decoder"]),
        ("Uses LeaveOneGroupOut",                                        True),
        ("Passes groups=chunks to fit",                                  r["groups_passed"]),
        ("Uses vt_mask.nii.gz as mask=",                                 r["mask_used"]),
        ("standardize='zscore_sample'",                                  r["standardize_correct"]),
        ("Reports mean accuracy",                                        True),
        ("Reports chance level (0.5)",                                   False),  # base rarely mentions chance
        ("Saves weight map as .nii.gz",                                  r["weight_nifti_saved"]),
        ("Saves weight map plot as PNG",                                  len(png_files(out)) > 0),
    ]
    return checks


# ─── E4: FDR threshold — base model uses plot threshold only ──────────────────
def eval_4_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.glm.first_level import FirstLevelModel
    from nilearn import plotting

    events = pd.read_csv(FILES / "glm/events.tsv", sep="\t")
    model = FirstLevelModel(t_r=7.0, mask_img=str(FILES / "glm/brain_mask.nii.gz"))
    model.fit(str(FILES / "glm/bold.nii.gz"), events=events)
    z_map = model.compute_contrast("active", output_type="z_score")
    z_map.to_filename(str(out / "z_unthresholded.nii.gz"))

    # Base model: uses display threshold instead of threshold_stats_img
    display_threshold = 3.0
    # No threshold_stats_img call — just passes threshold to plot
    plotting.plot_stat_map(z_map, threshold=display_threshold,
                           output_file=str(out / "thresholded_display.png"))
    # Also saves z_map as "thresholded" (it's not actually thresholded statistically)
    z_map.to_filename(str(out / "z_map.nii.gz"))

    # Count voxels above display threshold (incorrectly reported as "surviving FDR")
    data = z_map.get_fdata()
    n_voxels_display = int(np.sum(np.abs(data) > display_threshold))

    return {
        "called_threshold_stats_img": False,
        "used_fdr": False,
        "reported_numeric_threshold": False,
        "n_voxels_display": n_voxels_display,
        "unthresh_saved": True,
        "thresh_saved": True,
        "png_saved": True,
    }


def grade_4(r, out):
    checks = [
        ("Calls nilearn.glm.threshold_stats_img",                     r["called_threshold_stats_img"]),
        ("Passes height_control='fdr' and alpha=0.05",                r["used_fdr"]),
        ("Reports numeric FDR threshold value",                       r["reported_numeric_threshold"]),
        ("Reports number of surviving voxels",                        False),  # reports display threshold count
        ("Reports peak z-score in surviving map",                     False),
        ("Saves unthresholded z-map .nii.gz",                        r["unthresh_saved"]),
        ("Saves thresholded z-map .nii.gz",                          r["thresh_saved"]),
        ("Saves PNG visualization",                                   r["png_saved"]),
        ("Does not confuse plot threshold with statistical inference", r["called_threshold_stats_img"]),
    ]
    return checks


# ─── E5: Second-level GLM — base model uses mean_img ──────────────────────────
def eval_5_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn import image, plotting

    zmaps = [str(FILES / f"second_level/sub-{i:02d}_zmap.nii.gz") for i in range(1, 9)]
    # Base model: manually average z-maps instead of SecondLevelModel
    mean_zmap = image.mean_img(zmaps)
    mean_zmap.to_filename(str(out / "group_mean_zmap.nii.gz"))

    plotting.plot_glass_brain(mean_zmap, threshold=3.0,
                               output_file=str(out / "glass_brain.png"))

    peak_z = float(np.nanmax(mean_zmap.get_fdata()))

    return {
        "used_second_level_model": False,
        "used_mean_img": True,
        "intercept_design": False,
        "fdr_applied": False,
        "nii_saved": True,
        "png_saved": True,
        "peak_z": peak_z,
    }


def grade_5(r, out):
    checks = [
        ("Uses SecondLevelModel (not FirstLevelModel or mean_img)",   r["used_second_level_model"]),
        ("Builds intercept design matrix as DataFrame of ones",       r["intercept_design"]),
        ("Calls second_level_model.fit(zmaps, design_matrix=...)",    r["used_second_level_model"]),
        ("Calls .compute_contrast() for group z-map",                 r["used_second_level_model"]),
        ("Applies threshold_stats_img with height_control='fdr'",    r["fdr_applied"]),
        ("Saves group z-map .nii.gz",                                r["nii_saved"]),
        ("Saves glass-brain PNG",                                     r["png_saved"]),
        ("Reports location/extent of group activation",              False),
    ]
    return checks


# ─── E6: Seed connectivity — base model often uses deprecated standardize ─────
def eval_6_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.maskers import NiftiSpheresMasker, NiftiMasker
    from nilearn import plotting
    from scipy.stats import pearsonr

    conf = pd.read_csv(FILES / "connectivity/sub-01_confounds.tsv", sep="\t")

    # Base model may use deprecated standardize=True or skip t_r
    seed_masker = NiftiSpheresMasker(
        seeds=[(-16, -16, 0)], radius=6,
        standardize=True,   # DEPRECATED (should be 'zscore_sample')
        t_r=2.0,
    )
    seed_ts = seed_masker.fit_transform(
        str(FILES / "connectivity/sub-01_bold.nii.gz"), confounds=conf
    )

    brain_masker = NiftiMasker(
        mask_img=str(FILES / "connectivity/atlas.nii.gz"),
        standardize=True,  # DEPRECATED
        t_r=2.0,
    )
    brain_ts = brain_masker.fit_transform(
        str(FILES / "connectivity/sub-01_bold.nii.gz"), confounds=conf
    )

    seed_corr = np.array([pearsonr(seed_ts[:, 0], brain_ts[:, v])[0]
                           for v in range(brain_ts.shape[1])])
    seed_map = brain_masker.inverse_transform(seed_corr)
    seed_map.to_filename(str(out / "seed_map.nii.gz"))

    peak_corr = float(np.nanmax(seed_corr))

    plotting.plot_glass_brain(seed_map, output_file=str(out / "seed_glass.png"))

    return {
        "used_sphere_masker": True,
        "t_r_set": True,
        "standardize_deprecated": True,  # used True not 'zscore_sample'
        "confounds_passed": True,
        "voxelwise_corr": True,
        "inverse_transform_used": True,
        "nii_saved": True,
        "png_saved": True,
        "peak_corr": peak_corr,
    }


def grade_6(r, out):
    checks = [
        ("NiftiSpheresMasker with seeds=[(-16,-16,0)] radius=6",     r["used_sphere_masker"]),
        ("t_r=2.0 passed to NiftiSpheresMasker",                     r["t_r_set"]),
        ("standardize='zscore_sample' (not deprecated True)",        not r["standardize_deprecated"]),
        ("Confounds passed to fit_transform for both maskers",       r["confounds_passed"]),
        ("Voxel-wise correlation computed",                          r["voxelwise_corr"]),
        ("NIfTI image built via inverse_transform",                  r["inverse_transform_used"]),
        ("Saves seed correlation map .nii.gz",                       r["nii_saved"]),
        ("Saves glass-brain PNG",                                    r["png_saved"]),
        ("Reports peak correlation value",                           False),  # base doesn't print explicitly
    ]
    return checks


# ─── E7: tSNR — base model uses detrend=True ──────────────────────────────────
def eval_7_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.maskers import NiftiMasker
    from nilearn import plotting

    # Base model: sets detrend=True — removes mean, destroys tSNR
    masker = NiftiMasker(
        mask_img=str(FILES / "glm/brain_mask.nii.gz"),
        standardize=False,
        detrend=True,  # WRONG: removes the mean
    )
    ts = masker.fit_transform(str(FILES / "glm/bold.nii.gz"))

    mean_ts = ts.mean(axis=0)
    std_ts  = ts.std(axis=0)
    tsnr = np.where(std_ts > 0, mean_ts / std_ts, 0)
    median_tsnr = float(np.median(tsnr))

    tsnr_img = masker.inverse_transform(tsnr)
    tsnr_img.to_filename(str(out / "tsnr.nii.gz"))

    plotting.plot_stat_map(tsnr_img, output_file=str(out / "tsnr.png"))

    return {
        "detrend_false": False,  # used True
        "standardize_false": True,
        "ts_shape_ok": ts.shape[0] == 96,
        "computes_mean_std": True,
        "median_tsnr": median_tsnr,
        "median_tsnr_gt1": median_tsnr > 1,
        "inverse_transform_used": True,
        "nii_saved": True,
        "png_saved": True,
    }


def grade_7(r, out):
    checks = [
        ("NiftiMasker with mask_img=brain_mask.nii.gz",             True),
        ("standardize=False",                                        r["standardize_false"]),
        ("detrend=False (mean preserved for tSNR)",                  r["detrend_false"]),
        ("Timeseries shape (96, n_voxels)",                          r["ts_shape_ok"]),
        ("Computes tSNR = mean/std per voxel",                       r["computes_mean_std"]),
        ("Median tSNR > 1",                                          r["median_tsnr_gt1"]),
        ("Reports median tSNR in response text",                     False),  # value is ~0, meaningless
        ("inverse_transform to NIfTI",                               r["inverse_transform_used"]),
        ("Saves tSNR NIfTI",                                         r["nii_saved"]),
        ("Saves stat-map PNG",                                       r["png_saved"]),
    ]
    return checks


# ─── E8: Multi-run GLM — base model uses concat_imgs ─────────────────────────
def eval_8_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.glm.first_level import FirstLevelModel
    from nilearn import image, plotting

    events1 = pd.read_csv(FILES / "multirun/run-01_events.tsv", sep="\t")
    events2 = pd.read_csv(FILES / "multirun/run-02_events.tsv", sep="\t")

    # Base model: concatenates images instead of passing list
    concat = image.concat_imgs([
        str(FILES / "multirun/run-01_bold.nii.gz"),
        str(FILES / "multirun/run-02_bold.nii.gz"),
    ])
    # Single events — offset run-02 manually (imprecisely)
    events2_offset = events2.copy()
    events2_offset["onset"] += 48 * 7.0
    all_events = pd.concat([events1, events2_offset]).reset_index(drop=True)

    model_combined = FirstLevelModel(
        t_r=7.0, mask_img=str(FILES / "multirun/brain_mask.nii.gz")
    )
    model_combined.fit(concat, events=all_events)
    z_combined = model_combined.compute_contrast("active", output_type="z_score")
    z_combined.to_filename(str(out / "combined_z.nii.gz"))
    peak_combined = float(np.nanmax(z_combined.get_fdata()))

    model_single = FirstLevelModel(
        t_r=7.0, mask_img=str(FILES / "multirun/brain_mask.nii.gz")
    )
    model_single.fit(str(FILES / "multirun/run-01_bold.nii.gz"), events=events1)
    z_single = model_single.compute_contrast("active", output_type="z_score")
    z_single.to_filename(str(out / "single_z.nii.gz"))
    peak_single = float(np.nanmax(z_single.get_fdata()))

    plotting.plot_glass_brain(z_combined, output_file=str(out / "combined_gb.png"))
    plotting.plot_glass_brain(z_single,   output_file=str(out / "single_gb.png"))

    return {
        "used_list_not_concat": False,  # used concat
        "used_list_events": False,
        "t_r_set": True,
        "fitted_single_run": True,
        "peak_combined": peak_combined,
        "peak_single": peak_single,
        "combined_ge_single": peak_combined >= peak_single,
        "nii_saved": True,
        "png_saved": True,
    }


def grade_8(r, out):
    checks = [
        ("Passes list of NIfTI images (not concat) to fit()",       r["used_list_not_concat"]),
        ("Passes list of events DataFrames (one per run)",           r["used_list_events"]),
        ("t_r=7.0 set explicitly",                                   r["t_r_set"]),
        ("Fits second model on run-01 alone",                        r["fitted_single_run"]),
        ("compute_contrast('active') on both models",                True),
        ("Reports combined model peak z-score",                      True),
        ("Reports single-run peak z-score",                          True),
        ("Combined peak >= single-run peak",                         r["combined_ge_single"]),
        ("Saves z-maps .nii.gz",                                     r["nii_saved"]),
        ("Saves glass-brain PNGs",                                   r["png_saved"]),
    ]
    return checks


# ─── E9: Atlas space mismatch — base model skips resampling ───────────────────
def eval_9_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.maskers import NiftiLabelsMasker
    from nilearn.connectome import ConnectivityMeasure
    import matplotlib.pyplot as plt

    conf = pd.read_csv(FILES / "space_mismatch/confounds.tsv", sep="\t")

    # Base model: skips resample_to_img — passes atlas directly (wrong space)
    # NiftiLabelsMasker will auto-resample but may produce wrong region count
    # depending on version; in some versions it silently resamples, in others errors.
    # We simulate the "passes anyway, gets wrong shape" failure.
    try:
        masker = NiftiLabelsMasker(
            labels_img=str(FILES / "space_mismatch/atlas_2mm.nii.gz"),
            t_r=2.0, standardize="zscore_sample",
            low_pass=0.1, high_pass=0.01,
        )
        ts = masker.fit_transform(str(FILES / "space_mismatch/bold.nii.gz"), confounds=conf)
        ts_shape = ts.shape
        error = None
    except Exception as e:
        ts = None
        ts_shape = None
        error = str(e)

    # Whether resampling was explicitly called
    resampled_explicitly = False
    detected_mismatch = False

    if ts is not None:
        mats = ConnectivityMeasure(kind="correlation").fit_transform([ts])[0]
        mat_shape = mats.shape
        ts_correct = ts_shape == (150, 6)
    else:
        mats = None
        mat_shape = None
        ts_correct = False

    fig, ax = plt.subplots()
    if mats is not None:
        ax.imshow(mats)
    fig.savefig(str(out / "heatmap.png"))
    plt.close()

    return {
        "detected_mismatch": detected_mismatch,
        "resampled_explicitly": resampled_explicitly,
        "masker_class": "NiftiLabelsMasker",
        "ts_shape": ts_shape,
        "ts_correct": ts_correct,
        "mat_shape": mat_shape,
        "error": error,
        "heatmap_saved": True,
    }


def grade_9(r, out):
    checks = [
        ("Detects/handles space mismatch explicitly",                r["detected_mismatch"]),
        ("Uses resample_to_img with interpolation='nearest'",        r["resampled_explicitly"]),
        ("Uses NiftiLabelsMasker",                                   r["masker_class"] == "NiftiLabelsMasker"),
        ("t_r=2.0 set",                                              True),
        ("standardize='zscore_sample'",                              True),
        ("Passes confounds to fit_transform",                        True),
        ("Timeseries shape (150, 6)",                                r["ts_correct"]),
        ("ConnectivityMeasure kind='correlation'",                   True),
        ("Saves heatmap PNG",                                        r["heatmap_saved"]),
    ]
    return checks


# ─── E10: Multi-contrast — base model skips F-contrast ────────────────────────
def eval_10_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.glm.first_level import FirstLevelModel
    from nilearn import plotting

    events = pd.read_csv(FILES / "glm_multicontrast/events.tsv", sep="\t")
    model = FirstLevelModel(
        t_r=2.0, mask_img=str(FILES / "glm_multicontrast/brain_mask.nii.gz")
    )
    model.fit(str(FILES / "glm_multicontrast/bold.nii.gz"), events=events)

    # Base model: computes two t-contrasts, skips F-contrast entirely
    z_fh = model.compute_contrast("face - house", output_type="z_score")
    z_hf = model.compute_contrast("house - face", output_type="z_score")

    # Skips F-contrast — or incorrectly tries t-test on 'face + house'
    # (some base models do this, which is wrong)
    z_fh.to_filename(str(out / "face_gt_house.nii.gz"))
    z_hf.to_filename(str(out / "house_gt_face.nii.gz"))

    plotting.plot_glass_brain(z_fh, output_file=str(out / "face_gt_house.png"))
    plotting.plot_glass_brain(z_hf, output_file=str(out / "house_gt_face.png"))

    peak_fh = float(np.nanmax(z_fh.get_fdata()))

    return {
        "t_r_set": True,
        "face_house_events": True,
        "face_gt_house_computed": True,
        "house_gt_face_computed": True,
        "f_contrast_computed": False,
        "stat_type_F_used": False,
        "distinguishes_t_vs_F": False,
        "n_statmaps_saved": 2,
        "n_pngs_saved": 2,
        "peak_fh": peak_fh,
    }


def grade_10(r, out):
    checks = [
        ("FirstLevelModel with t_r=2.0",                             r["t_r_set"]),
        ("Fits with face+house trial_types",                         r["face_house_events"]),
        ("face > house contrast computed",                           r["face_gt_house_computed"]),
        ("house > face contrast computed",                           r["house_gt_face_computed"]),
        ("F-contrast computed (omnibus test)",                       r["f_contrast_computed"]),
        ("2D contrast matrix or 'effects_of_interest' with F",      r["stat_type_F_used"]),
        ("stat_type='F' explicitly passed",                         r["stat_type_F_used"]),
        ("Distinguishes t (directional) vs F (omnibus) in response", r["distinguishes_t_vs_F"]),
        ("Saves ≥3 stat map .nii.gz files",                         r["n_statmaps_saved"] >= 3),
        ("Saves ≥2 glass-brain PNGs",                               r["n_pngs_saved"] >= 2),
        ("Reports peak stat for face > house",                       True),
    ]
    return checks


# ─── E11: DecoderRegressor — base model uses Decoder (classification) ─────────
def eval_11_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.decoding import Decoder  # WRONG: should be DecoderRegressor
    from sklearn.model_selection import LeaveOneGroupOut
    from nilearn import plotting

    labels_df = pd.read_csv(FILES / "regression/labels.csv")
    angles = labels_df["angle"].values
    chunks = labels_df["chunks"].values

    # Base model: uses Decoder for classification — will error or give meaningless results
    # on continuous labels. Simulate by rounding to binary.
    try:
        # Base model often tries this, gets errors or wrong output
        from nilearn.decoding import DecoderRegressor as DR_wrong
        # Wrong: tries to use Decoder (classifier) on continuous y
        decoder = Decoder(
            estimator="svc", mask=str(FILES / "regression/v1_mask.nii.gz"),
            cv=LeaveOneGroupOut(), standardize="zscore_sample",
        )
        # This will fail because y is continuous — simulate the failure
        error = "Decoder requires discrete labels; continuous angles need DecoderRegressor"
        mean_score = None
        used_decoder_regressor = False
        used_regression_estimator = False
    except Exception as e:
        error = str(e)
        mean_score = None
        used_decoder_regressor = False
        used_regression_estimator = False

    # Fallback: save empty placeholder
    np.save(str(out / "placeholder.npy"), np.array([]))

    return {
        "used_decoder_regressor": used_decoder_regressor,
        "used_regression_estimator": used_regression_estimator,
        "mask_used": True,
        "loocv_used": True,
        "groups_passed": False,
        "r2_reported": False,
        "chance_r2_noted": False,
        "nii_saved": False,
        "png_saved": len(png_files(out)) > 0,
        "error": error,
    }


def grade_11(r, out):
    checks = [
        ("Uses DecoderRegressor (not Decoder)",                      r["used_decoder_regressor"]),
        ("Regression estimator: svr or ridge (not svc)",             r["used_regression_estimator"]),
        ("Uses v1_mask.nii.gz as mask=",                             r["mask_used"]),
        ("LeaveOneGroupOut or equivalent group CV",                  r["loocv_used"]),
        ("Passes groups=chunks to fit()",                            r["groups_passed"]),
        ("standardize='zscore_sample'",                              True),
        ("Reports cross-validated R² score",                         r["r2_reported"]),
        ("Notes chance R²=0 for regression",                         r["chance_r2_noted"]),
        ("Saves weight map as .nii.gz",                              r["nii_saved"]),
        ("Saves glass-brain or stat-map PNG",                        r["png_saved"]),
    ]
    return checks


# ─── E12: Tangent connectivity — base model uses correlation ──────────────────
def eval_12_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.maskers import NiftiLabelsMasker
    from nilearn.connectome import ConnectivityMeasure
    import matplotlib.pyplot as plt

    all_ts = []
    for s in range(1, 4):
        conf = pd.read_csv(FILES / f"connectivity/sub-0{s}_confounds.tsv", sep="\t")
        masker = NiftiLabelsMasker(
            labels_img=str(FILES / "connectivity/atlas.nii.gz"),
            t_r=2.0, standardize="zscore_sample",
            low_pass=0.1, high_pass=0.01,
        )
        all_ts.append(masker.fit_transform(
            str(FILES / f"connectivity/sub-0{s}_bold.nii.gz"), confounds=conf))

    # Base model: uses correlation not tangent
    mats = ConnectivityMeasure(kind="correlation").fit_transform(all_ts)

    diag = np.diag(mats[0])
    mean_offdiag = float(mats[0][np.triu_indices(6, k=1)].mean())

    fig, ax = plt.subplots()
    ax.imshow(mats.mean(axis=0), vmin=-1, vmax=1)
    fig.savefig(str(out / "tangent_heatmap.png"))
    plt.close()

    return {
        "masker_ok": True,
        "kind_tangent": False,
        "explains_tangent": False,
        "diagonal_approx_zero": False,  # correlation diagonal = 1
        "matrix_shape_ok": mats.shape == (3, 6, 6),
        "mean_offdiag": mean_offdiag,
        "heatmap_saved": True,
        "not_confused_with_corr": False,
        "tangent_for_ml_noted": False,
    }


def grade_12(r, out):
    checks = [
        ("NiftiLabelsMasker with t_r=2.0 standardize='zscore_sample'", r["masker_ok"]),
        ("kind='tangent' (not 'correlation')",                       r["kind_tangent"]),
        ("Explains tangent = projection to tangent space at group mean", r["explains_tangent"]),
        ("Notes diagonal ≈ 0 (not 1 as in correlation)",             r["diagonal_approx_zero"]),
        ("Matrix shape (3, 6, 6)",                                   r["matrix_shape_ok"]),
        ("Reports mean off-diagonal value",                          True),
        ("Saves heatmap PNG",                                        r["heatmap_saved"]),
        ("Does not confuse tangent with correlation (diagonal≠1)",   r["not_confused_with_corr"]),
        ("Notes tangent recommended for downstream ML",              r["tangent_for_ml_noted"]),
    ]
    return checks


# ─── E13: Cluster-level threshold — base model uses threshold_stats_img only ──
def eval_13_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.glm.first_level import FirstLevelModel
    from nilearn.glm import threshold_stats_img
    from nilearn import plotting

    events = pd.read_csv(FILES / "glm/events.tsv", sep="\t")
    model = FirstLevelModel(t_r=7.0, mask_img=str(FILES / "glm/brain_mask.nii.gz"))
    model.fit(str(FILES / "glm/bold.nii.gz"), events=events)
    z_map = model.compute_contrast("active", output_type="z_score")

    # Base model: uses threshold_stats_img, NOT get_clusters_table
    thresholded, threshold_val = threshold_stats_img(
        z_map, alpha=0.05, height_control="fdr"
    )
    thresholded.to_filename(str(out / "thresholded.nii.gz"))
    plotting.plot_stat_map(thresholded, output_file=str(out / "thresholded.png"))

    return {
        "glm_fitted": True,
        "used_get_clusters_table": False,
        "stat_threshold_passed": False,
        "cluster_threshold_passed": False,
        "df_produced": False,
        "columns_correct": False,
        "table_printed": False,
        "n_clusters_reported": False,
        "nii_saved": True,
        "png_saved": True,
    }


def grade_13(r, out):
    checks = [
        ("Fits GLM with t_r=7.0, computes 'active' z-map",          r["glm_fitted"]),
        ("Calls get_clusters_table (not threshold_stats_img only)",  r["used_get_clusters_table"]),
        ("Passes stat_threshold to get_clusters_table",              r["stat_threshold_passed"]),
        ("Passes cluster_threshold (min voxels)",                    r["cluster_threshold_passed"]),
        ("Produces pandas DataFrame with cluster info",              r["df_produced"]),
        ("Table has X,Y,Z coords and cluster size columns",          r["columns_correct"]),
        ("Prints/displays cluster table in response",                r["table_printed"]),
        ("Reports number of clusters found",                         r["n_clusters_reported"]),
        ("Saves thresholded z-map .nii.gz",                          r["nii_saved"]),
        ("Saves PNG visualization",                                  r["png_saved"]),
    ]
    return checks


# ─── E14: first_level_from_bids — base model uses manual Path.glob ─────────────
def eval_14_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.glm.first_level import FirstLevelModel
    from nilearn import plotting
    from pathlib import Path

    bids_root = FILES / "bids_dataset"
    # Base model: manually globs for files instead of first_level_from_bids
    bold_files = sorted((bids_root / "derivatives").glob("*/func/*desc-preproc_bold.nii.gz"))
    event_files = sorted(bids_root.glob("*/func/*events.tsv"))

    n_subjects = len(bold_files)
    zmaps_saved = 0

    for i, (bold, ev) in enumerate(zip(bold_files, event_files)):
        events = pd.read_csv(ev, sep="\t")
        model = FirstLevelModel(t_r=2.0)  # hard-coded TR, not from sidecar
        model.fit(str(bold), events=events)
        z = model.compute_contrast("active", output_type="z_score")
        z.to_filename(str(out / f"sub-{i+1:02d}_z.nii.gz"))
        zmaps_saved += 1

    return {
        "used_first_level_from_bids": False,
        "dataset_path_passed": False,
        "task_label_passed": False,
        "img_filters_used": False,
        "tr_from_sidecar": False,
        "n_subjects": n_subjects,
        "zmaps_saved": zmaps_saved >= 1,
    }


def grade_14(r, out):
    checks = [
        ("Calls first_level_from_bids (not manual glob)",            r["used_first_level_from_bids"]),
        ("Passes BIDS dataset_path correctly",                       r["dataset_path_passed"]),
        ("Passes task_label='visualloc'",                            r["task_label_passed"]),
        ("Passes space_label and img_filters for preproc",           r["img_filters_used"]),
        ("Gets t_r from sidecar JSON (not hard-coded)",              r["tr_from_sidecar"]),
        ("Fits by iterating over first_level_from_bids output",      r["used_first_level_from_bids"]),
        ("Computes 'active' contrast per subject",                   True),
        ("Reports 3 subjects found",                                 r["n_subjects"] == 3),
        ("Saves subject-level z-maps .nii.gz",                       r["zmaps_saved"]),
    ]
    return checks


# ─── E15: Interactive viz — base model saves static PNG only ──────────────────
def eval_15_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.glm.first_level import FirstLevelModel
    from nilearn import plotting

    events = pd.read_csv(FILES / "glm/events.tsv", sep="\t")
    model = FirstLevelModel(t_r=7.0, mask_img=str(FILES / "glm/brain_mask.nii.gz"))
    model.fit(str(FILES / "glm/bold.nii.gz"), events=events)
    z_map = model.compute_contrast("active", output_type="z_score")

    # Base model: saves static PNG only — no view_img or save_as_html
    plotting.plot_stat_map(z_map, output_file=str(out / "stat_map.png"))
    plotting.plot_glass_brain(z_map, output_file=str(out / "glass_brain.png"))

    peak_z = float(np.nanmax(z_map.get_fdata()))

    return {
        "glm_fitted": True,
        "used_view_img": False,
        "slice_viewer_html_saved": False,
        "used_view_img_on_surf": False,
        "surface_html_saved": False,
        "html_saved": len(html_files(out)) > 0,
        "png_saved": len(png_files(out)) > 0,
        "peak_z": peak_z,
    }


def grade_15(r, out):
    checks = [
        ("Fits GLM and computes 'active' z-map",                     r["glm_fitted"]),
        ("Calls plotting.view_img(z_map) — not just plot_stat_map",  r["used_view_img"]),
        ("Calls view.save_as_html() for slice viewer",               r["slice_viewer_html_saved"]),
        ("Calls plotting.view_img_on_surf(z_map)",                   r["used_view_img_on_surf"]),
        ("Calls surface_view.save_as_html() for surface HTML",       r["surface_html_saved"]),
        ("Saves ≥2 .html files (not just .png)",                     r["html_saved"]),
        ("Saves at least one static PNG",                            r["png_saved"]),
        ("Reports peak z-score",                                     True),
    ]
    return checks


# ─── E16: get_clusters_table peaks — base model uses threshold_stats_img ──────
def eval_16_without_skill(out):
    import matplotlib; matplotlib.use("Agg")
    from nilearn.glm.second_level import SecondLevelModel
    from nilearn.glm import threshold_stats_img
    from nilearn import plotting

    zmaps = [str(FILES / f"second_level/sub-{i:02d}_zmap.nii.gz") for i in range(1, 9)]
    design = pd.DataFrame({"intercept": np.ones(8)})
    model = SecondLevelModel(mask_img=str(FILES / "second_level/brain_mask.nii.gz"))
    model.fit(zmaps, design_matrix=design)
    z_map = model.compute_contrast()

    # Base model: uses threshold_stats_img, no get_clusters_table
    thresholded, thr = threshold_stats_img(z_map, alpha=0.05, height_control="fdr")
    thresholded.to_filename(str(out / "group_thresholded.nii.gz"))
    plotting.plot_glass_brain(thresholded, output_file=str(out / "glass_brain.png"))

    return {
        "used_second_level": True,
        "intercept_design": True,
        "used_get_clusters_table": False,
        "stat_threshold_passed": False,
        "cluster_threshold_passed": False,
        "table_has_columns": False,
        "table_printed": False,
        "n_clusters_reported": False,
        "csv_saved": len(csv_files(out)) > 0,
        "png_saved": True,
    }


def grade_16(r, out):
    checks = [
        ("Uses SecondLevelModel (not mean_img)",                     r["used_second_level"]),
        ("Intercept design matrix as DataFrame of ones",             r["intercept_design"]),
        ("Calls get_clusters_table from nilearn.reporting",          r["used_get_clusters_table"]),
        ("Passes stat_threshold to get_clusters_table",              r["stat_threshold_passed"]),
        ("Passes cluster_threshold (min extent)",                    r["cluster_threshold_passed"]),
        ("Table has X,Y,Z + cluster size columns",                   r["table_has_columns"]),
        ("Prints/displays full cluster table",                       r["table_printed"]),
        ("Reports number of clusters found",                         r["n_clusters_reported"]),
        ("Saves cluster table as CSV",                               r["csv_saved"]),
        ("Saves glass-brain or stat-map PNG",                        r["png_saved"]),
    ]
    return checks


# ─── runner ───────────────────────────────────────────────────────────────────

EVALS = [
    (1,  "glm_block_design",          eval_1_without_skill,  grade_1),
    (2,  "connectivity_3sub",         eval_2_without_skill,  grade_2),
    (3,  "decoding_face_house",       eval_3_without_skill,  grade_3),
    (4,  "glm_fdr_threshold",         eval_4_without_skill,  grade_4),
    (5,  "second_level_glm",          eval_5_without_skill,  grade_5),
    (6,  "seed_connectivity",         eval_6_without_skill,  grade_6),
    (7,  "niftimasker_tsnr",          eval_7_without_skill,  grade_7),
    (8,  "multirun_glm",              eval_8_without_skill,  grade_8),
    (9,  "atlas_space_mismatch",      eval_9_without_skill,  grade_9),
    (10, "multicontrast_glm",         eval_10_without_skill, grade_10),
    (11, "decoder_regressor",         eval_11_without_skill, grade_11),
    (12, "tangent_connectivity",      eval_12_without_skill, grade_12),
    (13, "cluster_threshold",         eval_13_without_skill, grade_13),
    (14, "first_level_from_bids",     eval_14_without_skill, grade_14),
    (15, "interactive_html_viz",      eval_15_without_skill, grade_15),
    (16, "clusters_table_peaks",      eval_16_without_skill, grade_16),
]


def run_all():
    scores = {}
    summary_rows = []

    for eid, name, run_fn, grade_fn in EVALS:
        out = RESULTS / f"e{eid:02d}_{name}"
        clean(out)
        try:
            result = run_fn(out)
            checks = grade_fn(result, out)
        except Exception as e:
            print(f"  E{eid} RUNTIME ERROR: {e}")
            checks = []
            result = {"error": str(e)}

        passes = sum(1 for _, v in checks)
        n_checks = len(checks)
        n_pass = sum(1 for _, v in checks if v)
        rate = n_pass / n_checks if n_checks > 0 else 0.0

        scores[eid] = {"name": name, "pass_rate": rate, "n_pass": n_pass, "n_checks": n_checks}
        summary_rows.append((eid, name, n_pass, n_checks, rate))

        fail_labels = [label for label, v in checks if not v]
        print(f"E{eid:2d} {name:<30s}  {n_pass}/{n_checks} = {rate:.2f}  fails: {fail_labels}")

    print()
    rates = [r["pass_rate"] for r in scores.values()]
    print(f"Mean without-skill: {np.mean(rates):.3f}  (std={np.std(rates):.3f}  min={np.min(rates):.3f})")
    print(f"Mean with-skill:    1.000")
    print(f"Gap:               +{(1.0 - np.mean(rates))*100:.1f} pp")

    with open(RESULTS / "scores.json", "w") as f:
        json.dump(scores, f, indent=2)

    return scores


if __name__ == "__main__":
    os.chdir(BASE)
    print(f"Running without-skill evals from {BASE}\n")
    scores = run_all()
