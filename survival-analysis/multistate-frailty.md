# Multi-state and frailty models

These two model families handle the most complex real-world settings: subjects moving through multiple states (multi-state), and unobserved heterogeneity across subjects or correlation within clusters (frailty). They overlap with — and extend — competing risks and recurrent events.

## Multi-state models

A multi-state model describes a subject moving through a discrete set of states over time, where each transition has its own hazard. They generalize competing risks (one starting state, multiple absorbing states) and recurrent events (repeated transitions between the same states).

### Common multi-state structures

- **Illness-death (irreversible)**: Healthy → Ill → Dead, with Healthy → Dead also possible. Three transitions, two absorbing states (well, one absorbing: Dead).
- **Illness-death (reversible)**: adds Ill → Healthy transition.
- **Disease progression**: Stage 1 → Stage 2 → ... → Stage K → Death.
- **Markov chain models**: subjects move stochastically through states with transition rates depending on covariates.

Pick the state diagram first, then choose modeling assumptions.

### Markov vs semi-Markov vs non-Markov

- **Markov**: transition hazard from state j to k at time t depends only on the current state and (optionally) covariates. Memoryless.
- **Semi-Markov**: transition hazard depends on time spent in the current state (gap time), not total time. The clock resets on each transition.
- **Non-Markov**: hazard depends on the full history. Hard to fit; sometimes captured via time-dependent covariates.

Most applied multi-state work uses Markov or semi-Markov assumptions.

### R — mstate package

```r
library(mstate)
library(survival)

# Define the transition matrix
# tmat[i, j] = transition number for j -> k, NA if not allowed
tmat <- transMat(x = list(c(2, 3), c(3), c()),
                 names = c("Healthy", "Ill", "Dead"))
print(tmat)

# Reshape data to long format (one row per (subject, transition))
df_long <- msprep(time = c(NA, "time_to_ill", "time_to_death"),
                  status = c(NA, "ill_event", "death_event"),
                  data = df, trans = tmat, keep = c("age", "sex"))

# Fit a Cox-type model per transition (transition-specific covariates via 'expand.covs')
df_long <- expand.covs(df_long, c("age", "sex"), append = TRUE, longnames = FALSE)
fit <- coxph(Surv(Tstart, Tstop, status) ~ age.1 + age.2 + age.3 +
             sex.1 + sex.2 + sex.3 + strata(trans), data = df_long)
summary(fit)
# .1, .2, .3 give transition-specific effects.

# Predict transition probabilities for a new subject
msf <- msfit(object = fit, newdata = newdata_long, trans = tmat)
pt <- probtrans(msf, predt = 0)  # transition probabilities from time 0
plot(pt, ord = c(2, 3, 1))       # plot stacked transition probabilities
```

### R — msm package (multi-state Markov for panel data)

When you observe subjects at discrete times rather than knowing exact transition times (panel data), use `msm`:

```r
library(msm)

# Initial transition intensity matrix
Q.init <- matrix(c(0, 0.1, 0.05,
                   0,   0, 0.10,
                   0,   0,    0),
                 nrow = 3, byrow = TRUE,
                 dimnames = list(c("Healthy","Ill","Dead"),
                                 c("Healthy","Ill","Dead")))

fit_msm <- msm(state ~ time, subject = id, data = df, qmatrix = Q.init,
               covariates = ~ age + sex)
summary(fit_msm)
# Transition intensities with covariate effects (hazard-ratio-like).
```

`msm` handles "we only see the state at clinic visits, not the moment of transition." Common in epidemiology.

### Python

Multi-state modeling in Python is minimal. lifelines has illness-death support via `AalenJohansenFitter` for the descriptive side, but no full multi-state regression equivalent to `mstate`. For serious multi-state work, R is the right tool.

### What multi-state buys you

- **Transition probabilities at any time t**: "What's the probability this subject is in state k at year 5?" Direct from the model.
- **Sojourn times**: "How long, on average, does a subject stay in the Ill state?"
- **Joint description of competing risks + recurrent transitions**: a subject can become ill, recover, become ill again, then die.

## Frailty models

A **frailty** is a subject-specific (or cluster-specific) random effect on the hazard, modeling unobserved heterogeneity. The hazard becomes:

$h_i(t) = u_i \cdot h_0(t) \cdot \exp(x_i^\top \beta)$

where $u_i$ is the frailty for subject $i$ (or cluster $i$), typically Gamma(θ, θ) (mean 1, variance θ) or log-normal. High frailty = "this subject is intrinsically high-risk in ways the covariates don't capture."

Frailty is the survival analog of a random intercept in a mixed model.

### When to use frailty

- **Clustered data**: patients within hospitals, students within schools, customers within accounts. Cluster-level frailty accounts for within-cluster correlation. Equivalent option: just use cluster-robust standard errors (`+ cluster(id)`), which is simpler if you only care about coefficient SEs.
- **Recurrent events with heterogeneity**: some subjects have many events, others few, beyond what covariates explain. Subject-level frailty.
- **Recurrent + terminal events**: joint frailty models the recurrent and terminal event processes as sharing a common frailty.
- **Selection on unobservables**: as time passes, the surviving population becomes enriched in low-frailty subjects, which can produce apparent declining hazards that are really just selection (the "frailty bias" in marginal hazard estimates).

### R — survival package (basic shared frailty)

```r
library(survival)

# Gamma shared frailty by cluster
fit_frailty <- coxph(Surv(time, status) ~ age + sex + frailty(hospital, distribution = "gamma"),
                     data = df)
summary(fit_frailty)
# Reports variance of the frailty (theta) + p-value for the heterogeneity.

# Log-normal frailty
fit_ln <- coxph(Surv(time, status) ~ age + sex + frailty(hospital, distribution = "gaussian"),
                data = df)
```

Note: `frailty()` in the `survival` package is being deprecated in favor of `coxme` for true mixed-effects Cox models.

### R — coxme (mixed-effects Cox, preferred for complex random effects)

```r
library(coxme)

# Random intercept by hospital (equivalent to shared frailty)
fit_me <- coxme(Surv(time, status) ~ age + sex + (1 | hospital), data = df)
print(fit_me)
# Reports fixed-effect HRs and random-effect variance.

# Nested or crossed random effects work too
fit_nested <- coxme(Surv(time, status) ~ age + (1 | hospital/doctor), data = df)
```

### R — frailtypack (advanced: nested, joint, recurrent + terminal)

```r
library(frailtypack)

# Recurrent events with shared frailty (gamma)
fit_rec <- frailtyPenal(Surv(tstart, tstop, recurrent_event) ~ cluster(id) + treatment + age,
                        data = df, recurrentAG = TRUE, n.knots = 8, kappa = 1e7)
print(fit_rec)

# Joint frailty: recurrent events AND a terminal event share a frailty
# Useful when the terminal event is informative censoring for recurrent events
fit_joint <- frailtyPenal(Surv(tstart, tstop, recurrent_event) ~ cluster(id) + treatment +
                          terminal(death_event),
                          formula.terminalEvent = ~ treatment + age,
                          data = df, recurrentAG = TRUE, n.knots = 8, kappa = c(1e7, 1e7))
print(fit_joint)
# Estimates the correlation between recurrent-event frailty and death-hazard frailty
# via alpha parameter. alpha > 0 means subjects prone to recurrent events also die sooner.
```

`frailtypack` also supports nested frailty (e.g., recurrent events within patients within hospitals), additive frailty (mixed continuous and binary effects), and multivariate joint models.

### Python

Frailty/mixed-effects Cox in Python is limited. Options:
- `lifelines` doesn't have shared frailty.
- `scikit-survival` doesn't either.
- `cluster_col` argument in lifelines gives robust SEs but not a frailty estimate.
- For real frailty modeling, use R (`coxme`, `frailtypack`, `parfm`).

## Joint frailty for recurrent + terminal events

The setup: subjects have a recurring non-terminal event (e.g., hospital readmission, equipment failure with repair) until a terminal event (death, scrappage) ends the process. The terminal event is informative censoring for the recurrent event: subjects who die have stopped generating readmissions for reasons related to their underlying risk.

Naive analysis (AG with death as censoring) underestimates the readmission rate for subjects who die early. Joint frailty fits both processes simultaneously:

$\lambda_R(t) = u_i \cdot \lambda_{R0}(t) \cdot \exp(x_i^\top \beta_R)$ (recurrent intensity)
$\lambda_D(t) = u_i^\alpha \cdot \lambda_{D0}(t) \cdot \exp(x_i^\top \beta_D)$ (terminal hazard)

The shared frailty $u_i$ couples the two processes. $\alpha$ is a positive scalar: $\alpha = 0$ means no association; $\alpha > 0$ means subjects with high recurrent-event rates also die faster (i.e., the censoring is informative).

```r
library(frailtypack)

fit_jf <- frailtyPenal(Surv(tstart, tstop, readmit) ~ cluster(id) + treatment +
                       terminal(death),
                       formula.terminalEvent = ~ treatment + age,
                       data = df, recurrentAG = TRUE, n.knots = 8, kappa = c(1e7, 1e7))
summary(fit_jf)
# Look at alpha and its CI. If alpha is significantly > 0, joint modeling matters.
```

## Selection / frailty bias on marginal hazards

A subtle conceptual point: even when the **conditional** hazard ratio (given frailty) is constant, the **marginal** hazard ratio (averaged over the surviving population) can decline over time, because the high-frailty subjects in the more-at-risk group die off faster, leaving a fitter remaining population. This can look like a PH violation when it's really an artifact of unobserved heterogeneity.

Frailty models explicitly account for this. Whether to interpret marginal or conditional HRs is a substantive question — both are valid, but they mean different things. Marginal HRs are what you'd see at the population level (relevant for public-health summary); conditional HRs are what an individual subject experiences given their frailty (relevant for mechanistic understanding).

## Reporting checklist

For multi-state models:

- The state diagram (a figure showing states and allowed transitions).
- Markov / semi-Markov / non-Markov assumption.
- Per-transition HRs (with CIs).
- Predicted state-occupancy / transition probabilities at meaningful time horizons.
- Sample sizes and event counts per transition.

For frailty / joint models:

- Frailty distribution chosen (Gamma, log-normal) and rationale.
- Estimated frailty variance with CI and test of heterogeneity.
- For joint models: the association parameter $\alpha$ with CI and what it implies about informative censoring.
- Fixed-effect HRs interpreted as conditional on frailty (subject-specific).
- Whether you compared to a simpler model (e.g., AG with robust SEs) and what changed.
