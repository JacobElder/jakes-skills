library(lme4)
library(lmerTest)
library(tidyverse)
library(ggplot2)

# Load data
df <- read.csv("sample_esm_nonergodic.csv")
df$person <- factor(df$person)

# ============================================================================
# STEP 1: Unconditional model — what is the ICC for mood?
# ============================================================================

m_null <- lmer(mood ~ 1 + (1 | person), data = df, REML = TRUE)
summary(m_null)

# Extract variance components
vc <- VarCorr(m_null)
sigma_sq_person <- as.numeric(vc$person)  # between-person variance
sigma_sq_residual <- attr(vc, "sc")^2     # within-person variance

icc <- sigma_sq_person / (sigma_sq_person + sigma_sq_residual)

cat("\n=== VARIANCE COMPONENTS (Null Model) ===\n")
cat("Between-person variance (tau_0^2):", round(sigma_sq_person, 3), "\n")
cat("Within-person variance (sigma^2):", round(sigma_sq_residual, 3), "\n")
cat("ICC(1) for mood:", round(icc, 3), "\n")
cat("Interpretation: ", round(icc*100, 1), "% of mood variance is between people.\n\n")

# ============================================================================
# STEP 2: Pooled model — assume all people have the same activity-mood slope
# ============================================================================

m_pooled <- lmer(mood ~ activity + (1 | person), data = df, REML = TRUE)
summary(m_pooled)

# ============================================================================
# STEP 3: Random slopes model — allow each person to have their own slope
# ============================================================================

m_random_slopes <- lmer(mood ~ activity + (1 + activity | person),
                        data = df, REML = TRUE)
summary(m_random_slopes)

# ============================================================================
# STEP 4: Compare pooled vs. random-slopes via Likelihood Ratio Test
# ============================================================================

# Refit with ML for LRT
m_pooled_ml <- lmer(mood ~ activity + (1 | person), data = df, REML = FALSE)
m_random_slopes_ml <- lmer(mood ~ activity + (1 + activity | person),
                           data = df, REML = FALSE)

lrt_result <- anova(m_pooled_ml, m_random_slopes_ml)
print(lrt_result)

cat("\n=== LIKELIHOOD RATIO TEST: Does random slope for activity help? ===\n")
cat("Chi-square statistic:", round(lrt_result$Chisq[2], 2), "\n")
cat("DF:", lrt_result$Df[2], "\n")
cat("P-value:", round(lrt_result$`Pr(>Chisq)`[2], 4), "\n")

if (lrt_result$`Pr(>Chisq)`[2] < 0.05) {
  cat("*** CONCLUSION: Random slopes SIGNIFICANTLY improve fit (p < 0.05) ***\n")
  cat("*** The activity-mood relationship VARIES substantially across people ***\n")
} else {
  cat("*** CONCLUSION: Random slopes do NOT significantly improve fit (p >= 0.05) ***\n")
  cat("*** The pooled model is appropriate; people don't differ much in slope ***\n")
}

# ============================================================================
# STEP 5: Extract and visualize the random slopes
# ============================================================================

# Get random effects from the random-slopes model
ranef_slopes <- ranef(m_random_slopes)$person
ranef_slopes$person_id <- rownames(ranef_slopes)

# Fixed effect slope
fixed_slope <- fixef(m_random_slopes)["activity"]

# Add individual slopes
ranef_slopes$individual_slope <- fixed_slope + ranef_slopes$activity

cat("\n=== VARIATION IN INDIVIDUAL SLOPES ===\n")
cat("Fixed (pooled) slope:", round(fixed_slope, 4), "\n")
cat("SD of random slopes:", round(sqrt(as.numeric(VarCorr(m_random_slopes)$person["activity", "activity"])), 4), "\n")
cat("Range of individual slopes:\n")
print(summary(ranef_slopes$individual_slope))

# ============================================================================
# STEP 6: Visualization — scatterplot with individual regression lines
# ============================================================================

pdf("activity_mood_individual_lines.pdf", width = 14, height = 10)

# Plot 1: All individuals with individual lines
p1 <- ggplot(df, aes(x = activity, y = mood, color = person)) +
  geom_point(alpha = 0.3, size = 1.5) +
  facet_wrap(~person, ncol = 7) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 1) +
  theme_minimal() +
  theme(legend.position = "none",
        strip.text = element_text(size = 8)) +
  labs(title = "Individual Activity-Mood Relationships (35 people, 55 days each)",
       x = "Activity", y = "Mood") +
  scale_color_viridis_d()

print(p1)

# Plot 2: Distribution of individual slopes
p2 <- ggplot(ranef_slopes, aes(x = individual_slope)) +
  geom_histogram(binwidth = 0.02, fill = "steelblue", alpha = 0.7, color = "black") +
  geom_vline(xintercept = fixed_slope, color = "red", linetype = "dashed", linewidth = 1.5,
             label = "Pooled slope") +
  theme_minimal() +
  labs(title = "Distribution of Individual Slopes (Activity → Mood)",
       x = "Individual Slope", y = "Number of People",
       subtitle = paste("Red dashed line = pooled slope (", round(fixed_slope, 4), ")", sep = "")) +
  annotate("text", x = Inf, y = Inf,
           label = paste("SD of slopes =", round(sqrt(as.numeric(VarCorr(m_random_slopes)$person["activity", "activity"])), 4)),
           hjust = 1.1, vjust = 1.5, size = 4, color = "darkred")

print(p2)

# Plot 3: Scatterplot with pooled line + individual lines overlay
p3 <- ggplot(df, aes(x = activity, y = mood)) +
  geom_point(alpha = 0.2, color = "gray50") +
  # Add individual lines (light)
  geom_abline(data = ranef_slopes,
              aes(slope = individual_slope,
                  intercept = `(Intercept)` + fixed_slope * mean(df$activity, na.rm=TRUE) - ranef_slopes$individual_slope * mean(df$activity, na.rm=TRUE)),
              alpha = 0.15, color = "steelblue", linewidth = 0.5) +
  # Add pooled line (bold red)
  geom_smooth(method = "lm", se = TRUE, color = "red", fill = "red", alpha = 0.2, linewidth = 2) +
  theme_minimal() +
  labs(title = "Pooled Model (Red) vs. Individual Lines (Light Blue)",
       x = "Activity", y = "Mood",
       subtitle = "Each light line = one person's fitted relationship") +
  coord_cartesian(xlim = c(0, 11))

print(p3)

dev.off()

cat("\nPlot saved as: activity_mood_individual_lines.pdf\n")

# ============================================================================
# STEP 7: Quantify effect size of heterogeneity
# ============================================================================

# How much does the SD of slopes represent relative to the fixed slope?
slope_sd <- sqrt(as.numeric(VarCorr(m_random_slopes)$person["activity", "activity"]))
slope_cv <- slope_sd / abs(fixed_slope)  # Coefficient of variation

cat("\n=== EFFECT SIZE OF SLOPE HETEROGENEITY ===\n")
cat("Pooled slope (estimate):", round(fixed_slope, 4), "\n")
cat("SD of individual slopes:", round(slope_sd, 4), "\n")
cat("Coefficient of variation (SD/|slope|):", round(slope_cv, 3), "\n")
cat("95% range of slopes (±1.96*SD):",
    round(fixed_slope - 1.96*slope_sd, 4), "to", round(fixed_slope + 1.96*slope_sd, 4), "\n")

# What % of people have slopes substantially different from the pooled estimate?
ranef_slopes$slope_ci_lower <- fixed_slope - 1.96 * slope_sd
ranef_slopes$slope_ci_upper <- fixed_slope + 1.96 * slope_sd
ranef_slopes$outside_ci <- (ranef_slopes$individual_slope < ranef_slopes$slope_ci_lower |
                            ranef_slopes$individual_slope > ranef_slopes$slope_ci_upper)

pct_outside <- mean(ranef_slopes$outside_ci) * 100
cat("\n% of people with slopes outside 95% interval around pooled slope:",
    round(pct_outside, 1), "%\n")

# ============================================================================
# STEP 8: Final recommendation for reviewer
# ============================================================================

sep_line <- paste(rep("=", 70), collapse = "")
cat("\n", sep_line, "\n")
cat("EVIDENCE SUMMARY FOR REVIEWER\n")
cat(sep_line, "\n\n")

cat("Question: Is a single pooled model defensible?\n\n")

if (lrt_result$`Pr(>Chisq)`[2] < 0.05) {
  cat("ANSWER: NO — this data shows SIGNIFICANT HETEROGENEITY.\n\n")
  cat("Evidence:\n")
  cat("1. LRT: χ²(2) =", round(lrt_result$Chisq[2], 2),
      ", p =", round(lrt_result$`Pr(>Chisq)`[2], 4),
      " (random slopes significantly improve fit)\n")
  cat("2. Slope variation: SD of slopes = ", round(slope_sd, 4),
      " (pooled slope = ", round(fixed_slope, 4), ")\n")
  cat("3. Heterogeneity: ", round(pct_outside, 1), "% of people have slopes outside ±1.96*SD\n")
  cat("4. Visual inspection: See faceted plot — relationships clearly differ across individuals\n\n")
  cat("RECOMMENDATION: Fit person-specific or mixed-effects models with random slopes.\n")
  cat("A pooled OLS model would be inappropriate and would mask individual differences.\n")
} else {
  cat("ANSWER: YES — this data shows HOMOGENEOUS slopes.\n\n")
  cat("Evidence:\n")
  cat("1. LRT: χ²(2) =", round(lrt_result$Chisq[2], 2),
      ", p =", round(lrt_result$`Pr(>Chisq)`[2], 4),
      " (random slopes do NOT significantly improve fit)\n")
  cat("2. Slope variation: SD of slopes = ", round(slope_sd, 4),
      " (negligible relative to pooled slope = ", round(fixed_slope, 4), ")\n")
  cat("3. Only ", round(pct_outside, 1), "% of people differ substantially from the pooled slope.\n\n")
  cat("RECOMMENDATION: A pooled model (with random intercepts only) is appropriate.\n")
  cat("The homogeneity in slopes means person-specific models add no value.\n")
}

cat("\n", sep_line, "\n")
