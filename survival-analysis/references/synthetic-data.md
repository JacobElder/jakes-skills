# Generating synthetic time-to-event data

When the user has no data on hand but wants a demo, when you need to test a method on data with known properties, or when you're verifying that a fit recovers the truth, you'll want to simulate. Improvising simulation code on the fly tends to produce data with subtle pathologies (everyone has the same hazard; censoring perfectly correlated with covariates; nobody is right-censored). This file gives clean recipes for each common pattern.

The general principle: simulate event times from an **explicit hazard or survival function**, then apply an **independent censoring mechanism**, then combine to get observed (time, event) pairs.

## Right-censored data from a Cox PH model

Generates the standard setup most methods assume.

### R
```r
set.seed(42)
n <- 500

# Covariates
age       <- rnorm(n, mean = 60, sd = 10)
sex       <- rbinom(n, 1, 0.5)
treatment <- rbinom(n, 1, 0.5)

# True log hazard ratios
beta_age <- 0.03   # per year
beta_sex <- -0.4   # female (sex=1) protective
beta_trt <- -0.7   # treatment protective

linpred <- beta_age * age + beta_sex * sex + beta_trt * treatment

# Generate event times from a Weibull baseline:
# T = (-log(U) / (lambda * exp(linpred)))^(1/shape)
lambda  <- 0.0001    # baseline scale
shape   <- 1.3       # Weibull shape > 1 -> increasing hazard
U       <- runif(n)
true_t  <- (-log(U) / (lambda * exp(linpred)))^(1/shape)

# Independent right censoring (administrative + dropout)
c_admin   <- 1500  # study ends at day 1500
c_dropout <- rexp(n, rate = 1/2000)  # exponential dropout times
c_time    <- pmin(c_admin, c_dropout)

time   <- pmin(true_t, c_time)
event  <- as.integer(true_t <= c_time)

df <- data.frame(id = 1:n, time = time, event = event,
                 age = age, sex = sex, treatment = treatment)

mean(df$event)  # event rate; aim for 0.3-0.7 for a well-powered example
```

### Python
```python
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 500

age       = rng.normal(60, 10, n)
sex       = rng.binomial(1, 0.5, n)
treatment = rng.binomial(1, 0.5, n)

beta_age, beta_sex, beta_trt = 0.03, -0.4, -0.7
linpred = beta_age * age + beta_sex * sex + beta_trt * treatment

lambda_, shape = 1e-4, 1.3
U = rng.uniform(size=n)
true_t = (-np.log(U) / (lambda_ * np.exp(linpred))) ** (1/shape)

c_admin   = 1500.0
c_dropout = rng.exponential(scale=2000, size=n)
c_time    = np.minimum(c_admin, c_dropout)

time  = np.minimum(true_t, c_time)
event = (true_t <= c_time).astype(int)

df = pd.DataFrame({'id': np.arange(n), 'time': time, 'event': event,
                   'age': age, 'sex': sex, 'treatment': treatment})
print(df['event'].mean())
```

**Sanity check**: fitting a Cox model on this data should recover coefficients close to `(0.03, -0.4, -0.7)`. If it doesn't, the simulation has a bug.

## Non-proportional hazards (delayed treatment effect)

Useful for demonstrating MaxCombo, RMST, or time-varying coefficients. The treatment effect kicks in at some point t_kick.

### R
```r
set.seed(42)
n <- 600
treatment <- rbinom(n, 1, 0.5)
t_kick    <- 90  # treatment effect appears at day 90

# Piecewise hazard: same for both arms before t_kick, halved for treated after
# Generate via inverse CDF; easier to simulate piece by piece.

simulate_one <- function(trt) {
  h1 <- 0.005                          # hazard before t_kick
  h2 <- if (trt == 1) 0.004 else 0.005  # hazard after t_kick (1.25x HR, modest delayed effect)
  
  # First, draw a candidate event time as if hazard were h1 forever
  t_cand <- rexp(1, rate = h1)
  if (t_cand <= t_kick) return(t_cand)
  
  # Otherwise the subject survived past t_kick; redraw under h2
  t_kick + rexp(1, rate = h2)
}

true_t <- vapply(treatment, simulate_one, numeric(1))
c_time <- runif(n, 180, 720)  # uniform admin censoring 6-24 months
time   <- pmin(true_t, c_time)
event  <- as.integer(true_t <= c_time)

df <- data.frame(time = time, event = event, treatment = treatment)
```

The KM curves for this data are flat-and-equal for the first 90 days, then diverge. With this parameterisation (seed=42, n=600), standard log-rank is non-significant (p≈0.15) while FH(0,1) reaches significance (p≈0.04), illustrating the power difference. MaxCombo gives a similar result.

## Crossing survival curves

For demonstrating cases where log-rank fails entirely.

### R
```r
set.seed(42)
n <- 600
treatment <- rbinom(n, 1, 0.5)

# Treatment: high early hazard, low late hazard (think: risky surgery that helps survivors)
# Control:   moderate constant hazard
simulate_one <- function(trt) {
  if (trt == 1) {
    if (runif(1) < 0.3) rexp(1, rate = 1/30) else rexp(1, rate = 1/3000) + 100
  } else {
    rexp(1, rate = 1/500)
  }
}

true_t <- vapply(treatment, simulate_one, numeric(1))
c_time <- runif(n, 600, 1200)
time   <- pmin(true_t, c_time)
event  <- as.integer(true_t <= c_time)

df <- data.frame(time = time, event = event, treatment = treatment)
```

KM curves cross around day 100. Standard log-rank p-value is often non-significant despite the obvious group difference. MaxCombo and stratified-by-time-period reporting handle it.

## Competing risks

Two causes; subject experiences whichever comes first.

### R
```r
set.seed(42)
n <- 800
age       <- rnorm(n, 60, 10)
treatment <- rbinom(n, 1, 0.5)

# Cause 1 (e.g., cancer death): treatment reduces hazard
# Cause 2 (e.g., other death):  treatment has no effect
linpred1 <- 0.02 * (age - 60) - 0.7 * treatment
linpred2 <- 0.04 * (age - 60) + 0.0 * treatment

t1 <- rexp(n, rate = 0.001 * exp(linpred1))
t2 <- rexp(n, rate = 0.0008 * exp(linpred2))

# Observed event = whichever came first
true_t <- pmin(t1, t2)
cause  <- ifelse(t1 < t2, 1, 2)

# Censoring
c_time <- runif(n, 800, 2000)
time   <- pmin(true_t, c_time)
status <- ifelse(true_t <= c_time, cause, 0)  # 0 = censored, 1 = cause 1, 2 = cause 2

df <- data.frame(time = time, status = status, age = age, treatment = treatment)
table(df$status)  # check distribution across 0/1/2
```

This produces the classic discrepancy: cause-specific HR for treatment on cause 1 is ~0.5 (the true effect), but Fine-Gray subdistribution HR will be closer to 0.7 because more treated subjects survive long enough to be at risk for cause 2.

## Recurrent events

Multiple events per subject. Generated by simulating sequential gap times from an exponential.

### R
```r
set.seed(42)
n <- 200
followup_max <- 1000

simulate_subject <- function(id, rate) {
  events <- numeric(0)
  t <- 0
  while (TRUE) {
    gap <- rexp(1, rate = rate)
    t <- t + gap
    if (t > followup_max) break
    events <- c(events, t)
  }
  events
}

rows <- list()
for (i in 1:n) {
  rate_i <- 1/200 * exp(rnorm(1, sd = 0.5))  # subject-level heterogeneity (frailty)
  events <- simulate_subject(i, rate_i)
  
  # Build counting-process rows
  starts <- c(0, events)
  ends   <- c(events, followup_max)
  ev     <- c(rep(1, length(events)), 0)
  
  rows[[i]] <- data.frame(id = i, tstart = starts, tstop = ends,
                          event = ev, enum = seq_along(starts))
}
df <- do.call(rbind, rows)
head(df, 15)
```

This is in counting-process format ready for `coxph(Surv(tstart, tstop, event) ~ ... + cluster(id))`. The `rnorm(1, sd=0.5)` creates frailty — useful for testing whether shared frailty models recover it.

## Left-truncated data (age as time scale)

Each subject enters at a random adult age and is followed until death or end of study.

### R
```r
set.seed(42)
n <- 500
age_entry <- runif(n, 50, 75)         # entry ages
sex       <- rbinom(n, 1, 0.5)

# True hazard depends on age and sex; baseline Gompertz-like
true_age_at_death <- numeric(n)
for (i in 1:n) {
  # Generate age at death starting from age_entry[i], conditional on having survived to entry
  # Use rejection: draw from full distribution, accept if > age_entry[i]
  repeat {
    cand <- rweibull(1, shape = 5, scale = 80) + 0.5 * sex[i]
    if (cand > age_entry[i]) {
      true_age_at_death[i] <- cand
      break
    }
  }
}

# Study end: subject is censored at age (entry + max follow-up of 10 years)
age_admin <- age_entry + 10
age_exit  <- pmin(true_age_at_death, age_admin)
event     <- as.integer(true_age_at_death <= age_admin)

df <- data.frame(id = 1:n, age_entry = age_entry, age_exit = age_exit,
                 event = event, sex = sex)

# Correct analysis: Surv(age_entry, age_exit, event)
# Wrong analysis (ignoring truncation): Surv(age_exit, event) - will overstate young-age survival
```

Useful for demonstrating that the truncation matters: fit both `coxph(Surv(age_entry, age_exit, event) ~ sex)` and `coxph(Surv(age_exit, event) ~ sex)` and show that the latter gives biased baseline hazards.

## Interval-censored data

Periodic check-ups; event observed within a window.

### R
```r
set.seed(42)
n <- 400
treatment <- rbinom(n, 1, 0.5)
true_t    <- rweibull(n, shape = 1.5, scale = ifelse(treatment == 1, 500, 300))

# Visit schedule: every 90 days, up to day 720
visit_times <- seq(0, 720, by = 90)

# For each subject, find which interval contains true_t
L <- R <- numeric(n)
for (i in 1:n) {
  if (true_t[i] > max(visit_times)) {
    L[i] <- max(visit_times); R[i] <- Inf       # right-censored
  } else {
    idx  <- findInterval(true_t[i], visit_times)
    L[i] <- visit_times[idx]
    R[i] <- visit_times[idx + 1]
  }
}

df <- data.frame(id = 1:n, L = L, R = R, treatment = treatment)
```

Compare two analyses on this data: naively treating `(L + R) / 2` as the exact event time (and Inf as right-censored), vs proper interval-censored analysis with `icenReg::ic_par`. The naive analysis is biased.

## Multi-state (illness-death)

```r
set.seed(42)
n <- 500
age <- rnorm(n, 60, 10)

# Transition hazards
h12 <- 0.0008 * exp(0.03 * (age - 60))  # Healthy -> Ill
h13 <- 0.0005 * exp(0.05 * (age - 60))  # Healthy -> Dead
h23 <- 0.002  * exp(0.04 * (age - 60))  # Ill -> Dead

rows <- list()
for (i in 1:n) {
  t_to_ill   <- rexp(1, rate = h12[i])
  t_to_death <- rexp(1, rate = h13[i])
  c_time     <- runif(1, 1000, 3000)
  
  if (t_to_death < t_to_ill && t_to_death < c_time) {
    # Direct Healthy -> Dead
    rows[[i]] <- data.frame(id = i, t_ill = NA, t_death = t_to_death,
                            ill = 0, death = 1, age = age[i])
  } else if (t_to_ill < c_time) {
    # Healthy -> Ill, then maybe Ill -> Dead
    t_in_ill   <- rexp(1, rate = h23[i])
    t_to_death <- t_to_ill + t_in_ill
    if (t_to_death < c_time) {
      rows[[i]] <- data.frame(id = i, t_ill = t_to_ill, t_death = t_to_death,
                              ill = 1, death = 1, age = age[i])
    } else {
      rows[[i]] <- data.frame(id = i, t_ill = t_to_ill, t_death = c_time,
                              ill = 1, death = 0, age = age[i])
    }
  } else {
    # Censored while healthy
    rows[[i]] <- data.frame(id = i, t_ill = NA, t_death = c_time,
                            ill = 0, death = 0, age = age[i])
  }
}
df <- do.call(rbind, rows)
```

Ready for `mstate::msprep` reshape and transition-specific Cox modeling.

## Heavy-tied data (for testing tie handling)

When event times are rounded (monthly cohorts, year of failure), many ties.

```r
set.seed(42)
n <- 500
true_t   <- rexp(n, rate = 1/100)
time     <- ceiling(true_t / 30) * 30   # round to monthly
event    <- rbinom(n, 1, 0.7)            # 70% event rate
df <- data.frame(time = time, event = event,
                 x = rnorm(n))
```

Use to show why `ties = "efron"` matters vs the Breslow default, and when to switch to discrete-time logistic (person-period format).

## Verifying a simulation

After simulating, run two checks:

1. **Visual KM**: does the KM curve look plausible? Median in a sensible range, curve not crashing to zero immediately or staying flat at 1?
2. **Recover the truth**: fit the model you expect (Cox if simulated from PH, Weibull AFT if simulated from Weibull) and check that coefficients are close to the values you put in. They should be — if they're not, the simulation is wrong, not the method.

For competing risks and recurrent events, the recovery is more subtle (cause-specific vs Fine-Gray, AG vs PWP) — match the fitting framework to what you generated.

## When to use which simulation

| Demonstration target | Simulation to use |
|---|---|
| Basic Cox / KM / log-rank | Right-censored from Cox PH |
| Why log-rank fails | Crossing curves OR delayed effect |
| MaxCombo / FH weights / RMST | Delayed effect OR crossing curves |
| Competing risks (naive KM is biased) | Two-cause competing risks |
| Recurrent events (AG vs single-event) | Recurrent with frailty |
| Joint frailty (recurrent + terminal) | Recurrent + competing death |
| Left truncation matters | Age-scale with varying entry ages |
| Interval censoring matters | Periodic-visit interval-censored |
| Multi-state transitions | Illness-death three-state |
| Ties matter | Heavy-tied monthly cohort |
