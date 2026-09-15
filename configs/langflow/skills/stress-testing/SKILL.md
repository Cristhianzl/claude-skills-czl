---
name: stress-testing
description: Plan, run, and interpret load and stress tests — smoke, average-load, stress, spike, breakpoint, and soak — with realistic workload modeling (open vs closed model, coordinated omission) and SLO-based thresholds (p95/p99, error rate). Use ONLY when the user explicitly asks for a load test, stress test, performance test under load, capacity check, spike/soak/breakpoint test, or "how much traffic can this handle". NEVER run or suggest running load tests proactively — they hammer real systems, consume resources, and can degrade shared environments. If load-related risk is spotted during other work, mention it in one line and stop.
license: MIT
---

# Stress testing — load, spike, soak, breakpoint

Load testing answers questions about a system under traffic. There is no single "stress test" — there are **six test types, each answering one question**, and the discipline is picking the right question, modeling realistic load, and judging by percentiles against a declared SLO.

## Hard rule: explicitly requested only

**Never run, schedule, or "quickly check" a load test on your own initiative.** Load tests consume real resources and can degrade or take down the target — especially shared/staging environments. This skill activates only when the user asks for it, against a target the user names. Before any run, confirm: the target environment (never production unless the user explicitly says so and owns that decision), and that the user accepts the load about to be generated.

## Read first (always)

List `learnings/` — the project's SLOs, tooling, environments, past baselines, and known bottlenecks live there and override defaults here.

## The six types (pick by the question — `references/test-types.md`)

| Type | Question | When |
|---|---|---|
| **Smoke** | Does the script and system work at all? | Always first; <5 VUs, minutes |
| **Average-load** | Does it handle **normal** production traffic? | The baseline; before any other heavy type |
| **Stress** | Does it handle the **peak** (50–100%+ above normal)? | Before high-traffic events |
| **Spike** | Does it survive a **sudden surge**? | Before launches/campaigns |
| **Breakpoint** | **Where and how** does it break? | Periodically, for capacity planning |
| **Soak** | Does it **degrade over time** (leaks, pools, disk)? | After significant changes; hours/days |

**Golden order: smoke → average-load → only then stress/spike/soak/breakpoint.** Stressing a system never validated at average load produces noise — you can't tell whether the peak broke it or it never handled normal traffic.

## Workflow

1. **Define pass/fail before generating load.** SLO-derived thresholds, declared in the tool (e.g. k6): `http_req_duration: ['p(95)<200']`, `http_req_failed: ['rate<0.01']`. **Percentiles, never averages.** No SLO? Derive a provisional one from current production percentiles (`observability.md`) and say so.
2. **Model the workload realistically** (`references/workload-modeling.md`): traffic-based scenario mix, parameterized data, human pacing, **open model** (arrival rate) for request-driven systems — and know the coordinated-omission trap.
3. **Confirm target + environment with the user**, sized realistically (data volume matters: problems hide at 1k rows and surface at 1M — see `data-layer.md`).
4. **Run smoke, then the chosen type.** Observability on during the run (metrics/traces tell you *why*; the test only tells you *that*).
5. **Interpret** (`references/interpreting-results.md`): thresholds pass/fail, the latency distribution, the knee of the curve, what saturated first, graceful vs catastrophic failure.
6. **Record the baseline** in `learnings/` — a load test without a previous baseline to compare against is half a test.

## Non-negotiables

- **Never against production** unless the user explicitly directs it and owns the call — and then with a kill switch (a way to stop the load immediately).
- **A saturated load generator invalidates the test.** If the generator hit its own limits, the results are inconclusive — discard and rerun with more capacity, never report them as findings.
- Results reported with **evidence** (the actual output, thresholds vs measured values), never "seemed fine" — same bar as `validating-in-reality`.
- Keep generator location/config consistent across runs; a moved generator invalidates comparison with the baseline.

## Capture a learning

Save the project's SLOs, tool choice, environment names, baseline numbers, and where it broke (`learnings/YYYY-MM-DD-slug.md` or `/learn`).

## See also

- `references/test-types.md` · `references/workload-modeling.md` · `references/interpreting-results.md`
- `skills/developing-features/references/observability.md` — percentiles, dev-time latency checks.
- `skills/developing-features/references/data-layer.md` — what saturates first (pools, indexes, write scaling).
- `skills/validating-in-reality` — evidence-over-assumption reporting.
