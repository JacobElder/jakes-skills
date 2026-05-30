# Reasoning Transcript

## Step 1: Identify the core question

The user wants to use MaxDiff to evaluate different price points for a SaaS tier pricing decision. The question is whether MaxDiff is the right tool.

## Step 2: Check the method-decision fit table in SKILL.md

The skill's first directive is: "Before sample size, before design, before anything: confirm the method matches the decision. Wrong-method studies cannot be salvaged with more respondents."

The decision table in SKILL.md lists:
- "Optimize a single attribute with many levels (e.g., 40 price points, 30 flavors)" → MaxDiff over levels or partial-profile CBC

That might seem like it endorses MaxDiff for pricing — but the skill also has a dedicated callout under "Common requests":

> "Can we use MaxDiff for pricing?" → Almost never directly. MaxDiff on price points gives a relative preference among prices, which is not the same as willingness to pay or demand curve. Use CBC with price as an attribute, or Van Westendorp / Gabor-Granger for pure pricing.

This is the controlling guidance. The row in the table refers to cases like optimizing flavor variants or non-price features where relative preference is the actual target. For pricing, the output needs to support a demand or willingness-to-pay inference, which MaxDiff cannot provide.

## Step 3: Characterize what MaxDiff actually produces and why it fails here

From maxdiff.md section 1: MaxDiff utilities are logit-scale relative-importance estimates. The model is multinomial logit over best-worst picks within sets. The utilities are only meaningful relative to each other within the study — they have no absolute zero unless anchored, and they still cannot represent demand elasticity even if anchored.

For pricing decisions, you need one of:
- A demand curve (purchase likelihood × volume as a function of price)
- A willingness-to-pay distribution
- A trade-off model (price vs. features)

None of these are producible from MaxDiff utilities.

## Step 4: Identify the structural design failure

Beyond the conceptual mismatch, MaxDiff on price points is also a design failure because price points are ordinally ordered. Respondents will not discriminate in any meaningful way — they will almost universally pick the lowest price as "best" and the highest as "worst." This produces high-precision, meaningless data.

## Step 5: Identify the correct methods

The skill's common-requests callout directly names the alternatives:
- **CBC with price as an attribute** — correct if the decision involves packaging/feature configuration alongside pricing
- **Van Westendorp / Gabor-Granger** — correct if the decision is purely "what price to charge" for a defined product

Given the context (SaaS tier, implying the tier's contents and price are both under consideration), CBC is probably the stronger fit. But if features are already locked in, Gabor-Granger is simpler and faster.

## Step 6: Draft the response

The response should:
1. Clearly say no and explain why (conceptual mismatch + design failure)
2. Name the correct alternatives with brief rationale for each
3. Give a clear actionable recommendation without hedging

Tone: senior practitioner, not condescending, direct. Avoid re-explaining what MaxDiff is. Focus on the failure mode and the fix.

## Skill guidance applied

- Used SKILL.md method-decision table as the first check
- Used SKILL.md "Common requests" section as the controlling callout for pricing
- Used maxdiff.md section 1 (model) and section 9 (failure modes) to characterize why relative utilities don't support pricing inference
- Recommended CBC per SKILL.md conjoint guidance (price as attribute), and named Gabor-Granger/Van Westendorp as the pure-pricing fallback per the same callout
