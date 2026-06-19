---
trigger: Any PR or commit task in /Users/criszl/Documents/langflow.
---

# Langflow project context

**Context:** Writing a PR for Langflow — `uv` workspace monorepo with backend, frontend, `lfx`, bundles, and a Docusaurus docs site. Multiple `pyproject.toml`s; version bumps go through `make patch v=X.Y.Z`.

**Lesson:** Treat `AGENTS.md` at the repo root as canonical. It explicitly says:

> Follow semantic commit conventions. Reference any issues fixed (e.g., `Fixes #1234`). Ensure all tests pass before submitting.

The generic SKILL.md's conventional-commit format aligns with Langflow's policy. Additional rules:

- **`Fixes #N` is allowed and desired in PR descriptions** (closes the issue on merge). This is the **opposite** of the generic SKILL.md's "never use `Fixes #N`" warning — which applies to **review comments**, not PR descriptions.
- **Use `uv run git commit`**, never bare `git commit`. The pre-commit hooks need the right Python interpreter.
- **Version bumps**: `make patch v=X.Y.Z` updates `pyproject.toml`, `src/backend/base/pyproject.toml`, and `src/frontend/package.json` atomically. Don't edit them by hand.

**Why:** Langflow has conventions that look like exceptions to the generic SKILL.md but are project-correct. Ignoring them produces PRs that get bounced.

**Apply when:** Always, on any PR / commit task in this repo.

## Title and description checklist

The generic SKILL.md gives the format (`type(scope): Summary`). Langflow specifics:

- **Scope is usually a Langflow area:** `auth`, `components`, `graph`, `api`, `frontend`, `bundles/<name>`, `lfx`, `docs`, `ci`.
- **`Fixes #N` in the description** (not the title) closes the issue.
- **No emojis** in the title.
- **No `Co-Authored-By: Claude` trailer** — per the user's durable preference, AND because Langflow's commit history doesn't carry this.

## Special PR shapes

| PR touches…                                       | Required extras in description                                             |
|---------------------------------------------------|----------------------------------------------------------------------------|
| A new or modified Component                        | Note in `## Notes`: "Component class name unchanged" OR "Adds new class `<X>` to replace deprecated `<Y>`" |
| A bundle                                          | "`BUNDLE_API.md` updated" — and it actually must be                        |
| A migration                                       | "Phase: EXPAND/MIGRATE/CONTRACT" — match the migration docstring          |
| AI/LLM integration                                | "AI Runtime" section with timeout, fallback, kill switch, SLO              |
| Frontend with new icon                            | "Icon added to `lazyIconImports.ts` for key `<X>`"                         |
| Breaking change                                    | `feat(scope)!:` or `fix(scope)!:` and a `## Notes` line with the migration path |
| Cross-platform fix                                 | "Verified on Ubuntu / macOS / Windows" (link CI run if helpful)           |

## Commit hygiene

- `make format_backend` before staging.
- `uv run git commit` to invoke pre-commit hooks.
- One logical change per commit. Slice-then-refactor commits are encouraged (see `developing-features-tdd/references/checklist.md`).
- Reference the issue in the **commit body** or the **PR description**, not the title.
