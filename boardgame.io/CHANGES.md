# boardgame-io skill — eval & polish pass

## What was done

### Smoke test
Ran `scripts/smoke-test.js` against `boardgame.io@0.50.2` (fresh install):
**16/16 passed, 0 failed.** All protected invariants hold.

### Eval grading (final: 30 evals, 100 assertions)

Ran all 30 evals through the standard harness (executor: claude-sonnet-4-6, grader: claude-haiku-4-5-20251001).

| Condition | Passed | Total | % |
|---|---|---|---|
| baseline (no skill) | 89 | 100 | 89.0% |
| with_skill | 100 | 100 | **100.0%** |
| **delta** | | | **+11.0pp** |

**Differentiating evals** (skill moved at least one assertion):

| ID | Name | Base | Skill | Gap |
|---|---|---|---|---|
| E10 | events-in-moves | 0/3 | 3/3 | **+100pp** — base kept using `ctx.events`, offered a wrong `client:false` workaround |
| E27 | turn-order-once-phase | 1/3 | 3/3 | **+67pp** — base diagnosed missing `endTurn()` (wrong); skill knows `next:` key on phase is missing |
| E02 | phase-move-shadowing | 2/3 | 3/3 | +33pp — base missed "omit phase moves key" option |
| E03 | endif-no-events | 2/3 | 3/3 | +33pp — base didn't note `events` inaccessible in `endIf` |
| E14 | maxmoves-endturn | 2/3 | 3/3 | +33pp — base used deprecated `moveLimit` without noting it |
| E00 | random-api-config | 3/4 | 4/4 | +25pp — base didn't note "no config needed" |
| E08 | bot-enumerate-required | 3/4 | 4/4 | +25pp — base missed positional `(G, ctx, playerID)` signature distinction |
| E17 | secret-hidden-state | 3/4 | 4/4 | +25pp — base missed `G.secret`/`G.players[id]` convention |

E10 and E27 are the skill's highest-value catches: both involve the base model being confidently wrong in a specific way that misleads a developer.

**Delta vs target (+25–35pp):** +11pp is below target. The gap is structural — baseline Sonnet 4.6 already knows most 0.50.x patterns. Most new evals added (E23-E26) also passed baseline at 100%; E27 (TurnOrder.ONCE) was the only new trap that differentiated.

### Edits made

1. **Created `boardgame.io/references/` subdirectory** and moved `typescript.md`, `turn-order.md`, `flow-lifecycle.md`, `lobby-and-server.md` into it. SKILL.md already pointed to `references/` paths — the files were incorrectly flat.

2. **Created `boardgame.io/scripts/` subdirectory** and moved `smoke-test.js` into it. SKILL.md already referred to `scripts/smoke-test.js`.

3. **Added symptom-table row to SKILL.md** (line 359): "Card briefly shows as `undefined` then corrects" → secret move ran optimistically without `G.secret` → mark `client: false`. One line, no invariant touched. SKILL.md is now 382 lines (< 400 ceiling).

4. **Added 5 new positive evals (E23-E27)** and renumbered the two existing negatives to E28-E29 (keeping them last). New evals cover: TypeScript `skipLibCheck`, `client: false` for secret moves, `redact: true` for move-arg log leakage, `ctx.events` code-review trap, and `TurnOrder.ONCE` phase-advance trap.

5. **Added 5 new should-trigger entries** to `trigger_queries.json` matching the new evals.

6. **Updated `boardgame.io-workspace/run_evals.py`** to read refs from `SKILL_DIR / "references"` instead of `SKILL_DIR` directly.

7. **Populated `evals.json`** — all 100 assertions across 30 evals have `passed: true` and `evidence` from the with_skill graded responses.

No SKILL.md invariants were weakened. No API claims were altered. Description is 837 chars (≤ 1024). Agent-agnostic language verified (no "Claude" in skill files).
