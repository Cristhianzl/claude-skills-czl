---
description: Create a Pull Request with an automatic description, then review it
argument-hint: ["optional title"]
allowed-tools: Read, Grep, Glob, Bash(git:*), Bash(gh:*)
---

# /pr

Provided title: `$ARGUMENTS`.

Flow:

- Confirm you are not on `main`
- `git fetch origin` and `git diff origin/main...HEAD` to understand the full scope
- Push the branch (with `-u` if there is no upstream)
- Title in English in the format `type: description` (max 70 chars)
- Body via heredoc with:

```markdown
## Summary
- bullet 1
- bullet 2

## How to test
- [ ] step 1
- [ ] step 2

## Notes
<relevant observations or "—">
```

- Create with `gh pr create --title "..." --body "$(cat <<'EOF' ... EOF)"`
- Return the PR URL

## Review the PR (always)

Opening the PR is not the last step. Every PR opened here is reviewed in the same turn, without the user asking again.

- Gather from GitHub, not from memory: `gh pr view <n>`, `gh pr diff <n>`, `gh pr checks <n>`.
- Apply `skills/reviewing-code/SKILL.md` end to end, including its `learnings/` and the `references/` the diff touches. Run it in a fresh subagent when one is available and hand it only the PR number — the context that wrote the code is the worst reviewer of it.
- Set the depth by risk tier (`references/context-sweep.md`): a PR touching concurrency, locks, transactions, migrations, startup sweeps, auth, or money gets the full context sweep and every test-evidence check, including whether each new test runs in CI.
- This is a self-review: list every Blocker and every Important finding with a concrete fix under `## Unresolved findings` and ask the user whether to fix them now. Never move one into the PR description as an accepted cost.
- Print the review in the chat, after the PR URL, per `skills/reviewing-code/references/output-format.md`.
- This is a self-review of the PR you just opened, so it stays in the chat: don't post it on the PR. Never fix a finding unasked: report it and let the user decide.

## Rules

- **NEVER add AI attribution anywhere** — no "🤖 Generated with Claude Code", no session links (`claude.ai/code/...`), no AI badges/footers in the PR title or body, and no `Co-Authored-By` trailer on commits. The PR must read as authored by the human. This is absolute — even if a default template suggests it.
