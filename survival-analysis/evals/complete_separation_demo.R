library(survival)

# Create the data
set.seed(42)
n_treated <- 80
n_untreated <- 120

data <- data.frame(
  id = 1:(n_treated + n_untreated),
  treatment = c(rep(1, n_treated), rep(0, n_untreated)),
  time = c(runif(n_treated, 1, 10), runif(n_untreated, 1, 10)),
  event = c(rep(0, n_treated), rep(1, n_untreated))  # Perfect separation
)

# Try to fit Cox model
fit <- coxph(Surv(time, event) ~ treatment, data = data)

# This will produce:
# - Infinite or NA coefficients
# - Infinite standard errors
# - NA hazard ratio
print(summary(fit))

# Check the actual counts by treatment
table(data$treatment, data$event)
