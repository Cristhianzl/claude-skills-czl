---
description: What this configuration does and how to drive it
---

# /help

Print this, adapted to what the user asked:

**This `.claude/` reviews pull requests. It does nothing else** — it cannot edit files, commit,
or push, and the only thing it can write on GitHub is the review you asked for. Everything else is blocked by `settings.json` and `hooks/block-mutations.sh`.

| Command | What it does |
|---------|--------------|
| `/review [base]` | Reviews the working tree, the staged diff, or the branch against `base`. |
| `/review-pr <n>` | Reviews GitHub PR number `n` via `gh`. |
| `/dual-review` | Two independent reviewers on the same diff, then converge. Both must approve. |
| `/help` | This message. |

**The ruleset** lives in `skills/reviewing-code/`: `SKILL.md` is the workflow and the severity
model; `references/` holds the depth — `context-sweep.md`, `test-evidence-checks.md`, `security-checks.md`, `web-security-checks.md`, `pr-pentest.md`, `structural-checks.md`,
`correctness-checks.md`, `grep-recipes.md`, `output-format.md`, `checklist.md`.

**To teach it your project:** drop a dated note in `skills/reviewing-code/learnings/`. A learning
overrides the defaults — the agent reads it first. That's where project-specific severity
adjustments, banned patterns, and recurring violations belong.

**The output is a GitHub review on the PR** — short inline comments on the changed lines, each starting with `**Blocker:**`, `**Important:**`, `**Recommended:**`, or `**Nit:**`, plus a brief summary of what was checked and the verdict. It is posted as a plain comment review; it approves or requests changes only when you ask. Your own PRs are never commented on — their review comes in the chat. `/review` (no PR) gives the same shape in the chat.
