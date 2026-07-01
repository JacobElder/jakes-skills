# rsa_template.R — Congruence Response Surface Analysis with the `RSA` package
#
# The RSA package (Schoenbrodt; v0.10.x, lavaan backend) is the REFERENCE
# implementation. Prefer it over hand-rolled polynomial regression in R: it
# fits the whole nested model family, computes a1..a5 + principal-axis
# parameters with bootstrapped CIs, and plots publication-quality surfaces.
#
# install.packages("RSA")

library(RSA)

# ---------------------------------------------------------------------------
# 0. DATA + PRECONDITIONS
# ---------------------------------------------------------------------------
# df must contain the two predictors (same metric!) and the outcome.
# df <- read.csv("data.csv")
#
# Commensurability: X and Y MUST be on the same scale (ideally the same
# instrument). If they are not, congruence is undefined — stop here.
#
# Centering: center BOTH predictors on ONE common value (the scale midpoint).
# Do NOT center each on its own mean — that destroys commensurability and shifts
# the line of congruence off X = Y. The RSA package will warn if it detects an
# unusual centering; pass `center = "none"` and pre-center yourself for full
# control, or use the built-in centering after confirming the scale midpoint.
MID <- 4                     # e.g. midpoint of a 1..7 scale; set to YOUR scale
df$X <- df$predX - MID
df$Y <- df$predY - MID

# ---------------------------------------------------------------------------
# 1. FIT THE FULL MODEL FAMILY
# ---------------------------------------------------------------------------
# RSA() fits the full second-order polynomial AND a family of constrained
# models (squared difference, shifted/rotated SQD, rising ridge, etc.) so you
# can compare hypothesized patterns rather than eyeballing coefficients.
r <- RSA(Z ~ X * Y, data = df,
         models = c("full", "SQD", "SSQD", "SRSQD", "RR"),
         center = "none")    # we already centered on the common midpoint

# ---------------------------------------------------------------------------
# 2. THE BLOCK TEST (GATE) — is a surface justified at all?
# ---------------------------------------------------------------------------
# Look at whether the full (curved) model beats the purely linear model. If the
# three higher-order terms do not jointly add fit, DO NOT interpret a1..a5 —
# report a linear model instead.
compare(r)                   # model comparison table (AIC/BIC/CFI, LR tests)
# getPar(r, "R2")            # R^2 of the full model

# ---------------------------------------------------------------------------
# 3. SURFACE PARAMETERS WITH BOOTSTRAP CIs
# ---------------------------------------------------------------------------
# a1..a5 and p10/p11 are nonlinear functions of the b's; use bootstrapped CIs.
r_boot <- RSA(Z ~ X * Y, data = df, models = "full",
              center = "none", se = "boot")   # bootstrapped SE/CI
getPar(r_boot, "coef")       # a1..a5, p10, p11 with CIs

# ---------------------------------------------------------------------------
# 4. CONGRUENCE CHECKLIST  (Humberg, Nestler & Back, 2019)
# ---------------------------------------------------------------------------
# A BROAD congruence effect requires ALL FOUR conditions simultaneously
# (no single parameter is sufficient):
#   C1  a4  < 0           inverted-U ridge over the line of incongruence
#   C2  a3  = 0           symmetric (the inverted-U peaks at the congruent point)
#   C3  p10 = 0           first principal axis not shifted off the LOC
#   C4  p11 = 1           first principal axis not rotated away from the LOC
# A STRICT congruence effect additionally requires:
#   C5  a1  = 0  and  C6  a2 = 0     (flat ridge along the LOC — level-independent)
#
# Read these off the getPar() CI table: "significant" = CI excludes the
# reference value (0 for a's and p10; 1 for p11).

# ---------------------------------------------------------------------------
# 5. PLOT
# ---------------------------------------------------------------------------
plot(r, model = "full",
     xlab = "X (centered)", ylab = "Y (centered)", zlab = "Outcome",
     legend = TRUE, project = c("LOC", "LOIC", "PA1"))   # show LOC, LOIC, ridge
# plot(r, type = "interactive")   # rgl interactive (needs rgl)
# plot(r, type = "contour")       # contour view

# ---------------------------------------------------------------------------
# 6. COMPETING-MODEL INFERENCE (recommended over piecemeal coefficient tests)
# ---------------------------------------------------------------------------
# Rather than testing a1..a5 one at a time, compare your hypothesized
# constrained model (e.g. "SQD" = pure congruence) against the full model and
# against rivals, using AIC/BIC weights. A pre-registered SQD that is not beaten
# by the full model is strong evidence for congruence.
aictab <- compare(r)
print(aictab)
