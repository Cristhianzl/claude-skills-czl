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
5. Open a PR with a conventional-commit title (`feat:`, `fix:`, `docs:`, …) and a short description of the motivation.

## Reporting issues

Open an issue describing the project type, what you expected, and what happened. For a hook false positive, include the file and the message the hook printed.
