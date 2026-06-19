---
trigger: A bug involving a Langflow component, a flow execution, a database migration, or a backward-compat regression.
---

# Langflow debugging hotspots

**Context:** Bugs in Langflow cluster around predictable shapes — dynamic component discovery, the `lfx`/`langflow-base` split, the expand-contract migration policy, and the "renaming = breaking" rule. Knowing these saves you 30 minutes of grep.

**Lesson:**

- **Component discovery is dynamic.** Components are loaded by introspection from `src/backend/base/langflow/components/<provider>/`. There is no central registry to grep. If a component "disappears", the cause is almost always: (a) the class name was renamed (breaks every saved flow), (b) the file was moved without a `file_names_mapping` entry in the test, (c) the `__init__.py` of the provider folder is missing the export.
- **Class name == identity of the component in saved flows.** Never rename. Add a new class with the next-version name, mark the old one `deprecated = True`, keep the old class intact. Same rule for every `inputs[].name` and `outputs[].name`.
- **Graph behavior bugs are usually in `lfx`, not `langflow-base`.** The graph engine, vertex / edge classes, and execution loop live in `src/lfx/src/lfx/graph/`. Wrappers in `src/backend/base/langflow/graph/` are thin. Grep both.
- **Migrations follow expand-contract.** Every Alembic migration must declare `Phase: EXPAND | MIGRATE | CONTRACT` in the docstring; the pre-commit migration validator enforces it. A bug in a migration is almost always: (a) wrong phase label, (b) a column drop in an EXPAND phase, (c) data migration mixed with schema change.
- **Pre-commit needs `uv run git commit`.** Bare `git commit` finds the wrong Python and the hook fails with a misleading error.
- **Sub-package missing deps?** Run `uv sync --group dev --package <name>`. The default `uv sync` only resolves the top-level workspace.
- **"Bug" might be a flow JSON shape change.** Flow JSON is forward-compatible-by-convention; if a saved flow loads incorrectly on a new version, an input/output name probably changed somewhere. Grep the flow JSON for the literal name and trace back.
- **`@pytest.mark.api_key_required` skip + green CI** is a common false-positive: the test was authored, marked, and never actually ran on CI without the secret. Verify the env var is set in the CI workflow before declaring "covered".

**Why:** Several real Langflow incidents trace to these exact shapes. The TDD cycle catches the bug; this learning saves the half hour of grep that finds where the bug lives in the first place.

**Apply when:** Phase 1 (UNDERSTAND) of a bug-fix, when locating the root cause.

## Cross-references

- `reviewing-code/learnings/2026-05-27-langflow-review-blockers.md` — the same patterns surface as blockers during review.
- `fixing-bugs/references/cycle.md` § "exact error path rule" — apply with platform-suspect bugs (Windows / Docker / macOS).
