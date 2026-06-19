---
trigger: Any task that involves writing or modifying Python code in Langflow.
---

# Langflow data and tooling specifics

**Context:** The generic `developing-features` SKILL.md assumes a single-package Python project. Langflow is a `uv` workspace monorepo with multiple sub-packages and specific ORM/runtime conventions that diverge from the defaults.

**Lesson:**

- **`uv`, not pip or poetry.** Install / sync: `uv sync`. Run a Python command: `uv run python …`, `uv run pytest …`, `uv run git commit`. Bare `python` and `pip` may resolve to the wrong interpreter or skip the workspace.
- **Sub-package dev sync.** When testing inside a sub-package (`langflow-base`, `lfx`, a bundle), run `uv sync --group dev --package <name>` first. The top-level `uv sync` does not pull dev-only deps (`fakeredis`, etc.) for sub-packages, and tests fail with confusing import errors.
- **SQLModel, not raw SQLAlchemy.** The ORM combines Pydantic validation with SQLAlchemy persistence. Model classes define both schema AND validation in one place. Don't import `sqlalchemy.orm` directly when a SQLModel-equivalent exists.
- **`lfx` is a separate package** holding the graph execution engine. Code in `src/backend/base/langflow/graph/` is **thin wrappers** around `lfx.graph`. Heavy graph logic lives in `src/lfx/src/lfx/graph/`. Search both when looking for graph behavior.
- **Service layer mediates DB access.** Repositories and services in `src/backend/base/langflow/services/` are the contract; do not import `database.session` directly from business logic.
- **`structlog` + `loguru` for logging.** Look at how nearby code logs before introducing a new pattern.
- **Encrypted variables.** Secrets at rest go through `services/variable/` (encryption). Never store an API key as a plain string.
- **Custom code execution.** `langflow.custom.validate` validates user-supplied component code. There's no full sandbox — user code runs in-process. Reviewers and authors must treat this as a high-risk area.

**Why:** Generic Python rules (`pip install`, `pytest`, direct SQLAlchemy use) silently produce wrong results in this repo. The conventions are documented in `AGENTS.md` but generic skills don't know about them until told.

**Apply when:** Any change to `src/backend/**`, any test against backend modules, any addition to dependencies, any DB interaction, any logging or secret handling.

## Cross-references

- `developing-features/references/security.md` — applies as-is, but the "Custom code execution" risk is amplified in Langflow because `langflow.custom` lets users run Python.
- `developing-features/references/file-structure.md` — file-structure hard limits apply, but the **mandatory separation by responsibility** table (`validation`/`formatting`/`parsing`/`client`/`repository`) maps directly onto Langflow's existing layout (`helpers/`, `services/<client>/`, `services/<repo>/`).
