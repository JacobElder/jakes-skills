# Validation & diagnostics

The discipline that separates real DR work from pretty pictures. **Every embedding you produce or
interpret gets validated quantitatively.** The bundled `scripts/dr_diagnostics.py` computes the
core metrics; this file explains what they mean, what good looks like, and the traps.

---

## Why this matters

The seductive failure mode is to tune the method until the 2D plot "looks right," then narrate the
plot as a finding. That is circular — for almost any dataset you can find a perplexity / n_neighbors /
seed / method that shows you clusters you wanted to see. Quantitative neighbourhood-preservation
metrics make the claim **falsifiable**: either the embedding preserves the structure of the original
space or it doesn't, independent of how appealing it looks.

## The core metrics (computed by the script)

**Trustworthiness.** Penalizes *false neighbours*: points that look close in the embedding but are
not close in the original space. Low trustworthiness = the embedding invented structure. (sklearn:
`manifold.trustworthiness`.)

**Continuity.** The dual: penalizes *missing neighbours* — points close in the original space that
the embedding tore apart. Low continuity = the embedding destroyed real structure. (Computed as
trustworthiness with the spaces swapped.)

**kNN overlap / preservation@k.** For each point, the fraction of its k original-space neighbours
that remain neighbours in the embedding, averaged. Intuitive and directly tied to "can I trust local
neighbourhoods here."

**Shepard correlation** (Pearson & Spearman between high-dim and low-dim pairwise distances). This is
the quantitative form of "you can't read distances off a t-SNE/UMAP plot." A **low Shepard
correlation is expected** for t-SNE/UMAP and is the proof you cite when telling someone their
inter-cluster gaps are artifacts. PCA/MDS should score high here.

**Rough reading of values** (data-dependent; calibrate against a PCA baseline on the same data):
- Trustworthiness / continuity > ~0.95 strong, 0.90–0.95 okay, < 0.90 suspect for fine structure.
- Shepard Spearman > ~0.7 means distances are fairly meaningful; < ~0.4 means they're not — interpret
  the plot as topology-only.
- Always report the metrics **alongside** the picture, never the picture alone.

## Label-based checks (when you have labels)

If classes/clusters are known, the script reports k-NN classification accuracy in **both** the
original space and the embedding.

**The critical trap (Chari & Pachter and its rebuttals).** People "validate" an embedding by showing
the known labels separate cleanly in 2D. But (a) if you computed the labels *by clustering the same
data*, clean separation is guaranteed and circular; and (b) if embedding accuracy *exceeds*
original-space accuracy, that's a warning sign the method is **manufacturing** separation, not
revealing it — not a triumph. Always compare against the signal that genuinely exists in the
original/PCA space. Silhouette score has the same circularity hazard: a high silhouette in the
embedding mostly reflects the algorithm's density-equalizing, not real cluster validity — prefer
silhouette computed in the original space.

## Other diagnostics worth knowing

- **Co-ranking matrix** and its derived Q_NX / quality curves — a more complete picture of
  neighbourhood preservation across all k at once (intrusions vs extrusions). Use when a single k is
  too coarse.
- **Scree / cumulative explained variance** (PCA): the right way to pick d and to sanity-check before
  any nonlinear method.
- **Reconstruction error** (PCA, NMF, autoencoders): how much information the embedding throws away.
- **Stability across seeds/parameters:** run the embedding ≥2 seeds and ≥2 hyperparameter settings;
  quantify agreement (e.g. Procrustes distance between embeddings, or label stability). A conclusion
  that doesn't survive a seed change isn't a conclusion.
- **Downstream task performance:** for *compression* (job 1), the only validation that ultimately
  matters is whether the reduced features help the downstream model on held-out data — validate there,
  not on neighbour metrics.

## Using the script

```bash
# CLI
python scripts/dr_diagnostics.py --hd X.npy --ld embedding.npy --labels y.npy --k 15 --out report.json

# in-process
from dr_diagnostics import diagnose
report = diagnose(X_highdim, Y_embedding, labels=y, k=15)
print(report["interpretation"])   # plain-language flags
```

It returns trustworthiness, continuity, kNN overlap, Shepard Pearson/Spearman, optional label k-NN
accuracy in both spaces, and a list of plain-language interpretation flags. Prefer it over
hand-rolled metrics so results stay consistent across analyses and so the circularity checks (e.g.
the LD-beats-HD warning) are applied every time.

## What to actually tell the user

A good DR report says, in order: which **job** this was; what **preprocessing** (standardization,
PCA-to-d); which **method** and **hyperparameters** (and that you scanned several); the **diagnostic
numbers**; and then the interpretation **with the caveats stated** (sizes/distances if it's
t-SNE/UMAP). The picture goes last and is labeled as a hypothesis-generating visualization, not a
result.

---

## Sources / further reading

- Trustworthiness & continuity: Venna & Kaski, "Neighborhood preservation in nonlinear projection
  methods," (2001) and subsequent work.
- Co-ranking matrix / Q_NX quality curves: Lee & Verleysen, "Quality assessment of dimensionality
  reduction: Rank-based criteria," *Neurocomputing* (2009).
- The circularity / label-leakage cautions: Chari & Pachter, *PLOS Comp Biol* (2023) and its
  rebuttals; the broader point that silhouette/kNN computed *on* an embedding can reward the
  algorithm's density-equalizing rather than real structure.
