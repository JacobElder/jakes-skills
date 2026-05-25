# Link Prediction

The task: given an observed network, predict which non-edges will become edges (future links), which observed edges are false positives, or which edges are missing from incomplete data. Different framings have different evaluation protocols and different appropriate methods.

## The three framings (state which one applies)

These have been conflated in published work, leading to incomparable benchmarks.

### 1. Temporal link prediction (forecasting)

Given network at time t, predict edges that will appear at time t+1. **Train / test split by time.** Evaluation: AUROC, average precision (AP) on the t+1 edges vs. negative samples.

This is the cleanest formulation but requires time-stamped data.

### 2. Missing link prediction (recovery)

Given an observed network that is *incomplete* (some edges weren't observed), predict which non-edges are actually missing edges. **Train / test split by randomly hiding edges.** Evaluation: AUROC on hidden vs. non-edges.

This is what most "link prediction benchmarks" measure. It tests whether the model captures the *generative structure* of the network.

### 3. Spurious link detection

Given an observed network with *false* edges, predict which observed edges are wrong. Less common but practically important (e.g., noisy collaboration networks). Different methods needed (Guimerà & Sales-Pardo 2009).

## Heuristic / unsupervised predictors

A node-pair (i, j) is scored; high score = likely link. Many heuristics are well-established and serve as strong baselines.

### Local (neighborhood-based)

- **Common Neighbors**: |N(i) ∩ N(j)|
- **Jaccard**: |N(i) ∩ N(j)| / |N(i) ∪ N(j)|
- **Adamic-Adar** (Adamic & Adar 2003): Σ_{k ∈ N(i) ∩ N(j)} 1/log(k_k). Down-weights popular common neighbors.
- **Preferential attachment**: k_i · k_j
- **Resource allocation** (Zhou, Lu & Zhang 2009): Σ_{k ∈ N(i) ∩ N(j)} 1/k_k. Similar to Adamic-Adar but 1/k instead of 1/log(k); often beats it on dense networks.

NetworkX has all these in `nx.link_prediction`. Adamic-Adar and resource allocation are typically the strongest unsupervised heuristics; they should always be reported as baselines.

### Global / quasi-local

- **Katz index**: Σ_l β^l |paths_l(i,j)| = ((I - βA)^(-1) - I)_{ij}. Aggregates all paths with decay.
- **SimRank** (Jeh & Widom 2002): recursive — i and j are similar if their neighbors are similar
- **Rooted PageRank**: PPR from i, score at j
- **Hitting / commute time**: expected steps for a random walk from i to reach j; commute is symmetric version

These are stronger but more expensive.

## Generative model approaches

Fit a generative network model; score (i,j) by the model's predicted edge probability.

### Stochastic Block Models

SBMs are particularly strong for missing link prediction. Procedure:
1. Remove some edges, fit SBM on the remainder
2. For each non-edge, the model gives a probability based on the block assignment
3. Rank non-edges by predicted probability; the held-out edges should rank high

Hierarchical / nested SBMs (Peixoto 2014) often outperform single-level SBMs because they capture multi-scale structure. **For benchmarks, nested SBM is consistently competitive with or beats GNNs** on link prediction tasks (Ghasemian et al. 2020).

### Hierarchical Random Graph (Clauset, Moore & Newman 2008)

Specifically designed for link prediction. Builds a dendrogram of node groupings; edge probability between two nodes is the parameter at their MRCA in the dendrogram. MCMC over dendrograms. Strong on networks with clear hierarchical structure.

### Latent space models

Hoff et al. (2002, 2005): each node has a position in a latent space; tie probability decreases with distance. R: `latentnet`. Good when the latent structure is well-modeled by a low-dimensional embedding.

### ERGMs for prediction

ERGMs aren't usually used for link prediction (they're for inference), but the fitted model implies tie probabilities. Caveat: ERGMs aren't usually well-calibrated for prediction without specific tuning.

## Supervised / embedding-based approaches

Treat link prediction as binary classification on node pairs.

### Standard pipeline

1. Compute node embeddings (node2vec, DeepWalk, GraphSAGE, GCN, etc.)
2. For each pair (i, j), construct a pair embedding: Hadamard product `h_i ⊙ h_j`, concatenation, or learned bilinear `h_i^T W h_j`
3. Train a classifier (logistic regression, MLP) on positive (edge) and negative (non-edge) pairs

### GNN-specific approaches

**Graph Auto-Encoder (GAE) / Variational GAE** (Kipf & Welling 2016): encode with GCN, decode with inner product. End-to-end trained for link prediction.

**SEAL** (Zhang & Chen 2018): for each target pair (i,j), extract a small subgraph around it, label nodes by their distance to i and j, and classify the subgraph. State-of-the-art on many benchmarks; theoretically motivated by the "γ-decaying heuristic" framework.

**Neo-GNN, NCN, BUDDY** (2022-2023): more recent SOTA architectures specifically for link prediction; learn pair-specific features.

### Why generic GNNs underperform on link prediction

A standard GCN for link prediction encodes each node *independently of the target pair*. But link prediction is fundamentally about *pair* properties: two structurally distinct pairs can have identical pairs of node embeddings. SEAL and successors fix this by making the encoding pair-aware.

## Evaluation: do it right

### Negative sampling

For each positive (held-out edge), sample one or more non-edges as negatives. Several choices, each measuring different things:

- **Random non-edges**: easy negatives; inflates AUROC
- **Non-edges with at least one common neighbor**: harder negatives; tests fine-grained discrimination
- **Non-edges sampled from the same component**: avoids the trivial "obviously disconnected" negatives
- **Stratified by node degree**: prevents methods from winning by simply predicting high-degree pairs

**Hard negatives matter for realistic evaluation.** Most "GNN beats Adamic-Adar" results use random negatives, which inflates the gap; under hard negative sampling, the gap shrinks dramatically (Hu et al. 2020, OGB benchmark).

### Train/val/test edge splits (critical for GNNs)

For GNN-based methods:
- **Train edges**: visible to message passing AND used as positives during training
- **Val edges**: hidden during training; used to tune hyperparameters
- **Test edges**: hidden during training and tuning

The message-passing graph must NOT include val or test edges. PyG's `RandomLinkSplit` handles this correctly; many ad-hoc implementations don't, which leaks information and inflates results.

### Metrics

- **AUROC**: standard, but insensitive to ranking at the top (where action happens)
- **AP (average precision)**: better when positives are rare
- **Hits@K**: fraction of true positives in the top K predictions; what matters for recommendation
- **MRR (mean reciprocal rank)**: average of 1/rank of the first true positive
- **NDCG**: for ranked retrieval

For real applications (recommendation), Hits@K and MRR are the metrics that matter — AUROC can be 0.95 while the top-10 predictions are garbage.

## Cold start

Predicting links for nodes with no observed edges (new users on a platform):
- Pure structural methods fail (no structure to use)
- Need **node features** (text, attributes) to embed cold nodes
- GraphSAGE and other inductive GNNs handle this
- Hybrid models that combine content and structure are standard

## Practical recommendations

| Situation | Recommended approach |
|---|---|
| Small graph, want strong baseline | Adamic-Adar, resource allocation, Katz |
| Medium graph, want best accuracy | Nested SBM (graph-tool) or SEAL |
| Large graph, fast prediction | node2vec + logistic regression on Hadamard pair embedding |
| Cold start (new nodes) | GraphSAGE or hybrid (GNN + content features) |
| Temporal forecasting | TGN, DyRep, or temporal GraphSAGE; or simple time-aware features |
| Bipartite recommendation | Matrix factorization, LightGCN, NCF — link prediction is bipartite ranking |
| Knowledge graph (typed edges) | TransE, RotatE, ComplEx, or RGCN |

## Common link prediction mistakes

- **Comparing to weak baselines**: if your fancy method beats only "common neighbors" but not "Adamic-Adar with hard negatives", you haven't actually shown anything (Ghasemian et al. 2020 made this very clear: many published GNN gains disappear with proper baselines)
- **Leaking test edges into message passing**: easy mistake in PyG/DGL pipelines
- **Using random negative sampling and inflating AUROC**: report hard-negative variants
- **Reporting only AUROC when Hits@K is what matters** for the application
- **Forgetting that link prediction is asymmetric** for directed networks: predicting i→j is different from predicting j→i, and you need to model both
- **Confusing link prediction with link recommendation**: prediction maximizes accuracy on held-out edges; recommendation maximizes user-relevant downstream metrics. They can disagree.
- **Reporting a single train/test split**: variance across splits can be huge; report mean ± SD across 5+ random splits

## Canonical references

- Liben-Nowell, D. & Kleinberg, J. (2007). "The link-prediction problem for social networks." *JASIST* 58: 1019–1031.
- Clauset, A., Moore, C., & Newman, M. E. J. (2008). "Hierarchical structure and the prediction of missing links in networks." *Nature* 453: 98–101.
- Zhou, T., Lü, L., & Zhang, Y.-C. (2009). "Predicting missing links via local information." *European Physical Journal B* 71: 623–630.
- Lü, L. & Zhou, T. (2011). "Link prediction in complex networks: A survey." *Physica A* 390: 1150–1170.
- Ghasemian, A., Hosseinmardi, H., Galstyan, A., Airoldi, E. M., & Clauset, A. (2020). "Stacking models for nearly optimal link prediction in complex networks." *PNAS* 117: 23393–23400.
- Zhang, M. & Chen, Y. (2018). "Link prediction based on graph neural networks." *NeurIPS*.
- Hu, W. et al. (2020). "Open Graph Benchmark: Datasets for machine learning on graphs." *NeurIPS*.
