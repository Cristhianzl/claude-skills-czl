# Data layer & scale

Cheap "born-scaled" defaults for any service that talks to a database. Apply them from day one — retrofitting pooling and indexes under load is an incident, not a refactor. Stack-agnostic: the idioms differ per ORM/driver, the rules don't.

## Connection pooling

- **Always use a pooled connection with explicit bounds.** Never open a connection per request/operation without a pool.
- Set them deliberately, don't accept blind defaults: **pool size**, **max overflow**, **acquire timeout**, and **recycle / pre-ping** (so a dead connection is dropped, not handed out).
- **Size the pool to the database, not the app.** Total connections across all instances × workers must stay under the DB's `max_connections`, with headroom for migrations/admin. Rough budget: `pool_size × instances × workers ≤ max_connections − reserve`.
- **Serverless / many short-lived instances → put a pooler in front** (e.g. PgBouncer in transaction mode). Per-instance pools don't bound total connections in that topology.
- One pool per process, created at startup — never per request.

## Indexes

- **Index every foreign key**, and every column used in `WHERE`, `JOIN`, `ORDER BY`, `GROUP BY`, or a uniqueness lookup. An unindexed filter is a full scan that looks fine at 1k rows and falls over at 1M.
- **Composite index order = predicate order:** equality columns first, then the range/sort column — `(tenant_id, status, created_at)` serves `WHERE tenant_id=? AND status=? ORDER BY created_at`. A composite can serve a left-prefix query; it can't serve one that skips its leading column.
- **Add the index with the feature**, in the same migration — don't wait for a slow query in prod.
- **Indexes cost writes and storage.** Don't index low-selectivity columns (e.g. a boolean) or duplicate a prefix already covered by a composite. Consider **partial** indexes (`WHERE active`) and **covering** indexes for hot read paths.
- On large/live tables, build **without locking** (Postgres `CREATE INDEX CONCURRENTLY`) in its own migration step.
- Enforce real invariants with a **unique index/constraint**, not only app-side checks.

## Query hygiene (the common scale killers)

- **No N+1.** Loading a list then a related row per item is N+1 — use eager/batch loading (a join, or a batched `IN (...)` / `selectinload`-style fetch).
- **No query inside a loop.** Hoist it to one set-based query.
- **Paginate every list from day one** (cursor preferred) — see `../../api-design/references/rest-conventions.md`.
- **Select only the columns you need** on hot paths; avoid shipping unused blobs.
- For hot counts/rankings at scale, prefer a **maintained counter/aggregate** over `COUNT(*)` per request.

## Transactions & timeouts

- Keep transactions **short**; never hold one open across an external/network call.
- Set a **statement/query timeout** so one pathological query can't pin a connection forever.
- Rely on DB constraints for correctness (uniqueness, FKs, checks), not only app code; pick the isolation level the invariant actually needs.

## What WOULD be over-engineering

Born-scaled ≠ premature distributed systems. Read replicas, sharding, a distributed cache, or CQRS come **only when a measured limit demands it**. Pooling, indexes, no-N+1, and pagination are the cheap baseline that buys you the runway to not need those yet.
