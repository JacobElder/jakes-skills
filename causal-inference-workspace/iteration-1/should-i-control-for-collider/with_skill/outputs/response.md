# Should You Control for "Got Hired at a Top-Tier Company"?

**Verdict: No. Do not include it. Doing so will introduce collider bias and corrupt your estimate.**

---

## Step 1: Name the Rung

Your question — "does years of experience causally affect salary?" — is a **Rung 2 (Intervention)** question. You want to know: if we could set someone's years of experience, how would that change their salary? That requires a causal estimate, not just an association. The follow-up question — "should I control for this variable?" — is a structural/DAG question, not a statistical one.

---

## Step 2: Sketch the DAG

Your dataset is a sample of people who got hired at tech companies. "Got hired" is not just a variable in your model — it is your **sample selection criterion**. You are not observing a random draw from the population of all people; you are observing only those who passed a hiring screen.

```
Experience (X) ──────────────────────────────────────→ Salary (Y)
        \                                                  /
         \                                                /
          └──────→ Got Hired (S) ←──────────────────────┘
                         ↑
                   (other factors: skills,
                    network, credentials, luck)
```

Key structural facts:
- **Experience → Salary**: the causal path you want to estimate.
- **Experience → Got Hired**: more experience improves hiring chances.
- **Salary (or salary potential) → Got Hired**: top-tier companies also select on expected productivity and pay potential.
- **Got Hired** is a **common effect** of Experience and Salary-related factors. That makes it a **collider**.
- You are already implicitly conditioning on Got Hired = 1 by restricting your sample to people who were hired. That conditioning is already in play.

---

## Step 3: Classify the Variable

Apply the per-variable taxonomy from the framework:

| Check | Answer |
|---|---|
| Is "Got Hired" a confounder (common cause of Experience and Salary)? | No. It is downstream of both. |
| Is it a mediator on Experience → Salary? | No. Hiring at a prior company doesn't mediate how experience accumulates into your current salary. |
| Is it a collider (common effect of Experience and salary-related factors)? | **Yes.** Both Experience and Salary potential causally influence who gets hired. |
| Is it a descendant of a collider? | Possibly — but it is itself the collider. |

**Structural role: Collider.**

**Verdict: Do not control for it.**

---

## Step 4: Why Controlling Creates Bias

From the collider rule: a collider node is a **closed path by default**. Conditioning on a collider **opens** the path, creating a spurious association between its causes.

Here is exactly what happens if you include "Got Hired at a Top-Tier Company" as a control:

You are conditioning on a selection outcome. Within the stratum "hired at top-tier companies," there is now a systematic negative correlation between experience and other hiring-relevant traits (skills, credentials, network). Why? Because among people who got hired, those with less experience must have compensated somehow (exceptional skills, elite credentials, strong networks). This induced correlation between experience and these other salary-relevant factors creates a **spurious back-door path** in your regression:

```
Experience (X) ←── [induced spurious correlation] ──→ Salary (Y)
```

This is sometimes called **Berkson's paradox** or **collider stratification bias**. It is the same mechanism as: "Among hospitalized patients, smoking appears protective against some diseases" — because hospitalization selects on sickness, and sick non-smokers got in some other way.

The practical effect: your estimated coefficient on experience will be **biased downward** (or in an unpredictable direction) because conditioning on the selection collider induces a negative correlation between experience and the unobserved salary-relevant traits.

---

## Step 5: The Deeper Problem — You Are Already Conditioning on It

Note that this bias isn't just about whether you include "Got Hired" as a regression covariate. The more fundamental issue is that **your entire dataset is conditioned on being hired**. The variable is already active as a sample restriction.

This means:
1. Your regression already has some collider bias baked in, regardless of what you control for.
2. Adding "Got Hired at a Top-Tier Company" as an explicit covariate compounds the problem by further stratifying within an already-selected sample.

To get an unbiased estimate of the experience → salary effect for the general population of tech workers, you would ideally need data on people who were **not** hired as well, or a different identification strategy.

---

## Step 6: What the Right Approach Looks Like

| Goal | Strategy |
|---|---|
| Estimate experience → salary for **the hired population** (ATT-like) | Acknowledge the selection, use the hired sample, but do NOT add more collider controls. Consider what confounders exist before hiring (e.g., education, field). |
| Estimate experience → salary for the **general workforce** | You need a broader sample or an identification strategy that accounts for selection (e.g., Heckman selection model, IV for hiring probability). |
| Block genuine confounders | Education, field of work, job type — these are pre-treatment common causes (forks). Control for those. |

Variables you **should** consider controlling for (confounders, not colliders):
- **Education level**: affects both years of experience (career start timing) and salary.
- **Job function/role**: affects both experience trajectory and pay.
- **Industry sub-sector**: a common cause of both career length and compensation.

---

## Key Trap Being Flagged

This is a textbook instance of two related traps from the framework:

1. **Collider conditioning**: "Got Hired" is a common effect of experience and salary potential. Conditioning on it opens a spurious path.
2. **Selection bias / collider stratification**: Your sample is already a selected population. Every estimate you produce is conditional on selection. Adding further conditioning on a downstream selection variable deepens the bias.

The instinct behind the question — "it correlates with both X and Y, so I should control for it" — is the exact reasoning the framework identifies as wrong. Correlation with X and Y is consistent with *every* structural role: confounder, mediator, collider, proxy. Only the DAG tells you which it is, and here the DAG is unambiguous.

---

**Bottom line**: Do not include "Got Hired at a Top-Tier Company" as a control variable. It is a collider (and simultaneously your sample selection criterion). Conditioning on it induces spurious correlation between experience and salary-relevant unobservables, biasing your estimate. Instead, focus on true pre-treatment confounders like education, role, and field.
