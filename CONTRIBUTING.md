# Contributing

Thanks for helping improve these configurations! Contributions of new skills, rules, commands, hooks, and fixes are welcome.

## Ground rules

- **English only** — all code, comments, documentation, and skill content.
- **Keep the baseline short.** `CLAUDE.md` is the actionable summary; depth belongs in `skills/`. Don't duplicate a skill's content into `CLAUDE.md`.
- **Stay language-agnostic in `configs/agnostic`.** Anything stack-specific goes in a `rules/<stack>.md` (gated by `globs`) or in a dedicated config like `configs/langflow`.
- **Follow the rules the configs preach.** No WHAT-comments, strong typing, files ≤ 500 LOC, path APIs, UTC at boundaries — the hooks in each config enforce these on themselves too.

## Project layout

- `configs/agnostic` — the generic baseline. Changes here should help *every* project.
- `configs/langflow` — the Langflow-specialized config. Langflow-only changes go here.

When you change a skill in one config, check whether the same skill exists in the other and keep them in sync (the generic skill bodies are shared; only `description` and `learnings/` differ).

## Making a change

1. Edit the relevant config under `configs/`.
2. If you add a hook, wire it in that config's `settings.json` and make sure it `python3 -m py_compile`s (or `bash -n`s) cleanly.
3. If you add a skill, give it a `SKILL.md` with a clear `description`, and keep `references/` focused.
4. Update `README.md` if you added a skill, command, or hook.
5. Run the checks below — they're the same ones CI runs.
6. Open a PR with a conventional-commit title (`feat:`, `fix:`, `docs:`, …) and a short description of the motivation. The PR template's checklist is the review bar.

## Before you open the PR

```bash
python3 .github/scripts/validate_configs.py            # structure, parity, README coverage, no local paths
find configs -name '*.py' -print0 | xargs -0 python3 -m py_compile
find configs -name '*.sh' -print0 | xargs -0 -n1 bash -n
```

`validate_configs.py` enforces mechanically what this document asks for: every `SKILL.md` has frontmatter whose `name` matches its directory, `settings.json` is valid JSON and only references hooks that exist, every skill and command in `agnostic` also exists in `langflow`, every skill/command/hook is documented in `README.md`, and no file carries an absolute local path (`/Users/...`, `/home/...`).

## Reporting issues

Use the [issue templates](https://github.com/Cristhianzl/claude-skills-czl/issues/new/choose) — bug, hook false positive, or a proposal for a new skill/command/rule/hook. For a hook false positive, include the snippet, the message the hook printed, and what you expected instead.

**Security vulnerabilities go through [SECURITY.md](SECURITY.md), not the issue tracker.**
