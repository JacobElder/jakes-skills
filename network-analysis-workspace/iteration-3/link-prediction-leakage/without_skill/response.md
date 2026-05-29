# Link Prediction Evaluation: Is AUROC 0.94 Too Good to Be True?

Your advisor is almost certainly right to be skeptical. An AUROC of 0.94 on a random edge split for link prediction is a strong signal that your evaluation has a data leakage problem — specifically, **transductive leakage from the graph structure itself**.

---

## The Core Problem: Random Edge Splits Leak Structural Information

When you train a GNN on 80% of edges and evaluate on the remaining 20%, the test edges are not truly unseen. Here is why:

**The graph the model sees during training is structurally entangled with the test edges.** The training graph includes edges that are neighbors of your test edges — nodes that appear in test edges still have their training-set connections visible. A GNN aggregates neighborhood features across multiple hops, so node embeddings learned during training are heavily shaped by the neighborhood structure that partially encodes the existence of test edges.

Put concretely: if node A and node B share many common neighbors in the training graph, those common neighbors were only present in the training graph *because* you kept 80% of edges. Some of those common neighbors may themselves be edges that, together with the test edge A-B, form triangles. The GNN learns that triangle closure is a strong predictor — and it is, trivially, because the triangle information is already in the training graph.

This is sometimes called **neighborhood overlap leakage** or **transductive leakage**.

---

## Why This Inflates AUROC So Dramatically

Link prediction performance has a known baseline: even simple heuristics like Common Neighbors, Jaccard Coefficient, or Adamic-Adar achieve high AUROC on random splits of most social networks. Social networks have high clustering coefficients, meaning most real edges close triangles. If your test edge exists in the ground truth, it almost certainly has many common neighbors visible in the training graph — information that would not exist in a truly predictive scenario.

The result is that you are not measuring "can the model predict future friendships?" You are measuring "can the model identify edges that were arbitrarily held out from a dense neighborhood?" These are very different tasks.

---

## How to Detect Whether You Have This Problem

Run these sanity checks:

**1. Compare against structural heuristics.** Compute Common Neighbors, Jaccard, and Adamic-Adar on the same 80/20 split and measure their AUROC. If these simple heuristics also score 0.85+, your GNN is not learning anything beyond local structure that is already trivially available — confirming leakage.

**2. Check neighborhood overlap in test edges.** For each held-out (positive) test edge (u, v), compute how many common neighbors u and v have in the *training graph*. If positive test edges have systematically higher common-neighbor counts than negative (non-edge) test pairs, the split is not clean.

**3. Try a temporal split instead.** If you have any timestamp or ordering information on edges, split by time. Train on all edges formed before month T, evaluate on edges formed after month T. Realistic AUROC on temporal splits for social networks is typically 0.60–0.80, depending on the dataset and method. If your AUROC drops substantially under temporal splitting, that gap is the magnitude of your leakage.

**4. Check negative sampling.** How are you generating negative examples (non-edges) for evaluation? If you are sampling negatives uniformly at random from all non-edges, many of those negatives are between nodes with no structural relationship whatsoever. This makes the task easier — the model just has to distinguish "nodes with shared neighbors" from "nodes that barely interact." A harder, more realistic negative set would sample negatives that have some proximity in the graph (e.g., two-hop neighbors that did not form an edge).

---

## How to Fix Your Evaluation

### Option 1: Temporal Split (Strongest Fix)

If your dataset has edge timestamps, this is the gold standard for link prediction in social networks:

- Training set: all edges with timestamp < T
- Validation/test set: edges with timestamp >= T

This directly mirrors the real prediction task (predicting future links) and prevents any structural leakage, because the training graph is built only from past interactions.

### Option 2: Inductive Node Split

Hold out a set of nodes entirely from training (along with all their edges). At test time, evaluate the model's ability to predict edges involving these unseen nodes. This is a stricter test of generalization and avoids the transductive leakage problem, though it tests a somewhat different capability (generalizing to new nodes vs. new edges).

### Option 3: Stronger Negative Sampling

If you must use a random edge split, at minimum:

- Use hard negatives: sample negative pairs from nodes that are 2-hop neighbors but not directly connected, rather than uniform random non-edges.
- Report performance separately for "hard" and "easy" negatives.
- Compare against structural heuristic baselines on the same split.

### Option 4: Double-Check Your Negative Sampling Ratio

Confirm your evaluation set has a realistic positive-to-negative ratio. Many implementations default to 1:1, which inflates AUROC relative to the real-world setting where negatives vastly outnumber positives. This is less severe than the structural leakage issue but worth checking.

---

## What Realistic Performance Looks Like

For reference:
- On standard benchmarks like OGB-collab or SNAP social network datasets with proper temporal or inductive splits, strong GNN methods typically achieve AUROC in the range of 0.60–0.85.
- On random splits of the same datasets, it is common to see 0.90+ even with simple methods — this is the leakage inflating the numbers.
- If a temporal split drops your AUROC from 0.94 to something in the 0.65–0.75 range, that is a normal and expected result, not a failure of your model.

---

## Summary

Your advisor is right to flag this. The likely culprit is that a random edge split on a social network allows the GNN to exploit neighborhood structure that trivially signals held-out edges, because those edges were part of the same dense clusters as your training edges. This is not a bug you wrote — it is a fundamental property of random splits on transductive graph data, and it is one of the most common evaluation mistakes in the link prediction literature.

The fix is to either (a) use a temporal split if you have timestamps, or (b) carefully evaluate against structural baselines to quantify how much of your performance is attributable to simple neighborhood overlap rather than anything the GNN learned. Either way, your model may still be genuinely useful — but you will have a much more defensible claim about what it is actually predicting.
