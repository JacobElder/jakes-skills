# Transformers, LLM Representations, and Reward Models

How transformers build representations, what their layers encode, scaling, and reward models as learned preference representations.

## Contents
1. The residual stream and attention as routing
2. What different layers represent
3. Embeddings inside an LLM (token, positional, contextual)
4. Scaling and representations
5. Reward models as learned preference representations

---

## 1. The residual stream and attention as routing

A transformer's central representational object is the **residual stream**: a per-token vector that every layer *reads from and writes to* additively. Attention heads and MLPs don't replace the representation; they **add** their outputs into it. This "read–compute–write to a shared bus" view (the mechanistic-interpretability framing, Elhage et al. 2021) is the right mental model:
- **Attention** *moves* information between token positions — it's content-based **routing**: each head reads a subspace, decides where to attend, and writes information from source tokens to the current position. Attention doesn't transform features so much as *gather* them.
- **MLPs** do per-token feature computation and are where much factual/associative "knowledge" lives (key-value memory view, Geva et al.).
- The **residual stream is the bottleneck**: it has fixed width, so heads/MLPs must share it — hence **superposition** and polysemantic directions (see interpretability file).

## 2. What different layers represent

Empirically (probing studies on BERT/GPT-style models):
- **Early layers:** surface/lexical and positional features, local syntax.
- **Middle layers:** syntax and richer semantics; often the **best layer for transfer/probing** — middle layers frequently beat the last layer for embedding tasks because late layers specialize for the pretraining objective (next-token), not for general features.
- **Late layers:** task-specific / objective-specific features (next-token prediction for decoders).
Practical implication: don't reflexively take the last hidden layer for embeddings — sweep layers; a middle layer is often better. Also, contextual embeddings get **more context-specific (less anisotropic-corrected) in higher layers**, and self-similarity of a word across contexts drops with depth (Ethayarajh 2019).

## 3. Embeddings inside an LLM

- **Token embeddings:** a learned lookup (vocabulary × d). The **unembedding** (final projection to logits) is a separate matrix; tied or untied. The "logit lens" reads intermediate residual stream through the unembedding to see the model's evolving next-token guess.
- **Positional information:** absolute learned, sinusoidal, or — now standard — **rotary (RoPE)** which rotates query/key subspaces by position so attention sees *relative* position; ALiBi biases attention by distance. This is a *representational* choice about how order is encoded.
- **Contextual token representations:** the residual-stream vectors; these are what probing/SAEs analyze and what you pool for embeddings.

## 4. Scaling and representations

- **Scaling laws** (Kaplan et al. 2020; Chinchilla, Hoffmann et al. 2022): loss falls as a power law in parameters, data, and compute; Chinchilla corrected the params/data balance (most large models were undertrained — scale *data* with params). These are laws about *loss*, and better loss generally buys better representations, but the mapping from loss to representation quality on a specific task is not a clean power law.
- **Emergence** debate: some capabilities appear to "switch on" with scale; Schaeffer et al. (2023) argue much apparent emergence is an artifact of discontinuous metrics. Relevant when someone claims a representation "emerges" at a scale.
- **Platonic representation hypothesis** (cross-model convergence with scale) — see geometry file; suggestive, not settled.

## 5. Reward models as learned preference representations

In RLHF, the reward model (RM) is trained on **pairwise human comparisons** with a Bradley-Terry loss: L = −log σ(r(x, y_chosen) − r(x, y_rejected)), where r is a scalar head on top of a (usually pretrained) transformer. Frame it precisely: **the RM is a learned representation of "what the preference dataset rewards,"** projected to one scalar. Consequences to state with confidence:
- **It is a proxy, not "what humans want."** It encodes the annotators, instructions, and data distribution — including their biases (length bias, sycophancy, formatting preferences).
- **Miscalibration is the norm;** the scalar's absolute value is not a calibrated utility, only its *ordering* is trained.
- **Reward overoptimization / Goodhart** (Gao et al. 2023): optimize policy hard against a fixed RM and true quality rises then *falls* — the policy finds directions that score high on the RM's representation but are actually worse. KL penalties to the reference model, RM ensembles, and on-policy RM updates mitigate.
- **Reward hacking** is exploitation of the *representational gaps* between the RM and true preference.
This is why "the reward model" is a representation-learning topic, not just an RL detail: its pathologies are representation pathologies (the learned scalar doesn't faithfully represent the target), and the connection to recsys/psychometric preference models (Bradley-Terry, random utility) is exact — see `embeddings-retrieval-recsys.md` §8. Newer preference-optimization methods (DPO) skip the explicit RM by reparameterizing the objective so the *policy itself* implicitly represents the reward — worth noting when the topic is "do you even need a separate reward representation."
