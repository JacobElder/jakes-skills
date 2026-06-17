---
name: sequence-analysis-hmm
description: Apply Hidden Markov Models and related sequence-analysis techniques (Markov chains, HMMs, HSMMs, profile-HMMs, CRFs) to problems with sequential data and latent structure — gene/protein analysis, regime detection, POS tagging, speech recognition, activity detection, log anomaly detection, customer-journey segmentation. Use whenever the user mentions HMMs, Viterbi, Baum-Welch, forward-backward, profile HMMs, HMMER, Pfam, regime-switching, hmmlearn, or pomegranate. Also use it when the user describes a problem that *should* be an HMM but doesn't name it ("noisy observations from something that switches modes," "segment this series into regimes," "find domains in this protein"). Don't skip this skill assuming generic ML knowledge is enough — HMM modeling has specific pitfalls (label switching, local optima, numerical underflow, choosing K, the geometric duration assumption) that generic advice misses, and there are domain-specific conventions (bioinformatics vs. finance vs. NLP) that matter for usable answers.
---

# Sequence Analysis and Hidden Markov Models

This skill helps the agent give expert-level help on sequence analysis problems where Hidden Markov Models (HMMs) or close relatives are the right tool. It covers the theory at the level a practitioner needs, the canonical algorithms (forward-backward, Viterbi, Baum-Welch), and the practical decisions — choosing K, picking emissions, handling numerical issues, validating fits — that determine whether a model actually works.

The skill is general-purpose: bioinformatics (genes, proteins, profile HMMs), time-series (regime switching, anomaly detection), and NLP/speech (tagging, decoding) all live here. When a question is squarely in one domain, consult the matching reference file for conventions, tools, and worked examples:

- `references/bioinformatics.md` — profile HMMs, HMMER, gene finding, sequence alignment
- `references/timeseries.md` — regime detection, financial state-switching, change-point alternatives
- `references/nlp_speech.md` — POS tagging, NER, acoustic models, comparison with CRFs and neural models

The opinionated guidance below applies across domains. Read it first; then dive into the relevant reference.

## Reference routing — read these when they apply

Don't pre-load everything. Decide which references the user's question needs:

| If the user mentions... | Read |
|---|---|
| Pfam, HMMER, profile HMM, protein, gene finding, sequence alignment, hmmbuild/hmmsearch | `references/bioinformatics.md` |
| Regimes, regime-switching, Hamilton, financial returns, volatility states, change points, activity recognition, sensor data | `references/timeseries.md` |
| POS tagging, NER, CRF, sequence labeling, speech recognition, ASR, Kaldi | `references/nlp_speech.md` |
| "What's the difference between HMM and X" | `references/comparisons.md` |
| Implementation details: forward, backward, Viterbi, Baum-Welch pseudocode, numerical stability | `references/algorithms.md` |
| User wants a worked end-to-end example with code, or asks "show me how to fit an HMM in Python" | `scripts/fit_hmm_demo.py` (runnable) |

Combine references when needed: time-series anomaly detection → `timeseries.md` + `scripts/fit_hmm_demo.py`. Comparing HMM and Kalman for a financial problem → `comparisons.md` + `timeseries.md`.

## Response shape — match the question

The skill is dense; responses shouldn't be. Calibrate to the question:

- **"What's an HMM?"** → 3–5 sentences in prose. Urn-and-balls metaphor or weather metaphor. No bullets, no math notation, no code. Offer to go deeper.
- **"Is an HMM right for [my problem]?"** → walk the "right tool" checklist out loud in prose, name the verdict, suggest the alternative if the answer is no. Avoid heavy formatting — even when the answer turns on data quantity or sequence length, stay in prose: "3–5 events per customer is too short for reliable HMM state inference; you'd need hundreds of transitions per state" is better than a bulleted breakdown.
- **"How do I fit an HMM on [my data]?"** → workflow + code. Bullets or numbered steps OK here. Include multi-restart by default — the single most important thing.
- **"My HMM fit looks weird"** → diagnostic questions first (what do the posteriors look like? transition matrix? convergence?), then targeted pitfall from the list.
- **"Explain [algorithm/concept]"** → prose with one concrete example. Pull math from `algorithms.md` only if the user signaled they want it (used notation themselves, asked about implementation, has a math/ML background).

Default to prose. Reach for headers/bullets only when the content is genuinely list-shaped (workflow steps, pitfall enumeration, comparison table). Avoid the "AI-generated" smell of headers-and-bullets on a question that could've been a paragraph.

Concrete contrast for *"what's an HMM?"*:

> **Bad** (typical AI-overformatting):
> ## What is a Hidden Markov Model?
> A Hidden Markov Model (HMM) is a powerful statistical tool used in:
> - **Speech recognition**
> - **Bioinformatics**
> - **Time series analysis**
> ### Key Components:
> 1. **Hidden States** — the underlying states...
> 2. **Observations** — what you actually see...
> 3. **Transition Probabilities** — how states change...
> ### How It Works:
> *(continues for 400 more words)*

> **Good** (what the skill is asking for):
> An HMM models a system you can't directly see, only its outputs. Imagine a friend rolling dice in another room and telling you the results — they might be using a fair die or a loaded die, switching between them sometimes, and you're trying to figure out which die was in use at each roll just from the numbers you heard. The "die in use" is the hidden state; the "number called out" is the observation. HMMs give you the math to reason about what state the system was probably in, and to learn the dice and switching patterns from enough data. Want me to dig into a specific application, or how the math works?

The good version is one paragraph, uses a concrete metaphor, offers a continuation. The bad version is what happens when the model reaches for structure-as-substitute-for-clarity. Resist that reflex.

## When an HMM is (and isn't) the right tool

State this up front, plainly, before any fitting:

**HMMs are the right tool when ALL of the following hold:**
1. Data is a sequence (time, position along DNA, words in order — anything with a well-defined index).
2. You believe the system has a small number of discrete latent "modes" or "states" that aren't directly observed.
3. The state at time *t* depends mainly on the state at *t-1* (Markov assumption is roughly defensible).
4. Observations at *t* depend mainly on the state at *t* and are roughly independent of other observations given the state (conditional independence).
5. Either you want to **decode** (which state was the system in at each step?), **evaluate** (how likely is this sequence under a model?), or **learn** the structure unsupervised from sequences.

**HMMs are usually the wrong tool when:**
- You have plenty of labeled data and the task is discriminative — use a CRF, a neural sequence model, or a transformer. HMMs are generative and waste capacity modeling P(observations) when you only care about P(states | observations).
- The latent variable is continuous (price level, position) — use a Kalman filter / linear-Gaussian state-space model or a particle filter.
- State durations are very non-geometric (e.g., "this regime always lasts about 30 days, never 1 day") — standard HMMs implicitly assume geometric duration; consider an HSMM (hidden semi-Markov model) instead.
- Long-range dependencies dominate — the Markov assumption is wrong and a neural sequence model will crush it.
- You don't have enough sequence data to estimate K² transition parameters reliably. Rough guide: you want hundreds of state-transitions per state, not dozens.

**HMMs remain genuinely best-in-class for:**
- Profile HMMs in bioinformatics (HMMER, Pfam) — neural models have not displaced these for remote homology detection and protein-family curation.
- Small-data, interpretable regime-switching where you need to report "the model thinks we're in state 2 right now, here's the transition matrix" to a non-ML stakeholder.
- Settings where you must integrate explicit prior knowledge of state structure (e.g., gene-finding architectures with explicit intron/exon/intergenic states).
- Online decoding with tight latency/compute budgets.
- Cases where you genuinely need a calibrated generative model (sampling, anomaly scoring via likelihood).

Say this directly when the user proposes an HMM for a task that doesn't fit. The most common mistake is reaching for HMMs out of habit when a CRF, Kalman filter, or change-point method would be better.

## The minimum you need to know about the math

An HMM has:
- **States** Z₁..Z_T from a discrete set of K hidden states.
- **Observations** X₁..X_T from any distribution (categorical, Gaussian, Poisson, mixture).
- **Initial distribution** π over states at t=1, length K.
- **Transition matrix** A, K×K, where A[i,j] = P(Z_{t+1}=j | Z_t=i). Rows sum to 1.
- **Emission model** B, where B[i] is the distribution of X_t given Z_t=i.

Three canonical problems and their algorithms:

| Problem | Question | Algorithm | Output |
|---|---|---|---|
| **Evaluation** | P(X | model) — how likely is this sequence? | Forward (or forward-backward) | A log-likelihood scalar |
| **Decoding** | argmax over Z of P(Z | X, model) — what was the state sequence? | Viterbi | A length-T state sequence |
| **Learning** | argmax over θ of P(X | θ) — fit model from data | Baum-Welch (= EM with forward-backward) | π, A, B |

The forward, backward, and Viterbi recursions are all O(T·K²). Forward computes α_t(i) = P(X₁..X_t, Z_t=i). Backward computes β_t(i) = P(X_{t+1}..X_T | Z_t=i). Together they give posterior state probabilities γ_t(i) = P(Z_t=i | X) and posterior pair probabilities ξ_t(i,j) used in Baum-Welch's E-step. Viterbi is the same as forward but with max instead of sum, plus backpointers.

If the user is fuzzy on the math, point them at Rabiner's 1989 tutorial ("A tutorial on hidden Markov models and selected applications in speech recognition") — it's the canonical reference and remains the best single intro. For bioinformatics, Durbin, Eddy, Krogh, & Mitchison's *Biological Sequence Analysis* (1998) is the bible.

Pseudocode for the three core algorithms is in `references/algorithms.md`. Read it before implementing anything from scratch — there are subtleties (scaling/log-space, ties in Viterbi) that bite.

## The pitfalls that get everyone

These are the things that go wrong in practice, in roughly the order they bite:

**1. Numerical underflow.** Forward probabilities α_t(i) decay exponentially with T. Naive implementation produces zeros for T > ~100. Two fixes: (a) work in log-space throughout (use logsumexp); (b) use the scaled forward-backward (rescale α at each step, store the scaling constants). Every serious library does one of these. If you write your own HMM and it returns -inf log-likelihoods or NaN gradients, this is almost always why.

**2. Local optima in Baum-Welch.** EM is guaranteed to increase the likelihood at each step, not to find the global optimum. Different random initializations give different fits — sometimes dramatically different. **Always run Baum-Welch from multiple random starts (10+ is reasonable for small models, 50+ for larger) and keep the best by held-out likelihood.** This is the single biggest difference between a careful HMM analysis and a sloppy one.

**3. Label switching.** State 0 in one fit may be state 2 in another. The model is identifiable only up to permutation of state labels. This bites when (a) comparing fits across runs, (b) doing Bayesian inference with MCMC, (c) reporting "state 0 means X" to stakeholders. Resolve by post-hoc relabeling — e.g., sort states by their mean emission for a 1D Gaussian HMM, or by their stationary probability, or by the order in which they first appear in the Viterbi path on a canonical sequence.

**4. Choosing K (number of states).** No silver bullet. Approaches in rough order of rigor:
- **Held-out log-likelihood** — fit for K ∈ {1, 2, ..., K_max}, plot, look for an elbow. Often the cleanest.
- **BIC** — penalizes parameters; reasonable default but can over-penalize.
- **AIC** — typically chooses larger K than BIC.
- **Cross-validated likelihood** — gold standard if you can afford it.
- **Domain knowledge** — often the right answer (e.g., "I want bull/bear/sideways → K=3, no model selection needed").
- **Sparsity-inducing priors** (hierarchical Dirichlet process HMM) — lets the data pick K. Heavier machinery; use when truly uncertain.

Avoid "elbow eyeballing" without held-out data. Training likelihood is monotone in K.

**5. The geometric duration assumption.** A standard HMM assumes the time spent in state i is geometrically distributed (because P(stay) is a constant per step). If your true durations are tightly peaked (e.g., phonemes last 50–150ms, not 1ms and not 5s), this is a real misspecification. Symptoms: the fitted model rapidly oscillates between states even when you "know" the system is stable. Fix: HSMM (hidden semi-Markov model) with an explicit duration distribution per state. Cost: roughly an order of magnitude more compute.

**6. Treating Viterbi output as ground truth.** The Viterbi path is the single most likely state sequence; the marginal-most-likely state at each position is a different sequence (and may not even be a legal path). For most reporting purposes, use posterior decoding (γ_t) and present uncertainty; use Viterbi only when you need a self-consistent single path (e.g., for downstream parsing).

**7. Conflating "the model fits" with "the model is right."** Likelihood always goes up with more states/parameters. Always check: (a) posterior state assignments make domain sense; (b) emission parameters per state are interpretable; (c) the model generates plausible synthetic data (the `sample` method exists in every library — use it); (d) held-out likelihood doesn't collapse.

**8. Ignoring the prior over initial state.** With long sequences it barely matters; with short sequences (T < 50) it can dominate. Set it deliberately rather than letting it default.

## Library choices (Python, 2024-)

For most practical work, use one of these. Don't roll your own unless you need to.

**`hmmlearn`** — the default. Scikit-learn-style API; supports `GaussianHMM`, `GMMHMM`, `MultinomialHMM`, `CategoricalHMM`, `PoissonHMM`. Mature and stable. Limitations: discrete emissions only via the multinomial/categorical classes, no built-in HSMM, single-sequence-at-a-time mental model (multi-sequence training works via concatenation + a `lengths` array). This is what to reach for first.

A minimal fit-with-restarts pattern (the only pattern worth pasting — single-restart fits are how people get bad answers):

```python
from hmmlearn import hmm

best = None
for seed in range(20):
    m = hmm.GaussianHMM(n_components=3, covariance_type="full",
                        n_iter=200, tol=1e-4, random_state=seed)
    try:
        m.fit(X_train, lengths=lengths_train)
    except Exception:
        continue  # state collapse on bad init; skip
    val_ll = m.score(X_val, lengths=lengths_val)
    if best is None or val_ll > best[0]:
        best = (val_ll, m)

model = best[1]
states = model.predict(X, lengths=lengths)        # Viterbi path
posteriors = model.predict_proba(X, lengths=lengths)  # γ_t(i) — show this, not just states
```

For a fuller pipeline (label-switch resolution, model selection sweep, diagnostic plots), run `scripts/fit_hmm_demo.py` and adapt it. Don't hand-roll a fit from scratch when the demo script already does it correctly.

**`pomegranate` v1.0+** — rewritten on PyTorch (as of v1.0). More flexible: any distribution as an emission (mix Poisson and Normal in the same model if you want), GPU support, easy custom distributions, supports HSMMs. The API changed significantly from v0.14.x — if you find a tutorial that uses `HiddenMarkovModel.from_samples`, it's the old API. Worth the switch when you need flexibility hmmlearn can't give.

**`HMMER`** — the answer for protein/nucleotide profile HMMs. Command-line tool (`hmmbuild`, `hmmsearch`, `hmmscan`, `jackhmmer`); not a Python library, but `pyhmmer` provides Python bindings. If the user is doing anything involving Pfam, protein families, or remote homology — they want HMMER, not hmmlearn. See `references/bioinformatics.md`.

**`dynamax`** — modern JAX-based state-space modeling library from the probml group (Murphy, Linderman et al.; published JOSS 2025). Excellent for HMMs and Kalman-filter-family models, vectorized, GPU/TPU-ready, supports HSMMs and more complex variants. Use when you need speed at scale or want to compose with other JAX/probabilistic code.

**`PyMC` / `NumPyro` / `Stan`** — fully Bayesian HMMs. Use when you genuinely need posterior uncertainty over parameters, are doing hierarchical modeling across many sequences, or want to handle label switching properly via constrained priors. Heavier weight; only reach for these when MLE plus a few random restarts isn't enough.

**Don't use:** `seqlearn` (effectively unmaintained), old `pomegranate` v0.14 tutorials (API changed), bespoke pure-Python implementations from Medium tutorials (almost always have numerical issues or bugs in Baum-Welch).

For non-Python: in R, `depmixS4` is the standard; for production speech/large-scale, `Kaldi` (C++) is industry-standard but is a different universe of complexity.

## A workflow that actually works

When the user has a dataset and wants to "fit an HMM," walk through this:

1. **Sanity-check the data.** What is T? How many sequences? What's the observation type? Is the sequence index meaningful (uniform time, position along genome, word index)? Are there missing values?

2. **Decide K.** Domain knowledge first. If unknown, plan a held-out-likelihood sweep over K ∈ {1..8} or so. Set this expectation early — model selection is part of the work, not a postscript.

3. **Pick the emission distribution.** Continuous 1D → Gaussian. Count data → Poisson. Categorical → CategoricalHMM (one-hot or integer-coded). Multimodal-within-state → GMM emissions. Mixed types → pomegranate. Don't default to Gaussian for everything; bad emission choices show up as too many states or as one state being a "garbage collector."

4. **Initialize thoughtfully.** Random initialization is fine but use multiple restarts. For continuous data, k-means on the observations to seed means and within-cluster covariance for covariances is a reasonable first init (this is what hmmlearn does by default). For categorical, uniform-with-noise.

5. **Fit with multiple restarts.** Hold out 20–30% of sequences (not 20–30% of timesteps within a sequence — that breaks the Markov chain). Loop over random seeds. Keep best by held-out log-likelihood.

6. **Diagnose.**
   - Posterior decoding plot: γ_t for each state across t, on representative sequences. Are states well-separated or fighting?
   - Transition matrix: are diagonals dominant (sticky states) or near-uniform (over-switching)?
   - Emission parameters: do means/probabilities per state correspond to recognizable real-world modes?
   - Sample from the model: do synthetic sequences look like real ones?
   - Convergence: did EM actually converge? hmmlearn exposes `model.monitor_`.

7. **Validate downstream.** If you're using state assignments as features for another model, check they help. If you're reporting regime assignments, get a domain expert to look at them. The likelihood number alone is a weak signal.

8. **Report uncertainty.** State assignments come with posterior probabilities. Don't show only the Viterbi path; show γ_t so stakeholders see where the model is confident vs. guessing.

## Common applications, at a glance

These get expanded in the reference files; this is the orientation.

**Bioinformatics.** Profile HMMs (HMMER) for protein family modeling and remote homology — the technique that built Pfam. Gene finding (e.g., GENSCAN, AUGUSTUS) with explicit exon/intron/intergenic state architectures. CpG island detection (classic Durbin example). Pairwise sequence alignment as a pair-HMM. See `references/bioinformatics.md`.

**Time series and finance.** Hamilton's regime-switching models for macroeconomic series (bull/bear, expansion/recession). Volatility regimes. Anomaly detection by training an HMM on "normal" sequences and flagging low-likelihood new sequences. Activity recognition from accelerometer data. See `references/timeseries.md`. Important: HMMs for stock-price prediction are mostly cargo-cult; the literature has not shown reliable alpha. Manage expectations.

**NLP and speech.** Historically: part-of-speech tagging (Brown corpus baselines), HMM-based ASR (Kaldi). Today: neural models dominate sequence-to-sequence tasks, but HMMs (and CRFs, which are their discriminative cousin) remain useful baselines, in low-resource settings, and in pipelines where calibrated probabilities matter. See `references/nlp_speech.md`.

**Across all domains:** for an end-to-end runnable example with diagnostics, point the user at `scripts/fit_hmm_demo.py`, which builds a 3-state Gaussian HMM on synthetic regime-switching data and walks through fitting, diagnosing, and visualizing. The patterns transfer — adapt the emission type and feature shape for the user's data.

## When the user is just starting

Don't dump all of this on them. Diagnose where they are:
- *"What's an HMM?"* → conceptual explanation with the urn-and-balls metaphor, then "and here's why you might care for your problem."
- *"I have data X and I think I want an HMM"* → run the "Is HMM the right tool" checklist out loud, then the workflow.
- *"My HMM fit looks weird"* → straight to the pitfalls list; ask for posterior decoding plots and the transition matrix.
- *"What's the difference between an HMM and X"* → comparison (CRF, Kalman filter, transformer, change-point) — `references/comparisons.md` has these.
- *"Here's my data, [silence]"* (user pasted sequences with no clear ask) → ask: what's the unit of observation (time? position?), how many sequences, what would success look like (regime labels? anomaly scores? a fitted model to deploy?). Don't fit anything until you know what they want.
- *"Can HMMs predict the stock market?"* → no, not reliably; see `references/timeseries.md` for what they *can* do in finance.

Be specific. "Run multiple random restarts" is more useful than "be careful with EM."
