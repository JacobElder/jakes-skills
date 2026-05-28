# How to Report Louvain Communities in a Co-authorship Network Paper

Your setup — 1200 authors, 4800 edges, 8 communities, modularity Q = 0.67 — is solid. A modularity above 0.6 is generally considered strong evidence of meaningful community structure. Here is a complete guide to reporting, naming, and interpreting your communities.

---

## 1. Report the Detection Method Fully

In your Methods section, include all of the following:

- **Algorithm**: Louvain community detection (Blondel et al., 2008)
- **Resolution parameter**: If you used the default (γ = 1.0), state it. If you tuned it, explain why and how.
- **Software and version**: e.g., `python-louvain` 0.16, NetworkX 3.x, igraph, or whichever you used
- **Random seed or runs**: Louvain is non-deterministic. State how many runs you performed and whether you report the partition from the single best run or a consensus partition across runs.
- **Modularity Q**: Report Q = 0.67 with the formula or citation so readers know which variant you used.

**Example Methods sentence:**

> "Community structure was detected using the Louvain algorithm (Blondel et al., 2008) with default resolution (γ = 1.0), implemented in python-louvain 0.16. We ran the algorithm 100 times with different random seeds and retained the partition with the highest modularity (Q = 0.67). The eight resulting communities ranged from N = [smallest] to N = [largest] authors."

---

## 2. Characterize Each Community Before Naming It

Before assigning a label, extract objective descriptors for each community. For a co-authorship network, the most useful characterizers are:

### A. Size and density
- Number of authors (nodes)
- Internal edge density vs. cross-community edges

### B. Top-cited or most-connected authors
- Degree centrality (who has the most co-authors?)
- Betweenness centrality (who bridges within the community?)
- These high-centrality nodes are often the "anchors" that define the community's identity

### C. Publication venues
- What journals or conferences do members of this community publish in?
- This is often the single most powerful naming signal

### D. Keywords and topics
- If you have author keywords or paper abstracts, run frequency analysis (TF-IDF or simple counts) on terms associated with each community's publications

### E. Institutional or geographic clustering
- Do community members share institutions, departments, or countries?

### F. Temporal trajectory
- When did this cluster form? Is it growing, stable, or declining?

---

## 3. How to Name Communities

Names should be **descriptive, not interpretive** at first — let the data drive the label. Use this three-step process:

**Step 1: Identify the dominant theme.**
Look at the top 3–5 most central authors and the journals/venues where community members publish. A community where 70% of papers appear in *NeuroImage* and *Cerebral Cortex* names itself.

**Step 2: Draft a label.**
Use the format: **[Domain] + [Methodological emphasis]** when possible.

- "Functional MRI Methods" rather than just "Neuroimaging"
- "Clinical Trials — Cardiovascular" rather than just "Cardiology"
- "Computational Social Science — NLP" rather than just "Social Media Research"

**Step 3: Check against outliers.**
Are there authors in the community who do not fit the label? If >15–20% of the community seems off-topic, the community may be a methodological cluster (people who co-author across topics) rather than a topical one. Adjust the name accordingly (e.g., "Quantitative Methods Hub").

---

## 4. Reporting Communities in the Paper

### In the Results section

Present a summary table. Example structure:

| Community | N (authors) | % of network | Key figures | Dominant venues | Label |
|-----------|-------------|--------------|-------------|-----------------|-------|
| C1 | 210 | 17.5% | Author A, Author B | Journal X, Conference Y | Social Network Analysis |
| C2 | 185 | 15.4% | Author C, Author D | Journal Z | Computational Linguistics |
| ... | | | | | |

Then for each community, provide 2–4 sentences of prose interpretation:

> "Community 1 (N = 210, 17.5% of authors) centers on social network analysis methods. Its most central members — [Author A] (degree = 47) and [Author B] (degree = 39) — have extensive co-authorship ties within the community and have published primarily in *Social Networks* and *Network Science*. The community's internal density (0.08) is the highest of the eight communities, suggesting a tightly knit research group with sustained collaboration."

### In the Discussion section

Address three questions:
1. Do the communities align with known disciplinary boundaries, or do they reveal unexpected cross-disciplinary collaboration?
2. What do the bridge authors (high betweenness between communities) represent — intellectual brokers, multi-disciplinary researchers, or methodologists?
3. How does the community structure compare to institutional or departmental affiliations?

---

## 5. Visualize the Communities

A figure is essential. Standard approach:

- **Force-directed layout** (e.g., Fruchterman-Reingold or ForceAtlas2) with nodes colored by community
- Label the 5–10 highest-degree nodes per community
- Use node size ∝ degree or citation count
- If 8 communities produce a crowded figure, consider showing each community in a separate panel in supplementary materials

Tools: Gephi (easiest for publication-quality network figures), NetworkX + matplotlib, or Pyvis for interactive HTML figures.

---

## 6. Address Louvain's Instability

Reviewers familiar with network analysis will ask about this. Louvain is stochastic — two runs can produce different partitions. Address it in one of these ways:

**Option A (minimum bar):** Report that you ran N iterations and the partition is from the run with maximum Q. Report the standard deviation of Q across runs to show Q is stable even if exact partition membership varies.

**Option B (stronger):** Compute a consensus partition. Use the co-occurrence matrix (how often do pairs of authors land in the same community across 100+ runs?) and apply hierarchical clustering to it. This gives a stable, run-independent partition.

**Option C (strongest for a methods-focused paper):** Report normalized mutual information (NMI) between runs to quantify partition stability, and compare your Louvain result to other algorithms (Infomap, Leiden, label propagation) to show robustness.

---

## 7. Caveats to Acknowledge

- **Resolution limit**: Louvain with γ = 1.0 may merge small, tight communities or split large diffuse ones. If some communities seem unexpectedly large or small, mention that you checked sensitivity to γ.
- **Edge definition**: Co-authorship networks have binary or weighted edges. State whether you used binary (co-authored ≥ 1 paper) or weighted (number of co-authored papers) and how this affects interpretation.
- **Isolated authors**: Authors with no co-authorship ties are excluded from meaningful community assignment. Report how many such isolates exist.

---

## 8. Citation Checklist

- Blondel, V.D. et al. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics*, P10008. — **cite for Louvain**
- Newman, M.E.J. & Girvan, M. (2004). Finding and evaluating community structure in networks. *Physical Review E*, 69, 026113. — **cite for modularity Q**
- If you use consensus clustering: Lancichinetti, A. & Fortunato, S. (2012). Consensus clustering in complex networks. *Scientific Reports*, 2, 336.

---

## Quick Checklist Before Submission

- [ ] Methods report algorithm, software, version, random seed handling, and number of runs
- [ ] Q = 0.67 reported with formula citation
- [ ] Summary table with community sizes, key authors, and venues
- [ ] Each community has a prose paragraph with centrality statistics
- [ ] Network figure with communities color-coded
- [ ] Stability of partition addressed (SD of Q across runs at minimum)
- [ ] Resolution parameter stated
- [ ] Caveats about Louvain stochasticity acknowledged
