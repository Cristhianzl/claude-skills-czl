# Anti vibe-coded — proving nobody will call it "generated"

`design-craft.md` says how to design well. This file says **what betrays that nobody designed it** — and how to prove that's not the case. **Before declaring any from-scratch UI delivery done, run the Vibe Check and the Scorecard below and report item by item.**

**Scope rule:** this audit is mandatory for **from-scratch** work (new site, new product surface, greenfield page). When a design system already exists, **the existing system is the law** — follow its tokens, components, and layout (Step 0 of the SKILL); never use these rules to justify restyling what's already consistent. On existing systems, only the *functional* layers apply (states, dead clicks, semantics, mobile, a11y).

## The thesis

A site doesn't look vibe-coded because of the tool or the speed. It looks vibe-coded because of **inconsistency, randomness, and the absence of a system** holding it together. No single fatal error — the sum of twenty decisions nobody made: seven border radii, four shadows, spacing without rhythm, a component that changes per page, a button that doesn't respond. Each is small; together they scream.

Two corollaries:
- **The fastest path to premium is consistency, not visual novelty.** Less effect, more deliberate repetition.
- Vibe-coded sites are **pretty and hollow**: the screenshot passes; what fails is everything that only shows when someone clicks, shares, or opens it on a phone. (Audits of hundreds of shipped AI-generated sites found: 66% have **no `<h1>` tag** — a giant styled `div` instead; 62% no canonical; 29% touch targets under 44px; 18% dead clicks; 18% zoom blocked. Appearance without structure — and the cheapest fixes there are.)

## Layer A — the visual signature (recognized in 2 seconds)

- **The purple problem.** Purple gradients, neon purple glows, `from-purple-500 to-pink-500` — the unofficial mascot of generated design. Purple (and any colored gradient) only enters if the brand identity asks for it; if you can't say where it came from, it came from the generator.
- **Sparkles and emoji as UI.** ✨ in the hero, emoji in buttons, headings, or pricing bullets. **Zero emoji in interface elements.** Emoji in client-written content is their call; emoji in a button is yours — and it's wrong.
- **Hover on everything.** Cards that jump, rotate, or drift out of alignment; flashlight shadows; bouncing buttons. Hover is subtle or absent — a color/border change is enough. Pick **one** hover pattern and repeat it site-wide.
- **Giant icon, tiny text.** A 48px icon over 13px text inverts the hierarchy — ornament outweighs information. The icon is subordinate to the text; if it's bigger than its heading, shrink it or cut it.
- **Semi-transparent blurred header.** Legitimate only if tested scrolling over light **and** dark sections with AA contrast in both. A solid header is a valid, safer choice.
- **Bad animation.** Wiggles, overshoot bounces, scroll animations that jank or fire off-screen. 120–250ms, eased, never `linear`, one orchestrated moment per page, `prefers-reduced-motion` respected (see `design-craft.md`).
- **Generic fonts without rhythm.** Inter/Poppins/Montserrat are not the problem — the undeclared use is. One pair, a declared scale (size + weight + line-height per level). If Inter is the choice, make it a *choice* — stated in the plan.

## Layer B — absence of system (the root cause)

- **≤3 border radii** in the whole project (e.g. 6px controls, 12px surfaces, 999px pills), assigned by hierarchy, never by local taste.
- **One elevation style, ≤2 levels.** Shadow only where something actually floats.
- **Spacing 100% on the 4/8pt scale.** No 13px/27px/45px; equivalent sections get identical breathing room.
- **A component is defined once and reused.** Styling the same button a second time means the system failed.
- **Grid aligned to a few vertical lines** — verify with an overlay, not by eye. One pixel of misalignment kills the impression of care.

## Layer C — states and interaction (where the site proves it's real)

- Every action with latency gives feedback in **<100ms**; buttons get a loading state and block double-submit; data areas use skeletons with the **same height** as the final content (otherwise it's CLS).
- **Every interactive element is tested by clicking it.** No `href="#"` in production, no `cursor: pointer` without a handler, no tab/accordion/carousel/modal/toggle that doesn't work. A social icon without a real profile **does not ship**.
- **LCP < 2.5s, INP < 200ms, CLS < 0.1** — measured on simulated 4G, not your wi-fi.

## Layer D — content and copy

- **Empty taglines** ("Build your dreams", "Launch faster", "Where ideas become reality") signal copy written last, in five minutes. The hero says what the product does and for whom, in concrete language. Specific beats pretty.
- **Em-dash chains** (—) across the hero are the mark of generated, unedited text. Short sentences with periods read better.
- **Fake testimonials** — AI-face avatars, "Sarah Chen", no role/company/link, repeated phrasing, the same photo twice — are perceived instantly. A testimonial without a real person is a visible `[PLACEHOLDER: awaiting client testimonial]`. Better one section fewer than one section lying.
- **The footer is the last thing read**: dynamic year (`new Date().getFullYear()`), real business name, proofread text.
- **Overloaded hero**: one promise, one support line, one primary action; a second button only for a real second audience. After assembling, **remove one element**.
- **Forgotten placeholders**: lorem ipsum, `John Doe`, `example@email.com`, fake partner logos, invented metrics ("+500 clients"). **The substitution test:** swap the name and logo for a competitor's — whatever stays true is generic and must be rewritten.

## Layer E — technical foundation

- **Complete `<head>` on every page**: unique `title` (≤60, never "Home") and `meta description` (≤155), canonical, full OG + Twitter card with a real 1200×630 image (test the share on WhatsApp/LinkedIn), own favicon (never the framework default), `lang`, structured data where it applies. **Never** `user-scalable=no` / `maximum-scale=1` — blocking zoom is an accessibility failure.
- **Semantics before style**: exactly one real `<h1>` per page (a tag, not a `div` with `text-5xl`); no heading jumps; real `header/nav/main/section/footer`; actions are `<button>`, navigation is `<a href>` — `<div onClick>` is a bug waiting to happen.
- **Measurement**: if the site exists to convert — analytics installed *and tested*, events named for real actions, conversion pixel before the first campaign, consent before non-essential tracking. If the client won't run paid traffic, say so in the report instead of omitting the layer.
- **Files real sites have**: `robots.txt`, `sitemap.xml`, own 404, legal pages, `apple-touch-icon`, `og.png`, real contact.

## Layer F — mobile (test at real 375px, not zoomed-out responsive mode)

No overflowing text or collapsing cards; touch targets ≥44×44px with ≥8px separation (`p-2` + `text-sm` usually renders below this); zoom enabled; zero accidental horizontal scroll; every `<img>` with `width`/`height` or `aspect-ratio`; mobile menu opens, closes, closes on `Esc` and on link click, body doesn't scroll behind it. A11y floor: `accessibility.md`. Code floor (no secrets in the client, server-side validation, rate limiting, clean build): baseline `CLAUDE.md` + `security.md`.

## The Vibe Check (compact list)

Count what exists on the site. **5 or more = it reads as vibe-coded.**

Purple/gradient without brand justification · sparkle/emoji in UI · animated hover on every card · emoji in heading or button · fake/unverifiable testimonial · giant icon with tiny text · framework-default font with no declared decision · blurred header with contrast issues · >3 border radii · component inconsistent across pages · missing loading state · misaligned grid · slow interaction · jittery sticky header · off-scale spacing · no OG image · no own favicon · a control that doesn't work · broken mobile layout · live placeholder · generic tagline · wrong footer text/year · buzzword pile · no clear value proposition.

## The five final tests

1. **Substitution** — swap name/logo for the competitor's; what stays true is generic.
2. **Thumb** — real phone, one hand: complete the primary action with the thumb only.
3. **Blind click** — click everything that looks clickable, social icons and footer included; anything silent is a dead click.
4. **View-source** — is there an `<h1>`? `<main>`? canonical? OG? Or div soup?
5. **Removal** — delete one thing (the section that exists because "every site has one", the gradient, the third generic icon). Generators add; designers edit.

## Automated audit (paste in the browser console)

Run on **every page** at 375px and 1440px. Targets: `radii` ≤3 · `shadows` ≤2 · `fonts` ≤2 · `fontSizes` ≤8 · `offScaleSpacing` empty · `purpleGradients` 0 (unless brand) · `emojiInUI` 0 · `h1Count` 1 · `skippedHeadings` empty · `zoomBlocked` false · `missingLandmarks` empty · every counter in the last table 0 · `copyrightYear` current. Complement with Lighthouse (all categories ≥90) and axe.

```js
const els = [...document.querySelectorAll('body *')];
const cs = e => getComputedStyle(e);
const uniq = (fn, ignore = []) => [...new Set(els.map(fn).filter(v => v && !ignore.includes(v)))];

const consistency = {
  radii: uniq(e => cs(e).borderRadius, ['0px']),
  shadows: uniq(e => cs(e).boxShadow, ['none']),
  fonts: uniq(e => cs(e).fontFamily),
  fontSizes: uniq(e => cs(e).fontSize),
  offScaleSpacing: [...new Set(els.flatMap(e => {
    const s = cs(e);
    return [s.paddingTop, s.paddingBottom, s.paddingLeft, s.paddingRight,
            s.marginTop, s.marginBottom, s.gap]
      .map(parseFloat).filter(n => n > 0 && n % 4 !== 0);
  }))].sort((a, b) => a - b),
};

const signature = {
  purpleGradients: els.filter(e => /gradient/.test(cs(e).backgroundImage) &&
    /rgb\((1[0-9]{2}|[6-9][0-9]),\s*\d{1,2},\s*(1[5-9][0-9]|2[0-5][0-9])\)/.test(cs(e).backgroundImage)).length,
  emojiInUI: [...document.querySelectorAll('button,a,h1,h2,h3,label,[role=button]')]
    .filter(e => /\p{Extended_Pictographic}/u.test(e.textContent)).length,
  emDashes: (document.body.innerText.match(/—/g) || []).length,
};

const foundation = {
  h1Count: document.querySelectorAll('h1').length,
  skippedHeadings: (() => {
    const hs = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => +h.tagName[1]);
    return hs.filter((n, i) => i && n - hs[i - 1] > 1);
  })(),
  canonical: !!document.querySelector('link[rel=canonical]'),
  ogImage: !!document.querySelector('meta[property="og:image"]'),
  metaDescription: !!document.querySelector('meta[name=description]'),
  schema: document.querySelectorAll('script[type="application/ld+json"]').length,
  favicon: !!document.querySelector('link[rel~=icon]'),
  title: document.title,
  zoomBlocked: /user-scalable=no|maximum-scale=1/.test(
    document.querySelector('meta[name=viewport]')?.content || ''),
  missingLandmarks: ['header', 'nav', 'main', 'footer'].filter(t => !document.querySelector(t)),
};

const behavior = {
  imgMissingAlt: [...document.images].filter(i => !i.hasAttribute('alt')).length,
  imgMissingDims: [...document.images].filter(i => !i.width || !i.height).length,
  unlabeledFields: [...document.querySelectorAll('input,select,textarea')]
    .filter(el => !el.labels?.length && !el.getAttribute('aria-label')).length,
  emptyLinks: [...document.querySelectorAll('a')]
    .filter(a => { const h = a.getAttribute('href'); return !h || h === '#'; }).length,
  deadClicks: els.filter(e => cs(e).cursor === 'pointer' &&
    !e.closest('a,button,label,[role=button],[onclick]')).length,
  smallTargets: [...document.querySelectorAll('a,button,[role=button]')]
    .filter(el => {
      const b = el.getBoundingClientRect();
      return b.width && (b.width < 44 || b.height < 44);
    }).length,
  horizontalScroll: document.documentElement.scrollWidth > window.innerWidth,
  copyrightYear: document.body.innerText.match(/©\s*(\d{4})/)?.[1],
};

console.group('VIBE CHECK');
console.table(consistency); console.table(signature);
console.table(foundation); console.table(behavior);
console.groupEnd();
```

## Delivery scorecard (any blocker at ✗ = not done)

Blockers: unique semantic `<h1>` per page · heading hierarchy + landmarks · unique title/description · canonical · own OG image (share-tested) · own favicon · own 404 + legal pages · analytics tested (when conversion is the goal) · zero dead clicks / `href="#"` / decorative social icons · every widget actually works · form submits with loading/success/error and no double-send · loading state on every async action · ≤3 radii, ≤2 shadows, ≤2 fonts, spacing 100% on scale · components identical across pages, grid aligned · zero emoji/sparkle in UI, zero unjustified purple · copy survives the substitution test, one-promise hero · zero unmarked fake content, correct footer · targets ≥44px, zoom enabled, no horizontal scroll at 375px · alt + labels everywhere · visible focus + full keyboard · AA contrast in all states · images sized/optimized, CWV on target · no secrets in the client, server-side validation, rate limiting · Vibe Check < 5 · the five final tests passed. Non-blocking: schema.org, robots/sitemap, hover/motion polish.

**Final report format:**

```
Scorecard: X/28 | Vibe Check: N marks | Open blockers: M
Evidence: [how each item was verified]
Client pending: [real content, photos, domain, analytics accounts]
Known risks: [what couldn't be tested and why]
```

Never write "it's done" with an open blocker — write what's missing.
