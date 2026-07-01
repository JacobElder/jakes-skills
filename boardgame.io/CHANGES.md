# boardgame-io skill — eval & polish pass

## What was done

### Smoke test
Ran `scripts/smoke-test.js` against `boardgame.io@0.50.2` (fresh install):
**16/16 passed, 0 failed.** All protected invariants hold.

### Eval grading

Ran 25 evals through the standard harness (executor: claude-sonnet-4-6, grader: claude-haiku-4-5-20251001).

| Condition | Passed | Total | % |
|---|---|---|---|
| baseline (no skill) | 73 | 82 | 89.0% |
| with_skill | 82 | 82 | **100.0%** |
| **delta** | | | **+11.0pp** |

**Differentiating evals** (skill moved at least one assertion):

| ID | Name | Base | Skill | Gap |
|---|---|---|---|---|
| E10 | events-in-moves | 0/3 | 3/3 | **+100pp** — base model kept using `ctx.events`, offering a wrong `client:false` workaround |
| E02 | phase-move-shadowing | 2/3 | 3/3 | +33pp — base missed "omit phase moves key" option |
| E03 | endif-no-events | 2/3 | 3/3 | +33pp — base didn't note `events` is inaccessible in `endIf` |
| E14 | maxmoves-endturn | 2/3 | 3/3 | +33pp — base used deprecated `moveLimit` without noting it |
| E00 | random-api-config | 3/4 | 4/4 | +25pp — base didn't explicitly note "no config needed" |
| E08 | bot-enumerate-required | 3/4 | 4/4 | +25pp — base didn't note positional `(G, ctx, playerID)` signature distinction |
| E17 | secret-hidden-state | 3/4 | 4/4 | +25pp — base used custom `playerView` but missed `G.secret`/`G.players[id]` convention |

E10 is the skill's primary value: the base model is confidently wrong there (never corrects `ctx.events` → `events`), exactly matching the handoff's threat model.

**Delta vs target (+25–35pp):** +11pp is below target. The gap is structural — baseline Sonnet 4.6 already knows most 0.50.x patterns. The 18 evals where baseline scored 100% are not differentiating. Future iterations could add harder traps (e.g., prompts that explicitly tempt the old `(G, ctx)` signature, or TypeScript-specific traps) to widen the delta.

### Edits made

1. **Created `boardgame.io/references/` subdirectory** and moved `typescript.md`, `turn-order.md`, `flow-lifecycle.md`, `lobby-and-server.md` into it. SKILL.md already pointed to `references/` paths — the files were incorrectly flat.

2. **Created `boardgame.io/scripts/` subdirectory** and moved `smoke-test.js` into it. SKILL.md already referred to `scripts/smoke-test.js`.

3. **Updated `boardgame.io-workspace/run_evals.py`** to read refs from `SKILL_DIR / "references"` instead of `SKILL_DIR` directly.

4. **Populated `evals.json`** — all 82 assertions now have `passed: true` and `evidence` from the with_skill graded responses.

No changes were made to SKILL.md body, SKILL.md frontmatter, any reference file content, or any protected invariant. No API claims were altered.
