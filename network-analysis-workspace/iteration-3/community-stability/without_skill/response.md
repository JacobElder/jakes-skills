# Reporting Louvain Communities in a Co-Authorship Network Paper

Your setup — 1,200 authors, 4,800 edges, 8 communities, Q = 0.67 — is solid. A modularity of 0.67 is genuinely high (anything above 0.3 is conventionally considered meaningful; above 0.6 is strong). Here is how to report it rigorously.

---

## 1. Before You Name Anything: Characterize Each Community Structurally

Run the following before writing prose descriptions:

**Size distribution.** Report the number of authors in each community. Unequal sizes are normal, but if one community contains 60% of nodes, your algorithm may have over-split the rest.

**Internal density vs. external connectivity.** For each community C, compute:
- Internal edge density: edges within C / possible edges within C
- Fraction of each node's edges that stay within C (the "embeddedness" score)

**Hub/core nodes.** Identify the top-3 to top-5 highest-degree nodes inside each community. These are usually the intellectual anchors and will drive your naming.

**Bridge nodes.** Find authors with high betweenness centrality who span community boundaries. They are worth naming explicitly in the text — they signal interdisciplinary linkage.

---

## 2. Name Communities by Intellectual Content, Not by Topology

A community label like "Community 3 (n = 187, Q contribution = 0.11)" is necessary but not sufficient. Readers want to know what the cluster *means*. Here is the naming workflow:

**Step 1 — Extract the anchor authors.** Look at the 5–10 highest-degree authors in each community. Look up their primary research areas.

**Step 2 — Extract the anchor papers/venues.** If you have edge weights derived from shared publications, identify the most common journals or conference venues within each community. These usually name the subfield for you.

**Step 3 — Apply a label at the right level of abstraction.** Labels should be:
- Descriptive of a research topic, not a person ("Cognitive Neuroscience of Memory" not "Smith et al. group")
- Consistent in grain size — don't mix "fMRI Methods" with "Neuroscience"
- Provisional — note that labels are interpretive, not ground truth

**Step 4 — Check label validity.** Ask one or two domain experts not involved in the study whether the labels match their intuition. One sentence in your methods section acknowledging expert validation goes a long way.

---

## 3. How to Report Modularity

Do not just say "modularity = 0.67." Report the full context:

```
We detected 8 communities using the Louvain algorithm (Blondel et al., 2008)
with resolution parameter γ = 1.0 (default). Modularity Q = 0.67.
To assess stability, we ran the algorithm 100 times with different random seeds
and computed the normalized mutual information (NMI) between each pair of
partitions; mean NMI = [X], indicating [high/moderate] partition stability.
Community sizes ranged from [n_min] to [n_max] authors (median = [n_med]).
```

This template forces you to confront the key caveat: **Louvain is non-deterministic.** If you run it once and report Q = 0.67, a reviewer will ask whether this is the lucky run. Robustness across seeds is the answer.

---

## 4. The Standard Table

Include a table with one row per community. Minimum columns:

| Community label | n (authors) | % of network | Top-5 hub authors | Representative journals/venues | Modularity contribution |
|---|---|---|---|---|---|

The "modularity contribution" column is the sum of (A_ij - k_i k_j / 2m) for edges within community C, divided by 2m. Most implementations return this per-community if you ask.

---

## 5. Visualization

A force-directed layout (e.g., Fruchterman-Reingold or ForceAtlas2) with nodes colored by community is standard. Practical tips:

- Use a colorblind-safe palette (ColorBrewer is the reference)
- Size nodes by degree or publication count, not uniformly
- Label only the top-3 hub nodes per community — labeling everyone creates a hairball
- If the graph is dense, show a "community condensation" view: collapse each community to a single node, sized by community size, with edge weights representing inter-community edge counts

---

## 6. Caveats to Acknowledge in the Paper

**Resolution limit.** Louvain with γ = 1.0 may merge small but cohesive clusters and may miss structure within large communities. If any community has more than ~400 nodes, consider whether it warrants recursive partitioning.

**Temporal stability.** Co-authorship networks change. If your edge list spans a long time window (e.g., 1990–2025), communities may reflect past collaborations that have dissolved. Mention your time window and consider whether a temporal network analysis is warranted.

**The naming is interpretive.** A sentence like "Community labels were assigned by the research team based on the primary research areas of hub authors and the most common publication venues; they represent post-hoc characterizations, not ground truth categories" is standard and protects you from reviewer objections.

**Multiple runs.** As noted above, run the algorithm at least 50–100 times. Report both the best Q and the distribution of Q values. If Q varies widely across runs, your partition is unstable and the 0.67 figure is misleading.

---

## 7. Example Write-Up Fragment

> "We applied Louvain community detection (Blondel et al., 2008; resolution γ = 1.0) to the co-authorship network (1,200 authors, 4,800 edges), yielding 8 communities with modularity Q = 0.67. To assess partition robustness, we repeated the procedure 100 times with independent random seeds; mean normalized mutual information across run pairs was 0.91 (SD = 0.04), indicating high stability. Community sizes ranged from 47 to 312 authors. We labeled each community by the dominant research topics of its five highest-degree members and the most frequently shared publication venues (Table 2). Community labels were confirmed by two independent domain experts. Four communities corresponded to distinct methodological traditions (e.g., 'Bayesian Cognitive Modeling,' 'EEG/ERP Methods'), while two reflected topical areas ('Decision Neuroscience,' 'Language and Reading'). Two smaller communities (n < 60) showed high inter-community connectivity and appear to represent bridging subgroups rather than isolated research silos."

---

## Key References to Cite

- Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*, 2008(10), P10008.
- Newman, M. E. J. (2006). Modularity and community structure in networks. *PNAS*, 103(23), 8577–8582.
- Lancichinetti, A., & Fortunato, S. (2012). Consensus clustering in complex networks. *Scientific Reports*, 2, 336. — This is the key reference for the consensus/stability approach.
- For NMI as a stability metric: Danon, L., et al. (2005). Comparing community structure identification. *Journal of Statistical Mechanics*, P09008.
