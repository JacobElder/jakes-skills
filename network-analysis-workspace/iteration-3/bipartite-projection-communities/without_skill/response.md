# Bipartite Projection + Louvain Community Detection

Your overall plan is sound and a common approach for this kind of problem. A few things worth knowing before you run it.

## Your plan is reasonable, but watch for information loss

Projecting a bipartite graph onto one mode (employees) and then running community detection is the standard workflow. The weight = number of shared projects is intuitive and easy to implement with `nx.bipartite.weighted_projected_graph`. That said, raw co-participation counts have a known bias: prolific participants inflate edge weights. An employee on 50 projects will share edges with many people simply because of volume, not because they collaborate tightly with any of them.

## Consider normalizing edge weights before running Louvain

Two common normalizations:

**Jaccard similarity** — shared projects / union of projects between the two employees. This penalizes pairs where one person is on many more projects than the other.

**Hyperbolic weighting (Newman)** — for each project, each pair of co-participants gets a weight contribution of 1/(k-1) where k is the project size. Large all-hands projects contribute less than small focused ones. NetworkX has this built in: `nx.bipartite.collaboration_weighted_projected_graph`.

For 800 employees and 150 projects, the raw count projection will likely produce a very dense graph (most employees share at least one project), which can make Louvain produce trivial or noisy partitions. Normalization or thresholding the edge list first usually gives cleaner communities.

## Louvain is a fine choice, but check your library

NetworkX itself does not ship Louvain. You are probably using `python-louvain` (the `community` package) or `networkx`'s `louvain_communities` function added in NetworkX 3.0. They use slightly different APIs and resolution parameters — make sure you know which one you have.

The resolution parameter (often called `resolution` or `gamma`) controls community granularity. At default resolution you may get a small number of large communities. It is worth sweeping over a few values (e.g., 0.5, 1.0, 1.5, 2.0) and inspecting the partition sizes to see what granularity makes sense for your use case.

## A few practical checks to run

1. **Check the projection density** — `nx.density(projected_graph)`. If it is above ~0.3 or 0.4 you probably need to threshold or normalize before community detection.

2. **Check for isolates** — employees who never shared a project with anyone will appear as isolated nodes. Decide whether to include or exclude them before running Louvain.

3. **Validate with modularity** — `community.modularity(partition, projected_graph, weight='weight')` gives you a quality score. Values above ~0.3 indicate meaningful structure.

4. **Consider running Louvain multiple times** — the algorithm is stochastic. Run it 10–20 times and either pick the highest-modularity partition or look for consensus across runs if stability matters.

## Alternative to consider: direct bipartite community detection

If you want to avoid projection entirely, algorithms like the Barber bipartite modularity method or spectral approaches on the bipartite adjacency matrix can find communities without collapsing the structure. This is more work to implement in NetworkX but avoids the information loss from projection. For most applied use cases the projection approach is fine, especially with normalized weights.

## Summary

Your plan is a standard, defensible approach. The main refinement I would suggest: use `collaboration_weighted_projected_graph` (Newman hyperbolic weighting) instead of raw co-participation counts, optionally threshold weak edges, and sweep the Louvain resolution parameter rather than trusting the default. That combination will give you more meaningful employee communities than raw weighted projection at default settings.
