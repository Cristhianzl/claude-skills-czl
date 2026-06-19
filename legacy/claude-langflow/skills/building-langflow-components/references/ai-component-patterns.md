# AI component patterns

When the component calls an LLM (or any AI service), apply this on top of the canonical anatomy. These rules are the implementation companion to `developing-features-tdd/references/ai-runtime.md` — same intent, shaped for a Langflow component.

---

## Timeout — always explicit

The SDK's default timeout is often "forever". A component that hangs blocks the whole flow.

```python
def generate_response(self) -> Message:
    from acme_sdk import Client

    client = Client(api_key=self.api_key, timeout=self.timeout_seconds)
    ...
```

Surface the timeout as an `IntInput`, defaulted to a sane value (e.g., 30 s for chat, 60 s for long generation, 120 s for image), marked `advanced=True`.

---

## Retries — delegate to the SDK

Reinventing retry logic in a component is a smell. Every official SDK already implements bounded retries with backoff. Configure them via the SDK's options if needed, but don't write a `for attempt in range(MAX_RETRIES): try: ...` loop inside the component method.

```python
client = Client(
    api_key=self.api_key,
    timeout=self.timeout_seconds,
    max_retries=2,             # if the SDK supports it
)
```

If the SDK doesn't expose retries and the component needs them, prefer `tenacity` or `backoff` over a hand-rolled loop, and keep the retry budget small (≤3).

---

## Error mapping — domain errors, not SDK exceptions

```python
def generate_response(self) -> Message:
    from acme_sdk import Client, AcmeError, AcmeRateLimitError, AcmeAuthError

    client = Client(api_key=self.api_key, timeout=self.timeout_seconds)
    try:
        result = client.chat(model=self.model, prompt=self.input_value)
    except AcmeAuthError as exc:
        msg = "Acme rejected the API key. Check your secret."
        self.status = msg
        raise ValueError(msg) from exc
    except AcmeRateLimitError as exc:
        msg = "Acme rate limit reached. Try again later."
        self.status = msg
        raise ValueError(msg) from exc
    except AcmeError as exc:
        msg = f"Acme call failed: {exc.code or 'unknown'}"
        self.status = msg
        raise ValueError(msg) from exc
    return Message(text=result.text)
```

Why:

- The user sees `self.status` on the node — make it actionable, not a stack trace.
- The flow continues or fails depending on the consumer; raising `ValueError` is the framework's convention for component failure.
- `from exc` preserves the chain in logs without leaking it to the UI.

---

## Streaming

If the SDK supports streaming and the user enables it via a `BoolInput`, accumulate as the stream arrives and return the final `Message`:

```python
class AcmeChatModelComponent(Component):
    inputs = [
        ...,
        BoolInput(name="stream", display_name="Stream", value=False, advanced=True),
    ]
    outputs = [Output(display_name="Response", name="response", method="generate_response")]

    def generate_response(self) -> Message:
        from acme_sdk import Client

        client = Client(api_key=self.api_key, timeout=self.timeout_seconds)
        if not self.stream:
            result = client.chat(model=self.model, prompt=self.input_value)
            return Message(text=result.text)

        chunks = []
        for chunk in client.chat_stream(model=self.model, prompt=self.input_value):
            chunks.append(chunk.text)
            # The framework picks up chunks via the event manager when the component
            # is run in streaming mode at the flow level. Check the current SSE
            # convention in src/backend/base/langflow/services/event_manager.py before
            # implementing — the helper may have evolved.
        return Message(text="".join(chunks))
```

Note: real streaming integration goes through the framework's event manager. Read `services/event_manager.py` before assuming the API; this example shows the shape, not the exact wiring.

---

## Token accounting

```python
from lfx.schema.token_usage import TokenUsage

def generate_response(self) -> Message:
    ...
    usage = TokenUsage(
        input_tokens=result.usage.prompt_tokens,
        output_tokens=result.usage.completion_tokens,
    )
    msg = Message(text=result.text)
    msg.token_usage = usage
    return msg
```

Token usage flows into Langflow's tracing services (LangSmith, LangFuse). If your provider returns tokens, attach them — it powers cost and usage dashboards downstream.

---

## Redaction in logs

Never log:

- The API key, even partially.
- The full prompt body.
- The full response body.

Log:

- The operation name (`acme.chat`).
- The model identifier.
- Sizes (`prompt_chars`, `response_chars`, `tokens`).
- The duration.
- The outcome (`success` / `rate_limited` / `timeout` / `auth_failed`).

```python
import time
from loguru import logger

def generate_response(self) -> Message:
    from acme_sdk import Client, AcmeError

    start = time.monotonic()
    client = Client(api_key=self.api_key, timeout=self.timeout_seconds)
    try:
        result = client.chat(model=self.model, prompt=self.input_value)
    except AcmeError as exc:
        logger.warning(
            "acme.chat.failed",
            extra={
                "model": self.model,
                "outcome": "failed",
                "error_code": exc.code,
                "duration_ms": int((time.monotonic() - start) * 1000),
            },
        )
        raise

    logger.info(
        "acme.chat.succeeded",
        extra={
            "model": self.model,
            "outcome": "success",
            "prompt_chars": len(self.input_value or ""),
            "response_chars": len(result.text),
            "duration_ms": int((time.monotonic() - start) * 1000),
        },
    )
    return Message(text=result.text)
```

---

## Caching

If the component result is deterministic enough to cache (rare for LLMs, common for embeddings):

- Use Langflow's cache service (`langflow.services.cache`).
- Key on the **inputs that drive the output**, not the timestamp.
- Cache invalidation = a `BoolInput` named `force_refresh` defaulting to `False`, `advanced=True`.

Don't reinvent caching with a module-level dict.

---

## Tools and Agents

If the component is meant to be called by an agent as a tool, its `method` should:

- Accept inputs that the agent can describe in natural language (so the agent can fill them).
- Return a `Message` or `Data` shaped for the agent to consume (the agent will paraphrase or quote it).
- Document the contract in `description` carefully — the agent reads it.

`description` is the **prompt** the agent uses to decide whether to call the tool. Write it with that audience in mind: short, action-oriented, no internal jargon.

```python
class WeatherLookupComponent(Component):
    display_name = "Weather Lookup"
    description = (
        "Look up the current weather for a city. "
        "Input: city name. Output: a short message with temperature and condition. "
        "Use when the user asks about weather."
    )
    ...
```

---

## When NOT to wrap an SDK as a component

- The SDK returns binary payloads with no Langflow type that fits.
- The operation is long-running (minutes) without a streaming interface — Langflow components are synchronous from the flow's perspective.
- The SDK requires complex state that doesn't survive across method calls (the framework constructs a new component per execution).

For those cases, build a service (under `services/`) and expose a thin component that calls the service. Don't try to make the SDK fit if it doesn't.
