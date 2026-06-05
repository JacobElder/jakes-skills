#!/usr/bin/env Rscript
# Complete Cox PH example on survival::lung dataset
# Fits a model, checks PH assumption, and plots survival curves

library(survival)
library(survminer)
library(broom)

# Load the data
data(lung)

# Quick data check
head(lung)
cat("Events:", sum(lung$status == 2), "Censored:", sum(lung$status == 1), "\n")

# Fit Cox model with specified predictors
# Note: status == 2 means event occurred, status == 1 means censored
# The Surv() function handles this automatically with the default coding
fit <- coxph(Surv(time, status) ~ age + sex + ph.ecog + ph.karno,
             data = lung, ties = "efron")

# Print summary
summary(fit)

# Tidy output with hazard ratios
cat("\n=== Hazard Ratios with 95% CI ===\n")
print(tidy(fit, exponentiate = TRUE, conf.int = TRUE))

# ============================================================================
# Proportional Hazards Assumption Check
# ============================================================================
cat("\n=== Proportional Hazards Test (cox.zph) ===\n")
zph <- cox.zph(fit)
print(zph)
# Global test p-value > 0.05 suggests PH assumption is reasonable per covariate

# Plot Schoenfeld residuals (scaled)
# Flat line = PH holds; clear trend = PH violated
cat("\nGenerating PH diagnostic plots...\n")
pdf(file = "cox_ph_assumption.pdf", width = 10, height = 8)
plot(zph)
dev.off()
cat("Saved to: cox_ph_assumption.pdf\n")

# ============================================================================
# Predicted Survival for Example Covariate Profiles
# ============================================================================
cat("\n=== Predicted Survival Curves ===\n")

# Define two example profiles to compare
# Profile 1: younger, male, low ECOG, good Karnofsky
profile1 <- data.frame(
  age = 55, sex = 1, ph.ecog = 0, ph.karno = 90
)

# Profile 2: older, female, higher ECOG, lower Karnofsky
profile2 <- data.frame(
  age = 70, sex = 2, ph.ecog = 2, ph.karno = 60
)

profiles <- rbind(profile1, profile2)
profiles$group <- c("Profile 1: age 55, M, ECOG=0, Karn=90",
                     "Profile 2: age 70, F, ECOG=2, Karn=60")

# Predict survival functions
sf <- survfit(fit, newdata = profiles)

# Plot with ggsurvplot for publication quality
p <- ggsurvplot(sf, data = lung,
           conf.int = TRUE,
           legend.labs = profiles$group,
           palette = c("steelblue", "coral"),
           xlab = "Time (days)",
           ylab = "Survival Probability",
           title = "Predicted Survival by Covariate Profile",
           ggtheme = theme_minimal())

print(p)
ggsave("cox_survival_curve.pdf", p, width = 10, height = 6)
cat("Saved to: cox_survival_curve.pdf\n")

# Survival estimates at specific time points
cat("\n=== Survival Estimates at Key Timepoints ===\n")
summary(sf, times = c(180, 365, 730))

# ============================================================================
# Model Diagnostics Summary
# ============================================================================
cat("\n=== Concordance Index ===\n")
cat("C-index:", round(fit$concordance["concordance"], 3), "\n")
cat("(0.5 = random, 1.0 = perfect prediction)\n")

# Influential observations (dfbeta)
cat("\n=== Checking for Influential Observations ===\n")
p_dfbeta <- ggcoxdiagnostics(fit, type = "dfbeta",
                             linear.predictions = FALSE)
print(p_dfbeta)
ggsave("cox_dfbeta.pdf", p_dfbeta, width = 10, height = 6)
cat("Saved to: cox_dfbeta.pdf\n")

cat("\n=== Script Complete ===\n")
cat("Generated files:\n")
cat("  - cox_ph_assumption.pdf (Schoenfeld residual plots)\n")
cat("  - cox_survival_curve.pdf (predicted survival curves)\n")
cat("  - cox_dfbeta.pdf (influence diagnostics)\n")
