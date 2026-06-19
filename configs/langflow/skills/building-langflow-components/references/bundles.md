# Bundles — when a component doesn't belong in base

Not every component should ship in `langflow-base`. Some are niche, some bring heavy or ecosystem-specific dependencies, some are maintained by a partner. Those live in **bundles** under `src/bundles/<bundle_name>/`.

Generic, broadly useful components (top model providers, top vector stores, top retrievers) live in `src/backend/base/langflow/components/<provider>/`.

---

## The decision tree

Use base when **all** of these are true:

- The component covers a top-N integration that the typical user expects to find out of the box.
- The dependency is small (or already pulled by another core component) and broadly compatible.
- The component is maintained by the Langflow team (or has a stable upstream you're willing to follow).

Use a bundle when **any** of these is true:

- The component is for a niche provider, region, or ecosystem.
- The dependency is heavy, optional, or has tricky compatibility (e.g., a CUDA-only library, a specific OS).
- A partner team owns it.
- It's experimental and may break.

If in doubt → put it in a bundle. Promoting from bundle to base later is easy; the reverse is painful for users who already depend on the import path.

---

## Bundle structure

```
src/bundles/<bundle_name>/
├── pyproject.toml              # bundle's own dependencies
├── BUNDLE_API.md               # public-facing changelog — REQUIRED
├── README.md                    # what the bundle does, installation, links
└── src/lfx_<bundle_name>/      # importable Python package
    ├── __init__.py
    └── components/
        ├── <provider>/
        │   ├── __init__.py
        │   └── my_component.py
        └── ...
```

The exact layout is enforced by the existing bundles — copy the structure from `src/bundles/duckduckgo/` or `src/bundles/arxiv/`.

---

## `BUNDLE_API.md` — the changelog gate

Every public-facing change to a bundle must be recorded in `BUNDLE_API.md`. A pre-commit hook (or CI check) blocks merges that change the bundle without updating this file.

Format:

```markdown
# Bundle API — <bundle_name>

## [Unreleased]

### Added
- `AcmeChatModelComponent`: support for the new `acme-deep` model.

### Changed
- `AcmeEmbeddingsComponent`: default `batch_size` raised from 16 to 64.

### Deprecated
- `AcmeLegacyChatComponent`: marked deprecated; will be removed in 2.0.

## [1.4.0] — 2026-04-12

### Added
- `AcmeFileLoaderComponent`.
```

What counts as a "public-facing change":

- Adding, deprecating, or removing a component class.
- Adding, renaming, or removing an input or output `name`.
- Changing a default value that affects behavior.
- Changing the dependency stack in `pyproject.toml`.
- Anything a downstream user might notice across a version bump.

What doesn't:

- Internal refactor that preserves the public surface.
- Tests, docs, comments inside the component.
- Whitespace, formatting, type-hint additions.

---

## Importing a bundle component

From inside Langflow:

```python
from lfx_acme.components.acme.acme_chat import AcmeChatModelComponent
```

The bundle module name is conventionally `lfx_<bundle_name>`. Check the existing bundles for the exact pattern before you assume.

---

## Adding a new bundle (rare)

When a whole new bundle is needed:

1. Open an issue / RFC first — adding a bundle is a project-level decision (maintenance burden, naming, governance).
2. Once approved, scaffold using `src/bundles/duckduckgo/` as a template.
3. Add the bundle to the workspace in the root `pyproject.toml` so `uv sync` picks it up.
4. Add a CI lane that runs the bundle's tests in isolation (the cross-platform-test workflow has examples).
5. Document the bundle in `docs/docs/Bundles/<bundle_name>.mdx`.

Adding a single **component** to an existing bundle is normal and doesn't need an RFC.

---

## Dependencies

The bundle's `pyproject.toml` declares its own deps. Keep them minimal and **pinned to compatible ranges** (`acme-sdk>=1.0,<2.0`), not exact pins (`acme-sdk==1.4.2`), so user-side compatibility doesn't break on minor SDK updates.

If the dependency is heavy (>50 MB), or has platform-specific wheels (CUDA, etc.), document the installation gotchas in the bundle's `README.md`.

---

## Testing a bundle

Bundle tests live alongside the bundle:

```
src/bundles/<bundle_name>/tests/
├── conftest.py
└── unit/
    └── components/
        └── test_acme_chat.py
```

Run them with:

```bash
uv sync --group dev --package lfx-<bundle_name>
uv run pytest src/bundles/<bundle_name>/tests/ -v
```

The same `ComponentTestBaseWith[out]Client` classes apply.

---

## Common mistakes

- **Forgetting `BUNDLE_API.md`.** Pre-commit / CI will block the merge. Update it as part of the same commit, not later.
- **Pinning exact dependency versions.** Use compatible ranges so users on the bundle aren't blocked by every minor upstream release.
- **Importing from `langflow.components.<provider>`** when the component lives in a bundle. Use `lfx_<bundle>.components.<provider>`.
- **Putting niche components in base.** Inflates the base install size and creates support burden. If in doubt, bundle.
- **Creating a bundle for one component.** Justified only if the component genuinely needs ecosystem isolation. Otherwise put it in base (or wait until you have a cluster of related components).
