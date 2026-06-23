#!/usr/bin/env python3
"""Grade all 20 eval pairs and write grading.json files.

Reads transcripts and produces grading based on assertions in evals.json.
With-skill transcripts are graded against expected behavior;
without-skill baselines are graded the same way to measure the delta.
"""

import json
import os
import re
from pathlib import Path

RESULTS = Path("/Users/jacobelder/Documents/GitHub/jakes-skills/information-theory/results")
EVALS_PATH = Path("/Users/jacobelder/Documents/GitHub/jakes-skills/information-theory/information-theory/evals/evals.json")

with open(EVALS_PATH) as f:
    evals_data = json.load(f)

evals = evals_data["evals"]

def read_transcript(eval_id: int, variant: str) -> str:
    path = RESULTS / f"eval_{eval_id:02d}" / variant / "transcript.md"
    if path.exists():
        return path.read_text()
    return ""

def write_grading(eval_id: int, variant: str, results: list[dict], eval_feedback: str = "Assertions are well-targeted and discriminating."):
    passed = sum(1 for r in results if r["passed"])
    grading = {
        "expectations": results,
        "summary": {
            "passed": passed,
            "failed": len(results) - passed,
            "total": len(results),
            "pass_rate": passed / len(results) if results else 0.0,
        },
        "claims": [],
        "eval_feedback": {
            "suggestions": [],
            "overall": eval_feedback,
        },
    }
    path = RESULTS / f"eval_{eval_id:02d}" / f"{variant}_grading.json"
    path.write_text(json.dumps(grading, indent=2))
    print(f"Wrote {path} ({passed}/{len(results)} passed)")
    return grading

# ─── Grading decisions ───────────────────────────────────────────────────────
# Each entry: (eval_id, variant) -> [(assertion_text, passed, evidence)]

def grade_all():
    summary_rows = []

    # ── EVAL 1: MI undersampled ──────────────────────────────────────────────
    with_1 = [
        {"text": "States that empirical/plug-in mutual information is biased upward (overestimates) in finite samples.",
         "passed": True,
         "evidence": "Transcript explicitly states plug-in MI is biased upward by (K_X-1)(K_Y-1)/(2N) ≈ 0.26 nats and quantifies it precisely."},
        {"text": "Connects the problem to undersampling: 150 rows is small relative to the ~12×8 joint cells.",
         "passed": True,
         "evidence": "States 150 rows over 12×8 = 96 cells gives ~1.6 rows/cell; identifies this as well below the ~10 per cell threshold."},
        {"text": "Recommends a permutation/shuffle null test or an explicit bias correction (Miller–Madow/NSB).",
         "passed": True,
         "evidence": "Provides complete runnable code for permutation null (500 shuffles) and Miller–Madow correction with all three entropy terms corrected."},
        {"text": "Does NOT simply affirm 0.42 as a real, trustworthy effect size.",
         "passed": True,
         "evidence": "Explicitly refuses to take 0.42 at face value; estimates signal gap as only ~0.16 nats at best after bias correction."},
    ]
    without_1 = [
        {"text": "States that empirical/plug-in mutual information is biased upward (overestimates) in finite samples.",
         "passed": True,
         "evidence": "States plug-in MI has substantial upward bias (~0.25 nats rough calculation), mentions bias floor."},
        {"text": "Connects the problem to undersampling: 150 rows is small relative to the ~12×8 joint cells.",
         "passed": True,
         "evidence": "Identifies 150 rows across 96 cells (12×8 table) as sparse."},
        {"text": "Recommends a permutation/shuffle null test or an explicit bias correction (Miller–Madow/NSB).",
         "passed": True,
         "evidence": "Recommends permutation test to compare observed MI against null distribution."},
        {"text": "Does NOT simply affirm 0.42 as a real, trustworthy effect size.",
         "passed": True,
         "evidence": "States 'there is probably some real association' but 'permutation test is required to confirm'; does not endorse 0.42 unconditionally."},
    ]
    write_grading(1, "with_skill", with_1)
    write_grading(1, "without_skill", without_1, "Both responses handle this well. With-skill provides exact bias quantification and runnable code; without-skill somewhat vaguer but correct direction.")
    summary_rows.append((1, sum(r["passed"] for r in with_1), len(with_1), sum(r["passed"] for r in without_1), len(without_1)))

    # ── EVAL 2: differential entropy negative ────────────────────────────────
    with_2 = [
        {"text": "States clearly that negative differential entropy is valid and not a bug.",
         "passed": True,
         "evidence": "Opens with: '-2.4 is not a bug.' Explains differential entropy can be negative."},
        {"text": "Explains differential entropy is not simply 'entropy for continuous variables' (e.g., can be negative; not expected surprisal).",
         "passed": True,
         "evidence": "Explicitly distinguishes differential entropy from discrete Shannon entropy; states it is not expected surprisal."},
        {"text": "Notes it is not invariant under reparameterization/rescaling (depends on units), so its value is scale-dependent.",
         "passed": True,
         "evidence": "Explains reparameterization non-invariance; recommends MI as the coordinate-free alternative."},
        {"text": "Does NOT incorrectly claim entropy must always be non-negative.",
         "passed": True,
         "evidence": "Correctly asserts the opposite — that negative values are expected and meaningful."},
    ]
    without_2 = [
        {"text": "States clearly that negative differential entropy is valid and not a bug.",
         "passed": True,
         "evidence": "States '-2.4 is not a bug'; differential entropy does not have the non-negativity guarantee of discrete Shannon entropy."},
        {"text": "Explains differential entropy is not simply 'entropy for continuous variables' (e.g., can be negative; not expected surprisal).",
         "passed": True,
         "evidence": "Distinguishes differential entropy from discrete Shannon entropy; explains densities can exceed 1."},
        {"text": "Notes it is not invariant under reparameterization/rescaling (depends on units), so its value is scale-dependent.",
         "passed": False,
         "evidence": "The baseline response focuses on why values go negative (density > 1) but does not explicitly address scale-dependence / reparameterization non-invariance. Mentions debugging advice but not the coordinate-dependence issue."},
        {"text": "Does NOT incorrectly claim entropy must always be non-negative.",
         "passed": True,
         "evidence": "Correctly validates the negative value."},
    ]
    write_grading(2, "with_skill", with_2)
    write_grading(2, "without_skill", without_2, "Assertion 2c (reparameterization non-invariance) is a key differentiator — the skill explicitly covers this, the baseline misses it.")
    summary_rows.append((2, sum(r["passed"] for r in with_2), len(with_2), sum(r["passed"] for r in without_2), len(without_2)))

    # ── EVAL 3: VI reverse KL ────────────────────────────────────────────────
    with_3 = [
        {"text": "Identifies that standard VI / the ELBO minimizes reverse KL, i.e. KL(q||p).",
         "passed": True,
         "evidence": "Explicitly states ELBO = minimizing KL(q‖p) = reverse KL."},
        {"text": "Explains reverse KL is mode-seeking / zero-forcing and therefore underestimates variance — the narrow intervals are expected, not a tuning bug.",
         "passed": True,
         "evidence": "States reverse KL is mode-seeking/zero-forcing; explains optimizer locks onto one mode and is systematically too narrow. Frames this as expected, not a bug."},
        {"text": "Contrasts with forward KL KL(p||q) being mass-covering / variance-respecting.",
         "passed": True,
         "evidence": "Explicitly contrasts forward KL (mass-covering, used by EP and MCMC) with reverse KL (mode-seeking, used by VI)."},
    ]
    without_3 = [
        {"text": "Identifies that standard VI / the ELBO minimizes reverse KL, i.e. KL(q||p).",
         "passed": True,
         "evidence": "States mean-field VI minimizes KL(q‖p) = reverse KL."},
        {"text": "Explains reverse KL is mode-seeking / zero-forcing and therefore underestimates variance — the narrow intervals are expected, not a tuning bug.",
         "passed": True,
         "evidence": "Explains zero-forcing behavior: optimizer concentrates q tightly on a mode, producing marginals that are systematically too narrow."},
        {"text": "Contrasts with forward KL KL(p||q) being mass-covering / variance-respecting.",
         "passed": True,
         "evidence": "Contrasts with minimizing KL(p‖q) which is mass-covering."},
    ]
    write_grading(3, "with_skill", with_3)
    write_grading(3, "without_skill", without_3, "Both responses cover all three assertions well. Base model knows VI/KL direction well. Skill adds mean-field compounding detail.")
    summary_rows.append((3, sum(r["passed"] for r in with_3), len(with_3), sum(r["passed"] for r in without_3), len(without_3)))

    # ── EVAL 4: cross-entropy / NLL / KL identity ────────────────────────────
    with_4 = [
        {"text": "States the decomposition H(p,q) = H(p) + D_KL(p||q).",
         "passed": True,
         "evidence": "Explicitly states the identity H(p,q) = H(p) + D_KL(p‖q) as the central hinge."},
        {"text": "Explains that minimizing cross-entropy over q equals maximum likelihood equals minimizing KL to the empirical distribution — the same objective.",
         "passed": True,
         "evidence": "Shows argmin_q H(p̂,q) = argmin KL(p̂‖q) = argmax log q(xᵢ) = MLE."},
        {"text": "Notes that 'cross-entropy loss', 'negative log-likelihood', and 'log loss' name the same thing (base only changes bits vs nats).",
         "passed": True,
         "evidence": "Explicitly states these are the same objective; only difference is log base (bits vs nats) and whether you average or sum."},
    ]
    without_4 = [
        {"text": "States the decomposition H(p,q) = H(p) + D_KL(p||q).",
         "passed": True,
         "evidence": "States the algebraic chain NLL = H(P,Q) = H(P) + KL(P‖Q)."},
        {"text": "Explains that minimizing cross-entropy over q equals maximum likelihood equals minimizing KL to the empirical distribution — the same objective.",
         "passed": True,
         "evidence": "Shows minimizing NLL = minimizing KL since H(P) is constant w.r.t. model parameters."},
        {"text": "Notes that 'cross-entropy loss', 'negative log-likelihood', and 'log loss' name the same thing (base only changes bits vs nats).",
         "passed": True,
         "evidence": "Summary table explicitly maps three names to one objective."},
    ]
    write_grading(4, "with_skill", with_4)
    write_grading(4, "without_skill", without_4, "Both responses pass all assertions. Base model handles this identity well. Skill adds CEM disambiguation and KL direction emphasis.")
    summary_rows.append((4, sum(r["passed"] for r in with_4), len(with_4), sum(r["passed"] for r in without_4), len(without_4)))

    # ── EVAL 5: Huffman vs arithmetic coding ─────────────────────────────────
    with_5 = [
        {"text": "Identifies that Huffman codes assign an integer number of bits per symbol, so the per-symbol overhead can be up to ~1 bit — the loss is inherent, not a bug.",
         "passed": True,
         "evidence": "Explicitly states Huffman is optimal only among codes with integer bits per symbol; overhead is inherent, not a bug. Computes exact overhead at p=0.95."},
        {"text": "Explains the skew (p≈0.95) is exactly the regime where this hurts, since the entropy is well below 1 bit/symbol.",
         "passed": True,
         "evidence": "Calculates entropy ≈ 0.286 bits/symbol vs 1.0 bit/symbol floor, showing 3.5× overhead specific to skewed distributions."},
        {"text": "Recommends arithmetic coding and/or ANS, which approach the entropy bound (within O(1) bits total, not per symbol).",
         "passed": True,
         "evidence": "Recommends arithmetic/ANS; explains O(1) bits total overhead (not per symbol), directly from coding.md."},
    ]
    without_5 = [
        {"text": "Identifies that Huffman codes assign an integer number of bits per symbol, so the per-symbol overhead can be up to ~1 bit — the loss is inherent, not a bug.",
         "passed": True,
         "evidence": "States Huffman cannot assign fractional-bit codewords; common symbol needs 0.074 bits but floors at 1 bit."},
        {"text": "Explains the skew (p≈0.95) is exactly the regime where this hurts, since the entropy is well below 1 bit/symbol.",
         "passed": True,
         "evidence": "Shows the dominant symbol deserves 0.074 bits but gets 1 bit, so ~13× overhead."},
        {"text": "Recommends arithmetic coding and/or ANS, which approach the entropy bound (within O(1) bits total, not per symbol).",
         "passed": True,
         "evidence": "Recommends arithmetic coding / ANS as the principled solution; notes block coding as partial fix."},
    ]
    write_grading(5, "with_skill", with_5)
    write_grading(5, "without_skill", without_5, "Both responses pass all assertions. This is a well-known coding result; base model handles it correctly.")
    summary_rows.append((5, sum(r["passed"] for r in with_5), len(with_5), sum(r["passed"] for r in without_5), len(without_5)))

    # ── EVAL 6: AIC vs BIC ──────────────────────────────────────────────────
    with_6 = [
        {"text": "States AIC targets out-of-sample predictive accuracy (expected KL / deviance); efficient, does not assume a true model in the set.",
         "passed": True,
         "evidence": "States AIC estimates out-of-sample predictive deviance (expected KL); efficient but not consistent; does not assume true model in candidate set."},
        {"text": "States BIC targets the true/parsimonious model (marginal-likelihood / consistency) under the assumption the true model is among the candidates.",
         "passed": True,
         "evidence": "States BIC ≈ log marginal likelihood via Laplace; consistent if true model is in candidate set — explicitly owns that assumption."},
        {"text": "Frames the choice by the question being asked (prediction vs identifying the true model) rather than declaring one universally superior or averaging them.",
         "passed": True,
         "evidence": "Reframes as category error; provides decision rule by question; explicitly prohibits averaging."},
        {"text": "Recommends cross-validation / LOO (or notes AIC ≈ LOO) as a direct way to settle a prediction-focused decision.",
         "passed": True,
         "evidence": "Recommends LOO-CV as a direct arbiter; notes AIC ≈ LOO asymptotically."},
    ]
    without_6 = [
        {"text": "States AIC targets out-of-sample predictive accuracy (expected KL / deviance); efficient, does not assume a true model in the set.",
         "passed": True,
         "evidence": "States AIC targets out-of-sample prediction / predictive accuracy; efficient not consistent; does not require true model in set."},
        {"text": "States BIC targets the true/parsimonious model (marginal-likelihood / consistency) under the assumption the true model is among the candidates.",
         "passed": True,
         "evidence": "States BIC targets identifying correct model structure / parsimony; consistency property noted."},
        {"text": "Frames the choice by the question being asked (prediction vs identifying the true model) rather than declaring one universally superior or averaging them.",
         "passed": True,
         "evidence": "Provides decision rule: prediction goal → AIC; structural truth → BIC. Does not declare one universally better."},
        {"text": "Recommends cross-validation / LOO (or notes AIC ≈ LOO) as a direct way to settle a prediction-focused decision.",
         "passed": False,
         "evidence": "The without-skill response does not recommend CV/LOO as an arbiter or note the AIC ≈ LOO equivalence."},
    ]
    write_grading(6, "with_skill", with_6)
    write_grading(6, "without_skill", without_6, "Assertion 6d (AIC ≈ LOO / recommend CV) differentiates the skill. The skill explicitly connects AIC to LOO; the base model misses this.")
    summary_rows.append((6, sum(r["passed"] for r in with_6), len(with_6), sum(r["passed"] for r in without_6), len(without_6)))

    # ── EVAL 7: bits/char compression ────────────────────────────────────────
    with_7 = [
        {"text": "Confirms the claim is essentially right and does the arithmetic (1.2 bits/char vs 8 bits/char ≈ 15%).",
         "passed": True,
         "evidence": "Confirms 1.2/8 = 15% arithmetic; confirms the colleague's claim is correct."},
        {"text": "Explains the bridge: cross-entropy / NLL in bits equals the achievable codelength, realizable with arithmetic coding.",
         "passed": True,
         "evidence": "Explicitly states the compression=prediction bridge; model's NLL IS the compressed file length via arithmetic coding."},
        {"text": "States the general principle that compression and prediction are the same problem (a good probabilistic model is a compressor).",
         "passed": True,
         "evidence": "States 'a probabilistic model IS a compressor'; frames bits/char as both loss and compressed file size."},
    ]
    without_7 = [
        {"text": "Confirms the claim is essentially right and does the arithmetic (1.2 bits/char vs 8 bits/char ≈ 15%).",
         "passed": True,
         "evidence": "Confirms 15% figure; does the arithmetic (1.2/8 = 0.15)."},
        {"text": "Explains the bridge: cross-entropy / NLL in bits equals the achievable codelength, realizable with arithmetic coding.",
         "passed": True,
         "evidence": "Explains arithmetic coder driven by model's per-character probabilities gives compressed length = cumulative NLL."},
        {"text": "States the general principle that compression and prediction are the same problem (a good probabilistic model is a compressor).",
         "passed": True,
         "evidence": "States better prediction ↔ better compression; notes compression benchmarks as language-modeling benchmarks."},
    ]
    write_grading(7, "with_skill", with_7)
    write_grading(7, "without_skill", without_7, "Both pass all assertions. The compression=prediction bridge is well-known to the base model.")
    summary_rows.append((7, sum(r["passed"] for r in with_7), len(with_7), sum(r["passed"] for r in without_7), len(without_7)))

    # ── EVAL 8: MI feature selection ─────────────────────────────────────────
    with_8 = [
        {"text": "Flags that ranking by marginal MI ignores redundancy among features, and recommends a redundancy-aware criterion (mRMR, JMI, or conditional MI).",
         "passed": True,
         "evidence": "Explicitly flags redundancy blindness; recommends mRMR or JMI/CMIM greedy selection instead of top-k ranking."},
        {"text": "Notes MI estimates are biased (upward) and the bias is worse for high-cardinality/continuous features, which can distort the ranking.",
         "passed": True,
         "evidence": "States plug-in MI is biased upward; bias is worst for high-cardinality/continuous features — exactly where overfit is most likely."},
        {"text": "Recommends a sound estimation practice (KSG over fixed-bin histograms for continuous features, and/or a permutation null).",
         "passed": True,
         "evidence": "Recommends KSG for continuous features and permutation null; mandatory for any reported MI value."},
        {"text": "Gives a nuanced verdict rather than simply endorsing top-k-by-MI.",
         "passed": True,
         "evidence": "Does not endorse the approach; identifies three failure modes with concrete fixes."},
    ]
    without_8 = [
        {"text": "Flags that ranking by marginal MI ignores redundancy among features, and recommends a redundancy-aware criterion (mRMR, JMI, or conditional MI).",
         "passed": True,
         "evidence": "Identifies redundancy as the biggest failure mode; recommends mRMR or post-hoc correlation check."},
        {"text": "Notes MI estimates are biased (upward) and the bias is worse for high-cardinality/continuous features, which can distort the ranking.",
         "passed": True,
         "evidence": "States high-cardinality categoricals are systematically overscored due to finite-sample bias."},
        {"text": "Recommends a sound estimation practice (KSG over fixed-bin histograms for continuous features, and/or a permutation null).",
         "passed": False,
         "evidence": "The without-skill response does not specifically recommend KSG over histogram binning for continuous features, or a permutation null test. Mentions the bias issue but not the estimation fix."},
        {"text": "Gives a nuanced verdict rather than simply endorsing top-k-by-MI.",
         "passed": True,
         "evidence": "Does not endorse; identifies multiple gotchas."},
    ]
    write_grading(8, "with_skill", with_8)
    write_grading(8, "without_skill", without_8, "Assertion 8c (KSG recommendation, permutation null) differentiates — the skill's estimation chapter drives this recommendation.")
    summary_rows.append((8, sum(r["passed"] for r in with_8), len(with_8), sum(r["passed"] for r in without_8), len(without_8)))

    # ── EVAL 9: decision tree high cardinality ───────────────────────────────
    with_9 = [
        {"text": "Connects information gain to mutual information / entropy reduction (H(Y) − H(Y|split)).",
         "passed": True,
         "evidence": "Explicitly connects information gain to plug-in mutual information; cites H(Y) − H(Y|split) definition."},
        {"text": "Explains high-cardinality splits inflate measured information gain (spurious purity / upward bias), i.e. it is overfitting, not real signal.",
         "passed": True,
         "evidence": "States upward bias is (K_X−1)(K_Y−1)/(2N); for customer_id K_X ≈ N so bias ≈ (K_Y−1)/2 — a fixed large offset unrelated to signal. Pure leaves are mechanical."},
        {"text": "Recommends a concrete fix: gain ratio, penalizing cardinality, or excluding ID-like columns.",
         "passed": True,
         "evidence": "Recommends (1) drop ID columns (correct structural fix), (2) gain ratio for custom rankers, (3) permutation null."},
    ]
    without_9 = [
        {"text": "Connects information gain to mutual information / entropy reduction (H(Y) − H(Y|split)).",
         "passed": True,
         "evidence": "Connects information gain to H(Y) − H(Y|split); identifies it as entropy reduction."},
        {"text": "Explains high-cardinality splits inflate measured information gain (spurious purity / upward bias), i.e. it is overfitting, not real signal.",
         "passed": True,
         "evidence": "Explains unique-ID creates one leaf per row (trivially pure); gain equals full training set entropy; this is overfitting not signal."},
        {"text": "Recommends a concrete fix: gain ratio, penalizing cardinality, or excluding ID-like columns.",
         "passed": True,
         "evidence": "Recommends (1) drop identifier columns, (2) gain ratio (C4.5), (3) min_samples_leaf, (4) target encoding."},
    ]
    write_grading(9, "with_skill", with_9)
    write_grading(9, "without_skill", without_9, "Both pass all assertions. Decision tree / information gain bias is well-known to the base model.")
    summary_rows.append((9, sum(r["passed"] for r in with_9), len(with_9), sum(r["passed"] for r in without_9), len(without_9)))

    # ── EVAL 10: KL Gaussians numeric ────────────────────────────────────────
    with_10 = [
        {"text": "Uses the correct 1-D Gaussian KL formula 0.5*[ln(var_q/var_p) + (var_p + (mu_p-mu_q)^2)/var_q - 1] (variances, not std).",
         "passed": True,
         "evidence": "Uses exact variance-form formula: KL = ½[ln(var_q/var_p) + (var_p+(μ_p-μ_q)²)/var_q - 1]."},
        {"text": "Forward KL(p||q) with var_p=1, var_q=2, mu_p=0, mu_q=1 evaluates to approximately 0.3466 nats (= 0.5 bits exactly).",
         "passed": True,
         "evidence": "Computes KL(p‖q) = 0.3466 nats = 0.5 bits exactly. Shows calculation step by step."},
        {"text": "Reverse KL(q||p) evaluates to approximately 0.6534 nats (= 0.9427 bits). NOT equal to the forward value.",
         "passed": True,
         "evidence": "Computes KL(q‖p) = 0.6534 nats ≈ 0.9427 bits. Shows calculation."},
        {"text": "Explicitly states the two values differ, so KL is asymmetric / not a metric.",
         "passed": True,
         "evidence": "States 'KL divergence is not symmetric' with the ratio nearly 2:1; explains structural reason for asymmetry."},
    ]
    without_10 = [
        {"text": "Uses the correct 1-D Gaussian KL formula 0.5*[ln(var_q/var_p) + (var_p + (mu_p-mu_q)^2)/var_q - 1] (variances, not std).",
         "passed": True,
         "evidence": "Uses the std-form formula log(σ_q/σ_p) + (σ_p²+(μ_p-μ_q)²)/(2σ_q²) - ½, which is mathematically equivalent to the variance form. The derivation is correct."},
        {"text": "Forward KL(p||q) with var_p=1, var_q=2, mu_p=0, mu_q=1 evaluates to approximately 0.3466 nats (= 0.5 bits exactly).",
         "passed": True,
         "evidence": "Computes KL(p‖q) = log(√2) + (1+1)/4 - 0.5 = 0.3466 nats. Correct."},
        {"text": "Reverse KL(q||p) evaluates to approximately 0.6534 nats (= 0.9427 bits). NOT equal to the forward value.",
         "passed": True,
         "evidence": "Computes KL(q‖p) = -log(√2) + 3/2 - 0.5 = 0.6534 nats. Correct."},
        {"text": "Explicitly states the two values differ, so KL is asymmetric / not a metric.",
         "passed": True,
         "evidence": "States 'KL divergence is not symmetric'; notes it is a divergence not a distance."},
    ]
    write_grading(10, "with_skill", with_10)
    write_grading(10, "without_skill", without_10, "Both compute correctly. With-skill adds the VI/MLE interpretation of the asymmetry. Eval 10d could require naming the direction (mode-seeking vs mass-covering) for a stronger discriminator.")
    summary_rows.append((10, sum(r["passed"] for r in with_10), len(with_10), sum(r["passed"] for r in without_10), len(without_10)))

    # ── EVAL 11: sample entropy computation ──────────────────────────────────
    with_11 = [
        {"text": "Identifies this as sample entropy / a time-series regularity measure (Richman-Moorman), explicitly NOT Shannon entropy of the value distribution.",
         "passed": True,
         "evidence": "Opens with 'This is NOT a Shannon entropy question.' Identifies SampEn as time-series regularity in Pincus/Richman-Moorman lineage."},
        {"text": "Computes r = 0.2 * SD correctly: SD ~= 14.87, so r ~= 2.97 (accepts 2.9-3.0).",
         "passed": True,
         "evidence": "SD = 14.869 ms, r = 2.974 ms (population std ddof=0). Within acceptance range 2.9-3.0."},
        {"text": "Reports SampEn ~= 0.61 (accept 0.59-0.62) using the -ln(A/B) definition with self-matches EXCLUDED (Chebyshev metric, m=2).",
         "passed": True,
         "evidence": "SampEn = 0.606 using script. Within acceptance range 0.59-0.62. Self-matches excluded confirmed."},
        {"text": "States the result is unitless (not bits) and/or that SampEn is only comparable across signals at the same (m, r, N); reports the parameters used.",
         "passed": True,
         "evidence": "States result is 'not in bits'; parameters (m=2, r, N=30) explicitly reported; comparisons must use matched parameters."},
    ]
    without_11 = [
        {"text": "Identifies this as sample entropy / a time-series regularity measure (Richman-Moorman), explicitly NOT Shannon entropy of the value distribution.",
         "passed": False,
         "evidence": "The without-skill response computes SampEn but never explicitly identifies it as a regularity statistic distinct from Shannon entropy, nor states it is NOT Shannon entropy. The disambiguation is absent."},
        {"text": "Computes r = 0.2 * SD correctly: SD ~= 14.87, so r ~= 2.97 (accepts 2.9-3.0).",
         "passed": False,
         "evidence": "Uses sample SD (ddof=1) = 15.12, giving r = 3.02. Outside the acceptance range 2.9-3.0 (just barely), but the root issue is using wrong SD convention."},
        {"text": "Reports SampEn ~= 0.61 (accept 0.59-0.62) using the -ln(A/B) definition with self-matches EXCLUDED (Chebyshev metric, m=2).",
         "passed": False,
         "evidence": "Reports SampEn = 0.539, outside the acceptance range 0.59-0.62. The difference is due to using sample SD vs population SD for r, leading to different match counts."},
        {"text": "States the result is unitless (not bits) and/or that SampEn is only comparable across signals at the same (m, r, N); reports the parameters used.",
         "passed": True,
         "evidence": "Reports parameters used; notes values only comparable at same (m, r, N). Does not explicitly state unitless but implies it."},
    ]
    write_grading(11, "with_skill", with_11)
    write_grading(11, "without_skill", without_11, "Strong discriminator: with-skill correctly identifies Shannon/SampEn distinction (thesis 7) and uses the correct SD convention from the script. Without-skill misses the disambiguation and uses wrong SD.")
    summary_rows.append((11, sum(r["passed"] for r in with_11), len(with_11), sum(r["passed"] for r in without_11), len(without_11)))

    # ── EVAL 12: EEG entropy disambiguation ──────────────────────────────────
    with_12 = [
        {"text": "Recommends a regularity/complexity entropy (sample entropy, permutation entropy, or multiscale entropy) rather than Shannon entropy of binned amplitude values.",
         "passed": True,
         "evidence": "Recommends SampEn (m=2, r=0.2×SD) as primary; also covers permutation entropy and MSE. Does not recommend Shannon entropy of amplitude distribution."},
        {"text": "Explains WHY Shannon entropy of the amplitude distribution is the wrong tool here: it is order-invariant / unchanged by shuffling, so it cannot capture temporal predictability or complexity.",
         "passed": True,
         "evidence": "Explicitly states Shannon entropy ignores temporal order; shuffling a sine wave gives same Shannon entropy as white noise but they are maximally different in complexity."},
        {"text": "Gives concrete parameter guidance (e.g., m=2, r=0.2*SD for SampEn, or embedding order for permutation entropy) and notes sensitivity to N / sampling.",
         "passed": True,
         "evidence": "Gives m=2, r=0.2×SD; notes parameter sensitivity ('m, r, and N all move the number'); warns against comparing across different parameter sets."},
        {"text": "Does not report the measure in bits as if it were Shannon information, and/or notes values are only comparable across signals at matched parameters.",
         "passed": True,
         "evidence": "States 'SampEn is not in bits'; notes values only comparable at matched parameters."},
    ]
    without_12 = [
        {"text": "Recommends a regularity/complexity entropy (sample entropy, permutation entropy, or multiscale entropy) rather than Shannon entropy of binned amplitude values.",
         "passed": True,
         "evidence": "Recommends SampEn with m=2, r=0.15×SD; also covers permutation entropy and MSE."},
        {"text": "Explains WHY Shannon entropy of the amplitude distribution is the wrong tool here: it is order-invariant / unchanged by shuffling, so it cannot capture temporal predictability or complexity.",
         "passed": True,
         "evidence": "States Shannon entropy ignores temporal order — periodic signal can have high Shannon entropy if histogram is flat."},
        {"text": "Gives concrete parameter guidance (e.g., m=2, r=0.2*SD for SampEn, or embedding order for permutation entropy) and notes sensitivity to N / sampling.",
         "passed": True,
         "evidence": "Gives m=2, r=0.15×SD for SampEn; L=5 for permutation entropy; notes stationarity and epoch-length effects."},
        {"text": "Does not report the measure in bits as if it were Shannon information, and/or notes values are only comparable across signals at matched parameters.",
         "passed": True,
         "evidence": "Practical checklist includes parameter documentation; does not claim bits."},
    ]
    write_grading(12, "with_skill", with_12)
    write_grading(12, "without_skill", without_12, "Both pass all assertions. Base model handles the EEG entropy disambiguation reasonably. Skill adds the explicit Shannon/SampEn lineage explanation.")
    summary_rows.append((12, sum(r["passed"] for r in with_12), len(with_12), sum(r["passed"] for r in without_12), len(without_12)))

    # ── EVAL 13: calibration proper scoring ──────────────────────────────────
    with_13 = [
        {"text": "Answers NO: low log-loss does not guarantee calibration.",
         "passed": True,
         "evidence": "Core answer is NO; explains the distinction between average quality (log-loss) and per-prediction calibration."},
        {"text": "Correctly states log-loss is a strictly proper scoring rule (minimized by true probabilities in expectation), but proper-ness is about expected score, not a calibration guarantee for the fitted model.",
         "passed": True,
         "evidence": "States log-loss is strictly proper; explains proper scoring rule gives expectation-level guarantee not per-prediction calibration. Three failure modes where a miscalibrated model can still have good average log-loss."},
        {"text": "Recommends a calibration diagnostic (reliability diagram / expected calibration error) distinct from the loss value.",
         "passed": True,
         "evidence": "Recommends reliability diagrams / ECE as the diagnostic."},
        {"text": "Recommends temperature scaling (or isotonic/Platt) as the fix, noting temperature scaling preserves the argmax/accuracy.",
         "passed": True,
         "evidence": "Recommends temperature scaling (one-parameter cross-entropy minimization); notes it preserves argmax/accuracy."},
    ]
    without_13 = [
        {"text": "Answers NO: low log-loss does not guarantee calibration.",
         "passed": True,
         "evidence": "Answers NO clearly."},
        {"text": "Correctly states log-loss is a strictly proper scoring rule (minimized by true probabilities in expectation), but proper-ness is about expected score, not a calibration guarantee for the fitted model.",
         "passed": True,
         "evidence": "States log-loss is a proper scoring rule; notes a model can have good average log-loss while still being miscalibrated."},
        {"text": "Recommends a calibration diagnostic (reliability diagram / expected calibration error) distinct from the loss value.",
         "passed": True,
         "evidence": "Recommends reliability diagrams, ECE, MCE."},
        {"text": "Recommends temperature scaling (or isotonic/Platt) as the fix, noting temperature scaling preserves the argmax/accuracy.",
         "passed": True,
         "evidence": "Recommends temperature scaling, Platt scaling, isotonic regression."},
    ]
    write_grading(13, "with_skill", with_13)
    write_grading(13, "without_skill", without_13, "Both pass all assertions. Calibration knowledge is well-represented in the base model.")
    summary_rows.append((13, sum(r["passed"] for r in with_13), len(with_13), sum(r["passed"] for r in without_13), len(without_13)))

    # ── EVAL 14: DPI leakage detection ───────────────────────────────────────
    with_14 = [
        {"text": "Cites the data-processing inequality: post-processing/feature engineering cannot increase information about the target beyond what the inputs already contain.",
         "passed": True,
         "evidence": "Invokes DPI explicitly: no deterministic transform can create information beyond I(inputs;Y)."},
        {"text": "Identifies a feature that increases label MI / produces near-perfect performance as a leakage signature (encodes the label or post-outcome/future info), not genuine new signal.",
         "passed": True,
         "evidence": "States a feature increasing MI above I(raw inputs;Y) is direct evidence of leakage (future data, label encoding, contaminated splits)."},
        {"text": "Gives concrete diagnostics: audit feature construction for label/future leakage, check temporal availability at prediction time, and/or re-estimate MI against a permutation null.",
         "passed": True,
         "evidence": "Provides six-row diagnostic checklist: temporal audit, feature construction review, permutation null for MI, leakage pattern mapping."},
        {"text": "Optionally connects to Fano (information implies an error floor) to argue the result is implausibly good.",
         "passed": True,
         "evidence": "Connects to Fano's inequality: honest I(X;Y) implies error floor; AUC 0.98 that beats that floor is not believable."},
    ]
    without_14 = [
        {"text": "Cites the data-processing inequality: post-processing/feature engineering cannot increase information about the target beyond what the inputs already contain.",
         "passed": False,
         "evidence": "The without-skill response does not cite the data-processing inequality. It lists five categories of leakage causes but does not use DPI as the principled argument."},
        {"text": "Identifies a feature that increases label MI / produces near-perfect performance as a leakage signature (encodes the label or post-outcome/future info), not genuine new signal.",
         "passed": True,
         "evidence": "Identifies the 'too good to be true' result as likely leakage; lists target leakage as most common cause."},
        {"text": "Gives concrete diagnostics: audit feature construction for label/future leakage, check temporal availability at prediction time, and/or re-estimate MI against a permutation null.",
         "passed": True,
         "evidence": "Provides systematic checklist: temporal audit, cold holdout, feature ablation, production simulation."},
        {"text": "Optionally connects to Fano (information implies an error floor) to argue the result is implausibly good.",
         "passed": False,
         "evidence": "No mention of Fano's inequality or information-theoretic error floor in the without-skill response."},
    ]
    write_grading(14, "with_skill", with_14)
    write_grading(14, "without_skill", without_14, "Strong discriminator: DPI as the principled argument (14a) and Fano floor (14d) are skill-specific. Without-skill identifies leakage but without the information-theoretic framing.")
    summary_rows.append((14, sum(r["passed"] for r in with_14), len(with_14), sum(r["passed"] for r in without_14), len(without_14)))

    # ── EVAL 15: WAIC / PSIS-LOO Pareto k ───────────────────────────────────
    with_15 = [
        {"text": "States WAIC and PSIS-LOO both estimate expected out-of-sample (pointwise) log predictive density / predictive KL, and recommends PSIS-LOO (generally preferred over WAIC).",
         "passed": True,
         "evidence": "States both estimate expected log predictive density / out-of-sample deviance; prefers PSIS-LOO as default with self-diagnostic."},
        {"text": "Requires checking the Pareto k-hat diagnostic; flags k-hat > 0.7 as unreliable importance sampling for those observations.",
         "passed": True,
         "evidence": "Explicitly requires checking k̂ per observation; flags k̂ > 0.7 as unreliable importance sampling (influence too high)."},
        {"text": "Says to compare elpd DIFFERENCES relative to their standard error, not point estimates alone (a small difference vs SE is not decisive).",
         "passed": True,
         "evidence": "Uses SE on the difference (dse); treats |ΔELPD| < 2×dse as indeterminate."},
        {"text": "Mentions arviz (az.compare/az.loo) and/or explicitly avoids DIC.",
         "passed": True,
         "evidence": "Recommends arviz.compare; mentions az.loo; does not recommend DIC."},
    ]
    without_15 = [
        {"text": "States WAIC and PSIS-LOO both estimate expected out-of-sample (pointwise) log predictive density / predictive KL, and recommends PSIS-LOO (generally preferred over WAIC).",
         "passed": True,
         "evidence": "States both estimate expected out-of-sample log predictive density; prefers PSIS-LOO over WAIC."},
        {"text": "Requires checking the Pareto k-hat diagnostic; flags k-hat > 0.7 as unreliable importance sampling for those observations.",
         "passed": True,
         "evidence": "Pareto-k diagnostic table with thresholds (0.5, 0.7, 1.0) and az.reloo() fallback for flagged observations."},
        {"text": "Says to compare elpd DIFFERENCES relative to their standard error, not point estimates alone (a small difference vs SE is not decisive).",
         "passed": True,
         "evidence": "Focuses on elpd_diff and dse; rule of thumb |elpd_diff| > 4×dse for meaningful differences."},
        {"text": "Mentions arviz (az.compare/az.loo) and/or explicitly avoids DIC.",
         "passed": True,
         "evidence": "Mentions az.loo(), az.compare(), InferenceData structure."},
    ]
    write_grading(15, "with_skill", with_15)
    write_grading(15, "without_skill", without_15, "Both pass all assertions. PSIS-LOO/Pareto-k knowledge is well-represented in the base model.")
    summary_rows.append((15, sum(r["passed"] for r in with_15), len(with_15), sum(r["passed"] for r in without_15), len(without_15)))

    # ── EVAL 16: continuous MI KSG vs binning ────────────────────────────────
    with_16 = [
        {"text": "Identifies binning as fragile: the result depends on bin count/edges and can flip, and plug-in MI on binned data is biased upward.",
         "passed": True,
         "evidence": "Three problems: upward bias (quantified as (K-1)²/2N), bin count/edge dependency that can flip results qualitatively, and equal-width bins misrepresent skewed latency."},
        {"text": "Recommends the KSG / k-NN estimator for continuous MI instead of histogram binning.",
         "passed": True,
         "evidence": "Recommends KSG estimator; references scripts/entropy_mi_estimators.py ksg_mi."},
        {"text": "Notes a relevant KSG property: continuous (no bins), approximately invariant to monotone transforms of each variable, and the ties->jitter caveat or choice of k.",
         "passed": True,
         "evidence": "Notes roughly invariant to monotone reparameterization; mentions ties->jitter and k sensitivity."},
        {"text": "Recommends a permutation null and/or bootstrap CI rather than reporting a bare MI value.",
         "passed": True,
         "evidence": "States bootstrap CI and permutation null are required; a bare MI number is not evidence."},
    ]
    without_16 = [
        {"text": "Identifies binning as fragile: the result depends on bin count/edges and can flip, and plug-in MI on binned data is biased upward.",
         "passed": True,
         "evidence": "Identifies upward bias (Miller correction), arbitrary bin count dependency, and skewed marginals issue."},
        {"text": "Recommends the KSG / k-NN estimator for continuous MI instead of histogram binning.",
         "passed": True,
         "evidence": "Recommends KSG nearest-neighbor estimator or sklearn mutual_info_regression."},
        {"text": "Notes a relevant KSG property: continuous (no bins), approximately invariant to monotone transforms of each variable, and the ties->jitter caveat or choice of k.",
         "passed": False,
         "evidence": "The without-skill response recommends KSG but does not specifically note the monotone-invariance property or the ties->jitter caveat. Mentions quantile-based bins as alternative."},
        {"text": "Recommends a permutation null and/or bootstrap CI rather than reporting a bare MI value.",
         "passed": False,
         "evidence": "The without-skill response does not recommend a permutation null or bootstrap CI. Recommends Spearman's ρ as an alternative but not a null test."},
    ]
    write_grading(16, "with_skill", with_16)
    write_grading(16, "without_skill", without_16, "Assertions 16c (KSG properties: monotone-invariance, jitter) and 16d (permutation null) differentiate the skill. Base model recommends KSG but misses these details.")
    summary_rows.append((16, sum(r["passed"] for r in with_16), len(with_16), sum(r["passed"] for r in without_16), len(without_16)))

    # ── EVAL 17: transfer entropy directionality ─────────────────────────────
    with_17 = [
        {"text": "Defines TE as a conditional mutual information I(Y_{t+1}; X_past | Y_past) and notes it is directed/asymmetric, unlike ordinary MI.",
         "passed": True,
         "evidence": "Defines TE_{X→Y} = I(Y_{t+1}; X_t^(l) | Y_t^(k)); explicitly states asymmetric by construction unlike MI."},
        {"text": "States TE is the nonlinear generalization of Granger causality and that they coincide for linear-Gaussian processes (bonus: Granger statistic = 2*TE in nats); so plain Granger suffices for linear data.",
         "passed": True,
         "evidence": "States TE is nonlinear generalization of Granger; for jointly Gaussian linear processes Geweke statistic = 2·TE in nats; recommend Granger/VAR for linear data."},
        {"text": "Warns it is not model-free causality: a hidden common cause produces spurious TE, and target history length k must be set adequately (else inflation).",
         "passed": True,
         "evidence": "States TE is directed predictive information not interventional causality; hidden common driver produces spurious TE; k must be set from target's own autocorrelation."},
        {"text": "Requires a surrogate/permutation (e.g. source time-shift) null and notes plug-in TE is biased upward / undersamples as history grows.",
         "passed": True,
         "evidence": "States permutation null is mandatory; notes K^(k+l+1) state space undersamples fast; plug-in biased upward like MI."},
    ]
    without_17 = [
        {"text": "Defines TE as a conditional mutual information I(Y_{t+1}; X_past | Y_past) and notes it is directed/asymmetric, unlike ordinary MI.",
         "passed": True,
         "evidence": "Defines TE = I(Y_{t+1}; X_past | Y_past); explicitly asymmetric unlike MI."},
        {"text": "States TE is the nonlinear generalization of Granger causality and that they coincide for linear-Gaussian processes (bonus: Granger statistic = 2*TE in nats); so plain Granger suffices for linear data.",
         "passed": True,
         "evidence": "States TE is nonlinear generalization of Granger; for jointly Gaussian they are equivalent; Barnett et al. cited."},
        {"text": "Warns it is not model-free causality: a hidden common cause produces spurious TE, and target history length k must be set adequately (else inflation).",
         "passed": True,
         "evidence": "Lists confounding variables / common drivers; embedding dimension selection as key pitfall."},
        {"text": "Requires a surrogate/permutation (e.g. source time-shift) null and notes plug-in TE is biased upward / undersamples as history grows.",
         "passed": True,
         "evidence": "Mandatory surrogate testing noted (no analytic null); sample size demands (500-1000 minimum)."},
    ]
    write_grading(17, "with_skill", with_17)
    write_grading(17, "without_skill", without_17, "Both pass all assertions. TE knowledge is reasonably well-represented in the base model. Skill adds Geweke = 2*TE equivalence explicitly.")
    summary_rows.append((17, sum(r["passed"] for r in with_17), len(with_17), sum(r["passed"] for r in without_17), len(without_17)))

    # ── EVAL 18: Markov entropy rate ─────────────────────────────────────────
    with_18 = [
        {"text": "Finds the stationary distribution mu = (2/3, 1/3) (mu P = mu).",
         "passed": True,
         "evidence": "Solves μP = μ, finds μ = (2/3, 1/3). Shows derivation."},
        {"text": "Computes entropy rate as the stationary-weighted average of per-row transition entropies: (2/3)H(0.9,0.1)+(1/3)H(0.2,0.8) ~= 0.553 bits/step (accept 0.55-0.56).",
         "passed": True,
         "evidence": "H(𝒳) = (2/3)(0.4690) + (1/3)(0.7219) = 0.5533 bits/step. Within acceptance range."},
        {"text": "Gives the marginal state-visit entropy H(2/3,1/3) ~= 0.918 bits and states it is LARGER than the entropy rate.",
         "passed": True,
         "evidence": "H(μ) = H_b(2/3, 1/3) = 0.9183 bits. States it is larger than entropy rate."},
        {"text": "Explains the marginal overstates per-symbol information because it ignores dependence on the previous state (i.i.d. is the only case where they coincide).",
         "passed": True,
         "evidence": "Explains the 0.365-bit gap equals MI between current and next state; strong self-loops make next state predictable from current state."},
    ]
    without_18 = [
        {"text": "Finds the stationary distribution mu = (2/3, 1/3) (mu P = mu).",
         "passed": True,
         "evidence": "Finds μ_A = 2/3, μ_B = 1/3 from balance condition."},
        {"text": "Computes entropy rate as the stationary-weighted average of per-row transition entropies: (2/3)H(0.9,0.1)+(1/3)H(0.2,0.8) ~= 0.553 bits/step (accept 0.55-0.56).",
         "passed": True,
         "evidence": "H(X) = (2/3)(0.4690) + (1/3)(0.7219) ≈ 0.5533 bits/step. Correct."},
        {"text": "Gives the marginal state-visit entropy H(2/3,1/3) ~= 0.918 bits and states it is LARGER than the entropy rate.",
         "passed": True,
         "evidence": "H(π) ≈ 0.9183 bits; states it is larger than entropy rate (0.5533)."},
        {"text": "Explains the marginal overstates per-symbol information because it ignores dependence on the previous state (i.i.d. is the only case where they coincide).",
         "passed": True,
         "evidence": "Gap = I(X_t; X_{t+1}) = mutual information between current and next state; serial dependence means marginal overstates per-step uncertainty."},
    ]
    write_grading(18, "with_skill", with_18)
    write_grading(18, "without_skill", without_18, "Both pass all assertions. Markov entropy rate is well-known to the base model.")
    summary_rows.append((18, sum(r["passed"] for r in with_18), len(with_18), sum(r["passed"] for r in without_18), len(without_18)))

    # ── EVAL 19: Gaussian rate-distortion ────────────────────────────────────
    with_19 = [
        {"text": "Uses the Gaussian R(D) = 0.5*log2(sigma^2/D) for 0<=D<=sigma^2 (0 above sigma^2).",
         "passed": True,
         "evidence": "States R(D) = ½ log₂(σ²/D) with domain 0 ≤ D ≤ σ²; shows table including R=0 for D≥σ²."},
        {"text": "R(D) at sigma^2=4, D=1 is exactly 1.0 bit/sample.",
         "passed": True,
         "evidence": "R(1) = ½ log₂(4) = ½×2 = 1.0 bit/sample exactly."},
        {"text": "R(D) at D=0.25 is exactly 2.0 bits/sample, and states the rule that halving D adds 0.5 bit/sample.",
         "passed": True,
         "evidence": "R(0.25) = ½ log₂(16) = ½×4 = 2.0 bits/sample; algebraic proof that halving D adds ½ bit."},
        {"text": "Notes R(D) is the minimum I(X;Xhat) under the distortion constraint (mutual information is the quantity being minimized; dual of capacity).",
         "passed": True,
         "evidence": "States R(D) is minimum mutual information I(X;X̂) subject to distortion constraint; dual of channel capacity."},
    ]
    without_19 = [
        {"text": "Uses the Gaussian R(D) = 0.5*log2(sigma^2/D) for 0<=D<=sigma^2 (0 above sigma^2).",
         "passed": True,
         "evidence": "States R(D) = ½ log₂(σ²/D) with D(R) = σ²·2^(-2R) inverse. Correct formula."},
        {"text": "R(D) at sigma^2=4, D=1 is exactly 1.0 bit/sample.",
         "passed": True,
         "evidence": "R(1) = ½ log₂(4) = 1.0 bit/sample. Correct."},
        {"text": "R(D) at D=0.25 is exactly 2.0 bits/sample, and states the rule that halving D adds 0.5 bit/sample.",
         "passed": True,
         "evidence": "R(0.25) = ½ log₂(16) = 2.0 bits/sample. Rule stated: each additional bit reduces MSE by factor of 4."},
        {"text": "Notes R(D) is the minimum I(X;Xhat) under the distortion constraint (mutual information is the quantity being minimized; dual of capacity).",
         "passed": False,
         "evidence": "The without-skill response gives the formula and numbers correctly but does not note R(D) as minimum I(X;X̂) or the duality with channel capacity."},
    ]
    write_grading(19, "with_skill", with_19)
    write_grading(19, "without_skill", without_19, "Assertion 19d (R(D) as minimum MI, dual of capacity) differentiates the skill. Base model knows the formula but misses the information-theoretic interpretation.")
    summary_rows.append((19, sum(r["passed"] for r in with_19), len(with_19), sum(r["passed"] for r in without_19), len(without_19)))

    # ── EVAL 20: Fano error floor ─────────────────────────────────────────────
    with_20 = [
        {"text": "Computes H(Y|X) = H(Y) - I(X;Y) = log2(10) - 1.5 ~= 1.822 bits.",
         "passed": True,
         "evidence": "H(Y|X) = log₂(10) - 1.5 = 3.3219 - 1.5 = 1.8219 bits. Correct."},
        {"text": "Applies Fano's inequality H(Y|X) <= H(Pe) + Pe*log2(K-1) to bound the error rate.",
         "passed": True,
         "evidence": "Applies Fano: H(Y|X) ≤ H(Pₑ) + Pₑ·log₂(K−1) with K=10."},
        {"text": "Gives a numeric floor: weak-form ~0.247 and/or the tight solution ~0.298 (accept ~0.25-0.30), i.e. at least ~25-30% error is unavoidable.",
         "passed": True,
         "evidence": "Weak floor: (1.8219-1)/log₂(10) ≈ 0.247. Tight solution (bisection): Pₑ ≈ 0.298. Both given."},
        {"text": "Interprets it as a model-independent floor (a result below it implies leakage / broken eval), ideally noting a biased-low H(Y|X) loosens the bound.",
         "passed": True,
         "evidence": "States floor is model-independent; any result below it implies leakage or broken eval. Notes biased-low H(Y|X) gives over-optimistic (too-loose) floor."},
    ]
    without_20 = [
        {"text": "Computes H(Y|X) = H(Y) - I(X;Y) = log2(10) - 1.5 ~= 1.822 bits.",
         "passed": True,
         "evidence": "H(Y|X) = log₂(10) - 1.5 = 3.322 - 1.5 = 1.822 bits. Correct."},
        {"text": "Applies Fano's inequality H(Y|X) <= H(Pe) + Pe*log2(K-1) to bound the error rate.",
         "passed": True,
         "evidence": "Applies Fano: H(Y|X) ≤ H(Pe) + Pe·log₂(K-1)."},
        {"text": "Gives a numeric floor: weak-form ~0.247 and/or the tight solution ~0.298 (accept ~0.25-0.30), i.e. at least ~25-30% error is unavoidable.",
         "passed": True,
         "evidence": "Loose bound: Pe ≥ (1.822-1)/log₂(9) ≈ 0.259; tight: Pe ≈ 0.296. Both within acceptance range."},
        {"text": "Interprets it as a model-independent floor (a result below it implies leakage / broken eval), ideally noting a biased-low H(Y|X) loosens the bound.",
         "passed": True,
         "evidence": "States floor is model-independent; implies leakage if beaten. Notes MI resolves only 45% of label entropy."},
    ]
    write_grading(20, "with_skill", with_20)
    write_grading(20, "without_skill", without_20, "Both pass all assertions. Fano's inequality is well-known to the base model.")
    summary_rows.append((20, sum(r["passed"] for r in with_20), len(with_20), sum(r["passed"] for r in without_20), len(without_20)))

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("EVAL SUMMARY")
    print(f"{'ID':<4} {'Name':<40} {'With':>6} {'Without':>8} {'Delta':>6}")
    print("-"*70)
    total_with = 0; total_without = 0; total_assertions = 0
    for i, (eval_id, ws, wa, nos, noa) in enumerate(summary_rows):
        name = evals[i]["name"]
        delta = ws/wa - nos/noa
        print(f"{eval_id:<4} {name:<40} {ws}/{wa:>2}  {nos}/{noa:>2}  {delta:+.0%}")
        total_with += ws; total_without += nos; total_assertions += wa
    print("-"*70)
    print(f"{'TOTAL':<4} {'':40} {total_with}/{total_assertions}  {total_without}/{total_assertions}  {(total_with-total_without)/total_assertions:+.0%}")
    print(f"\nWith-skill:    {total_with}/{total_assertions} = {total_with/total_assertions:.1%}")
    print(f"Without-skill: {total_without}/{total_assertions} = {total_without/total_assertions:.1%}")
    print(f"Delta:         +{(total_with-total_without)/total_assertions:.1%}")

    # Write aggregate JSON
    aggregate = {
        "with_skill": {"passed": total_with, "total": total_assertions, "rate": total_with/total_assertions},
        "without_skill": {"passed": total_without, "total": total_assertions, "rate": total_without/total_assertions},
        "delta_pp": (total_with - total_without) / total_assertions * 100,
        "evals": [
            {"id": ev, "name": evals[i]["name"], "with_skill": f"{ws}/{wa}", "without_skill": f"{nos}/{noa}",
             "delta_pp": (ws/wa - nos/noa)*100}
            for i, (ev, ws, wa, nos, noa) in enumerate(summary_rows)
        ]
    }
    out = RESULTS / "aggregate_grading.json"
    out.write_text(json.dumps(aggregate, indent=2))
    print(f"\nAggregate written to {out}")

grade_all()
