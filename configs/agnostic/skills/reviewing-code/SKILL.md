---
name: reviewing-code
description: Review a pull request and produce a human-voiced, copy-paste-safe review — first person, evidence first, findings as complete sentences ordered by severity (Blocker / Important / Recommended / Nice-to-have as internal triage, never as labels), each with file:line evidence and a disposition. Use when the user asks to review a PR, "code review", "review this diff", "verify the changes before merge", or asks for a second opinion on someone else's branch. Output is the review in chat — never run git or post to GitHub directly.
license: MIT
---

# Reviewing Code

Produce a PR review that reads like a competent engineer wrote it after doing the work. It applies a security lens, a comprehension audit, and structural checks, triages findings by severity internally, and delivers them as first-person prose — evidence first, disposition in every finding, copy-paste-safe for GitHub.

## Read first (always)

List `learnings/` and read every file relevant to the current PR (the touched modules, frameworks, or risk areas). Project-specific review conventions, severity adjustments, banned patterns, or scope rules live there and override the defaults in this SKILL.md. If a learning conflicts with this file, **the learning wins** — mention it to the user.

## Tradeoff — when to apply, when to lighten up

Apply the full discipline (security lens + comprehension audit + checklist + grep) for **production-bound PRs** touching shared services, payments, auth, user data, AI runtime, or anything externally observable.

Lighten formality for: docs-only changes, lockfile bumps with no API change, single-line typo fixes, internal-tooling-only changes behind a feature flag not yet enabled. Still apply the security lens — even doc PRs can leak secrets in examples.

## Hard rules — output is a chat message, not a side effect

Apply the same restrictions as the `writing-pull-requests` skill, plus review-specific ones:

- **Never** run `gh pr review`, `gh pr comment`, or any GitHub-mutating command. The user posts the review themselves.
- **Never** run `git commit`, `git add`, `git push`. Only the human commits.
- **Never** write the review to a file. Output goes in the chat.
- **Never** use `#N` anywhere in the output — GitHub auto-links it to PR/issue `N`.
- **Never hard-wrap prose**: one paragraph = one logical line; Enter only at paragraph/list/heading boundaries. Manual 72/80-column wrapping is the strongest "a tool wrote this" tell.
- **Write like a person** — first person, evidence first, findings as complete sentences with the disposition inside them. No finding IDs, no `**File:**`-style label lines, no emoji headers, no metadata tables. Full voice rules: `references/output-format.md`.
- **Never** `@mention` users unless the user explicitly asks.
- **Never** include `Fixes #N`, `Closes #N`, `Resolves #N` — they auto-close issues on merge.
- **Never** paste full file contents — link with `path/to/file.ts:42` and quote 3-10 relevant lines max.
- **Never request out-of-scope work as a blocker.** Pre-existing issues in code the PR doesn't touch and "while you're here" ideas are follow-ups, phrased as optional. Judge the PR against its own purpose; ask for less code, not more, unless a real defect requires more (`references/scope-checks.md` § 2).
- **Never** use absolute local paths (`/Users/...`, `/home/...`). Use repo-relative paths only.
- **Match the PR's language.** The review or comment is written in the language of the PR itself (title, description, discussion): a pt-BR PR gets a pt-BR review, an English PR gets English. Code identifiers, paths, and quoted code stay verbatim. Mixed or unclear → default to English. (This is the one exception to the English-always baseline.)

## Workflow

1. **Read the PR end-to-end before commenting.** Files, diffs, test changes, and the PR description. If the description claims something not in the diff, that's a finding by itself.
   → verify: you can summarize the PR in 1–3 sentences and name the dominant risk area (auth, payments, AI, infra, UI, refactor, etc.).

   **Then check scope** (`references/scope-checks.md`): walk the diff file by file against the PR's stated purpose. Unrelated refactors/renames/reformatting, behavior changes the description doesn't mention, weakened or deleted test assertions, unneeded deps/abstractions/config, unrequested artifacts, and slop on added lines are findings.
   → verify: every changed file maps to the PR's purpose, is a disclosed required change, or is a finding.

   **Then set the depth from the risk tier** (`references/context-sweep.md` § Risk tiers). Concurrency, locks, transactions, migrations, startup sweeps, auth, money, irreversible deletes, or data shared across users/processes make it Tier 3: every sweep, the concurrency lens, every test-evidence check, a fresh-context reviewer, and — if an automated reviewer also runs — its high effort level or above.
   → verify: you can state the tier and why.

   **Then sweep the context beyond the diff** (`references/context-sweep.md`): callers and transaction owners of every changed function; consumers of every value whose type, format, or identity changes; the contention map of everything the change locks or writes; the wiring that makes new tests, migrations, flags, and jobs actually run (CI workflows, gates, explicit file lists); and precedent in the codebase plus what the dependencies already provide at the project's declared floor. Most defects a human reviewer catches and a diff-only review misses live here.
   → verify: the summary names what you traced outside the diff.

2. **Apply the security lens** to every significant block (see `references/security-checks.md`; when the diff renders data, handles a request, or touches cookies, CORS, CSP, auth, queries, uploads, or outbound URLs, also `references/web-security-checks.md`). When such a PR can be run in a local or ephemeral environment, run the matching probes from `references/pr-pentest.md` under its rules of engagement — never against production or shared environments. Five questions: what is being trusted unverified? what's the authoritative source for this behavior? what happens on the failure path? who controls each value and could they lie? what is the blast radius if this is wrong?
   → verify: every "unverified assumption" has been mapped to either a finding or a defensible justification in the diff.

3. **Apply the comprehension audit.** For every non-trivial block: can the author summarize it in 1–3 sentences? Is the *why* captured durably (test name, `Why:` comment, PR `## Design Decisions`, ADR)? Or is the block "AI wrote it, I trust it"?
   → verify: every non-obvious choice has a durable anchor for its rationale. Red flags trigger a finding (see `references/security-checks.md` § Comprehension Audit).

4. **Apply the structural checks** (see `references/structural-checks.md`). File-structure hard limits (500 LOC / 5 different-prefix functions / 10 same-prefix / 1 main class / cyclomatic ≤ 10 / nesting ≤ 4). SOLID. Pragmatic principles (DRY, KISS, YAGNI, Demeter). Architecture / layer separation.
   → verify: every violation is triaged by severity; "would a senior call this overengineered/duplicated?" is your gut check.

5. **Apply the platform-agnostic checks.** Paths, encoding, shell, temp/config dirs, line endings, time, CI matrix. Full grep recipes in `references/grep-recipes.md`. See `ensuring-cross-platform` for the rationale.
   → verify: no Windows-only bug ships through this PR.

6. **Apply the correctness checks** (see `references/correctness-checks.md`). The third class of bug: code that is right on the happy path and silently wrong on an edge/error path. New enum member → audit every enumeration site. Control-flow/signal exceptions (pause/cancel/retry) propagate **unwrapped** through every layer. Degrade-don't-crash contracts never hard-raise. Locks and transactions (§4): what is locked, for how long (the enclosing transaction, often owned by a caller), who else waits, how each database engine behaves, and what an error inside the transaction does to the rest.
   → verify: every new state and every failure branch has a test that would fail if its line were deleted.

7. **Apply the testing checks.** Coverage gate (≥75%, target 80%) shown by the author. Tests challenge the code, not confirm it. Both happy path AND adversarial. Anti-patterns absent (Mirror, Liar, Giant, Mockery, Inspector, Chain Gang, Flaky, Snowball). See `writing-tests` for the full list. Then the evidence checks (`references/test-evidence-checks.md`): each new test fails on the base code, on every arm that claims coverage; each new test file runs in CI with its gates satisfied; concurrency tests force the interleaving instead of hoping for it; local results in the PR description are labeled as local.
   → verify: if you removed a line of business logic, at least one test would fail — in CI, not only on the author's machine.

8. **Triage the findings** by severity (Blocker / Important / Recommended / Nice-to-have) — this taxonomy is your internal ordering tool, not output scaffolding.
   → verify: every finding has file:line evidence, the cause and consequence, and a disposition (fix before merge / follow-up / take-or-leave).

9. **Render the review as human prose inside real sections** (`references/output-format.md`): a `## Summary` with what you did and the verdict, then `##` sections by disposition (before merge / this PR / follow-ups / tests) with a `###` per finding — prose written to the end of the line inside each. No emoji, no IDs, no paragraphs over ~5 sentences.
   → verify: it passes the copy-paste safety check, is scannable by headings, AND reads aloud like a person — no label-lines, no hard-wrapped lines, no walls of text.

10. **Capture a learning (final step).** Ask: *did I encounter a review pattern, codebase quirk, recurring violation, or severity adjustment not in this SKILL.md or `references/`?* If yes, append a `learnings/YYYY-MM-DD-slug.md`. If no, skip.

## Verdict rule — Request changes means BLOCKERS, nothing else

The verdict maps mechanically from the triage. **Never inflate it.**

| Situation | Verdict |
|---|---|
| At least one true Blocker | **Request changes** — and name exactly what unblocks it |
| Important findings, zero Blockers | **Approve with comments** — the PR can merge; the author decides when to address them |
| Only Recommended / Nice-to-have | **Approve** |

### Self-review and agent loops — the author does not decide

The table above is for reviewing **someone else's** change, where the author owns the follow-up. When the review is of your own change, or of a change an agent made — a pre-push review, a `/pr` review of a PR you just opened, any implement→review→fix loop — the author is the one being checked, so the author doesn't get to waive findings:

- Every Blocker, and every Important finding that comes with a concrete fix, is **fixed before push**. Leaving one unfixed requires the user's explicit approval for that specific finding.
- Writing a known defect into the PR description, a code comment, or a commit message as an "accepted cost", "known limitation", or "trade-off" without that approval is itself a Blocker — it converts a finding into documentation without anyone deciding.
- After fixes, re-review **each** finding against the new code: fixed, waived by the user, or disputed with evidence (a test or measurement, not an argument). "Documented" is not a resolution.
- The final report carries an `## Unresolved findings` section listing every finding not fixed, with its status and who approved it. An empty section is stated as empty.

A finding only counts as a Blocker if it meets the Blocker bar below (security defect, data loss/PII, broken build or tests, high-risk path with no test, a regression that makes user-facing requests wait or fail (for example a lock held across a long transaction on a row a hot path writes)) — "I'd strongly prefer this changed" is Important, **not** a Blocker, and never justifies Request changes. The same discipline applies to section placement: only true Blockers go under "Needs to change before merge"; everything else lives in "Worth fixing in this PR" or later. When in doubt between two severities, pick the lower one.

## Severity scoring (internal triage — expressed in prose, never as labels)

| Severity         | Meaning                                                          | How it sounds in the review |
|------------------|------------------------------------------------------------------|------------------------------|
| Blocker          | Must be fixed before merge. PII in logs, security defect, file-structure violation, missing test for a high-risk path, a regression that makes user-facing requests wait or fail (for example a lock held across a long transaction on a row a hot path writes). | "This needs to change before merge: …" |
| Important        | Preferably this PR. SOLID violations, architecture leaks, weak error handling, missing adversarial tests. | "I'd fix this here rather than later: …" |
| Recommended      | Can ship as a follow-up. Observability gaps, naming clarity, minor duplication. | "Fine as a follow-up: …" |
| Nice-to-have     | Polish. Idiomatic suggestions, refactor opportunities that don't affect correctness. | "Take it or leave it: …" |

The taxonomy orders the review; the words above carry it. **Never `#N` anywhere — GitHub auto-links it.**

## Required output structure

Render exactly the skeleton in `references/output-format.md` § Structure: `## Summary` (what you checked, ran, and traced, plus the verdict in plain words), then sections by disposition — `## Needs to change before merge` (true Blockers only), `## Worth fixing in this PR`, `## Follow-ups and take-it-or-leave-it`, `## Tests` — with a `###` per finding written as prose. No emoji headers, no finding IDs, no `**File:**`-style label lines, no metadata tables. Omit empty sections. When the review comes from a self-review or agent loop, add `## Unresolved findings` (see the verdict rule above).

## The five questions to ask on every PR

For every significant block of code:

1. **What is this code trusting without verifying?** — inputs, tokens, signatures, IDs, headers, flags from outside the system.
2. **What is the authoritative source for this behavior?** — is the implementation based on official docs/SDK, or on assumption/tutorial?
3. **What happens in every failure path?** — exceptions swallowed? failed checks that silently pass? errors leaking internals?
4. **Who controls each value, and could they lie?** — client-sent fields, URL params, headers are all forgeable unless verified server-side.
5. **What is the blast radius if this is wrong?** — data exposure? privilege escalation? forged events? resource exhaustion?

Unverified assumptions are where vulnerabilities live. They look like reasonable code.

## Blocker categories (zero-tolerance review)

These are Blockers automatically — full detail in `references/security-checks.md` and `references/structural-checks.md`:

- **PII in logs.** Any email, name, phone, address in a `logger`/`print`/`console` call. Approved identifiers: `auth_id`, `user_id`, `stripe_id`, internal `id`.
- **Secrets in code.** Hardcoded API keys, tokens, passwords. Webhook secrets not in env vars.
- **DRY violation.** Duplicate types, classes, or logic (5+ lines × 2+ occurrences).
- **File structure violation.** > 500 LOC / > 5 different-prefix functions / > 10 same-prefix / > 1 main class / cyclomatic > 10 / nesting > 4.
- **Mixed responsibility prefixes in one file.** `validate*` AND `format*` in the same file = violation.
- **Comprehension debt.** Author can't defend a block. "AI wrote it, I trust it." `Why:` missing on a non-obvious choice.
- **AI security violation** (when applicable). Direct DB access from AI layer. Secrets in system prompt. Output rendered raw. No human-in-the-loop on irreversible actions.
- **AI runtime missing resilience** (when applicable). No timeout, no circuit breaker, no fallback, no kill switch, no cost ceiling.
- **Third-party integration done wrong.** Custom signature verification instead of provider spec. `==` instead of timing-safe compare. Reading payload fields before verification.
- **AI-generated code in high-risk paths unverified.** Auth, payments, signatures, crypto — every assumption needs to be checked against the authoritative source.

## Output format

The review comment, ready to paste. Print it in the chat. Don't write a file. Don't run `gh`.

Detailed rules — labeling schemes, length, length, link format, copy-paste safety check — in `references/output-format.md`.

## See also

- `../documenting-features/references/communication.md` — answer-first structure (Minto Pyramid); lead the review with the verdict, then findings by severity.
- `references/output-format.md` — GitHub-comment formatting rules, label schemes, structure skeleton, copy-paste safety check.
- `references/security-checks.md` — PII zero-tolerance, AI security, third-party integration, AI-untrusted-code lens, AI runtime resilience.
- `references/pr-pentest.md` — minimal dynamic pentest for a PR: 13 safe `curl` probes (auth, BOLA, BFLA, mass assignment, CSRF, CORS, headers/cookies, stored XSS, open redirect, SSRF, injection, brute force/enumeration, error leakage) with rules of engagement and WSTG IDs.
- `references/web-security-checks.md` — client and server security as diff checks: XSS sinks, URL schemes, tokens in storage, UI-only authorization, CSRF/CORS/CSP/cookies, injection, BOLA/BFLA, mass assignment, SSRF, uploads, parsers, passwords, JWT, plus the PR-level reads (dependencies, CI, permission migrations).
- `skills/security-review` — for a dedicated, OWASP-2025 security audit (frontend + backend) beyond the always-on blockers here.
- `skills/writing-secure-code` — the build-time rules behind `web-security-checks.md`; link the relevant reference in a finding instead of re-deriving it.
- `references/structural-checks.md` — file structure hard limits, SOLID verification, pragmatic principles, layer separation, error handling.
- `references/context-sweep.md` — risk tiers and the five sweeps beyond the diff: callers and transaction owners, consumers of changed values, the contention map, wiring (does it run in CI?), precedent and platform.
- `references/test-evidence-checks.md` — fails without the fix (per arm), runs in CI (gates, explicit file lists, job logs, coverage), concurrency tests that force the schedule, local vs CI evidence, failure-path contracts.
- `references/correctness-checks.md` — enum/state-machine completeness, control-flow exceptions propagate unwrapped, degrade-don't-crash contracts + the failure-path test spec.
- `references/scope-checks.md` — is the PR in scope (unrelated hunks, unmentioned behavior changes, weakened tests, slop) and is the review in scope (no out-of-scope blockers).
- `references/grep-recipes.md` — copy-paste grep commands for catching common violations across languages.
- `references/checklist.md` — pre-submission checklist + perfect-score criteria + framework-specific guidelines.
- `developing-features` skill — the code quality rules being reviewed; if you find yourself rebuilding the rationale, link to that skill in the finding.
- `writing-tests` skill — what "good tests" means in a review context; the 8 anti-patterns map directly to review findings.
- `ensuring-cross-platform` skill — the portability rules; platform red flags are in the structural checks here.
- `learnings/` — project-specific review conventions, recurring violation patterns, severity adjustments.
