# Sources — the wording this skill is built on

Quoted verbatim from the pages listed. Where a point came only from a summary, it is not quoted.

## Definitions

- **Scope creep** — "continuous or uncontrolled growth in a project's scope, generally experienced after the project begins." — https://en.wikipedia.org/wiki/Scope_creep (same wording: https://www.briefbuilder.com/beware-the-scope-creep/)
- Scope creep — "needs, capabilities, or deliverables that were not initially stated for a project gradually grow or are introduced", "Usually started without official approval procedures, informally by project team members or stakeholders." — https://www.geeksforgeeks.org/business-studies/what-is-scope-creep-in-project-management/
- **Gold plating** — "The term 'gold plating' refers to the tendency to exceed a project's specifications." — https://stackoverflow.blog/2021/05/27/how-to-prevent-scope-creep-when-managing-a-project-from-home/ · "Gold plating occurs when a project team delivers more than was agreed upon in the scope." — https://pmstudycircle.com/scope-creep-vs-gold-plating/
- **YAGNI** — a "presumptive feature" is "any code that supports a feature that isn't yet being made available for use"; and "Yagni only applies to capabilities built into the software to support a presumptive feature, it does not apply to effort to make the software easier to modify." — https://martinfowler.com/bliki/Yagni.html
- **Over-engineering** — "where developers have made the code more generic than it needs to be, or added functionality that isn't presently needed by the system." — https://google.github.io/eng-practices/review/reviewer/looking-for.html
- **AI slop** — "output that compiles, passes review at a glance, and quietly degrades the codebase." — https://www.managed-code.com/blog-post/ai-slop-in-code

**Mapping to agents:** an agent adding unrequested work on its own initiative is gold plating; an agent silently reinterpreting the task is scope creep (the baseline changed without approval); slop is gold plating at the line level. Low cost of change is a known cause of creep — and generating code is nearly free.

## Anthropic — prompting best practices ("Overeagerness")

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

> Claude Opus 4.5 and Claude Opus 4.6 have a tendency to overengineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested.

> Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused:
> - Scope: Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.
> - Documentation: Don't add docstrings, comments, or type annotations to code you didn't change. Only add comments where the logic isn't self-evident.
> - Defensive coding: Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs).
> - Abstractions: Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task.

> If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.

> Do not hard-code values or create solutions that only work for specific test inputs. [...] If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them.

> Do not jump into implementation or change files unless clearly instructed to make changes. When the user's intent is ambiguous, default to providing information, doing research, and providing recommendations rather than taking action.

## Anthropic — model-specific prompting guides

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5

> Deliver what was asked, at the scope intended. Make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work. If the request seems mistaken or a better approach exists, say so in a sentence and continue with the task as asked rather than quietly narrowing, widening, or transforming it. Finish the whole task, and stop short of actions that are clearly beyond what was asked.

https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

> When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.

> When the work the user asked for is done and its checks pass, stop and report. Don't start extra rounds of review or hardening on your own, and don't launch reviewer sub-agents unless the user asked for a review.

> When the user asks for ideas, options or a plan, give them that and stop. Don't start building or changing anything until they say to go ahead.

## Anthropic — Claude Code best practices (scope belongs to the user)

https://code.claude.com/docs/en/best-practices — expansion comes from the user's explicit signal ("be ambitious"): "That's telling Claude about scope, which only you know."

## Community rule sets

Karpathy-inspired CLAUDE.md — https://github.com/forrestchang/andrej-karpathy-skills

> - Don't "improve" adjacent code, comments, or formatting.
> - Don't refactor things that aren't broken.
> - Match existing style, even if you'd do it differently.
> - If you notice unrelated dead code, mention it - don't delete it.
>
> The test: Every changed line should trace directly to the user's request.

> If multiple interpretations exist, present them - don't pick silently.

> If you write 200 lines and it could be 50, rewrite it.

deslop skill — https://github.com/brianlovin/agent-config/blob/main/skills/deslop/SKILL.md

> - Extra comments that a human wouldn't add or is inconsistent with the rest of the file
> - Extra defensive checks or try/catch blocks that are abnormal for that area of the codebase (especially if called by trusted / validated codepaths)
> - Casts to any to get around type issues
> - Any other style that is inconsistent with the file

## Google engineering practices

- "Encourage developers to solve the problem they know needs to be solved now, not the problem that the developer speculates might need to be solved in the future." — https://google.github.io/eng-practices/review/reviewer/looking-for.html
- A CL "makes a minimal change that addresses just one thing"; "It's usually best to do refactorings in a separate CL from feature changes or bug fixes." — https://google.github.io/eng-practices/review/developer/small-cls.html

## Change control (project management → agent behavior)

From the Stack Overflow blog, GeeksforGeeks, and BriefBuilder pages above: define goals, deliverables, and acceptance criteria up front; document what is out of scope; route every change through a request with a stated reason; assess impact before acting; get approval; log the change. BriefBuilder: "No change should be implemented without a clear understanding of its consequences and formal approval to match." For an agent: the scope contract, the parking lot, stop → classify → ask, and the "Beyond the literal request" section of the wrap-up.
