# CLAUDE.md — baseline (Langflow build)

Single source of truth for AI coding agents in this Langflow repo. This is the **robust** baseline + the **Langflow-specific** rules. The baseline below is the short, actionable layer; `.claude/skills/` hold the detailed HOW (features, TDD, bug fixing, testing, review, PRs, docs, cross-platform, and **building-langflow-components**). Per-stack rules live in `.claude/rules/*.md` and auto-apply by `globs` (see `rules/langflow.md`). Reusable workflows live in `.claude/commands/`.

The project's `AGENTS.md` and the relevant `.agents/skills/` are canonical for area expertise — read them first; when they conflict with this file, the more specific one wins.

## Language

All code, comments, commit messages, and documentation in English, regardless of conversation language.

## Code style

1. **No WHAT-comments.** Zero by default; only a one-line WHY when the reason is non-obvious. No section dividers. (detail: `skills/developing-features`)
2. **No banned patterns.** `shell=True`, `: any` / `as any`, `open(...)` without `encoding=`, `datetime.now()` without timezone, hardcoded `/tmp` / `/var` / `~/.config` / `C:\`, `console.log` / `print()` in production, `os.fork`, `eval`/`exec` on dynamic input, `dangerouslySetInnerHTML`, bare `except:`, tokens in `localStorage`.
3. **File size** ≤ 500 LOC of real code per file (500–700 only when SRP holds; > 700 blocks).
4. **Strong typing always** — no `any` / `object` / `dynamic`; type every public signature.
5. **Path APIs only** (`pathlib` / `path.join`), `encoding="utf-8"` on all text I/O. (detail: `skills/ensuring-cross-platform`)
6. **Time in UTC at boundaries**; convert to local only at presentation.
7. **Complexity** — cyclomatic ≤ 10, nesting ≤ 4 per function; small functions, single responsibility.

## Security

A lens, not a section. Validate/sanitize external inputs; parameterized queries; secrets from env/secret manager, never committed; least privilege; auth checked server-side. In Langflow: **API keys use `SecretStrInput`** and **no top-level SDK instantiation in components** (see `rules/langflow.md`). (detail: `skills/developing-features/references/security.md`)

## Tests

All new code has a test — function: success + error; endpoint: success + auth + validation; bug fix: a failing test that reproduces it first; refactor: existing tests still pass. Arrange-Act-Assert, testing pyramid, branch-coverage gate. **Prefer real integrations over mocks** (Langflow) — mock only failure modes a real sandbox cannot reproduce. (detail: `skills/writing-tests`, `skills/fixing-bugs`, `skills/developing-features-tdd`)

## Commits & git

This Langflow repo is **human-driven on git** and that overrides the generic agent-commits stance:

- The agent **never runs `git commit` / `git add` / `git push`** — it prepares and prints the message; the human commits. Never add `Co-Authored-By`.
- Commits go through **`uv run git commit`** — and `uv run` wraps **every** Python invocation (`uv run pytest`, `uv run ruff`), because pre-commit hooks need the workspace venv.
- Conventional format `type: short description` (subject ≤ 50 chars, imperative, no trailing period, English). Before committing: lint + tests green (`uv run`), no `.env`/credentials in the diff.

The `/commit`, `/push`, `/pr` commands stay available for the human to drive. (detail: `skills/writing-pull-requests`)

## Workflow

1. Read the file before editing; check for existing similar code first (Grep).
2. Read the relevant skill (`SKILL.md` + `learnings/`), plus `AGENTS.md` and the matching `.agents/skills/`, before generating.
3. Follow the matching `rules/<area>.md` (`rules/langflow.md` auto-applies to Python).
4. Write/update tests alongside the code; run lint + tests locally via `uv run`.
5. State assumptions when ambiguous; surface tradeoffs instead of burying them.

## Langflow

This repo is a Langflow monorepo (uv workspaces; `lfx` / `langflow-base` split; SQLModel; Components are the building blocks of every flow). The Langflow-specific rules — hook-enforced (`SecretStrInput`, no top-level SDK init, Alembic `Phase:` markers) and review-enforced (never rename a Component class, `BUNDLE_API.md` updated with bundle changes, `uv run` everywhere, real integrations over mocks) — live in **`rules/langflow.md`**. For creating/evolving Components, follow **`skills/building-langflow-components`**.

## Map of this configuration

- **`rules/`** — per-stack rules applied by `globs`: `langflow.md` (this repo's Python/component/migration rules) + `TEMPLATE.md` for adding more.
- **`commands/`** — `/init` `/next` `/check` `/test` `/review` `/done` `/commit` `/push` `/pr` `/roadmap` `/task` `/sync` `/security` `/help`.
- **`skills/`** — the detailed HOW, incl. **`building-langflow-components`**; the generic skills carry Langflow `learnings/`.
- **`hooks/`** — PostToolUse checks (comments, file size, banned patterns, **Langflow rules**), a `Stop` doc-sync check, and `pre-push-smoke.sh`.
