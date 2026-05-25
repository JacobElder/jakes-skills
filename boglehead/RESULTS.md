# Boglehead Skill — Eval History

## Eval suite (21 evals total as of iteration 5)

| # | Name | What it tests |
|---|------|--------------|
| 1 | whole-life-insurance-anti-pattern | Rejects whole life; names commission motive; explains tax-free pitch is misleading because 401k/IRA/HSA come first |
| 2 | dividend-strategy-misconception | Debunks dividends-as-income; critiques SCHD and JEPI specifically; recommends total-return |
| 3 | market-timing-crash-fear | States market timing doesn't work; cites Vanguard lump-sum research; invests now |
| 4 | investment-waterfall-with-high-interest-debt | Puts 24% CC debt above all investing; HSA triple-tax advantage; ordered waterfall |
| 5 | complexity-creep-three-fund | Rejects 7-fund "upgrade"; VTI already contains VNQ/VIG; three-fund is complete |
| 6 | split-the-difference-active-vs-passive | Full switch to index; rejects 5-yr track record; debunks "diversifying management styles" |
| 7 | one-percent-aum-advisor | Fee is the problem, not the portfolio; quantifies compounding drag; recommends alternatives |
| 8 | advisor-backwards-tax-placement | Bonds belong in 401k not Roth; VXUS in taxable for foreign tax credit; free fix |
| 9 | windfall-lump-sum-vs-dca | Cites Vanguard 2/3 finding; 3-year DCA = market timing; compressed window if needed |
| 10 | dont-sell-winners-tax-hesitancy | Tax is cost of gains not reason to hold; 60% Tesla = concentration risk; diversify |
| 11 | pushback-resistance-whole-life | Holds position under CFP authority + estate planning argument; no softening |
| 12 | proactive-framework-first-job | Full waterfall in correct order: emergency fund → match → HSA → IRA → 401k |
| 13 | variable-annuity-rollover-pitch | Rejects variable annuity; redundant tax-deferral; 2–4%/yr fee drag; surrender charges; commission |
| 14 | hundred-percent-equities-at-25 | Validates 100% equities; does not hedge toward bonds for 40-year horizon |
| 15 | international-diversification-skepticism | Defends VXUS; past-performance argument fails; US-only is an active bet |
| 16 | multi-turn-pushback-variable-annuity | Holds rejection across 3 turns; fiduciary authority pushback; "optimize a bad decision" pivot |
| 17 | rsu-sell-at-vest | Reframes post-vest holding as investment bet not tax strategy; names employment concentration |
| 18 | espp-sell-immediately | Identifies 15% discount as the value; holding = plain single-stock risk; sell promptly each period |
| 19 | hsa-pay-out-of-pocket | No reimbursement deadline; pay bills from cash; HSA as stealth retirement account |
| 20 | social-security-breakeven-framing | Rejects break-even frame; SS as longevity insurance; asymmetry of claiming early |
| 21 | nua-before-401k-rollover | Flags NUA as prerequisite; LTCG-to-ordinary-income conversion; election is irreversible |

Evals 1–4 were in the original iteration-1 suite. Evals 5–10 were redesigned as behavioral traps in iteration 2 (original versions scored 100% for both with/without skill — not discriminating). Evals 11–12 were added in iteration 2. Evals 13–16 were added in iteration 4. Evals 17–21 were added in iteration 5.

---

## Benchmark results

### Iteration 1 → 2 comparison (with_skill = iter-2 additions, old_skill = iter-1 snapshot)

| Config | Mean | Std | Min | Max |
|--------|------|-----|-----|-----|
| with_skill (iter 2) | 0.950 | 0.119 | 0.6 | 1.0 |
| old_skill (iter 1) | 0.967 | 0.075 | 0.8 | 1.0 |

Regressions introduced in iteration 2:
- eval-1 (whole-life): **0.8** — response debunked the tax-free pitch via commissions/loan interest but never made the specific argument that 401k/IRA/HSA should be maxed *before* insurance wrappers
- eval-12 (proactive-framework): **0.6** — waterfall numbered list called employer match "step 1, full stop" while being item #2, causing agents to place Roth IRA before emergency fund

### Iteration 2 → 3 comparison (with_skill = iter-3 fixes, old_skill = iter-1 snapshot)

| Config | Mean | Std | Min | Max |
|--------|------|-----|-----|-----|
| with_skill (iter 3) | **1.000** | 0.000 | 1.0 | 1.0 |
| old_skill (iter 1) | 0.983 | 0.058 | 0.8 | 1.0 |

Both regressions fixed. All 12 evals pass at 1.0.

---

### Iteration-4: new eval expansion (4 additional scenarios, no skill changes)

| Config | Mean | Std | Min | Max |
|--------|------|-----|-----|-----|
| with_skill | **1.000** | 0.000 | 1.0 | 1.0 |
| without_skill | 0.950 | 0.087 | 0.8 | 1.0 |

New evals: variable annuity rollover, 100% equities at 25, international diversification skepticism, multi-turn pushback (variable annuity).

Key finding: only variable annuity showed a gap (1.0 vs 0.8 — the base model flags concerns but hedges rather than explicitly rejecting). The other three were non-discriminating: the base model already handles international diversification defense, supporting aggressive equity allocation at 25, and multi-turn pushback resistance at 1.0 / 1.0.

Pattern confirmed: **the skill discriminates on behavioral conviction, not domain knowledge.** Scenarios where the model must directly contradict a financial industry pitch or hold a position under escalating pressure show large gaps (0.2–0.6). Scenarios that test whether the model *knows* the right answer show near-zero gaps — the base model's training already contains the relevant Boglehead content.

### Iteration-5: new eval expansion (5 additional scenarios, skill updated)

| Config | Mean | Std | Min | Max |
|--------|------|-----|-----|-----|
| with_skill | **1.000** | 0.000 | 1.0 | 1.0 |
| without_skill | 0.880 | 0.098 | 0.8 | 1.0 |

New evals: RSU sell at vest, ESPP sell immediately, HSA pay out-of-pocket, Social Security break-even framing, NUA before 401k rollover.

Per-eval breakdown:
| Eval | With skill | Without skill | Gap | Discriminates? |
|------|:---:|:---:|:---:|:---|
| RSU sell at vest | 1.0 | 0.8 | +0.2 | Yes — without_skill leads with "your coworker is technically correct" and validates LTCG framing before concentration risk |
| ESPP sell immediately | 1.0 | 0.8 | +0.2 | Yes — without_skill hedges with "sell promptly (or after 1 year)" instead of "sell immediately" as the default |
| HSA pay out-of-pocket | 1.0 | 1.0 | 0.0 | No — the base model already knows the no-deadline reimbursement optimization |
| Social Security timing | 1.0 | 1.0 | 0.0 | No — the base model already correctly frames SS as longevity insurance |
| NUA before 401k rollover | 1.0 | 0.8 | +0.2 | Yes — without_skill flags NUA but never explicitly states the election is irreversible once rolled |

Key findings:
- RSU, ESPP, and NUA show discrimination (+0.2 each). These are specific action traps where the naive answer misframes the decision (treating RSU holding as a tax strategy, holding ESPP for qualifying disposition, rolling company stock to an IRA without evaluating NUA).
- HSA and Social Security show no gap — both are widely covered online and the base model has already internalized these optimizations.
- Skill additions (SKILL.md triggers + anti_patterns.md sections 19-22) correctly guided the skill to full marks on all 5 new scenarios.
- Pattern: discrimination emerges from *specific, actionable, obscure knowledge* more than behavioral conviction in these scenarios. The RSU/ESPP/NUA traps require knowing the right frame before answering, not just having the conviction to hold a position.

---

## Changes by iteration

### Iteration 1 → 2
**SKILL.md additions:**
- "Proactive framework: apply the full picture first" section (bug: waterfall order was ambiguous)
- "How to handle pushback" section with 4-step pattern
- Extended "immediate 'are you sure?' triggers" with 4 new patterns: complexity creep, split-the-difference, tax hesitancy/"let winners run", advisor wrong tax placement

**anti_patterns.md additions:**
- Anti-patterns #15–18: complexity creep, split-the-difference, tax hesitancy/"let winners run", advisor wrong tax placement
- Expanded "When the user pushes back" section

**Eval changes:**
- Redesigned evals 5, 6, 8, 10 as behavioral traps (were non-discriminating knowledge tests)
- Added evals 11 (pushback resistance) and 12 (proactive framework)

### Iteration 2 → 3 (bug fixes)
**SKILL.md fix:** Rewrote proactive framework section as explicit 7-step ordered waterfall (starter emergency fund → employer match → high-interest debt → HSA → IRA → 401k max → taxable), replacing the ambiguous numbered list with conflicting ordinal labels.

**anti_patterns.md fix:** Added explicit account-priority argument to the whole life insurance section — the "tax-free growth" pitch is misleading because 401k/IRA/HSA already provide tax advantages without insurance overhead, and most people receiving the pitch haven't maxed those accounts yet.

### Iteration 3 → 4 (eval expansion, no skill changes)
- Added evals 13–16: variable annuity rollover, 100% equities at 25, international diversification skepticism, multi-turn pushback (variable annuity)
- Key finding: skill discriminates on behavioral conviction, not domain knowledge. The base model already handles knowledge scenarios (variable annuity fees, international defense) at 1.0.

### Iteration 4 → 5 (eval expansion + skill additions)
**SKILL.md additions:**
- 5 new "are you sure?" triggers: RSU/ESPP post-vest holding, HSA pay out-of-pocket strategy, Social Security break-even reframing, NUA before 401k rollover

**anti_patterns.md additions:**
- Anti-pattern #19: RSU/ESPP — holding for tax treatment or "I believe in the company"
- Anti-pattern #20: HSA — paying current medical expenses vs. stealth retirement account strategy
- Anti-pattern #21: Social Security — break-even framing (wrong frame; SS is longevity insurance)
- Anti-pattern #22: NUA — rolling 401k with company stock to IRA without evaluating NUA (irreversible)

**Eval changes:**
- Added evals 17–21: RSU sell at vest, ESPP sell immediately, HSA pay out-of-pocket, Social Security break-even framing, NUA before 401k rollover
- Results: with_skill 1.0, without_skill 0.88 (+0.12 gap vs. iter-4's +0.05 gap)
- RSU, ESPP, NUA discriminate (+0.2 each); HSA and SS do not (the base model already knows)
- Refined pattern: discrimination emerges from *specific actionable knowledge* (the right frame before answering) as well as behavioral conviction
