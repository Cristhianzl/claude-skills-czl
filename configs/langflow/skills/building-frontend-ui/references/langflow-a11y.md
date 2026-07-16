# Langflow frontend accessibility — machinery & gotchas

Langflow-specific a11y knowledge, owned by this config (not dependent on any in-repo agent docs). The standard is **WCAG 2.2** ([official W3C quickref](https://www.w3.org/WAI/WCAG22/quickref/)); composite-widget behavior follows the [W3C ARIA APG patterns](https://www.w3.org/WAI/ARIA/apg/patterns/). Generic floor: `accessibility.md` (this folder).

## The bar: two engines, every meaningful state

The frontend ships **two scan engines — both must report zero**; they catch different bug classes (one is strong on contrast/labels; the other is stricter on ARIA structure and keyboard semantics, and catches real WCAG issues the first passes silently):

- **Jest + axe** (`@/utils/a11y-test`, jsdom): fast, component-level. Note: `color-contrast` is disabled in jsdom (can't measure layout). Tests live at `__tests__/<name>.a11y.test.tsx`.
- **Playwright live-DOM scan — `page.runA11yScan(label)`**: scans the browser DOM *after your interactions*, so it sees open modals/menus, selected and editing states. Specs live at `src/frontend/tests/a11y/<feature>.a11y.spec.ts`.

```bash
cd src/frontend
npx jest path/to/<name>.a11y.test.tsx --runInBand
RUN_A11Y=true RUN_A11Y_ASSERT=true npx playwright test tests/a11y/<feature>.a11y.spec.ts --project=chromium --workers=5
```

`RUN_A11Y=true` runs the scans; `RUN_A11Y_ASSERT=true` makes new violations fail (without it the scan is informational). There is also a route batch scanner (`scripts/a11y/a11y_scan.py`, routes in `scripts/a11y/a11y_routes.json`) for default-loaded pages only.

**Scan the state matrix, not just default render:** populated, empty, loading, error/validation visible, modal/dropdown open, selected/expanded row, mobile viewport. After changing a shared component, re-scan **every page that uses it**.

## Structure violations the stricter engine catches (all real WCAG)

| Typical cause | WCAG |
|---|---|
| Tabbable element with `role="presentation"` / no widget role (focus sentinels, wrappers) | 4.1.2 |
| `rowgroup`/`list`/`tablist` owning no valid child role | 1.3.1 |
| Composite widget with no tabbable descendant (needs roving `tabindex`) | 2.1.1 / 4.1.2 |
| Focusable element inside `aria-hidden="true"` | 4.1.2 |
| Widget role with no accessible name (e.g. an icon-only grid column header) | 4.1.2 |
| Content outside any landmark (portaled menus/popovers to `<body>`) — often app-wide debt → baseline it | 1.3.1 |

Rule of thumb: touched a table/tree/listbox/menu → run the live-DOM scan.

## AG Grid (the shared `TableComponent`) gotchas

- **Disabled paging buttons**: `tabindex="-1"`, but never `inert`/`disabled` — that breaks the grid's tab guards and traps Shift+Tab entry (WCAG 2.1.2).
- **Icon-only/action column header**: the accessible name comes from `field`/`headerName`; a column with neither is nameless (4.1.2). Give it a `headerName` and visually hide it via `headerClass` (sr-only clip).
- **Interactive control inside a cell**: the grid navigates cell-by-cell and never tab-focuses the inner control — activate it from `onCellKeyDown` on Enter/Space. A Radix trigger opens on keydown, not synthetic `.click()` — focus the trigger and re-dispatch the key (guard against re-entry).
- **Borderless grids** (`.ag-no-border`) suppress the cell focus outline (2.4.7) — restore with a scoped `:focus-visible` ring. Verify with a clean first-interaction page (a session that already used the keyboard contaminates `:focus-visible`).
- Set `ensureDomOrder: true` so DOM order matches visual order (2.4.3).
- **Keyboard map for selectable rows** (reference: `GlobalVariablesPage`): **Space** toggles selection, **Enter** opens edit. Implement with page-level `onCellKeyDown` + `suppressKeyboardEvent` for those keys; sync React selection state after `node.setSelected`.
- **Focus restore on modal close (2.4.3)**: remember the focused cell (`rowIndex` + `colId`); on Escape/Cancel/save restore via `api.setFocusedCell` + DOM `.focus()` across a few `requestAnimationFrame`s (to outlast dialog focus cleanup). Verify with a keyboard test: open from a cell → Escape → focus is on that cell → Enter opens again.

## Radix (shadcn) gotchas

- **`Trigger asChild`**: a Dialog/DropdownMenu trigger wrapping a real `<button>` **without `asChild`** renders nested buttons → two consecutive tab stops (2.4.3). Always pass `asChild` when the child is interactive.
- **Focus-restore race**: on close, Radix restores focus to its trigger once, asynchronously. If your action moves focus elsewhere (e.g. inline editor), re-assert focus across a few `requestAnimationFrame`s to outlast it.
- **Portaled menu content** lands outside any landmark (1.3.1) and `<main>` is `overflow-hidden` (can't re-portal). Treat as tracked debt → baseline it; cover the menu's real a11y (role, named trigger, keyboard open/close, focus restore) with a keyboard test instead.

## Baselines — accepting known framework debt

Some violations are real but framework-level and can't be fixed per-page. Track them in a **committed baseline** so scans stay green while the debt is recorded — never silently drop the scan or the assertion. Baselines live in `src/frontend/tests/a11y/baselines/{project}__{label}.json`, matched by rule + DOM path; a minimal file (only the entries to ignore, with a `description` of why) is clearest. **Deleting the baseline resurfaces the violation.** Matching is exact-DOM-path — scan with no other overlays (toasts) open, or the path shifts and the baseline goes stale.

## Manual spot checks scanners can't do

Tab **and Shift+Tab** through the surface (2.1.1/2.1.2, no trap either way); Escape closes overlays; focus order matches visual order and the ring is visible (2.4.3/2.4.7); 320px width / 400% zoom reflows without horizontal scroll (1.4.10); status/errors not color-only (1.4.1); errors named in text and tied to fields (3.3.1/3.3.2).
