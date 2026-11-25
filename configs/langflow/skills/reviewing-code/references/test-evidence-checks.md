# Test evidence — do the tests prove what the PR claims?

A green test suite is evidence only if the tests would have been red without the change, and only for the environments where they actually ran. These checks are language- and framework-agnostic; adapt the commands to your stack. They are mandatory on Tier 3 PRs (`context-sweep.md`) and apply to any PR that adds or changes tests.

## 1. The test fails without the fix

Run the new or changed tests against the **base** code with the PR's tests applied. Every test that claims to cover the fix must fail there; a test that passes on the base proves nothing about the change.

```bash
git stash -u
git checkout <base> -- <production paths the PR changed>
<run the PR's new tests>
git checkout HEAD -- <production paths the PR changed>
git stash pop
```

- Check it **per arm**. A test parametrized over several environments (databases, platforms, feature flags) must fail without the fix on each arm that claims to cover it. An arm that passes on the base — because the bug only exists on another engine, or because the arm takes a different path — is not coverage of the fix; it is decoration.
- When you can't run the suite, read the test and reason about it explicitly: which assertion would fail on the base, and why? If you can't name it, say so as a finding.
- A PR description that says "fails on the base" is a claim; reproduce it or mark it unverified.

→ verify: for each test the PR adds for the fix, you know which assertion fails on the base, on which arm.

## 2. The test runs in CI

A test that only runs on the author's machine protects nobody. For each new test file:

- Find the workflow and job that execute it. Some workflows run a whole directory; others **list test files explicitly** — a new file is then silently left out until someone adds it.
- If the test is gated (an environment variable, a service URL, a database dialect, a marker, a `skipif`/`skip` condition), confirm that job provides what the gate needs. Where no job does, every gated case **skips in CI** and only the ungated arm runs.
- When CI results exist, open the job log and confirm the test names appear as run, not skipped. Check the coverage report for the changed lines — a lock branch or error path that shows as missed means no CI run exercised it.
- When a gated arm is the one that actually exercises the fix, a PR that doesn't wire it into CI ships an untested fix, whatever the description says. That is at least Important, and a Blocker on Tier 3.

→ verify: each new test file maps to a CI job that runs it with every gate satisfied, or the gap is a finding.

## 3. Concurrency tests force the schedule they claim to test

A test for a race passes trivially if the race never happens during the run. Check that it **forces** the interleaving:

- **The barrier is per subject and per phase.** If the test claims "two workers read before either writes", every worker's *first* read must complete before any worker proceeds — for each key the test exercises, not just the first two calls overall. A barrier shared across all keys, or one that counts later re-checks as arrivals, releases too early.
- **No timeout escape.** A barrier with a timeout that lets one worker "proceed alone" on a slow runner turns a race test into a sequential one; the test then passes with the protection removed.
- **Re-checks and retries bypass the barrier.** Only the step the race is about is gated; the protected re-check must not be counted, or the barrier can be released by the code path it is meant to test.
- **The test fails when the protection is removed.** Delete the lock, the unique constraint, or the conditional update, run the test several times, and confirm it fails every time (or with a stated, high probability). This is check 1 applied to concurrency.
- **Swallowed errors are visible.** If workers log and swallow exceptions, the test asserts no worker errored; otherwise a deadlock or lock timeout looks like success.

→ verify: you can name the mechanism that guarantees the interleaving and the run that showed the test fails without the protection.

## 4. Local evidence vs CI evidence

Numbers in a PR description from a local run — row counts, timings, "passes with the real database enabled" — describe the author's environment. Separate them in the review:

- What CI proves: the jobs and arms that ran and passed.
- What only the author's machine shows: everything else. Say which claims rest on local evidence only, and ask for the missing CI wiring when the claim matters (Tier 3, or the gated arm is the one exercising the fix).
- Measurements that justify a trade-off ("the lock wait is negligible") must come from a run that reproduces the real contention: the competing operation, at realistic scale, while the change holds its lock.

→ verify: every evidence claim in the description is labeled in your head as CI-proven, locally reproduced by you, or unverified.

## 5. The test covers the failure path, not only the happy path

For each failure branch the change adds or touches — an error mid-loop, a rollback, a lock timeout, a partial batch — there is a test that drives it and asserts the resulting state (what committed, what rolled back, what the next run does). A rollback test that asserts "no rows" for the whole batch when the intended behavior is per-item atomicity is testing the wrong contract.

→ verify: each failure branch has a test whose assertion matches the intended contract.
