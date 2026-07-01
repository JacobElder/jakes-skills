# Autoencoders, VAEs, and Latent-Variable Representations

Deterministic codes vs distributional latents, the ELBO, the failure modes, and the truth about disentanglement.

## Contents
1. Autoencoders: codes without semantics
2. The VAE: making the latent a real latent
3. The ELBO and what each term buys
4. Posterior collapse
5. β-VAE and the disentanglement story (and its impossibility)
6. VQ-VAE: discrete codes
7. Diffusion and other latents

---

## 1. Autoencoders: codes without semantics

A plain autoencoder learns encoder f and decoder g to minimize reconstruction error ‖x − g(f(x))‖². The bottleneck code z = f(x) is a compressed representation. Useful for denoising (denoising AE), anomaly detection (high reconstruction error = anomaly), and pretraining. **But the latent space has no generative semantics:** there's no prior, so sampling a random z and decoding gives garbage, and the code's coordinates need not be meaningful or smooth. An AE is *not* a latent-variable model — it's a learned nonlinear compressor. (Linear AE with MSE = PCA, up to rotation.) This distinction is a frequent trap: people sample a vanilla AE's latent expecting a generative model.

## 2. The VAE: making the latent a real latent

A VAE posits a generative model p(x|z)p(z) with prior p(z)=N(0,I), and learns an *approximate posterior* q(z|x) (the encoder outputs a mean and variance). Two changes make the latent meaningful:
- **A prior** the latent is regularized toward → the space is filled and samplable; decode a random N(0,I) draw and get a plausible x.
- **Stochastic encoding** (z is sampled, not deterministic) → nearby codes decode similarly, so the space is smooth/continuous.
The **reparameterization trick** (z = μ + σ⊙ε, ε∼N(0,I)) makes sampling differentiable so you can backprop through it. This is the move that made VAEs trainable end-to-end (Kingma & Welling 2013).

## 3. The ELBO and what each term buys

Maximize the evidence lower bound:
ELBO = E_q(z|x)[log p(x|z)] − KL(q(z|x) ‖ p(z))
- **Reconstruction term** E[log p(x|z)]: decode z back to x (fidelity).
- **KL term**: pull the posterior toward the prior (regularize the latent; enable sampling).
There's a sharper read (Hoffman & Johnson): the KL averaged over data decomposes into a **mutual-information term** I(x;z) and a **marginal-KL** between the aggregate posterior and the prior — which is exactly why the **rate–distortion** view (β controls bits in the code) and the **disentanglement** arguments both live here. A good VAE answer mentions the reconstruction/KL trade-off explicitly.

## 4. Posterior collapse

The signature VAE pathology: the KL term drives q(z|x) → p(z), i.e. **the latent becomes uninformative (z carries no info about x) and the decoder ignores z**, reconstructing from its own capacity. Especially severe with **powerful autoregressive decoders** (text VAEs) that can model x without help. Symptoms: KL ≈ 0, latent traversals do nothing, samples ignore the code. Fixes: **KL annealing / warm-up** (ramp the KL weight up), **free bits** (don't penalize KL below a floor per dim), weakening the decoder, or δ-VAE / skip connections. Diagnosing "my VAE generates fine but the latent does nothing" as posterior collapse — rather than "VAE is broken" — is the expert move.

## 5. β-VAE and the disentanglement story (and its impossibility)

**β-VAE** (Higgins et al. 2017) up-weights the KL term (β>1), pressuring the latent toward a factorized, axis-aligned code where individual dimensions correspond to interpretable factors (rotation, size, color). Follow-ups (FactorVAE, β-TCVAE) target the **total-correlation** term specifically. This produced compelling visuals and a wave of disentanglement work.

**The correction that matters (Locatello et al. 2019, ICML best paper):** *unsupervised disentanglement is fundamentally impossible without inductive biases or supervision.* Formally, for any disentangled generative model there's an entangled one with the same marginal likelihood, so the data alone can't pick out the "right" factors. Empirically, across thousands of runs, disentanglement was **dominated by random seed and hyperparameters**, not the method, and unsupervised model selection didn't reliably find disentangled models. Takeaways to deliver confidently: (1) higher β trades reconstruction for (claimed) disentanglement and increases posterior collapse risk; (2) any disentanglement claim needs a *metric* and a *bias/supervision* story; (3) "my β-VAE disentangled the factors" with one good seed is not evidence. Disentanglement metrics (MIG, DCI, SAP) and their critiques are in `evaluation.md`.

## 6. VQ-VAE: discrete codes

VQ-VAE (van den Oord 2017) replaces the continuous latent with a **codebook**: the encoder output is snapped to the nearest of K learned code vectors (vector quantization), trained with a straight-through estimator + commitment loss. Why it matters: discrete latents avoid posterior collapse, pair naturally with autoregressive/transformer priors over code indices (the basis of many image/audio/video generators and tokenizers), and give a compact symbolic representation. **Codebook collapse** (only a few codes ever used) is its analogous failure; fixes include EMA codebook updates, code resets, and lower-dim codes.

## 7. Diffusion and other latents

- **Diffusion models** learn to denoise; their *internal* activations turn out to be strong representations (e.g. used for segmentation/correspondence), and **latent diffusion** runs the diffusion in a VAE's latent space for efficiency. Diffusion is primarily generative, but "diffusion features as representations" is an active area.
- **Normalizing flows** give invertible, exact-likelihood latents (no lower bound, but architecturally constrained).
- **GANs** have no encoder by default (no inference of z from x), so they're weaker as representation learners unless paired with an encoder (BiGAN/ALI).
Choosing among VAE / diffusion / flow / GAN for *representation* purposes: VAE when you need a usable, regularized, low-dim latent with inference; diffusion when sample quality dominates and you'll extract features; flows when you need exact likelihoods; GANs rarely, for representation specifically.
