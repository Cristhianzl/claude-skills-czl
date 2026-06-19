---
trigger: Compiling the action checklist at the end of a Langflow PR review.
---

# Langflow-specific items to add to the action checklist

**Context:** The generic `reviewing-code/references/checklist.md` lists the universal items (PII in logs, file structure, SOLID, etc.). Langflow has additional items that must appear when relevant.

**Lesson:** Add these to the **Action checklist for the author** section when applicable:

```
Langflow-specific (when applicable):
- [ ] Component class name unchanged (or new class + old class deprecated = True)
- [ ] inputs[].name and outputs[].name unchanged on existing components
- [ ] Alembic migration declares Phase: EXPAND | MIGRATE | CONTRACT in docstring
- [ ] BUNDLE_API.md updated if anything public-facing changed in src/bundles/<name>/
- [ ] AI/LLM call has explicit timeout (not the SDK default)
- [ ] No raw prompt / response logged (only chars / tokens / outcome / duration)
- [ ] No top-level SDK instantiation in component module
- [ ] API key uses SecretStrInput, not MessageTextInput
- [ ] Tests use real integrations (mocks only for failure modes the sandbox can't reproduce)
- [ ] Tests use uv run pytest (not bare pytest) and the right ComponentTestBase
- [ ] Pre-commit was invoked via uv run git commit
- [ ] Version bump (if applicable) was done with make patch v=X.Y.Z
- [ ] Cross-platform: tested on Ubuntu / macOS / Windows in CI
- [ ] Icon: registered in lazyIconImports.ts AND the Python icon = "X" key matches
- [ ] Hot-reload verified: LFX_DEV=<provider> make backend shows the new component
```

**Why:** These items map 1:1 to Langflow-specific blockers and recommended practices. Including them in the action checklist gives the author a clear, copy-paste-ready set of next steps tied to the review findings.

**Apply when:** Writing the final action checklist section of a Langflow PR review.

## Severity hint

If any of these items is the reason for a `B` blocker finding, also list it as a Blocker action item (`- [ ] B<N> — <one-line>`) so it shows up under the blocker section, not just the general Langflow list.
