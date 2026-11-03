# Scope-creep signals — observable, per phase

Every signal here is something you can check against the request, the plan, or the diff. One hit is not automatically a violation — it is a question: *which part of the request requires this?* No answer → revert it, or move it to the parking lot.

## Design / planning

- A component, option, flag, or config key in the plan that no sentence of the request asks for.
- "For the future", "extensible", "in case we later", "generic", "pluggable" — with no caller that exists today.
- An interface, base class, factory, or strategy with exactly one implementation.
- Two materially different readings of the request, and the plan silently picked one.
- The user asked for ideas, options, a plan, or a review — and you started editing files.
- The plan has no **Out of scope** list or no **Done when** check.
- The plan solves a neighbouring problem ("while we're redesigning this, let's also…").
- Estimate drift: the plan is several times bigger than the request implies, and nobody approved the size.

## Implementation

- The diff touches a file that is neither named in the task nor required by the change.
- A new file where editing an existing one would do (a two-line helper in its own module).
- A new dependency for something the stdlib, the platform, or an installed package already does.
- A new helper that near-duplicates one that already exists in the repo.
- Hunks that are only reformatting, renames, reordered imports, or whitespace in code the task didn't need.
- Pre-existing dead code deleted without being asked (mention it — don't delete it).
- Try/catch, null checks, fallbacks, or validation added on internal, already-trusted paths.
- `any` / casts / `# type: ignore` added to silence the type checker.
- A backward-compat shim, overload, or versioned signature with one caller.
- A new parameter or option with no requested use ("configurable timeout" nobody asked for).
- Style that doesn't match the surrounding file (pattern drift).
- Debug logs, entry/exit logging, generic TODOs left behind.
- The diff is much larger than the request warrants — "if you write 200 lines and it could be 50, rewrite it".

## Bug fix

- Changes that are not on the causal path of the bug.
- The working function was rewritten instead of the faulty lines being changed.
- A second bug noticed during the investigation was fixed in the same change.
- No failing test reproduced the bug before the fix.
- The fix special-cases the test input (hardcoding) instead of fixing the logic.
- "Cleanup" of surrounding code: renamed variables, extracted helpers, modernized syntax.

## Tests

- An existing assertion was changed, loosened, skipped, deleted, or marked xfail to get green.
- Asked only to run or write tests, you changed production code — or "fixed" a test to match actual (buggy) output.
- Tests added for behavior this change didn't touch.
- Hollow tests: asserting trivia, asserting the mock, or mirroring the implementation.
- A new test framework, fixture system, or helper library introduced for one test.

## Docs / comments

- Docstrings, comments, or type annotations added to code you didn't change.
- WHAT-comments narrating the code instead of a one-line WHY.
- A README, CHANGELOG, `SUMMARY.md`, `NOTES.md`, or design doc created that nobody asked for.
- Scratch scripts or temp files left in the tree.
- Docs "improved" that your change did not make inaccurate.

## PR / review

- The PR mixes a refactor with a feature or a fix (Google: refactorings go in a separate CL).
- The PR does more than one self-contained thing; its title needs "and".
- Reverting the "cleanup" hunks would leave the feature intact — so the cleanup is a separate change.
- The PR description claims or omits things that don't match the diff.
- **As a reviewer:** you're requesting work the PR never set out to do as a blocker; you're running extra review/hardening rounds nobody asked for; you're "fixing" code outside the diff.

## Agent loops / multi-step runs

- Each iteration improves something new instead of converging on the original goal.
- The de-sloppify/cleanup pass redesigns instead of removing slop.
- The step is checked against the previous step's output, not against the original contract.
- Scope keeps widening while nothing lands (see `debugging-agent-runs`).
- A side operation for verification (stash/pop, reset, reinstall) mutates user state that wasn't part of the task.

## The one-question test

For any line, file, or step: **"If I reverted this, would the thing the user asked for still work?"** If yes, it's out of scope.
