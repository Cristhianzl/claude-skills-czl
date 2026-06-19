---
name: building-langflow-components
description: Create, evolve, and ship Langflow Components — the building blocks of every flow. Use when the user asks to "create a component", "add a provider component", "build an LLM component", "add Anthropic / OpenAI / Chroma / etc. integration", "expose this as a Component", or "wrap this LangChain class as a Component". Enforces the immutable-class-name rule, the inputs/outputs API, the hot-reload workflow, ComponentTestBase fixtures, and the bundle-vs-base placement decision. For refactoring an existing component, also see Langflow's bundled `.agents/skills/component-refactoring` skill.
license: MIT
---

# Building Langflow Components

A Langflow Component is a Python class that becomes a draggable node in the visual flow editor. Every component is a contract between the flow JSON (which references the class by name) and the runtime (which loads and executes it). Get the contract right and the component lasts forever; get it wrong and you break saved flows for every user who ever used it.

## Read first (always)

List `learnings/` and read every file relevant to the current component (provider, bundle, AI runtime, etc.). Project-specific naming conventions, banned dependencies, icon rules, or provider-specific patterns live there and override the defaults in this SKILL.md. If a learning conflicts with this file, **the learning wins** — mention it to the user.

Also read `/Users/criszl/Documents/langflow/AGENTS.md` (or the project's current version) — it's canonical and may have evolved.

## Tradeoff — when to apply, when to lighten up

Apply the full discipline (immutable name, full test suite with `ComponentTestBaseWith[out]Client`, ADR for non-obvious design, BUNDLE_API changelog when relevant) for **every new component that ships**.

Lighten formality for: throwaway experiments, components behind `LFX_DEV=...,my_local_only` that will never enter `__init__.py`, internal sandbox tests. Even then, follow the class structure — it's how the framework discovers the component at all.

## The non-negotiable rule

> **A component's class name is its identity in every saved flow.** Renaming `OpenAIModelComponent` to `OpenAIChatModelComponent` doesn't refactor a class — it deletes a component for every user who has it on a saved flow, and creates a different component nobody is using.

If the name is wrong from day one, you're stuck with it. Spend the extra minute up front. If you must evolve the contract, create a **new class with a new name**, mark the old one `deprecated = True`, keep the old behavior intact, and let flows migrate one user at a time.

The same rule applies to every `inputs[].name` and `outputs[].name` — they appear in flow JSON.

## Workflow

1. **Decide bundle vs base.** Generic, broadly useful components (OpenAI, Anthropic, Chroma, etc.) live in `src/backend/base/langflow/components/<provider>/`. Niche or ecosystem-specific components belong in an optional **bundle** under `src/bundles/<bundle_name>/` and must be documented in that bundle's `BUNDLE_API.md`. If in doubt → ask the user.
   → verify: you can name the exact path the new file will live at, and you've checked it isn't a duplicate of an existing component.

2. **Pick the class name carefully** — it is forever. Use `<Provider><Capability>Component`: `AnthropicChatModelComponent`, `ChromaVectorStoreComponent`, `OpenAIEmbeddingsComponent`. Spelling matches the provider's official brand. No abbreviations.
   → verify: the name is unambiguous, brand-correct, and would still make sense if a coworker grepped for it 18 months from now.

3. **Pick the icon.** Lucide icon name (e.g., `"sparkles"`) or a custom SVG from `src/frontend/src/icons/<IconName>/` (see `references/icons.md` for the SVG → Python wiring). When in doubt, copy the convention from a neighboring component in the same provider folder.
   → verify: `icon = "..."` matches either a real Lucide name or an exported icon in `lazyIconImports.ts`.

4. **Define `inputs` and `outputs` with `name`s that will never change.** Inputs use the `langflow.io` types — `MessageTextInput`, `IntInput`, `BoolInput`, `DropdownInput`, `SecretStrInput`, `HandleInput`, `DataInput`, `FileInput`. Outputs declare `name`, `display_name`, and the `method` that produces them.
   → verify: every `name` is snake_case, matches the attribute Python uses internally, and would still be the right field name a year from now.

5. **Implement the output method(s).** Each output's `method` is a Python method on the class that returns the declared type (`Message`, `Data`, `DataFrame`, etc.). Methods access inputs via `self.<input_name>`. Do **not** instantiate external SDKs at import time — do it inside the method so failures show up as runtime errors with context.
   → verify: every output's `method` exists on the class and returns the correct type; no top-level SDK initialization.

6. **Apply AI runtime rules if the component calls an LLM.** Explicit timeout, retries delegated to the official SDK (don't reinvent), surface errors as domain errors (`MessageError` / `ToolError`), redact secrets in logs. See `references/ai-component-patterns.md`.
   → verify: the component does not hang indefinitely, does not log raw prompts or API keys, and maps SDK errors to user-readable messages.

7. **Wire dynamic loading for dev.** Run `LFX_DEV=1 make backend` (or `LFX_DEV=<provider>` to scope to just yours) to pick up new components without a restart. Frontend on `:3000` will discover the component as soon as the backend reloads.
   → verify: the component appears in the sidebar under the right category; dragging it onto a flow doesn't error.

8. **Add tests using the right `ComponentTestBase`.** `ComponentTestBaseWithoutClient` for pure logic; `ComponentTestBaseWithClient` for components that need the backend client (file inputs, vector store contexts, etc.). Mandatory fixtures: `component_class`, `default_kwargs`, `file_names_mapping`.
   → verify: tests pass standalone (`uv run pytest path/to/test.py`), and the suite (`make unit_tests`) is green.

9. **Prefer real integrations over mocks** (Langflow convention from `AGENTS.md`). Use `@pytest.mark.api_key_required` for tests that need an API key. CI provides the keys for the marked tests.
   → verify: the test asserts observable behavior against the real provider (or its sandbox) when possible; mocks are reserved for failure paths the provider sandbox cannot reproduce.

10. **Register the component.** Add it to the provider folder's `__init__.py` in alphabetical order. For bundles, update the bundle's `BUNDLE_API.md` (the changelog gate enforces this).
    → verify: `from langflow.components.<provider> import <YourClass>` succeeds.

11. **Pre-commit and version bump.** `make format_backend` → `uv run git commit` (pre-commit runs ruff + biome + migration validator). If the component triggers a release, bump version with `make patch v=X.Y.Z` — it updates all three `pyproject.toml`s.
    → verify: pre-commit passes; the build runs.

12. **Capture a learning (final step, mandatory ask).** Ask yourself: *did I encounter a provider quirk, an SDK trap, a hot-reload caveat, or an icon-wiring gotcha that wasn't in this SKILL.md, `references/`, or AGENTS.md?* If yes, append a `learnings/YYYY-MM-DD-slug.md` per `learnings/README.md`. If no, skip.

## Component anatomy (canonical shape)

```python
from langflow.custom import Component
from langflow.io import (
    MessageTextInput,
    SecretStrInput,
    IntInput,
    DropdownInput,
    Output,
)
from langflow.schema import Message


class AcmeChatModelComponent(Component):
    display_name = "Acme Chat"
    description = "Chat with an Acme model."
    icon = "Acme"
    documentation = "https://docs.acme.ai/api/chat"

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="Acme API key. Stored encrypted.",
            required=True,
        ),
        DropdownInput(
            name="model",
            display_name="Model",
            options=["acme-fast", "acme-balanced", "acme-deep"],
            value="acme-balanced",
            required=True,
        ),
        MessageTextInput(name="input_value", display_name="Input"),
        IntInput(
            name="timeout_seconds",
            display_name="Timeout (s)",
            value=30,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Response", name="response", method="generate_response"),
    ]

    def generate_response(self) -> Message:
        from acme_sdk import Client, AcmeError

        client = Client(api_key=self.api_key, timeout=self.timeout_seconds)
        try:
            result = client.chat(model=self.model, prompt=self.input_value)
        except AcmeError as exc:
            self.status = f"Acme call failed: {exc.code}"
            raise ValueError(self.status) from exc
        return Message(text=result.text)
```

What this example demonstrates — explained in prose because the code already speaks for itself:

- **The class name is identity.** `AcmeChatModelComponent` lives in every flow JSON forever. Renames break flows.
- **`display_name`, `icon`, `description`, `documentation`** are human-facing and safe to change.
- **`SecretStrInput` for the API key** — Langflow encrypts it at rest and masks it in the UI; `MessageTextInput` would store it in clear.
- **`DropdownInput` for enumerated choices** — the user can't fat-finger an invalid model name.
- **`advanced=True`** hides the field under "Advanced" so the basic UI stays clean.
- **The SDK import lives inside the method** — `__init__` stays cheap; if the SDK is missing the user gets a runtime error scoped to this component, not a top-level crash.
- **`self.status` carries the short failure message** to the node in the UI; `raise ValueError(...) from exc` propagates the original exception to the flow runtime.
- **No top-level state.** Construction is cheap; cost is paid in the method when the flow runs.

## When to use which input type

| Input type           | Use for                                                       |
|----------------------|---------------------------------------------------------------|
| `MessageTextInput`   | Free-text the user types or pipes from another component      |
| `MultilineInput`     | Long text (system prompts, templates)                          |
| `IntInput`           | Bounded integers (timeouts, top_k, max_tokens)                |
| `FloatInput`         | Bounded floats (temperature, top_p)                            |
| `BoolInput`          | Toggle (`stream`, `cache`, `verbose`)                          |
| `DropdownInput`      | Enumerated options. Always prefer over `MessageTextInput`.    |
| `SecretStrInput`     | API keys, tokens, passwords. Stored encrypted, masked in UI.   |
| `HandleInput`        | Wire from another component's output                          |
| `DataInput`          | Structured `Data` from upstream                               |
| `FileInput`          | File the user uploads                                          |
| `TableInput`         | Tabular configuration the user fills in                       |

Don't use `MessageTextInput` for what should be a `DropdownInput` or `BoolInput`. Each wrong type costs the user a future bug.

## When to use which output type

| Output type    | Use for                                                              |
|----------------|----------------------------------------------------------------------|
| `Message`      | A chat-like message (LLM responses, user-facing strings)             |
| `Data`         | A structured record (JSON-shaped)                                    |
| `DataFrame`    | Tabular data (multi-row results)                                      |
| `Text`         | Plain string (rare — prefer `Message`)                                |

Returning the wrong type makes the next component in the flow fail validation, often with a confusing error. Pick once, document it in the `Output(display_name=...)`, never change.

## Hot reload — fastest dev loop

In one terminal:

```bash
LFX_DEV=1 make backend            # all components reload on save
# or — load only the providers you're working on:
LFX_DEV=openai,anthropic,acme make backend
```

In another:

```bash
make frontend                     # Vite dev server, picks up backend at :7860
```

When you save a `.py` file under `src/backend/base/langflow/components/...`, the backend reimports the module. Refresh the flow editor; the component re-renders with your changes.

**Caveats:**

- Adding a brand-new `inputs[]` field doesn't migrate existing flows that reference the older shape — they keep their saved values. If you add a required field, default it sensibly so old flows don't break.
- Changing an input's `type` (e.g., `MessageTextInput` → `DropdownInput`) is a breaking change to the flow JSON. Treat it like a rename: new component, deprecate the old.

## Hard rules

- **Never rename the class** of an existing component. Add a new class with a new name; deprecate the old via `deprecated = True`.
- **Never rename `inputs[].name` or `outputs[].name`** for an existing component. Same reason.
- **Never** instantiate an SDK client at module import time. Inside the method only.
- **Never** log raw prompts, raw responses, or API keys.
- **Never** suppress errors silently — surface as `ValueError` / `ToolError` / `MessageError` with context, and set `self.status` for the UI.
- **Never** commit with bare `git commit` — pre-commit needs `uv run git commit` to find the right Python.
- **Never** add a new bundle component without updating the bundle's `BUNDLE_API.md` — the changelog gate is enforced.
- **Never** decorate the component with WHAT-comments. The `inputs` and `outputs` declarations are self-describing; the method names say what they do. Reserve comments for the WHY that isn't obvious from naming — e.g., "this SDK's timeout default is `None`; pin it explicitly" or "API returns 200 with `error` in body; treat as failure". Section dividers (`# === Identity ===`, `# === Outputs ===`) belong nowhere in real components.

## See also

- `references/component-anatomy.md` — full anatomy with comments line by line, alternative shapes (tool-as-component, MCP component), and common mistakes.
- `references/io-reference.md` — every input and output type with options, defaults, and when to reach for which.
- `references/testing.md` — `ComponentTestBaseWithClient` vs `ComponentTestBaseWithoutClient`, the three mandatory fixtures, `@pytest.mark.api_key_required` and friends, integration-vs-mock policy.
- `references/icons.md` — wiring a custom SVG icon end-to-end (SVG → forwardRef component → `lazyIconImports.ts` → Python `icon = "Name"`).
- `references/ai-component-patterns.md` — timeouts, retries, error mapping, streaming, token accounting, redaction.
- `references/bundles.md` — when a component belongs in a bundle, how the bundle directory is laid out, `BUNDLE_API.md` requirements.
- `learnings/` — provider-specific quirks, SDK traps, and Langflow conventions accumulated over time.
- **Langflow's own skills** at `/Users/criszl/Documents/langflow/.agents/skills/` — especially `component-refactoring` for evolving an existing component (different from creating one), `backend-code-review` for reviewing the PR, and `frontend-testing` for component UI tests.
- `building-langflow-components` is **complementary** to `developing-features-tdd` — the TDD cycle applies, the file-structure rules apply, but the **shape** of the artifact (a `Component` subclass) is governed here.
