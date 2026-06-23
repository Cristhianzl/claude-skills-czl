# CLAUDE.md — baseline (Langflow build)

Single source of truth for AI coding agents in this Langflow repo. This is the **robust** baseline + the **Langflow-specific** rules. The baseline below is the short, actionable layer; `.claude/skills/` hold the detailed HOW (features, TDD, bug fixing, testing, review, PRs, docs, cross-platform, and **building-langflow-components**). Per-stack rules live in `.claude/rules/*.md` and auto-apply by `globs` (see `rules/langflow.md`). Reusable workflows live in `.claude/commands/`.

The project's `AGENTS.md` and the relevant `.agents/skills/` are canonical for area expertise — read them first; when they conflict with this file, the more specific one wins.

## ⚠️ Backward compatibility & portability — applies to EVERY change

This is the first thing to check on any Langflow change. It's **official Langflow policy** — see [`AGENTS.md`](https://github.com/langflow-ai/langflow/blob/main/AGENTS.md) and [docs.langflow.org/contributing-components](https://docs.langflow.org/contributing-components); full detail + citations in `rules/langflow.md`.

**Never break existing components or saved flows.** A saved flow is a detached copy that references components, inputs, and outputs **by name** (the frontend matches on the `type` = class name or the `name` attribute). Rename or remove one and you silently break every flow — and every user — that has it. Therefore:

- **Never rename** a Component class or its `name` attribute — *"breaks the component for all existing users."* If a new internal name is needed, mark the old one **`legacy=true`** and create a new component as a separate entity.
- **Never rename/remove `inputs[].name` / `outputs[].name`** (disconnects edges); mark fields **`deprecated`** and keep them in place. **Never remove methods/attributes from base classes** (e.g. `LCModelComponent`).
- **Additive-only** *(our convention)*: new inputs/outputs optional with safe defaults; never change a field's type or an existing default.
- **Removal needs a documented migration plan.** Deprecated/legacy components stay usable in old flows, hidden for new ones.
- **DB migrations must not lose data on upgrade** (upstream CI proves this end-to-end). *Our convention:* a `Phase: EXPAND | MIGRATE | CONTRACT` marker — expand first, contract later.
- **Bundle changelog (`BUNDLE_API.md`)** is a project/fork convention, **not** upstream — verify before relying on it.
- API/contract changes follow the same discipline — see `skills/api-design`.

**It must run everywhere.** Langflow's CI runs a real matrix — Linux + macOS + **Windows** × Python 3.10/3.12 ([`cross-platform-test.yml`](https://github.com/langflow-ai/langflow/blob/main/.github/workflows/cross-platform-test.yml)). Every change has to work across those OSes and across Langflow's run modes — **server, API (`/v1/run`), Docker, and the stateless `lfx` package** (`lfx serve`; no DB) — plus the `langflow-base` split. Therefore:

- The path / encoding / subprocess / time rules in `skills/ensuring-cross-platform` are mandatory — no POSIX-only assumptions, no hardcoded paths, `encoding="utf-8"`, no `shell=True`, UTC at boundaries.
- Code reachable from `lfx` or the API must not depend on a server/UI context (no server-only globals, no frontend, no interactive state).
- Reason about — and where feasible test — the change across OSes and the run modes it touches; CI runs the cross-platform matrix.

> Gate before merging any Langflow change: **"Could this break a saved flow or an existing component? Does it still run on Windows/Linux/Docker, via the API, and from `lfx`?"** If unsure → stop and verify.

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
6. Write prose answer-first — lead with the conclusion/recommendation, then grouped reasons, then detail (Minto Pyramid / SCQA). Applies to docs, PRDs, PR descriptions, reviews, and updates. (detail: `skills/documenting-features/references/communication.md`)

## Langflow

This repo is a Langflow monorepo (uv workspaces; `lfx` / `langflow-base` split; SQLModel; Components are the building blocks of every flow). The Langflow-specific rules — hook-enforced (`SecretStrInput`, no top-level SDK init, Alembic `Phase:` markers) and review-enforced (never rename a Component class, `BUNDLE_API.md` updated with bundle changes, `uv run` everywhere, real integrations over mocks) — live in **`rules/langflow.md`**. For creating/evolving Components, follow **`skills/building-langflow-components`**.

## Map of this configuration

- **`rules/`** — per-stack rules applied by `globs`: `langflow.md` (this repo's Python/component/migration rules) + `TEMPLATE.md` for adding more.
- **`commands/`** — `/init` `/next` `/check` `/test` `/review` `/done` `/commit` `/push` `/pr` `/roadmap` `/task` `/sync` `/security` `/help`.
- **`skills/`** — the detailed HOW, incl. **`building-langflow-components`**; the generic skills carry Langflow `learnings/`.
- **`hooks/`** — PostToolUse checks (comments, file size, banned patterns, **Langflow rules**), a `Stop` doc-sync check, and `pre-push-smoke.sh`.
