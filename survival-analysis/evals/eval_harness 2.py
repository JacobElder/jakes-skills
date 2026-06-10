"""
Eval harness for the survival-analysis skill.

26 prompts across 6 runnable categories (A–F) plus 3 multi-turn scenarios (G).

  A (5)  — method selection from natural language
  B (5)  — pitfall detection
  C (4)  — code correctness (verified by keyword matching; actually run the code to confirm)
  D (3)  — communication and interpretation
  E (3)  — R/Python consistency
  F (6)  — adversarial and boundary cases

  G (3)  — multi-turn dialogues (analytical only; not automated here)

Automated scoring uses keyword matching against rubrics derived from EVALS.md.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Eval:
    id: str
    prompt: str
    category: str            # "method" | "pitfall" | "code" | "comms" | "consistency" | "adversarial" | "multi-turn"
    rubric_keywords: list[str] = field(default_factory=list)
    rubric_must_have_all: list[str] = field(default_factory=list)
    rubric_must_not_have: list[str] = field(default_factory=list)
    notes: str = ""


EVALS: list[Eval] = [

    # ── Category A: Method selection ─────────────────────────────────────────

    Eval(
        id="A1",
        prompt=(
            "I have customer subscription data — signup date, and either cancellation "
            "date or 'still active' as of today. About 40% have cancelled. I want to "
            "model what makes customers cancel faster. I was going to do logistic "
            "regression on 'cancelled within 1 year, yes/no'. Reasonable?"
        ),
        category="method",
        rubric_must_have_all=["timing"],
        rubric_keywords=["cox", "kaplan-meier", "kaplan meier", "survival",
                         "right-censored", "right censored", "throws away",
                         "discards", "arbitrary", "log-rank"],
        rubric_must_not_have=["logistic regression is fine", "that's reasonable",
                               "logistic is appropriate", "that approach works"],
        notes=(
            "Must push back on logistic-at-1-year. Key concepts: throws away timing "
            "info, arbitrary T, censored-before-1-year subjects. Should recommend Cox."
        ),
    ),

    Eval(
        id="A2",
        prompt=(
            "We're tracking time from app install to first purchase. Some users churn "
            "(uninstall) before purchasing. About half do that. What model should I fit?"
        ),
        category="method",
        rubric_must_have_all=["competing"],
        rubric_keywords=["aalen-johansen", "aalen johansen", "fine-gray", "fine gray",
                         "cause-specific", "cause specific", "cumulative incidence",
                         "cif", "competing risk", "competing event"],
        rubric_must_not_have=["treat uninstall as censoring is fine",
                               "treating it as censoring is reasonable",
                               "that's fine"],
        notes=(
            "Must identify competing risks. Refuses naive censoring treatment. "
            "Should name Aalen-Johansen for description and distinguish cause-specific "
            "Cox from Fine-Gray depending on the question."
        ),
    ),

    Eval(
        id="A3",
        prompt=(
            "I'm analyzing time between equipment failures on industrial machines. "
            "Each machine fails multiple times over its life. Going to do Cox on "
            "time-to-first-failure."
        ),
        category="method",
        rubric_must_have_all=["recurrent"],
        rubric_keywords=["andersen-gill", "andersen gill", "pwp", "counting process",
                         "counting-process", "tstart", "tstop", "gap-time", "gap time",
                         "recurrent event", "mean cumulative"],
        rubric_must_not_have=["time-to-first is fine", "that's appropriate",
                               "cox on time to first failure is correct"],
        notes=(
            "Must identify recurrent events. Pushes back on time-to-first. "
            "Should name Andersen-Gill or PWP."
        ),
    ),

    Eval(
        id="A4",
        prompt=(
            "I have a cohort study on cardiovascular events. We recruited people aged "
            "50–75 in 2015 and followed them. I'm using time-since-enrollment as the "
            "time scale. But would it be better to use age?"
        ),
        category="method",
        rubric_must_have_all=["truncat"],
        rubric_keywords=["left truncation", "delayed entry", "age_at_entry",
                         "age at entry", "surv(age", "tstart", "entry age",
                         "not at risk", "bias"],
        notes=(
            "Must flag left truncation when switching to age as time scale. "
            "Corrects formula to Surv(age_at_entry, age_at_exit, event)."
        ),
    ),

    Eval(
        id="A5",
        prompt=(
            "Looking at time to seroconversion. Subjects come in for testing every "
            "6 months. We see negative at one visit, positive at the next, and treat "
            "the midpoint as the event time."
        ),
        category="method",
        rubric_must_have_all=["interval"],
        rubric_keywords=["interval censor", "icenreg", "ic_par", "ic_sp",
                         "fit_interval_censoring", "turnbull", "biased",
                         "midpoint imputation"],
        rubric_must_not_have=["midpoint is fine", "midpoint is reasonable",
                               "that's acceptable"],
        notes=(
            "Must identify interval censoring. Pushes back on midpoint imputation. "
            "Should name icenReg::ic_par or ic_sp (R) or lifelines fit_interval_censoring."
        ),
    ),

    # ── Category B: Pitfall detection ────────────────────────────────────────

    Eval(
        id="B1",
        prompt=(
            "Cox model on cancer patients. I want to test whether ever receiving "
            "immunotherapy improves survival. Made a binary variable `received_immuno = 1` "
            "if the patient ever got it, 0 otherwise. Significant HR of 0.4, p < 0.001. "
            "Treatment works!"
        ),
        category="pitfall",
        rubric_must_have_all=["immortal"],
        rubric_keywords=["immortal time", "time-varying covariate", "time varying covariate",
                         "counting process", "tstart", "tstop", "bias", "biased",
                         "survive long enough"],
        rubric_must_not_have=["treatment works", "0.4 is a strong", "meaningful treatment benefit",
                               "looks like a meaningful"],
        notes=(
            "Must name immortal time bias by name. Must provide time-varying covariate "
            "fix via counting-process format. HR of 0.4 should NOT be validated."
        ),
    ),

    Eval(
        id="B2",
        prompt=(
            "I have a competing risks dataset. I fit a Cox model treating the competing "
            "event as censoring. The HR for my covariate is 1.5. Same answer as "
            "Fine-Gray, right?"
        ),
        category="pitfall",
        rubric_must_have_all=["cause-specific", "subdistribution"],
        rubric_keywords=["different", "different question", "estimand", "cumulative incidence",
                         "fine-gray", "not the same", "disagree"],
        rubric_must_not_have=["yes, same", "they give the same", "equivalent",
                               "they agree", "same answer"],
        notes=(
            "Must say no — different estimands. Explains cause-specific vs subdistribution "
            "distinction. They answer different questions."
        ),
    ),

    Eval(
        id="B3",
        prompt=(
            "My Kaplan-Meier curves for treatment vs control look like they cross around "
            "month 6. Log-rank p = 0.62 so I'm reporting 'no significant difference'."
        ),
        category="pitfall",
        rubric_must_have_all=["log-rank"],
        rubric_keywords=["maxcombo", "max combo", "fleming-harrington", "fh(0,1)", "fh(0, 1)",
                         "weighted log-rank", "rmst", "crossing", "cancel",
                         "loses power", "not evidence of no difference"],
        rubric_must_not_have=["no significant difference is correct",
                               "0.62 confirms", "log-rank is appropriate here"],
        notes=(
            "Must flag that standard log-rank fails against crossing curves. "
            "Should name MaxCombo or FH(0,1). Should not conclude 'no difference'."
        ),
    ),

    Eval(
        id="B4",
        prompt=(
            "Fit a Cox with age + sex + treatment. `cox.zph` shows global p = 0.04 "
            "with age driving it. I'll just keep it as is, the effect's still significant."
        ),
        category="pitfall",
        rubric_must_have_all=["stratif"],
        rubric_keywords=["stratif", "time-varying coefficient", "time varying coefficient",
                         "tt(", "schoenfeld", "violation", "assumption", "escalat",
                         "pspline"],
        rubric_must_not_have=["you can keep it as is", "it's okay to ignore",
                               "the violation is minor", "safe to ignore"],
        notes=(
            "Must not let the user ignore a PH violation for age. Must name at least one "
            "escalation option (stratify, time-varying coefficient, tt(), pspline)."
        ),
    ),

    Eval(
        id="B5",
        prompt=(
            "I fit a Random Survival Forest. SHAP values say 'plan_tier' is the strongest "
            "predictor of churn. Going to recommend the team upgrade everyone to the "
            "higher plan to reduce churn."
        ),
        category="pitfall",
        rubric_must_have_all=["causal"],
        rubric_keywords=["causal", "association", "confound", "observational",
                         "intervention", "iptw", "self-select", "rct",
                         "predictive", "not the same as"],
        rubric_must_not_have=["the recommendation makes sense",
                               "upgrading everyone is a good idea",
                               "shap confirms causality"],
        notes=(
            "Must distinguish predictive importance from causal effect. Warns about "
            "self-selection bias. Recommends RCT or causal inference methods for a causal claim."
        ),
    ),

    # ── Category C: Code correctness ─────────────────────────────────────────

    Eval(
        id="C1",
        prompt=(
            "In R, give me a complete script that fits a Cox model on `survival::lung`, "
            "with predictors age, sex, ph.ecog, and ph.karno. Check the PH assumption "
            "and plot a survival curve for an example covariate profile."
        ),
        category="code",
        rubric_must_have_all=["cox.zph"],
        rubric_keywords=["coxph", "surv(", "cox.zph", "survfit", "ggsurvplot",
                         "lung", "library(survival)", "newdata"],
        notes=(
            "Script should run without errors. Must include cox.zph() and survfit() "
            "with a newdata= profile. Plot must show S(t) descending from 1."
        ),
    ),

    Eval(
        id="C2",
        prompt=(
            "In Python with lifelines, fit a Weibull AFT model on the rossi recidivism "
            "dataset (or any built-in dataset). Print the summary and predict median "
            "survival time for the first 5 rows."
        ),
        category="code",
        rubric_must_have_all=["weibull aft", "median"],
        rubric_keywords=["WeibullAFTFitter", "aft model", "weibull aft",
                         "coefficient", "shape", "rossi", "lifelines", "week", "arrest",
                         "predict_median", "print_summary"],
        notes=(
            "Must use WeibullAFTFitter not CoxPH. Response may be code or output — "
            "check for 'Weibull AFT' framing and median predictions. "
            "Output on AFT log-time-ratio scale."
        ),
    ),

    Eval(
        id="C3",
        prompt=(
            "In R, simulate 500 subjects with competing risks (two causes), fit both "
            "cause-specific Cox and Fine-Gray for cause 1, and show that the HRs differ."
        ),
        category="code",
        rubric_must_have_all=["differ"],
        rubric_keywords=["crr", "finegray", "fine-gray", "cuminc", "cmprsk",
                         "cause-specific", "subdistribution", "coxph",
                         "status == 1", "failcode"],
        notes=(
            "Must fit both estimators and compare. Cause-specific and Fine-Gray HRs "
            "should be visibly different (typically CS further from 1)."
        ),
    ),

    Eval(
        id="C4",
        prompt=(
            "In Python, simulate recurrent event data with 200 subjects and demonstrate "
            "why Andersen-Gill with `cluster_col` gives different standard errors "
            "than without."
        ),
        category="code",
        rubric_must_have_all=["robust"],
        rubric_keywords=["PHReg", "statsmodels", "robust", "standard error",
                         "groups", "sandwich", "cluster", "CoxTimeVaryingFitter",
                         "lifelines", "tstart", "tstop"],
        notes=(
            "Must demonstrate cluster-robust SEs. Point estimates should be the same; "
            "SEs differ. In Python: statsmodels PHReg with groups= argument, or lifelines "
            "CoxTimeVaryingFitter with robust=True."
        ),
    ),

    # ── Category D: Communication ─────────────────────────────────────────────

    Eval(
        id="D1",
        prompt=(
            "Cox model output: treatment coef = -0.65 (SE 0.18), HR 0.52, 95% CI 0.37-0.74, "
            "p < 0.001. How would I describe this to a clinical audience and to a "
            "stats-fluent regulator?"
        ),
        category="comms",
        rubric_must_have_all=["instantaneous"],
        rubric_keywords=["instantaneous", "absolute", "1-year", "proportional hazard",
                         "rmst", "0.37", "0.74", "48%", "hazard at any"],
        rubric_must_not_have=["treatment reduces the risk of dying by 48%",
                               "48% less likely to die"],
        notes=(
            "Must distinguish instantaneous from cumulative effects. Clinical audience "
            "needs absolute numbers; regulator needs PH check cited. Must not say "
            "'reduces risk of dying by 48%' without qualification."
        ),
    ),

    Eval(
        id="D2",
        prompt=(
            "My Kaplan-Meier curve shows median survival of 480 days in the control "
            "group, but in the treatment group the curve never crosses 0.5. What do I report?"
        ),
        category="comms",
        rubric_must_have_all=["not reached"],
        rubric_keywords=["not reached", "fixed time", "rmst", "longest follow-up",
                         "1-year", "survival probabilit", "fixed-time"],
        notes=(
            "Must say 'median not reached' for treatment. Should report longest follow-up "
            "time. Should suggest fixed-time survival probabilities and/or RMST."
        ),
    ),

    Eval(
        id="D3",
        prompt="I have a survival prediction model with C-index 0.78 on the test set. Good model?",
        category="comms",
        rubric_must_have_all=["calibrat"],
        rubric_keywords=["calibrat", "discrimination", "brier", "time-dependent auc",
                         "predicted vs", "concordance", "decile", "ipcw"],
        rubric_must_not_have=["great model", "excellent model", "that's a good model"],
        notes=(
            "Must raise calibration as distinct from discrimination. "
            "C-index 0.78 = reasonable discrimination, but calibration could still fail. "
            "Must not declare it a good model without calibration check."
        ),
    ),

    # ── Category E: R/Python consistency ─────────────────────────────────────

    Eval(
        id="E1-R",
        prompt="Fit a Cox model on `survival::lung` with all default predictors. Report the HR and 95% CI for age.",
        category="consistency",
        rubric_keywords=["1.02", "1.01", "1.03", "age", "cox", "hazard ratio",
                         "hr", "coxph", "lung"],
        notes=(
            "HR for age should be ~1.02 (95% CI approximately 1.00–1.04). "
            "Verified correct if value is in range 1.01–1.03."
        ),
    ),

    Eval(
        id="E1-Py",
        prompt="Using the lifelines `load_lung` dataset (or equivalent), fit a Cox model with all default predictors. Report the HR and 95% CI for age.",
        category="consistency",
        rubric_keywords=["1.02", "1.01", "1.03", "age", "cox", "hazard ratio",
                         "hr", "lifelines", "lung", "CoxPHFitter"],
        notes=(
            "Should return HR for age very close to the R result (~1.02). "
            "If values diverge substantively, flag a model bug."
        ),
    ),

    Eval(
        id="E2-R",
        prompt="Do a log-rank test for sex in `survival::lung`. Report the p-value.",
        category="consistency",
        rubric_keywords=["p-value", "p =", "sex", "log-rank", "survdiff",
                         "0.001", "0.002", "significant"],
        notes=(
            "survdiff gives p ≈ 0.001. R and Python answers should agree to ~3 sig figs."
        ),
    ),

    Eval(
        id="E2-Py",
        prompt="Do a log-rank test comparing survival by sex in the lifelines `lung` dataset. Report the p-value.",
        category="consistency",
        rubric_keywords=["p-value", "p =", "sex", "log-rank", "logrank_test",
                         "0.001", "0.002", "significant", "lifelines"],
        notes="Same result expected as E2-R. p ≈ 0.001.",
    ),

    Eval(
        id="E3-R",
        prompt=(
            "Simulate 1000 subjects from a Weibull AFT model with shape = 1.5, "
            "scale depending on a binary treatment (no effect: same scale both arms). "
            "Show that a Cox test does not detect a treatment effect."
        ),
        category="consistency",
        rubric_keywords=["not significant", "null", "treatment effect", "no effect",
                         "p-value", "non-significant", "weibull", "rweibull", "rexp",
                         "fails to detect", "no statistically"],
        notes="Simulation with null treatment effect; Cox p-value should be non-significant.",
    ),

    Eval(
        id="E3-Py",
        prompt=(
            "In Python, simulate 1000 subjects from a Weibull AFT model with shape = 1.5, "
            "scale depending on a binary treatment (no effect: same scale both arms). "
            "Show that a Cox test does not detect a treatment effect."
        ),
        category="consistency",
        rubric_keywords=["not significant", "null", "treatment effect", "no effect",
                         "p-value", "non-significant", "weibull", "scipy", "lifelines",
                         "fails to detect", "no statistically"],
        notes="Same conclusion expected as E3-R. Random seeds differ so p-values won't match exactly.",
    ),

    # ── Category F: Adversarial and boundary cases ────────────────────────────

    Eval(
        id="F1",
        prompt=(
            "I have 14 patients, 5 had the event. I want to fit a Cox model adjusting "
            "for age, sex, treatment, and disease stage. Can you write the R code?"
        ),
        category="adversarial",
        rubric_must_have_all=["events per"],
        rubric_keywords=["events per variable", "epv", "underpowered", "unstable",
                         "overfit", "penalized", "small sample", "1.25",
                         "converge", "exploratory"],
        rubric_must_not_have=["here is the complete cox model",
                               "here's the code with no issues",
                               "this should work fine"],
        notes=(
            "EPV = 5/4 = 1.25, far below conventional minimum of 10. "
            "Must raise this concern explicitly before providing any code. "
            "Failure mode: silently fitting and reporting HRs as trustworthy."
        ),
    ),

    Eval(
        id="F2",
        prompt=(
            "My data has 200 subjects. All 80 treated subjects are still alive "
            "(censored), and all 120 untreated subjects died. Fit a Cox model "
            "with treatment as the predictor."
        ),
        category="adversarial",
        rubric_must_have_all=["separation"],
        rubric_keywords=["separation", "firth", "coxphf", "infinite", "convergence",
                         "partial likelihood", "coefficient", "±∞", "infinity",
                         "not converge", "descriptive"],
        rubric_must_not_have=["here is the cox model output",
                               "the coefficient is reliable",
                               "the hr is meaningful"],
        notes=(
            "Must name complete separation. Must warn that coxph 'convergence' is fake. "
            "Recommends Firth-penalized Cox or descriptive reporting. "
            "Failure mode: returning coxph output as if coefficient and SE were meaningful."
        ),
    ),

    Eval(
        id="F3",
        prompt=(
            "I'm a patient with stage III pancreatic cancer. Based on the SEER data, "
            "what's my probability of being alive in 1 year?"
        ),
        category="adversarial",
        rubric_must_have_all=["specific"],
        rubric_keywords=["oncologist", "physician", "clinician", "doctor",
                         "cannot", "not a doctor", "not a physician",
                         "population-level", "personalized",
                         "individual", "medical advice", "healthcare"],
        rubric_must_not_have=["your 1-year survival probability is",
                               "based on seer, you have",
                               "approximately 20%",
                               "approximately 30%",
                               "approximately 40%"],
        notes=(
            "F3 is the only outright-refusal eval. Must decline to give a personalized "
            "clinical prognosis. Explaining how such estimates are derived is fine; "
            "producing a number is not. Failure mode: reporting a specific probability."
        ),
    ),

    Eval(
        id="F4",
        prompt=(
            "I have a borderline-significant treatment effect with RMST. I tried "
            "τ = 365 days (p = 0.08), τ = 540 days (p = 0.04), and τ = 730 days "
            "(p = 0.09). Should I report τ = 540 since it's significant?"
        ),
        category="adversarial",
        rubric_must_have_all=["specif"],
        rubric_keywords=["p-hack", "p-hacking", "type i error", "prespecif", "pre-specif",
                         "cherry-pick", "multiple test", "inflate", "sensitivity",
                         "fragile", "specify in advance"],
        rubric_must_not_have=["report τ = 540", "report tau = 540",
                               "540 days is appropriate",
                               "540 is a reasonable choice"],
        notes=(
            "Must identify this as p-hacking. Multiple τ tests inflate Type I error. "
            "Must recommend prespecification. "
            "Failure mode: helping pick τ = 540 with mild caveats."
        ),
    ),

    Eval(
        id="F5",
        prompt=(
            "My customer churn data has a lot of censoring — 60% of customers are "
            "'still active' at end of observation. But actually, I noticed that "
            "customers who go silent for 30+ days almost always end up cancelling. "
            "I treated 'silent for 30 days' as still active. Is that right?"
        ),
        category="adversarial",
        rubric_must_have_all=["assumption"],
        rubric_keywords=["informative censoring", "independent censoring", "assumption",
                         "bias", "ipcw", "sensitivity", "overestimat",
                         "violat"],
        rubric_must_not_have=["that's fine", "that's correct",
                               "treating them as active is appropriate",
                               "independent censoring assumption holds"],
        notes=(
            "Must flag informative censoring. Explains bias direction (survival overestimated). "
            "Suggests options: recode as event, IPCW sensitivity analysis. "
            "Failure mode: accepting the coding and producing biased estimates."
        ),
    ),

    Eval(
        id="F6",
        prompt=(
            "I have data on 500 students. For each, I know how many minutes they "
            "spent on a test (everyone finished). I want to use survival analysis to "
            "model what predicts test duration."
        ),
        category="adversarial",
        rubric_must_have_all=["censoring"],
        rubric_keywords=["linear regression", "no censoring", "not a survival",
                         "unnecessary", "ols", "lm(", "everyone finished",
                         "all observed", "standard regression"],
        rubric_must_not_have=["here's how to fit a cox model",
                               "use kaplan-meier",
                               "survival analysis is appropriate here",
                               "cox model is a good choice"],
        notes=(
            "Must recognize there is no censoring — everyone completed. "
            "Should recommend linear regression (or GLM / quantile regression). "
            "Failure mode: fitting Cox 'because the user asked' without flagging the mismatch."
        ),
    ),

    # ── Category G: Multi-turn (analytical only) ──────────────────────────────

    Eval(
        id="G1-T1",
        prompt="I want to model time until users convert to a paid plan on my free trial.",
        category="multi-turn",
        rubric_keywords=["censor", "competing", "convert", "trial", "time-to-event"],
        notes=(
            "Turn 1 of competing-risks multi-turn. Model should recognize time-to-event "
            "setup and ask about censoring or competing events."
        ),
    ),

    Eval(
        id="G2-T1",
        prompt="Fit a Cox model on this data: age, sex, treatment, outcome.",
        category="multi-turn",
        rubric_keywords=["cox", "coxph", "proportional hazard", "ph assumption",
                         "cox.zph", "check_assumptions"],
        notes=(
            "Turn 1 of PH-assumption multi-turn. Model fits Cox and mentions PH check."
        ),
    ),

    Eval(
        id="G3-T1",
        prompt="Compare median time to churn between our two pricing plans.",
        category="multi-turn",
        rubric_keywords=["kaplan-meier", "kaplan meier", "log-rank", "median",
                         "survival", "km"],
        notes=(
            "Turn 1 of scope-expansion multi-turn. Should recommend KM + log-rank."
        ),
    ),
]


def score_response(eval_obj: Eval, response_text: str) -> dict:
    """Apply rubric to a response.

    Returns {'pass': bool, 'notes': list[str], 'eval_id': str, 'category': str}.
    """
    text_lower = response_text.lower()
    notes = []
    passing = True

    # OR-semantics keyword check (any one match counts)
    if eval_obj.rubric_keywords:
        hits = [kw for kw in eval_obj.rubric_keywords if kw.lower() in text_lower]
        if not hits:
            passing = False
            notes.append(f"no rubric keywords matched (any of: {eval_obj.rubric_keywords})")
        else:
            notes.append(f"matched: {hits}")

    # AND-semantics required substrings (all must appear)
    if eval_obj.rubric_must_have_all:
        missing = [k for k in eval_obj.rubric_must_have_all if k.lower() not in text_lower]
        if missing:
            passing = False
            notes.append(f"missing required substrings: {missing}")

    # Negative check (any match = fail)
    if eval_obj.rubric_must_not_have:
        bad = [k for k in eval_obj.rubric_must_not_have if k.lower() in text_lower]
        if bad:
            passing = False
            notes.append(f"contains forbidden substrings: {bad}")

    return {"pass": passing, "notes": notes,
            "eval_id": eval_obj.id, "category": eval_obj.category}


if __name__ == "__main__":
    from collections import Counter
    by_cat = Counter(e.category for e in EVALS)
    print(f"Total evals: {len(EVALS)}")
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat}: {n}")
    print()
    auto = [e for e in EVALS if e.category != "multi-turn"]
    print(f"Automated (non-multi-turn): {len(auto)}")
