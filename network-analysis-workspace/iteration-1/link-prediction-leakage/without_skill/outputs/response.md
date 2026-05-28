# Link Prediction Evaluation: Is Your AUROC = 0.94 Valid?

## Short Answer

Your advisor is almost certainly right. An AUROC of 0.94 on a link prediction task is extremely high, and the most likely explanation is **data leakage caused by random edge splitting**. This is one of the most common — and most consequential — evaluation mistakes in graph machine learning.

---

## The Core Problem: Random Edge Splitting on Graphs

When you randomly split your 300k edges 80/20, you placed ~60k edges in the test set. But those test edges connect nodes that are already in your training graph (just via different edges). This creates several forms of leakage:

### 1. Structural Leakage (the main culprit)

A GNN learns node representations by aggregating neighborhood information. If node A and node B are connected in the test set, but A and B both appear extensively in the training graph — connected to many of the same neighbors — then the model has already "seen" that A and B are structurally close. The test edge is not truly unknown; it's heavily implied by the training structure.

**Example:** In a social network, if A and B share 15 mutual friends in the training graph, a GNN will assign their pair a very high score. The test edge A-B is then "easy" to predict, not because the model generalizes well, but because the training graph already revealed the answer.

This is sometimes called the **"common neighbors leakage"** problem. Many link prediction features (common neighbors, Jaccard coefficient, Adamic-Adar, etc.) and GNN architectures implicitly compute exactly these structural similarities.

### 2. Node Representation Leakage

During training, your GNN learns embeddings for every node in the graph. When you evaluate on a test edge (u, v), both u and v already have trained embeddings — embeddings that were shaped by the full neighborhood structure, which includes indirect signals from the test edge's endpoints. The model isn't predicting truly unseen relationships; it's scoring pairs of nodes it fully understands.

### 3. Negative Sample Contamination

For AUROC, you need negative examples (non-edges). If you sample negatives randomly from all non-existing pairs, many of those negatives will be between nodes that have no structural connection whatsoever — trivially easy to distinguish from test positives that share many common neighbors. This inflates AUROC dramatically.

---

## Why 0.94 Is the Red Flag

Legitimate link prediction benchmarks on real social networks typically yield AUROC in the range of **0.75–0.88** for strong GNN models, depending on the dataset and how carefully the evaluation is constructed. Scores above 0.90 almost always indicate one of:

- Random edge splitting (leakage as described above)
- Trivially easy negative samples
- A dataset with very strong structural signals that doesn't generalize
- Accidentally including test edges in training

---

## How to Validate Your Evaluation

### Step 1: Check your split method

**Bad:** Random 80/20 edge split on a single static snapshot.

**Better:** Temporal split. Since you're predicting friendships in the next 6 months, you should be training on edges that exist at time T and predicting edges that form between T and T+6 months. This is the only split that matches your actual deployment scenario. If you don't have timestamps, you have a fundamental data problem.

**Also better for ablation:** Node-disjoint or inductive split. Hold out a set of nodes entirely from training, and predict edges among/between those held-out nodes. This tests whether your model generalizes to nodes it has never seen, which is often closer to real-world use.

### Step 2: Audit your negative samples

How did you generate negative examples for evaluation?

- **Inflated:** Random non-edges from the entire graph (most non-edges involve structurally distant node pairs)
- **Harder and more realistic:** Negative samples drawn from node pairs at distance 2 (i.e., pairs that share at least one common neighbor). These are structurally similar to positives and much harder to distinguish.

Run your evaluation with distance-2 negatives only. If your AUROC drops substantially (e.g., to 0.70–0.80), that's diagnostic of easy-negative inflation.

### Step 3: Run a structural baseline

Before trusting your GNN score, compute AUROC using only a simple structural heuristic — no learning involved:

- **Common Neighbors score:** score(u,v) = |N(u) ∩ N(v)|
- **Adamic-Adar index**
- **Jaccard coefficient**

If a purely structural heuristic (which requires zero training) achieves AUROC of, say, 0.88, and your GNN achieves 0.94, your GNN is adding only marginal value — and both scores are likely inflated by the same leakage.

### Step 4: Check for temporal validity

For your specific use case (predicting friendships forming in the next 6 months):

- Confirm you have edge timestamps
- Train only on edges with timestamp < cutoff date
- Evaluate only on edges with timestamp in [cutoff, cutoff + 6 months]
- Make sure no future edge information leaks into node features, graph structure, or negative sampling

### Step 5: Degree-stratified analysis

High-degree nodes ("hubs") are easy to predict for: they connect to many nodes, so any new edge from a hub is structurally plausible. Examine your model's performance broken down by node degree:

- If performance is near-perfect for high-degree nodes but poor for low-degree nodes, your model is exploiting popularity bias
- Report performance for the lowest-degree quartile specifically

---

## Concrete Checklist

| Check | What to look for | Red flag |
|---|---|---|
| Split method | Temporal vs. random | Random split on a static snapshot |
| Negative sampling | Distance-2 vs. random non-edges | Random non-edges from full graph |
| Structural baseline | AUROC of common neighbors | Baseline AUROC > 0.85 |
| Degree distribution | Perf by degree bin | Near-perfect on high-degree only |
| Test node overlap | Are test nodes in training graph? | All test nodes have training edges |
| Timestamp leakage | No future info in features | Features computed on full graph |

---

## What a Valid Evaluation Looks Like

For your 6-month friendship prediction task, a rigorous evaluation would:

1. **Split by time:** Train on edges formed before month 0, test on edges formed in months 1–6
2. **Use hard negatives:** Sample test negatives from node pairs at graph distance 2 that did NOT form an edge during the test window
3. **Report realistic metrics:** Expect AUROC in the 0.72–0.85 range for a good model; anything higher deserves scrutiny
4. **Compare to structural baselines:** Show your GNN beats common neighbors or Adamic-Adar by a meaningful margin
5. **Report precision@K:** Since you care about which specific friendships form, precision@K (e.g., for K = 10, 50, 100 candidate pairs per node) is more meaningful than AUROC anyway

---

## Summary

Your advisor is right. AUROC = 0.94 almost certainly reflects structural leakage from random edge splitting, inflated by easy negative samples. The fix is to (a) use a temporal split, (b) use hard negatives (distance-2 non-edges), and (c) compare against a structural baseline. After these corrections, expect your AUROC to drop — but that lower number will actually be meaningful and publishable.
