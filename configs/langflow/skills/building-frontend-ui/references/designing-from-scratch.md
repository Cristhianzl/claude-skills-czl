# Designing from scratch — strategy → structure → visual

Read this when building a UI, site, or product surface **from zero** (no existing design to extend). The order is non-negotiable: **strategy → structure (sitemap/wireframe) → design system → screens**. Content before layout; structure before aesthetics; **no code before the plan**. Skipping a phase is how expensive rework happens.

## Strategy first (the project's compass)

- **One measurable goal.** Nearly every request is one of: sales (conversion/revenue), traffic/leads (sessions/signups), or reputation (time on page, inquiries). If nobody can name the goal, the project has no success criterion — force the definition before designing.
- **One primary action per page.** Write down what it is. The nav CTA and the hero CTA are the same action.
- **Scan the field**: 5–10 sites in the sector, 3–5 outside it; note what works and what doesn't — *and why*. Never copy because someone "liked it"; ask *what* they liked (the answer is almost always functional, not aesthetic).
- **One sentence of strategy** before any pixel — e.g. "Turn out-of-town visitors into bookings by proving safety and professionalism within 10 seconds."
- Missing answers (audience, goal, tone, constraints)? Ask 3–5 objective questions, or **declare assumptions at the top of the plan** and flag them for confirmation.

## The design plan — delivered as text BEFORE any code

```
Subject & audience: …
Primary goal & target action: …
Concept (1 sentence): …
Palette (4–6 hex, each with a role): …
Typography (families, roles, scale): …
Layout (ASCII wireframe of the main sections + alignment): …
Where the one bold element is: …
What we will NOT do (anti-patterns avoided): …
Assumptions to confirm: …
```

Then **self-critique before coding**: *"Would I produce exactly this for any other client of the same type?"* If yes, the generic part gets revised — and say what changed and why. (Anti-pattern list: `design-craft.md`.)

## Structure (UX before UI)

- **Sitemap**: pages that are *needed*, not *nice*. A young business with little content and a single target action → a **one-pager** is the right call. For each page: objective, primary action, who lands on it, and from where.
- **Pages → sections → elements.** Sections are chapters: each does one job and pushes to the next. The job list: nav orients; **hero answers in ~5 seconds — what is this, for whom, why stay, and the next step**; social proof reduces risk (it moves *up* when the brand is unknown or the purchase is high-risk); features translate *what it is* into *what changes for the user*; pricing removes the blocking doubt; FAQ kills objections before the form; CTA asks plainly; footer closes with access to everything plus legal.
- **Content hierarchy inside a section**: eyebrow/context (optional) → title (the promise) → short paragraph (the proof) → action. One `h1` per page. Section headings sell the benefit, not the category — "Book in 2 minutes" beats "Our services".
- **Wireframe in gray** — no color, no photos, no nice fonts; boxes, hierarchy, and *real text*. It answers one question: does the content make sense in this order? Do desktop **and** mobile for key pages; **if a section doesn't survive 375px, the section is wrong.** Proven patterns (hero = headline + sub + CTA + image; 3-card grid; accordion FAQ) are tested shortcuts, not laziness — personalize what differentiates, not what already works.

## Tokens before components, components before pages

Define the tokens first (color roles, 4/8pt space scale, type scale, radius/shadow/motion) and use only them — zero magic values. Then base components (button, field, card, nav, footer) with **all** states, then pages assembled from them, then responsive + empty/loading/error passes, then the audit (pre-delivery checklist + `accessibility.md`). Craft rules: `design-craft.md`.

## Content honesty

- **No lorem ipsum delivered as content.** If there's no copy, draft plausible copy and flag it as provisional.
- Numbers, testimonials, client logos, and certifications are `[PLACEHOLDER]` until confirmed — **never invent institutional facts as if true**.

## SEO & technical foundation (floor)

One `h1` and a real heading hierarchy; unique `title` (≤60 chars) and `meta description` (≤155) per page; Open Graph + social image; clean descriptive URLs, `canonical`, `sitemap.xml`, `robots.txt`; structured data where it applies (`LocalBusiness`, `Product`, `Article`, `FAQPage`); links with descriptive text (never "click here"); legal pages exist (privacy, terms, cookies); a useful `404` with a way back.

## Delivery

Close with: **decisions made** (each with its reason), **assumptions**, **pending items** (real content, images, font licenses), and **what to measure**. Never announce "done" while a mandatory item fails — say what's missing instead.

## Changing an existing site instead?

Inventory before touching anything (stack, existing tokens and components — **use them; never introduce a parallel system**). Diagnose with evidence, not opinion. Fix in impact order: accessibility + functional breakage → hero/primary-action clarity → token consistency (usually kills half the "amateur feel") → rhythm and type hierarchy → performance → aesthetic polish. Changes are surgical and reversible — one theme per change, justified by an observed problem; no full redesign without an explicit ask.
