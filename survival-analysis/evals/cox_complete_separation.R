#!/usr/bin/env Rscript
# Cox model with complete separation: treated (n=80) all censored vs untreated (n=120) all events
# This demonstrates what happens when predictors perfectly separate outcomes

library(survival)
library(survminer)

# ============================================================================
# PART 1: Create data with complete separation
# ============================================================================

set.seed(123)
n_treated <- 80
n_untreated <- 120

# Treated subjects: all censored (event=0)
treated <- data.frame(
  subject_id = 1:n_treated,
  treatment = 1,
  time = runif(n_treated, min = 100, max = 1000),  # arbitrary times
  event = 0  # all censored
)

# Untreated subjects: all events (event=1)
untreated <- data.frame(
  subject_id = (n_treated + 1):(n_treated + n_untreated),
  treatment = 0,
  time = runif(n_untreated, min = 10, max = 500),  # earlier deaths
  event = 1  # all dead
)

data <- rbind(treated, untreated)

cat("=== Data Summary ===\n")
cat("N total:", nrow(data), "\n")
cat("Treated (treatment=1):", sum(data$treatment == 1), "| Events:", sum(data$treatment == 1 & data$event == 1), "| Censored:", sum(data$treatment == 1 & data$event == 0), "\n")
cat("Untreated (treatment=0):", sum(data$treatment == 0), "| Events:", sum(data$treatment == 0 & data$event == 1), "| Censored:", sum(data$treatment == 0 & data$event == 0), "\n\n")

# ============================================================================
# PART 2: Attempt to fit Cox model
# ============================================================================

cat("=== Fitting Cox PH Model ===\n")
cat("NOTE: This data has COMPLETE SEPARATION (treated=all censored, untreated=all events).\n")
cat("This violates the assumption that both groups have both censored and event subjects.\n")
cat("The model may fail to converge or produce unreliable estimates.\n\n")

fit <- tryCatch({
  coxph(Surv(time, event) ~ treatment, data = data)
}, error = function(e) {
  cat("ERROR during fitting:\n")
  print(e)
  return(NULL)
}, warning = function(w) {
  cat("WARNING during fitting:\n")
  print(w)
  return(NULL)
})

if (!is.null(fit)) {
  cat("\n=== Cox PH Model Summary ===\n")
  print(summary(fit))

  cat("\n=== Hazard Ratio (Treatment effect) ===\n")
  hr <- exp(coef(fit)["treatment"])
  cat("HR (treated vs untreated):", hr, "\n")
  cat("Interpretation: Treated subjects have", round((1 - hr) * 100), "% lower hazard\n")
  cat("(However, this estimate is unreliable due to complete separation.)\n")
}

# ============================================================================
# PART 3: Kaplan-Meier curves (informative despite model issues)
# ============================================================================

cat("\n=== Kaplan-Meier Curves by Treatment ===\n")
km_fit <- survfit(Surv(time, event) ~ treatment, data = data)
print(km_fit)

p <- ggsurvplot(km_fit, data = data,
                title = "Survival by Treatment Group (Complete Separation)",
                xlab = "Time", ylab = "Survival Probability",
                legend.labs = c("Untreated", "Treated"),
                palette = c("red", "blue"),
                risk.table = TRUE, risk.table.height = 0.25,
                ggtheme = theme_minimal())
print(p)

# ============================================================================
# PART 4: What went wrong and why
# ============================================================================

cat("\n=== DIAGNOSIS: COMPLETE SEPARATION ===\n")
cat("✗ Treated group (treatment=1):  80 subjects, 0 events, 80 censored\n")
cat("✗ Untreated group (treatment=0): 120 subjects, 120 events, 0 censored\n\n")

cat("This is a structural problem for Cox regression because:\n")
cat("1. The likelihood is unbounded (coefficient → ∞ as it tries to perfectly separate)\n")
cat("2. Standard errors become unreliable or infinite\n")
cat("3. The model cannot distinguish between 'strong effect' and 'measurement artifact'\n\n")

cat("SOLUTION: Add covariates that vary within treatment groups\n")
cat("(So some treated subjects have events and some untreated are censored)\n")
cat("This reduces separation and stabilizes estimates.\n")
