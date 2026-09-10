---
description: Frontend — enforced essentials for UI code (reuse, accessibility, security, components)
globs: "**/*.{tsx,jsx,vue,svelte,astro,mdx,css,scss}"
---

# Frontend

> Prerequisite: `CLAUDE.md` (general baseline). Depth: `skills/building-frontend-ui` (and its `references/`).

The short, non-negotiable subset. The skill carries the full reasoning, checklists, and per-framework detail.

## Reuse first

- Before creating anything, grep for an existing component/utility that does the job and **reuse or extend it**.
- Use the project's design tokens / theme. **Never hardcode raw hex, spacing, or font sizes** in a component — reference the token source. Before defining a new color, sweep the existing palette — a token duplicating a color that already has a name is a defect (enforced by `hooks/check-design-tokens.py`).

## Components

- Small, single responsibility, one component per file.
- Composition over configuration; prefer explicit variant components over boolean-flag combinations.
- Never define a component inside another component.
- Type props and state fully (no `any`); stable list keys (not the array index when items reorder).
- Handle loading, error, empty, and long-content states.

## Accessibility (floor)

- Semantic HTML before ARIA: `<button>` for actions, `<a>` for navigation — never a clickable `<div>`.
- Every control has a label; meaningful images have `alt` (`alt=""` if decorative); icon-only buttons have `aria-label`.
- Keyboard operable; visible focus — never remove the focus outline without replacing it.
- Honor `prefers-reduced-motion`.
- Never invent alt text, labels, or copy — leave a `TODO` for contextual/visual decisions.

## Security & PII (client)

- No tokens or secrets in `localStorage`/`sessionStorage` — prefer httpOnly cookies.
- Never render untrusted HTML without sanitizing (`dangerouslySetInnerHTML` / `innerHTML`).
- Don't leak PII into props/markup/logs/analytics. No `console.log` in production.

## State & data

- Keep data fetching out of leaf components.
- Derive state instead of duplicating it; reflect navigable state (filters, tabs, pagination) in the URL.

## Anti vibe-coded (floor)

- **Existing design system = the law.** Follow its tokens, components, and layout; never introduce a parallel style.
- **From-scratch UI**: before calling it done, run the Vibe Check + delivery scorecard in `skills/building-frontend-ui/references/anti-vibe-coded.md`. The floor: zero emoji/sparkles in UI, no purple/gradient without brand justification, ≤3 border radii, ≤2 shadows, spacing 100% on the 4/8pt scale, one real `<h1>` + semantic landmarks, zero dead clicks / `href="#"`, loading state on every async action, no unmarked placeholder or fake testimonial.

## i18n (when the project has one)

- If the repo has a `locales/` dir or i18n config, **never hardcode a user-facing string** — use the translation function.
- Every new translation key is added to **every** locale file; a key missing in one language is a bug.
