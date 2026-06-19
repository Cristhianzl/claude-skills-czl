# Component anatomy — full reference

The canonical class plus the variants you'll meet in real code.

---

## Canonical chat-model component

The structure is invariant across providers: identity attributes → discoverability attributes → lifecycle flags → `inputs` → `outputs` → method(s). The shape of the class is the documentation; no section comments needed.

```python
from langflow.custom import Component
from langflow.io import (
    MessageTextInput,
    SecretStrInput,
    IntInput,
    FloatInput,
    DropdownInput,
    Output,
)
from langflow.schema import Message


class AcmeChatModelComponent(Component):
    name = "AcmeChatModelComponent"
    display_name = "Acme Chat"
    description = "Chat with an Acme model."
    icon = "Acme"
    documentation = "https://docs.acme.ai/api/chat"
    deprecated = False
    beta = False

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="Acme API key. Stored encrypted server-side.",
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
        FloatInput(
            name="temperature",
            display_name="Temperature",
            value=0.7,
            range_spec=(0.0, 2.0),
            advanced=True,
        ),
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
            result = client.chat(
                model=self.model,
                prompt=self.input_value,
                temperature=self.temperature,
            )
        except AcmeError as exc:
            self.status = f"Acme call failed: {exc.code}"
            raise ValueError(self.status) from exc

        return Message(text=result.text)
```

Why this shape:

- `name` defaults to the class name; setting it explicitly is rare and only done when the class itself has to be renamed (a breaking change you would avoid in the first place).
- `display_name`, `description`, `icon`, `documentation` are human-facing; they can change freely.
- `deprecated = True` keeps the class loadable for saved flows that reference it, hides it from new sidebar additions, and surfaces a warning in the UI. **Do not delete deprecated classes** — the flow JSON would break.
- `beta = True` surfaces a "Beta" badge in the UI; safe to flip on and off.
- Every `inputs[].name` and `outputs[].name` is referenced in saved flow JSON. They are forever — see `io-reference.md` § Names are forever.
- The SDK is imported inside `generate_response` so importing the module doesn't pay the cost and `__init__` stays cheap; if the SDK is missing the user gets a runtime error scoped to this component, not a top-level crash.
- `self.status` is the short message rendered on the node when execution fails; `raise ValueError(...) from exc` propagates the failure to the flow runtime with the original exception preserved.

---

## Tool-as-component (callable from agents)

A component exposed as a tool that agents can call. The shape is the same, but the method returns a `Message` or `Data`, and the component is discoverable to the agent runtime by being typed as a tool.

```python
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Message


class WeatherLookupComponent(Component):
    display_name = "Weather Lookup"
    description = "Return the current weather for a city."
    icon = "cloud"

    inputs = [
        MessageTextInput(name="city", display_name="City", required=True),
    ]
    outputs = [
        Output(display_name="Weather", name="weather", method="lookup"),
    ]

    def lookup(self) -> Message:
        # The agent calls this with `city` set from its tool invocation.
        import httpx

        with httpx.Client(timeout=10) as http:
            resp = http.get(
                "https://api.example.weather/v1/current",
                params={"city": self.city},
            )
            resp.raise_for_status()
            data = resp.json()
        return Message(text=f"{data['city']}: {data['temp_c']}°C, {data['condition']}")
```

Agent components consume this kind of component via `HandleInput` typed as a tool.

---

## Component returning structured data

```python
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data


class ParseCsvRowComponent(Component):
    display_name = "Parse CSV Row"
    description = "Parse a comma-separated row into a structured record."
    icon = "table"

    inputs = [
        MessageTextInput(name="row", display_name="Row", required=True),
        MessageTextInput(name="headers", display_name="Headers (comma-separated)", required=True),
    ]
    outputs = [
        Output(display_name="Record", name="record", method="parse"),
    ]

    def parse(self) -> Data:
        cells = [c.strip() for c in self.row.split(",")]
        headers = [h.strip() for h in self.headers.split(",")]
        if len(cells) != len(headers):
            msg = f"Header count ({len(headers)}) does not match row count ({len(cells)})."
            self.status = msg
            raise ValueError(msg)
        return Data(data=dict(zip(headers, cells, strict=True)))
```

`Data` flows into downstream components that consume `DataInput`.

---

## Component returning a DataFrame

```python
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import DataFrame


class SearchResultsComponent(Component):
    display_name = "Search Results"
    description = "Run a search and return rows."
    icon = "search"

    inputs = [
        MessageTextInput(name="query", display_name="Query", required=True),
        IntInput(name="limit", display_name="Limit", value=10),
    ]
    outputs = [
        Output(display_name="Rows", name="rows", method="search"),
    ]

    def search(self) -> DataFrame:
        rows = self._run_search(self.query, self.limit)
        return DataFrame(data=rows)

    def _run_search(self, q: str, limit: int) -> list[dict]:
        # private helper — fine to extract; only the public method() is the contract
        ...
```

---

## Multiple outputs

```python
class SplitMessageComponent(Component):
    display_name = "Split Message"
    description = "Split a message into a question and an answer half."
    icon = "split"

    inputs = [MessageTextInput(name="input_value", display_name="Input")]
    outputs = [
        Output(display_name="Question", name="question", method="extract_question"),
        Output(display_name="Answer", name="answer", method="extract_answer"),
    ]

    def extract_question(self) -> Message:
        return Message(text=self.input_value.split("?")[0] + "?")

    def extract_answer(self) -> Message:
        parts = self.input_value.split("?", 1)
        return Message(text=parts[1].strip() if len(parts) > 1 else "")
```

Two outputs = two methods. Each named individually. Each callable from a different downstream node.

---

## Deprecating without breaking

When a component must evolve in a breaking way, **do not modify it in place**. Create a new class with the next-version semantics, keep the old class around with `deprecated = True`, and let the UI surface a hint to migrate.

```python
class OldThingComponent(Component):
    display_name = "Old Thing"
    description = "Use OldThingComponent only for legacy flows."
    icon = "thing"
    deprecated = True
    ...

class NewThingComponent(Component):
    display_name = "Thing"
    description = "Replaces OldThingComponent with the new contract."
    icon = "thing"
    ...
```

A `deprecated` component still loads in flows that reference it. The UI shows a warning. New flows can't add it from the sidebar (typically — verify in the current UI).

---

## Common mistakes

- **Defining inputs / outputs as class instance variables instead of class attributes.** The framework reads them off the class itself. `def __init__(self): self.inputs = [...]` does not work.
- **Returning `str` instead of `Message`.** Type checkers won't always catch it; downstream nodes fail at runtime.
- **Mutating `self` in unexpected places.** Components are stateless by contract. Set `self.status` for UI messaging and that's it.
- **Computing once in `__init__`.** The method is what runs per execution; `__init__` runs at construction. Heavy work belongs in the method.
- **Silently swallowing SDK exceptions.** Map them to `ValueError` (or a Langflow-specific error) and set `self.status` so the UI tells the user what's wrong.
- **Calling `print()` from a component.** Use the framework logger; production logs strip stdout.
