# Project Instructions

## Language conventions

**Agent-agnostic phrasing.** Do not use "Claude" to refer to the agent executing a skill, the model being benchmarked, or the AI following skill instructions. Use platform-neutral terms instead:

| Instead of | Use |
|---|---|
| "Claude should…" | "The agent should…" |
| "base Claude" | "the base model" |
| "With the skill, Claude…" | "With the skill, the model…" |
| "A Claude skill" | "A skill" |
| "Once installed, Claude will…" | "Once installed, the skill will…" |
| "It gives Claude the conviction…" | "It gives the agent the conviction…" |
| "Claude is not a fiduciary…" | "The assistant is not a fiduciary…" |

This applies to SKILL.md files, README.md files, evals, and any other documentation in this repo. Exception: installation paths like `~/.claude/skills/` are platform-specific by necessity and may keep the `claude` path component.

---

## Dual packaging — always maintain both forms

Every skill must have **both**:

1. **Loose files** — `SKILL.md` at the directory root, plus `references/` (or `reference/`), `scripts/`, `assets/`, etc. as applicable. These are the editable source of truth.
2. **Packaged `.skill` zip** — `<skill-name>/<skill-name>.skill`, a ZIP archive containing exactly the same content as the loose files (SKILL.md + references + scripts + assets). Used for uploading to Claude.ai chat.

Both forms must stay in sync. Whenever you edit loose files, also update the `.skill` zip. Never commit with one form ahead of the other.

**This has silently failed before — verify, don't assume.** Before any commit that touches a `.skill` zip, or as part of any "audit" or "structural fix" pass across skills, check that every file inside each `<skill>.skill` zip also exists as a loose file at the matching path (and vice versa is worth a glance too, in case loose files were added but the zip never rebuilt). A one-liner using Python's `zipfile` per skill directory is enough — `unzip -l` plus `test -f` in a loop works too. Do this across **all** skill directories periodically, not just the one you're currently editing, since this class of bug is easy to introduce in one skill while "fixing" another (see the 2026-07-01 incident above).

### What goes in the `.skill` zip

Include: `SKILL.md`, `references/` (all `.md` files), `scripts/` (all `.py`/`.js` files and `requirements.txt` if present), `assets/` (templates, config files). Exclude: `evals.json`, `trigger_queries.json`, `benchmark_comparison.png`, `README.md`, any `HANDOFF`, `TODO`, or planning files.

### When to rebuild the `.skill`

Rebuild the `.skill` whenever the skill reaches a **completion state** (benchmark run completed, new iteration committed, SKILL.md content changed). Use:

```bash
cd <skill-dir>
rm -f <skill-name>.skill
zip -r <skill-name>.skill SKILL.md references/ scripts/ assets/    # include only dirs that exist
```

**`zip -r` does NOT error on a missing directory** — it prints a `zip warning: name not matched: ...` and exits 0, silently producing a smaller archive. This is exactly how `game-development` lost its `references/` content from the packaged `.skill` on 2026-07-01: a rebuild ran after the loose `references/` directory had never been extracted from a prior zip-only state, the command silently zipped just `SKILL.md`, and it went unnoticed for several commits. The same audit that day also found `psychometrics` (whose `references/` had *never* existed as loose files, only inside the zip, since the skill's creation) and `dimensionality-reduction` (whose zip was stale and out of sync with a since-restructured loose layout). Before treating a rebuild as done, verify it — don't trust the exit code:

```bash
ls references/ scripts/ assets/ 2>/dev/null   # confirm these exist BEFORE zipping if SKILL.md references them
unzip -l <skill-name>.skill                   # confirm the zip actually contains what you expect after
```

If `SKILL.md` links to `references/foo.md` or `scripts/bar.py`, those paths must exist as loose files at exactly that location — grep `SKILL.md` for `references/` and `scripts/` references and confirm each resolves on disk. If you're about to `zip -r` and one of `references/`, `scripts/`, `assets/` doesn't exist as a loose directory, stop and figure out why (content only in an old zip? never extracted? wrong path?) rather than proceeding — don't add directories that don't exist to the zip command without first understanding why they're missing.

### Completion-state checklist

When a skill reaches a completion state:

1. **Rebuild the `.skill` zip** (see above).
2. **Update the skill's local README** with current benchmark numbers (assertions with skill, assertions without, delta in pp).
3. **Update the global README.md** table row and detailed section with the new numbers.
4. **Document which model was used** for the benchmark run (see Model attribution section below).

---

## Model attribution in benchmark documentation

Every benchmark result must name the model(s) used. Evals performance is model-dependent — the same eval suite can show very different deltas on different models.

**Required format:**

- In the skill's local `README.md` benchmark section, always state: "Graded by `<grader-model-id>`; responses from `<response-model-id>`."
- In the global `README.md` table row, append the response model in parentheses, e.g., `+11.0pp (100/100 with skill, 89/100 base; sonnet-4-6)`.
- In benchmark plots or tables, include the model ID in a caption or header row.

If you add eval results from a different model than the original benchmark, document both runs separately — do not silently merge numbers from different models.
