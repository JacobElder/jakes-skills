# Counterfactuals (rung 3)

Counterfactuals ask about specific cases under hypothetical alternatives, conditional on what actually happened. "Would this patient have recovered without the drug?" "Would this user have churned if we hadn't sent the email?" "Would the company have failed but for the CEO's decision?"

These are *not* the same as rung-2 (interventional) questions. Rung 2 asks about populations: "what's the average effect of the drug on patients in this group?" Rung 3 asks about individuals: "what would have happened to *this specific patient*, given everything we know about them?" The two can give different answers.

Counterfactuals are the rung where causation meets attribution, blame, regret, and policy evaluation under specific cases.

## Why this rung is harder

A randomized experiment fully answers rung-2 questions about average effects. It does *not* fully answer rung-3 questions, because we never observe the same individual under both treated and untreated conditions — only one or the other.

Closing this gap requires assumptions stronger than a DAG. A **structural causal model** (SCM) specifies not only the topology of effects but the functional form of each — how each variable is generated from its parents and an exogenous noise term. With an SCM, counterfactuals become computable.

## The three-step counterfactual procedure

Pearl's algorithm for computing a counterfactual:

**1. Abduction.** Update the noise terms (the "exogenous" inputs) to be consistent with the observed evidence. This conditions the model on what actually happened.

**2. Action.** Modify the model to set X to its counterfactual value. This is the do-operator: sever incoming arrows to X and assign the new value.

**3. Prediction.** Compute Y in the modified model with the updated noise terms.

Concretely: someone took the drug and recovered. We want to know whether they would have recovered without it.

1. *Abduction:* given that this person took the drug and recovered, what does that tell us about their unobserved characteristics (immune strength, disease severity, etc.)?
2. *Action:* set drug = 0 in the modified model.
3. *Prediction:* compute the probability of recovery given the updated characteristics.

The output is the counterfactual: P(recovery | did not take drug, did take drug and recovered).

Each step requires modeling assumptions beyond what observation alone provides.

## Necessary vs. sufficient causation

Two distinct counterfactual questions for the same X→Y relationship:

**Probability of necessity (PN).** Given that Y happened and X happened, would Y have happened without X? "But-for" causation. This is the legal standard for liability: if the accident wouldn't have occurred but for the defendant's action, the defendant is liable.

PN = P(Y_{X=0} = 0 | X = 1, Y = 1)

**Probability of sufficiency (PS).** Given that X didn't happen and Y didn't happen, would X have produced Y if it had occurred? This is the policy-relevant question: how often is X enough on its own to produce Y?

PS = P(Y_{X=1} = 1 | X = 0, Y = 0)

PN and PS can be very different numbers for the same situation. A treatment can be highly *necessary* (most people who recovered would not have recovered without it) but only modestly *sufficient* (most people who didn't take it wouldn't have recovered even if they had).

The combined **probability of necessity and sufficiency (PNS)** captures cases where X both produced Y *and* was needed for it — useful for assigning credit or blame.

## When to invoke counterfactuals

Most everyday causal questions are rung-2: "should we ship this feature?" "does this drug work?" These don't require counterfactual machinery; an interventional answer is what you want.

Counterfactuals come into play when:

- **Attribution.** "What share of this outcome is *because of* X?" (Climate attribution science, fault assignment in accidents, contribution analysis.)
- **Liability.** "Would this harm have occurred but for the defendant's action?"
- **Policy evaluation under specific cases.** "Would this particular patient have benefited from the treatment?"
- **Regret and what-if reasoning.** "Should we have done X instead?"
- **Mediation analysis.** "Of the total effect of X on Y, how much runs through M and how much through other pathways?"

For straight intervention questions ("does X cause Y on average"), stay on rung 2.

## A note on identifiability

Counterfactual quantities are not always identifiable from observational data, even when the corresponding interventional quantity is. Bounds are often available — the counterfactual sits in some range determined by the data and the structural assumptions, even when it can't be pinned down exactly.

When working with a counterfactual question, always check whether it's actually identifiable from what's available. Many counterfactual claims in applied research conflate rungs without acknowledging the additional assumptions required.
