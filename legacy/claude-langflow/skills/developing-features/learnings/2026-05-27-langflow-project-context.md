---
trigger: Any task in the Langflow repo at /Users/criszl/Documents/langflow. Read this first.
---

# Langflow project context

**Context:** This skill is now invoked inside Langflow, a visual workflow builder for AI agents — Python/FastAPI backend + React 19/TypeScript frontend + `lfx` lightweight executor CLI. The repo is a `uv` workspace monorepo at `/Users/criszl/Documents/langflow`.

**Lesson:** Treat `AGENTS.md` (at the repo root) as the canonical guide for development conventions; it supersedes the generic defaults in this skill's SKILL.md. The minimal `CLAUDE.md` just delegates to it. Several specialty Langflow skills already exist under `.agents/skills/` — read them before writing new generic code:

- `backend-code-review/` — backend review focused on services, repositories, SQLAlchemy patterns, DB schema rules.
- `component-refactoring/` — refactor an existing Langflow Component.
- `e2e-testing/` — Playwright end-to-end tests.
- `frontend-code-review/` — React/TypeScript review.
- `frontend-query-mutation/` — TanStack Query patterns in the frontend.
- `frontend-testing/` — Jest unit tests for frontend with templates under `assets/`.

The skills in `.claude-langflow/skills/` (this set) provide the **workflow** (writing PRs, reviewing, TDD, etc.); Langflow's own skills provide **specialty expertise** (DB rules, component refactoring patterns, frontend query patterns). Use both — they complement, not compete.

**Why:** The user populated `.claude-langflow/skills/` deliberately so these generic skills can be tailored for Langflow. Langflow itself already ships specialty skills under `.agents/skills/` that go deeper into specific areas. Conflating the two wastes effort and creates contradictory advice.

**Apply when:** Always, on the first action of any task in this repo. Subsequent actions in the same conversation don't need to re-read this — it's the baseline.

## Key paths

- Backend core: `src/backend/base/langflow/` (langflow-base package)
- Built-in components: `src/backend/base/langflow/components/<provider>/`
- Graph engine: `src/lfx/src/lfx/graph/` (separate `lfx` package — NOT in langflow-base)
- API routes: `src/backend/base/langflow/api/v1/` and `v2/`
- Services: `src/backend/base/langflow/services/<service_name>/`
- Backend tests: `src/backend/tests/unit/` and `src/backend/tests/integration/`
- Frontend: `src/frontend/src/`
- Frontend tests: colocated `*.test.tsx` or under `__tests__/`
- Docs (Docusaurus): `docs/docs/`
- Bundles: `src/bundles/<bundle_name>/`
- Database migrations: `src/backend/base/langflow/alembic/versions/`

## Build / test tooling

- **Python:** 3.10 – 3.13. Package manager: `uv` (NEVER pip/poetry).
- **Node:** 20.19.0+. Package manager: `npm`.
- **Lint/format backend:** `ruff` (replaces black/isort/flake8). Run `make format_backend` before `git commit`.
- **Lint/format frontend:** `biome` (NOT ESLint).
- **Type check:** `mypy` via `make lint`.
- **Test backend:** `pytest` (parallel by default). Run `uv run pytest …`, never bare `pytest`.
- **Test frontend:** `jest` + `playwright`.
- **Pre-commit:** Must invoke `uv run git commit` (the `uv run` ensures the right Python).

## Hot-reload dev loop

- Terminal 1: `LFX_DEV=1 make backend` (FastAPI on :7860) — or `LFX_DEV=openai,anthropic,acme make backend` to load specific component modules only.
- Terminal 2: `make frontend` (Vite on :3000).
