"""
Eval harness for the idiographic-quant skill.

8 prompts across 6 categories:
  pushback    (2) — model must refuse/redirect bad plans
  ergodicity  (1) — applying group findings to individuals
  causal      (1) — single-case experimental design
  scope       (1) — nomothetic guard (must NOT over-apply)
  pooled      (1) — pooled person-specific recommendation
  method      (1) — P-technique factor analysis
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
        rubric_must_have_all=["nonergodic", "sign reversal"],
        rubric_keywords=[
            "check_ergodicity", "check_ergodicity.py",
            "non-ergodic", "nonergodic", "not ergodic",
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
