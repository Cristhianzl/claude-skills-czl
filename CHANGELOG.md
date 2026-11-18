# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Because this repo ships **configuration you copy into your project**, "breaking"
means: a hook starts blocking code it used to allow, a skill or rule reverses
advice you may have built on, or a file moves so an existing install stops
resolving it.

## [2.6.0] - 2026-11-18

### Added

- **`skills/writing-secure-code`** (agnostic, langflow) — build-time security for any client and any server, independent of language, framework, and architecture: five invariants, a workflow that ends in abuse tests, architecture defaults, and references for clients (browser, webview, mobile, desktop), the browser–server boundary (cookies, sessions, CSRF, CORS, CSP, headers), servers (validation, injection, authentication, passwords, tokens, authorization, service-to-service trust, SSRF, files and parsers, secrets, crypto, logging, abuse limits), and supply chain. Distilled from six articles and seven talks, every factual claim checked against its primary source (OWASP, NIST SP 800-63B-4, MDN, CSP spec, RFC 9700/10017/8252, PCI DSS, MASVS) and every behavior claim tested — cookies, CSRF, CORS, CSP, Trusted Types, frames, and redirects in Chromium 159, Firefox 159, and WebKit 27.2; library behavior in Node and Python. `references/sources.md` records the versions, the results, and the popular advice that was rejected and why.
- **`reviewing-code/references/web-security-checks.md`** (agnostic, langflow, pr-reviewer) — the same rules as diff checks for clients and servers, with triage guidance and grep starters.
- **`reviewing-code/references/pr-pentest.md`** (agnostic, langflow, pr-reviewer) — a minimal dynamic pentest for PRs: 13 safe `curl` probes (unauthenticated access, BOLA read/write, BFLA, mass assignment, CSRF, CORS reflection, headers and cookie flags, stored XSS, open redirect, SSRF through four address encodings, filter injection, brute force and enumeration, error leakage), each mapped to an OWASP WSTG test, under rules of engagement (local or ephemeral environment only, disposable accounts, no load, human approval per command). Every probe was run against a deliberately vulnerable app and its fixed twin: 26/26 correct verdicts.

### Changed

- **`hooks/check-banned-patterns.py`** (agnostic, langflow) — no longer blocks `dangerouslySetInnerHTML` when the value passes through a sanitizer inside `__html` (the skills prescribe exactly that), and now also blocks tokens in `sessionStorage` (the rules ban both web storages). Behavior verified with a before/after test.
- **Contradictions fixed across the configs:** password hashing everywhere now names OWASP parameters and rejects SHA-256/512, not only MD5/SHA-1; "sanitize inputs" became validate at the boundary, encode on output, sanitize only user-authored markup at render; the JWT rule pins algorithms instead of mandating RS256; CSRF guidance no longer treats `SameSite` as sufficient; CSP is containment, not "the strongest XSS defense"; admin routes need a role check, not an obscure path; hard account lockout replaced by layered rate limits; `404` for objects the caller doesn't own; the PII-in-logs examples no longer recommend `console.log` or carry code comments; SSRF added to the audit checklist.
- **`reviewing-code`, `/review`, `/review-pr`, `/security`, `security-review`, `developing-features`, `api-design`, `building-frontend-ui`, `threat-modeling`, `rules/frontend.md`, `rules/api.md`, and both baselines** now point to `writing-secure-code`, `web-security-checks.md`, and `pr-pentest.md` where they apply.

## [2.5.0] - 2026-11-10

### Changed

- **`/pr` reviews the PR it opens** (agnostic, langflow) — after `gh pr create`, the command reads the PR back from GitHub and applies `reviewing-code` in the same turn, preferably in a fresh subagent that gets only the PR number. The review is printed in chat after the URL; it is never posted and findings are never fixed unasked. `writing-pull-requests` gains the matching workflow step, so a PR opened outside `/pr` gets the same review.

## [2.4.0] - 2026-11-03

### Added

- **`building-frontend-ui/references/simplicity-first.md`** — the root directive for every UI: as polished as Linear's website or Apple Notes — simple purpose, simple architecture, simple design, simple implementation. Cut taglines, helper text, and secondary labels; if a screen needs them to make sense, fix the layout (the layout-fix ladder: rename → remove → reorder/group → show, don't tell → disclose progressively → teach by acting → only then one helper line). Every decision raises UX, DX, and AX (agent experience: semantics, accessible names, state in URL/ARIA) at once, without breaking anything. Explicit never-cut list (labels, accessible names, errors, destructive-action consequences, required legal text) and the **mute test**.

### Changed

- **`building-frontend-ui`** — the directive is the first section of the skill ("read before anything else"), part of its description and triggers, and the first pre-delivery check. On existing products it governs new UI and the lines being changed; removing existing copy or screens is proposed, never done unasked.
- **Anti vibe-coded audit** — new corollary (clarity comes from subtraction), a "copy that props up the layout" signal, a Vibe Check item, the mute test as the sixth final test and a scorecard blocker (now 29 items), and a `helperCopy` counter in the console audit.
- **`ux-writing.md` / `designing-from-scratch.md`** — eyebrows and hero sub-lines are no longer defaults; empty states teach by acting in one line.
- **`rules/frontend.md`** — "Simplicity first" is now the first enforced section for UI files.
- **Review checklists** (agnostic, langflow, pr-reviewer) — a simplicity-first check for diffs that create or reshape UI.

## [2.3.0] - 2026-11-03

### Added

- **`skills/guarding-scope`** — scope discipline in every phase (design, planning, implementation, bug fix, tests, docs, review, agent loops). The scope contract before any change (goal / in scope / out of scope / done when), observable scope-creep signals per phase, the AI-slop catalog with a bounded deslop pass on added lines, the mandatory diff-vs-request audit before claiming done, the parking lot ("Out of scope — noticed, not done") for ideas, and stop → classify → ask for necessary expansions. Grounded in Anthropic's over-engineering and task-scope guidance, the Karpathy-inspired "surgical changes" rules, Google's small-CL practice, and project-management change control (sources quoted in `references/sources.md`). The Langflow build adds a learning on what counts as required vs. creep under backward-compat rules.
- **`hooks/check-scope.py`** — snapshots the working tree on each user prompt; at turn end, lists only the files *this turn* changed and makes the agent justify each against the request, revert what doesn't trace, and remove the slop it added. Silent on turns that changed nothing and never loops (`stop_hook_active`).
- **`reviewing-code/references/scope-checks.md`** (agnostic, langflow, pr-reviewer) — the PR's scope (unrelated hunks, unmentioned behavior changes, weakened tests as Blockers, slop) and the review's own scope (pre-existing issues and "while you're here" ideas are follow-ups, never blockers).

### Changed

- **`CLAUDE.md`** (agnostic, langflow) — new always-loaded "Scope discipline — applies to EVERY task" section; wrap-ups carry the "Beyond the literal request (required)" and "Out of scope — noticed, not done" lists when non-empty. **`pr-reviewer/CLAUDE.md`** — new "Scope creep — in the PR and in the review" section; scope joins the lens order after security.
- **Phase skills now gate on scope:** `developing-features` (scope contract first, scope audit before learnings), `developing-features-tdd` (the spec is the boundary; refactor only feature code), `fixing-bugs` (causal lines only; second bugs reported, not fixed), `writing-tests` (never weaken an existing assertion to get green), `running-agent-loops` (de-sloppify is bounded; check against the original contract), `writing-pull-requests`, `building-frontend-ui`, `security-review`, `documenting-features`, `building-langflow-components`, and the `/review` and `/done` commands.

## [2.2.1] - 2026-09-24

### Fixed

- **Review output is sectioned prose, not a wall of text.** The 2.2.0 human-voice reform overcorrected: real reviews came out as six giant paragraphs with zero headings. The format is now a hybrid — `## Summary` / `## Needs to change before merge` / `## Worth fixing in this PR` / `## Follow-ups` / `## Tests` with a `###` per finding — human first-person prose written to the end of the line inside each section, a ~5-sentence cap per paragraph, and still zero emoji, IDs, metadata tables, or label-lines.
- **Request changes only on true Blockers.** The verdict now maps mechanically from the triage: at least one finding meeting the Blocker bar (security defect, data loss/PII, broken build or tests, untested high-risk path) → Request changes; Important findings alone → Approve with comments; otherwise Approve. "Needs to change before merge" may contain only true Blockers, and a tie between two severities resolves to the lower one.

## [2.2.0] - 2026-09-23

### Added

- **`hooks/check-duplication.py`** — anti-duplication guard. When a written function/class name is already defined elsewhere in the repo, the agent gets immediate feedback with the existing location: reuse or justify. Test files and generic names are exempt. Paired with a verifiable "reuse sweep" in `developing-features` (search the concept + synonyms + conventional homes, and name what you found before writing anything new).
- **`hooks/check-design-tokens.py`** — design-system guard. Flags raw color literals hardcoded in components (naming the matching existing token) and new tokens that duplicate or nearly duplicate a color the palette already names. Understands hex, `rgb()`, and shadcn-style HSL triplets.
- **UX/visual design in `building-frontend-ui`** — `references/designing-from-scratch.md` (strategy → structure → design plan delivered before code → tokens → screens, content honesty, SEO floor) and `references/design-craft.md` (typography pairing and weights, color 60/30/10, 8pt spacing and vertical rhythm, motion discipline).
- **Anti-vibe-coded audit** — `building-frontend-ui/references/anti-vibe-coded.md`: the Vibe Check, a paste-in-console audit script, five final tests, and a delivery scorecard with blockers. From-scratch UI must pass it; on an existing design system the system is the law and only the functional layers apply. Enforced as a floor in `rules/frontend.md` and a review-checklist group.
- **`skills/optimizing-discoverability`** — SEO (rank + click), AEO (be the direct answer: question-shaped headings with 40–60-word answer blocks), and GEO (be the source AI engines cite: citable passages, statistics + named sources, original data, AI-crawler policy). Grounded in Google's official AI-features guidance and the KDD 2024 GEO study, with the officially debunked myths called out.
- **`skills/stress-testing`** — the six load-test types with the golden order (smoke → average → stress/spike/soak/breakpoint), open-vs-closed workload modeling with coordinated-omission awareness, SLO thresholds on p95/p99, knee-of-the-curve interpretation. Activates on explicit request only — it never runs or suggests load tests proactively.

### Changed

- **Reviews are human prose, in the PR's language.** `reviewing-code` output dropped the robotic scaffolding (finding IDs, metadata tables, emoji headers, label lines) for first-person prose: evidence first, cause and consequence inside the sentence, a disposition on every finding, severity as internal triage only. Hard-wrapping prose is banned (one paragraph = one logical line). Reviews and PR comments now match the PR's own language — the second official exception to the English-always baseline (`REVIEWS/`/`CZL/` paths exempted in `check-language.py`).
- **`check-doc-sync.py` is quiet.** It fires only when the turn actually changed source (working-tree fingerprint), sends the doc list to a file instead of the terminal, and speaks through the Stop hook's JSON `decision/reason` channel so the user sees only "Ran 1 stop hook". Wording now demands one commit suggestion and silence about docs that are fine.

### Fixed

- Permission settings that muted read-only bash (env-read denies) and caused prompt noise.

### Added

- **`configs/pr-reviewer`** — a third configuration that does one job: review a pull request.
  16 files against the full configs' 307. It ships `CLAUDE.md`, the `reviewing-code` skill with all
  six references, four commands (`/review`, `/review-pr`, `/dual-review`, `/help`), and one hook.
  No skills for writing code, no commit or PR workflow, no per-stack rules.
- **The reviewer is read-only, and that is enforced twice.** `settings.json` denies `Write`, `Edit`,
  `MultiEdit`, and `NotebookEdit` outright, and denies the mutating `git` and `gh` subcommands.
  `hooks/block-mutations.sh` then inspects the whole Bash command string before it runs, so a
  mutation hidden after `&&` or `;` in a compound line — which a permission prefix rule does not
  catch — is blocked too. Mutating `gh api` calls (`-X POST`/`PATCH`/`PUT`/`DELETE`) are blocked;
  read-only ones pass.
- **`/review-pr <n>`** — reviews a GitHub PR by number through `gh`, comparing the PR description
  against the diff. It reads the PR; it never posts to it.

### Changed

- **`.variant` accepts an optional `standalone` marker on a second line.** A config that declares it
  is exempt from the baseline-parity check, so a deliberately focused config no longer has to carry
  every skill and command that `agnostic` has. Existing single-line `.variant` files are unaffected.
- `validate_configs.py` enforces the new marker: the first line must still match the directory name,
  and `standalone` is the only extra value allowed.

## [2.0.0] - 2026-08-27

### Added

- **`check-language.py` hook** (both configs) — blocks any write whose new lines are not English.
  Scores Portuguese and Spanish markers across the delta of the edit: one accented marker
  (`configuração`, `usuário`, `função`, `contraseña`, …) blocks on its own; unaccented ones <!-- i18n-ok -->
  (`arquivo`, `quando`, `retorna`, …) need several to agree. Only the lines the operation touched <!-- i18n-ok -->
  are scanned, so editing an English line in a file with legacy non-English text does not block.

### Changed

- **`CLAUDE.md` — the `## Language` section is now explicit and enumerated.** It states that the
  conversation language never sets the output language, and lists where English is mandatory:
  code and identifiers, comments and docstrings, log and error messages, test names and fixtures,
  commit messages, branch names, PR titles and descriptions, review comments, issue text, and
  documentation. The previous one-line rule was true but easy to skip past.

### Exempted from the language rule

Product UI copy in a translation catalog — any path under `locale(s)/`, `i18n/`, `intl/`, `lang(s)/`,
`translation(s)/`, `messages/`, any `*.po`, `*.pot`, `*.xliff`, `*.properties`, `*.arb`, and
locale-named files such as `pt-BR.json` or `es.yml`. A deliberate non-English line outside a catalog
can be marked `i18n-ok`.

### Upgrade note

**This is a major bump because the hook blocks writes that previously passed.** If your project has
non-English comments or docs, the first edit that touches those lines will be blocked until they are
rewritten in English, or the file is moved into an i18n catalog, or the line is marked `i18n-ok`.
Nothing is rewritten for you and no existing file is scanned until you edit it.

## [1.0.0] - 2026-08-10

First tagged release. Two drop-in `.claude/` configurations for
[Claude Code](https://docs.claude.com/en/docs/claude-code) — a `CLAUDE.md`
baseline, skills, slash commands, per-stack rules, and hooks that enforce the
non-negotiable rules mechanically.

### Configurations

- **`configs/agnostic`** — language- and framework-neutral baseline. 19 skills,
  20 commands, 6 hooks, 3 rule files.
- **`configs/langflow`** — everything in `agnostic`, plus Langflow-specific
  rules, the `building-langflow-components` skill, a `check-langflow-rules.py`
  hook, and `learnings/` entries carrying Langflow project context.

Each config is self-contained: copy the folder to `.claude/` and it works. A
`.variant` marker identifies which one is installed so the `/update-*` commands
refuse to cross-update by accident.

### Baseline (`CLAUDE.md`)

The short, enforced contract the agent reads first: English-only output, no
WHAT-comments, banned patterns, ≤ 500 LOC per file, strong typing everywhere,
path APIs with explicit `encoding`, UTC at boundaries, complexity ceilings,
security as a lens rather than a section, a test for every change, Conventional
Commits, and answer-first prose. Depth lives in the skills; the baseline defers
to them instead of duplicating them.

### Skills

**Writing code** — `developing-features`, `developing-features-tdd`,
`fixing-bugs`, `writing-tests`, `building-frontend-ui`, `api-design`,
`ensuring-cross-platform`, `building-langflow-components` *(langflow only)*.

**Reviewing and shipping** — `reviewing-code`, `writing-pull-requests`,
`documenting-features`, `security-review`, `threat-modeling`.

**Testing in reality** — `validating-in-reality`, `exploratory-testing`,
`playwright-cli`.

**Product and agent operations** — `writing-prd`, `running-agent-loops`,
`debugging-agent-runs`, `evaluating-ai-output`.

Every skill is a `SKILL.md` with frontmatter, focused `references/`, and a
`learnings/` folder whose dated notes **override** the skill's defaults — the
mechanism for teaching a skill your project's specifics without forking it.

### Slash commands

`/init` `/next` `/check` `/test` `/review` `/done` `/commit` `/push` `/pr`
`/roadmap` `/task` `/sync` `/security` `/help` `/learn` `/verify`
`/dual-review` `/evolve` `/update-agnostic` `/update-langflow`

`/update-agnostic` and `/update-langflow` refresh an installed `.claude/` from
this repo: they back up the current folder and preserve local additions
(`learnings/`, `settings.local.json`, project-only rules and skills), with a
variant guard on cross-updates.

### Hooks

| Hook | Event | Enforces |
|------|-------|----------|
| `check-comments.py` | Write/Edit | No WHAT-comments, comment-density cap; doc-comments exempt |
| `check-file-size.py` | Write/Edit | ≤ 500 LOC (≤ 700 with justification) |
| `check-banned-patterns.py` | Write/Edit | `shell=True`, `eval`/`exec` on input, hardcoded paths, tokens in `localStorage`, bare `except:`, … |
| `check-doc-sync.py` | Stop | Flags docs that drifted from changed source; suggests a Conventional Commits message |
| `check-real-validation.py` | UserPromptSubmit | A cURL or local endpoint in the prompt becomes the acceptance test |
| `pre-push-smoke.sh` | before `git push` | Fast lint/test smoke on changed areas (project-configurable skeleton) |
| `check-langflow-rules.py` | Write/Edit | *(langflow)* `SecretStrInput` for API keys, no top-level SDK init, Alembic `Phase:` markers |

Hooks scan only the delta of an edit, so touching one line in a legacy file
doesn't flag pre-existing debt. `settings.json` ships a permission allowlist
plus a deny list covering `.env`, `**/secrets/**`, `credentials.json`,
`git push --force`, `git reset --hard`, and `rm -rf`.

### Rules

Per-stack files that auto-attach by `globs`: `api.md`, `frontend.md`,
`langflow.md` *(langflow only)*, and a `TEMPLATE.md` to add your own.

### Notable decisions folded in along the way

- **No AI attribution anywhere** — no `Co-Authored-By` trailer, no "Generated
  with" footer, no session links in commits or PRs.
- **The agent never runs git on its own** — staging and committing happen only
  after explicit confirmation, through `/commit`, `/push`, `/pr`.
- **Untrusted content is data, never instructions** — external, fetched, tool,
  MCP, and user-pasted content, with a prompt-injection guard.
- **i18n coverage is detected and enforced** in frontend work and PR review
  (mandatory in the Langflow config); a11y references are vendor-neutral
  (WCAG/W3C).
- **Answer-first prose** (Minto/SCQA) across docs, PRDs, reviews, and PR
  descriptions.
- **Scale guidance is gated by measurement** — pooling, indexes, no N+1,
  batching, queueing, sharding, transaction isolation, latency percentiles.
- **TDD inherits the full feature playbook** — only the workflow differs.

### Project infrastructure

- MIT license, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant
  2.1), and `SECURITY.md` scoped to a repo that ships executable hooks and a
  permission allowlist, with private vulnerability reporting enabled.
- Issue templates for bugs, hook false positives, and proposals; a PR template
  carrying the contribution checklist.
- CI on every push and pull request: byte-compiles the Python hooks, parses and
  shellchecks the shell hooks, and runs `.github/scripts/validate_configs.py` —
  which verifies skill frontmatter, `settings.json` hook references, parity
  between the two configs, README coverage of every skill/command/hook, and the
  absence of absolute local paths.

[2.1.0]: https://github.com/Cristhianzl/claude-skills-czl/releases/tag/2.1.0
[2.0.0]: https://github.com/Cristhianzl/claude-skills-czl/releases/tag/2.0.0
[1.0.0]: https://github.com/Cristhianzl/claude-skills-czl/releases/tag/1.0.0
