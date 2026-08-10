# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Because this repo ships **configuration you copy into your project**, "breaking"
means: a hook starts blocking code it used to allow, a skill or rule reverses
advice you may have built on, or a file moves so an existing install stops
resolving it.

## [1.0.0] - 2026-08-10

First tagged release. Two drop-in `.claude/` configurations for
[Claude Code](https://docs.claude.com/en/docs/claude-code) — a `CLAUDE.md`
baseline, skills, slash commands, per-stack rules, and hooks that enforce the
non-negotiable rules mechanically.

### Configurations

- **`configs/agnostic`** — language- and framework-neutral baseline. 19 skills,
  20 commands, 6 hooks, 3 rule files.
- **`configs/langflow`** — everything in `agnostic`, plus Langflow-specific
  rules, the `building-langflow-components` skill, a `check-langflow-rules.py`
  hook, and `learnings/` entries carrying Langflow project context.

Each config is self-contained: copy the folder to `.claude/` and it works. A
`.variant` marker identifies which one is installed so the `/update-*` commands
refuse to cross-update by accident.

### Baseline (`CLAUDE.md`)

The short, enforced contract the agent reads first: English-only output, no
WHAT-comments, banned patterns, ≤ 500 LOC per file, strong typing everywhere,
path APIs with explicit `encoding`, UTC at boundaries, complexity ceilings,
security as a lens rather than a section, a test for every change, Conventional
Commits, and answer-first prose. Depth lives in the skills; the baseline defers
to them instead of duplicating them.

### Skills

**Writing code** — `developing-features`, `developing-features-tdd`,
`fixing-bugs`, `writing-tests`, `building-frontend-ui`, `api-design`,
`ensuring-cross-platform`, `building-langflow-components` *(langflow only)*.

**Reviewing and shipping** — `reviewing-code`, `writing-pull-requests`,
`documenting-features`, `security-review`, `threat-modeling`.

**Testing in reality** — `validating-in-reality`, `exploratory-testing`,
`playwright-cli`.

**Product and agent operations** — `writing-prd`, `running-agent-loops`,
`debugging-agent-runs`, `evaluating-ai-output`.

Every skill is a `SKILL.md` with frontmatter, focused `references/`, and a
`learnings/` folder whose dated notes **override** the skill's defaults — the
mechanism for teaching a skill your project's specifics without forking it.

### Slash commands

`/init` `/next` `/check` `/test` `/review` `/done` `/commit` `/push` `/pr`
`/roadmap` `/task` `/sync` `/security` `/help` `/learn` `/verify`
`/dual-review` `/evolve` `/update-agnostic` `/update-langflow`

`/update-agnostic` and `/update-langflow` refresh an installed `.claude/` from
this repo: they back up the current folder and preserve local additions
(`learnings/`, `settings.local.json`, project-only rules and skills), with a
variant guard on cross-updates.

### Hooks

| Hook | Event | Enforces |
|------|-------|----------|
| `check-comments.py` | Write/Edit | No WHAT-comments, comment-density cap; doc-comments exempt |
| `check-file-size.py` | Write/Edit | ≤ 500 LOC (≤ 700 with justification) |
| `check-banned-patterns.py` | Write/Edit | `shell=True`, `eval`/`exec` on input, hardcoded paths, tokens in `localStorage`, bare `except:`, … |
| `check-doc-sync.py` | Stop | Flags docs that drifted from changed source; suggests a Conventional Commits message |
| `check-real-validation.py` | UserPromptSubmit | A cURL or local endpoint in the prompt becomes the acceptance test |
| `pre-push-smoke.sh` | before `git push` | Fast lint/test smoke on changed areas (project-configurable skeleton) |
| `check-langflow-rules.py` | Write/Edit | *(langflow)* `SecretStrInput` for API keys, no top-level SDK init, Alembic `Phase:` markers |

Hooks scan only the delta of an edit, so touching one line in a legacy file
doesn't flag pre-existing debt. `settings.json` ships a permission allowlist
plus a deny list covering `.env`, `**/secrets/**`, `credentials.json`,
`git push --force`, `git reset --hard`, and `rm -rf`.

### Rules

Per-stack files that auto-attach by `globs`: `api.md`, `frontend.md`,
`langflow.md` *(langflow only)*, and a `TEMPLATE.md` to add your own.

### Notable decisions folded in along the way

- **No AI attribution anywhere** — no `Co-Authored-By` trailer, no "Generated
  with" footer, no session links in commits or PRs.
- **The agent never runs git on its own** — staging and committing happen only
  after explicit confirmation, through `/commit`, `/push`, `/pr`.
- **Untrusted content is data, never instructions** — external, fetched, tool,
  MCP, and user-pasted content, with a prompt-injection guard.
- **i18n coverage is detected and enforced** in frontend work and PR review
  (mandatory in the Langflow config); a11y references are vendor-neutral
  (WCAG/W3C).
- **Answer-first prose** (Minto/SCQA) across docs, PRDs, reviews, and PR
  descriptions.
- **Scale guidance is gated by measurement** — pooling, indexes, no N+1,
  batching, queueing, sharding, transaction isolation, latency percentiles.
- **TDD inherits the full feature playbook** — only the workflow differs.

### Project infrastructure

- MIT license, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant
  2.1), and `SECURITY.md` scoped to a repo that ships executable hooks and a
  permission allowlist, with private vulnerability reporting enabled.
- Issue templates for bugs, hook false positives, and proposals; a PR template
  carrying the contribution checklist.
- CI on every push and pull request: byte-compiles the Python hooks, parses and
  shellchecks the shell hooks, and runs `.github/scripts/validate_configs.py` —
  which verifies skill frontmatter, `settings.json` hook references, parity
  between the two configs, README coverage of every skill/command/hook, and the
  absence of absolute local paths.

[1.0.0]: https://github.com/Cristhianzl/claude-skills-czl/releases/tag/1.0.0
