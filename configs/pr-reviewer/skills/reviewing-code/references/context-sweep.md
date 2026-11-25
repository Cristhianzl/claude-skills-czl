# Context sweep — what the diff doesn't show

Most defects a careful human reviewer catches and a diff-only review misses live **outside the changed lines**: in the caller that owns the transaction, the other code path that writes the same row, the consumer of a value whose type just changed, the CI workflow that never runs the new test, or the helper the codebase already has for exactly this. This reference turns that into a fixed procedure. It is language-, framework-, and architecture-agnostic; the commands are examples of "search the repository", so use your stack's equivalent.

## Risk tiers — set the depth before reading for defects

Classify the PR by the riskiest thing it touches. The tier decides how much of this sweep is mandatory and how the review runs.

| Tier | The diff touches… | Depth |
|---|---|---|
| **3 — deep** | Concurrency, locks, transactions, retries, idempotency; schema changes and migrations; startup/boot paths and background sweeps; authentication or authorization; money, quotas, or irreversible deletes; data shared across users, tenants, or processes | All five sweeps below, the concurrency lens (`correctness-checks.md` §4), and every check in `test-evidence-checks.md`. Execute, don't only read: run the new tests against the base and the head on every engine they claim to cover, and measure any cost the change accepts (§ Execute before you judge). A reviewer with fresh context, never only the author's own pass. If an automated reviewer is also used, run it at its high effort level or above — a "few high-confidence findings" setting is not enough here. |
| **2 — standard** | New endpoints, business logic, new tests, configuration that changes behavior | Sweeps 1, 2, and 4; the rest when a finding points there. |
| **1 — light** | Docs, comments, copy, formatting, dependency bumps without API change | The security lens and the scope check; no sweep unless something surprises you. |

When unsure between two tiers, take the higher one — the cost of a deep pass is minutes, the cost of a missed lock or an untested migration is an incident.

## Execute before you judge (Tier 3)

A reviewer who only reads the code can say "this might block" or "this test probably fails on the base". A reviewer who runs it can say "the competing login waited 4.7 seconds" and "the two-workers test fails 3 of 3 on the base and passes 15 of 15 on the head". On a Tier 3 PR, that evidence is part of the review, not a bonus:

1. **Set up what the tests need.** Install the project's dependencies with its own tooling (the lockfile-enforcing install), and start a **throwaway** instance of every external engine the tests are parametrized over — a local database cluster on a free port with its own data directory, a container, an in-memory fake only when the real engine is impossible. Never point tests at a shared or long-lived instance.
2. **Run the new tests on the head and on the base** (the base with the PR's tests applied, `test-evidence-checks.md` §1), on every engine. Record pass/fail counts per engine.
3. **Measure what the change trades away.** If it takes a lock, hold it the way the change does (inside a transaction of realistic length) and time the competing operation from a second session. If it adds work to a hot path, time the path before and after. A trade-off the author accepted in prose becomes a number in the review.
4. **Check the CI evidence** when CI has run: the job log lists the new tests as run, and the coverage report covers the changed lines.

If any step can't be done in the time available, say exactly which one and why in the summary ("not verified empirically: no PostgreSQL available") and keep the affected findings phrased as unverified. Do not approve a Tier 3 concurrency or migration change on reasoning alone; ask for the evidence instead.

## The five sweeps

Each sweep starts from what the diff changes and follows it to code the diff doesn't show. Record what you followed in the review's summary ("I traced the two callers of `reserve_stock` and the other writers of `products`…") — a reader should see that the sweep happened.

### 1. Callers and transaction owners

For every function the diff changes or adds, find who calls it and what context they put around it — above all, **who opens and commits the transaction**, which retries or timeouts wrap it, and which loop it runs inside.

```bash
git grep -n "reserve_stock(" -- ':!*test*'
```

The questions: Does a caller run this inside one long transaction (a startup sweep over every account, a nightly batch over every order), so anything this function locks stays locked until the caller commits? Does a caller swallow its exceptions? Is it called per request, per user, or once per process? A function that is correct alone can be wrong in the context every caller gives it.

→ verify: for each changed function you can name its callers, who owns the transaction, and how long that transaction lives.

### 2. Consumers of changed values

For every value whose **type, format, identity, or meaning** changes — a variable rebound to a different type (`account_id = int(account_id)`, `key = key.lower()`), a cast, a renamed field, a new default, a changed unit, a different encoding — find everything downstream that consumes it: storage keys, cache keys, external systems, serializers, comparisons, logs, other services. Pay special attention to values that are later used to **address** something (a secret name, a file path, a cache entry, a partition, a URL), because two representations of "the same" ID can address different things.

```bash
git grep -n "cache_key(\|storage_path(\|account_id" -- 'src/'
```

Make it mechanical: **list every parameter or variable the diff reassigns** — the same name on both sides of an assignment, or a name reassigned after it was already used — and for each one, list every use **after** the reassignment. Pay attention to parameters declared with a union or loose type (`A | B`, `str | int`, an untyped argument): the code before the reassignment ran with whatever the caller passed, the code after it runs with the new type, and any consumer that behaves differently per type (an encoder, a key builder, a lookup) now sees a different value for some callers. Introducing a new name for the converted value (`lock_key = int(account_id)`) and keeping the original for everything else is usually the fix.

```bash
git diff <base>...HEAD -U0 | perl -ne 'print if /^\+\s*([A-Za-z_]\w*)\s*=(?!=).*\b\1\b/'
```

It lists candidate lines (a few are ordinary initializations to dismiss); `grep -P` works too where available. Then, for each real rebinding:

```text
<name>: reassigned at <file:line> from <declared type> to <new type>; uses after it → <each consumer and whether it accepts the new type>
```

→ verify: every rebinding or conversion in the diff is either confined to one use or followed to each consumer, and each consumer accepts the new form for every type the parameter is declared to accept.

### 3. Contention map — who else touches what this change locks or writes

For every row, table, file, key, queue, or lock the diff writes or locks, list the **other** code paths that read or write the same thing, and when they run. Search by the model, table, and column names, not only by the function name.

```bash
git grep -n "stock_level\|update(Product)\|products SET" -- ':!*test*'
```

The questions: If this change holds a lock for the duration of a long transaction, which user-facing request waits behind it (a checkout decrementing stock, a profile save, a token refresh)? If this change writes a row another path also writes, which write wins, and is either one lost? Does a background job run at the same time as requests?

→ verify: for each lock or write you can name the competing paths, and for each competing path whether it waits, fails, or wins.

### 4. Wiring — does it actually run where the PR says it runs?

New tests, migrations, configuration, feature flags, and jobs only matter if something runs them. For each:

- **Tests:** find the CI workflow and job that execute the file. If the test is gated (an environment variable, a database dialect, a marker, a `skipif`), confirm that job sets what the gate needs. If the workflow lists test files explicitly, confirm the new file is in the list. When CI results are available, confirm the job log shows the new tests ran and were not skipped, and check coverage for the changed lines.

  ```bash
  git grep -n "TEST_DATABASE_URL\|pytest .*tests/" -- .github/ ci/ Makefile
  ```

- **Migrations:** the migration chain has one head; the model and the migration agree; the migration is exercised by whatever validates migrations in CI.
- **Config, flags, jobs:** the new setting is read where it's needed, has a default in every environment, and the job is registered with the scheduler.

A PR description that reports results from a local run ("all green against the real database") is a claim about the author's machine. Check which of those results CI reproduces; a gated arm that only ran locally is untested for everyone else.

→ verify: every new test, migration, flag, and job is wired into something that runs it, and every gated arm runs somewhere in CI.

### 5. Precedent and platform

Before accepting new machinery, search for how the codebase already solves the same problem and what the dependencies already provide at the version the project actually requires.

```bash
git grep -n "with_retry(\|per_item_transaction(\|create_if_missing" -- src/
grep -n "<library>" <manifest> <lockfile>
```

The questions: Is there an established pattern for this (a per-item commit helper, a lock helper, a migration idiom) that the PR diverges from without saying why? Does the library, at the project's declared minimum version, already offer this as a parameter or function (check the dependency floor in the manifest or lockfile against the library's changelog)? Can two branches become one statement because the platform already behaves the same way on both? Divergence from precedent is a consistency finding; hand-rolled code the platform already provides is a simplification finding — and on a Tier 3 PR, the simpler form is often also the more correct one.

→ verify: for each new mechanism you checked for an existing pattern and a platform-provided equivalent at the project's dependency floor.

## Reporting what the sweep finds

A sweep finding cites both ends: the changed line and the code outside the diff that makes it a problem ("`stock.py:88` locks each product row; the only caller runs the nightly reconciliation in one transaction (`jobs/reconcile.py:40`), and checkout updates the same rows (`checkout.py:112`) — so every checkout waits for the whole reconciliation"). When you can measure the consequence, do: a second session performing the competing write while the first holds the lock turns "might block" into a measured wait.
