# brms_alternative.R — the lowest-risk R path.
# brms compiles to Stan for whatever Stan version you have approved, so it sidesteps both the
# hand-written-Stan syntax risk and the PyMC-version problem. It expresses the accuracy (2PL) and
# latency channels cleanly as a multivariate GLMM. The 4PL upper-asymptote (slip) needs a custom
# brms family and is NOT covered here — use stan/joint_glmm.stan for that.
#
# Mapping to the engine's parameters:
#   the nonlinear 2PL gives item difficulty (b) and discrimination (exp(logalpha));
#   (1 | v | variant) on both responses estimates the ability<->effort correlation (van der Linden);
#   ranef(fit) variances are the G-theory variance components; theta = the variant random effects.

library(brms)
library(data.table)

d <- fread("results.csv")                 # columns: taker_id, item_id, score, cot_len[, confidence]
d[, y := as.integer(score >= 0.5)]
d[, lncot := log(pmax(cot_len, 1e-6))]

# ---- Accuracy channel: hierarchical 2PL (probit), item + variant effects ----
# eta = alpha_item * (theta_variant - b_item); 2PL via a nonlinear formula.
bf_acc <- bf(
  y ~ exp(logalpha) * (theta - b),
  theta ~ 0 + (1 | v | taker_id),         # variant ability (shares 'v' group w/ latency for corr)
  b ~ 0 + (1 | item_id),                  # item difficulty
  logalpha ~ 0 + (1 | item_id),           # log discrimination (partial pooling = adaptive shrinkage)
  nl = TRUE, family = bernoulli("probit")
)

# ---- Latency channel: ln(cot) = lam_item - speed_variant ----
bf_lat <- bf(
  lncot ~ 1 + (1 | item_id) + (1 | v | taker_id)   # same 'v' -> estimates ability<->speed correlation
)

priors <- c(
  prior(normal(0, 1),   class = "sd",  resp = "y", nlpar = "b"),
  prior(normal(0, 0.5), class = "sd",  resp = "y", nlpar = "logalpha"),
  prior(normal(0, 1),   class = "sd",  resp = "y", nlpar = "theta"),
  prior(student_t(3,0,2), class = "sd", resp = "lncot")
)

fit <- brm(bf_acc + bf_lat + set_rescor(FALSE),
           data = d, prior = priors, chains = 2, cores = 2,
           iter = 2000, control = list(adapt_delta = 0.95))

print(summary(fit))
# theta per variant:
print(ranef(fit)$taker_id[, , "theta_Intercept"])
# ability<->speed correlation (the van der Linden identifiability term):
print(VarCorr(fit)$taker_id$cor)
# G-theory variance components live in VarCorr(fit); empirical reliability:
# rel = var(theta_hat) / (var(theta_hat) + mean(posterior_var(theta_hat)))
