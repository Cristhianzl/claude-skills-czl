---
name: guarding-scope
description: Keep every piece of work inside the scope the user asked for — and detect scope creep, gold plating, and AI slop in any phase (designing a solution, planning, implementing a feature, fixing a bug, writing tests or docs, reviewing a PR, running agent loops). Use on EVERY task that changes code, plans, or specs — not only when the user says "scope". Also use when the user says "scope creep", "only what I asked", "don't touch anything else", "minimal change", "why did you change X", "slop", "over-engineered", "gold plating", "YAGNI", "deslop", or asks to audit a diff/PR for unrequested changes. Defines the scope contract, the per-phase creep signals, the diff-vs-request audit before claiming done, the parking lot for ideas, and the protocol for a genuinely necessary expansion (stop → justify → ask).
license: MIT
---

# Guarding Scope

**Deliver what was asked, at the scope intended — nothing more, nothing less, nothing different.** Every changed line must trace to the request. Anything else is either a *required* consequence of the request (disclosed), or an idea for the parking lot (mentioned, never done).

This is not a style preference. Scope creep is the agent quietly changing the baseline without approval; gold plating is the agent adding work nobody asked for. Both cost review time, hide the real change inside noise, add risk to code nobody wanted touched, and break the user's trust that "fix X" means "only X changed". Anthropic documents the tendency directly: models "tend to overengineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested", and can "expand the scope of a task, adding steps that weren't requested" (sources: `references/sources.md`).

## Read first (always)

List `learnings/` and read every file relevant to the current task. Project-specific scope rules (e.g. "this repo allows formatting-on-save", "migrations always ship with their model change") live there and override the defaults in this SKILL.md. If a learning conflicts with this file, **the learning wins** — mention it to the user.

## The five laws

1. **The user owns the scope.** Only the user widens it. Expansion needs an explicit signal ("be ambitious", "clean up while you're there", "and also…", a yes to your proposal). Your judgment that something "would be better" is a suggestion, never a license.
2. **Every changed line traces to the request.** If a hunk can be reverted and the requested outcome still works, it does not belong in this change.
3. **Necessary ≠ nice.** A change is *necessary* only when the requested outcome cannot be reached without it. "Cleaner", "more robust", "more consistent", "future-proof", "while I'm here" are not necessary.
4. **Ideas go to the parking lot, not the diff.** Bugs you noticed, refactors you want, tests you'd add, docs you'd write — list them in the final message under **Out of scope — noticed, not done**. Do not do them.
5. **Never narrow or transform silently either.** Scope discipline cuts both ways: don't quietly skip part of the request, swap in "a better approach", or weaken a test to get green. If the request looks mistaken, say so in one sentence and do it as asked — or ask, when readings differ materially.

## The scope contract (before any change)

Before editing anything, state the contract — in your head for a one-liner, written out (2–6 lines in chat) for anything bigger:

```
Goal:          <the outcome the user asked for, in their words>
In scope:      <files/modules/behaviors this will touch — and why each>
Out of scope:  <adjacent things you will deliberately NOT touch>
Done when:     <the observable check — failing test goes green, cURL returns X, UI shows Y>
```

- **Ambiguity:** if two readings lead to *materially different work*, present them and ask — don't pick silently. If they lead to the same work, pick, state the assumption in one line, and proceed.
- **Asked for ideas, a plan, options, or a review?** Deliver exactly that and **stop**. No edits until the user says go.
- **Tripwire:** if the change you're about to make is clearly larger than the request implies (a new file, a new dependency, a new abstraction, touching a module not in the contract, or a diff several times bigger than expected) → stop and re-propose before writing.

## Per-phase gates

| Phase | The creep it attracts | The gate |
|---|---|---|
| **Design / planning** | Speculative generality, config knobs, "extensible" layers, components no sentence of the request asks for | Every component maps to a requirement; the plan has an explicit **Out of scope** list; no abstraction without ≥ 2 real callers today |
| **Implementation** | Drive-by refactors, renames, reformatting, new helpers/files/deps, defensive code for impossible cases | Touch only the contract's files; match local style; reuse before writing; validate only at system boundaries |
| **Bug fix** | "Cleaning up" around the bug, rewriting the working function, fixing a second bug you spotted | Change only the lines on the causal path; second bug → parking lot (or its own fix after the user agrees) |
| **Tests** | Editing/weakening existing assertions to get green, tests for unchanged behavior, hollow tests | Tests cover the requested change; an existing test that looks wrong is **reported, never rewritten to pass** |
| **Docs / comments** | Docstrings on code you didn't change, unrequested README/summary `.md` files, WHAT-comments | Update only docs your change made inaccurate; create no doc file unless asked |
| **Review** | Requesting out-of-scope work as blockers; extra review/hardening rounds; fixing things outside the diff | Review the PR against its stated purpose; outside-the-diff ideas are follow-ups, never blockers |
| **Agent loops** | Each iteration "improves" something new; cleanup passes that redesign | Every step is checked against the original contract, not the last step's output |

Full observable signal catalog per phase: `references/signals.md`.

## The scope audit (before claiming done — mandatory)

Run it on the actual diff (`git diff` + `git status` for new files), not on your memory of what you did:

1. **List every changed file.** For each, answer: *which part of the request requires this file?* No answer → revert the file.
2. **Walk every hunk.** Reformatting, renames, reordered imports, comment edits, added type hints, moved code, deleted pre-existing dead code in lines the task didn't need → revert the hunk.
3. **New things.** Every new file, dependency, config option, parameter, abstraction, or test must be required by the request. Otherwise revert it.
4. **Slop pass on added lines** (`references/slop.md`): WHAT-comments, try/catch or null checks on trusted internal paths, `any`/casts to silence types, debug logs, generic TODOs, pattern drift from the file's style. Remove only what you added and what is inconsistent — keep domain-valid guards.
5. **Orphans.** Remove imports/variables/functions *your* change made unused. Leave pre-existing dead code alone (mention it).
6. **Tests.** No existing assertion was weakened, skipped, deleted, or changed to match buggy output.
7. **Temp files.** Scratch scripts and helper files you created for iteration are deleted.
8. **Report.** In the wrap-up, if anything outside the literal request was changed because it was *required*, list it under **Beyond the literal request (required)** — one line each with the reason. Then the parking lot.

`hooks/check-scope.py` forces this audit at the end of any turn that changed files.

## When an expansion is genuinely necessary

1. **Stop** before making it.
2. **Classify:**
   - **Required** — the requested outcome cannot work without it (the fix needs a signature change in its one caller; the feature needs a migration). Make the **smallest** version, keep it separable (own commit when the repo commits), and disclose it in the report.
   - **Materially different work** — a redesign, a new module, a contract/API change, a dependency, touching another team's area, or anything that roughly doubles the diff → **ask first**, with the reason and the impact (files, risk, size).
   - **Optional but beneficial** → parking lot. Do not do it.
3. **Never** justify with "while I was here", "for consistency", "to be safe", or "for the future".

A small preparatory refactor that *makes the requested change possible* is allowed (YAGNI does not forbid making code easier to change) — but it is named, minimal, and separate. A refactor that merely makes the code nicer is not.

## Wrap-up format (when anything was noticed or expanded)

```
<what changed — ≤ 3 bullets, all traceable to the request>

Beyond the literal request (required):
- <file/change> — <why the requested outcome needed it>

Out of scope — noticed, not done:
- <idea/bug/refactor> — <one line; offer to do it as a separate task>
```

Omit a section when it's empty. Never smuggle a parking-lot item into the diff "because it was quick".

## Tradeoff — when to lighten up

Throwaway scripts, spikes the user labelled as exploratory, and explicit "go wild / be ambitious / refactor freely" requests widen the scope **by the user's own words** — follow them, and still disclose what you touched. Security fixes inside the lines you're already changing (e.g. the SQL you're editing is injectable) are part of doing the change correctly; a security problem *elsewhere* goes to the parking lot flagged as urgent, not silently fixed.

## Capture a learning (final step)

Ask: *did the user correct a scope decision, or did I hit a project-specific rule about what counts as in scope?* If yes, append a `learnings/YYYY-MM-DD-slug.md`. If no, skip.

## References

- `references/signals.md` — observable scope-creep signals per phase (design, implementation, bugfix, tests, docs, PR/review, loops).
- `references/slop.md` — the AI-slop catalog and the deslop pass on added lines.
- `references/sources.md` — the definitions and the exact Anthropic / community / Google wording this skill is built on.
