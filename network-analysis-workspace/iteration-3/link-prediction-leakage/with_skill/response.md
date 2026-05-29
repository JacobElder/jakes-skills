# Link Prediction Evaluation: Is Your AUROC = 0.94 Real?

Your advisor is almost certainly right to be skeptical. A random edge split on a graph network is the single most common source of inflated AUROC in GNN link prediction — and 0.94 is a signature number for it. Here is exactly what is going wrong and how to fix it.

---

## Your network, characterized

Before diagnosing the evaluation, let's fix the type:

- **Mode**: one-mode (person-to-person friendship)
- **Directionality**: likely undirected (friendships are typically symmetric), but confirm whether your data captures direction
- **Scale**: large (~50k nodes, ~300k edges; density ≈ 300k / (50k × 49,999 / 2) ≈ 0.00024)
- **Time**: you have a temporal framing (predicting friendships in the next 6 months), which is the most important structural fact about your task

This matters because you are doing **temporal link prediction** (framing 1 in the reference taxonomy), not missing link recovery (framing 2). That distinction changes both your split strategy and your baseline comparisons.

---

## What is wrong with your evaluation

There are two separate problems. Either one alone could inflate AUROC significantly; you likely have both.

### Problem 1: Message-passing leakage from a random edge split

When you randomly split edges 80/20, the 20% test edges are *not* removed from the graph before training the GNN. Here is the mechanism:

- A GNN encodes each node by aggregating messages from its neighbors
- If test edge (A, B) is present in the training adjacency matrix during message passing, node A's embedding encodes information about B's neighborhood, and vice versa
- When you then ask "will A and B connect?", the GNN already knows they are connected — it was in the training graph

This is not a subtle effect. The test edges are still visible to the encoder. The AUROC you are measuring is roughly: "can the GNN decode information it was already given?" — not "can it predict future links?"

**The fix**: the message-passing graph must have *all* test and validation edges removed before any node embedding is computed. In PyG, this is:

```python
from torch_geometric.transforms import RandomLinkSplit

transform = RandomLinkSplit(
    num_val=0.05,
    num_test=0.20,
    is_undirected=True,   # critical for undirected friendships
    add_negative_train_samples=True,
)
train_data, val_data, test_data = transform(data)

# train_data.edge_index  → message-passing graph (train edges only)
# train_data.edge_label_index → supervision edges for training
# test_data.edge_label_index  → test edges (NEVER in message passing)
```

If you implemented your own split and passed the full adjacency to the GNN encoder, you need to redo the experiment with a masked split. The drop from 0.94 to the corrected number is typically 10–20 AUROC points.

### Problem 2: Easy random negatives inflate the absolute AUROC number

When you sample negatives for AUROC computation, how did you pick non-edges? If you sampled uniformly at random from all non-edges, most of your negatives are pairs of nodes with no common neighbors, in different communities, possibly in different components — these are trivially easy to distinguish from real friendships. The model gets credit for correctly assigning low scores to pairs that are obviously not going to connect, which inflates the AUROC.

For social friendship prediction, realistic negatives are pairs with at least one common friend (distance-2 non-edges). These are the pairs that *could* realistically become friends but didn't. A model that only gets these right is genuinely predicting social dynamics.

**The fix**: use **hard negatives** — non-edges that share at least one common neighbor:

```python
import networkx as nx

G_train = nx.Graph()
G_train.add_edges_from(train_edges)

# Candidate hard negatives: pairs with common neighbors but no edge
hard_negatives = []
for u, v, _ in nx.adamic_adar_index(G_train, ebunch=None):
    # nx.adamic_adar_index iterates over non-edges with shared neighbors
    if not G_train.has_edge(u, v):
        hard_negatives.append((u, v))
```

Or more simply, sample negatives from node pairs at graph distance exactly 2 (one hop away from being connected). Alternatively, stratify by degree to prevent the model from winning by predicting high-degree pairs.

---

## How to know if your evaluation is valid

Work through this checklist before trusting any AUROC:

**Split validity**
- [ ] Are test edges completely absent from the message-passing adjacency during GNN encoding?
- [ ] Are validation edges also absent (not just test edges)?
- [ ] If you implemented the split yourself rather than using PyG's `RandomLinkSplit`, did you pass a separate `edge_index` (training edges only) to the encoder vs. the full data object?

**Temporal validity** (because your framing is forecasting)
- [ ] Did you split by time, not randomly? All edges formed before time T go to train; all edges formed in the 6-month window go to test. A random split allows future edges to inform training, which is another form of leakage.
- [ ] Does your negative sampling draw non-edges *at the time of evaluation*, not from the final snapshot?

**Negative sampling validity**
- [ ] Are you using hard negatives (distance-2 pairs) rather than random non-edges?
- [ ] Have you stratified by degree?

**Baseline sanity check** (the single most informative diagnostic)
- [ ] Have you computed Adamic-Adar on the training graph and measured its AUROC on the same test set?

The Adamic-Adar baseline is critical. If your GNN scores 0.94 and Adamic-Adar scores 0.91, the GNN isn't adding much. If Adamic-Adar also scores 0.94, that is strong evidence the task is trivially easy with the negatives you chose — because Adamic-Adar has no parameters and cannot overfit.

```python
from networkx.algorithms.link_prediction import adamic_adar_index
from sklearn.metrics import roc_auc_score

# Score all test pairs
test_pairs = list(zip(test_pos_edges + test_neg_edges))
scores = {(u, v): s for u, v, s in adamic_adar_index(G_train, test_pairs)}
y_true = [1] * len(test_pos_edges) + [0] * len(test_neg_edges)
y_score = [scores[(u, v)] for u, v in test_pairs]
print("Adamic-Adar AUROC:", roc_auc_score(y_true, y_score))
```

If Adamic-Adar AUROC is also very high (say, above 0.88), your negative samples are still too easy. If Adamic-Adar is around 0.70–0.80 and your GNN is at 0.94 under a proper temporal split with hard negatives, that is a genuinely strong result.

---

## The correct evaluation pipeline for your task

Because you are doing temporal forecasting, the right evaluation architecture is:

1. **Temporal split**: train on edges formed before cutoff T; test on edges formed in the 6-month window after T. This is the only way to simulate real deployment.

2. **Message-passing graph = training edges only**: pass only train-period edges to the GNN encoder. Val and test edges are supervision-only, never in the adjacency.

3. **Negative sampling**: sample non-edges at-time-T with at least one common neighbor (distance-2 pairs), stratified by degree.

4. **Metrics beyond AUROC**: for friend recommendation on a social platform, AUROC is not the operational metric. Report:
   - Hits@10 or Hits@50: what fraction of new friendships were in your top predictions?
   - Average Precision: better than AUROC when positives are rare
   - MRR: mean reciprocal rank of the first correct prediction

5. **Baselines to beat**: Adamic-Adar and Resource Allocation (Zhou, Lu & Zhang 2009) on the same temporal split and same hard negatives. These have zero parameters and often match GNN performance under fair evaluation (Ghasemian et al. 2020, PNAS 117: 23393–23400 showed this rigorously — many published GNN link-prediction gains disappear with proper baselines and harder negatives).

---

## Bottom line

Your advisor is right. The AUROC = 0.94 is almost certainly inflated by one or both of:

1. **Test edges visible during GNN message passing** (classic random-split leakage) — the most likely culprit, and correcting it typically drops AUROC 10–20 points
2. **Trivially easy random negatives** — correcting this can drop AUROC another 5–15 points

Fix the split first (use PyG's `RandomLinkSplit` correctly, or implement a temporal split), then switch to hard negatives, then rerun with Adamic-Adar as a baseline. Once you have those numbers, you will know whether your GNN is doing something real.
