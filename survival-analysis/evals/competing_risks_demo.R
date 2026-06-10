library(survival)
library(cmprsk)

set.seed(42)
n <- 500

# Simulate covariates
treatment <- rbinom(n, 1, 0.5)
age <- rnorm(n, mean = 65, sd = 10)

# Simulate competing risks with OPPOSITE treatment effects
# Cause 1 (primary): treatment INCREASES risk
lambda1 <- 0.010 * exp(0.9 * treatment + 0.015 * (age - 65))
T1 <- rexp(n, rate = lambda1)

# Cause 2 (competing): treatment DECREASES risk (protective)
# This creates strong competition
lambda2 <- 0.012 * exp(-0.8 * treatment + 0.010 * (age - 65))
T2 <- rexp(n, rate = lambda2)

# Observed time is the minimum; event indicates which cause occurred first
time <- pmin(T1, T2)
cause <- ifelse(T1 < T2, 1, 2)

# Add administrative censoring at 75th percentile
tau <- quantile(time, 0.75)
event <- ifelse(time <= tau, cause, 0)
time <- pmin(time, tau)

# Create dataset
data <- data.frame(time = time, event = event, treatment = treatment, age = age)

cat("=== Competing Risks Simulation (Opposite Treatment Effects) ===\n")
cat("Subjects:", n, "\n")
cat("Cause 1 events:", sum(event == 1), "\n")
cat("Cause 2 events:", sum(event == 2), "\n")
cat("Censored:", sum(event == 0), "\n\n")

# ============================================
# APPROACH 1: Cause-Specific Cox Regression
# ============================================
# Treats cause 2 as censoring (ignores competing risk)
cs_cox <- coxph(Surv(time, event == 1) ~ treatment + age, data = data)

cat("CAUSE-SPECIFIC COX MODEL FOR CAUSE 1\n")
cat("(treats cause 2 as censoring)\n")
print(summary(cs_cox))
cs_hr_treatment <- exp(coef(cs_cox)["treatment"])
cat("\nTreatment HR (cause-specific):", round(cs_hr_treatment, 4), "\n\n")

# ============================================
# APPROACH 2: Fine-Gray Model
# ============================================
# Accounts for competing risk via subdistribution hazard
fg_model <- crr(ftime = data$time,
                fstatus = data$event,
                cov1 = data[, c("treatment", "age")])

cat("FINE-GRAY MODEL FOR CAUSE 1\n")
cat("(accounts for competing risk via subdistribution hazard)\n")
cat("\nCoefficients:\n")
print(fg_model$coef)
cat("\nHazard Ratios:\n")
print(exp(fg_model$coef))
fg_hr_treatment <- exp(fg_model$coef["treatment"])
cat("\nTreatment HR (Fine-Gray):", round(fg_hr_treatment, 4), "\n\n")

# ============================================
# COMPARISON
# ============================================
cat("=== COMPARISON ===\n")
cat("Cause-specific Cox HR:  ", round(cs_hr_treatment, 4), "\n")
cat("Fine-Gray HR:           ", round(fg_hr_treatment, 4), "\n")
cat("Difference in HR:       ", round(cs_hr_treatment - fg_hr_treatment, 4), "\n")
cat("Percent difference:     ", round(100 * (cs_hr_treatment - fg_hr_treatment) / fg_hr_treatment, 1), "%\n\n")

cat("WHY THEY DIFFER:\n")
cat("- Cause-specific Cox: Treatment increases cause 1 hazard (HR=", round(cs_hr_treatment, 3), ")\n")
cat("  but IGNORES that treatment decreases cause 2 (competing event)\n\n")
cat("- Fine-Gray: Accounts for the fact that reduced cause 2 means\n")
cat("  LESS COMPETITION for cause 1, AMPLIFYING the effect (HR=", round(fg_hr_treatment, 3), ")\n\n")
cat("INTERPRETATION:\n")
cat("Because treatment protects against cause 2, fewer treated subjects\n")
cat("are 'removed' by competing risk, so more end up with cause 1.\n")
cat("The cumulative incidence effect is LARGER than the\n")
cat("instantaneous hazard effect because of reduced competition.\n\n")

# ============================================
# PLOT CUMULATIVE INCIDENCE FUNCTIONS
# ============================================
cat("Generating cumulative incidence plot...\n")

# Compute non-parametric CIFs by treatment group
cifs <- cuminc(ftime = data$time, fstatus = data$event, group = data$treatment)

png("competing_risks_cif_plot.png", width = 10, height = 6, units = "in", res = 120)
plot(cifs,
     main = "Cumulative Incidence Functions: Cause 1 by Treatment Group",
     xlab = "Time",
     ylab = "Cumulative Incidence of Cause 1",
     lty = c(1, 2, 1, 2),
     col = c("darkred", "darkred", "darkblue", "darkblue"),
     lwd = 2.5)
legend("topleft",
       legend = c("Cause 1 (Control)", "Cause 1 (Treatment)",
                  "Cause 2 (Control)", "Cause 2 (Treatment)"),
       lty = c(1, 2, 1, 2),
       col = c("darkred", "darkred", "darkblue", "darkblue"),
       bty = "n",
       cex = 1.1)
dev.off()

cat("\nPlot saved to competing_risks_cif_plot.png\n")
cat("\nKEY TAKEAWAY:\n")
cat("The CURVES (cumulative incidence by group) reflect the Fine-Gray effect.\n")
cat("Treatment lowers cause 1 CIF because of competition from a protective effect on cause 2.\n")
