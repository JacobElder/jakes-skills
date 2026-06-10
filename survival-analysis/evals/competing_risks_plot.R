library(survival)
library(cmprsk)

set.seed(42)
n <- 500

# Same simulation as before
treatment <- rbinom(n, 1, 0.5)
age <- rnorm(n, mean = 65, sd = 10)

lambda1 <- 0.010 * exp(0.9 * treatment + 0.015 * (age - 65))
T1 <- rexp(n, rate = lambda1)

lambda2 <- 0.012 * exp(-0.8 * treatment + 0.010 * (age - 65))
T2 <- rexp(n, rate = lambda2)

time <- pmin(T1, T2)
cause <- ifelse(T1 < T2, 1, 2)

tau <- quantile(time, 0.75)
event <- ifelse(time <= tau, cause, 0)
time <- pmin(time, tau)

data <- data.frame(time = time, event = event, treatment = treatment, age = age)

# Estimate cumulative incidence curves for the whole sample, stratified by treatment
cif <- cuminc(data$time, data$event, data$treatment, cencode = 0)

# Create plot
png("competing_risks_comparison.png", width = 1000, height = 400)
par(mfrow = c(1, 2), mar = c(4.5, 4.5, 3, 1))

# Plot 1: Cumulative incidence of cause 1
plot(cif, main = "Cause-Specific Cumulative Incidence Curves",
     lwd = 2, ylim = c(0, 0.55), xlab = "Time", ylab = "Cumulative Incidence")
legend("topleft",
       c("Cause 1, Control", "Cause 1, Treatment",
         "Cause 2, Control", "Cause 2, Treatment"),
       col = c(1, 2, 1, 2), lwd = 2, lty = c(1, 1, 2, 2))

# Plot 2: Focus on cause 1 only by treatment group
plot.new()
plot.window(xlim = c(0, max(data$time)), ylim = c(0, 0.55))
lines(cif$"1 0"$time, cif$"1 0"$est, type = "s", lwd = 2.5, col = "blue", lty = 1)
lines(cif$"1 1"$time, cif$"1 1"$est, type = "s", lwd = 2.5, col = "red", lty = 1)
axis(1); axis(2)
box()
title(main = "Cumulative Incidence of Cause 1",
      xlab = "Time", ylab = "Cumulative Incidence")
legend("topleft",
       c("Control (treatment=0)", "Treatment (treatment=1)"),
       col = c("blue", "red"), lwd = 2.5)

dev.off()

cat("Plot saved to competing_risks_comparison.png\n\n")
cat("KEY OBSERVATION:\n")
cat("The left panel shows both causes: treatment increases cause 1 incidence\n")
cat("but decreases cause 2 (competing) incidence.\n")
cat("The right panel isolates cause 1: the gap shows the cumulative incidence\n")
cat("difference between treatment and control.\n")
