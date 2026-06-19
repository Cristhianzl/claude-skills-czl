# Inputs and Outputs — full reference

Every type with its options, defaults, and when to use it.

All types come from `langflow.io`:

```python
from langflow.io import (
    MessageTextInput, MultilineInput, IntInput, FloatInput, BoolInput,
    DropdownInput, SecretStrInput, HandleInput, DataInput, DataFrameInput,
    FileInput, TableInput, NestedDictInput, CodeInput, PromptInput,
    Output,
)
```

The exact list available depends on the Langflow version — read `src/lfx/src/lfx/inputs/` for the source of truth.

---

## Universal options

Every input type accepts:

| Option         | Meaning                                                                                          |
|----------------|--------------------------------------------------------------------------------------------------|
| `name`         | **Required.** Snake_case. Becomes the attribute on `self`. **Never change after release.**       |
| `display_name` | Human label shown in the UI. Safe to change.                                                     |
| `info`         | Tooltip text. Use to explain non-obvious fields.                                                  |
| `value`        | Default value. Choose one that lets old flows that didn't set this field still work.              |
| `required`     | Boolean. If `True`, the node fails validation when the field is empty.                            |
| `advanced`     | Boolean. If `True`, the field is hidden under "Advanced" — use for niche options.                  |
| `show`         | Boolean. If `False`, the field is not shown at all (rare — used for derived/conditional fields). |
| `placeholder`  | Placeholder text shown when the field is empty.                                                   |

---

## Text inputs

### `MessageTextInput`

A single-line text field. The most common input type.

```python
MessageTextInput(
    name="input_value",
    display_name="Input",
    info="The user prompt.",
)
```

Use for: short free-text from the user, or text piped from another node's `Message` output.

### `MultilineInput`

A multi-line text area. Use for long prompts and templates.

```python
MultilineInput(
    name="system_prompt",
    display_name="System Prompt",
    value="You are a helpful assistant.",
)
```

### `PromptInput`

Multiline input pre-typed as a prompt template. The UI may render it with template-variable syntax highlighting.

```python
PromptInput(
    name="prompt_template",
    display_name="Prompt Template",
    value="Answer the question: {question}",
)
```

### `CodeInput`

Multiline input pre-typed as a code block. The UI renders monospace with syntax highlighting.

```python
CodeInput(
    name="python_code",
    display_name="Python Code",
    info="A small Python snippet to execute.",
)
```

---

## Numeric inputs

### `IntInput`

```python
IntInput(name="max_tokens", display_name="Max Tokens", value=1024)
```

### `FloatInput`

```python
FloatInput(name="temperature", display_name="Temperature", value=0.7)
```

Use `info` to communicate the meaningful range. If your input type supports `range_spec`, use it to bound the value in the UI.

---

## Choice inputs

### `BoolInput`

```python
BoolInput(name="stream", display_name="Stream", value=False)
```

Use for any two-state setting. **Never** use `MessageTextInput` with `value="true"/"false"`.

### `DropdownInput`

Fixed set of choices.

```python
DropdownInput(
    name="model",
    display_name="Model",
    options=["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"],
    value="claude-sonnet-4-6",
)
```

The set of `options` can be computed dynamically in `__init__` or in a class-level helper that runs at load time. Avoid choices that change per request — that's `MessageTextInput` territory.

---

## Sensitive inputs

### `SecretStrInput`

API keys, tokens, passwords. The value is stored encrypted server-side and masked in the UI.

```python
SecretStrInput(
    name="api_key",
    display_name="API Key",
    info="Your provider API key. Encrypted at rest.",
    required=True,
)
```

**Never** use `MessageTextInput` for an API key. It will be stored in clear and printed in logs.

---

## Wiring inputs

### `HandleInput`

Wires an output from one component to an input of this one. The `input_types` declares what shape this input accepts.

```python
HandleInput(
    name="model",
    display_name="Language Model",
    input_types=["LanguageModel"],
    required=True,
)
```

Use for: receiving a model, a tool, an agent, or any structured object from an upstream component.

### `DataInput`

Receives a `Data` (structured record) from upstream.

```python
DataInput(name="user_record", display_name="User", required=True)
```

### `DataFrameInput`

Receives a `DataFrame` from upstream.

```python
DataFrameInput(name="rows", display_name="Rows", required=True)
```

---

## File and table inputs

### `FileInput`

The user uploads a file via the UI.

```python
FileInput(
    name="document",
    display_name="Document",
    file_types=["pdf", "docx", "txt"],
    required=True,
)
```

The component receives a file path or a file-like reference, depending on the version — read the input class source if uncertain.

### `TableInput`

The user fills in a table of structured rows.

```python
TableInput(
    name="rules",
    display_name="Routing Rules",
    table_schema=[
        {"name": "pattern", "type": "str", "required": True},
        {"name": "target", "type": "str", "required": True},
    ],
)
```

### `NestedDictInput`

The user provides a structured JSON/dict.

```python
NestedDictInput(
    name="parameters",
    display_name="Parameters",
    value={},
)
```

---

## Outputs

```python
Output(
    name="response",                # snake_case; flow JSON references this
    display_name="Response",        # human label
    method="generate_response",     # the method on the class that produces the value
    types=["Message"],              # optional explicit type list (rare)
)
```

| Output return type | Use for                                                              |
|--------------------|-----------------------------------------------------------------------|
| `Message`          | LLM responses, user-facing strings, tool outputs                      |
| `Data`             | Structured record (JSON-shaped)                                       |
| `DataFrame`        | Tabular data (multiple rows)                                          |
| `Text` (rare)      | Plain string. Prefer `Message`.                                       |

Returning the wrong type makes the next node in the flow fail validation. The error message references the missing field shape, not the type itself — so picking the right type up front saves the user from a confusing failure later.

---

## Choosing between input types — common dilemmas

| Question                                                                   | Pick                       |
|----------------------------------------------------------------------------|----------------------------|
| User picks from N known options                                            | `DropdownInput`             |
| User toggles a boolean                                                     | `BoolInput`                 |
| User types an API key                                                      | `SecretStrInput`            |
| User types a single line                                                   | `MessageTextInput`          |
| User types a multi-line prompt                                             | `MultilineInput` / `PromptInput` |
| User pipes a string from another component                                 | `MessageTextInput` (it accepts both) |
| User pipes a structured object (`Data`) from another component             | `DataInput`                 |
| User pipes a model or tool from another component                          | `HandleInput`               |
| User pipes tabular data                                                    | `DataFrameInput`            |
| User configures structured rules                                           | `TableInput`                |
| User uploads a file                                                        | `FileInput`                 |
| The value should change between every flow run                              | Receive from another input via `HandleInput` or wire from an upstream component, not a literal |

---

## Names are forever

Every `name` field in `inputs[]` and `outputs[]` is referenced in saved flow JSON. Renaming `api_key` to `apikey` after release will silently drop the saved value on every flow that uses the component.

If you must evolve the contract, **add a new input with a new name**, default it to derive its value from the old one if it's set, and deprecate the old field over a release or two with a clear migration note in `BUNDLE_API.md` (for bundles) or the release notes (for base).
