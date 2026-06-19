# Learnings — read before, append after

This folder accumulates Langflow-specific lessons that aren't obvious from the main SKILL.md, `references/`, or `AGENTS.md`. It is the **memory of the skill**.

The protocol below applies to **every** skill that has a `learnings/` folder.

---

## Before generating: read

List this folder and read every file whose name looks relevant to the current component (provider, bundle, SDK, runtime). Provider quirks, SDK traps, deprecation policies, icon registration gotchas live here. If a learning contradicts a default in `SKILL.md`, the learning wins — mention it to the user.

If `learnings/` is empty except for this README, proceed with the SKILL.md defaults.

---

## After completing: append (only when warranted)

Append a new learning only if you discovered something that:

- Was **not obvious** from `SKILL.md`, `references/`, `AGENTS.md`, or `BUNDLE_API.md`.
- Would have **changed how you started** if you had known it.
- Is **likely to apply again** to this user / project / provider.
- Is a **convention, constraint, or trap** — not a one-off fact about the current component.

Do **not** append:

- A summary of the component you just built.
- Restatements of the SKILL.md content.
- Ephemeral facts ("today I added 3 inputs").
- Anything you can't state as a rule applicable to a future component.

---

## Append protocol

**Filename:** `YYYY-MM-DD-short-kebab-slug.md` — use the real date.

**Body:**

```markdown
---
trigger: <one-line: when does this learning apply?>
---

# <Title — what the rule is, in one short phrase>

**Context:** <one or two sentences — the situation where the lesson surfaced>

**Lesson:** <the rule itself, stated so it can be applied without re-reading the context>

**Why:** <the reason — incident, preference, convention, technical constraint>

**Apply when:** <the trigger condition, more precise than the frontmatter>
```

Keep the body under 30 lines.

---

## How learnings interact with the SKILL.md

- `SKILL.md` is the **default behavior**.
- `references/` are the **detailed defaults**, loaded on demand.
- `learnings/` are the **overrides** — narrower, Langflow-version-specific or provider-specific, accumulated over time.

When a learning conflicts with the SKILL.md, follow the learning **and mention it** to the user so they can correct or refine it.

---

## Examples of good learnings for this skill (illustrative — delete when real ones land)

- `2026-02-12-acme-sdk-needs-explicit-async-client.md` — "The Acme SDK's `Client` blocks the event loop in async flows. For agent-callable components, use `AsyncClient` and `await client.chat(...)`. Documented under `lfx.schema.tool_async`."
- `2026-03-04-anthropic-streaming-uses-events.md` — "Anthropic's streaming API yields typed events, not raw chunks. Iterate `for event in stream` and dispatch on `event.type`. Plain string concat misses tool-call deltas."
- `2026-04-21-chroma-component-uses-context-not-init.md` — "Chroma vector store components must accept the collection from a parent `ChromaContextComponent` via `HandleInput`, never instantiate Chroma in `__init__`. See `services/storage/chroma.py`."
- `2026-05-08-add-tests-when-adding-bundle-component.md` — "Every new component added to a bundle must include tests in `src/bundles/<name>/tests/` AND an entry in BUNDLE_API.md. The pre-commit gate enforces both."

Examples of bad learnings (do not write these):

- `2026-05-01-built-the-acme-chat-component.md` — describes a specific component, not a reusable rule.
- `2026-05-12-use-component-class.md` — already in SKILL.md; duplication.
- `2026-05-15-icons-are-tricky.md` — opinion without an observed trigger.

---

## Maintenance

When a learning becomes stale (the SDK changed, the convention evolved), **delete the file** rather than editing it in place. Git history preserves the older version; the folder reflects what is currently true.

When two learnings overlap, merge them and delete the duplicate.
