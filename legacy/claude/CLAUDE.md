# Hard rules — apply on every action

These rules are enforced by PostToolUse hooks in `.claude/hooks/`. A violation will fail the Write/Edit tool call with an error explaining what to fix. Treat these as inviolable defaults; the only way to "skip" one is to redesign the code so the rule no longer applies.

## Code style

1. **No WHAT-comments.** Default to zero comments. Only WHY-comments where the reason is genuinely non-obvious (hidden constraint, subtle invariant, workaround for a specific bug). One short line max. No section dividers (`# === Section ===`). No multi-paragraph docstrings on functions whose name and signature already speak for themselves.
2. **No banned patterns.** `shell=True`, `: any` (TypeScript), `as any`, `open(...)` without `encoding=`, `datetime.now()` without `timezone.utc`, hardcoded `/tmp` / `~/.config` / `C:\` paths, `console.log` in production, `print()` in production (Python), `os.fork`, `eval`/`exec` on dynamic input, `dangerouslySetInnerHTML`, bare `except:`, `localStorage.setItem(...token...)`.
3. **File size cap.** ≤ 500 LOC of non-blank, non-comment, non-import code. Up to 700 acceptable only when SRP and separation-by-responsibility hold. Above 700 blocks.

## Workflow

4. **Never run `git commit`, `git add`, or `git push`.** Print the title / commit message / PR description in chat — the human commits.
5. **Never add `Co-Authored-By: Claude`** to any commit message draft.
6. **Read `.claude/skills/<relevant-skill>/SKILL.md` and its `learnings/` before starting** any task that matches a skill's description. The skill is the spec.

## Communication

7. **All code and skill content in English** regardless of conversation language.

---

When a hook blocks the Write/Edit, **do not** try to bypass with a different tool or pattern that lies to the hook. Fix the underlying code so the rule is satisfied, then retry.
