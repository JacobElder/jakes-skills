# Boglehead Skill — Eval History

## Eval suite (12 evals, finalized in iteration 2)

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

Evals 1–4 were in the original iteration-1 suite. Evals 5–10 were redesigned as behavioral traps in iteration 2 (original versions scored 100% for both with/without skill — not discriminating). Evals 11–12 were added in iteration 2.

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

Key finding: only variable annuity showed a gap (1.0 vs 0.8 — base Claude flags concerns but hedges rather than explicitly rejecting). The other three were non-discriminating: base Claude already handles international diversification defense, supporting aggressive equity allocation at 25, and multi-turn pushback resistance at 1.0 / 1.0.

Pattern confirmed: **the skill discriminates on behavioral conviction, not domain knowledge.** Scenarios where Claude must directly contradict a financial industry pitch or hold a position under escalating pressure show large gaps (0.2–0.6). Scenarios that test whether Claude *knows* the right answer show near-zero gaps — base Claude's training already contains the relevant Boglehead content.

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
