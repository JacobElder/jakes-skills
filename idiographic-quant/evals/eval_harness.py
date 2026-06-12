"""
Eval harness for the idiographic-quant skill.

17 prompts across 7 categories:
  pushback    (5) — model must refuse/redirect bad plans
  ergodicity  (1) — applying group findings to individuals
  causal      (3) — single-case experimental design
  scope       (1) — nomothetic guard (must NOT over-apply)
  pooled      (1) — pooled person-specific recommendation
  method      (5) — method selection (P-technique, DSEM, DFA, ctsem)
  script      (1) — use bundled check_ergodicity.py
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Eval:
    id: str
    prompt: str
    category: str
    rubric_keywords: list[str] = field(default_factory=list)
    rubric_must_have_all: list[str] = field(default_factory=list)
    rubric_must_not_have: list[str] = field(default_factory=list)
    notes: str = ""
    files: list[str] = field(default_factory=list)


EVALS: list[Eval] = [

    # ── 0: underpowered network pushback ─────────────────────────────────────
    Eval(
        id="E0",
        prompt=(
            "I ran an EMA study on one client over two weeks (4 beeps a day, ~56 "
            "observations). I measured 8 things: anxiety, sadness, anger, fatigue, "
            "rumination, urge to avoid, social contact, sleep quality. I want a lagged "
            "network showing what predicts what for this person so I can pick an "
            "intervention target. Walk me through it in R?"
        ),
        category="pushback",
        rubric_must_have_all=["graphicalvar"],
        rubric_keywords=[
            "too few", "not enough", "underpowered", "insufficient",
            "56", "parameters", "quadratic", "scale", "node",
            "reduce", "fewer nodes", "alternative", "contemporaneous",
            "unstable", "unreliable", "stability",
            "beepvar", "dayvar", "day boundaries",
        ],
        rubric_must_not_have=[
            "here's how to run graphicalvar",
            "let's proceed with the 8-node",
            "the 56 observations should be",
        ],
        notes=(
            "Must flag ~56 occasions as insufficient for an 8-node lag-1 network. "
            "Must push back and offer alternatives. Must mention graphicalVAR "
            "and beepvar/dayvar. Must caution about stability before picking targets."
        ),
    ),

    # ── 1: ergodicity trap ────────────────────────────────────────────────────
    Eval(
        id="E1",
        prompt=(
            "We have a validated regression from a big cross-sectional study: across "
            "~5000 people, sleep quality and screen time predict next-day mood. My PI "
            "wants to use the coefficients to tell an individual coaching client how "
            "much to cut screen time to improve THEIR mood. Seems reasonable since the "
            "model is well-powered. Is this fine?"
        ),
        category="ergodicity",
        rubric_must_have_all=["ergodic"],
        rubric_keywords=[
            "ergodicity", "ergodic",
            "homogeneity", "stationarity", "homogeneous", "stationary",
            "opposite sign", "reverse", "differ", "different direction",
            "within-person", "person-specific",
            "fisher", "measure",
        ],
        rubric_must_not_have=[
            "is fine", "is reasonable", "seems reasonable",
            "you can use the coefficients",
            "the model is well-powered so",
        ],
        notes=(
            "Must identify the ergodicity trap (group model does not describe "
            "individuals). Must explain homogeneity + stationarity requirements. "
            "Must note individual relationship can reverse sign. "
            "Must NOT endorse using the group coefficients."
        ),
    ),

    # ── 2: single-case causal design ─────────────────────────────────────────
    Eval(
        id="E2",
        prompt=(
            "I'm a UX researcher. I want to know whether a new focus-mode feature "
            "reduces one power user's task-switching during deep work. I can turn it "
            "on/off and I log switches per session. It's really about whether it works "
            "for this specific high-value user, not a big sample. How should I design "
            "and analyze this rigorously?"
        ),
        category="causal",
        rubric_must_have_all=["randomization"],
        rubric_keywords=[
            "abab", "withdrawal", "single-case", "single case",
            "reversibl", "phase",
            "randomization test", "randomisation test",
            "visual analysis", "single-case effect", "tau-u", "tau_u", "pem", "nonoverlap",
            "scribe", "replicat",
        ],
        rubric_must_not_have=[
            "t-test is appropriate", "run a paired t-test",
            "use anova", "just compare means",
        ],
        notes=(
            "Must frame as single-case experimental (ABAB/withdrawal for reversible effect). "
            "Must recommend randomization test + visual analysis. "
            "Must warn against ordinary t-test on autocorrelated session data. "
            "Generalizability note (replication) or SCRIBE is a bonus."
        ),
    ),

    # ── 3: nomothetic-is-correct guard ───────────────────────────────────────
    Eval(
        id="E3",
        prompt=(
            "I keep reading that group averages don't apply to individuals and that I "
            "should do person-specific analysis. But my situation: I'm running an A/B "
            "test on our checkout flow, ~50,000 users, each user sees exactly one "
            "version, and I just need to know which version converts better so we can "
            "ship one to everyone. Should I be doing idiographic / within-person "
            "modeling here instead of just comparing the two groups?"
        ),
        category="scope",
        rubric_must_have_all=["nomothetic"],
        rubric_keywords=[
            "nomothetic", "population", "between-group", "between group",
            "a/b test", "ab test", "two-proportion", "chi-square", "chi square",
            "logistic regression", "z-test", "standard",
            "one observation", "single measurement", "no within-person",
            "does not apply", "not idiographic",
        ],
        rubric_must_not_have=[
            "you should use idiographic",
            "i recommend person-specific",
            "consider within-person modeling",
            "idiographic analysis would be better",
        ],
        notes=(
            "Must call this NOMOTHETIC — one obs per user, population-level decision. "
            "Must recommend standard A/B test / proportion test / logistic regression. "
            "Must NOT push idiographic / within-person methods onto this question."
        ),
    ),

    # ── 4: pooled person-specific (mlVAR/GIMME/DSEM) ─────────────────────────
    Eval(
        id="E4",
        prompt=(
            "I've got ESM data from 120 people, ~70 beeps each, measuring stress, "
            "sleepiness, and craving in a smoking-cessation study. I want the "
            "stress-to-craving dynamic. My advisor wants one model for the whole "
            "sample; I think everyone is different. Is there a way to get both the "
            "general pattern AND each person's own dynamics without running 120 "
            "separate models?"
        ),
        category="pooled",
        rubric_must_have_all=["mlvar"],
        rubric_keywords=[
            "mlvar", "gimme", "dsem",
            "shrinkage", "partial pooling", "multilevel", "borrows strength",
            "person-specific", "individual-level", "both levels",
            "group", "general pattern",
        ],
        rubric_must_not_have=[
            "run 120 separate graphicalvar",
            "fit one pooled model ignoring individual differences",
        ],
        notes=(
            "Must recommend mlVAR (primary), GIMME, or DSEM. "
            "Must explain partial pooling / shrinkage advantage. "
            "Must make clear both group-level AND person-specific estimates are available."
        ),
    ),

    # ── 5: P-technique factor analysis ───────────────────────────────────────
    Eval(
        id="E5",
        prompt=(
            "I have one participant who completed a 20-item Big Five short form once "
            "a day for 90 days. I want to find out whether the standard five-factor "
            "structure actually describes how HER traits hang together day to day, or "
            "whether her personality is organized differently. What analysis answers that?"
        ),
        category="method",
        rubric_must_have_all=["p-technique"],
        rubric_keywords=[
            "p-technique", "p technique",
            "occasion", "across occasions", "transpose",
            "five-factor", "big five", "nomothetic",
            "90 occasions", "small", "unreliable", "stable",
            "autocorrelat", "temporal", "dynamic factor", "lagged",
        ],
        notes=(
            "Must name P-technique factor analysis. "
            "Must explain the core idea (occasions take the role of persons). "
            "Must connect to nomothetic five-factor structure. "
            "Must flag ~90 occasions as small and note autocorrelation issue."
        ),
    ),

    # ── 6: use bundled ergodicity script ─────────────────────────────────────
    Eval(
        id="E6",
        prompt=(
            "I've attached intensive longitudinal data (sample_esm_nonergodic.csv) "
            "— 35 people, 55 daily observations each, with 'activity' and 'mood'. "
            "A reviewer is demanding evidence about whether it's even defensible to "
            "fit one pooled model to everyone, or whether I need person-specific models. "
            "Can you check this for me and tell me what the data says?"
        ),
        category="script",
        rubric_must_have_all=["ergodic", "sign disagree"],
        rubric_keywords=[
            "check_ergodicity", "check_ergodicity.py",
            "non-ergodic", "nonergodic", "not ergodic", "ergodicity",
            "opposite sign", "sign reversal", "sign disagreement",
            "simpson", "reversal",
            "positive", "negative",
            "person-specific", "idiographic", "pooled person",
            "descriptive", "screen", "not a formal test",
        ],
        notes=(
            "Must report non-ergodic verdict (nonergodic / not ergodic). "
            "Must identify sign reversal: between-person positive, within-person negative. "
            "Ideally uses check_ergodicity.py; acceptable to analyze CSV directly if "
            "conclusions and key findings are correct. "
            "Must recommend person-specific / pooled person-specific modeling."
        ),
        files=["sample_esm_nonergodic.csv"],
    ),

    # ── 8: stationarity vs theory tension ────────────────────────────────────
    Eval(
        id="E8",
        prompt=(
            "I'm studying one patient's mood recovery over 90 days of therapy using "
            "graphicalVAR. Mood clearly trends upward — that IS the phenomenon I care "
            "about (the therapy working). My stats consultant says I have to detrend "
            "before fitting VAR. But if I detrend, I'm removing the very effect I want "
            "to study. Are they right? Should I really detrend and lose the trend?"
        ),
        category="pushback",
        rubric_must_have_all=["stationarity"],
        rubric_keywords=[
            "tension", "theory", "stationarity", "stationary",
            "detrend", "remove", "residual",
            "dsem", "time-varying", "tv-var",
            "trend", "recovery", "drift",
            "model the trend", "nonstationarity", "nonstationary",
        ],
        rubric_must_not_have=[
            "just proceed without detrending",
            "your consultant is wrong",
            "the trend doesn't matter for var",
        ],
        notes=(
            "Must acknowledge the stationarity–theory tension explicitly. "
            "SKILL.md notes: 'stationarity is often in direct tension with the theory.' "
            "Good answer explains: detrended residuals answer a different question "
            "(co-fluctuations around trend); the trend is a separate phenomenon; "
            "DSEM or time-varying VAR can model both simultaneously. "
            "Must not simply say 'just detrend and proceed' OR 'skip detrending.'"
        ),
    ),

    # ── 9: cross-night lag / beepvar trap ─────────────────────────────────────
    Eval(
        id="E9",
        prompt=(
            "I'm setting up graphicalVAR on 5 beeps/day EMA data for 60 days. "
            "I'm treating every consecutive pair as a lag-1 transition, including "
            "the last beep at ~10pm paired with the first beep the next morning at ~8am. "
            "My colleague says I should use beepvar and dayvar to exclude these "
            "cross-night pairs. But isn't lag-1 just lag-1? Why does spanning midnight "
            "matter?"
        ),
        category="pushback",
        rubric_must_have_all=["beepvar"],
        rubric_keywords=[
            "beepvar", "dayvar", "day boundaries",
            "overnight", "sleep", "cross-day", "cross-night",
            "interval", "gap", "unequal",
            "different process", "10 hours", "hours apart",
            "contaminate", "confound",
        ],
        rubric_must_not_have=[
            "lag-1 is lag-1", "doesn't matter",
            "overnight pairs are fine",
            "your colleague is wrong",
        ],
        notes=(
            "Must explain why cross-night lags are problematic: overnight gap is "
            "~10h vs ~2-3h within day; spans sleep (a different process); produces "
            "a different 'lag-1' construct than daytime transitions; can create "
            "artificial overnight associations. beepvar/dayvar in graphicalVAR "
            "is the standard fix to exclude cross-day transitions."
        ),
    ),

    # ── 10: Nickell/Lüdtke bias from person-mean centering ───────────────────
    Eval(
        id="E10",
        prompt=(
            "I have 20 EMA observations per person in my study. I person-mean-centered "
            "all variables by subtracting each person's observed mean. My advisor says "
            "this introduces 'Nickell bias' or 'Lüdtke bias' in my autoregressive "
            "estimates. What does that mean and how serious is it?"
        ),
        category="pushback",
        rubric_must_have_all=["bias"],
        rubric_keywords=[
            "nickell", "lüdtke", "ludtke",
            "observed mean", "unreliable", "estimation error",
            "autoregressive", "attenuated", "attenuation",
            "dsem", "latent mean", "latent-variable",
            "20 occasions", "few occasions", "small t",
        ],
        rubric_must_not_have=[
            "person-mean centering is fine at n=20",
            "20 observations is sufficient",
            "the bias is negligible",
        ],
        notes=(
            "Must explain Nickell/Lüdtke bias: observed person mean is an unreliable "
            "estimate of the true latent mean; centering on a noisy mean introduces "
            "correlated measurement error into centered scores; this biases "
            "autoregressive (lag-1) estimates, typically toward zero (attenuation). "
            "Fix: more T, or DSEM which uses latent-variable mean centering."
        ),
    ),

    # ── 11: N-of-1 trial design ───────────────────────────────────────────────
    Eval(
        id="E11",
        prompt=(
            "I want to test whether melatonin actually improves MY sleep quality. "
            "I sleep poorly and have tried it a few times, but I want to do this "
            "rigorously — a real N-of-1 trial. What's involved in setting that up "
            "and analyzing it properly?"
        ),
        category="causal",
        rubric_must_have_all=["washout"],
        rubric_keywords=[
            "n-of-1", "n of 1", "crossover", "randomized crossover",
            "washout", "carryover",
            "blinding", "placebo", "allocation",
            "randomization test", "mixed model", "repeated",
            "cent", "reporting",
        ],
        notes=(
            "Must recognize this as an N-of-1 trial question. "
            "Must address: randomized crossover design, washout periods to handle "
            "carryover effects, blinding if possible, and appropriate analysis "
            "(randomization tests or mixed models). Mention of CENT reporting is a bonus."
        ),
    ),

    # ── 12: ESM protocol design before data collection ────────────────────────
    Eval(
        id="E12",
        prompt=(
            "I'm designing an ESM study to track one patient's anxiety, avoidance, "
            "and sleep over 4 weeks. I'm thinking 3 beeps a day, fixed times "
            "(9am/1pm/8pm). Before I launch, what are the most important design "
            "decisions I need to get right to end up with data I can actually analyze?"
        ),
        category="method",
        rubric_must_have_all=["compliance"],
        rubric_keywords=[
            "beeps per day", "sampling", "timescale", "process",
            "fixed", "random", "semi-random",
            "personalized", "common item",
            "reactivity", "burden", "fatigue",
            "compliance", "missingness",
            "stationarity", "baseline",
        ],
        notes=(
            "Must engage with protocol design decisions, not just analysis. "
            "Must flag at least: (a) 3 beeps/day may miss fast-turning dynamics, "
            "(b) fixed vs random timing tradeoffs (reactivity vs unequal spacing), "
            "(c) common vs personalized items, (d) compliance/burden. "
            "Should note these are baked in before data exists."
        ),
    ),

    # ── 7: centrality-as-treatment-target trap ────────────────────────────────
    Eval(
        id="E7",
        prompt=(
            "I estimated a symptom network from my dataset — 400 people, measured at "
            "a single timepoint — and 'fatigue' has the highest centrality (both "
            "strength and betweenness). So fatigue is the best treatment target to "
            "focus on for my patients, right? I want to write that up as the "
            "clinical implication."
        ),
        category="pushback",
        rubric_must_have_all=["centrality"],
        rubric_keywords=[
            "unstable", "instability", "unreliable",
            "bringmann", "poorly suited",
            "cross-sectional", "single timepoint", "single time point", "between-person",
            "ergodic", "individual",
            "causal", "hypothesis", "direction to test",
            "not a lever", "not causal", "experimental",
        ],
        rubric_must_not_have=[
            "fatigue is the best target",
            "fatigue is a good target",
            "you should target fatigue",
            "targeting fatigue makes sense",
            "write that up",
        ],
        notes=(
            "Must push back on centrality → treatment target. "
            "Must note centrality instability (esp. betweenness). "
            "Must flag cross-sectional network ≠ within-individual process. "
            "Must reframe as hypothesis. Must NOT endorse clinical write-up as stated."
        ),
    ),
    # ── 13: DSEM — advisor validates mlVAR on sum scores, user asks whether
    #             to just add a limitation note ─────────────────────────────────
    Eval(
        id="E13",
        prompt=(
            "I ran mlVAR on sum scores (6-item anxiety and 6-item depression, averaged) "
            "from 80 people with 100 daily observations each. My advisor reviewed the "
            "analysis and said it looks solid — the lagged paths are stable and the model "
            "converged cleanly. Someone at a conference mentioned DSEM, but my advisor "
            "said sum scores are standard and reviewers won't push back on it. Should I "
            "just add a short limitation note about measurement error and submit, or is "
            "DSEM a substantive improvement I actually need to make?"
        ),
        category="method",
        rubric_must_have_all=["dsem", "latent"],
        rubric_keywords=[
            "dsem", "dynamic structural equation",
            "latent", "measurement model", "measurement error",
            "latent centering", "latent mean",
            "lüdtke", "ludtke", "nickell",
            "bias", "attenuated", "attenuation",
            "two-level", "bayesian", "mplus",
        ],
        rubric_must_not_have=[
            "limitation note is sufficient",
            "adding a limitation is enough",
            "just add a limitation",
            "submit as is",
            "mlvar is fine for this",
        ],
        notes=(
            "Trap: advisor + reviewer-won't-notice framing. "
            "Must push back: DSEM is a substantive improvement, not cosmetic. "
            "Sum scores import measurement error into the VAR; observed person-mean "
            "centering introduces Lüdtke/Nickell bias in autoregressive estimates. "
            "DSEM's latent-variable approach fixes both. A limitation note is not enough."
        ),
    ),

    # ── 14: DFA — supervisor says non-significant autocorrelation test
    #             clears P-technique ────────────────────────────────────────────
    Eval(
        id="E14",
        prompt=(
            "I ran P-technique factor analysis on one participant's daily ratings of "
            "15 affect items over 120 days and found 3 factors. I ran a formal test for "
            "autocorrelation in the residuals and it came back non-significant (p = .09). "
            "My supervisor says this settles it — the data meets the independence "
            "assumption and I can proceed with P-technique as the final analysis. "
            "Does a non-significant autocorrelation test actually clear P-technique here?"
        ),
        category="method",
        rubric_must_have_all=["dynamic factor"],
        rubric_keywords=[
            "dynamic factor", "dfa",
            "autocorrelat", "serial dependence", "temporal dependence",
            "independence", "independent occasions",
            "underpowered", "power", "false negative",
            "biased", "violated", "assumption",
            "p-technique", "state-space", "openmx", "mplus",
        ],
        rubric_must_not_have=[
            "the test settles it",
            "non-significant means the assumption holds",
            "p-technique is cleared",
            "your supervisor is right",
            "p-technique is appropriate here",
        ],
        notes=(
            "Trap: authority (supervisor) + a non-significant statistical test presented "
            "as proof the assumption holds. "
            "Must push back: non-significant ≠ assumption met — with N=120 residual "
            "test is underpowered for modest autocorrelation; daily affect data almost "
            "always has autocorrelation; P-technique independence assumption is likely "
            "violated. Must recommend DFA (OpenMx/Mplus) or at minimum checking "
            "residual ACF plots rather than relying on a single p-value."
        ),
    ),

    # ── 15: multiple baseline — irreversible effect, ABAB withdrawal not possible ──
    Eval(
        id="E15",
        category="causal",
        prompt=(
            "I'm a school counselor doing a single-case study with one student. I want "
            "to teach her a cognitive restructuring skill to reduce catastrophizing. "
            "I'll measure catastrophizing daily. My supervisor suggested I use an ABAB "
            "design (teach the skill, withdraw it, re-introduce). But once a student "
            "learns cognitive restructuring, you can't really 'take it away' — the skill "
            "sticks. Is ABAB the right design here, or is there something better?"
        ),
        rubric_must_have_all=["multiple baseline"],
        rubric_keywords=[
            "multiple baseline", "multiple-baseline",
            "irreversible", "can't be withdrawn", "cannot be withdrawn",
            "skill", "learning", "carryover",
            "abab", "withdrawal", "reversal",
            "behavior", "setting", "replicate",
            "logic of replication", "staggered",
        ],
        rubric_must_not_have=[
            "abab is fine here",
            "abab is appropriate",
            "abab would work",
            "withdrawal design is suitable",
            "withdrawal is appropriate",
        ],
        notes=(
            "Must catch that ABAB/withdrawal requires the effect to be reversible. "
            "A learned cognitive skill persists — withdrawal is impossible. "
            "Must recommend multiple baseline design (across behaviors, settings, "
            "or a small set of students) as the correct alternative: stagger baseline "
            "lengths across units, introduce treatment at different times, show "
            "improvement tracks introduction rather than time alone. "
            "Must NOT endorse ABAB."
        ),
    ),

    # ── 16: ctsem / continuous-time — unequally-spaced ESM ───────────────────
    Eval(
        id="E16",
        category="method",
        prompt=(
            "I have ESM data from one participant: 200 beeps over 8 weeks, scheduled "
            "at random times (not fixed intervals) — sometimes 45 minutes apart, "
            "sometimes 4 hours. I want to model the lagged dynamics between anxiety "
            "and avoidance. My plan was to run graphicalVAR treating each consecutive "
            "pair of beeps as a lag-1 observation. Is that approach valid?"
        ),
        rubric_must_have_all=["continuous-time", "unequal"],
        rubric_keywords=[
            "continuous-time", "continuous time", "ctsem",
            "unequal", "unequally spaced", "irregular",
            "discrete-time", "discrete time",
            "interval", "spacing", "gap",
            "bias", "biased", "different lag",
            "tinterval", "dsem",
        ],
        rubric_must_not_have=[
            "graphicalvar is valid here",
            "treating consecutive beeps as lag-1 is fine",
            "the spacing doesn't matter",
            "unequal spacing is not a problem",
        ],
        notes=(
            "Must flag that discrete-time VAR (graphicalVAR) assumes equal spacing: "
            "a 45-minute lag-1 and a 4-hour lag-1 are not the same construct. "
            "Treating unequally-spaced beeps as equally-spaced biases the lagged estimates. "
            "Must recommend continuous-time models (ctsem, or DSEM with TINTERVAL) "
            "which estimate the underlying continuous process and derive effects for any interval. "
            "Must NOT endorse the graphicalVAR-as-planned approach."
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
            notes.append(f"matched keywords: {hits}")

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
