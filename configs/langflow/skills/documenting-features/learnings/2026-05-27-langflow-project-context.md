---
trigger: Any documentation task in /Users/criszl/Documents/langflow.
---

# Langflow project context

**Context:** Documentation tasks in Langflow — visual flow builder for AI agents. The docs site uses Docusaurus; component docs live in the contributing section; bundles have their own `BUNDLE_API.md`.

**Lesson:** Treat `AGENTS.md` at the repo root as canonical. Documentation source files live in `docs/docs/`, served by Docusaurus.

**Why:** The generic SKILL.md template covers feature docs as a single `.md` file at `docs/features/<feature>.md`. Langflow's docs are organized differently (Docusaurus categories, contributing guides, API reference, partials). Use the existing convention.

**Apply when:** Always, on any docs-writing task in this repo.

## Documentation map

| What you're documenting                                          | Where it goes                                                              |
|------------------------------------------------------------------|-----------------------------------------------------------------------------|
| User-facing feature concept                                       | `docs/docs/Concepts/<feature>.mdx`                                          |
| New component (user guide)                                        | `docs/docs/Components/<provider>/<component>.mdx`                           |
| Bundle public surface                                             | `src/bundles/<bundle>/BUNDLE_API.md` (changelog gate, enforced)            |
| Contributing a new component (developer guide)                    | `docs/docs/Contributing/contributing-components.mdx`                        |
| Deployment / environment                                          | `docs/docs/Deployment/<topic>.mdx`                                          |
| API reference                                                     | `docs/docs/API-Reference/` (generated from FastAPI where possible)         |
| Reusable doc snippets                                              | `docs/docs/_partial-*.mdx`                                                  |
| ADRs (architecture decisions)                                     | Inline in PR description's `## Design Decisions`, OR `docs/adr/NNNN-slug.md` if a project-wide pattern emerges |
| Internal dev guide                                                | `AGENTS.md` (canonical) and `DEVELOPMENT.md`                                |

## Running the docs site

```bash
cd /Users/criszl/Documents/langflow/docs
yarn install
yarn start          # Dev server on :3000 (prompts for :3001 if 3000 is busy)
```

## Conventions

- Docusaurus uses `.mdx` (Markdown + JSX). Prefer JSX components for callouts and admonitions.
- Headings start at `##` (the page title is `#` from front-matter).
- Code fences with language tags for syntax highlighting (`bash`, `python`, `typescript`).
- Internal links use `[Text](/path/to/page)` (no `.mdx` extension).
- Reusable content goes in `_partial-*.mdx` and is imported with `import PartialName from './_partial-name.mdx'`.

## The generic SKILL.md still applies — with adaptations

The 10-section template (`developing-features/references/template.md`) is for **feature design documentation** that lives alongside the code. For user-facing Docusaurus pages, the structure is lighter:

- Section 1 (Overview) → page intro + use cases.
- Section 4 (Behaviors) → "How to use" with concrete examples.
- Section 6 (Technical Spec) → "Configuration" with input/output tables.
- Section 10 (Platform Compatibility) → "Requirements" if non-obvious.

Sections 2, 3, 5, 7, 8, 9 are typically engineering-internal — keep them in design docs / ADRs, not on the public site.
