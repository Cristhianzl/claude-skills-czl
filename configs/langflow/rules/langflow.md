---
description: Langflow — component, security, migration, and workflow rules specific to this repo
globs: "**/*.py"
---

# Langflow

> Prerequisite: `CLAUDE.md` (general baseline). Depth: `skills/building-langflow-components`, `skills/developing-features`, and `skills/reviewing-code/learnings/`.

## Hook-enforced (`hooks/check-langflow-rules.py`)

- **API keys use `SecretStrInput`**, never `MessageTextInput` — encrypted at rest, masked in the UI.
- **No top-level SDK instantiation in component modules.** No `client = openai.OpenAI()` at module top — instantiate inside the output `method` (lazy import + lazy init).
- **Alembic migrations declare `Phase: EXPAND | MIGRATE | CONTRACT`** in the docstring/comments.

## Enforced by review + the human

- **Never rename a Component class.** The class name is its identity in every saved flow JSON. To evolve, add a new class with the new name, mark the old one `deprecated = True`, and keep its behavior intact. Same rule for every `inputs[].name` and `outputs[].name`.
- **Bundle changes update `BUNDLE_API.md`** in the same commit (the pre-commit changelog gate blocks otherwise).
- **`uv run` for every Python invocation** — `uv run pytest`, `uv run ruff`, and even `uv run git commit` (pre-commit hooks need the workspace venv). Bare `python` / `pip` / `pytest` / `git commit` fail or misbehave.
- **Prefer real integrations over mocks** in tests; mock only the failure modes a real sandbox cannot reproduce (per `AGENTS.md`).

## Context to read first

- `AGENTS.md` (canonical) and the relevant `.agents/skills/` for area expertise, before any non-trivial work.
- New components → `skills/building-langflow-components`. Placement: generic/broadly useful → `src/backend/base/langflow/components/<provider>/`; niche/ecosystem-specific → `src/bundles/<bundle>/` (and its `BUNDLE_API.md`).
