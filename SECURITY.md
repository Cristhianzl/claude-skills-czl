# Security Policy

## What this repo ships

These configs are **not a library you import** — they are files Claude Code reads and executes on your machine:

- `hooks/` — Python and shell scripts that run automatically on tool use, on turn end, and before `git push`.
- `settings.json` — a permission allowlist that decides which commands the agent may run without asking.
- `CLAUDE.md`, `skills/`, `commands/`, `rules/` — instructions the agent follows.

A vulnerability here means a config could cause the agent to run something you didn't intend, leak data outside the project, or weaken a protection you were relying on. Treat a config the way you'd treat a shell script from the internet: read it before you install it.

## Reporting a vulnerability

**Do not open a public issue.** Use one of:

- GitHub → the repo's **Security** tab → **Report a vulnerability** (private advisory), or
- Email **cristhian.lousa@gmail.com** with `SECURITY` in the subject.

Please include the config (`agnostic` / `langflow`), the file and line, what an attacker or a careless prompt could cause, and a reproduction if you have one.

You'll get an acknowledgement within **5 days** and a fix or a decision within **30 days**. Fixes land on `main`; the advisory is published once the fix is out. Credit is given unless you'd rather stay anonymous.

## In scope

- A hook that can be made to execute attacker-controlled input, or that can be trivially bypassed while still reporting success.
- A `settings.json` `allow` entry broad enough to permit a destructive or exfiltrating command, or a `deny` entry that doesn't actually block what it claims to.
- Instructions in `CLAUDE.md`, a skill, a command, or a rule that steer the agent into leaking secrets, disabling a safety check, or running an unreviewed remote script.
- A `/update-*` command flow that could overwrite files outside `.claude/` or restore a backup from an untrusted path.
- Any secret, token, or private path committed to this repo.

## Out of scope

- Vulnerabilities in Claude Code, the Anthropic API, or Langflow — report those to their own maintainers.
- Vulnerabilities in *your* project that the agent failed to catch. These configs raise the floor; they are not a security control and do not replace review, CI, or a scanner.
- A hook false positive or false negative on a code-quality rule (comments, file size, banned patterns). That's a bug — open a normal issue.
- Any risk that requires an attacker who already has write access to your `.claude/` directory or your shell.

## Hardening notes for users

- **Review `settings.json` before installing.** `defaultMode` is `acceptEdits` and the allowlist includes `git commit`, `git push`, `gh`, `npm`, and `npx`. That's a deliberate tradeoff for speed — narrow it if your threat model is stricter.
- **Keep the `deny` list.** It blocks reading and writing `.env` files, `**/secrets/**`, and `credentials.json`, plus `git push --force`, `git reset --hard`, and `rm -rf`.
- **Prefer copying over symlinking** if the config lives in a directory other people can write to.
- **Pin what you install.** If you copy from `main`, you get whatever `main` says today; check the diff when you re-run `/update-agnostic` or `/update-langflow`.
