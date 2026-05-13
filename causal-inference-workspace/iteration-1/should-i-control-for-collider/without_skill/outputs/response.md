# Should You Control for "Got Hired at a Top-Tier Company"?

## The Short Answer

**No.** You should not include "got hired at a top-tier company" as a control variable. Doing so would introduce a serious bias known as **collider bias**, which would corrupt your estimate of the effect of experience on salary.

---

## Understanding the Causal Structure

To reason about whether to include a variable as a control, you need to think about the **causal graph** (a DAG) underlying your data.

The relevant variables are:

- **Experience (X):** Years of experience — your independent variable
- **Salary (Y):** Salary — your dependent variable
- **Ability/Skill (U):** Some unobserved factor like talent or domain expertise
- **Hired at Top-Tier Company (C):** The proposed control variable

The causal structure is:

```
Experience (X) ─────────────────────────────► Salary (Y)
      │                                              ▲
      ▼                                              │
Hired at Top-Tier Company (C) ◄─── Ability (U) ─────┘
```

- Experience increases the chance of being hired at a top-tier company.
- Ability also increases the chance of being hired at a top-tier company.
- Ability also increases salary.

This makes **"Got Hired at a Top-Tier Company" a collider** — a node with two or more causes flowing into it.

---

## What Is a Collider and Why Is Controlling for One Harmful?

A **collider** is a variable caused by two or more other variables. The key property:

> On its own, a collider **blocks** association between its causes. But **conditioning on** a collider **opens** a spurious path between those causes.

Experience and Ability may be mostly uncorrelated in the general population. But among people hired at top-tier companies, they become **negatively correlated**. Why? Because getting into a top-tier firm requires either lots of experience *or* high ability. If you observe a low-experience hire, you infer they must be highly able.

Conditioning on the collider creates a spurious backdoor path:

```
Experience ←─── (Collider Conditioning) ───► Ability ──► Salary
```

This biases your coefficient on experience — typically downward, since high ability (which predicts higher salary) is negatively associated with experience among top-tier hires.

---

## Concrete Illustration

| Person | Experience | Ability | Why Hired |
|--------|-----------|---------|-----------|
| A | High | Moderate | Experience got them in |
| B | Low | High | Ability got them in |

Within the conditioned group, experience and ability are negatively correlated. Your regression will wrongly attribute ability's salary premium to a negative experience effect, distorting your estimate.

---

## Your Dataset Is Already Selected

There's an additional issue: your dataset consists entirely of people hired at tech companies. This means you've **already conditioned on a selection event**. Your estimates will reflect "the effect of experience on salary among people hired at tech companies," not the full population. Be explicit about this scope limitation when reporting results.

---

## What Should You Do Instead?

**1. Leave the collider out.** Your core model is simply:

```
Salary = β₀ + β₁ × Experience + ε
```

**2. Control for actual backdoor confounders** — variables that cause both Experience and Salary without being colliders or mediators:
- Education level
- Industry / job function
- Geographic region
- Age (if distinct from experience)

**3. Use the backdoor criterion.** For causal identification, block all backdoor paths from Experience to Salary without conditioning on colliders or mediators. Tools like **DAGitty** (dagitty.net) help with this.

**4. Acknowledge sample selection** in your write-up and consider whether inverse probability weighting is warranted for population-level inference.

---

## Key Concepts Summary

| Variable Type | Definition | What to Do |
|--------------|-----------|-----------|
| Confounder | Causes both X and Y | Control for it |
| Mediator | On the causal path X → Y | Do NOT control (blocks the effect) |
| Collider | Caused by both X and another variable | Do NOT control (opens spurious paths) |
| Instrument | Causes X but not Y directly | Use in IV regression |

---

## Bottom Line

"Got hired at a top-tier company" is a **collider**. Controlling for it is one of the most common and consequential mistakes in applied regression — it does not reduce bias, it **introduces** it by creating a spurious correlation between experience and unobserved ability. Leave it out and focus on blocking genuine backdoor confounders.
