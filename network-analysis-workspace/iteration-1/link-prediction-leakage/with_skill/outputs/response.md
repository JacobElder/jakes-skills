# Is Your Advisor Right? Yes, and Here Is Why

Your AUROC of 0.94 is almost certainly inflated, and your advisor is correct to be suspicious. The issue is a specific, well-documented methodological error called **test edge leakage into the message-passing graph**. Before explaining the fix, let me situate your setup precisely.

---

## What kind of link prediction problem do you have?

The reference taxonomy has three framings. You need to be clear about which one applies to you:

1. **Temporal link prediction (forecasting):** train on network at time t, predict edges at time t+1. Your framing — "friendships that will form in the next 6 months" — is *temporal*. This is the cleanest formulation but requires time-stamped edges.

2. **Missing link prediction (recovery):** randomly hide edges, predict the hidden ones. This is what your current random 80/20 split measures — but it is **not** what you said you want to measure. Recovery tests whether the model captures the network's generative structure, not whether it forecasts the future.

3. **Spurious link detection:** identify which observed edges are wrong. Not your task.

**The mismatch between your stated goal (forecasting) and your evaluation protocol (missing-link recovery) is itself a validity problem**, separate from the leakage issue. We will return to this.

---

## The core validity problem: test edge leakage

This is the most common error in GNN-based link prediction. Here is exactly what happens.

A GNN learns node representations through **message passing**: each node aggregates features from its neighbors, then its neighbors' neighbors, and so on. The graph that message passing runs on — call it the *message-passing graph* — determines what the GNN sees.

When you do a random 80/20 edge split and then train a GNN:

- **If the message-passing graph contains the test edges**, the GNN has effectively seen the answers during training. The 20% test edges are visible as structure during encoding, so the model is not predicting them from the 80% — it has observed them.
- This inflates AUROC dramatically. Results can jump from realistic values of 0.75–0.85 to values above 0.90, depending on network density and how central the leaked edges are.

PyG's `RandomLinkSplit` handles this correctly **if used properly**, but many custom implementations — and many tutorial-level PyG examples — do not remove test edges from the message-passing graph before encoding.

**How to check whether you have this problem:**

```python
from torch_geometric.transforms import RandomLinkSplit

transform = RandomLinkSplit(
    num_val=0.0,       # or whatever val fraction you use
    num_test=0.2,
    is_undirected=True,
    add_negative_train_samples=True,
    neg_sampling_ratio=1.0
)
train_data, val_data, test_data = transform(data)

# The message-passing graph for the test evaluation is train_data.edge_index
# Test positive edges are in test_data.edge_label_index[test_data.edge_label == 1]
# These two sets must NOT overlap
import torch
train_edges = set(map(tuple, train_data.edge_index.t().tolist()))
test_pos = test_data.edge_label_index[:, test_data.edge_label == 1].t().tolist()
leaked = [e for e in test_pos if tuple(e) in train_edges]
print(f"Leaked test edges: {len(leaked)}")  # Must be 0
```

If `leaked > 0`, your evaluation is invalid.

---

## The second problem: negative sampling

Your AUROC also depends heavily on how you sample the negative examples (non-edges) the model must distinguish from positive test edges.

- **Random non-edges** (the default in most implementations): you draw uniformly from all non-edges. In a 50k-node network with 300k edges, there are ~1.25 billion possible non-edges, and the vast majority are between nodes in different regions of the network with zero structural connection. The model trivially discriminates these from actual edges because they have no common neighbors, no shared block membership, nothing. This produces **inflated AUROC** — you are asking an easy question.

- **Hard negatives** — non-edges with at least one common neighbor, or non-edges within the same connected component, or degree-stratified samples — produce realistic AUROC values that are typically 10–20 points lower than random-negative AUROC for GNNs.

The OGB benchmark (Hu et al. 2020) demonstrated this explicitly: many GNN results that looked impressive under random negatives collapsed under hard negative sampling. **Adamic-Adar with hard negatives frequently outperforms fancy GNNs on random-negative AUROC**, which means the "AUROC = 0.94" number tells you very little about whether your GNN is actually good.

---

## The third problem: your framing is wrong for the goal

You said you want to predict which friendships will form in the **next 6 months**. That is temporal forecasting, not missing link recovery.

- A random 80/20 split trains on a random subset of the *existing* edges and tests on another random subset of *existing* edges. The test edges existed at the same time as the training edges; the model is being asked to "predict" edges that were already formed.
- This measures the model's ability to reconstruct the graph's generative structure — which is fine for evaluating whether a GNN has learned the right inductive biases, but it does **not** measure forecasting ability.

For temporal link prediction, you need:

1. **Time-stamped edges.** If your data has edge timestamps (or even coarse timestamps like "wave 1 edges" vs. "wave 2 edges"), you can do a proper temporal split.
2. **Train on edges formed before time T; test on edges formed after T.** Never mix.
3. **The message-passing graph contains only pre-T edges.** Same leakage concern applies.

If your data has no timestamps, you cannot evaluate temporal link prediction honestly. You can evaluate missing-link recovery, which is a well-defined task — but then your framing should change from "predict future friendships" to "predict missing friendships given partial observation."

---

## How to diagnose and fix your current evaluation

### Step 1: Check for leakage

Run the check above. If you see leaked test edges, fix the split so message passing only sees training edges.

### Step 2: Check your negative sampling strategy

What negatives are you using? If random, re-run with:
- **Within-component negatives**: sample non-edges where both nodes are in the same connected component
- **Common-neighbor negatives**: sample non-edges where |N(i) ∩ N(j)| >= 1

Report AUROC under each strategy. If it drops substantially (say, from 0.94 to 0.78), most of your model's apparent performance was coming from easy discrimination.

### Step 3: Run heuristic baselines

These are required before any GNN result is meaningful:

```python
import networkx as nx

G_train = nx.Graph()
G_train.add_edges_from(train_edges)  # message-passing graph only

# Adamic-Adar on test pairs
preds_aa = dict(nx.adamic_adar_index(G_train, test_pairs))

# Resource allocation
preds_ra = dict(nx.resource_allocation_index(G_train, test_pairs))

# Common neighbors
preds_cn = dict(nx.common_neighbor_centrality(G_train, test_pairs))
```

If Adamic-Adar achieves AUROC = 0.90 and your GNN achieves 0.94, the GNN's advantage is modest and may not justify its complexity. If Adamic-Adar achieves 0.91 and your GNN achieves 0.94, you have a real but small gain. If Adamic-Adar achieves 0.93 under the same conditions, the GNN adds almost nothing.

The Ghasemian et al. (2020) PNAS paper made this point definitively: most published GNN gains over "classical baselines" disappear when the baselines are (a) properly tuned and (b) evaluated under the same negative sampling strategy.

Also run a **nested SBM** (graph-tool) as a generative model baseline — it is consistently competitive with GNNs on link prediction and provides a principled probability estimate for each non-edge.

### Step 4: Report variance across splits

A single 80/20 split is not enough. Run 5–10 random splits (or temporal splits if you have timestamps), report mean AUROC ± standard deviation. Variance across splits on link prediction tasks is often surprisingly large, and a single high result can be a lucky split.

### Step 5: For real temporal forecasting, use the right evaluation

If timestamps are available:

```python
# Temporal split
T_cutoff = ...  # some timestamp
train_edges = [(u, v) for u, v, t in edge_list if t < T_cutoff]
test_edges  = [(u, v) for u, v, t in edge_list if t >= T_cutoff]

# Message passing graph: train_edges only
G_mp = nx.Graph()
G_mp.add_edges_from(train_edges)

# For each test edge, score using heuristics on G_mp
# or embed nodes using only G_mp
```

For temporal GNN approaches specifically, TGN (Temporal Graph Network, Rossi et al. 2020) and DyRep are designed for this framing and handle the temporal leakage issue correctly.

---

## What a realistic AUROC looks like

For context on your 50k node / 300k edge network:

- Under **random negative sampling with no leakage**: AUROC of 0.85–0.92 for a well-implemented GNN is plausible. 0.94 is on the high end but not impossible.
- Under **hard negative sampling**: expect AUROC to drop 10–20 points. AUROC of 0.75–0.85 is realistic for a genuinely good model.
- **Adamic-Adar under random negatives**: often 0.85–0.92 on sparse social networks — competitive with or better than a basic GNN.
- If you have leakage: any number is possible, and 0.94 is entirely consistent with a broken evaluation.

---

## Summary checklist

Before trusting your result, verify every item:

| Check | How to verify | Common finding |
|---|---|---|
| Test edges not in message-passing graph | Compute set intersection (code above) | Often fails in custom PyG implementations |
| Negative sampling strategy | Inspect your data loader | Usually random; rarely hard |
| Heuristic baselines run | Adamic-Adar, resource allocation on same splits | Often competitive with GNN |
| Multiple splits reported | Mean ± SD across 5+ splits | Single split result is unreliable |
| Correct framing for goal | Is your split temporal or random? | Mismatch is common |
| Appropriate metrics | AUROC + AP + Hits@K | AUROC alone is insufficient for recommendation use-case |

---

## Canonical references

- Hu, W. et al. (2020). "Open Graph Benchmark." *NeurIPS*. — The gold standard for how to evaluate GNNs on link prediction properly.
- Ghasemian, A. et al. (2020). "Stacking models for nearly optimal link prediction." *PNAS* 117: 23393–23400. — Shows that classical baselines dominate many GNN results when evaluation is done correctly.
- Zhang, M. & Chen, Y. (2018). "Link prediction based on graph neural networks (SEAL)." *NeurIPS*. — State-of-the-art that correctly handles pair-aware encoding.
- Liben-Nowell, D. & Kleinberg, J. (2007). "The link-prediction problem for social networks." *JASIST* 58. — Original formulation and baselines.
