library(survival)
library(ggplot2)

# Load and prepare data
data(lung)
lung_clean <- lung[complete.cases(lung[, c("time", "status", "age", "sex", "ph.ecog", "ph.karno")]), ]

# Fit Cox model
cox_model <- coxph(Surv(time, status) ~ age + sex + ph.ecog + ph.karno, data = lung_clean)

# Display model summary
print(summary(cox_model))

# Check proportional hazards assumption
ph_test <- cox.zph(cox_model)
print(ph_test)

# Plot PH assumption diagnostics
pdf("ph_assumption_diagnostics.pdf", width = 10, height = 8)
par(mfrow = c(2, 2))
plot(ph_test)
par(mfrow = c(1, 1))
dev.off()

# Create example covariate profiles
newdata <- data.frame(
  age = c(50, 60, 70),
  sex = c(1, 1, 1),           # 1 = male
  ph.ecog = c(0, 0, 1),       # ECOG performance status
  ph.karno = c(90, 80, 70)    # Karnofsky score
)

# Predict survival curves
surv_pred <- survfit(cox_model, newdata = newdata)

# Plot survival curves
plot(surv_pred,
     main = "Cox Model: Predicted Survival Curves",
     xlab = "Time (days)",
     ylab = "Survival Probability",
     col = c("blue", "green", "red"),
     lty = 1,
     lwd = 2)

# Add legend with covariate profiles
legend("topright",
       legend = c("Age=50, ECOG=0, Karno=90",
                  "Age=60, ECOG=0, Karno=80",
                  "Age=70, ECOG=1, Karno=70"),
       col = c("blue", "green", "red"),
       lty = 1,
       lwd = 2)

# Alternative: ggplot2 visualization
surv_tidy <- fortify(surv_pred, newdata = newdata)
surv_tidy$profile <- paste0("Age=", newdata$age[surv_tidy$strata],
                            ", ECOG=", newdata$ph.ecog[surv_tidy$strata],
                            ", Karno=", newdata$ph.karno[surv_tidy$strata])

p <- ggplot(surv_tidy, aes(x = time, y = surv, color = profile)) +
  geom_step() +
  geom_point(aes(y = surv), data = subset(surv_tidy, n.event > 0), size = 2) +
  labs(title = "Predicted Survival Curves from Cox Model",
       x = "Time (days)",
       y = "Survival Probability",
       color = "Covariate Profile") +
  theme_minimal() +
  theme(legend.position = "bottomleft")

print(p)
ggsave("survival_curves.pdf", p, width = 8, height = 6)

# Summary statistics for predicted survival
print("Predicted 1-year survival probabilities:")
print(summary(surv_pred, times = 365))
