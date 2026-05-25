# Network Visualization

A bad network visualization is not "decoration that didn't work" — it is an inference error that you will then defend in front of stakeholders. This file covers when to visualize (often: don't), what to visualize (often: not the full network), and how to encode network properties so they are legible.

## When NOT to visualize the whole network

For networks with more than ~500 nodes or any moderate density (>5%), the default force-directed plot produces a "hairball": a dense central blob with peripheral stragglers, from which no structural insight can be drawn. The instinct to "show the network" is usually wrong for non-trivial networks. Alternatives:

- **Show a metagraph**: cluster nodes by community / role / attribute, plot a graph of clusters with weighted edges. Far more legible.
- **Show a matrix view**: an N×N heatmap of the adjacency, optionally reordered by community. For dense networks, this is more informative than the graph view.
- **Show ego networks of representative nodes**: pick a few exemplars and show their local neighborhoods.
- **Show summary distributions**: degree, betweenness, clustering, geodesic distance histograms. For exploratory work, these often answer the question.
- **Show small multiples**: facet by community, time, or condition.
- **Show a backbone**: extract the significant edges (disparity filter / SDSM) and plot only those.

## When to visualize, do it well

If you have a small-to-medium network (< few thousand nodes after backbone) and a graph view will help:

### Layout algorithms

| Algorithm | Best for | Limitations |
|---|---|---|
| **Fruchterman-Reingold** | Small graphs (< 1000 nodes), general purpose | Slow, hairball on large/dense |
| **Kamada-Kawai** | Small graphs where path distances matter | Slow O(n³) for full distance matrix |
| **ForceAtlas2** (Jacomy et al. 2014) | Medium graphs (< 10k), Gephi default | Better than FR for community structure with LinLog mode |
| **OpenOrd / DrL** | Large graphs (> 10k) | Fast but less faithful to local structure |
| **LGL (Large Graph Layout)** | Very large graphs with clusters | Identifies clusters first |
| **Stress majorization** (Gansner et al. 2004) | Medium graphs where geodesic distances matter | Quality-focused, not fast |
| **Yifan Hu multilevel** | Medium-to-large graphs | Good balance of speed and quality |
| **Sugiyama (layered)** | DAGs, hierarchical structure | Only for DAGs |
| **Circular** | Showing all nodes equally, comparison | Loses structure |
| **MDS** | When you want geometric interpretation | Slow; quality depends on dimensionality |

### Force-directed mechanics

All FDLs model nodes as particles with attractive forces (for connected pairs) and repulsive forces (for all pairs); the layout converges to an energy minimum.

- Fruchterman-Reingold: linear attractive, quadratic repulsive
- Kamada-Kawai: spring forces proportional to *graph-theoretic* (path) distances, not just connection
- ForceAtlas2 LinLog: logarithmic attraction, stronger separation of communities

Kobourov (2014) is the canonical survey.

### The hairball problem

For dense or large networks, standard FDLs converge to high-energy "hairball" states because there are too many constraints to satisfy. Fixes (Both, Pournaki et al. 2023; Meirelles et al. 2023):

1. **Multi-scale / hierarchical**: lay out clusters first, then nodes within clusters
2. **Backbone first**: extract significant edges only, lay out those
3. **GNN-based**: train a GNN to predict good layout positions (Both et al. 2023 — 10–100× speedup)
4. **Constraint relaxation**: drop weak edges before layout
5. **Latent-space-based** (Both et al. 2022): derive forces from a latent space model; gives interpretable positions

### Layouts that respect community structure

- ForceAtlas2 with `linLogMode=True` (Gephi)
- Yifan Hu multilevel
- Cluster-first then within-cluster: compute communities, lay out a metagraph, then lay out each community in its assigned region

For graph-tool nested SBMs, `draw_hierarchy` produces the canonical hierarchical visualization with concentric blocks.

## Visual encoding

### Node properties

- **Size**: numeric attribute (degree, centrality, attribute). Use **area** ∝ value, not radius (humans perceive area, not radius).
- **Color (hue)**: categorical attribute (community, role)
- **Color (saturation/luminance)**: continuous attribute (centrality, age). Sequential or diverging colormap depending on whether zero is meaningful (viridis for sequential; RdBu for diverging — never rainbow / jet)
- **Shape**: secondary categorical attribute (when hue is used for primary)
- **Border**: tertiary highlight (selected nodes)
- **Label**: only for the most important nodes (top-k by some criterion); labels for all nodes are illegible in any non-trivial network

### Edge properties

- **Width / thickness**: edge weight
- **Color**: edge attribute (type, sign positive/negative, direction)
- **Transparency**: low for hairballs (transparency lets density carry the signal)
- **Arrows**: for directed; sized appropriately for the layout
- **Curvature**: for directed reciprocal pairs (each direction curves differently), or to reduce overlap in bipartite-style displays

### Background and chrome

- White or very light gray background
- Suppress axes, gridlines, legends if not adding information
- Always include: legend (if encoding categorical attributes), scale (if positions have geometric meaning), source / N reported

## Specific visualization patterns

### Adjacency matrix view

For dense or large networks, replace the node-link view with a heatmap of A.

- Reorder rows/columns by **community** (Cuthill-McKee, RCM, or SBM block order) — block structure becomes visible as diagonal blocks
- For bipartite: rectangular heatmap
- For weighted: color = weight; for binary: black/white
- Implementation: `seaborn.heatmap`, `matplotlib.imshow`, or `holoviews` for interactive

Matrix views excel at showing block structure; they suck at showing path structure (you can't trace a path).

### Arc diagram

Nodes on a line, edges as arcs above. Good for:
- Small networks with a meaningful 1D order (time, alphabetical)
- Showing temporal sequence

Bad for: anything you actually want to read structurally.

### Hive plot (Krzywinski et al. 2012)

Nodes placed on radial axes (one per category); edges as curves between axes. Good for:
- Multi-attribute networks where you want to show category-by-category interaction
- Standardized comparisons across networks

### Sankey / alluvial diagram

For network flows or transitions over time. Each "slice" is a snapshot; edges between slices show movement.

### Geographic embedding

If nodes have geographic meaning (cities, brain regions), use the geography:
- For cities: place by lat/lon
- For brain regions: use anatomical coordinates
- For abstract networks: don't fake geography

### Temporal animation / small multiples

For temporal networks:
- **Animation**: smooth interpolation of layouts is hard; nodes "jump" between frames. Stabilization techniques (e.g., position regularization) help.
- **Small multiples**: 4-9 snapshots at chosen time points. Often more readable than animation.

## Tools

| Tool | Best for |
|---|---|
| **Gephi** | Interactive exploration, medium graphs, great FDL implementations |
| **Cytoscape** | Biological networks, large feature set, plugins |
| **igraph plotting** (R, Python) | Programmatic, reproducible static plots |
| **NetworkX matplotlib** | Quick prototyping; limited beauty |
| **graph-tool draw** | Publication-quality static plots; hierarchy support |
| **ggraph** (R) | Tidy/ggplot pipeline for network plots |
| **Plotly / Bokeh / D3** | Interactive web plots |
| **Sigma.js, Cytoscape.js, Cosmograph** | Web-native, scales to large |
| **VOSviewer** | Bibliometric networks specifically |
| **Tulip** | Very large graphs, hierarchy-aware |

For production publication graphics, the typical pipeline is: layout in Gephi or graph-tool → export coordinates → render in matplotlib/ggraph for final polish.

## Reproducibility checklist

When publishing a network plot:
- **Set a random seed** for stochastic layouts; report the seed
- **State the layout algorithm and parameters** (FR, KK, FA2, with iteration counts)
- **State the N, m, density** of the network plotted (not just the original network if backbone was extracted)
- **State the visual encodings** explicitly: "node size is proportional to degree; color is community assignment from Leiden at γ=1.0"
- **Provide the data** (edge list + attributes) for reproducibility

## Common visualization mistakes

- **Plotting the whole network when a metagraph or matrix would work better**: results in hairball
- **Using node radius (instead of area) for size encoding**: visually exaggerates small values
- **Using rainbow / jet colormap for continuous values**: perceptually misleading, fails for colorblind viewers
- **Hairball + no chrome stripping**: keeping labels, axes, gridlines makes it worse
- **Not stating the layout algorithm**: a network looks completely different under FR vs. KK vs. ForceAtlas2; readers can't reproduce
- **Animating temporal networks without stabilization**: node-jumping defeats the purpose
- **Drawing only the giant component without saying so**: misleading about the network's overall structure
- **Treating layout positions as if they have meaning when they don't**: FDL positions are arbitrary up to rotation/reflection; do not annotate "north" and "south" of a hairball

## Canonical references

- Kobourov, S. G. (2014). "Force-directed drawing algorithms." In *Handbook of Graph Drawing and Visualization*.
- Jacomy, M., Venturini, T., Heymann, S., & Bastian, M. (2014). "ForceAtlas2, a continuous graph layout algorithm for handy network visualization." *PLOS ONE* 9: e98679.
- Fruchterman, T. M. J. & Reingold, E. M. (1991). "Graph drawing by force-directed placement." *Software: Practice and Experience* 21: 1129–1164.
- Kamada, T. & Kawai, S. (1989). "An algorithm for drawing general undirected graphs." *Information Processing Letters* 31: 7–15.
- Krzywinski, M., Birol, I., Jones, S. J., & Marra, M. A. (2012). "Hive plots—rational approach to visualizing networks." *Briefings in Bioinformatics* 13: 627–644.
- Both, C. A. et al. (2023). "Accelerating network layouts using graph neural networks." *Nature Communications* 14: 1560.
- Munzner, T. (2014). *Visualization Analysis and Design*. CRC Press. (Chapters 9 on networks)
