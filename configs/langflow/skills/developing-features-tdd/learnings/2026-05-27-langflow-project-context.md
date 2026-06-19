---
trigger: Any TDD task in the Langflow repo at /Users/criszl/Documents/langflow. Read this first.
---

# Langflow project context

**Context:** This skill is now invoked inside Langflow — Python/FastAPI backend + React 19/TypeScript frontend + `lfx` executor. `uv` workspace monorepo at `/Users/criszl/Documents/langflow`.

**Lesson:** Treat `AGENTS.md` at the repo root as canonical. Langflow already ships specialty skills under `.agents/skills/`:

- `backend-code-review/`, `component-refactoring/`, `e2e-testing/`, `frontend-code-review/`, `frontend-query-mutation/`, `frontend-testing/`.

Use both: these skills (`.claude-langflow/skills/`) cover the TDD workflow; Langflow's specialty skills cover area-specific patterns (DB schema rules, frontend query patterns, etc.).

**Why:** The user populated `.claude-langflow/skills/` deliberately so generic skills get tailored for Langflow. Conflating with Langflow's own skills duplicates effort or creates contradictions.

**Apply when:** Always, first action of any task in this repo.

## Key paths

- Backend: `src/backend/base/langflow/` (with `api/`, `components/`, `services/`, `graph/`, `custom/`).
- Components: `src/backend/base/langflow/components/<provider>/`.
- Graph engine: `src/lfx/src/lfx/graph/` (separate package).
- Backend tests: `src/backend/tests/unit/`, `src/backend/tests/integration/`.
- Frontend: `src/frontend/src/`.
- Migrations: `src/backend/base/langflow/alembic/versions/`.
- Bundles: `src/bundles/<bundle_name>/`.

## Tooling

- `uv`, not pip/poetry. `uv run pytest`, never bare `pytest`. `uv run git commit`, never bare `git commit`.
- `ruff` (backend), `biome` (frontend), `mypy`, `pytest`, `jest`, `playwright`.
- Hot-reload: `LFX_DEV=1 make backend` (or specific modules) + `make frontend`.
- Cross-platform CI matrix: Ubuntu, Windows, macOS (Intel + ARM) — see `.github/workflows/cross-platform-test.yml`.
