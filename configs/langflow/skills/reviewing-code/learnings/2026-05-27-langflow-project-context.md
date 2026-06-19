---
trigger: Any PR review task in /Users/criszl/Documents/langflow.
---

# Langflow project context

**Context:** Reviewing a PR inside Langflow — Python/FastAPI backend, React/TS frontend, `lfx` graph engine. `uv` workspace monorepo.

**Lesson:** Treat `AGENTS.md` at the repo root as the canonical conventions doc. Langflow already ships specialty review skills at `.agents/skills/`:

- `backend-code-review/` — backend review with sub-rules under `references/` (repositories, sqlalchemy, db-schema, architecture).
- `frontend-code-review/` — React/TS review.
- `component-refactoring/` — refactor-specific patterns.

This skill (`reviewing-code`) covers the general workflow (output format, severity scoring, comprehension audit). Apply Langflow's specialty review skills when the PR touches their area — they go deeper into DB schema rules, repository patterns, etc.

**Why:** Conflating generic and Langflow-specific reviews wastes effort. The specialty skills already encode the team's DB and repository patterns; this skill provides the wrapper, the severity labels, the GitHub comment formatting.

**Apply when:** Always, first action of any review task in this repo.
