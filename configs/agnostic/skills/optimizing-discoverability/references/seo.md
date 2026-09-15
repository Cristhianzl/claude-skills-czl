# SEO — earn the rank and the click

The foundation lens. Google's AI features and third-party answer/generative engines pull overwhelmingly from pages that already index and rank — win here first. The technical on-page floor (one `h1`, unique title/meta, canonical, sitemap/robots, OG, clean URLs) lives in `building-frontend-ui/references/designing-from-scratch.md`; this file is the discipline above it.

## Intent before keywords

- Map every target query to an **intent**: informational (learn), commercial (compare), transactional (buy/do), navigational (find brand). The page type must match the intent — a product page can't win an informational query and vice versa.
- **One page owns one intent cluster.** Two of your pages competing for the same query cannibalize each other; consolidate or differentiate.
- Don't chase keyword density or long-tail permutations — engines resolve synonyms and meaning. Write the query's *answer*, use the natural vocabulary of the audience (the words users actually type), and let variants happen.

## Content that survives core updates

- **Non-commodity content wins.** Google's own guidance: unique expert or experienced takes "that go beyond common knowledge". If the page just re-states what the top 10 already say, it has no reason to rank — add what only this business knows: its data, its cases, its process, its opinion.
- **E-E-A-T is demonstrated, never claimed**: real author with a name, credentials, and a consistent presence on the topic (author pages, profiles, mentions elsewhere); first-hand experience visible in the content (real photos, real numbers, "we tested"); cited primary sources; accurate, dated, maintained content. **Never fabricate any of it.**
- **Topical authority beats scattered posts**: cover a niche deeply (cluster of related pages interlinked around a pillar) rather than publishing random one-offs. Sites are increasingly evaluated on niche-level expertise.
- Freshness where it matters: update and re-date content whose accuracy decays (prices, versions, laws); leave evergreen alone.

## Architecture & internal linking

- **Pillar → cluster**: a broad pillar page links to specific subpages and each subpage links back and sideways. Internal links are how you tell engines (and LLMs) what's related and what's most important.
- Descriptive anchor text ("connection pooling guide", never "click here"). Orphan pages (no internal links pointing in) effectively don't exist.
- Shallow depth: important pages reachable in ≤3 clicks from home.

## Technical discipline (beyond the floor)

- **Crawlability & indexability first** — a `noindex` left behind, a robots.txt block, or a canonical pointing at the wrong page silently kills everything else. Verify in Search Console, not by assumption.
- **Canonical strategy** for filters/params/variants; paginated lists self-canonicalize per page.
- **`hreflang`** on multilingual sites (pairs with the kit's i18n rules): each language version declares all alternates including itself; missing return-links invalidate the set.
- **Core Web Vitals** (LCP < 2.5s, INP < 200ms, CLS < 0.1) are a ranking input and a UX floor — measured on real 4G, see `building-frontend-ui/references/performance.md`.
- JS-heavy sites: content must exist in rendered HTML the crawler gets — verify with the URL-inspection tool, not by looking at the browser.

## Links & mentions

- Links still matter as part of the bigger trust picture. Earn them with citable assets (original data, tools, definitive guides) — never buy, exchange, or scheme them; inauthentic link-building remains counterproductive and is explicitly called out by Google.
- Consistent NAP/entity data (name, address, profiles) and a real About page feed the same trust graph that GEO relies on.

## Measure

Search Console: queries, clicks, impressions, average position; index coverage. Watch **query-per-page ownership** (is the intended page ranking for the intended query?). Meaningful movement takes 3–6 months.
