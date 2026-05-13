# Should You Control for "Attended a Career Fair"?

**Short answer: Not automatically — and possibly not at all. Pre-treatment timing is not a license to control. The DAG is.**

---

## Step 1: Name the rung

Your question is rung 2 (intervention): "What is the causal effect of the training program on earnings?" The outcome is earnings; the treatment is training enrollment. You want P(earnings | do(training)), not just a correlation. That distinction matters for every subsequent choice.

---

## Step 2: Sketch the candidate DAGs

"Attended a career fair" (call it CF) is pre-treatment, correlates with training enrollment (T), and correlates with later earnings (E). The standard intuition says: *sounds like a confounder, control for it.* But correlation with both T and E is the fingerprint of every structural type — confounder, mediator, collider, proxy. You need a DAG, not a correlation table.

Here are three plausible structures for CF:

### DAG A — Classic confounder (the folklore case)

```
CF
↙  ↘
T  →  E
```

CF is a common cause: motivated people attend career fairs AND sign up for training AND earn more later. Controlling for CF blocks the back-door path T ← CF → E. **This is the case where the standard advice is correct.**

### DAG B — M-bias (the trap)

```
U1 → CF ← U2
↓           ↓
T           E
```

CF is a *collider* between two separate unobserved factors: U1 (e.g., access to career resources) affects both career-fair attendance and training enrollment; U2 (e.g., underlying career motivation) affects both career-fair attendance and earnings. CF itself has no direct arrow into T or E — it's a downstream symptom of two different latent traits, not a common cause.

By default this path is **closed** — no spurious correlation flows between T and E through CF. Conditioning on CF **opens** the path, creating a spurious U1 ↔ U2 association that contaminates the T → E estimate. You manufacture bias from nothing.

### DAG C — Bias amplification (near-instrument case)

```
CF → T → E
     ↑
     U (unobserved)
     ↓
     E
```

CF strongly predicts training enrollment but has little or no direct effect on earnings (attending a career fair doesn't by itself change your wage). This is an instrument or near-instrument structure. With unmeasured confounding U present, controlling for CF **strictly increases bias**: conditioning on CF removes CF's contribution to the variation in T, leaving the remaining variation in T disproportionately driven by the unmeasured confounder U. U effectively becomes a stronger confounder than it was in the unadjusted estimate.

---

## Step 3: Why the standard advice fails here

The folklore rule is: *"Control for any pre-treatment variable that predicts both treatment and outcome."*

The same correlation pattern — CF predicts T, CF predicts E — is consistent with DAG A (good control), DAG B (M-bias: bad control), and DAG C (bias amplification: bad control). Statistical association between CF, T, and E cannot distinguish these three structures. Temporal ordering doesn't help either: M-bias and near-IV structures are both fully pre-treatment by construction.

The rule fails because it answers a structural question with a statistical criterion.

---

## Step 4: What actually determines the right answer

Ask yourself: *What causes career-fair attendance?*

- If the main driver is a single underlying motivation or information set that also drives both training enrollment and earnings — you're in DAG A territory, and controlling helps.
- If attendance at a career fair is driven by one set of factors that also affects training sign-up (e.g., employer outreach on campus) while earnings are separately driven by a different unmeasured factor (e.g., inherent ambition or skill) — you're in DAG B territory. CF is where these two separate causal rivers happen to meet, making it a collider. Controlling creates the very bias you're trying to remove.
- If career-fair attendance is essentially a predictor of who eventually signs up for training but has no independent earnings impact — you're in DAG C territory, and controlling amplifies bias from whatever unmeasured confounder remains.

In a job training context, the most natural reading is actually a mix of B and C: some people attend career fairs because they're job-market-oriented (related to T); others attend because of access to institutional resources on campus (related to E through a different channel); the career fair itself doesn't determine wages. That pattern points toward M-bias or near-IV, not classic confounding.

---

## Step 5: What to do instead

1. **Draw your DAG explicitly.** Write down the substantive causes of career-fair attendance, training enrollment, and earnings separately. Check whether CF sits at a fork (confounder) or a junction between two separate causal streams (collider).

2. **Look for the unmeasured confounders directly.** What you really want to adjust for is the underlying motivation or background that drives both T and E. If you can measure that directly (e.g., prior employment history, baseline skills, stated career goals), adjust for those instead of for CF as a proxy.

3. **If uncertain, test sensitivity.** Run the analysis with and without CF. If the coefficient on T changes dramatically when you add CF, that's a signal — but it doesn't tell you which estimate is closer to the truth. Only structural reasoning can do that.

4. **Use dagitty.** If the DAG is even slightly complex, draw it at https://www.dagitty.net and ask it for valid adjustment sets. It will tell you whether CF is in the minimal adjustment set or not given your assumed structure.

5. **Consider design-based identification.** If there's a lottery or eligibility threshold for the training program, regression discontinuity or instrumental-variable methods can bypass the covariate-selection problem entirely.

---

## Key takeaway

Pre-treatment timing is not a sufficient justification for including a variable. "Attended a career fair" is pre-treatment, correlated with both treatment and outcome — and that description fits a confounder (control), a collider (don't control), and a near-instrument (don't control as a covariate). The right answer requires a causal model of what drives career-fair attendance, not just a correlation check.

The standard advice — *control for pre-treatment variables that predict both treatment and outcome* — is one of the most persistent errors in applied research. It is wrong as a general rule. Use the structural taxonomy: classify by DAG role, not by timing or correlation.
