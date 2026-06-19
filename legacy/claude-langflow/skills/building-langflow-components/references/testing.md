# Testing components

The exact shape Langflow expects for component tests, the two base classes, and the conventions Langflow chose deliberately (no mocks, real integrations).

---

## Pick the right base class

| Base class                         | Use when                                                                                          |
|------------------------------------|---------------------------------------------------------------------------------------------------|
| `ComponentTestBaseWithoutClient`   | Pure-logic components. No HTTP backend client, no file uploads, no DB.                            |
| `ComponentTestBaseWithClient`      | Components that need the backend client (file inputs, vector store context, anything that calls Langflow's API). |

Both live in `src/backend/tests/base.py`.

---

## The three mandatory fixtures

Every component test class must provide:

| Fixture                | Type                              | Purpose                                                                       |
|------------------------|-----------------------------------|--------------------------------------------------------------------------------|
| `component_class`      | `type[Component]`                 | The class under test                                                          |
| `default_kwargs`       | `dict[str, Any]`                  | Minimum valid input set — instantiates a working component                    |
| `file_names_mapping`   | `dict[str, dict[str, str]]`       | Backward-compat snapshots: previous file name → current name (drop if N/A)    |

The fixtures power the base class's parametrized smoke tests: "can it be instantiated", "do all inputs resolve", "do all outputs run", "is the class name still discoverable under any of its previous names".

---

## Without-client example

```python
import pytest

from langflow.components.acme.acme_chat import AcmeChatModelComponent
from langflow.schema import Message

from tests.base import ComponentTestBaseWithoutClient


class TestAcmeChatModelComponent(ComponentTestBaseWithoutClient):
    @pytest.fixture
    def component_class(self) -> type[AcmeChatModelComponent]:
        return AcmeChatModelComponent

    @pytest.fixture
    def default_kwargs(self) -> dict:
        return {
            "api_key": "test-key-not-used-in-this-test",
            "model": "acme-balanced",
            "input_value": "Hello",
            "timeout_seconds": 30,
        }

    @pytest.fixture
    def file_names_mapping(self) -> dict:
        return {}  # no prior names

    def test_should_return_message_when_sdk_succeeds(self, component_class, default_kwargs, mocker):
        # When the goal is to assert wiring (not the provider), mock the SDK call
        mock_client = mocker.patch("acme_sdk.Client")
        mock_client.return_value.chat.return_value = mocker.Mock(text="Hi there")
        component = component_class(**default_kwargs)

        result = component.generate_response()

        assert isinstance(result, Message)
        assert result.text == "Hi there"

    def test_should_raise_value_error_when_sdk_fails(self, component_class, default_kwargs, mocker):
        from acme_sdk import AcmeError

        mock_client = mocker.patch("acme_sdk.Client")
        mock_client.return_value.chat.side_effect = AcmeError(code="rate_limited")
        component = component_class(**default_kwargs)

        with pytest.raises(ValueError, match="rate_limited"):
            component.generate_response()
        assert "rate_limited" in component.status
```

The first two tests run automatically from the base class (existence, defaults, output methods). The behavior-specific tests above are what you write per component.

---

## With-client example

```python
import pytest

from langflow.components.acme.acme_file_loader import AcmeFileLoaderComponent
from langflow.schema import Data

from tests.base import ComponentTestBaseWithClient


class TestAcmeFileLoaderComponent(ComponentTestBaseWithClient):
    @pytest.fixture
    def component_class(self) -> type[AcmeFileLoaderComponent]:
        return AcmeFileLoaderComponent

    @pytest.fixture
    def default_kwargs(self, file_uploader) -> dict:
        file_id = file_uploader.upload("tests/fixtures/sample.pdf")
        return {"file": file_id, "max_pages": 5}

    @pytest.fixture
    def file_names_mapping(self) -> dict:
        return {}
```

`file_uploader` is provided by `ComponentTestBaseWithClient`.

---

## Backward-compat snapshots — `file_names_mapping`

When a component's source file is renamed (e.g., moved to a different provider folder), Langflow's discovery layer needs to know the old path to keep saved flows working. The fixture captures the mapping:

```python
@pytest.fixture
def file_names_mapping(self) -> dict:
    return {
        "AcmeChatModelComponent": {
            "previous_file_path": "langflow.components.legacy.acme_chat",
            "current_file_path": "langflow.components.acme.acme_chat",
        },
    }
```

If the file has never moved, return `{}`.

**Note:** moving the file is OK if the class name stays the same and the mapping is captured. Renaming the **class** is not OK ever.

---

## Real integrations over mocks — Langflow's policy

From `AGENTS.md`:

> Avoid mocking in tests when possible. Prefer real integrations for more reliable tests.

Apply this to component tests when:

- The provider has a sandbox or free tier reachable from CI.
- The provider's behavior is the thing being tested.

Use real integrations marked with `@pytest.mark.api_key_required`:

```python
@pytest.mark.api_key_required
def test_should_complete_a_real_call(self, component_class, default_kwargs):
    default_kwargs["api_key"] = os.environ["ACME_API_KEY"]
    default_kwargs["input_value"] = "Say hi in one word."
    component = component_class(**default_kwargs)

    result = component.generate_response()

    assert isinstance(result, Message)
    assert len(result.text) > 0
```

The CI workflow provides API keys for the marked tests; local runs skip them unless the env var is set.

**Reserve mocks for:**

- Failure modes the provider's sandbox cannot reproduce (rate limit, timeout, malformed response).
- Tests that are about your **wiring** (does the component pass the right args to the SDK?) where the actual call isn't the point.

---

## Marks

| Mark                              | Meaning                                                                                       |
|-----------------------------------|------------------------------------------------------------------------------------------------|
| `@pytest.mark.api_key_required`   | Skip unless the env var the test reads is set. CI provides keys for the marked tests.          |
| `@pytest.mark.no_blockbuster`     | Skip when the blockbuster plugin is active (blockbuster wraps blocking calls).                 |
| `@pytest.mark.asyncio`            | Async test. Use sparingly — most component logic is sync; the runtime calls it async-safe.     |

---

## Running tests

```bash
# Single test file
uv run pytest src/backend/tests/unit/components/acme/test_acme_chat.py -v

# Single test
uv run pytest src/backend/tests/unit/components/acme/test_acme_chat.py::TestAcmeChatModelComponent::test_should_raise_value_error_when_sdk_fails -v

# All component tests in parallel
make unit_tests

# Sequential (for debugging order dependencies)
make unit_tests async=false

# Inside a sub-package — sync that package's dev group first
uv sync --group dev --package langflow-base
uv run pytest src/backend/base/tests/...
```

If you skip `uv sync --group dev --package langflow-base` before testing a sub-package, `fakeredis` and other dev-only deps won't be installed and the tests fail with confusing import errors.

---

## Coverage

The base classes' automatic tests count toward coverage. Plus the behavior tests you write. Target: 80%, floor: 75% — same as the generic `writing-tests` skill's gate, applied per-OS via the CI matrix.

---

## Common testing mistakes

- **Missing `file_names_mapping`** — base classes fail with a fixture error if the fixture isn't defined. Return `{}` even when there's no history.
- **Mocking the world** — Langflow's policy is "prefer real". Heavy mocking is a smell; if your test is 30 lines of mock setup, you're testing the mocks.
- **Calling `component.run()`** — components are executed via their declared output `method`. Call the method directly in tests; don't invent a `run()` entry point.
- **Asserting on `self.status`** when the test is about the return value. Two different concerns: `status` is UI-side feedback, the return value is the data contract.
- **Skipping `@pytest.mark.api_key_required`** — if your test calls the real provider, mark it. Otherwise CI on a fork without the secret will fail and waste reviewer time.
- **Running pytest without `uv run`** — pre-commit and the framework rely on the right Python. Bare `pytest` may pick a different interpreter.
