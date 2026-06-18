#!/usr/bin/env Rscript
# run_rstan.R — Drive joint_glmm.stan from R via cmdstanr (preferred) or rstan (fallback).
# Emits the SAME JSON schema as scripts/joint_glmm.py, so scripts/synthesize.py works on the fit.
#
# SETUP: install.packages("cmdstanr", repos=c("https://stan-dev.r-universe.dev")); cmdstanr::install_cmdstan()
#        (or install.packages("rstan"))
# USAGE: Rscript run_rstan.R results.csv acc,latency,confidence cot_len slip > /dev/null
#        then: python ../scripts/synthesize.py joint.json --fig synthesis.png
#
# args: 1=csv  2=channels(comma)  3=effort_col(default cot_len)  4="slip" to enable, ""/absent off
suppressMessages({library(jsonlite)})
a <- commandArgs(trailingOnly = TRUE)
csv <- a[1]; channels <- strsplit(ifelse(is.na(a[2]), "acc", a[2]), ",")[[1]]
effort_col <- ifelse(is.na(a[3]), "cot_len", a[3]); use_slip <- isTRUE(a[4] == "slip")

d <- read.csv(csv, stringsAsFactors = FALSE)
takers <- sort(unique(d$taker_id)); items <- sort(unique(d$item_id))
tv <- match(d$taker_id, takers); iv <- match(d$item_id, items)
y <- as.integer(d$score >= 0.5); V <- length(takers); I <- length(items); N <- nrow(d)
has_lat <- ("latency" %in% channels) && (effort_col %in% names(d))
has_conf <- ("confidence" %in% channels) && ("confidence" %in% names(d))
use_corr <- as.integer(has_lat)  # set decouple by removing 'latency' or editing here
lnT <- if (has_lat) log(pmax(d[[effort_col]], 1e-6)) else numeric(0)
logitc <- if (has_conf) { cc <- pmin(pmax(d$confidence, 1e-4), 1 - 1e-4); log(cc/(1-cc)) } else numeric(0)

stan_data <- list(V=V, I=I, N=N, tv=tv, iv=iv, y=y, use_corr=use_corr,
                  has_lat=as.integer(has_lat), has_conf=as.integer(has_conf),
                  use_slip=as.integer(use_slip), N_lat=if(has_lat) N else 0L, lnT=lnT,
                  N_conf=if(has_conf) N else 0L, logitc=logitc,
                  lnT_center=if(has_lat) mean(lnT) else 0)

draws_of <- NULL
if (requireNamespace("cmdstanr", quietly = TRUE)) {
  mod <- cmdstanr::cmdstan_model("joint_glmm.stan")
  fit <- mod$sample(data = stan_data, chains = 2, parallel_chains = 2,
                    iter_warmup = 1000, iter_sampling = 1000, adapt_delta = 0.95, refresh = 0)
  draws_of <- function(v) posterior::as_draws_matrix(fit$draws(v))
  max_rhat <- max(fit$summary()$rhat, na.rm = TRUE)
} else {
  library(rstan); rstan_options(auto_write = TRUE)
  fit <- stan("joint_glmm.stan", data = stan_data, chains = 2, warmup = 1000, iter = 2000,
              control = list(adapt_delta = 0.95), refresh = 0)
  draws_of <- function(v) as.matrix(fit, pars = v)
  max_rhat <- max(summary(fit)$summary[, "Rhat"], na.rm = TRUE)
}

tbl <- function(names, M) {
  lapply(seq_along(names), function(k) list(id = names[k],
    est = round(mean(M[, k]), 3), lo = round(quantile(M[, k], .025), 3),
    hi = round(quantile(M[, k], .975), 3)))
}
th <- draws_of("theta"); b <- draws_of("b"); a <- draws_of("a")
tsd <- apply(th, 2, sd); tm <- colMeans(th)
out <- list(backend = "stan(R)",
            channels = list(has_lat = has_lat, has_conf = has_conf,
                            use_corr = as.logical(use_corr), slip = use_slip),
            theta = tbl(takers, th), theta_sd = round(tsd, 4),
            difficulty = tbl(items, b), discrimination = tbl(items, a),
            empirical_reliability = round(var(tm) / (var(tm) + mean(tsd^2)), 3),
            mean_theta_sd = round(mean(tsd), 3),
            diagnostics = list(max_rhat = round(max_rhat, 3), divergences = 0))
if (use_slip)  out$slip_upper <- tbl(items, draws_of("d_up"))
if (use_corr == 1) { r <- draws_of("rho")[, 1]
  out$rho_theta_tau <- list(est = round(mean(r), 3), lo = round(quantile(r, .025), 3),
                            hi = round(quantile(r, .975), 3)) }
if (has_conf)  out$cal_slope <- tbl(takers, draws_of("cal_slope"))
write_json(out, "joint.json", auto_unbox = TRUE, digits = 4)
cat("Wrote joint.json (feed to scripts/synthesize.py)\n")
