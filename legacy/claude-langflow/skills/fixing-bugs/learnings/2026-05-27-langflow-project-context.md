---
trigger: Any bug-fix task in the Langflow repo at /Users/criszl/Documents/langflow. Read this first.
---

# Langflow project context

**Context:** This skill is invoked inside Langflow — `uv` workspace monorepo with backend (`src/backend/base/langflow/`), frontend (`src/frontend/`), and a separate `lfx` graph-engine package (`src/lfx/`).

**Lesson:** Treat `AGENTS.md` at the repo root as canonical. Langflow ships specialty skills at `.agents/skills/` — `backend-code-review/`, `component-refactoring/`, `e2e-testing/`, `frontend-*`. Read them when the bug touches their area.

**Why:** Generic bug-fix rules apply, but Langflow has specific hotspots — component discovery, graph execution split, expand-contract migrations — that aren't obvious from the SKILL.md alone.

**Apply when:** Always, first action of any bug-fix task in this repo.

## Where to look by symptom

| Symptom                                                     | First place to grep                                                         |
|-------------------------------------------------------------|------------------------------------------------------------------------------|
| Component missing / wrong on a saved flow                   | `src/backend/base/langflow/components/<provider>/` (renames break flows)    |
| Flow execution crash / wrong order                          | `src/lfx/src/lfx/graph/` (NOT in langflow-base)                              |
| API error (404, 500, schema mismatch)                       | `src/backend/base/langflow/api/v1/` or `v2/`                                 |
| DB migration failure                                        | `src/backend/base/langflow/alembic/versions/` + pre-commit migration validator |
| Auth / session bug                                          | `src/backend/base/langflow/services/auth/`                                   |
| Secret / variable not decrypted                             | `src/backend/base/langflow/services/variable/` + `utils/secrets.py`         |
| UI bug                                                       | `src/frontend/src/` (often a Zustand store under `stores/`)                 |
| Streaming / SSE not arriving                                 | `services/event_manager.py`                                                  |
| Tracing / observability gap                                  | `services/tracing/`                                                          |
| Pre-commit hook failing                                      | `.pre-commit-config.yaml` — and **must use `uv run git commit`**             |
| Cross-platform flake                                         | Check `.github/workflows/cross-platform-test.yml` to see what's covered    |

## Tooling reminders

- `uv run pytest path::test`, never bare `pytest`.
- `uv run git commit`, never bare `git commit`.
- For sub-package tests: `uv sync --group dev --package <name>` first.
- `make format_backend` before staging fixes most ruff complaints.
