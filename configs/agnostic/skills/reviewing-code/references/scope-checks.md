# Scope checks — the PR's scope and the review's own scope

Two directions. The PR must do what it says and only that; the review must judge the PR against its purpose and not turn into a wish list. Signal catalog and rationale: `guarding-scope` (`references/signals.md`, `references/slop.md`).

## 1. Is the PR in scope?

Establish the PR's purpose first — title, description, linked issue — in one sentence. Then walk the diff file by file with one question: **which part of that purpose requires this change?**

| Signal in the diff | Default severity |
|---|---|
| An existing test assertion loosened, skipped, deleted, or changed to match new output, with no stated reason | **Blocker** — the safety net was cut to get green |
| A behavior change not mentioned in the description (a "while I was here" fix, a changed default, a removed branch) | **Blocker** when it touches a high-risk path (auth, payments, data, AI runtime) without a test; **Important** otherwise |
| The PR mixes a refactor/rename/reformat with a feature or fix | **Important** — ask to split; the refactor hides the real change and makes revert unsafe |
| Files touched that the purpose doesn't need (drive-by edits, formatting sweeps, renamed variables in untouched code) | **Important** — ask to revert or split |
| New dependency, config option, abstraction, or public API the purpose doesn't need | **Important** — YAGNI; each is a maintenance cost the PR didn't justify |
| Slop on added lines: WHAT-comments, try/catch on trusted paths, casts to `any`, debug logs, generic TODOs, single-use helpers | **Recommended** (Important when it's widespread or masks errors) |
| Unrequested artifacts: summary `.md` files, scratch scripts, example files | **Recommended** — ask to remove |
| Description claims something the diff doesn't do, or omits something it does | Finding by itself (already step 1 of the workflow) |

The reversibility test decides borderline cases: *if this hunk were reverted, would the PR still achieve its stated purpose?* If yes, it's out of scope for this PR.

Scope creep that is **required** and disclosed (the fix genuinely needs the caller's signature to change; the feature needs its migration) is not a finding — note it as fine.

## 2. Is the review in scope?

The reviewer is subject to the same discipline:

- **Review the diff against the PR's purpose.** Pre-existing problems in untouched code are **follow-ups**, never "before merge" — unless the PR makes them worse or newly reachable.
- **Never request out-of-scope work as a blocker.** "While you're here, also refactor X / add feature Y / migrate Z" belongs in Follow-ups, phrased as optional.
- **Don't ask for the PR to grow.** Suggesting extra abstractions, configurability, or "future-proofing" is gold plating by proxy. Ask for less code, not more, unless a real defect requires more.
- **One review pass.** Don't run extra rounds of review or hardening nobody asked for.
- **The reviewer never edits.** A fix you'd make is described in the finding; the author applies it.

## How to write a scope finding

State the purpose, the hunk, and the consequence, then the disposition — e.g. "The PR fixes the token-expiry check, but `src/auth/session.ts:40-88` also renames four variables and reorders imports in code the fix doesn't touch. That makes the one-line fix hard to see and the revert riskier; I'd move the rename into its own PR." Never accuse — describe the diff.
