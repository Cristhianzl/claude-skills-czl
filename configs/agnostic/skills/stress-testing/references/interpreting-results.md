# Interpreting results — from numbers to decisions

The test says *that* something degraded; observability during the run says *why*. Always analyze both together.

## Judge against declared thresholds

Pass/fail was defined before the run (SLO-derived, e.g. `p(95)<200ms`, `error rate<1%`). Report the measured value next to the threshold — "p95 312ms vs threshold 200ms" — never adjectives. A threshold tool-enforced (k6 exits non-zero) makes the test CI-runnable.

## Read the distribution, not a number

- **Averages lie under load** — they smooth out exactly the pain you're hunting. Read p50/p90/p95/p99 + max.
- A **gap between p50 and p99** widening as load grows = queuing somewhere (pool, GC, lock, downstream).
- **Error rate and latency together**: fast errors can *improve* latency numbers while the system fails (a 500 in 5ms beats a 200 in 800ms on the chart). Segment latency by response status — k6 tags `expected_response` for this.
- **Throughput plateau while load grows** = saturation: requests queue, latency climbs, RPS stays flat. That's the system's ceiling at this configuration.

## Find the knee and the bottleneck

- Plot latency vs load across steps: the **knee** is where p95 leaves linear growth. Capacity planning happens at the knee, not at the crash.
- Correlate with system metrics at the knee timestamp: CPU, memory, DB connections in use, queue depth, downstream latency. **The first resource to saturate is the finding** — and usually maps to `data-layer.md` suspects (pool size, missing index, N+1 amplified, sync I/O on the hot path).
- Failure mode matters as much as failure point: graceful (429s, load shedding, queued with backpressure) vs catastrophic (timeout cascades, OOM, crash loops). Catastrophic at reachable load = a fix, not a note.

## Soak-specific reading

Trend lines over hours, not snapshots: memory climbing under flat load (leak), connection count creeping (leak/no timeout), disk filling (logs/temp), latency drifting upward (fragmentation, cache decay). The slope is the finding.

## Recovery

After spike/stress/breakpoint, watch the return to baseline: does latency recover within minutes, do queues drain, do circuit breakers close? A system that survives the spike but stays degraded for an hour failed the test.

## Report format

Target + environment (and how far from production) · test type + question it answered · workload model (open/closed, rate/VUs, mix, data) · thresholds vs measured (table) · the knee / bottleneck / failure mode with the correlated system metric · recovery behavior · generator health (proof it didn't saturate) · baseline comparison (or "first baseline, recorded in learnings/") · prioritized recommendations. Real output pasted, trimmed to the relevant part.
