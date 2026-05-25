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
