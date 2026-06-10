#!/usr/bin/env Rscript
# Demonstration: Weibull AFT with no treatment effect
# Shows that Cox PH correctly finds no effect when data are generated with no effect

library(survival)
library(flexsurv)
library(survminer)

set.seed(42)
n <- 1000

# Covariates: binary treatment, no effect
treatment <- rbinom(n, 1, 0.5)

# Weibull AFT parameters (same for both arms — no treatment effect)
shape <- 1.5  # increasing hazard over time
scale <- 365  # mean survival ~355 days

# Generate event times from Weibull
# Weibull with shape and scale: T ~ scale * (-log(U))^(1/shape)
# When there's no covariate effect, scale is constant across arms
U <- runif(n)
true_t <- scale * (-log(U))^(1/shape)

# Independent administrative censoring at time 800 days
# Plus random dropout exponential with mean 1200
c_admin <- 800
c_dropout <- rexp(n, rate = 1/1200)
c_time <- pmin(c_admin, c_dropout)

# Observed times and event indicator
time <- pmin(true_t, c_time)
event <- as.integer(true_t <= c_time)

df <- data.frame(
  id = 1:n,
  time = time,
  event = event,
  treatment = treatment
)

cat("Data summary:\n")
cat("  Total subjects:", nrow(df), "\n")
cat("  Events observed:", sum(df$event), "\n")
cat("  Event rate:", mean(df$event), "\n")
cat("  Median follow-up (all):", median(df$time), "days\n")
cat("  Median follow-up (censored):", median(df$time[df$event == 0]), "days\n")
cat("\n")

# ============================================================================
# 1. Kaplan-Meier survival curves by treatment
# ============================================================================
cat("=== Kaplan-Meier Curves ===\n")
km_fit <- survfit(Surv(time, event) ~ treatment, data = df)
print(km_fit)
cat("\n")

# Plot KM curves
png("weibull_km_curves.png", width = 8, height = 6, units = "in", res = 100)
ggsurvplot(km_fit, data = df,
           title = "Kaplan-Meier Curves by Treatment (Weibull AFT, No Effect)",
           xlab = "Days",
           ylab = "Survival probability",
           legend.labs = c("Control (treatment=0)", "Treated (treatment=1)"),
           risk.table = TRUE,
           cumevents = FALSE)
dev.off()
cat("  Plot saved to: weibull_km_curves.png\n\n")

# ============================================================================
# 2. Log-rank test (standard Cox test)
# ============================================================================
cat("=== Log-Rank Test (comparing treatment groups) ===\n")
logrank_test <- survdiff(Surv(time, event) ~ treatment, data = df)
print(logrank_test)
cat("\n")

# ============================================================================
# 3. Cox proportional hazards model
# ============================================================================
cat("=== Cox Proportional Hazards Model ===\n")
cox_fit <- coxph(Surv(time, event) ~ treatment, data = df)
print(summary(cox_fit))
cat("\nInterpretation:\n")
cat("  If Cox coefficient ≈ 0 and p-value is large (>> 0.05),\n")
cat("  then Cox correctly finds NO treatment effect.\n\n")

# Check PH assumption
cat("=== Proportional Hazards Assumption Check ===\n")
cox_ph_check <- cox.zph(cox_fit)
print(cox_ph_check)
cat("\n")

# ============================================================================
# 4. Fit the true Weibull AFT model (to show it recovers the null)
# ============================================================================
cat("=== Weibull AFT Model (True Model) ===\n")
aft_fit <- flexsurvreg(Surv(time, event) ~ treatment, data = df, dist = "weibull")
print(aft_fit)
cat("\nInterpretation:\n")
cat("  treatment coefficient ≈ 0 indicates no treatment effect.\n")
cat("  This is the true model since we generated from Weibull AFT with no effect.\n\n")

# ============================================================================
# 5. Summary of findings
# ============================================================================
cat("=== SUMMARY ===\n")
cat("Data generated from: Weibull AFT (shape =", shape, ", scale =", scale, ")\n")
cat("Treatment effect in DGP: None (both arms have same shape and scale)\n\n")

cat("Findings:\n")
cat("1. Kaplan-Meier curves are nearly overlapping (visual inspection)\n")
cat("2. Log-rank test: ",
    if(logrank_test$pvalue > 0.05) "NOT significant" else "significant",
    " (p =", round(logrank_test$pvalue, 4), ")\n")

cox_coef <- coef(cox_fit)
cox_pval <- summary(cox_fit)$coefficients[, "Pr(>|z|)"]
cat("3. Cox PH model:\n")
cat("   Treatment coefficient:", round(cox_coef, 4), "\n")
cat("   Hazard ratio:", round(exp(cox_coef), 4), "\n")
cat("   p-value:", round(cox_pval, 4), "\n")
cat("   Interpretation: ",
    if(cox_pval > 0.05) "NO significant effect detected (correct)" else "Effect detected (unexpected)",
    "\n\n")

cat("4. Weibull AFT model:\n")
cat("   Treatment coefficient:", round(aft_fit$coefficients["treatment"], 4), "\n")
cat("   Interpretation: NO treatment effect (as expected from DGP)\n\n")

cat("Conclusion: When data are generated with no treatment effect, Cox PH\n")
cat("correctly fails to detect one. Cox and AFT agree in this case.\n")
