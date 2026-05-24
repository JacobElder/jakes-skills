# Category Learning Models

Read this when the user is modeling categorization — classifying stimuli into discrete categories based on training experience, exemplar vs prototype vs rule-based debates, the Shepard/Hovland/Jenkins 6-problem structure, rule-plus-exception (RPE) tasks, 5/4 task, weather prediction, family resemblance categories, or feature-based generalization.

This is a different beast from RL: the focus is on the *representation* of category knowledge (exemplars in memory? abstracted prototypes? rules? clusters?) and how that representation produces classification responses to novel items. Most models share a common structure — assume a representation, define similarity, define a response rule — but differ on what the representation is and how it changes with experience.

Canonical references: Nosofsky (1986) for GCM; Kruschke (1992) for ALCOVE; Love, Medin & Gureckis (2004) for SUSTAIN; Ashby et al. (1998), Ashby & Maddox (2005) for COVIS; Nosofsky, Palmeri & McKinley (1994) for the rule-plus-exception model; Anderson (1991) for the rational/Bayesian model; Pothos & Wills (2011) *Formal Approaches in Categorization* for a textbook overview.

For Tyler Davis's work specifically: Davis, Love & Preston (2012) — SUSTAIN fits to neural data; Davis & Goldwater (2017) — rule vs exemplar individual differences.

## The basic structure shared by most models

Even very different models share a template:

1. **Stimulus representation** — usually a feature vector or a point in a similarity space (often derived from MDS on similarity judgments).
2. **Category representation** — what's stored: every exemplar (GCM, ALCOVE), category prototypes (prototype model), clusters that grow as needed (SUSTAIN), rules (COVIS rule system), or a Bayesian distribution over category structures.
3. **Activation/similarity function** — how a new stimulus contacts the stored representation. Typically exponentially decaying similarity in psychological space:
   $$s(i,j) = \exp(-c \cdot d_{ij})$$
   where `c` is a sensitivity parameter and `d` is distance.
4. **Distance metric.** Minkowski-r distance over weighted dimensions:
   $$d_{ij} = \left(\sum_k w_k |x_{ik} - x_{jk}|^r\right)^{1/r}$$
   `r = 1` (city-block) for separable dimensions (size, color), `r = 2` (Euclidean) for integral dimensions (saturation, brightness). `w_k` are the attention weights; learning often consists of tuning these.
5. **Response rule.** Usually Luce/softmax over category-level summed activations:
   $$P(C_A | x) = \frac{[\eta_A \cdot E_A(x)]^{\gamma}}{\sum_K [\eta_K \cdot E_K(x)]^{\gamma}}$$
   `η_K` is a category bias; `E_K(x)` is the evidence for category K; `γ` is a response-deterministic parameter (γ → ∞ is hard maximum). Some implementations use `exp(β · E_K)` (softmax) instead.

The differences between models live in steps 2 and (sometimes) 4. Understanding this structure makes the models far easier to keep straight.

## Generalized Context Model (GCM) — the standard exemplar model

**Nosofsky (1986).** The reference exemplar model. Category representation = every training exemplar stored in memory.

Evidence for category K = sum of similarities to all stored exemplars in K:

$$E_K(x) = \sum_{i \in K} s(x, x_i)$$

with similarity `s(x, x_i) = exp(-c · d(x, x_i))` and distance computed with attention-weighted Minkowski.

Free parameters per subject:
- **`c`** — sensitivity / specificity. High c = similarity drops off quickly with distance (steep generalization gradient); low c = broad generalization.
- **`w_1, ..., w_D`** — attention weights on each dimension, summing to 1 (so D-1 free).
- **`η_K`** — category response biases (K-1 free if K categories, often fixed equal).
- **`γ`** — response determinism (often fixed to 1; if free, called "response scaling").

Total: roughly 1 + (D−1) + (K−1) + 1, so 4–6 for typical 2-D, 2-category tasks. Very tractable.

**Strengths:** Fits a huge range of classification data; explains the typicality effect, family resemblance, exception items; closed-form likelihood; mature theoretical literature.

**Weaknesses:** Doesn't learn — assumes the representation is already in place; doesn't naturally handle multi-stage learning curves; struggles with information-integration tasks that COVIS handles better.

### GCM likelihood in Python

```python
import numpy as np
from scipy.optimize import minimize

def gcm_loglik(params, stim, choice, exemplars, exemplar_cats,
               n_dim, n_cat, r=2):
    """
    stim: (n_trials, n_dim) stimulus features for test trials
    choice: (n_trials,) chosen category in [0, n_cat)
    exemplars: (n_exemplars, n_dim) training exemplars
    exemplar_cats: (n_exemplars,) category labels for training exemplars
    """
    c = params[0]
    # Attention weights: simplex (last is 1 - sum of others)
    w = np.concatenate([params[1:n_dim], [1 - np.sum(params[1:n_dim])]])
    # Sanity check on simplex
    if np.any(w < 0):
        return 1e10
    
    # Pairwise distances between stim and exemplars (weighted Minkowski)
    diffs = np.abs(stim[:, None, :] - exemplars[None, :, :])      # (N_trial, N_exemplar, D)
    weighted = (w[None, None, :] * diffs**r).sum(axis=2)
    dists = weighted**(1.0 / r)
    sims = np.exp(-c * dists)                                     # (N_trial, N_exemplar)
    
    # Summed similarity to each category
    evidence = np.zeros((stim.shape[0], n_cat))
    for k in range(n_cat):
        mask = exemplar_cats == k
        evidence[:, k] = sims[:, mask].sum(axis=1)
    
    # Probabilistic choice (softmax with γ = 1 here)
    probs = evidence / evidence.sum(axis=1, keepdims=True)
    probs = np.clip(probs, 1e-9, 1 - 1e-9)
    chosen_probs = probs[np.arange(len(choice)), choice]
    return -np.sum(np.log(chosen_probs))
```

For Bayesian fitting, `BayesGCM` (Bartlema, Lee, Wetzels & Vanpaemel 2014) provides a JAGS implementation. The `catlearn` R package has `slpGCM` for the iterative/learning version.

## Prototype model

Same machinery as GCM but the category representation is a single point (the prototype, typically the centroid of training exemplars) instead of every exemplar. Fewer free parameters; predicts that classification depends only on distance-to-prototype.

Equivalent to GCM in the limit of certain parameter settings. Often loses to GCM on most data, but useful as a comparison and dominant in some conditions (e.g., when training set is small or noisy, the prototype representation can be more robust).

## ALCOVE — Kruschke's learning extension of GCM

**Kruschke (1992).** Adds learning: attention weights `w_k` and category-association weights are updated by gradient descent on a delta-rule error signal. So ALCOVE = GCM where the representation tunes over trials.

Free parameters (per subject):
- **`c`** — specificity (as in GCM)
- **`λ_w`** — attention learning rate
- **`λ_a`** — association learning rate
- **`φ`** — response mapping parameter

Captures the *time course* of learning, which GCM cannot. Predicts characteristic patterns of dimensional attention (subjects learn to weight diagnostic dimensions higher).

**Weakness:** Like GCM, struggles with information-integration tasks and with sudden rule discovery. `catlearn::slpALCOVE` provides the standard implementation.

## SUSTAIN — adaptive clustering

**Love, Medin & Gureckis (2004).** A clustering model: builds up clusters as needed during learning. When a stimulus is correctly predicted by the existing clusters, an existing cluster is updated. When a stimulus is misclassified (or, in unsupervised mode, sufficiently surprising), a *new cluster* is recruited centered on that stimulus.

This is what makes SUSTAIN distinctive — and what Tyler Davis's neuroimaging work leverages. The cluster recruitment provides a model-derived "surprise" signal that maps onto medial temporal lobe activity (Davis, Love & Preston 2012a,b).

Free parameters (per subject):
- **`r`** — attention focus (controls how attention weights distribute across dimensions)
- **`β`** — cluster competition (winner-take-all sharpness; higher β = more all-or-nothing cluster activation)
- **`d`** — decision determinism (Luce response rule exponent)
- **`η`** — learning rate
- **`τ`** (threshold) — cluster recruitment threshold; new cluster recruited when activation falls below this (in unsupervised mode) or on misprediction (in supervised mode)

That's ~5 parameters. The strength is that SUSTAIN can mimic prototype representation (one cluster per category), exemplar representation (one cluster per stimulus), or anywhere in between, depending on parameter settings and task. This is consistent with growing evidence that human categorization is not a single strategy.

`catlearn::slpSUSTAIN` is the canonical R implementation. The original Love et al. (2004) paper has detailed equations.

## COVIS — rule + procedural dual systems

**Ashby, Alfonso-Reese, Turken & Waldron (1998).** A *dual-process* model: an explicit rule-learning system and an implicit procedural (RL-based) system compete for control of responding.

The verbal/rule system hypothesizes and tests single-dimension or simple-conjunction rules using a Wisconsin Card Sort-like mechanism. The procedural system learns associations from stimulus regions to motor responses via dopamine-mediated RL.

Free parameters: ~7+. Hard to fit. Designed primarily as a theoretical framework explaining the dissociation between rule-based (RB) and information-integration (II) categorization tasks. The strong claim: RB tasks rely on the verbal system (prefrontal/medial temporal), II tasks on the procedural system (basal ganglia).

When to use COVIS: when the scientific question is specifically about the dual-system claim, or when the design contrasts RB and II structures and you want to test whether subjects use different strategies. Otherwise, GCM/SUSTAIN are usually easier to fit and tell most of the same story.

Note that the dual-system theory is contested — Newell, Dunn & Kalish (2011) and others argue a single-system account fits most data equally well. Report both.

## Rule-plus-exception (RPE) and rational/Bayesian models

**Nosofsky, Palmeri & McKinley (1994)** — RULEX: a rule that explains most items + a list of memorized exceptions. The Davis lab has done influential work fitting variants of this and SUSTAIN to neural data from RPE tasks.

**Anderson (1991)** rational model of categorization — a Bayesian nonparametric (Chinese restaurant process) prior over cluster structure; closely related to Dirichlet-process mixtures. Sanborn, Griffiths & Navarro (2010) develop this into a particle filter for online inference. SUSTAIN can be derived as an approximation to this rational model (Sanborn et al. 2010; Gershman & Niv 2010).

These models matter when you want to explain *how* categorization adapts to category structure of the input — they predict that the model builds the representation it needs rather than committing to exemplar or prototype a priori.

## Choice of model — a decision guide

| Question | Default model |
|----------|---------------|
| Fit a steady-state classification dataset, no learning curve | GCM |
| Fit a learning task and capture the time course | ALCOVE or SUSTAIN |
| Test exemplar vs prototype vs rule explanations | Compare GCM, prototype, RULEX, possibly SUSTAIN |
| RB vs II dissociation | COVIS, also fit GCM and SUSTAIN for comparison |
| RPE (rule-plus-exception) tasks, especially with neural data | SUSTAIN — handles cluster recruitment for exceptions naturally |
| Family resemblance, prototype effects | GCM is the canonical fit; prototype as alternative |
| Information-integration with continuous dimensions | GCM or COVIS procedural system |
| Bayesian/rational analysis | Anderson 1991 / Sanborn et al. 2010 |
| Individual differences in strategy use | SUSTAIN with cluster count as DV; or fit GCM + a rule model and compare per subject |

## Parameter recovery is harder than for RL

Category models often have more parameters with more trade-offs:

- `c` and `w_k` trade off in GCM — high `c` with broad `w` ≈ low `c` with peaked `w` at the diagnostic dimension.
- SUSTAIN's `β` and `τ` jointly control how many clusters get recruited; they're not orthogonal.
- COVIS has so many parameters that recovery is generally poor on standard datasets.

**Always do parameter recovery on category models before reporting individual estimates.** If the recovery is poor, fit at the group level only and report group-level inferences.

## Implementation: the `catlearn` R package

R's `catlearn` (Wills, Lea & colleagues) provides consistent interfaces for GCM, ALCOVE, SUSTAIN, DIVA, exemplar-based linear classifier, and others. The state-of-the-art for non-Bayesian per-subject category-model fitting:

```r
library(catlearn)
# Each model exposes a slpXXX function that processes a trial-by-trial input matrix
# and returns trial-by-trial output (predicted responses)
out <- slpGCM(st = list(c = 2, w = c(0.4, 0.6), nDim = 2, ...), tr = your_trials)
# Fit by optimizing some loss between out$p and observed responses
```

For Bayesian fits, options are sparser — `BayesGCM` for GCM specifically, or write Stan/JAGS code for the model you care about. The Wagenmakers/Lee *Bayesian Cognitive Modeling* book has chapters on Bayesian categorization models in JAGS that are still good starting points.

## Common pitfalls in category-model fitting

- **The Minkowski-r exponent matters and is often fixed by stimulus type.** Don't fit `r` freely — pick based on whether dimensions are separable (r=1) or integral (r=2). Garner (1974) gives the operational definition.
- **The stimulus representation matters as much as the model.** GCM with a bad MDS solution fits worse than the simplest baseline; GCM with a good representation often fits beautifully. When possible, collect similarity ratings and derive MDS coordinates yourself rather than using pixel-space coordinates.
- **Don't confuse exemplar-storage with exemplar-strategy.** GCM stores every exemplar but can mimic prototype-like generalization given certain attention weights. The fitting doesn't tell you what the subject *introspectively does*.
- **The 5/4 task and Medin-Schaffer set are famously discriminating.** If you're testing exemplar vs prototype, use the canonical structures designed to dissociate them. Other category structures often can't tell the models apart.
- **Rule-based tasks may show sudden learning transitions** that GCM and ALCOVE can't reproduce because they're gradient-descent (Smith & Ell 2015). If your data show abrupt aha-moment shifts, consider a discrete-rule model or report the qualitative misfit even if the WAIC favors the gradient model.
- **Individual differences are large.** Group-average fits often hide subjects using qualitatively different strategies. Whenever possible, fit per-subject and inspect the parameter distribution.
- **Test items differ from training items in informative ways.** Use generalization to novel test items as the primary fit target, not training-trial fits. Training-trial fits are easy because the model just memorizes.

## Connections to other model families

- SUSTAIN ↔ Bayesian nonparametric clustering (Sanborn et al. 2010; Gershman & Niv 2010): SUSTAIN is approximately the maximum-a-posteriori online clustering under a Dirichlet-process prior over category structure.
- ALCOVE ↔ kernel methods in machine learning: ALCOVE is a kernel-machine classifier with the kernel being the exponential-similarity function and the weights tuned by gradient descent.
- GCM ↔ kernel density classification: GCM is, in effect, classification by KDE with an exponential kernel.

These connections are useful when explaining the models to ML-fluent users or when borrowing techniques (e.g., adapting recent kernel-machine work to cognitive models).

## What to report

When publishing a category-modeling result:

- Stimulus representation (and how it was obtained).
- Specific model form, all free parameters and their priors/bounds.
- Per-subject and group-level parameter estimates with uncertainty.
- Model comparison results (relative fit) plus PPC (absolute fit).
- Parameter and model recovery on simulated data with the same trial structure.
- Strategy heterogeneity check — what fraction of subjects are best fit by each model?
