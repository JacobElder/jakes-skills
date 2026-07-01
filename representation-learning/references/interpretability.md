# Interpreting Representations: Probing, Superposition, SAEs, Steering

How to find out what a representation encodes — and the crucial difference between *what's decodable* and *what's used*.

## Contents
1. The decodability vs use distinction (read this first)
2. Linear probing done right (selectivity, control tasks)
3. Causal methods (amnesic probing, activation patching)
4. Superposition
5. Sparse autoencoders
6. Representation engineering / steering vectors
7. Representational similarity (CKA/RSA) recap

---

## 1. The decodability vs use distinction (read this first)

The error that defines shallow interpretability: **"a probe decodes feature F with 95% accuracy, therefore the model uses F."** False. A probe measures whether F is **linearly decodable** from the representation — *accessibility*, not *reliance*. A representation can linearly encode a feature the model never reads downstream, and can use a feature a *linear* probe can't extract (it's there nonlinearly). Three different questions, three different tools:
- **Is F present (decodable)?** → a probe's accuracy, *with a control* (§2).
- **Is F present beyond what the probe could memorize?** → **selectivity** / control tasks.
- **Does the model causally use F?** → **intervention** (§3), never a probe alone.
Insisting on this distinction is the single highest-signal move in any interpretability discussion.

## 2. Linear probing done right

- A **linear probe** = train a linear classifier on frozen representations to predict property F. Linear (not MLP) on purpose: you want to measure what's *linearly accessible*, and a powerful probe can learn the task itself, telling you about the probe rather than the representation.
- **Control tasks / selectivity (Hewitt & Liang 2019):** also train the probe on a *random* labeling of the same inputs. **Selectivity = real-task accuracy − control-task accuracy.** High probe accuracy with high control accuracy means the probe is just memorizing — selectivity, not raw accuracy, is the evidence that the representation encodes F. Always pair a probe with a control.
- **Probe expressivity trap:** an MLP probe scoring high tells you almost nothing (it could learn F from scratch). If you must use a nonlinear probe, report the control.
- **Use linear probing for representation *evaluation*** too (frozen-feature transfer accuracy) — see `evaluation.md`.

## 3. Causal methods (you need these for "use")

- **Amnesic probing (Elazar et al. 2021) / INLP (Iterative Nullspace Projection, Ravfogel et al. 2020):** *remove* a feature from the representation by iteratively projecting out the directions a linear probe uses, then measure whether the downstream behavior changes. If erasing F from the representation degrades the model's task, F was *used*. (Concept erasure has sharper successors: **R-LACE** (Ravfogel et al. 2022), **LEACE** (Belrose et al. 2023) — closed-form/optimal erasure.)
- **Activation patching / causal tracing:** run the model on a corrupted input, then *patch in* a clean activation at a specific layer/position and see if the correct behavior is restored — localizes *where* a representation causally matters. The backbone of circuit-level mechanistic interpretability.
- **Steering as a causal test (§6):** adding a direction and observing a behavior change is itself evidence of causal use.

## 4. Superposition

Models represent **more features than they have dimensions** by assigning each feature a *direction* (not a dedicated neuron); features that rarely co-occur can share dimensions with little interference (Elhage et al. 2022, *Toy Models of Superposition*). Consequences:
- **Polysemantic neurons:** a single neuron activates for several unrelated concepts → reading neurons directly is misleading.
- Features live in **near-orthogonal directions** in activation space, not axis-aligned — so the natural unit of analysis is a *direction*, not a *neuron*.
- Superposition is *why* SAEs exist: to recover the overcomplete set of feature directions the model packed in.
- The **linear representation hypothesis** (features = linear directions, concepts composed additively) underlies steering and SAEs; it holds well empirically for many features but isn't universal (some features are nonlinear / multi-dimensional, e.g. circular day-of-week representations).

## 5. Sparse autoencoders

**Goal:** decompose a dense, superposed activation vector into a **sparse, overcomplete** set of interpretable features. An SAE is a wide autoencoder (dictionary size ≫ model dim) with an L1 (or top-k / JumpReLU) sparsity penalty, trained to reconstruct activations using few active features at a time; the learned dictionary directions are often **monosemantic** (Anthropic's *Towards Monosemanticity* 2023; *Scaling Monosemanticity* 2024 found millions of features in production-scale models).
Honest status — state both the promise and the caveats:
- **Promise:** disentangles polysemantic activations into human-interpretable features you can find, label, and *steer* with (clamp a feature up/down → behavior changes, a causal test).
- **Caveats / open problems:** **reconstruction fidelity ≠ faithfulness** (low recon loss doesn't prove the features are the model's "real" computational units); **feature splitting** (wider SAEs split one concept into many — feature count is partly an artifact of dictionary size); SAEs may **miss features** the model uses and **invent** features the data merely contains; and recent work questions whether SAE features beat simpler baselines on downstream tasks. Variants chase these issues: **top-k / JumpReLU / gated** SAEs (better sparsity–fidelity frontier), **transcoders** (replace an MLP with an interpretable sparse map), **crosscoders** (features shared across layers/models). Treat SAEs as the leading *hypothesis-generating* tool for features, not as a solved decoder of the model's mind.

## 6. Representation engineering / steering vectors

If features are linear directions, you can **intervene**: find a direction (via contrastive prompt pairs, mean-difference of activations, or an SAE feature) and **add it to the residual stream** to push behavior (sentiment, refusal, sycophancy, "honesty"). Activation addition / ActAdd, *Representation Engineering* (Zou et al. 2023), and "refusal is mediated by a single direction" are the canonical references. Uses: cheap behavioral control without fine-tuning, and a **causal probe** of whether a representation drives behavior. Limits: directions found one way may not transfer; steering can degrade general capability; "a single direction" results don't generalize to all behaviors.

## 7. Representational similarity (CKA/RSA) recap

To compare representations across layers/models/seeds (not features within one): **CKA** (invariant to orthogonal transforms and isotropic scaling) and **RSA** (compare distance matrices). Use these for "did these two models learn the same thing," convergence/Platonic-hypothesis questions, and layer-wise analysis. Never raw cosine across unaligned spaces (see geometry file).
