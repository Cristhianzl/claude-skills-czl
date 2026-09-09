# Design craft — typography, color, space, motion

The decision layer above implementation: the rules that make a UI read as *designed* rather than *generated*. The governing principle is **one decision, one reason** — if you can't say why this font/color/spacing is what it is, it isn't a decision yet, it's a default. And **dare in one place only**: one memorable element per page; everything else disciplined and quiet.

## Typography

- **One family for most projects; two at the absolute max** — and then they must be *obviously* different (display vs body), with fixed roles: display only in headings, body everywhere else.
- **Skip weights for contrast**: `Light ↔ Medium`, `Regular ↔ Bold`. Adjacent weights (`Regular ↔ Medium`) read as a mistake, not hierarchy.
- The type scale is **fixed and comes from tokens** — never "this heading looks better at 27px". Headings `line-height` 110–125%; body 140–160% (large text needs less, small text needs more).
- Body text is **left-aligned**; center only short blocks (hero, CTA); **never justify** on the web.
- **No pure `#000` on `#FFF`** (use near-black like `#16181D`); no pure white text on dark backgrounds.
- A beautiful display face that's fragile at small sizes (thin strokes, high contrast) **doesn't qualify for body** — test any candidate at 14px before adopting it.
- Font delivery: ≤4 files, `woff2`, subset, `font-display: swap`, preload only the hero face.

## Color

- **60/30/10**: ~60% base/background, ~30% surfaces/secondary, ~10% accent. The action color works *because it is scarce*.
- **~6 base colors + states, max.** A large palette is a symptom of indecision, not richness.
- Choose a **named harmony** deliberately — analogous (calm), complementary (tension), triad (energy) — and be able to say which and why. Color psychology is context, not law (blue→trust, red→urgency, green→growth…), and culture shifts it; consider the audience.
- Color is defined by **role** (`--text-muted`), never by appearance (`--light-gray-2`); switching themes must not rename anything.
- If you need a value outside the scale, either the scale is wrong or the decision is — **fix the scale**, don't add a magic value.
- Dark mode is not inversion: desaturate accents, create elevation with surfaces (not heavy shadows). Contrast floors (AA, all states including hover/disabled) live in `accessibility.md`.

## Space & layout

- **8pt grid**: spacing, padding, margins, and icon sizes in multiples of 8 (8/16/24/32/48/64/96); **4pt only for intimate pairs** (label↔input, icon↔text).
- **Vertical rhythm**: space *between sections* > space *within a section* > space *between sibling elements*. Invert that and the page feels loose and ungrouped. Keep section padding constant across the page (desktop ~96–128px, mobile ~48–72px) — random variation is the amateur tell.
- **Alignment to a few vertical lines** is what reads professional. Asymmetry only when intentional and balanced (one large block ≈ several small ones).
- **Proximity replaces ~90% of borders and dividers**: related things sit together, unrelated things sit apart. **Repetition**: the same kind of content always uses the same component with the same spacing.
- `max-width` on text blocks (~65ch) and `min-width` on cards — otherwise the layout stretches ugly at 1920px and crushes at 360px.

## Motion

- Motion **responds to an action and shows what changed** — open, expand, confirm, navigate. Decoration is not a reason.
- 120–250ms for micro-interactions, up to 400ms for layout transitions; eased (never `linear`).
- **One orchestrated moment per page.** Fade-and-slide on every section plus animated hover on every card is the generated-template look.
- Never move content while someone is reading it. Always honor `prefers-reduced-motion`.

## Anti-patterns — the tells of a generated page

Avoid unless the brief explicitly asks:

1. Cream background + high-contrast serif + terracotta accent (the default "AI landing page" palette).
2. Near-black background with a single acid-green or hot-red accent.
3. Everything diced into identical cards — same radius on every element, same gray shadow on everything, gradients as ornament.
4. `UPPERCASE EYEBROW` labels above every heading; metadata joined by `·`; an `→` glued to every button label.
5. Decorative "almost black" (`#0B0B0B`, `#111`) pretending to be black; monospace on every small label.
6. Numbered markers `01 / 02 / 03` on content that is **not** a sequence.
7. Generic icon salad (rocket, lightbulb, target) with no relation to the content.
8. "Big number + label + gradient" hero as the default for any business.
9. Auto-advancing hero carousel (nobody sees slide 2).
10. Text over a photo without a guaranteed-contrast overlay.
11. Lorem ipsum delivered as if it were content.

The test: **if the result could belong to any company in any sector, it's wrong.** Identity comes from the subject — the materials, vocabulary, setting, and audience of *this* business.

This list is the design-time lens. The full delivery audit — Vibe Check, console script, five final tests, and the blocker scorecard — lives in `anti-vibe-coded.md` and is mandatory before declaring from-scratch work done.

## See also

- `ux-writing.md` — type-scale mechanics, microcopy, typographic details.
- `accessibility.md` — contrast floors, focus, reduced motion (the non-negotiables).
- `designing-from-scratch.md` — where these decisions get made in order.
