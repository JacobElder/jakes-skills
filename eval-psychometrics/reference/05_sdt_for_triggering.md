# 05 — Signal Detection Theory for Triggering

This file is **SDT used on skill triggering/routing** — not how SDT works. For d′ derivation,
ROC/isosensitivity curves, and the equal-variance assumption, defer to the **signal-detection-
theory skill**. Script: `scripts/sdt_trigger.py`.

## Why triggering is a detection problem

A skill's trigger is a yes/no detector over incoming queries: *fire* or *stay quiet*. Evaluating
it with raw accuracy or F1 conflates two failures that have **different fixes**, which is exactly
what SDT was built to separate. Map the trigger eval to the SDT 2×2:

| | Skill **fires** | Skill **stays quiet** |
|---|---|---|
| Query **is** in-scope (signal) | **Hit** | **Miss** |
| Query **not** in-scope (noise) | **False alarm** | **Correct rejection** |

From the rates `H = hits / (hits+misses)` and `FA = false_alarms / (false_alarms+correct_rej)`:

- **Discriminability d′ = z(H) − z(FA)** — how well the description separates in-scope from
  out-of-scope queries, *independent of how eager it is*. (z = inverse normal CDF.)
- **Criterion c = −½·(z(H) + z(FA))** — the trigger's bias. c < 0 = trigger-happy (fires too
  readily, leans toward false alarms); c > 0 = trigger-shy (too reluctant, leans toward misses);
  c ≈ 0 = neutral.

## The actionability split — the whole point

Two skills can have the same trigger accuracy and need opposite fixes. SDT tells them apart:

- **Low d′ (≈ 0–1): the description can't tell relevant from irrelevant.** No amount of
  eagerness-tuning fixes this — at low d′, every criterion setting trades misses for false alarms
  one-for-one. **Fix the content:** sharpen what the skill is *for*, add the distinguishing
  contexts and the near-miss cases it should *not* catch, resolve overlap with neighboring skills.
  This is a rewrite-the-description problem.
- **High d′ but biased criterion: the description discriminates fine but fires at the wrong
  threshold.** **Fix the wording's eagerness,** not its content: c < 0 (over-fires, collides with
  other skills) → tighten/qualify trigger phrases, add explicit "do not use when…" carve-outs;
  c > 0 (under-fires, the classic skill problem) → make the description "pushier," add more of the
  user phrasings that *should* match. This is a small, targeted edit.

Reporting only accuracy, you'd "fix" both the same way and fail half the time. d′ vs. c routes the
fix correctly. (Note skills tend to **under**-trigger by default, so a positive criterion is the
common finding and the standard remedy is a pushier description.)

## Mutual-exclusion routing between skills, in SDT terms

When you have a *set* of skills that should partition query space, run the detection analysis
**per skill** and read it as a confusion structure:

- A pair of skills that both fire on each other's in-scope queries shows up as **high cross
  false-alarm rates** — they're not discriminable *from each other*. The fix is boundary-drawing:
  make each description state where the other takes over.
- A skill with low d′ specifically against one neighbor (not against unrelated queries) localizes
  the overlap to that pair — you know exactly which two descriptions to disambiguate.
- Track each skill's criterion to balance the routing: if every skill is trigger-shy, queries fall
  through; if several are trigger-happy, they collide.

This turns "my skills' routing is fuzzy" into a per-pair table of *what to edit*.

## Practical cautions

- **Log-linear correction is mandatory at eval scale.** Trigger evals are small, so you'll hit
  H = 1 or FA = 0 constantly, and z(1)/z(0) are ±∞. Apply the standard correction — add 0.5 to each
  cell and 1.0 to each row total — *before* computing rates. The script does this and flags when it
  kicked in (it means your estimate is being pulled toward chance by sparse data; widen the eval).
- **Use a nonparametric backup at tiny N.** When cell counts are small or the equal-variance
  assumption is shaky, report **A′** (nonparametric sensitivity, 0.5 = chance, 1 = perfect) and
  **B″** (nonparametric bias) alongside d′/c. The script returns both.
- **Build a balanced noise set.** d′ and criterion are only meaningful with genuine out-of-scope
  queries (the "noise" trials). A trigger eval with only in-scope prompts can measure misses but
  not false alarms — you'll have no FA rate and the whole framework collapses. Include realistic
  near-miss out-of-scope queries (the ones most likely to cause false alarms), not just obviously
  unrelated ones.
- **Tie it back to the suite.** Triggering quality and task quality are different axes: a skill can
  execute perfectly (high task pass rate) yet trigger terribly (low d′), or vice-versa. Report them
  separately; never average them into one "skill score."
