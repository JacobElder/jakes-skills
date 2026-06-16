#!/usr/bin/env Rscript
# sdt.R — R mirror of scripts/sdt.py for the signal-detection-theory skill.
# Same conventions, same numbers. Use whichever language fits your pipeline;
# for serious model-based work in R prefer brms/lme4/sensR (see references/).
#
# Conventions (identical to sdt.py):
#   z(p) = qnorm(p);  d' = z(H) - z(F)
#   c = -0.5*(z(H)+z(F));  c>0 conservative, c<0 liberal
#   ln(beta) = c*d';  beta = exp(ln beta)
#   UNEQUAL VARIANCE: s = z-ROC slope = sigma_noise/sigma_signal
#       d_a = sqrt(2/(1+s^2)) * (z(H) - s*z(F))   [reduces to d' at s=1]
#       A_z = pnorm(d_a/sqrt(2))

# ---- rates and corrections -------------------------------------------------
sdt_rates <- function(hits, misses, fas, crs, correction = "loglinear") {
  n_signal <- hits + misses
  n_noise  <- fas + crs
  if (correction == "loglinear") {
    H <- (hits + 0.5) / (n_signal + 1)
    F <- (fas  + 0.5) / (n_noise  + 1)
  } else if (correction == "2N") {
    H <- hits / n_signal; F <- fas / n_noise
    if (H == 0) H <- 1 / (2 * n_signal) else if (H == 1) H <- 1 - 1 / (2 * n_signal)
    if (F == 0) F <- 1 / (2 * n_noise)  else if (F == 1) F <- 1 - 1 / (2 * n_noise)
  } else if (correction == "none") {
    H <- hits / n_signal; F <- fas / n_noise
  } else stop("unknown correction")
  c(H = H, F = F)
}

# ---- equal-variance measures ----------------------------------------------
dprime    <- function(H, F) qnorm(H) - qnorm(F)
criterion <- function(H, F) -0.5 * (qnorm(H) + qnorm(F))
c_prime   <- function(H, F) { d <- dprime(H, F); if (d == 0) NA else criterion(H, F) / d }
ln_beta   <- function(H, F) criterion(H, F) * dprime(H, F)
beta_     <- function(H, F) exp(ln_beta(H, F))

# ---- unequal-variance measures --------------------------------------------
da <- function(H, F, s) sqrt(2 / (1 + s^2)) * (qnorm(H) - s * qnorm(F))
az_from_da <- function(d_a) pnorm(d_a / sqrt(2))
criterion_uv <- function(H, F, s) -(qnorm(H) + qnorm(F)) / (1 + s)  # ->c at s=1

# ---- inference: SE of d' (delta method) -----------------------------------
var_dprime <- function(H, F, n_signal, n_noise) {
  (H * (1 - H)) / (n_signal * dnorm(qnorm(H))^2) +
  (F * (1 - F)) / (n_noise  * dnorm(qnorm(F))^2)
}
se_dprime <- function(H, F, n_signal, n_noise) sqrt(var_dprime(H, F, n_signal, n_noise))
dprime_ci <- function(H, F, n_signal, n_noise, level = 0.95) {
  d <- dprime(H, F); se <- se_dprime(H, F, n_signal, n_noise)
  zc <- qnorm(0.5 + level / 2); c(lower = d - zc * se, upper = d + zc * se)
}
dprime_test_zero <- function(H, F, n_signal, n_noise) {
  d <- dprime(H, F); se <- se_dprime(H, F, n_signal, n_noise)
  zstat <- d / se; c(z = zstat, p_two_sided = 2 * (1 - pnorm(abs(zstat))))
}

# ---- optimal criterion (base rates + payoffs) -----------------------------
optimal_criterion <- function(p_signal, dprime_val,
                              v_hit = 1, v_cr = 1, c_miss = 1, c_fa = 1) {
  beta_opt <- ((1 - p_signal) / p_signal) * ((v_cr + c_fa) / (v_hit + c_miss))
  c(beta_opt = beta_opt, c_opt = if (dprime_val != 0) log(beta_opt) / dprime_val else NA)
}

# ---- forced choice ---------------------------------------------------------
dprime_2afc <- function(pc) sqrt(2) * qnorm(pc)

# ---- z-ROC fit from rating counts (least squares; see fit_zroc_mle in .py) -
fit_zroc <- function(signal_counts, noise_counts) {
  s_adj <- signal_counts + 0.5; n_adj <- noise_counts + 0.5
  cumH <- head(cumsum(s_adj), -1) / sum(s_adj)
  cumF <- head(cumsum(n_adj), -1) / sum(n_adj)
  fit <- lm(qnorm(cumH) ~ qnorm(cumF))
  s_slope <- unname(coef(fit)[2]); a_int <- unname(coef(fit)[1])
  list(zroc_slope_s = s_slope, zroc_intercept_a = a_int,
       da = sqrt(2 / (1 + s_slope^2)) * a_int,
       Az = pnorm(a_int / sqrt(1 + s_slope^2)))
}

# ---- full report -----------------------------------------------------------
sdt_report <- function(hits, misses, fas, crs, correction = "loglinear") {
  r <- sdt_rates(hits, misses, fas, crs, correction); H <- r["H"]; F <- r["F"]
  data.frame(n_signal = hits + misses, n_noise = fas + crs,
             hit_rate = round(H, 4), fa_rate = round(F, 4), correction = correction,
             dprime = round(dprime(H, F), 4), criterion_c = round(criterion(H, F), 4),
             c_relative = round(c_prime(H, F), 4), beta = round(beta_(H, F), 4),
             se_dprime = round(se_dprime(H, F, hits + misses, fas + crs), 4),
             row.names = NULL)
}

# ---- self-check when run directly (cross-validates against sdt.py values) --
if (sys.nframe() == 0) {
  cat("sdt.R self-check\n")
  print(sdt_report(45, 5, 12, 38))                       # d'≈1.93, c≈-0.27
  cat("da(0.85,0.30,s=0.75) =", round(da(0.85, 0.30, 0.75), 4), "(expect 1.618)\n")
  cat("dprime_2afc(0.80)    =", round(dprime_2afc(0.80), 4), "(expect 1.190)\n")
  cat("SE d'(.892,.245,50,50)=",
      round(se_dprime(0.8922, 0.2451, 50, 50), 4), "\n")
  print(round(optimal_criterion(0.2, 2.0), 4))           # beta_opt=4, c_opt>0
}
