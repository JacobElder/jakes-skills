"""
Lightweight programmatic eval harness for the comp-modeling skill.

The evals in evals.md are mostly behavioral and require LLM grading. This file
provides the structured machine-readable versions that can be fed to an
automated harness (e.g., Claude Code running an eval loop, or a custom script
calling the Anthropic API).

Each eval has:
  - id: unique string
  - prompt: what to send to the model
  - category: triggering | routing | content
  - expected_files: which references should be read (for routing evals)
  - rubric_keywords: substrings the response should contain (for content evals;
    OR semantics — any one match counts)
  - rubric_must_have_all: substrings that MUST all appear (AND semantics)
  - rubric_must_not_have: substrings that should NOT appear (failure if present)
  - notes: human-readable judgment guide for ambiguous cases

The harness is structured so that automated scoring catches the obvious wins,
and human review handles the rest.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Eval:
    id: str
    prompt: str
    category: str  # "triggering" | "routing" | "content"
    expected_files: list[str] = field(default_factory=list)
    rubric_keywords: list[str] = field(default_factory=list)
    rubric_must_have_all: list[str] = field(default_factory=list)
    rubric_must_not_have: list[str] = field(default_factory=list)
    skill_should_fire: bool = True
    notes: str = ""


EVALS: list[Eval] = [
    # ------- Triggering -------
    Eval(
        id="T1",
        prompt="I want to fit a Rescorla-Wagner model to my probabilistic reversal data — what's the best way to start?",
        category="triggering",
        skill_should_fire=True,
        expected_files=["reinforcement_learning.md"],
    ),
    Eval(
        id="T2",
        prompt="I've got bandit task data and want to get a learning rate out of it. Where do I start?",
        category="triggering",
        skill_should_fire=True,
        expected_files=["reinforcement_learning.md"],
    ),
    Eval(
        id="T3",
        prompt="Help me debug my hBayesDM call — ra_prospect is throwing errors when I pass my data.",
        category="triggering",
        skill_should_fire=True,
        expected_files=["prospect_theory.md"],
    ),
    Eval(
        id="T4",
        prompt="My HDDM fit gave a drift rate of -0.05 for the hard condition and +0.02 for the easy one. The signs look right but the magnitudes feel small. Should I worry?",
        category="triggering",
        skill_should_fire=True,
        expected_files=["drift_diffusion.md"],
    ),
    Eval(
        id="T5",
        prompt="I have ΔWAIC = 8 in favor of my dual-α model over single-α. Is that reliable?",
        category="triggering",
        skill_should_fire=True,
        expected_files=["model_comparison.md"],
        rubric_keywords=["standard error", "SE", "se_diff", "uncertainty"],
        notes="Should ask for the SE of the difference, not just yes/no.",
    ),
    Eval(
        id="T6",
        prompt="I want to predict customer churn from behavioral logs using gradient boosting — what features should I engineer?",
        category="triggering",
        skill_should_fire=False,
        notes="Negative control. This is predictive ML, not cognitive modeling.",
    ),
    Eval(
        id="T7",
        prompt="Compare mean accuracy between my two patient groups — what test should I use?",
        category="triggering",
        skill_should_fire=False,
        notes="Negative control. Descriptive stats, not modeling.",
    ),
    Eval(
        id="T8",
        prompt="I'm running a CFA on my questionnaire data with three latent factors. How do I check fit?",
        category="triggering",
        skill_should_fire=False,
        notes="Negative control. SEM is a different methodology family.",
    ),
    Eval(
        id="T9",
        prompt="I have RT data from a Stroop task and want to compare conditions.",
        category="triggering",
        skill_should_fire=False,  # ambiguous; acceptable to fire IF clarifies first
        notes="Edge case: should clarify whether user wants DDM decomp or just means.",
    ),
    Eval(
        id="T10",
        prompt="I want to compare Q-learning, model-based RL, and a hybrid, on my two-step task data. What's the right workflow?",
        category="triggering",
        skill_should_fire=True,
        expected_files=["reinforcement_learning.md", "model_comparison.md", "recovery.md"],
    ),

    # ------- Routing -------
    Eval(
        id="R1",
        prompt="Walk me through the math of the Rescorla-Wagner update rule.",
        category="routing",
        expected_files=["reinforcement_learning.md"],
        rubric_must_not_have=["drift_diffusion", "category_learning"],
    ),
    Eval(
        id="R2",
        prompt="How do I estimate loss aversion from Sokol-Hessner-style gambles?",
        category="routing",
        expected_files=["prospect_theory.md"],
    ),
    Eval(
        id="R3",
        prompt="My DDM fit gives the correct mean RT but the slow-error pattern is wrong.",
        category="routing",
        expected_files=["drift_diffusion.md"],
        rubric_keywords=["sv", "drift variability", "inter-trial variability"],
        notes="Should specifically mention sv (inter-trial drift variability).",
    ),
    Eval(
        id="R4",
        prompt="I'm comparing GCM and prototype models on a family resemblance task. What stimuli should I use?",
        category="routing",
        expected_files=["category_learning.md"],
        rubric_keywords=["Medin-Schaffer", "5/4", "family resemblance"],
    ),
    Eval(
        id="R5",
        prompt="I have Kirby MCQ data. Should I use the traditional k-scoring or fit the hyperbolic model?",
        category="routing",
        expected_files=["delay_discounting.md"],
    ),
    Eval(
        id="R6",
        prompt="Subjects show faster learning in the volatile block than the stable block. What model captures this?",
        category="routing",
        expected_files=["bayesian_learning.md"],
        rubric_keywords=["Behrens", "HGF", "Kalman", "adaptive"],
        rubric_must_have_all=["volatil"],
        notes="Should mention that fixed-α RW can't capture this by design.",
    ),
    Eval(
        id="R7",
        prompt="How do I know if my parameter estimates are trustworthy?",
        category="routing",
        expected_files=["recovery.md"],
        rubric_must_have_all=["recovery", "simulat"],
    ),
    Eval(
        id="R8",
        prompt="When should I use WAIC vs PSIS-LOO?",
        category="routing",
        expected_files=["model_comparison.md"],
    ),
    Eval(
        id="R9",
        prompt="My hierarchical RL Stan model is divergent.",
        category="routing",
        expected_files=["hierarchical_stan.md"],
        rubric_keywords=["non-centered", "reparameter"],
        notes="Should suggest non-centered parameterization first.",
    ),
    Eval(
        id="R10",
        prompt="I want to fit an RL-DDM to my instrumental learning data with RTs.",
        category="routing",
        expected_files=["reinforcement_learning.md", "drift_diffusion.md"],
    ),

    # ------- Content / workflow -------
    Eval(
        id="C1",
        prompt="I fit a 3-parameter RL model to 60 subjects and the group-mean learning rate is 0.34 (SE 0.04). Is that publishable?",
        category="content",
        rubric_keywords=["parameter recovery", "model comparison", "posterior predictive",
                         "PPC", "alternative model"],
        rubric_must_have_all=["recovery", "comparison"],
        rubric_must_not_have=["looks fine", "looks good", "looks great",
                              "solid learning rate", "reasonable learning rate",
                              "sounds good", "well-identified"],
        notes="Must require recovery + comparison before endorsing. 'publishable' removed from "
              "must_not_have because the prompt asks 'is it publishable?' and models naturally "
              "use the word even while requiring caveats. Check for uncritical validation instead.",
    ),
    Eval(
        id="C2",
        prompt="I have a bunch of subjects whose fitted learning rate is essentially 1.0 (at the upper bound), and inverse temperature β is all over the place. The model fit is okay on LOO.",
        category="content",
        rubric_keywords=["boundary", "trade-off", "tradeoff", "identifia", "non-identif"],
        rubric_must_have_all=["α", "β"],  # or 'alpha', 'beta' — accept either
        notes="Should recognize the α/β identification issue.",
    ),
    Eval(
        id="C3",
        prompt="I want to estimate loss aversion (λ) from a gain-only task with gambles like $10 vs sure $5.",
        category="content",
        rubric_keywords=["identifia", "not identif", "cannot estimate", "can't estimate",
                         "mixed gambles", "gain and loss"],
        rubric_must_not_have=["Here's some Stan code", "here is the model"],
        notes="Must flag that λ is unidentified from gain-only data.",
    ),
    Eval(
        id="C4",
        prompt="I'm using HDDM but my fitted boundary `a` is 1200 and `t` is 350. What's wrong?",
        category="content",
        rubric_keywords=["seconds", "milliseconds", "ms", "1000", "units"],
        notes="Should diagnose RT-in-ms-instead-of-seconds immediately.",
    ),
    Eval(
        id="C5",
        prompt="I want to use the model-based weight `w` from the two-step task as a between-subjects individual difference measure correlating with my clinical scores.",
        category="content",
        rubric_keywords=["reliability", "test-retest", "Brown", "Shahar", "Kool"],
        notes="Should flag poor test-retest reliability of w.",
    ),
    Eval(
        id="C6",
        prompt="My hierarchical Bayesian RL fit shows everyone's α basically equal to the group mean. I expected more individual variation.",
        category="content",
        rubric_keywords=["sigma", "group SD", "hyperprior", "shrinkage"],
        notes="Should diagnose over-shrinkage from tight group prior.",
    ),
    Eval(
        id="C7",
        prompt="Here's my CSV of bandit data. Please write Stan code and fit it for me.",
        category="content",
        rubric_keywords=["parameter recovery", "simulate", "PPC", "posterior predictive",
                         "baseline", "comparison"],
        notes="Should provide code but ALSO insist on recovery/PPC/baseline.",
    ),
    Eval(
        id="C8",
        prompt="Model A has the best WAIC by a wide margin (ΔWAIC = 50 vs B). I'm going with A.",
        category="content",
        rubric_keywords=["SE", "standard error", "se_diff", "posterior predictive",
                         "PPC", "model recovery", "confusion"],
        rubric_must_have_all=["model recovery", "posterior predictive"],
        rubric_must_not_have=["ship it", "go with A", "you're good to go",
                              "sounds good", "looks good"],
        notes="Should require PPC + model recovery before endorsing ΔWAIC. "
              "must_not_have checks only for flat unconditional endorsements; "
              "conditional 'if X then clear winner' is acceptable.",
    ),
    Eval(
        id="C9",
        prompt="I'm fitting GCM to my categorization data — c = 2.3, w = (0.7, 0.3). Reasonable?",
        category="content",
        rubric_keywords=["trade-off", "tradeoff", "MDS", "stimulus", "scaling", "recovery"],
        notes="Should mention c/w trade-off and stimulus representation issue.",
    ),
    Eval(
        id="C10",
        prompt="I want to show subjects' learning rates are higher in the volatile block than the stable block, so I'm fitting RW with separate α per block.",
        category="content",
        rubric_keywords=["normative", "Bayesian", "HGF", "Behrens", "Kalman", "descriptive"],
        notes="Should distinguish descriptive vs normative approaches.",
    ),
    Eval(
        id="C11",
        prompt="I have 30 trials per subject and want per-subject MLE estimates of α and β.",
        category="content",
        rubric_keywords=["boundary", "extreme", "MAP", "hierarchical", "shrinkage"],
        rubric_must_not_have=["here's the MLE code"],
        notes="Should warn against MLE on too few trials and recommend MAP/HB.",
    ),
    Eval(
        id="C12",
        prompt="I fit cumulative prospect theory to my gambles data and the parameters look great.",
        category="content",
        rubric_keywords=["expected utility", "EU", "baseline", "comparison", "PPC",
                         "posterior predictive"],
        notes="Should ask about EU baseline comparison.",
    ),
    Eval(
        id="C13",
        prompt="I have a perceptual decision task with 3 difficulty levels. Should I fit one drift rate or three?",
        category="content",
        rubric_keywords=["three", "per condition", "by condition", "depends_on", "regression"],
        notes="Answer is three (or via regression on difficulty).",
    ),
    Eval(
        id="C14",
        prompt="What's the best learning model for my data?",
        category="content",
        rubric_keywords=["?", "what task", "what is the task", "goal", "scientific question",
                         "parameter estimation", "model comparison", "regressor"],
        notes="Should ask clarifying questions before recommending.",
    ),
    Eval(
        id="C15",
        prompt=(
            "Here's my Stan output:\n"
            "       mean  se_mean   sd  2.5%  25%  50%  75%  97.5%  n_eff  Rhat\n"
            "alpha  0.34   0.01  0.08  0.18 0.28 0.34 0.40 0.51    156  1.04\n"
            "beta   3.21   0.05  0.41  2.44 2.93 3.20 3.49 4.03    220  1.03\n"
        ),
        category="content",
        rubric_keywords=["Rhat", "1.01", "convergence", "ESS", "n_eff", "more iter"],
        notes="Should engage with the actual diagnostics, not say 'looks great'.",
    ),

    # ------- Gap-fill evals (added post-review) -------

    Eval(
        id="C16",
        prompt=(
            "I want to fit a category learning model that uses discriminative reconstruction "
            "rather than exemplar similarity. What's the right model?"
        ),
        category="content",
        expected_files=["category_learning.md"],
        rubric_keywords=["DIVA", "Kurtz", "discriminat", "catlearn", "reconstruction"],
        notes="Should mention DIVA (Kurtz 2007) as the reconstruction-based alternative to GCM/SUSTAIN.",
    ),

    Eval(
        id="C17",
        prompt=(
            "I have a complex collapsing-bound accumulator model with no closed-form likelihood. "
            "How do I fit it to behavioral data?"
        ),
        category="content",
        expected_files=["hierarchical_stan.md"],
        rubric_keywords=["simulation-based", "sbi", "BayesFlow", "SBI", "intractable",
                         "amortized", "summary stat"],
        notes="Should recommend sbi or BayesFlow for models without tractable likelihoods.",
    ),

    # ------- New content evals (modeling traps not covered above) -------

    Eval(
        id="C18",
        prompt=(
            "My per-subject MLE gives α = 0.15 in condition A and α = −0.08 in condition B. "
            "The negative value in condition B suggests aversive or avoidance learning. Right?"
        ),
        category="content",
        expected_files=["reinforcement_learning.md"],
        rubric_keywords=["sign error", "bug", "reversed", "bounded", "constraint",
                         "unconstrained", "likelihood"],
        rubric_must_have_all=["bug"],
        rubric_must_not_have=["not necessarily", "could suggest opposite",
                              "could indicate aversive", "consistent with avoidance",
                              "might mean aversive"],
        notes="Negative α is a model/coding bug, not a psychological finding. "
              "Must say 'bug' explicitly. 'aversive/avoidance learning' removed from "
              "must_not_have — both correct and incorrect responses use these words in "
              "denial context. 'not necessarily' catches the base model's hedge instead.",
    ),

    Eval(
        id="C19",
        prompt=(
            "I have 50 subjects with 80 trials each. I'm going to pool all their trials "
            "into one 4000-trial sequence and fit a single (α, β) pair. "
            "More data means more stable estimates, right?"
        ),
        category="content",
        expected_files=["reinforcement_learning.md"],
        rubric_keywords=["individual", "hierarchical", "per-subject",
                         "pseudo-replication", "independence", "pooling",
                         "between-subject", "variability"],
        rubric_must_not_have=["good idea", "more stable", "that works",
                              "more data is better", "reasonable approach"],
        notes="Pooled fitting violates trial independence, erases individual differences, "
              "and produces uninterpretable parameters. Hierarchical Bayes is the fix.",
    ),

    Eval(
        id="C20",
        prompt=(
            "I'm fitting my RL model to block-level accuracy — I calculated the proportion "
            "correct in each 10-trial block, then fit the model to those 20 accuracy values. "
            "Is that okay?"
        ),
        category="content",
        expected_files=["reinforcement_learning.md"],
        rubric_keywords=["trial-level", "trial-by-trial", "likelihood",
                         "aggregat", "information", "RPE", "prediction error"],
        rubric_must_not_have=["that's fine", "that works", "valid approach",
                              "reasonable", "one approach"],
        notes="Block-level fitting discards the trial-by-trial likelihood and RPE sequence. "
              "Parameters cannot be interpreted. Must fit to the full trial sequence.",
    ),

    # ------- Further iteration evals (DDM v/z bias, β scale, ε-greedy) -------

    Eval(
        id="C21",
        prompt=(
            "I have a cued response-bias task — a cue makes one response option more likely "
            "correct. My HDDM fit shows drift rate v shifts toward the cued option. "
            "I'm concluding that the cue influences evidence accumulation — subjects are "
            "interpreting the cue as evidence. Is that justified?"
        ),
        category="content",
        expected_files=["drift_diffusion.md"],
        rubric_keywords=["starting point", "z", "starting-point", "response bias",
                         "both models", "compare", "both variants", "z-bias",
                         "prior", "alternative"],
        rubric_must_have_all=["z"],
        rubric_must_not_have=["yes, that's justified", "that's right",
                              "supports evidence accumulation interpretation",
                              "confirms evidence accumulation"],
        notes="v-shift and z-shift both produce response-option asymmetry. Must flag starting "
              "point z as an alternative and recommend fitting and comparing both model variants. "
              "Must say 'z' explicitly.",
    ),

    Eval(
        id="C22",
        prompt=(
            "I fitted an RL model to a bandit task with 0/1 rewards and got β = 5.2. "
            "My colleague ran the same paradigm with 0–100 point rewards and got β = 0.04. "
            "She's concluding her subjects are less exploitative than mine. Is that a valid "
            "comparison?"
        ),
        category="content",
        expected_files=["reinforcement_learning.md"],
        rubric_keywords=["scale", "reward magnitude", "rescal", "normalize",
                         "not comparable", "reward scale", "100×", "100x",
                         "magnitude", "units"],
        rubric_must_not_have=["her comparison is valid", "she's right",
                              "yes, that's a valid comparison",
                              "that comparison holds", "valid cross-study"],
        notes="β is not comparable across reward scales. β × reward_magnitude determines "
              "exploitativeness; β = 5.2 on {0,1} ≈ β = 0.052 on {0,100}. Must flag "
              "the comparison as invalid without normalization.",
    ),

    Eval(
        id="C23",
        prompt=(
            "My ML collaborator recommends ε-greedy for modeling exploration in my bandit task. "
            "Should I use it instead of softmax for fitting behavioral data?"
        ),
        category="content",
        expected_files=["reinforcement_learning.md"],
        rubric_keywords=["degenerate", "likelihood", "gradient", "smooth",
                         "differentiable", "uniform", "softmax", "non-differentiable",
                         "equal probability", "non-greedy"],
        rubric_must_have_all=["likelihood"],
        rubric_must_not_have=["yes, use ε-greedy", "either works equally",
                              "same result", "interchangeable",
                              "no meaningful difference", "both are fine"],
        notes="ε-greedy assigns equal probability to all non-greedy choices — the likelihood "
              "is degenerate (no gradient for which non-greedy option was chosen). Softmax "
              "provides a smooth, differentiable likelihood. Skill should name the likelihood "
              "issue and recommend softmax for behavioral fitting.",
    ),

    Eval(
        id="R11",
        prompt=(
            "What's the difference between GCM, ALCOVE, SUSTAIN, and DIVA for category learning?"
        ),
        category="routing",
        expected_files=["category_learning.md"],
        rubric_keywords=["DIVA", "Kurtz", "discriminat", "reconstruction", "catlearn"],
        notes="Should route to category_learning.md and cover all four models including DIVA.",
    ),

    Eval(
        id="R12",
        prompt=(
            "My accumulator model doesn't have a closed-form likelihood — it requires "
            "simulation. What's the modern fitting approach?"
        ),
        category="routing",
        expected_files=["hierarchical_stan.md"],
        rubric_keywords=["sbi", "BayesFlow", "simulation-based inference", "SBI"],
        notes="Should route to hierarchical_stan.md and name SBI toolboxes.",
    ),
]


def score_response(eval_obj: Eval, response_text: str,
                   files_read: list[str] | None = None) -> dict:
    """Apply rubric to a response.

    Returns a dict with 'pass' bool and 'notes' list. files_read may be None
    if the harness can't observe which files were read.
    """
    text_lower = response_text.lower()
    notes = []
    passing = True

    # Check files-read expectations (routing evals)
    if files_read is not None and eval_obj.expected_files:
        missing = [f for f in eval_obj.expected_files
                   if not any(f in r for r in files_read)]
        if missing:
            passing = False
            notes.append(f"missing expected files: {missing}")

    # OR-semantics keyword check
    if eval_obj.rubric_keywords:
        hits = [kw for kw in eval_obj.rubric_keywords
                if kw.lower() in text_lower]
        if not hits:
            passing = False
            notes.append(f"no rubric keywords matched (any of: {eval_obj.rubric_keywords})")
        else:
            notes.append(f"matched: {hits}")

    # AND-semantics required substrings
    if eval_obj.rubric_must_have_all:
        missing = [k for k in eval_obj.rubric_must_have_all
                   if k.lower() not in text_lower]
        if missing:
            passing = False
            notes.append(f"missing required substrings: {missing}")

    # Negative check
    if eval_obj.rubric_must_not_have:
        bad = [k for k in eval_obj.rubric_must_not_have
               if k.lower() in text_lower]
        if bad:
            passing = False
            notes.append(f"contains forbidden substrings: {bad}")

    return {"pass": passing, "notes": notes, "eval_id": eval_obj.id,
            "category": eval_obj.category}


if __name__ == "__main__":
    # Print a summary of the eval set
    from collections import Counter
    by_cat = Counter(e.category for e in EVALS)
    print(f"Total evals: {len(EVALS)}")
    for cat, n in sorted(by_cat.items()):
        print(f"  {cat}: {n}")
    print()
    print("Evals with negative skill-firing expectation (negative controls):")
    for e in EVALS:
        if not e.skill_should_fire:
            print(f"  {e.id}: {e.prompt[:70]}...")
