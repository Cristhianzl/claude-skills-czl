---
description: Langflow — component, security, migration, and workflow rules specific to this repo
globs: "**/*.py"
---

# Langflow

> Prerequisite: `CLAUDE.md` (general baseline). Depth: `skills/building-langflow-components`, `skills/developing-features`.
>
> **Official Langflow guidance is the source of truth — read it first, don't reinvent it:**
> [`AGENTS.md`](https://github.com/langflow-ai/langflow/blob/main/AGENTS.md) ·
> [Contribute components](https://docs.langflow.org/contributing-components) ·
> [Custom components](https://docs.langflow.org/components-custom-components) ·
> [Components overview](https://docs.langflow.org/concepts-components) ·
> [DEVELOPMENT.md](https://github.com/langflow-ai/langflow/blob/main/DEVELOPMENT.md).
> Sections below are tagged **[official]** (summarizing those sources) or **[ours]** (our convention on top).

## Backward compatibility — never break old components or flows

**[official]** A saved flow is a detached copy that references components, inputs, and outputs **by name** — the frontend matches on the `type` (the class name or the `name` attribute). Per [Contribute components](https://docs.langflow.org/contributing-components):

- **Never rename a Component class or its `name` attribute** — *"Changing the class name or the `name` attribute breaks the component for all existing users."* If a new internal name is needed, **mark the old one `legacy=true` and create a new component** as a separate entity.
- **Never rename or remove `inputs[].name` / `outputs[].name`** — *"Removing fields or outputs can cause edges to disconnect."* Mark fields `deprecated` and keep them in the same location.
- **Never remove methods or attributes from base classes** (e.g. `LCModelComponent`).
- **Removal needs a documented migration plan.** Legacy components stay usable in existing flows but are hidden for new ones ([legacy components](https://docs.langflow.org/legacy-core-components)).
- Flows freeze the component version/state at insert time, so old flows keep working — another reason additive evolution matters ([concepts-components](https://docs.langflow.org/concepts-components)).

**[ours]** Add new inputs/outputs as **optional with safe defaults**; never change a field's type or an existing default. API/contract changes follow the same discipline — see `skills/api-design`.

## Database migrations

**[official]** Schema is managed with Alembic (`uv run langflow migration --fix` applies). PostgreSQL 15+ in production. Upgrades **must not lose data** — Langflow's CI proves this end-to-end (`.github/workflows/db-migration-validation.yml`: upgrade with witness data, confirm no loss across pip + Docker).

**[ours]** New migrations declare a `Phase: EXPAND | MIGRATE | CONTRACT` marker (enforced by our hook): expand first, contract only once nothing uses the old shape, so rollbacks stay safe. This is our convention layered on top of the upstream data-preservation guarantee — Langflow itself doesn't require the marker.

## Portability — it must run everywhere

**[official]** Langflow's CI runs a real matrix — **Linux + macOS (Intel/ARM) + Windows × Python 3.10/3.12** ([`.github/workflows/cross-platform-test.yml`](https://github.com/langflow-ai/langflow/blob/main/.github/workflows/cross-platform-test.yml)); supported Python 3.10–3.14. A change must also work across Langflow's run modes: **server** (`langflow run`), **API** (`POST /v1/run/{flow}`), **Docker** image, and the **`lfx`** package (`lfx serve`). LFX is **stateless** — no DB, a `NoopSession` ([`src/lfx/README.md`](https://github.com/langflow-ai/langflow/blob/main/src/lfx/README.md)).

**[ours]** Follow `skills/ensuring-cross-platform`: `pathlib` paths, `encoding="utf-8"`, no `shell=True`, no hardcoded `/tmp`/`C:\` paths, UTC at boundaries. Code reachable from `lfx`/API must not assume a DB, server-only globals, the frontend, or interactive state (LFX is stateless).

## Hook-enforced (`hooks/check-langflow-rules.py`)

- **API keys use `SecretStrInput`**, never `MessageTextInput`. *(Idiomatic in the codebase — `SecretStrInput` is the canonical secret field everywhere — though not stated as a rule on the docs site. Docs-level secret handling is global variables, Credential type + DB-encrypted, and env vars: [global variables](https://docs.langflow.org/configuration-global-variables).)*
- **No top-level SDK instantiation in component modules** — no `client = openai.OpenAI()` at module top; instantiate inside the output `method` (lazy import + lazy init). *(Our convention, aligned with Langflow's `_pre_run_setup()` / lazy-load patterns; not an explicit upstream rule.)*
- **Alembic migrations declare `Phase:`** (see Database migrations above).

## Tooling & tests

**[official]** `uv run` for **every** Python invocation — `uv run pytest`, `uv run ruff`, and **`uv run git commit`** (pre-commit hooks live in the workspace venv). `make init` sets up deps + hooks; `make format` (ruff/biome) then `make lint` (ruff + **mypy**); `make unit_tests`. **Prefer real integrations over mocks** — *"Avoid mocking in tests when possible."* Semantic/conventional commit titles; target the release-candidate branch.

## Context to read first

- `AGENTS.md` (canonical) and the relevant `.agents/skills/` for area expertise, before any non-trivial work.
- New components → `skills/building-langflow-components`. Placement (current layout): components live under `lfx`, e.g. `src/lfx/src/lfx/components/<provider>/`; bundles under `src/bundles/<bundle>/`.

> **`BUNDLE_API.md` / bundle changelog gate:** this is a **project/fork convention** (used in this repo's workflow), **not** part of upstream Langflow — verify it still applies before relying on it.
