# Project Instructions

## Language conventions

**Agent-agnostic phrasing.** Do not use "Codex" to refer to the agent executing a skill, the model being benchmarked, or the AI following skill instructions. Use platform-neutral terms instead:

| Instead of | Use |
|---|---|
| "Codex should…" | "The agent should…" |
| "base Codex" | "the base model" |
| "With the skill, Codex…" | "With the skill, the model…" |
| "A Codex skill" | "A skill" |
| "Once installed, Codex will…" | "Once installed, the skill will…" |
| "It gives Codex the conviction…" | "It gives the agent the conviction…" |
| "Codex is not a fiduciary…" | "The assistant is not a fiduciary…" |

This applies to SKILL.md files, README.md files, evals, and any other documentation in this repo. Exception: installation paths like `~/.Codex/skills/` are platform-specific by necessity and may keep the `Codex` path component.
