# Generative / LLM Agents in ABM (GABM)

A fast-moving development worth treating carefully: replacing hand-coded agent
rules with **large language models** that plan, reason, and interact in natural
language. The umbrella term is **Generative Agent-Based Modeling (GABM)** or
**LLM-ABM**, kicked off by Park et al. (2023), *Generative Agents: Interactive
Simulacra of Human Behavior*. By 2025 it is an active research area with its own
critical literature — and the consensus of that literature is cautionary.

This file exists so that when a user proposes "agents powered by GPT/Claude," you
can help them do it without abandoning the rigor the rest of this skill insists
on. The short version: **LLM agents change what the agent decision rule is, not
what makes a simulation trustworthy** — and they make several of ABM's hardest
problems worse, not better.

---

## What's appealing

- **Expressiveness.** Agents can exhibit rich, context-sensitive,
  natural-language behavior (bargaining, persuasion, coalition-forming, attitude
  change) that rule-based or RL agents struggle to produce.
- **Less hand-coding of micro-rules.** You describe roles and context in prose
  instead of formalizing every decision rule.
- **Synthetic subjects.** Scalable, privacy-preserving stand-ins for human
  participants in pilot studies and design evaluation.

Reported uses include synthetic societies, economic/market behavior, opinion
dynamics and echo chambers, epidemic-attitude spread, and crisis-response
simulation.

---

## Why it is dangerous — and what to do about each

The benefits are real for **exploratory and illustrative** work. The danger is
treating GABM output as evidence about the real world. The 2025 reviews
(Larooij & Törnberg 2025; "Validation is the central challenge for generative
social simulation," *AI Review* 2025; *IEEE TAI* 2025) converge on these:

1. **Reproducibility collapses.** LLM outputs are stochastic, and even at
   temperature 0 are not reliably deterministic across model versions, providers,
   or dates; vendors deprecate and silently update models. A result you can't
   regenerate isn't a scientific result. → **Pin the exact model name + version,
   decoding parameters (temperature, top-p), and the full prompts; record the
   date; archive transcripts. Treat the LLM and its settings as part of the model
   specification in your ODD** (see `odd-protocol.md`), not an implementation
   detail. Assume provider changes will eventually break replication and say so.

2. **Black-box squared.** A traditional ABM's emergence is already hard to trace
   to micro-rules; now the micro-rule *itself* is an opaque neural net with no
   inspectable mechanism. Attribution of a macro-outcome to a cause becomes
   close to impossible. → Keep a **rule-based ABM baseline** for any claim that
   matters; use the LLM version to generate hypotheses, not to confirm them.

3. **Data leakage / training contamination — the critical one.** What looks like
   *emergence* may be the LLM **reproducing a pattern it read in its training
   data** rather than generating it from agent interactions (Barrie & Törnberg
   2025). The model "knows" Schelling segregation, echo chambers, prisoner's
   dilemma results, and historical events, so it can recreate them without the
   mechanism you think you're testing. This **breaks the generative/sufficiency
   logic** that justifies ABM as explanation (see the sufficiency-vs-necessity
   guardrail in `SKILL.md` §3): you haven't shown your micro-rules *produce* the
   pattern; the model may simply be recalling it. → **Test for leakage:** does the
   pattern still appear when you withhold or scramble the supposed mechanism, use
   counterfactual/fictional setups the model can't have memorized, or anonymize
   the scenario? If the "finding" survives removing the mechanism, it was recall.

4. **Bias.** *Social bias* (stereotyped portrayals of groups) and *selection
   bias* (an unrepresentative training corpus) mean agents may reflect the
   internet's distribution of text, not your target population. → State the
   population you intend to represent and check the agents against it; don't
   assume "a persona prompt" yields a representative sample.

5. **Hallucination / no internal validity check.** LLMs are probabilistic
   next-token predictors with no built-in mechanism to verify their own outputs;
   agents can act on confidently false premises. → Constrain the action space;
   validate behavior at the agent level before trusting interactions (the
   agent/model/output hierarchy in `validation-and-calibration.md`).

6. **"Believability" is not validity.** Early GABM work often graded itself on
   how *believable* or *realistic* agents seemed, conflating generative
   sufficiency with operational validity and ignoring the decades-old simulation
   V&V literature (Larooij & Törnberg 2025). → Hold GABM to the **same**
   verification/calibration/validation standard as any ABM; believability is not
   evidence.

7. **Cost and scale.** An LLM call per agent per step is orders of magnitude more
   expensive than evaluating a rule, which sharply limits population size,
   replications, and parameter sweeps — exactly the things ABM rigor requires.

---

## Net assessment and when to use it

The honest summary from the current literature: **LLMs may exacerbate rather than
alleviate ABM's long-standing validation problem.** Validation is *the* central
challenge of GABM, not a footnote.

Reasonable uses today:
- **Exploration and hypothesis generation** — surfacing candidate mechanisms or
  behaviors to then formalize and test in a transparent, reproducible model.
- **Enriching a constrained action space** in a model that is otherwise
  rule-based and validated, where the LLM handles one well-bounded sub-decision.
- **Pilot/synthetic-subject studies** with explicit caveats and human validation
  before any real-world claim.

Treat with strong skepticism:
- Any claim that an LLM simulation *explains* or *predicts* a real social
  phenomenon, absent a leakage test, a rule-based baseline, and independent
  out-of-sample validation.

If a user is excited about GABM, match the enthusiasm with the checklist above —
the goal is to keep the expressive power while not letting it quietly void the
epistemics.

## Key references

- Park, J. S., et al. (2023). Generative Agents: Interactive Simulacra of Human
  Behavior. *UIST*.
- Larooij, M. & Törnberg, P. (2025). Do Large Language Models Solve the Problems
  of Agent-Based Modeling? A Critical Review of Generative Social Simulations.
  (arXiv:2504.03274; journal version in *Artificial Intelligence Review*, below.)
- Barrie, C. & Törnberg, P. (2025). Emergent LLM behaviors are observationally
  equivalent to data leakage. (arXiv:2505.23796.)
- *Validation is the central challenge for generative social simulation: a
  critical review of LLMs in agent-based modeling.* (2025). *Artificial
  Intelligence Review*.
- *Generative Agents in Agent-Based Modeling: Overview, Validation, and Emerging
  Challenges.* (2025). *IEEE Transactions on Artificial Intelligence*.
- *Large language models empowered agent-based modeling and simulation: a survey
  and perspectives.* (2024). *Humanities and Social Sciences Communications*.

(Confirm exact venues/pages before citing in a manuscript — this area is moving
quickly and preprints are common.)
