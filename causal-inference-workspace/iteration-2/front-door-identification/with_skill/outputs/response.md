# Causal Identification of Training on Performance Ratings

## Step 1: Name the Rung

This is a **Rung 2 (intervention)** question. You want to know what would happen to performance ratings if you *did* provide training — P(Rating | do(Training)). Observational association between who received training and their ratings is a Rung 1 answer. The concern about the unmeasured confounder is exactly the right flag that Rung 1 tools cannot answer this without additional causal assumptions.

---

## Step 2: Sketch the DAG

Here is the causal structure you have described:

```
  U (Ambition — unobserved)
  ↙                    ↘
Training  →  Skills Applied  →  Performance Rating
```

In prose:
- **U (Ambition)** is an unobserved common cause of Training (ambitious employees get sent to or seek training) and Performance Rating (ambitious employees perform better regardless of training).
- **Training → Skills Applied → Performance Rating** is the full directed causal path. Skills Applied on the Job is a mediator that sits strictly between Training and Performance.
- There is a back-door path: Training ← U → Performance Rating. This path is open and contains an *unobserved* node, so back-door adjustment is not possible.

---

## Step 3: Can the Effect Be Identified? The Front-Door Criterion

The unmeasured confounder blocks the back-door strategy. But this does **not** mean the effect is unidentifiable. The structure you have described is almost exactly Pearl's classic front-door scenario. Ask whether Skills Applied satisfies the **front-door criterion**:

1. **M blocks all directed paths from Training to Performance Rating.**
   Skills Applied must capture the *entire* effect of Training on Performance — meaning Training has no direct effect on Performance except through Skills Applied. If training only affects ratings because it causes employees to apply new skills (and not, for example, because attending training itself signals something to managers), this condition holds.

2. **No unblocked back-door path from Training to Skills Applied.**
   The back-door path from Training to Skills Applied would run through U (Ambition). Does Ambition independently cause Skills Applied, separately from training? The critical question here is whether ambitious employees apply skills at work *because of their ambition* rather than because of the training. If Skills Applied is defined specifically as applying the training content in daily work, and ambitious employees without training would not be "applying training content" (because there is no training content to apply), then this condition plausibly holds. Ambition causes who gets training, and trained employees apply the skills — but Ambition's path to Skills Applied runs *through* Training, not independently around it. In DAG terms: U → Training → Skills Applied, not U → Skills Applied directly.

3. **All back-door paths from Skills Applied to Performance Rating are blocked by Training.**
   Is there any back-door from Skills Applied to Performance Rating that bypasses Training? The only plausible back-door would run through U. Does U (Ambition) independently cause Skills Applied without going through Training? If not — if the only way to be "applying training content" is to have received the training — then conditioning on Training blocks the one back-door path from Skills Applied back to U, and thus blocks all back-doors from Skills Applied to Performance Rating.

If all three conditions hold, the total causal effect P(Rating | do(Training)) is identified from observational data via the **front-door adjustment formula**:

```
P(Rating | do(Training)) = 
  Σ_M  P(Skills Applied = M | Training)  ×  Σ_T'  P(Rating | Skills Applied = M, Training = T') P(Training = T')
```

In regression terms, this is a two-stage procedure:
- **Stage 1:** Regress Skills Applied on Training to estimate how training affects skill application.
- **Stage 2:** Regress Performance Rating on Skills Applied and Training together to estimate how skill application affects performance, using the variation in Training to block the back-door from Skills Applied to Performance via U.

The total effect is the product of the two stages, averaged over the distribution of Training.

---

## Step 4: Does "Skills Applied" Create Any New Problems?

You correctly identified that Skills Applied sits between Training and the outcome — making it a mediator, not a confounder. This has two implications:

**Do not include it naively as a covariate in a single regression of Performance on Training.** That would block the very causal path you are trying to measure and estimate only the direct effect of Training on Performance that bypasses skill application — likely zero or near-zero if the entire mechanism runs through skills. This is the mediator (overcontrol) trap from the structural taxonomy.

**Use it as the front-door mediator in the two-stage identification procedure described above.** This is the correct role for this variable.

---

## Step 5: The Most Important Condition to Scrutinize

The front-door criterion is powerful but its conditions are restrictive. The one most worth stress-testing in your setting is **Condition 1**: does Training affect Performance *entirely* through Skills Applied, or are there direct paths?

Potential direct paths to consider:
- **Signaling effects.** Does completing training affect how managers rate employees independently of whether the employee actually applies skills? If yes, there is a direct Training → Performance arrow that bypasses Skills Applied, and the mediator no longer fully blocks the causal path.
- **Selection into visibility.** Does attending training make an employee more visible to decision-makers, affecting ratings through a non-skill mechanism?
- **Measurement bleed.** Is "Skills Applied" defined narrowly enough that it captures only the training-specific content? If it also absorbs ambient motivation or effort, it may be a partial descendant of U directly, which would violate Condition 2.

If Condition 1 is violated and there is a residual direct effect, the front-door formula gives a biased estimate of the total effect (it will undercount the direct effect). You would need to either (a) measure and account for that direct pathway, or (b) treat the front-door estimate as a lower bound on the total effect, with sensitivity analysis on the size of the direct path.

---

## Step 6: Alternative DAG Readings and Their Implications

| Structural assumption | Consequence |
|---|---|
| Skills Applied fully mediates Training → Performance; no direct Training → Performance path; no direct U → Skills Applied path | Front-door criterion satisfied; effect identifiable via the two-stage formula |
| Training has a direct effect on Performance in addition to the mediated path | Front-door underestimates total effect; size of bias equals the direct effect |
| Ambition (U) independently causes Skills Applied (e.g., ambitious employees apply skills regardless of training content) | Condition 2 violated; back-door from Training to Skills Applied is open through U; front-door formula gives biased estimate |
| Skills Applied affects Performance but has its own unobserved confounders unrelated to Training or Ambition | Condition 3 violated; would need to block those additional back-doors |

---

## Conclusion

**No — the unmeasured confounder does not make this effect unidentifiable**, given the structure you described. The variable "Skills Applied on the Job" is exactly the kind of observed mediator that Pearl's front-door criterion was designed to exploit. When:

1. Skills Applied fully mediates the Training → Performance relationship,
2. Ambition does not independently cause Skills Applied except through Training, and
3. Conditioning on Training blocks the back-door from Skills Applied to Performance via Ambition,

— the total causal effect of Training on Performance Ratings is identified from observational data using the front-door adjustment formula, despite the unobserved confounder.

The critical practical work is verifying Condition 1 (no direct effect of Training on Performance that bypasses skill application) and Condition 2 (Ambition does not independently drive skill application outside of training). Both are domain judgments, not statistical ones — which is precisely why the DAG must be made explicit and its assumptions stated openly. If the conditions hold, run the two-stage procedure. If you are uncertain about the direct-effect assumption, run a sensitivity analysis around the size of the residual direct path.
