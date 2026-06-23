# claude-skills-czl

> Battle-tested [Claude Code](https://docs.claude.com/en/docs/claude-code) configurations — opinionated `CLAUDE.md` baselines, **skills**, **slash commands**, and **enforcement hooks** you drop into any project so the AI follows your engineering standards by default.

Stop re-explaining your standards every session. Drop a config into your project's `.claude/` folder and the agent already knows your rules for code style, security, testing, commits, and docs — and the hooks **enforce** the non-negotiable ones mechanically.

## What's in here

Two ready-to-use configurations:

| Config | Use it when | Highlights |
|--------|-------------|------------|
| [`configs/agnostic`](configs/agnostic) | **Any project, any language** | A clean, language-agnostic baseline. Nothing assumes a stack; the hooks never fight a language's idioms. |
| [`configs/langflow`](configs/langflow) | Working in the **Langflow** codebase | Everything in `agnostic`, plus Langflow-specific rules, a `building-langflow-components` skill, and a hook that enforces Langflow conventions. |

Both are **self-contained** — each is a complete `.claude/` folder.

## Repository layout

```
claude-skills-czl/
├── configs/
│   ├── agnostic/            # generic, language-agnostic config
│   │   ├── CLAUDE.md            # the short, enforced baseline
│   │   ├── settings.json        # registers the hooks + permissions
│   │   ├── commands/            # slash commands (/check, /done, /pr, …)
│   │   ├── hooks/               # PostToolUse / Stop / PreToolUse checks
│   │   ├── rules/               # optional per-stack rules (auto-applied by globs)
│   │   └── skills/              # the detailed "how" playbooks
│   └── langflow/            # same shape, specialized for Langflow
├── legacy/                 # earlier iterations, kept for reference
└── README.md
```

## What a config contains

Every config is a drop-in `.claude/` folder made of five parts:

- **`CLAUDE.md`** — the single source of truth: a short, actionable baseline (code style, security, tests, commits, workflow). It's the *what*; it defers to the skills for the *how*.
- **`skills/`** — detailed, self-contained playbooks the agent reads before a matching task. Each has a `SKILL.md`, `references/`, and a `learnings/` folder for project-specific knowledge that accumulates over time.
- **`commands/`** — slash commands for the recurring workflow (start a session, run checks, review a diff, open a PR…).
- **`hooks/`** — Python/shell scripts wired via `settings.json` that run automatically and **block** on violations.
- **`rules/`** — optional per-stack rule files that auto-attach by file `globs` (e.g. only on `**/*.py`). Copy `TEMPLATE.md` to add your own.

### Skills

| Skill | What it covers |
|-------|----------------|
| `developing-features` | Production code: security-first, SOLID, pragmatic principles, observability, file-structure limits |
| `developing-features-tdd` | Strict red-green-refactor TDD for new features |
| `fixing-bugs` | Reproduce-first bug fixing (failing test before the fix) |
| `writing-tests` | Testing pyramid, AAA, naming, coverage gate |
| `reviewing-code` | Severity-labeled PR review with an action checklist + correctness lenses (enum/state-machine completeness, control-flow exceptions, degrade-don't-crash) |
| `writing-pull-requests` | Conventional-commit PR titles, messages, descriptions |
| `documenting-features` | Living, DDD-aligned feature docs (ADRs, C4, Gherkin) |
| `ensuring-cross-platform` | Linux/macOS/Windows portability rules |
| `playwright-cli` | Browser automation & E2E testing with Playwright |
| `building-frontend-ui` | Framework-agnostic frontend UI — reuse & design tokens, components, accessibility, forms, state & data, responsive, performance, client security/PII (with per-framework references for React/Vue/Svelte/Web Components) |
| `building-langflow-components` | *(Langflow only)* Create and evolve Langflow components safely |
| `exploratory-testing` | Structured manual/exploratory testing — charters, time-boxed sessions, heuristics & oracles, solid bug reports |
| `writing-prd` | Product requirements — PRDs, one-pagers, PR-FAQs; problem-first, testable metrics, explicit non-goals |
| `api-design` | Contract-first, resource-oriented, backward-compatible, secure-by-default HTTP/REST APIs (with REST/GraphQL/gRPC guidance) |
| `threat-modeling` | Security design analysis — data-flow diagrams & trust boundaries, STRIDE, abuse cases, threats → controls → tests |

### Commands

`/init` · `/next` · `/check` · `/test` · `/review` · `/done` · `/commit` · `/push` · `/pr` · `/roadmap` · `/task` · `/sync` · `/security` · `/help`

### Hooks (what gets enforced)

| Hook | Event | Enforces |
|------|-------|----------|
| `check-comments.py` | on Write/Edit | No WHAT-comments; comment-density cap; doc-comments (`///`, `//!`) exempt |
| `check-file-size.py` | on Write/Edit | ≤ 500 LOC per file (≤ 700 with justification) |
| `check-banned-patterns.py` | on Write/Edit | `shell=True`, `eval`/`exec` on input, hardcoded paths, tokens in `localStorage`, bare `except:`, … |
| `check-doc-sync.py` | on Stop (turn end) | When you changed source: flags repo docs that may have drifted (so you don't have to ask), then suggests a Conventional-Commits message for the change — human commits, agent never runs git |
| `pre-push-smoke.sh` | before `git push` | Fast lint/test smoke on changed areas (project-configurable skeleton) |
| `check-langflow-rules.py` | on Write/Edit | *(Langflow only)* `SecretStrInput` for API keys, no top-level SDK init in components, Alembic `Phase:` markers |

## Quick start

> **The whole setup is: copy one config folder into your project, rename it to `.claude`, and git-ignore it.** That's it — Claude Code reads `.claude/` automatically.

**1. Copy a config into your project as `.claude/`** (this both copies and renames):

```bash
# from the root of YOUR project — pick agnostic (any language) or langflow
cp -R /path/to/claude-skills-czl/configs/agnostic .claude
```

Use `configs/langflow` instead when working inside the Langflow codebase.

**2. Git-ignore it** so your project repo doesn't track it:

```bash
echo ".claude/" >> .gitignore
```

**3. Done.** Open the project in Claude Code — the `CLAUDE.md` baseline, skills, commands, and hooks are active. (Want the whole team to share these rules instead of keeping them local? Skip step 2 and commit `.claude/`.)

### Keep it in sync (optional)

Prefer a **symlink** instead of a copy if you want updates to this repo to flow through automatically:

```bash
# from the root of YOUR project
ln -sfn /path/to/claude-skills-czl/configs/agnostic .claude
echo ".claude" >> .gitignore
```

### Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code)
- `python3` (the enforcement hooks)
- `jq` (used by a couple of hooks)
- `git` (the doc-sync and pre-push hooks)

## Customize

- **Add per-stack rules:** copy `rules/TEMPLATE.md` to `rules/<stack>.md`, set its `globs`, keep it short, and point to the skills for depth.
- **Teach the agent project specifics:** drop a dated note in any skill's `learnings/` folder. A learning overrides the skill's defaults — the agent reads it first.
- **Tune the hooks:** they're small, dependency-free scripts; the thresholds live at the top of each file.

## `legacy/`

Earlier iterations of these configs, kept for reference and history. Not maintained — start from `configs/`.

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). All content (code, comments, docs, skills) is in **English**.

## License

[MIT](LICENSE) © Cristhian Zanforlin
