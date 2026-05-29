"""
Eval harness for the sequence-analysis-hmm skill.

25 evals across three categories:

  triggering (15) — explicit keyword triggers, implicit problem-description triggers,
                    and negative controls (skill should NOT redirect to HMMs).
                    These are run analytically; automated scoring validates content
                    quality when the skill is present.

  routing (3)     — which reference file should the answer draw on.
                    Analytical only (requires real skill install with file-read tools).

  content (10)    — correctness, response shape, wrong-tool pushback, code quality.
                    These run live against the API (baseline vs with-skill).

Automated scoring uses keyword matching. Formatting tests (prose vs headers) are
graded by rubric_must_not_have checks on known overformatting markers.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Eval:
    id: str
    prompt: str
    category: str            # "triggering" | "routing" | "content"
    expected_files: list[str] = field(default_factory=list)
    rubric_keywords: list[str] = field(default_factory=list)
    rubric_must_have_all: list[str] = field(default_factory=list)
    rubric_must_not_have: list[str] = field(default_factory=list)
    skill_should_fire: bool = True
    notes: str = ""


EVALS: list[Eval] = [

    # ── Triggering — explicit keyword ────────────────────────────────────────

    Eval(
        id="T1",
        prompt="What is Baum-Welch?",
        category="triggering",
        skill_should_fire=True,
        rubric_keywords=["em", "expectation", "e-step", "m-step", "forward-backward",
                         "parameter", "converge"],
        rubric_must_not_have=["## what is baum", "## baum-welch", "### key"],
        notes="Explicit keyword trigger. Response shape test: should be prose, not headers-and-bullets.",
    ),
    Eval(
        id="T2",
        prompt="How do I use hmmlearn to fit a model on time-series data?",
        category="triggering",
        skill_should_fire=True,
        expected_files=["timeseries.md"],
        rubric_must_have_all=["restart"],
        rubric_keywords=["GaussianHMM", "random_state", "seed", "multiple", "n_components"],
        notes="Explicit library trigger. Multi-restart is required — single-restart answer = fail.",
    ),
    Eval(
        id="T3",
        prompt="I need to search Pfam with HMMER — what's the command?",
        category="triggering",
        skill_should_fire=True,
        expected_files=["bioinformatics.md"],
        rubric_must_have_all=["hmmscan", "hmmbuild"],
        rubric_keywords=["pfam", "hmmpress", "e-value", "tblout", "hmmer"],
        notes="Explicit HMMER trigger. Should give actual commands, not just concept.",
    ),
    Eval(
        id="T4",
        prompt="What's the difference between an HMM and a CRF?",
        category="triggering",
        skill_should_fire=True,
        expected_files=["comparisons.md"],
        rubric_must_have_all=["generative", "discriminative"],
        rubric_keywords=["p(z|x)", "p(x,z)", "label", "features", "baum-welch",
                         "conditional", "sequence labeling"],
        notes="Explicit comparison trigger. Must frame around generative/discriminative distinction.",
    ),
    Eval(
        id="T5",
        prompt="My hmmlearn model has NaN means after a few EM iterations — what's going wrong?",
        category="triggering",
        skill_should_fire=True,
        rubric_must_have_all=["collapse"],
        rubric_keywords=["state collapse", "degenerate", "covariance", "singular",
                         "regulariz", "restart", "seed"],
        notes="Explicit hmmlearn trigger. Must name state collapse; should suggest regularization or restart.",
    ),

    # ── Triggering — implicit (problem description) ───────────────────────────

    Eval(
        id="T6",
        prompt=(
            "I have triaxial accelerometer data from a wrist sensor and I want to "
            "segment it into activities — walking, sitting, running. What approach do you recommend?"
        ),
        category="triggering",
        skill_should_fire=True,
        expected_files=["timeseries.md"],
        rubric_keywords=["hidden markov", "hmm", "regime", "state", "segment",
                         "latent", "hmmlearn"],
        notes="Implicit trigger: activity recognition from sensor data.",
    ),
    Eval(
        id="T7",
        prompt=(
            "My stock returns seem to switch between calm periods and volatile ones. "
            "I want a model that captures that switching structure."
        ),
        category="triggering",
        skill_should_fire=True,
        expected_files=["timeseries.md"],
        rubric_keywords=["hmm", "regime", "hamilton", "gaussian", "state", "switching"],
        notes="Implicit trigger: financial regime switching.",
    ),
    Eval(
        id="T8",
        prompt=(
            "I have 50 aligned protein sequences from a kinase family and I want to build "
            "a model that lets me search for new family members in a proteome."
        ),
        category="triggering",
        skill_should_fire=True,
        expected_files=["bioinformatics.md"],
        rubric_must_have_all=["hmmer", "hmmbuild"],
        rubric_keywords=["profile hmm", "pfam", "hmmsearch", "e-value", "msa"],
        notes="Implicit trigger: protein family modeling. Must recommend HMMER not hmmlearn.",
    ),
    Eval(
        id="T9",
        prompt=(
            "I'm recording EEG during sleep and want to automatically identify sleep "
            "stages from the signal. Is there a natural model for this?"
        ),
        category="triggering",
        skill_should_fire=True,
        expected_files=["timeseries.md"],
        rubric_keywords=["hmm", "hidden markov", "state", "regime", "stage", "latent"],
        notes="Implicit trigger: sleep staging from EEG.",
    ),
    Eval(
        id="T10",
        prompt=(
            "I have server request logs — sequences of request types per session — "
            "and I want to flag sessions that look anomalous compared to normal behavior."
        ),
        category="triggering",
        skill_should_fire=True,
        expected_files=["timeseries.md"],
        rubric_must_have_all=["likelihood"],
        rubric_keywords=["hmm", "hidden markov", "anomaly", "log-likelihood", "normal",
                         "score", "flag"],
        notes="Implicit trigger: anomaly detection via likelihood scoring.",
    ),
    Eval(
        id="T11",
        prompt=(
            "I'm working with DNA sequences and want a probabilistic model to identify "
            "CpG islands along a chromosome."
        ),
        category="triggering",
        skill_should_fire=True,
        expected_files=["bioinformatics.md"],
        rubric_must_have_all=["cpg"],
        rubric_keywords=["hmm", "hidden markov", "durbin", "state", "posterior", "decode"],
        notes="Implicit trigger: CpG island detection — the classic textbook bioinformatics example.",
    ),

    # ── Negative controls — should NOT redirect to HMMs ──────────────────────

    Eval(
        id="N1",
        prompt="I want to predict tomorrow's stock price using historical prices. What's the best model?",
        category="triggering",
        skill_should_fire=False,
        rubric_keywords=["lstm", "transformer", "arima", "neural", "gradient", "forecast"],
        rubric_must_not_have=["use an hmm instead", "hmm would be better than",
                               "switch to hmm", "hmm is better here"],
        notes=(
            "Negative control: pure price prediction. Model should help with forecasting "
            "without redirecting entirely to HMMs. May mention HMMs as a comparison, "
            "but should not replace the forecasting answer with regime detection."
        ),
    ),
    Eval(
        id="N2",
        prompt="I'm building a transformer for sentiment classification — how should I fine-tune it?",
        category="triggering",
        skill_should_fire=False,
        rubric_keywords=["transformer", "bert", "fine-tune", "fine-tuning", "huggingface",
                         "classification", "tokeniz"],
        rubric_must_not_have=["use an hmm instead", "hmm would be better",
                               "consider an hmm"],
        notes=(
            "Negative control: supervised NLP with a transformer. "
            "Skill should not redirect to HMMs."
        ),
    ),
    Eval(
        id="N3",
        prompt=(
            "I have 50,000 customer records and I want to segment them into groups. "
            "The records are not time-ordered — each is an independent snapshot."
        ),
        category="triggering",
        skill_should_fire=False,
        rubric_keywords=["kmeans", "k-means", "gmm", "mixture", "cluster",
                         "gaussian mixture", "dbscan", "unsupervised"],
        rubric_must_not_have=["use an hmm", "hidden markov model would", "hmm is appropriate here"],
        notes=(
            "Negative control: i.i.d. clustering. No sequence structure. "
            "GMM or k-means is correct; HMM is wrong."
        ),
    ),
    Eval(
        id="N4",
        prompt="How do I implement GARCH for volatility forecasting in Python?",
        category="triggering",
        skill_should_fire=False,
        rubric_must_have_all=["arch"],
        rubric_keywords=["garch", "arch", "arch(", "conditional variance", "volatility",
                         "arma", "ugarch"],
        rubric_must_not_have=["instead of garch, use an hmm", "hmm is a better choice than garch"],
        notes=(
            "Negative control: GARCH is a different model family. "
            "Should answer the GARCH question; may mention HMM regime-switching as a "
            "conceptual complement but should not replace the GARCH answer."
        ),
    ),

    # ── Routing (analytical — requires real file-read tools) ──────────────────

    Eval(
        id="R1",
        prompt="Explain how profile HMM construction works in HMMER — specifically the match/insert/delete state architecture.",
        category="routing",
        expected_files=["bioinformatics.md"],
        rubric_must_have_all=["match", "insert", "delete"],
        rubric_keywords=["plan 7", "hmmbuild", "alignment", "msa", "position-specific",
                         "column", "profile"],
        notes="Should route to bioinformatics.md and describe the Plan 7 architecture.",
    ),
    Eval(
        id="R2",
        prompt="Compare HMM and Kalman filter for modeling a process with continuous latent state.",
        category="routing",
        expected_files=["comparisons.md"],
        rubric_must_have_all=["continuous", "discrete"],
        rubric_keywords=["linear-gaussian", "kalman", "latent", "regime",
                         "switching state", "slds"],
        notes="Should route to comparisons.md. Must name the discrete/continuous distinction.",
    ),
    Eval(
        id="R3",
        prompt="What's the comparison between an HMM and a change-point detection method?",
        category="routing",
        expected_files=["comparisons.md"],
        rubric_must_have_all=["recur"],
        rubric_keywords=["ruptures", "change-point", "recurring", "one-off",
                         "structural break", "regime"],
        notes="Should route to comparisons.md. Key distinction: recurring states (HMM) vs one-off breaks (change-point).",
    ),

    # ── Content / workflow (run live, baseline vs with-skill) ─────────────────

    Eval(
        id="C1",
        prompt="What's an HMM?",
        category="content",
        rubric_keywords=["dice", "urn", "balls", "weather", "imagine", "rolling",
                         "friend", "hidden state", "latent", "observe", "metaphor"],
        rubric_must_not_have=["## what is", "### key", "**hidden states**",
                               "**observations**", "**transition prob",
                               "**key components", "powerful statistical tool",
                               "**speech recognition**", "**bioinformatics**"],
        notes=(
            "THE response-shape test. Must be a prose paragraph with a metaphor. "
            "Any of the must_not_have overformatting markers = fail. "
            "Headers or named subcomponent bullet lists = fail."
        ),
    ),
    Eval(
        id="C2",
        prompt=(
            "Here's my data: X = np.array([[0.2],[0.8],[0.1],[0.9],[0.15],[0.7]]). "
            "Fit an HMM to it."
        ),
        category="content",
        rubric_must_have_all=["restart"],
        rubric_keywords=["for seed", "range(", "random_state", "multiple", "n_components",
                         "GaussianHMM"],
        notes=(
            "Code quality test. Single-restart fit = fail. "
            "'restart' must appear somewhere in the response."
        ),
    ),
    Eval(
        id="C3",
        prompt="What's the difference between an HMM and a Kalman filter?",
        category="content",
        rubric_must_have_all=["continuous", "discrete"],
        rubric_keywords=["linear-gaussian", "kalman", "latent", "regime",
                         "continuous latent", "particle filter", "slds"],
        notes=(
            "Correctness test + mild shape test. Must distinguish discrete vs continuous "
            "latent state. May use some structure since it's a comparison question, "
            "but a bulleted pro/con list without the discrete/continuous framing = fail."
        ),
    ),
    Eval(
        id="C4",
        prompt=(
            "My fitted HMM keeps switching states every 1–2 timesteps even though I "
            "know the system stays in each state for at least 20 steps. What's wrong?"
        ),
        category="content",
        rubric_must_have_all=["geometric"],
        rubric_keywords=["hsmm", "semi-markov", "duration", "pomegranate", "dynamax",
                         "geometric distribution", "duration distribution"],
        notes=(
            "Pitfall #5 test. Must name the geometric duration assumption as the cause. "
            "Should recommend HSMM and name a library (pomegranate or dynamax)."
        ),
    ),
    Eval(
        id="C5",
        prompt="Explain how profile HMM construction works — the match/insert/delete state architecture.",
        category="content",
        expected_files=["bioinformatics.md"],
        rubric_must_have_all=["match", "insert", "delete"],
        rubric_keywords=["plan 7", "hmmbuild", "hmmer", "msa", "alignment",
                         "position-specific", "column", "profile"],
        notes="Domain deep-dive. Must describe M/I/D states. Should mention hmmbuild and Plan 7.",
    ),
    Eval(
        id="C6",
        prompt="Walk me through implementing the Viterbi algorithm from scratch in NumPy.",
        category="content",
        expected_files=["algorithms.md"],
        rubric_must_have_all=["log"],
        rubric_keywords=["log-space", "backpointer", "log_pi", "log_a", "argmax",
                         "underflow", "delta", "psi"],
        rubric_must_not_have=["naive", "without log"],
        notes=(
            "Code quality test. Must work in log-space. "
            "Naive probability-space implementation without log = fail on underflow grounds."
        ),
    ),
    Eval(
        id="C7",
        prompt="What are the main advantages of pomegranate over hmmlearn, and when should I switch?",
        category="content",
        rubric_must_have_all=["pytorch", "hsmm"],
        rubric_keywords=["emission", "gpu", "flexible", "api", "v1.0", "1.0",
                         "from_samples", "custom distribution", "semi-markov"],
        notes=(
            "Library knowledge test. Must name PyTorch backend and HSMM support as key differentiators. "
            "Old API warning (from_samples) is a bonus but not required."
        ),
    ),
    Eval(
        id="C8",
        prompt="Can I use an HMM to reliably predict stock prices and build a trading strategy?",
        category="content",
        rubric_must_have_all=["out-of-sample"],
        rubric_keywords=["not reliable", "regime", "realized", "volatility",
                         "manage expectations", "limited", "no", "doesn't",
                         "look-ahead", "backtest"],
        rubric_must_not_have=["reliable alpha", "yes, hmms can predict",
                               "can generate profits", "consistent returns",
                               "can reliably predict"],
        notes=(
            "Wrong-tool pushback. Must push back clearly. "
            "Must mention out-of-sample failure and name what HMMs CAN do in finance."
        ),
    ),
    Eval(
        id="C9",
        prompt=(
            "I have a labeled NER dataset with 10,000 annotated sentences. "
            "Should I use an HMM for sequence labeling?"
        ),
        category="content",
        rubric_must_have_all=["crf"],
        rubric_keywords=["conditional random field", "discriminative", "generative",
                         "neural", "labeled data", "transformer", "bert"],
        rubric_must_not_have=["yes, use an hmm", "hmm is a great choice here",
                               "hmm works well for this"],
        notes=(
            "Wrong-tool redirect. With labeled data and a discriminative task, "
            "CRF or neural is correct. Must name CRF explicitly."
        ),
    ),
    Eval(
        id="C10",
        prompt=(
            "I want to model customer journeys but each customer only has 3–5 events "
            "total. Is an HMM a good fit?"
        ),
        category="content",
        rubric_must_have_all=["transition"],
        rubric_keywords=["not enough", "too few", "insufficient", "hundreds",
                         "data", "short", "sparse", "markov chain"],
        rubric_must_not_have=["hmm is a great fit", "hmm works well here",
                               "good choice for this", "well suited"],
        notes=(
            "Data scarcity flag. Skill says 'hundreds of state-transitions per state.' "
            "3-5 events is far below that. Must raise the data concern before proceeding."
        ),
    ),
]


def score_response(eval_obj: Eval, response_text: str,
                   files_read: list[str] | None = None) -> dict:
    """Apply rubric to a response.

    Returns {'pass': bool, 'notes': list, 'eval_id': str, 'category': str}.
    files_read may be None if the harness cannot observe which files were opened.
    """
    text_lower = response_text.lower()
    notes = []
    passing = True

    # Files-read check (routing evals only; skipped when files_read is None)
    if files_read is not None and eval_obj.expected_files:
        missing = [f for f in eval_obj.expected_files
                   if not any(f in r for r in files_read)]
        if missing:
            passing = False
            notes.append(f"missing expected files: {missing}")

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
    print("Negative controls:")
    for e in EVALS:
        if not e.skill_should_fire:
            print(f"  {e.id}: {e.prompt[:80]}...")
