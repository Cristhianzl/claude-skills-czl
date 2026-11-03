# Simplicity first — the root directive for every UI

> Make it as polished as Linear's website or Apple Notes — the benchmark for restraint: **simple purpose, simple architecture, simple design, simple implementation.** Cut taglines, helper text, and secondary labels. **If a screen needs them to make sense, fix the layout.** Every decision must raise the **user experience (UX)**, the **developer experience (DX)**, and the **agent experience (AX)** at once — **without breaking anything.**

Every other rule in this skill is an application of that paragraph. Accessibility, tokens, states, and the anti-vibe audit tell you what *must* be there; this directive tells you to remove everything else. Generators add; designers edit.

## The four simples

| Simple… | Means | The check |
|---|---|---|
| **Purpose** | Each screen has one job and one primary action | You can state the screen's job in one sentence without "and" |
| **Architecture** | Few routes, few states, shallow navigation, state that lives in one place | Every route and every piece of state answers to a user need; no screen exists "because apps have one" |
| **Design** | Hierarchy carried by layout, size, spacing, and order — not by extra words, boxes, colors, or icons | Squint test: the primary action and the main content are obvious with the text blurred |
| **Implementation** | The fewest components, props, and dependencies that do the job; the platform before a library | A new developer (or agent) can find, read, and change the screen without a tour |

## Words are the last resort — the layout-fix ladder

When a screen seems to need a tagline, helper line, subtitle, tooltip, or secondary label to make sense, **the layout is wrong.** Climb this ladder and stop at the first rung that removes the need:

1. **Rename** — the label/heading says exactly what it is, in the user's words ("Due date", not "Date" + helper "When this task is due").
2. **Remove** — the element, field, or option isn't needed at all (or has a sensible default).
3. **Reorder and group** — proximity and order explain the relationship; a field next to what it affects needs no explanation.
4. **Show, don't tell** — a good default, a preview, a visible affordance, the input format in the control itself (date picker, currency prefix, unit suffix).
5. **Disclose progressively** — advanced options behind one clear control, not explained inline.
6. **Teach by acting** — an empty state is one line plus the first action, not a paragraph.
7. **Only then** — one short helper line, because the information is genuinely not expressible in the layout (a constraint the user can't infer: "8+ characters, one number").

### What to cut by default

- Taglines and slogans under page or section headings ("Manage everything in one place").
- Helper text that restates its label ("Email — Enter your email address").
- Secondary labels and eyebrows above headings, captions under self-explanatory images, descriptions under obvious section titles.
- Tooltips that explain what a clear label already says.
- Redundant confirmations of what the user can see ("Your items are listed below").
- Duplicate actions (the same command as a button, a link, and a menu item on one screen).

### What is never cut (simplicity never overrides these)

- **Labels and accessible names** — every control keeps a visible label (or `aria-label` for an icon-only button); a placeholder is not a label. Cutting helper text never means cutting the label.
- **Error messages** and the next step to fix them; **validation constraints** the user can't infer.
- **Destructive-action consequences** ("Deletes 12 tasks permanently") and confirmation of irreversible steps.
- **Legal, consent, privacy, pricing, and safety text** required to be shown.
- **Units, formats, and states** that change meaning (currency, time zone, "draft", "read-only").
- The accessibility floor and the security/PII rules — always ranked above simplicity.

## UX + DX + AX — every decision, all three at once

A choice that helps one and hurts another is the wrong choice; find the one that helps all three. Usually the simplest option does.

| | What it means here | Concrete checks |
|---|---|---|
| **UX** — the person using it | Fewer things to read, decide, and click to reach the goal | One primary action; the primary flow takes the fewest steps; every state (loading, error, empty, long content) handled; works on a phone with one thumb |
| **DX** — the developer changing it | Code that is obvious to read and safe to change | Reuse existing components and tokens; small single-purpose components; typed props; variants over boolean flags; no clever abstractions; colocated tests |
| **AX** — the agent using or changing it | Browser/computer-use agents read the **accessibility tree**, not pixels; coding agents read the code | Semantic HTML and landmarks; every control has an accessible name that matches its visible text; actions are real `<button>`s and links are real `<a href>`; navigable state lives in the URL; no hover-only or drag-only controls without a clickable alternative; states exposed with ARIA/attributes (`aria-expanded`, `aria-busy`, `disabled`) not only with color; stable, conventional file and component names |

Most AX wins are accessibility wins: a UI a screen reader can drive is a UI an agent can drive.

## Without breaking anything

- **Existing products:** this directive governs **new UI and the lines in the requested change**. Removing existing copy, fields, or screens is a product change — **propose it, don't do it** (it goes to the parking lot; see `guarding-scope`). An existing design system remains the law.
- **Simplifying is not deleting behavior.** Removing a label, option, or step must not remove a capability someone depends on, break a saved state, a deep link, a test selector, or an i18n key in use. When you remove a translated string, remove its key from **every** locale.
- **Verify after cutting:** the flow still completes, the accessibility scan still passes, the tests still pass.

## The mute test (run before calling any screen done)

Hide every tagline, helper line, subtitle, tooltip, and secondary label on the screen. **Can a first-time user still understand the screen and complete its primary action?**

- Yes → keep them cut.
- No → don't put the words back first; climb the layout-fix ladder. A helper line survives only at rung 7, and you can say why the layout can't carry it.

Report it in the delivery: `Mute test: passed` or the specific lines kept and the reason for each.
