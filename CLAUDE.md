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

### What goes in the `.skill` zip

Include: `SKILL.md`, `references/` (all `.md` files), `scripts/` (all `.py`/`.js` files and `requirements.txt` if present), `assets/` (templates, config files). Exclude: `evals.json`, `trigger_queries.json`, `benchmark_comparison.png`, `README.md`, any `HANDOFF`, `TODO`, or planning files.

### When to rebuild the `.skill`

Rebuild the `.skill` whenever the skill reaches a **completion state** (benchmark run completed, new iteration committed, SKILL.md content changed). Use:

```bash
cd <skill-dir>
rm -f <skill-name>.skill
zip -r <skill-name>.skill SKILL.md references/ scripts/ assets/    # include only dirs that exist
```

Do not add directories that don't exist (the zip command will error).

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
