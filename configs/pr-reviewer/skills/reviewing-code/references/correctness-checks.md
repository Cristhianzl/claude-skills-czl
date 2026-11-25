# Correctness checks — state machines, control-flow exceptions, failure paths, locks and transactions

> The structural and security checks catch *shape* and *trust*. These catch a third class:
> **logic that is correct on the happy path and silently wrong on an edge or error path.**
> Most "it passed tests and review, then broke in production" bugs live here, because the
> failing path was never exercised.

---

## 1. Enum / state-machine completeness

When a PR **adds a member to an enum** (a status, state, signal, kind, role, event type), every
site that *enumerates* that enum must be revisited. Miss one and you get a silent gap: the new
state falls through a guard, a dispatch, or a filter as if it didn't exist.

**Why it's dangerous:** the addition compiles, the happy path works, and the gap only shows when
the system is actually *in* the new state — often a concurrency or recovery path that tests skip.

**What to grep** when an enum gains a member `NEW`:

```bash
# every membership test / dispatch / match over the enum type — audit each for the new member
grep -rnE "\.in_\(\[|\bin \{|\bin \(|match .*:|switch ?\(|== (Status|State|Kind|SignalType|Role)\." \
  --include="*.py" --include="*.ts" --include="*.go" | grep -i "<enum_name>"

# dict-dispatch tables keyed by the enum (a missing key = KeyError or silent default)
grep -rnE "\{[^}]*(Status|State|Kind)\.[A-Z_]+ *:" --include="*.py" --include="*.ts"
```

**Raise a finding when:** a new enum member is added but a `.in_([...])` guard, a `match`/`switch`,
an `if x in {...}` set, or a dispatch dict that handles its siblings was **not** updated. Name the
exact unhandled site and the behavior in the new state.

> Real example: adding a `SUSPENDED` job status but leaving it out of a dedupe guard's
> `.in_([QUEUED, IN_PROGRESS, COMPLETED])` — a retry while suspended bypasses dedupe and launches a
> second concurrent run.

---

## 2. Control-flow exceptions must propagate unwrapped

Some exceptions are **signals, not failures** — `pause`/`suspend`, `cancel`, `retry`, `redirect`,
`StopIteration`-style sentinels. They are raised deep and meant to be caught by a *specific* handler
several frames up. A generic `except Exception` (or `except: ... raise SomeError`) **between the
raise site and that handler** swallows or rewraps the signal — turning a pause into a "failure", a
cancel into a 500, a retry into a crash.

**What to grep:**

```bash
# broad excepts that re-raise as a different type — verify they let control-flow signals through first
grep -rnE "except (Exception|BaseException)" -A3 --include="*.py" | grep -iE "raise [A-Z][A-Za-z]*Error\(|raise ValueError"

# the catch-all that returns/logs instead of re-raising (may eat a cancel/pause)
grep -rnE "except (Exception|BaseException)[^:]*:" -A2 --include="*.py" | grep -iE "return|pass|continue"

# JS/TS: a catch that maps every error to one shape
grep -rnE "catch *\(.*\) *\{" -A3 --include="*.ts" --include="*.js" | grep -iE "throw new |return \{ *(ok|error)"
```

**Raise a finding when:** a control-flow/signal exception can reach a generic handler that wraps or
swallows it. The fix is a narrow `except SignalException: raise` (or equivalent) placed **before**
the generic handler, at *every* layer the signal crosses (the build loop, the run wrapper, the job
boundary — not just the innermost one).

> Real example: `Graph._run` wrapped *everything* from `process()` in `raise ValueError(...)`, so a
> `GraphPausedException` reached the job layer as a `ValueError` and the run was finalized FAILED
> instead of SUSPENDED. One `except (GraphPausedException, CancelledError): raise` before the
> generic except fixes it — and the same guard is needed at each enclosing layer.

---

## 3. Degrade-don't-crash contracts, and the test that proves it

If a function's contract is **"degrade gracefully"** (return `None`/a default, skip, fall back) when
an input can't be handled, then it must **never hard-raise** on that input — a raise escapes to a
caller that assumed the contract held, often bypassing an entire code path (a pause, a checkpoint, a
retry). Two recurring shapes:

- A serializer/normalizer documented to "drop non-serializable values to `None`" that actually
  `raise`s on one — escaping the path that was supposed to continue.
- A nested-collection degrade that only checks the *top-level* value: an opaque *member* of a
  returned dict/list silently becomes `None`, corrupting state without bubbling up.

**The decisive review question (it doubles as the test spec):**

> *For every new state and every failure branch — is there a test that fails if I delete this line?*

A PR that adds a `SUSPENDED` state, a degrade-to-`None` path, a rollback-on-failure, or a
suspend/resume boundary, but whose tests only exercise the clean happy path, is **under-tested by
construction**. Ask for the adversarial cases (`writing-tests` covers the shapes): non-serializable
input, the failure mid-persist, the timeout-cleanup path, the concurrent retry, the loop/cyclic
flow. The happy-path green is not evidence the edge path works — it's evidence it was never run.

> Real examples caught only by edge tests: a checkpoint builder that hard-raised on a non-JSON
> `built_object` (bypassing the pause → run FAILED); a resume that re-consumed an already-exhausted
> async generator; a deadline sweep that transitioned the job but leaked its checkpoint row.

---

## 4. Locks, transactions, and concurrency

Concurrency defects pass every single-threaded test and every diff-only read. Review them as four questions, answered with code outside the diff (`context-sweep.md` sweeps 1 and 3).

**What is locked, and how strongly?** Name each lock the change takes: a row lock (and its mode), a table lock, a database-wide write lock, an advisory lock, a file or distributed lock. Lock modes differ by engine, and plain writes take locks too. Observed on PostgreSQL 17.9: a no-op `UPDATE` of a non-key column on a row behaves like `SELECT … FOR NO KEY UPDATE` — inserts into child tables that reference the row go through, while another non-key `UPDATE` of the row and another `FOR NO KEY UPDATE` wait; `SET id = id` behaves the same because the key value doesn't change; `FOR UPDATE` also blocks those child inserts. Observed on SQLite (WAL): a single-row no-op `UPDATE` inside a transaction takes the database-wide write lock, so a write to an unrelated table waits, while plain reads continue. Two engine-specific branches that end up taking the same lock can often be one statement — check before accepting both.

**How long is it held?** A lock lives until the enclosing transaction ends (observed: the competing update waited while the holder's transaction was open and went through right after it committed). Find who owns that transaction — often a caller far from the diff, such as a startup sweep or a batch job that commits once at the end. A per-item lock inside a loop that commits once holds every item's lock until the last item is done. Long-running work over many items commits per item, like any established per-item helper in the codebase.

**Who else waits?** From the contention map: every other path that writes or locks the same rows — user-facing requests above all (a profile save, a checkout updating stock, a token refresh). If a request waits behind a background sweep, the finding is the measured or estimated wait, not "possible contention". When the environment allows, measure it: hold the lock in one session and time the competing statement in another.

**What does an error inside the transaction do?** On PostgreSQL, after any failed statement the transaction is aborted and every later statement is rejected until a rollback (observed: "current transaction is aborted, commands ignored until end of transaction block"); a `ROLLBACK TO SAVEPOINT` recovers it. So a loop that catches an exception per item and continues — without a rollback or savepoint — fails every following item and loses the earlier uncommitted work. The contract to look for is explicit: per-item atomicity (commit or roll back each item) or all-or-nothing (stop at the first error), and a test for the one chosen.

Also check lock ordering when several rows are locked in one transaction (consistent order, or deadlocks under load), retries on lock timeouts (bounded, with backoff), and that idempotency comes from a constraint or a conditional write rather than from check-then-insert timing.
