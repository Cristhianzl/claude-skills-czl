# AEO — be the answer, not just a link

Answer Engine Optimization targets the surfaces that answer *instead of* listing: Google featured snippets, People Also Ask (PAA), voice assistants (which read the snippet aloud), and the extraction layer AI engines use. The unit of optimization is not the page — it's the **question + answer block**.

## The core pattern: question → direct answer → depth

- **Headings are real questions**, phrased the way people ask them ("How much does X cost?", "Can I use X with Y?"). Mine them from PAA boxes, autocomplete, support tickets, and sales calls — not from imagination.
- **Immediately under the question heading, a 40–60-word direct answer** that fully resolves it: definition-style, self-contained, no "it depends" throat-clearing, no forcing a scroll. This is the snippet candidate and what voice reads.
- **Then expand** with the nuance, examples, and edge cases for the human who wants depth. Answer-first is the same Minto principle the kit already uses for prose (`documenting-features/references/communication.md`) applied to content.

## Format for extraction

- **Steps → ordered list. Comparisons → table. Options → bulleted list.** Engines lift these structures verbatim into list/table snippets; prose paragraphs lose to them.
- One question cluster per page; each sub-question is an `h2`/`h3` with its own answer block. A real FAQ section catches the long-tail variants at the end.
- Keep answer blocks **self-contained**: pronouns resolved ("Langflow supports…", not "It supports…"), one claim per sentence, units and dates explicit. An extracted block is read without its surroundings.
- Front-load the page too: the page-level promise answered in the first screen, not after 800 words of introduction.

## Schema — clarify, never decorate

- Schema's job is to make the visible content unambiguous. **Mark up only what's on the page**; invisible or exaggerated markup is a spam signal.
- Useful types: `FAQPage` (only when the page genuinely shows Q&A), `HowTo`, `QAPage`, `Product`, `Organization`, `Article` with a real `author`, `BreadcrumbList`.
- **Honesty note:** Google has restricted FAQ/HowTo *rich results* to a narrow set of sites since 2023, and states no schema is required for AI features — so treat schema as disambiguation for machines (still worthwhile, low cost), never as a growth hack.

## Voice & zero-click reality

- Voice assistants read one answer — the snippet. Winning it means your 40–60-word block, in spoken-language phrasing.
- AEO trades clicks for presence: the answer box satisfies many users on the results page. Decide deliberately which questions you *want* to answer fully in-snippet (awareness plays) and which should resolve on your page (conversion plays) — put the conversion path adjacent to the answer for the ones that must click.

## Measure

Search Console: track queries where the page ranks top-10 but has low CTR (snippet opportunity) and question-form queries gained. Manually check the money questions in PAA and voice. A snippet won by a competitor with worse content = your formatting lost, not your content — fix the block, not the page.
