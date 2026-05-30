# Getting to Absolute Importance from a MaxDiff

This is a real limitation of standard MaxDiff that trips up a lot of stakeholders, and it matters which direction you push them.

## The problem: plain MaxDiff utilities are relative by construction

Standard MaxDiff utilities have no absolute zero. The normalization (sum-to-zero or sum-to-100) means every study produces scores relative to the items in *that* study. An item scoring 15 on a 0–100 scale might be universally loved in a world where everything else is also loved — or it might be genuinely unimportant. You cannot tell from the utility alone. The only valid claim from unanchored MaxDiff is: "Item A is more preferred than Item B." You cannot claim "Item A is important" or "Item B is unimportant."

When stakeholders ask "which features are actually important," they're asking about absolute importance — does this feature cross a threshold that would drive behavior? That requires anchoring.

## The solution: anchored MaxDiff

There are two established anchoring methods.

### Direct binary anchor (recommended default)

After respondents complete all MaxDiff sets, present every item one at a time (or as a checklist) and ask a threshold question:

> "Which of these would you consider an important factor in your decision?"

or

> "Which of these would be a meaningful benefit to you?"

The proportion who flag each item as "yes" is your anchor. Items where the majority flag "yes" are genuinely important; items flagged by a minority are not. You can also use individual-level flagging to rescale utilities: in the HB model, the anchor mark serves as a reference point, and items with utilities above the anchor-implied threshold are "above the bar."

The cleanest reporting output: **share of respondents who flagged each item as important** (from the binary question), plotted alongside the utility rank. This gives stakeholders two numbers per item — where it ranks, and whether it actually matters.

**The wording matters enormously.** "Would you like to have this feature?" will inflate flags (everything sounds nice). "Would this feature meaningfully influence your decision?" forces a more meaningful threshold. Match the wording to the decision context.

### Dual-response anchor (use when direct binary would feel awkward)

Instead of a separate post-task question, ask a follow-up after each MaxDiff set:

> "Of the items you just saw, are any of them genuinely important to your decision?"

This embeds the anchor in the task itself. The estimation model then simultaneously fits utilities and each item's probability of exceeding the respondent's internal threshold.

Dual-response tends to have less scale-use bias than a standalone binary question. The tradeoff: it's more complex to implement correctly (requires custom estimation), longer per set, and produces noisier per-item anchor estimates at typical sample sizes unless you have n ≥ 400+.

For most studies where the anchor question can stand alone naturally, direct binary is the right choice.

## What the output looks like

Once anchored, you can report:

1. **Share above the bar** — the percentage of respondents for whom each item exceeded the threshold. This is the "actually important" number. Items at 70%+ are broadly important; items at 20% are niche or irrelevant.

2. **Rescaled utilities** — for rank-ordering within the "above the bar" set. Knowing Feature A and Feature B both clear the threshold, but A is preferred 2:1 over B, is actionable.

3. **Cross-study comparability** — anchored shares are comparable across different MaxDiff studies; raw utilities are not. If the stakeholder will want to track importance over time or compare to a prior wave, the anchor is not optional.

## What to avoid

Do not present unanchored utilities with language like "moderately important" or "low importance." Positioning utilities along an importance gradient when you have no anchor is a fabrication — it sounds like insight but is just labeling arbitrary points on a relative scale.

Also do not use the raw utility magnitude as a proxy for "important vs. not important." A utility of 20 (vs. the top item at 80) could still describe something most respondents care about deeply — it's just less preferred *relative to the other items tested*. The anchor is the only honest way to make absolute claims.

## If the study already ran without an anchor

You have limited options:

- **Refield with anchoring** — the right call if the decision is high-stakes and the cost of a wrong priority list is meaningful.
- **Proxy anchor from a separate survey question** — if you have a separate importance rating or a "must-have vs. nice-to-have" question, you can map that onto items post hoc. This is a workaround, not a substitute; the anchor will be noisier.
- **Flag the limitation clearly** — if you must report results, say explicitly: "These scores show relative preference only. We cannot determine from this study which features cross the threshold of 'actually important' without anchoring data. Do not use these utilities to conclude any feature is unimportant."

The third option protects you professionally and forces stakeholders to be honest about what the data can and cannot support.
