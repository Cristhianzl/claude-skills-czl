# Accessibility

The floor is non-negotiable: a UI that a keyboard or screen-reader user can't operate is broken, not unpolished. Most of this is plain HTML/CSS/ARIA and applies to any framework.

## Semantic HTML before ARIA

- Use the native element first: `<button>` for actions, `<a href>` for navigation, `<label>`, `<table>`, `<ul>/<ol>`, `<nav>`, `<main>`, `<dialog>`. ARIA is a patch for when no native element fits — the first rule of ARIA is don't use ARIA.
- **Never** a clickable `<div>`/`<span>` for an action — it loses focusability, keyboard activation, and role. If you must, add `role`, `tabindex="0"`, and key handlers (Enter/Space) — but prefer the real element.
- One `<h1>` per page; headings are sequential (`h1→h2→h3`, no skipped levels). Provide a skip-to-content link.
- Landmarks: a single `main`, plus `nav`/`header`/`footer` so AT users can jump.

## Names, roles, alt text

- Every control has an accessible name: a visible `<label>`, `aria-label`, or `aria-labelledby`.
- Icon-only buttons need `aria-label`.
- Meaningful images need `alt`; decorative images use `alt=""` and decorative icons use `aria-hidden="true"`.
- **Fixability gate:** alt text, labels, and error copy are *contextual* — if you don't know the real text, leave a `TODO` with what's needed. **Never invent** alt text or labels just to satisfy the rule.

## Keyboard & focus

- Everything interactive is reachable and operable by keyboard; tab order follows visual order.
- Visible focus always: use `:focus-visible`; **never** `outline: none` without an equivalent visible replacement (ring/border).
- Manage focus on state changes: move focus into an opened dialog (and trap it), restore it on close, close on `Escape`; on route change move focus to the main region; on form submit focus the first invalid field.
- No keyboard traps; group related controls with `:focus-within` where helpful.

## Color & motion

- Text contrast ≥ 4.5:1 (≥ 3:1 for large text / UI components). Never convey meaning by color alone — pair with text, icon, or pattern.
- Honor `prefers-reduced-motion` (reduce/disable non-essential animation). Support OS text scaling/zoom up to 200% without clipping; don't lock orientation.

## Forms (a11y specifics)

- Programmatically associate label↔control; show errors inline next to the field and announce them (`role="alert"` / `aria-live="assertive"`); provide an error summary that links to fields for long forms.
- Async/status updates (toasts, validation, save state) use `aria-live="polite"` and must not steal focus.

## Test & verify accessibility

- **Audit the rendered DOM, not just source** — most violations appear only after JS runs.
- Add automated a11y assertions to tests (axe-core / `toBeAccessible()` style); ratchet existing debt with a snapshot/baseline and gate on new violations.
- Automated tools catch the *mechanical* layer only. Manual review is still required for: screen-reader announcement quality, keyboard-flow coherence, content clarity, and nuanced contrast. Flag those for human review — don't guess.
