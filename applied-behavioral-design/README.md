# Applied Behavioral Design Skill

A skill that applies ideas42-style applied behavioral science to problems of the form "people aren't doing X." It does two things that the base model doesn't do reliably: (1) diagnose *why* a behavior isn't happening before designing anything, and (2) distinguish problems where behavioral tools are useful from problems where the real constraint is structural.

The skill has a strong point of view. Most behavior-change failures happen because practitioners skip straight to a solution — a reminder, an incentive, a gamification layer — before mapping why the behavior breaks down. The skill enforces diagnosis before design, declines to behavioralize structural constraints, treats bias names as hypotheses not diagnoses, generates interventions three ways rather than defaulting to motivation, and holds incentive skepticism under pressure. These positions are grounded in the ideas42 methodology and the skill holds them even when the user arrives with a solution already in hand.

## Installation

```bash
npx skills add https://github.com/JacobElder/jakes-skills/tree/main/applied-behavioral-design
```

Or manually:

```bash
cp -r jakes-skills/applied-behavioral-design ~/.claude/skills/applied-behavioral-design
```

Once installed, the skill applies automatically whenever someone frames a problem as "people aren't doing X" — low adoption, uptake, activation, enrollment, completion, no-shows, funnel drop-off — or asks to design a nudge, reduce friction, or change the behavior of users, employees, customers, patients, students, or citizens. It also fires when the user jumps straight to a solution ("we need gamification / an incentive / a reminder campaign"), because the entire discipline is to diagnose before designing.

---

## Example use cases

**"Leadership wants to add streaks and badges to drive activation on our dev tool. Can you help me design the gamification system?"**

The skill declines to design the gamification immediately. It restates "activation" as a concrete target behavior (developer runs the bot on a real task in week 1), proposes mapping the path to that action and forming barrier hypotheses before building anything, and frames gamification as one unvetted motivation-focused option — not the answer. Cheaper friction-reduction or default changes may outperform it.

---

**"Let's just pay people. I want to give users a $10 gift card every time they complete onboarding."**

The skill raises substantive concerns before designing the incentive: cash can crowd out intrinsic motivation, turn a moral action into a transaction, and collapse at scale. It proposes cheaper alternatives to test first (friction reduction, defaults, reminders). Then, even when recommending against incentives, it completes the response: if the team proceeds anyway, here's how to enhance them behaviorally (loss-framing, immediate salience, probabilistic rewards) and here's the backfire metric to watch.

---

**"Quick one — which cognitive bias explains why people don't finish our 6-step account setup?"**

The skill declines to crown a single bias. It states explicitly that there is no one-to-one mapping from psychology to bottleneck — multiple barriers plausibly co-occur — and that naming "present bias" without evidence is diagnosis theater. It offers three to four competing hypotheses (hassle/friction at a specific step, choice overload, identity threat, unclear value) and specifies what per-step drop-off data or observation would adjudicate between them.

---

**"We're ready to test the new simplified enrollment form against the old one. How do I calculate sample size?"**

The skill explicitly defers the math: "For sample size and power, use the experimental-design skill — those calculations need dedicated treatment." Its job is to frame *why* a counterfactual matters (randomization balances unobservable confounds; before/after is a fallback with named weaknesses), what to measure (outcome + mechanism), and how to interpret results — not to compute the numbers itself.

---

**"We run a rural clinic. Patients miss 45% of follow-ups. They live 2–3 hours away and can't afford the bus fare. We want to design nudges."**

The skill applies Gate 1 hard: transport cost and time cost are structural barriers that behavioral tools cannot address. It names this honestly, routes the structural part to whoever owns resources or policy (transport vouchers, mobile clinic, telehealth), and applies behavioral tools only to a genuine behavioral remainder — scheduling friction, confirmation, inertia — once the structural constraint is resolved.

---

## What it does

The base model knows behavioral concepts. The skill gives the agent the *discipline to apply the ideas42 workflow correctly when the standard helpful response is wrong*. The hard cases require the agent to:

- **Refuse to design a solution before diagnosing** — push back on "design the gamification," "write the incentive program," "build the reminder sequence" and back up to target behavior + barrier hypotheses first (Gate 2)
- **Sort behavioral from structural** — name when a constraint is actually about resources, access, or price, and decline to behavioralize it (Gate 1)
- **Generate competing hypotheses with evidence specs** — not "the bias is present bias" but "here are three plausible barriers, and here's what per-step data would adjudicate"
- **Generate interventions three ways** — lower/eliminate the barrier, go around it (change the path), or go over it (raise motivation); default to the cheaper "lower/around" options before motivation/incentive
- **Hold incentive skepticism and complete the answer** — raise crowding-out and scale concerns, propose alternatives, then still complete with behavioral enhancement guidance if incentives proceed
- **Route test mechanics explicitly** — name the experimental-design skill and refuse to fabricate sample sizes, rather than just including a caveat
- **Apply scarcity-population discipline** — strip process steps first for low-income/bandwidth-taxed populations, not reframing or messaging

Without the skill, the model tends to helpfully comply with whatever solution the user arrived with, name one bias as the explanation, and skip the diagnostic workflow entirely.

## Benchmark: skill vs. base model

Evaluated on 20 scenarios covering Gate 1/2 enforcement, target-behavior precision, decision-action mapping, bias-hypothesis generation, three-way intervention design, incentive skepticism, experimental-design handoff, ethics, scarcity populations, scale constraints, and full end-to-end quality. Each scenario is graded on 4–5 specific assertions about whether the model gave the correct, opinionated, diagnosis-first response.

```
Condition       Score        Pass rate
───────────────────────────────────────
Base model      56 / 83      67.5%
With skill      83 / 83      100.0%
Delta                        +32.5pp
```

20 evals, 83 assertions. The skill achieves 100% with-skill pass rate; the base model passes 10/20 evals (50%) and 56/83 assertions (67.5%).

The largest gains come from cases where the base model is "helpfully compliant":

| Eval | Topic | Base | Skill | Gap |
|------|-------|:----:|:-----:|:---:|
| premature-solutioning | refuses gamification, backs up to diagnosis | 0% | 100% | **+100pp** |
| incentive-skepticism | raises crowding-out + completes with enhancement | 0% | 100% | **+100pp** |
| single-bias-guard | generates competing hypotheses with evidence | 0% | 100% | **+100pp** |
| happy-path end-to-end | full IDEAS plan (prototype → RCT, mechanism, handoff) | 40% | 100% | **+60pp** |
| handoff to exp-design | routes AB test mechanics rather than computing them | 50% | 100% | **+50pp** |

The base model already handles: contextual (not dispositional) attribution, problem-as-outcome framing, re-diagnosing a proposed design for new barriers, scope-guarding pure statistics, ethics (declining dark patterns), and scale constraints. The skill's value concentrates on the diagnosis-before-design discipline, bias-as-hypothesis rigor, three-way intervention generation, and test-mechanics handoff.

## Eval suite

20 scenarios across 9 categories, graded by `claude-haiku-4-5` against explicit assertions (executor: `claude-sonnet-4-6`).

| # | Scenario | Category |
|---|----------|----------|
| 1 | Gamification requested before diagnosis | Gate 2 / premature solutioning |
| 2 | Target behavior stated as a driver ("understand the value") | Target behavior precision |
| 3 | Problem stated as solution ("they're not watching our videos") | Problem framing |
| 4 | Build a decision-action map for a FAFSA renewal problem | Decision-action mapping |
| 5 | Dispositional vs. contextual attribution for no-shows | Barrier diagnosis |
| 6 | "Which bias explains this?" for a 6-step account setup | Bias-as-hypothesis |
| 7 | Design interventions once a barrier is diagnosed | Three-way intervention |
| 8 | "Just pay people" — gift card incentive design | Incentive skepticism |
| 9 | Re-diagnose a caseworker call-intervention design | Re-diagnosis |
| 10 | AB test mechanics requested for simplified enrollment form | Handoff to experimental-design |
| 11 | "Fit a Cox model to my churn data" | Scope guard (not behavioral) |
| 12 | Design a friction-filled cancellation flow | Ethics |
| 13 | Benefits enrollment for scarcity-context population | Scarcity populations |
| 14 | Scale a specialist-intensive pilot to 1000 sites | Scale constraints |
| 15 | Food-pantry no-shows: behavioral vs. structural split | Gate 1 |
| 16 | Full end-to-end behavioral design brief | End-to-end quality |
| 17 | "Our nudge worked — 4% lift. Are we done?" | Mechanism confirmation |
| 18 | Rural clinic patients miss follow-ups (transport barrier) | Gate 1 hard |
| 19 | Incentive pilot worked; remove incentives now? | Post-incentive sustainability |
| 20 | Design mechanism measures for an RCT | Mechanism measurement upfront |

## License

MIT
