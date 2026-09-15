# Workload modeling — making the load real

A load test is only as good as its model of reality. N identical requests in a loop measures your cache, not your system.

## Open vs closed model — the decision that changes everything

- **Closed model**: a fixed number of virtual users in a loop; each sends the next request only after the previous one completes. Models systems that pull work (a worker draining a queue, a call center with N agents).
- **Open model**: new requests arrive at a set rate **regardless of how the system is coping** (k6 `constant-arrival-rate` / `ramping-arrival-rate`). Models the real web: users keep arriving whether or not the site is slow.

**Request-driven systems (web/API) must be tested with the open model.** A closed generator self-throttles: when the system slows down, iterations take longer, so the generator sends *less* load — exactly when production would be piling *more* on. Closed-model results for an open system are optimistic by construction.

## Coordinated omission — the statistical trap

The measurement artifact of that self-throttling: during the worst moments the closed generator stops issuing (and therefore stops *measuring*) requests, so the bad samples are missing from the dataset and the reported average/p95 comes out artificially good. Defenses:

- Use the open model for open systems.
- Judge by **p95/p99 and the max**, never the average.
- **If the load generator itself saturates (CPU, sockets, bandwidth), the run is inconclusive** — discard it and rerun with more generator capacity; never report its numbers.

## Scenario realism

- **Traffic mix from real data**: weight endpoints/flows by production analytics (e.g. 70% browse, 20% search, 10% checkout), not one endpoint hammered in isolation — unless the question is specifically about that endpoint.
- **Parameterize the data**: varied users, IDs, and payloads per iteration (k6 `SharedArray` from a JSON/CSV). Identical requests hit caches and unique-constraint paths that real traffic doesn't.
- **Human pacing**: randomized sleeps between steps in user-flow scenarios; humans don't fire requests back-to-back. (Arrival-rate scenarios encode pacing in the rate itself.)
- **Error handling in the script**: under load the system WILL return errors; the script must handle them (check status before dependent requests) instead of crashing and distorting the run.
- **Realistic environment and data volume**: an empty database and a laptop-sized instance don't extrapolate. State explicitly how far the test environment is from production and what that limits.

## Generator discipline

Same generator location/spec for every comparable run (a generator moved closer to the target "improves" latency by lying). For internal APIs, generate from inside the network. Monitor the generator like a suspect: its saturation is the first alternative explanation for any weird result.
