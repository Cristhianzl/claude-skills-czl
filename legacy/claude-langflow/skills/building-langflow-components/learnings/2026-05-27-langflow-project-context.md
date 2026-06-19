---
trigger: Any task creating or evolving a Langflow Component.
---

# Langflow project context

**Context:** This skill builds Components in Langflow — `uv` workspace monorepo, Python 3.10-3.13 backend, React 19 frontend with custom icon system. `AGENTS.md` at the repo root is the canonical conventions doc.

**Lesson:** Langflow ships its own specialty skills that complement this one. Read them when applicable:

- `.agents/skills/component-refactoring/SKILL.md` — for refactoring an existing component (vs creating new).
- `.agents/skills/backend-code-review/SKILL.md` — the review lens that will be applied to your PR.
- `.agents/skills/frontend-testing/SKILL.md` — for testing the icon and any frontend-side wiring.

**Why:** Creating a new component is **this** skill's scope. Refactoring an existing one has different concerns (preserving the class name, the `file_names_mapping` rename trail, deprecation flags) that Langflow's own skill covers in depth.

**Apply when:** Always, first action when creating or evolving a Langflow Component.

## Where components live by intent

- **Top-N providers and broadly useful tools** → `src/backend/base/langflow/components/<provider>/`. These are shipped with `langflow-base`.
- **Niche, partner-maintained, ecosystem-specific** → `src/bundles/<bundle_name>/src/lfx_<bundle>/components/<provider>/`. Each bundle has its own `pyproject.toml` and **`BUNDLE_API.md`** (changelog gate enforced).
- **Throwaway / experiments** → behind `LFX_DEV=<my_name> make backend`; never enter `__init__.py`.

## The non-negotiable that overrides everything

From `AGENTS.md`:

> Changing a component's class name is a breaking change and should never be done. The class name serves as an identifier used to match components in saved flows and to flag them for updates in the UI. Renaming it will break existing flows that use that component.

Same for `inputs[].name` and `outputs[].name`. **Plan the names carefully up front** — they are forever.

## Tooling reminders

- `uv run pytest`, `uv run git commit`.
- `LFX_DEV=1 make backend` for hot-reload of all components.
- `LFX_DEV=acme,openai make backend` to scope hot-reload to specific providers.
- Pre-commit runs ruff + biome + migration validator automatically.
