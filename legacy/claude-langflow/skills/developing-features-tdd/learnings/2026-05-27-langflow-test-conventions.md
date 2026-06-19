---
trigger: TDD phase 3 (RED) or any time the next step is writing a test against backend code.
---

# Langflow test conventions override the generic defaults

**Context:** The generic `developing-features-tdd` SKILL.md leans on `unittest.mock` / `pytest-mock` and emphasizes adversarial tests against fakes. Langflow has the opposite stance on mocking and uses specific base classes for component tests.

**Lesson:**

- **Prefer real integrations over mocks.** From `AGENTS.md`: "Avoid mocking in tests when possible. Prefer real integrations for more reliable tests." Reserve mocks for failure paths the real service or its sandbox cannot reproduce (rate limit, timeout, malformed payload).
- **Component tests use `ComponentTestBase[With/Without]Client`** from `src/backend/tests/base.py`. Required fixtures (provide all three even if empty):
  - `component_class` — the class under test.
  - `default_kwargs` — minimum valid input set.
  - `file_names_mapping` — backward-compat path snapshots (`{}` if none).
- **`@pytest.mark.api_key_required`** for tests that need an external API key. CI sets the keys; local runs skip unless the env var is present.
- **`@pytest.mark.no_blockbuster`** when the blockbuster plugin breaks the test (blockbuster wraps blocking I/O calls).
- **Graph tests follow a specific pattern** (per `AGENTS.md`):
  1. Build graph with connected components.
  2. Connect via `.set()` calls.
  3. Call `async_start` and iterate over results.
  4. Validate results.
- **Run tests with `uv run pytest …`**, never bare `pytest`. Pre-commit needs `uv run git commit`.
- **Sub-package testing** requires `uv sync --group dev --package <name>` before the first run, or dev deps (`fakeredis`, etc.) are missing.

**Why:** Langflow's bug history showed that heavily mocked tests passed while real integrations broke — the team's policy is now "prefer real". Component tests rely on the base class to drive parameterized smoke tests (existence, defaults, output methods) that catch the most common breakages; skipping the fixtures bypasses those checks.

**Apply when:** Any RED test in Phase 3 of the TDD cycle, especially for components and graph code.

## Cross-references

- The full anti-mocking rationale is in `building-langflow-components/references/testing.md`.
- Multi-platform tests follow the generic `ensuring-cross-platform` rules — Langflow's CI matrix (Ubuntu + macOS + Windows, Intel + ARM) is in `.github/workflows/cross-platform-test.yml`.
