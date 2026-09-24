# Output format — write like a person

The review is read by a colleague, on GitHub or in a `.md` file. It must read like a competent engineer wrote it after actually doing the work — not like a tool filled in a form. The severity taxonomy (Blocker / Important / Recommended / Nice-to-have) stays as your **internal triage**; the output expresses it in prose and in ordering, not in labeled scaffolding.

## The exemplar shape

A strong human review looks like this (structure, not content):

> Checked X in all N directions, with live tests. A, B and C all come through unchanged. I pushed three small fixes, each with a test that fails without it:
>
> - [abc1234](link): `add_embeddings` raises above its `bulk_size` of 500, so a batch of 501+ failed. It now writes in slices.
> - …
>
> I wouldn't apply <bot>'s `text_field` suggestion as written: similarity search also reads `text`, so writes should keep matching ingestion. That can go in a follow-up.

What makes it work: it **opens with what the reviewer did** (the evidence), findings are **complete sentences with the cause and the consequence in them**, links live **inside the sentence**, and every judgment ends with a **disposition** (fix now / follow-up / won't do, with the reason).

## Voice rules

- **First person, evidence first.** Open with what you checked/ran/read — "Ran the migration against a copy of the staging DB", "Traced the auth path end to end" — then what you found. Never open with a metadata table or a verdict badge.
- **Prose paragraphs, not forms.** No `**File:**` / `**Issue:**` / `**Why it matters:**` / `**Suggested fix:**` label lines — that information goes *inside* the sentences: "`chroma.py:56` coerces metadata to scalars, so a nested dict silently flattens and the round-trip loses it; the other two backends keep it. Either flatten everywhere or reject nested metadata at the interface."
- **No invented finding IDs** (`B1`, `I2`, `F3`), no findings-count line, no emoji section headers, no severity badges. Severity is carried by **order** (what blocks the merge comes first) and by **plain words** ("this needs to happen before merge"; "fine as a follow-up"; "take it or leave it").
- **Every judgment gets a disposition and a reason.** "I wouldn't do X as written: <reason>. <where it should go instead>." A finding without a recommended disposition is a complaint, not a review.
- **Bullets only for true enumerations** (commits, repro steps, a list of affected files) — and each bullet is a complete thought, written to the end.
- **Structure is not the enemy — walls of text are.** Use real GitHub markup: `##` section headings, `###` per finding, `code` spans, fenced code, bold sparingly. What stays banned is the *robotic* scaffolding: emoji in headings, finding IDs, metadata tables, label-lines.
- **A paragraph carries one finding-sized idea.** More than ~5 sentences means it needs a split or its own `###`. Six ten-sentence paragraphs in a row is a bible, not a review — nobody reads it.
- **Write in the PR's language** (title/description/discussion decide): pt-BR PR → pt-BR review; English PR → English. Code, paths, and quotes stay verbatim; mixed or unclear defaults to English.

## Never hard-wrap prose

**One paragraph = one logical line.** Press Enter only at a real boundary: end of paragraph, end of list item, before/after a heading or code fence. Never wrap at 72/80/100 columns — GitHub and every editor soft-wrap, and manual mid-sentence line breaks are the single strongest "a tool wrote this" tell in a `.md` file. This applies to every prose file you write, not just reviews.

## Structure (the skeleton — human voice inside real sections)

Reviews with more than ~2 findings use this shape. A trivial PR can be a single short paragraph with no headings at all.

```markdown
## Summary

<First person, 2-5 sentences: what you checked/ran (the evidence) and the verdict in plain words. The verdict follows the mechanical rule in SKILL.md: Request changes ONLY with a true Blocker; Important findings alone = "Good to merge — a few things worth addressing"; never "needs to change before merge" for something that doesn't meet the Blocker bar. Full-width lines, no hard wrap.>

## Needs to change before merge

<ONLY true Blockers (security defect, data loss/PII, broken build/tests, untested high-risk path). If nothing meets that bar, this section does not exist.>

### <Short descriptive title — no ID, no emoji>

<Prose: the cause, the consequence, the evidence (file:line inside the sentence), and the fix. One finding-sized idea per paragraph.>

## Worth fixing in this PR

### <Short title>

<...>

## Follow-ups and take-it-or-leave-it

<Smaller items; a short list is fine when they're parallel. Each entry says its disposition.>

## Tests

<What the tests prove, what's missing, what you ran.>
```

Omit any section with nothing in it — empty sections are scaffolding. When the user asks for it or the list is long, close with a short action checklist (`- [ ]` one line per action, matching the findings one-for-one).

No fixed length. A clean PR earns three sentences; a loaded one earns as much as its findings demand — and nothing more. Quote code sparingly (3–10 lines, fenced with a language tag; `<details>` for anything longer).

## Mechanics that prevent broken output (unchanged, non-negotiable)

| Never | Why |
|---|---|
| `#N` / `GH-N` / bare issue numbers as references or labels | GitHub auto-links to unrelated PRs/issues |
| `@username` mentions | Unwanted notifications |
| `Fixes/Closes/Resolves #N` | Auto-closes issues on merge |
| Absolute local paths (`/Users/...`, `/home/...`) | Leaks local environment |
| Pasting full files | Unreadable; GitHub truncates |
| The internal checklist verbatim | The output is the findings the checklist produced |

Links: repo-relative `path/to/file.ts:42` by default; `[file.ts:42](path#L42)` only when anchors resolve; commit short-hashes linked when reviewing on GitHub.

## Copy-paste safety check (before delivering)

- [ ] No `#N` outside code fences; no `@mentions`; no `Fixes/Closes #N`; no local paths.
- [ ] No hard-wrapped prose — every paragraph is one logical line.
- [ ] Scannable: real `##`/`###` headings when there are more than ~2 findings; no paragraph over ~5 sentences; no wall of text.
- [ ] Verdict not inflated: Request changes only if a finding meets the Blocker bar; "Needs to change before merge" contains only true Blockers.
- [ ] Reads aloud like a person: no label-lines, no finding IDs, no emoji headers, no metadata table.
- [ ] Every finding has file:line evidence in the sentence and a disposition.
- [ ] Renders cleanly (fences closed, no broken tables).

## Raising specific finding kinds (same voice)

- **Security:** state the assumption, why it's wrong or unverified, the blast radius, and the fix — as sentences: "This assumes the body is the signed content, but the provider signs a constructed string — anyone can forge the webhook. Implement the `x-signature` check per the official docs before merge."
- **Comprehension:** quote or link the block and ask for the *why* ("Why this dispatch table instead of the strategy pattern already in `payment_strategies.py`?"); the PR shouldn't merge until the rationale is defended and captured durably or the block is rewritten with understanding.
- **AI-generated code in a high-risk path:** name the assumption in the code, where to verify it (official docs/reference implementation), and the risk if it's wrong — and require that verification before merge.
