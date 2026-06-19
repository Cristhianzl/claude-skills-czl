---
trigger: Any task that writes or modifies tests in /Users/criszl/Documents/langflow.
---

# Langflow project context

**Context:** This skill is invoked inside Langflow — Python/FastAPI backend, React 19/TS frontend, `lfx` graph engine. `uv` workspace monorepo.

**Lesson:** Treat `AGENTS.md` at the repo root as canonical for test conventions. Langflow already ships specialty test skills at `.agents/skills/`:

- `frontend-testing/` — Jest unit tests with `assets/` templates for components, hooks, utilities.
- `e2e-testing/` — Playwright end-to-end tests.

Use them when the test type matches. This skill (`writing-tests`) covers the workflow; the specialty skills cover the patterns.

**Why:** Langflow's test stack and policies (no mocks, ComponentTestBase, `uv run pytest`) override the generic defaults. The specialty skills already cover frontend; this learning fills the gap for backend.

**Apply when:** Always, first action of any test-writing task in this repo.

## Test stack at a glance

| Layer        | Backend (Python)                          | Frontend (TypeScript)               |
|--------------|-------------------------------------------|--------------------------------------|
| Unit         | `pytest` + `pytest-asyncio`               | `jest`                               |
| Integration  | `pytest` against real Postgres / SQLite   | (limited; mostly via E2E)           |
| E2E          | (via Playwright through frontend)         | `playwright`                         |
| Where        | `src/backend/tests/unit/`, `integration/` | colocated `*.test.tsx`, `__tests__/` |
| Coverage     | `pytest-cov` (branch coverage)            | `jest --coverage`                    |

## Key paths

- Backend tests: `src/backend/tests/`.
- Test base classes: `src/backend/tests/base.py` (`ComponentTestBaseWithClient`, `ComponentTestBaseWithoutClient`).
- Frontend tests: alongside source, or in `__tests__/`.
- Frontend test templates: `.agents/skills/frontend-testing/assets/`.

## Tooling

- `uv run pytest path::test`, never bare `pytest`.
- `make unit_tests` (parallel), `make unit_tests async=false` (sequential).
- `make test_frontend` (Jest), `make tests_frontend` (Playwright e2e).
- Sub-package: `uv sync --group dev --package <name>` first, then `uv run pytest …`.
