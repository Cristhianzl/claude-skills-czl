---
trigger: Deciding whether a change to a Langflow component, migration, locale file, or bundle is required by the request or is scope creep.
---

# Langflow scope boundaries — what counts as required

**Context:** Langflow's backward-compat and i18n rules force some changes that look like expansion but are part of doing the requested change correctly. Others look harmless and are pure creep that breaks saved flows.

**Lesson:**

- **Required, not creep:** keeping a deprecated input/output in place while adding its replacement; marking the old component `legacy=true` when a new one supersedes it; adding a new i18n key to **every** locale file in the same PR; shipping an Alembic migration with the model change that needs it (with its `Phase:` marker); updating `BUNDLE_API.md` when the repo uses it and the bundle changed. Disclose these under "Beyond the literal request (required)".
- **Creep — never without an explicit ask:** renaming a Component class, its `name`, or any `inputs[].name` / `outputs[].name` "for consistency" (it breaks every saved flow); "cleaning up" deprecated fields; moving components between provider folders; reformatting or retyping a component you only needed to read; touching `lfx` when the request is server-only, or the reverse; adding providers, inputs, or options the request didn't name.
- **Scope does not shrink the portability floor.** The cross-platform and run-mode rules (Windows/Linux/macOS, server/API/Docker/`lfx`) apply to the lines you change — they are not an excuse to rework untouched code for portability. Portability issues you notice elsewhere go to the parking lot.

**Why:** In Langflow a "harmless" rename or cleanup is a silent breaking change for every user with a saved flow, so drive-by edits carry far more risk than in a typical repo.

**Apply when:** writing the scope contract and running the scope audit on any Langflow change.
