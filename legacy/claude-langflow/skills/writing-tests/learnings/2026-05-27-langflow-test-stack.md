---
trigger: Writing any test against backend code, component code, or graph code in Langflow.
---

# Langflow test stack — overrides for the generic SKILL.md

**Context:** The generic `writing-tests` SKILL.md is framework-agnostic and assumes a single Python project. Langflow's stack has specific conventions that override several defaults.

**Lesson:**

- **Prefer real integrations over mocks** (from `AGENTS.md`). Mock only the failure modes the real service / sandbox can't reproduce.
- **Component tests use base classes**, not bare `pytest`. Pick:
  - `ComponentTestBaseWithoutClient` — pure-logic components.
  - `ComponentTestBaseWithClient` — components needing the backend client (file uploads, vector stores, etc.).
  - Both require fixtures: `component_class`, `default_kwargs`, `file_names_mapping` (return `{}` if no rename history).
- **Graph test pattern** (from `AGENTS.md`):
  1. Build graph with connected components.
  2. Connect via `.set()` calls.
  3. Call `async_start` and iterate over results.
  4. Validate results.
- **Mandatory marks:**
  - `@pytest.mark.api_key_required` — needs an env-var secret; CI provides it.
  - `@pytest.mark.no_blockbuster` — skip when blockbuster plugin is active.
- **Run with `uv run pytest …`**, never bare `pytest`. Pre-commit needs `uv run git commit`.
- **Sub-package testing:** `uv sync --group dev --package <name>` before the first run.
- **Database tests** may pass individually and fail in batch — known flakiness around shared state. Investigate with `pytest --shuffle` if a test starts failing only in CI.
- **Frontend tests** use `jest` (NOT Vitest) for unit tests and `playwright` for e2e. There are templates and patterns under `.agents/skills/frontend-testing/`.

**Why:** The generic SKILL.md describes the universal AAA pattern and the 8 anti-patterns; those still apply. This learning overlays Langflow's specific stack and required fixtures so tests integrate with the suite instead of fighting it.

**Apply when:** Any test creation or modification under `src/backend/tests/` or `src/frontend/src/`.

## Cross-references

- `writing-tests/references/pre-commit.md` — the 8-step pre-commit applies; substitute `uv run pytest` for bare `pytest`.
- `writing-tests/references/multi-platform.md` — Langflow's matrix is in `.github/workflows/cross-platform-test.yml` (Ubuntu, macOS Intel + ARM, Windows).
- `building-langflow-components/references/testing.md` — the deep-dive on `ComponentTestBase*` with concrete examples.
- Langflow's own `.agents/skills/frontend-testing/` for the React side — has templates ready to copy.
