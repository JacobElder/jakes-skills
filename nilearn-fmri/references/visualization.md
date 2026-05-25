# Visualization and Reporting

nilearn ships rich plotting (`nilearn.plotting`) and HTML reporting (`nilearn.reporting`). This reference covers the patterns that come up most.

## Static brain map plots

### plot_stat_map — slice views with stat overlay

The most common plot: shows axial/sagittal/coronal slices with a stat map overlay.

```python
from nilearn import plotting

plotting.plot_stat_map(
    z_map,
    threshold=3.1,                  # display threshold, not statistical correction
    display_mode="ortho",           # 'ortho' (3 slices), 'x', 'y', 'z' (axis), 'mosaic'
    cut_coords=(-30, -50, 0),       # MNI coords; or an int for n auto-chosen cuts
    bg_img=anat_img,                # optional background; defaults to MNI152
    title="Face > House (z>3.1)",
    colorbar=True,
    output_file="face_vs_house.png",  # if None, returns the display object
)
```

To get many slices along one axis:
```python
plotting.plot_stat_map(z_map, display_mode="z", cut_coords=10, threshold=3.1)
```

### plot_glass_brain — see whole brain at once

Maximum-intensity projection onto a glass brain. Good for getting a holistic view.

```python
plotting.plot_glass_brain(
    z_map,
    threshold=3.1,
    plot_abs=False,           # False shows positive/negative; True shows magnitude only
    display_mode="lyrz",      # 'l' left sag, 'y' coronal, 'r' right sag, 'z' axial
    colorbar=True,
    title="Group face > house",
    output_file="glass_brain.png",
)
```

### plot_anat / plot_epi / plot_roi

```python
# Anatomical
plotting.plot_anat(anat_img, title="T1w")

# Mean EPI (for QC)
from nilearn.image import mean_img
plotting.plot_epi(mean_img(bold_img), title="Mean BOLD")

# ROI mask or atlas
plotting.plot_roi(atlas.maps, title="Schaefer 400", colorbar=True)
```

### plot_design_matrix

```python
from nilearn.plotting import plot_design_matrix
plot_design_matrix(model.design_matrices_[0], output_file="design.png")
```

### plot_contrast_matrix

```python
from nilearn.plotting import plot_contrast_matrix
contrast = "face - house"
plot_contrast_matrix(contrast, design_matrix=model.design_matrices_[0],
                      output_file="contrast.png")
```

## Connectivity plots

### plot_matrix — correlation matrix heatmap

```python
import numpy as np

# Always zero the diagonal first
np.fill_diagonal(matrix, 0)

plotting.plot_matrix(
    matrix,
    labels=atlas.labels,
    vmax=0.8, vmin=-0.8,
    reorder=True,           # cluster-reorder
    figure=(10, 10),
)
```

### plot_connectome — edges on a glass brain

```python
from nilearn.plotting import find_parcellation_cut_coords

coords = find_parcellation_cut_coords(atlas.maps)
plotting.plot_connectome(
    matrix,
    coords,
    edge_threshold="95%",       # show strongest 5% of edges
    node_size=20,
    colorbar=True,
    title="Connectome",
    output_file="connectome.png",
)
```

### plot_markers — values at ROI coords (e.g., decoding scores per region)

```python
plotting.plot_markers(
    node_values=accuracies,    # 1D array, one value per ROI
    node_coords=coords,
    node_size=50,
    output_file="markers.png",
)
```

## Interactive views (HTML)

These produce standalone HTML files with WebGL-based interactive 3D viewers. Use them when you want the user to be able to explore.

```python
# Interactive stat map (slice viewer with hover/zoom)
view = plotting.view_img(z_map, threshold=3.1, title="Face > House")
view.save_as_html("stat_map.html")

# 3D surface view
view = plotting.view_img_on_surf(z_map, threshold=3.1)
view.save_as_html("surface_view.html")

# Interactive connectome
view = plotting.view_connectome(matrix, coords, edge_threshold="95%")
view.save_as_html("connectome.html")

# 3D marker view
view = plotting.view_markers(coords, marker_size=10)
view.save_as_html("markers.html")
```

## HTML reports for GLM

A fitted first- or second-level model has a `.generate_report()` method that produces a comprehensive HTML report: design matrices, contrast definitions, glass-brain views, slice views, and clusters tables.

```python
# After fitting a first-level model
report = model.generate_report(
    contrasts={
        "face - house": "face - house",
        "face": "face",
        "house": "house",
    },
    threshold=3.1,                # only used when height_control=None
    height_control=None,          # or "fpr" / "fdr" / "bonferroni" + alpha=
    alpha=0.001,
    cluster_threshold=15,
    bg_img="MNI152TEMPLATE",      # default MNI152
    title="Subject 01 First-Level Report",
    plot_type="slice",            # or "glass"
)
report.save_as_html("first_level_report.html")
```

For second-level:
```python
report = group_model.generate_report(
    contrasts={"intercept": "intercept"},
    height_control="fdr", alpha=0.05, cluster_threshold=10
)
report.save_as_html("group_report.html")
```

**Important**: `threshold` is only honored when `height_control=None`. Otherwise nilearn computes the threshold from `alpha` and `height_control` and your `threshold` argument is ignored (with a warning).

The standalone `nilearn.reporting.make_glm_report` is still available but will be deprecated in 0.15 — use `.generate_report()` going forward.

## Surface plotting (fsaverage)

nilearn can also work on cortical surfaces (fsaverage). Useful for visualization even if your analysis was volumetric.

```python
from nilearn import surface, datasets

fsaverage = datasets.fetch_surf_fsaverage(mesh="fsaverage5")
texture = surface.vol_to_surf(z_map, fsaverage.pial_right)

plotting.plot_surf_stat_map(
    fsaverage.infl_right,
    texture,
    hemi="right",
    threshold=3.1,
    bg_map=fsaverage.sulc_right,
    output_file="surface.png",
)
```

## Clusters table

To get a tabular report of significant clusters (peak coordinates, sizes, etc.):

```python
from nilearn.reporting import get_clusters_table

table = get_clusters_table(
    z_map,
    stat_threshold=3.1,
    cluster_threshold=10,    # min cluster size in voxels
    two_sided=True,
)
print(table)
# Save as CSV
table.to_csv("clusters.csv", index=False)
```

The returned DataFrame has columns: `X`, `Y`, `Z` (peak MNI coordinates in mm), `Peak Stat` (z- or t-value at peak), `Cluster Size (mm3)` (volume of cluster), and `Parent Cluster` (0 for main cluster, 1+ for sub-peaks). This is the table that goes into a paper's "Table 1."

```python
# Typical usage: filter to main clusters only
main_clusters = table[table["Parent Cluster"] == 0]
print(f"Found {len(main_clusters)} clusters")
print(main_clusters[["X", "Y", "Z", "Peak Stat", "Cluster Size (mm3)"]].to_string())
```

## Common pitfalls

**`threshold` is display-only.** Setting `threshold=3.1` in `plot_stat_map` doesn't do statistical correction; it just hides voxels below |3.1|. For inference use `threshold_stats_img` first to get a corrected threshold, then pass that to the plot.

**Saving plots**: use the `output_file` argument inside the plot function rather than `plt.savefig` after. The functions return display objects that can be further modified (`disp.add_contours`, `disp.add_markers`), then saved via `disp.savefig(path)`.

**Headless rendering**: in a server environment without a display, set `matplotlib.use("Agg")` before importing nilearn plotting, or use `output_file=` consistently. Otherwise you may get backend errors.

**Massive HTML files**: `view_img` with high-resolution data can produce a 10+ MB HTML. Downsample to ~3mm before for shareability: `from nilearn.image import resample_img; ...`.

**Glass brain background**: `plot_glass_brain` uses a standardized brain outline, ignoring `bg_img`. Don't try to pass an anat — it'll be ignored.

**Atlas label colors are random**: if you want consistent colors across plots, pass an explicit cmap or build a custom colormap from atlas labels.

**Saving figure objects**: `plot_stat_map` etc. return a `OrthoSlicer` (or similar) display object, not a matplotlib Figure. To get the underlying figure: `display.frame_axes.figure`. But usually `output_file=` is cleaner.
