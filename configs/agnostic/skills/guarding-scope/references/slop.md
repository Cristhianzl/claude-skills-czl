# AI slop — the catalog and the deslop pass

**Slop** is code that compiles, passes review at a glance, and quietly degrades the codebase. It is the quality side of gold plating: nobody asked for it, it adds weight, and it hides the real change. Scope creep is *what* you changed; slop is *how much noise* you added while changing it. Both fail the same test: every added line must earn its place.

## The catalog (check added lines only)

| Slop | What it looks like | Keep it only when |
|---|---|---|
| **Ceremonial comments** | `// increment counter`, `# Initialize the list`, section dividers, docstrings restating the signature | It's a one-line WHY the code can't express |
| **Defensive overkill** | try/catch around code that can't throw, triple null checks, re-validating already-validated input, `if (x === true)` | It guards a real system boundary (user input, external API, I/O) |
| **Empty catch-and-log** | `catch (e) { console.error(e) }` that swallows and continues | Never — handle, rethrow with context, or let it propagate |
| **Type escapes** | `as any`, `: any`, `# type: ignore`, `cast(...)` to silence the checker | Never to silence — fix the type |
| **Speculative generality** | Interface/base class/factory with one implementation; options nobody passes; "for future use" params | There are ≥ 2 real callers today |
| **Single-use helpers** | A helper, util, or module created for one call site | It removes real duplication or names a non-obvious concept |
| **Pattern drift** | Different naming, error style, import style, or structure than the rest of the file | Never — match the file |
| **Verbose ceremony** | `isUserAuthenticatedAndAuthorizedFlag`, `Promise.all([single])`, needless intermediate variables | It genuinely aids reading |
| **Debug residue** | `print`, `console.log`, function entry/exit logging, commented-out code | Never in the final diff |
| **Generic TODOs** | `// TODO: add error handling`, `// TODO: optimize` | It names an owner/ticket and a concrete gap |
| **Fallback that hides bugs** | `value ?? defaultThatMasksAMissingField`, silent `except: pass` defaults | The default is a documented contract |
| **Unrequested artifacts** | Summary `.md` files, example scripts, extra test files for unchanged code | The user asked for them |

## The deslop pass (procedure)

Run it on **your** added lines (`git diff` — the `+` side), before the scope audit's report step:

1. For every added comment: is it a WHY the code can't say? No → delete.
2. For every added try/catch, null check, fallback, validation: is this a system boundary, or a path where the failure can really happen? No → delete.
3. For every cast / `any` / ignore: fix the type instead.
4. For every new helper/abstraction/option: ≥ 2 real callers or a requested use? No → inline it.
5. For every new name and construct: does it match the file's existing style? No → match it.
6. Remove debug residue, commented-out code, generic TODOs.
7. Keep behavior identical and keep domain-valid guards — **remove only inconsistent slop**. The deslop pass never redesigns, never touches lines you didn't add, and never widens scope.

Report it in one line at most ("Removed 3 redundant comments and an unreachable try/catch I had added"). If nothing was found, say nothing.

## What the deslop pass is NOT

- Not a license to clean up pre-existing code (that's scope creep — parking lot).
- Not a refactor pass.
- Not a reason to delete security floors: boundary validation, authz checks, PII-safe logging, and real error handling stay.
