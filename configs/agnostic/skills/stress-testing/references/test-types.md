# The six load-test types

Each type answers one question with a distinct load profile. Source of truth for the taxonomy: Grafana's load-testing guidance ([grafana.com/load-testing/types-of-load-testing](https://grafana.com/load-testing/types-of-load-testing/)). Tailor absolute numbers to the project's real traffic — never copy someone else's percentages.

## Smoke — "does it work at all?"

Minimal load (<5 VUs, seconds to minutes). Validates the test script itself, the environment, and baseline behavior before any real load. **Run it first, every time** — a broken script under heavy load produces expensive garbage.

## Average-load — "does it handle normal traffic?"

Simulates typical production concurrency: gradual ramp-up → plateau at normal load (5–60 min) → ramp-down. This is the baseline every other type compares against. Derive "normal" from real analytics/APM numbers (concurrent users, RPS at a typical peak hour), not from guesses.

## Stress — "does it handle the peak?"

Same shape as average-load at 50–100%+ higher load — the Black-Friday-morning level, not the apocalypse. Run **only after** average-load passes. Before expected high-traffic periods.

## Spike — "does it survive a sudden surge?"

Near-instant jump to very high load, brief hold, fast drop — the flash-sale / viral-moment / TV-ad shape. Tests autoscaling reaction time, queue behavior, and rate-limiting. Recovery matters as much as survival: does the system return to normal after the spike, or stay wedged?

## Breakpoint — "where and how does it break?"

Progressive ramp to unrealistic load until thresholds fail. The output is not pass/fail — it's **the knee of the curve** (the load where p95 takes off), **what saturated first** (CPU, DB pool, memory, disk, downstream API), and **the failure mode** (graceful 429s/queuing vs cascading timeouts). Feeds capacity planning and the `data-layer.md` scaling decisions. Run in isolated environments — it ends in failure by design.

## Soak — "does it degrade over time?"

Average load sustained for hours or days. Catches what short tests can't: memory leaks, connection-pool exhaustion, disk filling from logs/temp files, cache drift, scheduled-job pile-ups. Watch resource trends over time, not just latency: flat load with climbing memory is the finding.

## Choosing

- New system or new test suite → smoke, then average-load. Grow from there.
- Preparing for an event → stress + spike.
- Capacity planning / "how far can we go" → breakpoint.
- Leak suspicion, long-running degradation reports → soak.
- One type never eliminates all risk — they target different failure modes; combine over time.
