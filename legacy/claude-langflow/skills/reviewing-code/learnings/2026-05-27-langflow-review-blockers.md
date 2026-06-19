---
trigger: Reviewing any PR that touches backend, components, migrations, or bundles in Langflow.
---

# Langflow-specific blocker patterns

**Context:** The generic `reviewing-code` SKILL.md lists universal blockers (PII in logs, file structure, secrets). Langflow has additional zero-tolerance blockers tied to its architecture that the generic skill doesn't cover.

**Lesson — these are **`B` blockers** in Langflow code review:**

- **Renaming a Component class.** The class name is the identity in every saved flow. Block with: "Renaming `<OldClassName>` to `<NewClassName>` breaks every saved flow that uses this component. Add a new class with the new name and mark the old one `deprecated = True`." See `AGENTS.md` § Component Development.

- **Renaming `inputs[].name` or `outputs[].name`** on an existing Component. Same reason — they appear in flow JSON.

- **Alembic migration without `Phase:` label.** Every migration must declare `Phase: EXPAND | MIGRATE | CONTRACT` in the docstring. The pre-commit `migration_validator.py` should catch it; if a PR slipped past, block.

- **Column drop in an EXPAND phase.** EXPAND adds; CONTRACT removes. A column drop in EXPAND violates the expand-contract policy and risks downtime.

- **Bundle change without `BUNDLE_API.md` update.** Adding, renaming, deprecating, or removing anything public-facing in `src/bundles/<name>/` requires a `BUNDLE_API.md` entry. CI enforces this — block early to avoid the back-and-forth.

- **AI/chatbot component without explicit timeout.** Every component that calls an LLM must pass an explicit timeout to the SDK. SDK defaults are often infinity.

- **Logging the full prompt or response.** Components that log raw LLM content leak PII and secrets. Map to `prompt_chars`, `response_chars`, `tokens`, `model`, `outcome`, `duration_ms` — never the body.

- **Top-level SDK instantiation in a component module.** `client = openai.OpenAI()` at import time means every flow that touches the module pays the network cost and locks in the SDK's defaults. SDK init goes **inside the output method**.

- **Using `MessageTextInput` for an API key.** Must be `SecretStrInput` so it's encrypted at rest and masked in the UI.

- **Suggesting `unittest.mock` to replace a real integration test** — against Langflow's policy from `AGENTS.md`. The team prefers real integrations; suggest a mock only for failure paths the real provider sandbox cannot reproduce.

- **Bare `git commit` in a recommended workflow.** Pre-commit needs `uv run git commit`. A PR description that says "run pre-commit with `git commit`" is wrong.

- **Bare `pip install` or `poetry add`.** Always `uv` in Langflow. If the PR introduces a non-`uv` install path, block.

- **`langflow.components.<provider>` import that bypasses a bundle's `lfx_<bundle>` namespace.** Bundles must be imported via their own namespace; reaching into them by `langflow.components.<provider>` is wrong.

**Why:** Each of these has caused a real Langflow incident or a back-and-forth in PR review. Pre-flagging them as `B` saves the loop.

**Apply when:** Reviewing any backend, component, migration, or bundle PR. Use the `B` label per the generic SKILL.md's output format.

## How to write the finding

```
### B1 — Component class renamed
**File:** `src/backend/base/langflow/components/openai/openai_chat.py:42`
**Issue:** Renaming `OpenAIModelComponent` to `OpenAIChatComponent` breaks every saved flow that has the old class on the canvas.
**Why it matters:** The class name is the identity in flow JSON. Existing users will see "missing component" on flows they've saved.
**Suggested fix:** Add a new class `OpenAIChatComponent` for the new contract. Mark the old `OpenAIModelComponent` as `deprecated = True` and keep its current behavior intact. Both classes can coexist for one or two releases; old flows continue to work, new flows use the new class.
```

## Cross-references

- `reviewing-code/references/security-checks.md` — PII / secrets rules. Apply on top of the Langflow-specific blockers above.
- `reviewing-code/references/grep-recipes.md` — add the Langflow-specific greps below to the kit.

## Langflow-specific grep recipes

```bash
# Renamed Component classes — diff shows a class definition change
git diff main -- 'src/backend/base/langflow/components/**/*.py' \
  | grep -E '^[-+]class .*Component'

# Migrations missing the Phase label
grep -L "Phase: " src/backend/base/langflow/alembic/versions/*.py

# Top-level SDK instantiation in component modules
grep -rn "^\(client\|llm\|model\) = " src/backend/base/langflow/components/ | grep -v "def "

# Bare git commit in docs
grep -rn "git commit" docs/ --include="*.md" --include="*.mdx" | grep -v "uv run"

# MessageTextInput for an api_key
grep -rn "MessageTextInput.*api_key\|api_key.*MessageTextInput" src/

# Bundle changes missing BUNDLE_API.md update
git diff main --name-only | grep "src/bundles/" | xargs -I{} dirname {} | sort -u | while read d; do
  if [ -d "$d" ] && ! git diff main --name-only | grep -q "$d/BUNDLE_API.md"; then
    echo "Bundle $d changed without BUNDLE_API.md update"
  fi
done
```
