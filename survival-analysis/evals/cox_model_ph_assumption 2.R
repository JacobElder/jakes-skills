library(survival)
library(ggplot2)

# Load data
data(lung)

# Fit Cox proportional hazards model
cox_fit <- coxph(
  Surv(time, status) ~ age + sex + ph.ecog + ph.karno,
  data = lung
)

# Display model summary
cat("=== Cox Model Summary ===\n")
print(summary(cox_fit))

# Test proportional hazards assumption
ph_test <- cox.zph(cox_fit)

cat("\n=== Proportional Hazards Assumption Test ===\n")
print(ph_test)

# Plot PH diagnostic plots
cat("\nGenerating PH assumption diagnostic plots...\n")
par(mfrow = c(2, 2))
plot(ph_test)
par(mfrow = c(1, 1))

# Create survival curve for example covariate profile
# Use median values for continuous variables, reference level for categorical
example_profile <- data.frame(
  age = median(lung$age, na.rm = TRUE),
  sex = 1,  # Male (reference level)
  ph.ecog = 1,
  ph.karno = median(lung$ph.karno, na.rm = TRUE)
)

cat("\n=== Example Covariate Profile ===\n")
print(example_profile)

# Fit survival curve for the example profile
surv_curve <- survfit(cox_fit, newdata = example_profile)

# Plot survival curve
plot(
  surv_curve,
  main = "Predicted Survival Curve\n(Median Age, Male, ph.ecog=1, Median ph.karno)",
  xlab = "Time (days)",
  ylab = "Survival Probability",
  lwd = 2,
  col = "steelblue"
)
grid()

# Alternative: ggplot2 version
surv_df <- data.frame(
  time = surv_curve$time,
  survival = surv_curve$surv,
  lower = surv_curve$lower,
  upper = surv_curve$upper
)

p <- ggplot(surv_df, aes(x = time, y = survival)) +
  geom_step(color = "steelblue", linewidth = 1) +
  geom_ribbon(aes(ymin = lower, ymax = upper), alpha = 0.2, fill = "steelblue") +
  labs(
    title = "Predicted Survival Curve",
    subtitle = "Median Age, Male, ph.ecog=1, Median ph.karno",
    x = "Time (days)",
    y = "Survival Probability"
  ) +
  theme_minimal() +
  theme(plot.title = element_text(face = "bold", size = 12))

print(p)
