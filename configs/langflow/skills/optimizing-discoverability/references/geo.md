# GEO — be the source the AI cites

Generative Engine Optimization targets ChatGPT, Claude, Perplexity, Gemini, and Google's AI Overviews/AI Mode: the goal is being **retrieved, used, and cited** in generated answers. Two grounding facts keep this discipline honest: Google states its AI features are **rooted in the core ranking systems** (so classic SEO is the entry ticket), and the only large-scale academic study — **Aggarwal et al., KDD 2024** ([arxiv.org/abs/2311.09735](https://arxiv.org/abs/2311.09735), 9 tactics × 10k queries) — measured what actually moves citations.

## What measurably works (the GEO study)

Relative visibility gains of **30–40%** came from three content tactics, all cheap to apply:

- **Cite sources** — claims backed by named, linked references.
- **Add statistics** — concrete numbers instead of vague qualifiers ("reduces latency by 38%" beats "significantly faster").
- **Add quotations** — attributed quotes from named people/organizations (strongest in people/history/explanation domains).

Also positive: **fluency** (clear, well-edited prose) and an **authoritative voice**. Combining tactics (statistics + fluency) performed best. **Keyword stuffing reduced AI visibility** — the study measured it hurting, not just not helping.

## Be quotable — write passages an LLM can lift

- **Self-contained claim units**: a passage that makes sense alone — subject named (no dangling pronouns), claim + number + source in the same breath, date explicit. LLMs synthesize from fragments; fragments that survive extraction get cited.
- Clear structure (real headings, short paragraphs, tables) — the same formatting AEO wants (`aeo.md`); the answer block is also the citation block.
- **Consistency of entity**: same product/company name, description, and facts across your site, profiles, docs, and repos. Contradictions make a model drop you as a source.

## Be the primary source

The strongest GEO asset is **information that exists nowhere else**: your own benchmarks, surveys, usage data, teardown, pricing analysis. Commodity content gets synthesized *from* someone; original data gets **attributed** — engines must name where a number came from. One real dataset outperforms ten rewritten listicles.

## Authority off-site

Generative engines weigh where a brand appears across the corpus: reviews, comparisons, community threads (Reddit/HN/Stack Overflow), industry publications, docs of tools you integrate with. Earn genuine mentions in the places your niche already trusts — and remember Google explicitly calls artificial mention-building counterproductive. Author entities matter too: the same named expert publishing on the topic across venues strengthens every page they sign.

## Crawler access — a deliberate policy, not a default

Being cited requires being readable by the engine's bots. Decide explicitly, in `robots.txt`:

- **Search/answer-time bots** (`OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, Googlebot): allowing them is what makes citations in ChatGPT search / Claude / Perplexity possible. Blocking them = invisible to those engines.
- **Training bots** (`GPTBot`, `Google-Extended`, `CCBot`, `anthropic-ai`): a separate business decision — blocking them limits training-set inclusion without (today) removing you from answer-time citation. Document which trade-off the project chose.
- `llms.txt` (a proposed index of your best pages for LLMs): **Google explicitly ignores it**; some tools read it. Cheap to add, never the strategy.
- Content must be in server-rendered/renderable HTML — several AI crawlers execute little or no JavaScript; if the content only exists client-side, you don't exist.

## Freshness and maintenance

Generated answers favor current sources for time-sensitive topics: visible dates, real update cadence, changelogs. Stale pages fade out of answers before they fade out of rankings.

## Measure

- Ask the target engines the money questions monthly (same prompts, logged) — is the brand present, cited, described correctly?
- Track AI referral traffic separately (referrers like `chatgpt.com`, `perplexity.ai`) and branded-search lift.
- Correct the record: if an assistant describes the product wrongly, the fix is published, crawlable, self-contained content stating the fact — not a complaint.
