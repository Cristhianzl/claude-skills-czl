# Hard rules — apply on every action in this repo

These rules are enforced by PostToolUse hooks in `.claude/hooks/`. A violation fails the Write/Edit tool call with a clear stderr message. Treat them as inviolable defaults; the only way to "skip" one is to redesign the code so the rule no longer applies.

## Universal rules (enforced by hooks)

1. **No WHAT-comments.** Zero by default. Only WHY-comments where the reason is genuinely non-obvious (one short line max). No section dividers (`# === Section ===`). No multi-paragraph docstrings on functions whose signature already explains them.
2. **No banned patterns.** `shell=True`, `: any` (TS), `as any`, `open()` without `encoding=`, `datetime.now()` without `timezone.utc`, hardcoded `/tmp` / `~/.config` / `C:\` paths, `console.log` in production, `print()` in production, `os.fork`, `eval`/`exec` on dynamic input, `dangerouslySetInnerHTML`, bare `except:`, `localStorage.setItem(...token...)`.
3. **File size cap.** ≤ 500 LOC of code (non-blank, non-comment, non-import). 500–700 acceptable only when SRP + separation-by-responsibility hold. > 700 blocks.

## Langflow rules (enforced by hooks)

4. **API keys use `SecretStrInput`**, never `MessageTextInput`. (Encrypted at rest, masked in UI.)
5. **No top-level SDK instantiation in component modules.** No `client = openai.OpenAI()` at module top — move inside the output `method`.
6. **Alembic migrations declare `Phase: EXPAND | MIGRATE | CONTRACT`** in the docstring. Pre-commit + this hook both enforce.

## Langflow rules (enforced by code review and the human)

7. **Never rename a Component class.** Name = identity in every saved flow JSON. To evolve: add a new class with the new name, mark the old one `deprecated = True`, keep its behavior intact. Same rule for `inputs[].name` and `outputs[].name`.
8. **Bundle changes update `BUNDLE_API.md`** in the same commit. The pre-commit changelog gate will block otherwise.
9. **`uv run` for every Python invocation**, including `git commit`. Bare `python` / `pip` / `pytest` / `git commit` fails pre-commit silently or wrong.
10. **Prefer real integrations over mocks** in tests. Mocks only for failure modes a real sandbox cannot reproduce. (From `AGENTS.md`.)

## Workflow

11. **Never run `git commit`, `git add`, or `git push`.** Print the message in chat. Only the human commits.
12. **Never add `Co-Authored-By: Claude`** to any draft.
13. **Read `.claude/skills/<relevant-skill>/SKILL.md` and its `learnings/`** before starting any task that matches a skill's description. The skill is the spec. Also read `AGENTS.md` (canonical) and the relevant `.agents/skills/` for area expertise.

## Communication

14. **All code and skill content in English** regardless of conversation language.

---

When a hook blocks Write/Edit, **fix the code** so the rule is satisfied. Do not try to bypass with a different tool or with a pattern designed to fool the regex — the rules exist for production reasons, and bypassing them produces a different kind of incident than the one the rule prevents.

Detail and rationale: `.claude/skills/`, especially `developing-features/SKILL.md`, `building-langflow-components/SKILL.md`, `reviewing-code/learnings/2026-05-27-langflow-review-blockers.md`.
