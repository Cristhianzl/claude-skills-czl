<!-- Title must be a conventional commit: feat: / fix: / docs: / refactor: / chore: -->

## What & why

<!-- What changes, and the motivation. Link the issue if there is one (Closes #123). -->

## Config(s) touched

- [ ] `configs/agnostic`
- [ ] `configs/langflow`
- [ ] Repo-level (README, CI, templates…)

## Checklist

- [ ] **English only** — code, comments, docs, and skill content.
- [ ] **Kept in sync** — if this changes a skill that exists in both configs, the other one got the same change (only `description` and `learnings/` are allowed to differ).
- [ ] **No local paths** — no `/Users/...` or `/home/...`; repo-relative or `$CLAUDE_PROJECT_DIR` only.
- [ ] **Baseline stayed short** — depth went into `skills/`, not into `CLAUDE.md`.
- [ ] **Agnostic stayed agnostic** — stack-specific content went to `rules/<stack>.md` or `configs/langflow`.
- [ ] **New hook** is wired in that config's `settings.json` and compiles (`python3 -m py_compile` / `bash -n`).
- [ ] **New skill** has a `SKILL.md` with a clear `description`.
- [ ] **`README.md` updated** if a skill, command, or hook was added or removed.
- [ ] **No AI attribution** — no `Co-Authored-By` trailer, no "Generated with" footer, no session links.

## How it was verified

<!-- e.g. ran the hook against a file that should trip it and one that shouldn't; installed the config in a real project and ran the command. -->
