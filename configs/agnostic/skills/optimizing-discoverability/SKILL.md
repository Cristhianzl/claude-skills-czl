---
name: optimizing-discoverability
description: Optimize a site or content to be found — SEO (rank and earn the click on Google/Bing), AEO (be the direct answer in featured snippets, People Also Ask, and voice assistants), and GEO (be the source that ChatGPT, Claude, Perplexity, and Google AI Overviews cite). Use whenever the task involves search visibility or AI visibility: "SEO", "AEO", "GEO", "rank on Google", "organic traffic", "featured snippet", "meta description", "keywords", "be cited by AI / ChatGPT", "AI Overviews", "llms.txt", content strategy for a landing page or blog, or auditing why a site doesn't show up. Technical on-page floor (h1, title/meta, canonical, sitemap) lives in building-frontend-ui — this skill owns the discipline and strategy on top of it.
license: MIT
---

# Optimizing discoverability — SEO · AEO · GEO

Three lenses on one goal, each aiming at a different "searcher": **SEO** wants the **click** on a results page; **AEO** wants to **be the answer** (featured snippet, People Also Ask, voice); **GEO** wants to be the **source an AI cites** (ChatGPT, Claude, Perplexity, AI Overviews). They compound: answer engines and generative engines overwhelmingly pull from pages that already index and rank well — **SEO is the foundation; AEO and GEO are layers on top, not replacements.**

## Read first (always)

List `learnings/` and read anything relevant — the project's niche, existing rankings, target queries, analytics stack, and past decisions live there and override the defaults here.

## Grounding — what this skill is based on

- **Google's official AI-features guidance** ([developers.google.com/search/docs/fundamentals/ai-optimization-guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)): AI features "are rooted in our core Search ranking and quality systems" — pages must be indexed and snippet-eligible; the winning content is "unique, non-commodity" with a real point of view.
- **The GEO study** (Aggarwal et al., KDD 2024 — [arxiv.org/abs/2311.09735](https://arxiv.org/abs/2311.09735)): first large-scale test (9 tactics, 10k queries) of what makes generative engines cite a page. Adding **citations to sources, quotations, and statistics** boosted visibility 30–40%; **keyword stuffing made it worse**.

## Myths — officially debunked, don't spend effort here

Google states these explicitly (for Google surfaces):
- **`llms.txt` and "AI text files" are ignored by Google Search.** (For non-Google engines it's an emerging, optional standard — see `references/geo.md`; never treat it as the strategy.)
- **No chunking required** — you don't need to fragment content "for the AI".
- **No special schema is required for AI features**; structured data clarifies what's already visible, it doesn't unlock anything hidden.
- **Keyword density / long-tail stuffing is obsolete** — systems understand synonyms and meaning; the GEO study measured stuffing *reducing* AI visibility.
- **Artificial mentions/link schemes** remain counterproductive.

## Workflow

1. **Scope and goal.** What does "found" mean for this project — clicks (SEO), the answer box (AEO), AI citations (GEO), or all three? Which pages, which market/language, what's the primary conversion? One measurable target.
2. **Audit what exists.** Indexability first (robots, sitemap, canonicals, the technical floor in `building-frontend-ui/references/designing-from-scratch.md`); then current rankings/queries (Search Console), current AI visibility (ask the major assistants the money questions — is the brand cited?), and the competitor set.
3. **Map queries to intent to pages.** Every target query gets one owning page and an intent label (informational / commercial / transactional / navigational). One page per intent cluster — never two pages competing for the same query.
4. **Apply the three passes, in order:**
   - **SEO pass** — `references/seo.md`: intent match, E-E-A-T with real experience, topical authority, internal linking, technical health.
   - **AEO pass** — `references/aeo.md`: question-shaped headings, a 40–60-word direct answer immediately under each, lists/tables for steps and comparisons, schema that mirrors visible content.
   - **GEO pass** — `references/geo.md`: citable self-contained passages, named sources + statistics + quotations, original data, entity consistency, AI-crawler access policy.
5. **Measure and iterate.** Search Console (clicks, impressions, position), snippet/PAA wins, AI-referral traffic and brand citations in assistant answers. Expect **3–6 months** for meaningful movement; report that honestly instead of promising fast wins.

## Non-negotiables

- **Never fabricate E-E-A-T**: no fake authors, fake reviews, invented statistics, or "as seen in" logos that aren't real. That's the discoverability version of the fake-testimonial rule (`building-frontend-ui/references/anti-vibe-coded.md`) — and quality raters and AI engines are specifically tuned to smell it.
- **Content answers the query it targets** — the promise in the title is kept in the first screen. Clickbait that under-delivers dies in every one of the three lenses.
- **Schema mirrors visible content only.** Marking up content that isn't on the page is a spam signal.
- **The technical floor comes first.** A page that isn't crawlable/indexable/snippet-eligible can't win any of the three games (floor: `building-frontend-ui`).
- **Don't sacrifice readers for engines.** Google's own summary: "Focus on what your visitors would enjoy, find helpful, and feel satisfied with."

## Output

For an audit: a prioritized report — indexability blockers first, then per-lens gaps with the specific page and fix, then the measurement plan. For content work: the intent map, then the content with the three passes applied, then what to measure. State assumptions (market, language, competitor set) explicitly.

## Capture a learning

Record the project's niche, target queries, what ranked/got cited and what didn't, and any engine-specific behavior you observe (`learnings/YYYY-MM-DD-slug.md` or `/learn`).

## See also

- `references/seo.md` · `references/aeo.md` · `references/geo.md`
- `skills/building-frontend-ui` — the technical on-page floor (head, semantics, CWV) and `references/designing-from-scratch.md` (SEO foundation checklist).
- `skills/writing-prd` — when the real problem is "what content should exist", scope it before optimizing it.
