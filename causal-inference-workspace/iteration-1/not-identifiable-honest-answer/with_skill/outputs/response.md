# Can You Estimate the Causal Effect of Mentorship on Career Success?

**Short answer: Not reliably from this data alone. Here's why, and what you could do instead.**

---

## Step 1: Name the rung

Your question — "does having a mentor *cause* higher career success?" — is a **Rung 2 (intervention) question**. You're asking what would happen to salary if a person were given a mentor, not merely what patterns exist among people who had mentors. Observational data lives on Rung 1 (association). Moving from Rung 1 to Rung 2 requires additional causal assumptions, typically formalized in a DAG. No sample size — not 5,000, not 500,000 — bridges this gap on its own.

---

## Step 2: Sketch the DAG

Let's make the assumptions visible. A minimal DAG for this problem:

```
   U1 (ambition / drive)
   ↙       ↘
Mentor ------→ Salary
   ↑
U2 (social capital / network access)
   ↘
  Mentor
   ↓
  Salary      ←── U3 (industry / field)
```

More carefully written:

```
U1 (ambition) → Mentor
U1 (ambition) → Salary
U2 (social capital) → Mentor
U2 (social capital) → Salary
U3 (field/industry) → Mentor
U3 (field/industry) → Salary
Mentor → Salary   [the path you want]
```

Back-door paths from Mentor to Salary that are NOT the causal path:
- Mentor ← U1 → Salary
- Mentor ← U2 → Salary
- Mentor ← U3 → Salary

To identify the causal effect, you need to block all of these. Your data has demographics. The question is whether demographics close all three backdoors.

---

## Step 3: Named unmeasured confounders

Here are the specific confounders that are almost certainly unmeasured in your dataset:

**1. Ambition / intrinsic drive (U1)**
People who seek out mentors are self-selected for motivation. Ambitious people pursue mentors *and* work harder to succeed. If you don't measure drive, conscientiousness, or goal-orientation, the mentor-salary association will overstate the causal effect — some of it is really the effect of ambition. Demographics (age, gender, education level) don't capture this.

**2. Social capital and network access (U2)**
Having a mentor often requires knowing the right people. Someone raised in a high-status household, who attended a prestigious school, or who already has professional connections is both more likely to obtain a mentor and more likely to earn a high salary — independently of the mentor. Demographic variables are weak proxies for this. Education level helps, but a Harvard MBA and a community college degree holder both have "bachelor's degree" as a demographic category.

**3. Industry and role type (U3)**
Some fields (finance, tech, consulting) have strong mentorship cultures *and* pay more. If field/industry isn't measured, or is only measured coarsely, industry sorting will leak into your estimate. Someone in investment banking mentored or not will out-earn most industries entirely.

**4. Prior performance and ability**
High performers get noticed, get mentors, and get promoted. Prior achievement confounds both the likelihood of receiving mentorship and the outcome. Self-reported mentor status doesn't tell you whether the person attracted a mentor by already standing out.

**5. Organizational context**
Formal mentorship programs at large companies vs. informal mentorship at startups are fundamentally different interventions. The data conflates these. Someone in a structured program at a Fortune 500 is in a different selection environment than someone who cold-emailed an executive.

---

## Step 4: Why demographics alone don't close the backdoors

Even if your demographics include age, gender, race, education level, and geographic region, they are:

- **Proxies, not causes.** Demographics correlate with ambition and social capital but don't measure them. Controlling for a noisy proxy of a confounder removes *some* bias but leaves residual confounding.
- **Potentially mediators or colliders, not just confounders.** Gender, for instance, may affect *both* access to mentors (via discrimination) and salary (via wage gaps). If gender is a mediator of the mentor → salary path (mentor access is partly determined by gender dynamics), then controlling for gender blocks part of the causal effect you want to estimate — overcontrol bias.
- **Incomplete.** The key confounders (ambition, drive, network access, prior performance) are behavioral and psychological constructs. No standard demographic variable captures them.

The back-door criterion requires that your adjustment set Z blocks *every* path from Mentor to Salary that starts with an arrow into Mentor. Ambition, social capital, and ability all have arrows into Mentor and into Salary. If they're unmeasured — or measured only indirectly through demographics — the criterion is not satisfied, and the OLS coefficient on mentor status is not a causal estimate.

---

## Step 5: Verdict

**The causal effect is not identifiable from this data using back-door adjustment.** Running a regression of salary on mentor status plus demographics will give you a number, but that number conflates the causal effect with selection bias from at least three major unmeasured confounders. The honest answer is: you don't know how much of the mentor-salary gap is causal.

This is not a failure of sample size. 50,000 observations with the same variables would have the same problem. More data reduces sampling variance; it does not close structural backdoors.

---

## Step 6: What you could do instead

**Option A: Instrumental variables (IV)**
Find a variable Z that:
1. Affects whether someone got a mentor (relevance)
2. Has no direct effect on salary (exclusion restriction)
3. Shares no confounder with salary (exogeneity)

Candidates worth exploring:
- **Employer-assigned mentor programs**: some employers randomly or quasi-randomly assign mentors to new hires. If you can identify people in formal programs vs. not, program participation could instrument for mentorship.
- **Proximity to a professional association chapter**: distance from a professional organization that facilitates mentorship could be as-if-random variation in access — unrelated to individual ambition.
- **Cohort timing**: entering the workforce during a period when a company had an active mentorship program vs. not.

The exclusion restriction (Z has no direct path to salary) is untestable and must be argued from domain knowledge. This is IV's chief limitation.

**Option B: Natural experiment**
Look for contexts where mentorship was assigned in a way that's as-if-random. Corporate rotational programs that assign mentors by cohort, mentorship lottery programs (some organizations do this), or a policy change that introduced a formal mentorship program at a specific time — these provide variation not driven by individual motivation.

**Option C: Differences-in-differences (DiD)**
If some subset of your professionals experienced a change in mentorship availability (e.g., their company introduced a program, or a program ended), and you have salary data from before and after, DiD compares the salary trajectory of those affected vs. unaffected. This removes time-invariant confounding. The assumption is parallel trends: the treated and control groups would have had similar salary growth absent the change. This requires longitudinal data you don't currently have.

**Option D: Sensitivity analysis (honest reporting)**
If you report the observational association anyway (which can be informative), accompany it with a formal sensitivity analysis — e.g., using the `sensemakr` framework (Cinelli & Hazlett 2020). This quantifies: how strong would an unmeasured confounder need to be (in terms of its correlation with both mentor status and salary) to reduce the estimated effect to zero? If the answer is "a confounder as strong as education," the result is fragile. If the answer is "a confounder 5x stronger than any measured variable," it's more robust.

**Option E: Bounds**
Without assumptions about specific confounders, you can compute Manski-style bounds on the causal effect — the range of values it could plausibly take given the structure of the data. These bounds are often wide, but wide bounds are an honest answer. They prevent overconfident claims.

**Option F: Collect better data**
Add validated measures of conscientiousness, self-efficacy, or career ambition (e.g., via survey). Add prior-job performance ratings. Add detailed industry and role-level data. Add social-capital measures (network size, elite school attendance). With better covariates, back-door adjustment becomes more credible — not certain, but more defensible. This is the standard justification for matching and propensity-score methods: they work when you've actually measured the important confounders, not as a substitute for having measured them.

---

## Summary

| Question | Answer |
|---|---|
| Is this a causal question? | Yes — Rung 2 (intervention) |
| Is it identifiable from your current data? | No — multiple unmeasured confounders |
| Will bigger sample fix it? | No — structural problem, not sampling |
| Can demographics close the backdoors? | Unlikely — they're noisy proxies for the true confounders |
| Can you report the association? | Yes, with explicit caveats and sensitivity analysis |
| What would actually identify the effect? | IV, natural experiment, formal mentorship program randomization, or DiD with longitudinal data |

The mentor-salary correlation in your data is real. Whether it's causal — and if so, how large the effect is — cannot be determined without a source of as-if-random variation in mentorship assignment. That's not a methodological technicality; it's the difference between knowing whether to invest in mentorship programs vs. just knowing that successful people often had mentors.
