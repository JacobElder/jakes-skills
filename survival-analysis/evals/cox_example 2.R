#!/usr/bin/env Rscript
# Complete Cox PH example on survival::lung dataset
# Fits a model, checks PH assumption, plots survival curves

library(survival)
library(survminer)

# ============================================================================
# PART 1: Setup and descriptive analysis
# ============================================================================

data(lung)
cat("=== Lung Cancer Dataset ===\n")
cat("N =", nrow(lung), "| Events:", sum(lung$status == 2),
    "| Censored:", sum(lung$status == 1), "\n\n")

# Kaplan-Meier curve first: always start here before any modeling
km_overall <- survfit(Surv(time, status) ~ 1, data = lung)
cat("=== Overall Kaplan-Meier Estimate ===\n")
print(km_overall)

# Plot overall survival with number at risk table (essential)
ggsurvplot(km_overall, data = lung,
           title = "Overall Survival",
           xlab = "Time (days)", ylab = "Survival Probability",
           risk.table = TRUE, risk.table.height = 0.25,
           conf.int = TRUE)

# ============================================================================
# PART 2: Fit Cox proportional hazards model
# ============================================================================

fit <- coxph(Surv(time, status) ~ age + sex + ph.ecog + ph.karno,
             data = lung, ties = "efron")

cat("\n=== Cox PH Model Summary ===\n")
summary(fit)

# ============================================================================
# PART 3: CHECK PROPORTIONAL HAZARDS ASSUMPTION (non-negotiable)
# ============================================================================
cat("\n=== PROPORTIONAL HAZARDS ASSUMPTION CHECK ===\n")
cat("Rule: If p > 0.05, PH assumption is NOT violated at the 0.05 level.\n")
cat("But LOOK AT THE PLOTS. A flat line = PH holds; a trend = PH violated.\n")
cat("The p-value is oversensitive in large samples, so visual inspection is key.\n\n")

zph <- cox.zph(fit)
print(zph)

# Plot scaled Schoenfeld residuals vs time for each covariate
# Expect a roughly flat, symmetric band around zero
cat("\nPlotting PH diagnostics (4-panel figure)...\n")
par(mfrow = c(2, 2), mar = c(4, 4, 2, 2))
plot(zph)
mtext("Scaled Schoenfeld Residuals\nFlat line = PH OK; Trend = PH violated",
      outer = TRUE, line = -1, cex = 0.9)
par(mfrow = c(1, 1))

# ============================================================================
# PART 4: Hazard ratios with interpretation
# ============================================================================
cat("\n=== HAZARD RATIOS (95% Confidence Intervals) ===\n")
cat("Remember: HR is instantaneous risk, not cumulative.\n")
cat("HR = 1.5 means 'at any given moment, 50% higher hazard'.\n\n")

coef_summary <- summary(fit)$coefficients[, c(1, 2, 5)]
hr_table <- data.frame(
  Variable = rownames(coef_summary),
  HR = exp(coef(fit)),
  LCI = exp(coef(fit) - 1.96 * coef_summary[, 2]),
  UCI = exp(coef(fit) + 1.96 * coef_summary[, 2]),
  "p-value" = coef_summary[, 3],
  row.names = NULL
)
print(hr_table)

cat("\nInterpretation guide:\n")
cat("- age:     HR per 1-year increase\n")
cat("- sex=2:   HR for female (coded 2) vs male (coded 1)\n")
cat("- ph.ecog: HR per 1-unit increase in ECOG score (worse performance)\n")
cat("- ph.karno: HR per 1-unit increase in Karnofsky score (better performance)\n")

# ============================================================================
# PART 5: Predicted survival for example covariate profiles
# ============================================================================
cat("\n=== PREDICTED SURVIVAL CURVES ===\n")

# Profile 1: Younger, male, good performance status
profile1 <- data.frame(
  age = 55, sex = 1, ph.ecog = 0, ph.karno = 90
)

# Profile 2: Older, female, poor performance status
profile2 <- data.frame(
  age = 70, sex = 2, ph.ecog = 2, ph.karno = 60
)

profiles <- rbind(profile1, profile2)
profiles$label <- c(
  "Profile 1: Age 55, Male, ECOG=0, Karnofsky=90",
  "Profile 2: Age 70, Female, ECOG=2, Karnofsky=60"
)

# Predict survival curves from the Cox model
sf <- survfit(fit, newdata = profiles)

# Plot with number at risk table
p <- ggsurvplot(sf, data = lung,
           conf.int = TRUE,
           legend.labs = profiles$label,
           palette = c("steelblue", "coral"),
           xlab = "Time (days)",
           ylab = "Survival Probability",
           title = "Predicted Survival by Covariate Profile\n(from Cox PH model)",
           risk.table = TRUE, risk.table.height = 0.25,
           ggtheme = theme_minimal())
print(p)

# Survival probabilities at key timepoints
cat("\n=== Survival Probabilities at Selected Timepoints ===\n")
cat("Profile 1 (age 55, M, ECOG=0, Karn=90):\n")
summary(sf[1], times = c(90, 180, 365))
cat("\nProfile 2 (age 70, F, ECOG=2, Karn=60):\n")
summary(sf[2], times = c(90, 180, 365))

# ============================================================================
# PART 6: Check for influential observations
# ============================================================================
cat("\n=== INFLUENTIAL OBSERVATIONS (dfbeta residuals) ===\n")
cat("Outliers in dfbeta may have outsized influence on the model.\n")

dfbeta_vals <- residuals(fit, type = "dfbeta")
par(mfrow = c(2, 2), mar = c(4, 4, 2, 2))
for (i in 1:4) {
  plot(dfbeta_vals[, i], main = colnames(dfbeta_vals)[i],
       xlab = "Observation", ylab = "dfbeta")
  abline(h = 0, col = "gray", lty = 2)
}
par(mfrow = c(1, 1))

# ============================================================================
# PART 7: Summary
# ============================================================================
cat("\n=== MODEL CONCORDANCE INDEX ===\n")
cat("C-index:", round(fit$concordance["concordance"], 3), "\n")
cat("Range: 0.5 (random) to 1.0 (perfect discrimination)\n")

cat("\n=== WORKFLOW CHECKLIST ===\n")
cat("✓ Kaplan-Meier plotted (starting point)\n")
cat("✓ Cox model fitted\n")
cat("✓ PH assumption checked (see residual plots above)\n")
cat("✓ Hazard ratios reported with 95% CIs\n")
cat("✓ Predicted curves plotted for example profiles\n")
cat("✓ Influential observations assessed\n")
cat("✓ C-index reported\n")
cat("\nScript complete.\n")
