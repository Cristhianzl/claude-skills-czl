# Server security

What any server-side code must do — a monolith, a microservice, a serverless function, a worker, a gateway — in any language. The server is the last line of defense: treat every request as coming from a capable attacker with a raw HTTP client, not from your own UI. Users send malformed input, requests don't only come from your client, parameters get modified, IDs get guessed. Most server vulnerabilities are data crossing a trust boundary without validation or access control.

Library names below are examples of "your stack's equivalent". Behavior marked *observed* was tested with the version named (`sources.md` → Empirical verification); re-check it for the version your project uses.

## Validate at the boundary

- Parse every request into a typed structure with a schema validator **before** handler logic: types, formats, enums, ranges, **maximum lengths and sizes**, maximum collection lengths. Reject what doesn't fit (`400`/`422`); don't coerce silently.
- Allow-list, don't block-list. Reject or drop unknown fields where they could matter (mass assignment, below).
- Canonicalize before validating (decode, normalize Unicode, resolve paths), then validate the canonical form.
- Validation is correctness, not the injection defense — a valid email can still carry a payload. Keeping structure and data apart is the defense; validation narrows what reaches it.

## Injection — keep structure and data apart

Every interpreter the server talks to has a grammar. User data that reaches it as text becomes code.

- **Query languages (SQL and others):** bound parameters, always — the driver's placeholders (`?`, `$1`, `:name`, `%s`, `@p`), never string building. Observed: a string-built `WHERE email = '…'` returned every row for `' OR '1'='1`; the bound version returned none. ORMs and query builders parameterize by default, but their raw-query escape hatches don't. Identifiers (table, column, sort direction) can't be bound — map them from an allow-list.
- **Query objects (document databases):** the attack is controlling the *structure*, not just the value — observed: a filter built from a request body matched a user for `{"password": {"$ne": null}}`. Verify that each field is a scalar of the expected type, never pass a request object into a query, and disable server-side script operators.
- **OS commands:** don't invoke a shell. Use the process API that takes an argument array. Arrays still allow **argument injection** — observed: a user value `--output=<path>` passed to `git log` wrote a file; placing `--` before it neutralized it. End options with `--`, validate the value, and prefer server-generated filenames.
- **Templates:** user input is a variable passed to a template, never part of the template source (server-side template injection).
- **Headers and logs:** strip CR/LF from anything placed in an HTTP or email header; log with structured fields so input can't forge log lines.
- **Spreadsheet exports:** prefix cells starting with `=`, `+`, `-`, `@`, tab, or carriage return so spreadsheets don't evaluate them.
- **Directory and XML-path query languages:** escape per interpreter.
- **Graph query APIs (GraphQL and similar):** limit query depth and amount (by default "both be unlimited which may lead to a DoS"), apply cost analysis, limit how many operations can be batched (batching turns one request into a fast brute force), and disable introspection and schema explorers in production (OWASP GraphQL Cheat Sheet).
- **Least-privilege database identity:** the application's database user has data-manipulation rights only (no schema changes, no superuser), so a successful injection can't drop tables or read other schemas.

## Authentication

- Prefer a managed identity provider or a battle-tested library over hand-rolled auth; follow the OWASP Authentication and Password Storage cheat sheets, not a tutorial.
- **Password hashing (OWASP minimums):** Argon2id with m=19 MiB, t=2, p=1; or scrypt N=2^17, r=8, p=1; or bcrypt with work factor ≥ 10; or PBKDF2-HMAC-SHA256 with 600,000 iterations where FIPS applies. Never MD5, SHA-1, or SHA-256/512 for passwords — fast general-purpose hashes fall to GPU cracking even when salted — and never reversible encryption. Good libraries generate and embed the salt and parameters in the hash string (observed with an Argon2id library). bcrypt reads at most 72 bytes: some libraries silently ignore the rest, newer ones reject longer input (observed) — enforce a 72-byte maximum. An optional pepper is stored separately from the password database. Re-hash on the next successful login when parameters change; never bulk-migrate.
- **Password policy (NIST SP 800-63B-4, July 2025):** at least 15 characters when the password is the only factor, at least 8 when it is part of MFA; permit at least 64; compare against a blocklist of common and compromised passwords; no composition rules; no periodic forced changes — but force a change on evidence of compromise.
- **MFA:** passkeys/WebAuthn first, TOTP next, SMS last (SIM swap, interception). Push approval uses number matching to resist MFA fatigue. Administrators require MFA.
- **No user enumeration:** login, signup, and password reset return the same response and comparable timing whether or not the account exists.
- **Password reset:** CSPRNG token, single use, short expiry (≤ 1 hour), stored hashed, sent only to the verified address; on success, invalidate the token and every existing session.
- **Brute force — layer the limits:** per IP (catches simple scripts, misfires behind NAT), per account (defeats IP rotation), and a global failed-login rate (catches password spraying across many accounts). Respond with progressive delays and CAPTCHA, not a hard lockout an attacker can use to lock real users out; alert on spikes.
- **Account linking:** link an external identity to an existing account only through a verified email, never an unverified claim.

## Sessions and tokens

- **Prefer server-side sessions** when you need revocation, device lists, or "sign out everywhere" — almost always. Identifiers carry at least 64 bits of entropy (OWASP minimum); generate 128 bits with a CSPRNG. Browser cookie, fixation, and timeout rules: `browser-boundary.md`.
- **Self-contained tokens (JWT and similar), when stateless verification is a real requirement:**
  - Pin the accepted algorithm(s) at verification; reject `none` and algorithm confusion. Library defaults vary — observed: a current Node JWT library already rejected both — so pin explicitly anyway.
  - Verify, never just decode: decoding returns attacker-chosen claims without checking anything (observed).
  - Validate `exp`, `nbf`, `iss`, and `aud` on every request.
  - Asymmetric signing (ES256, EdDSA, RS256) when verifiers aren't the issuer, with key rotation via `kid` and a key set endpoint; a shared-secret algorithm only when one service both signs and verifies, with a ≥ 256-bit random secret from the secret store.
  - Short-lived access tokens (5–15 minutes). Refresh tokens are stored hashed server-side, rotated on every use, and a reused refresh token revokes the whole token family.
  - The payload is readable by anyone: no personal data, no secrets, no permissions the server doesn't re-check.
  - Missing or invalid credential → `401`; valid credential without permission → `403` (or `404`, below).

## Authorization — the most common breach class

Authentication says who is calling. Authorization decides, for **this** object and **this** operation, whether they may. Broken access control is #1 in the OWASP Top 10 2025 (A01).

- **Identity from the session, never the request.** User, tenant, and role come from the verified session or token. An ID in the body or query is input, not identity.
- **Object level (BOLA/IDOR):** scope every query — reads **and** writes — by owner or tenant at the data-access layer, in the same statement:

  ```sql
  UPDATE invoices SET status = :status WHERE id = :id AND tenant_id = :tenant_from_session
  ```

  No row → `404`, not `403`: a `403` after fetching confirms the object exists and enables enumeration. Unguessable IDs are defense in depth only; the scoped query is the control.
- **Function level (BFLA):** privileged operations check role or permission in addition to authentication. An unlisted URL is not protection — routes leak through client code, logs, and traffic.
- **Deny by default.** A new endpoint or handler is protected until explicitly opened. Centralize the policy (one authorization module or policy engine, plus a data-layer guard) rather than scattering role checks.
- **Database row-level policies,** where the database offers them: enabled on every user-data table with explicit policies, and no privileged function or view quietly bypassing them.
- **Mass assignment:** bind requests to an explicit input model of writable fields. A profile update never accepts `role`, `is_admin`, `tenant_id`, `balance`, or `email_verified`.
- **Excessive data exposure:** responses go through an explicit output model — never serialize the persistence entity. No password hashes, internal flags, or other users' fields.
- **Server-side business values:** recompute prices, discounts, totals, quotas, and eligibility on the server; the client's numbers are display only.
- **Race conditions:** balance changes, coupon redemption, stock decrements, and "one per user" rules use a transaction with row locks, a conditional update, or a unique constraint — not read-then-write.
- **Test it in CI:** user A requests user B's object (expect 404); a member calls an admin operation (expect 403); an anonymous caller hits an authenticated route (expect 401). Log every denied authorization as a security event — denials are how probing shows up.

## Service-to-service and distributed systems

Grounded in the OWASP Microservices Security Cheat Sheet.

- "Each service must enforce access to its protected operations, including internal calls." Being inside the network is not a credential: services authenticate each other (mTLS, or signed short-lived tokens the callee validates), and authentication never replaces service-level authorization.
- Propagate the end user's context "in a form each receiving service can validate" — a signed token, not a plain `X-User-Id` header any caller can set. A valid signature proves integrity, not permission; each service still decides whether that user may perform that operation.
- Gateways and edge functions add controls (rate limits, authentication, WAF), but "gateway checks complement these controls; they do not establish that a downstream operation is authorized."
- Queue and event consumers validate messages like any other untrusted input; a producer can be compromised or buggy.
- Serverless functions and workers get their own least-privilege identity, not a shared broad role.

## SSRF — the server fetching a URL someone else chose

Any feature that fetches a user-influenced URL — webhooks, link previews, image import, "import from URL", document renderers, identity-provider discovery — can be aimed at internal services or the cloud metadata endpoint. (Capital One, 2019: a misconfigured WAF was abused — widely described as SSRF — to reach EC2 instance metadata and obtain role credentials.) SSRF is CWE-918, mapped to OWASP 2025 A01.

- Allow-list schemes (`https`) and, where possible, destination hosts.
- Resolve the hostname, validate **every resolved IP** against private, loopback, link-local, and reserved ranges — `10/8`, `172.16/12`, `192.168/16`, `127/8`, `169.254/16`, `0.0.0.0/8`, `::1`, `fc00::/7`, `fe80::/10`, the AWS IPv6 metadata address `fd00:ec2::254` — after normalizing IPv4-mapped IPv6 addresses. Observed: the WHATWG URL parser rewrites `[::ffff:127.0.0.1]` as `[::ffff:7f00:1]` and `2130706433`, `0x7f.1`, and `127.1` as `127.0.0.1`, so a validator that only recognizes the dotted form misses them — a plausible-looking fix in the test bed for `pr-pentest.md` let `[::ffff:127.0.0.1]` through until the mapped form was decoded; Python 3.9's address helpers don't flag `::ffff:169.254.169.254` as link-local unless you unwrap the mapped IPv4 (3.12+ do); and a hostname written as a decimal integer (`2852039166`) resolves to `169.254.169.254`, so string checks on the URL's host are useless.
- Connect to the IP you validated, so a second DNS lookup (rebinding) can't swap it.
- Disable redirect following, or re-validate every hop.
- Route outbound fetches through an egress proxy with its own allow-list; set timeouts and a response-size cap.
- On AWS, require IMDSv2 and disable IMDSv1 — defense in depth, not a complete fix — and give the workload identity only the permissions it needs.

## Files, paths, and parsers

- **Uploads:** cap size at the proxy and the app; decide the type from content (magic bytes), not the extension or the client's `Content-Type`; store under a server-generated name outside any executable or web root (object storage is ideal); serve user files with `Content-Disposition: attachment` and `nosniff`, ideally from a separate domain. Re-encode images (drops embedded payloads and location metadata). SVG is XML that can carry script — sanitize it or serve it only as an attachment. Archives: reject entries that resolve outside the target directory (zip slip) and cap the expanded size (decompression bombs). Scan shared files for malware where relevant.
- **Path traversal:** resolve the final path and confirm it is inside the base directory before opening it. Path APIs disagree on absolute segments — observed: Python's `pathlib` join and Node's `path.resolve` let `/etc/passwd` replace the base, while Node's `path.join` appends it — and `../../etc/passwd` escaped the base in every case. A resolve-then-contain check caught all of them.
- **XML:** disable DTDs and external entities. Defaults differ by parser and version — observed: `defusedxml` raised on an external entity, current `lxml` refused it by default, and `lxml` with entity resolution enabled read a local file. Prefer JSON when you control the format.
- **Deserialization:** never use native object deserialization on anything a user could have touched — the OWASP Deserialization Cheat Sheet names, among others, Python `pickle`, Java `ObjectInputStream`, PHP `unserialize()`, and .NET `BinaryFormatter` ("dangerous and cannot be secured", per Microsoft) — observed: an unsafe YAML loader executed a constructor from the document; the safe loader rejected it. Use a data-only format plus schema validation, and sign state that must round-trip through a client.

## Secrets and configuration

- Secrets come from a secret manager, ideally through workload identity or short-lived credentials; environment variables are the fallback (they leak through crash dumps, child processes, and debug pages). Never in code, comments, commit messages, images, or logs.
- A committed secret is compromised for good (version history) — **rotate it**, then remove it. Enable secret scanning with push protection and a pre-commit scanner.
- Debug mode off in production; production log level `info` or higher. No default credentials; admin consoles behind authentication plus role checks and, where possible, network restrictions.
- Least privilege for every identity: no wildcard cloud permissions, scoped CI credentials, processes and containers running as a non-root user.

## Crypto and randomness

- Use vetted high-level libraries, never hand-rolled primitives. Symmetric encryption uses an AEAD (AES-256-GCM or ChaCha20-Poly1305) with a unique nonce per message; never ECB, never unauthenticated CBC.
- Keep keys apart from the data they protect (a KMS with envelope encryption); rotate them.
- Security-relevant randomness comes from the platform CSPRNG, never a general-purpose PRNG (`Math.random`, `rand()`, `random`).
- Compare secrets, tokens, and signatures in constant time.
- The best sensitive data is data you don't store: delegate cards to a payment provider; encrypt the rest at rest; mask it in responses.

## Errors and logging

- Clients get a generic error with a stable machine-readable code (for HTTP APIs, `application/problem+json`); never a stack trace, query, file path, internal hostname, or framework version.
- Log security events: login success and failure, MFA changes, password and email changes, denied authorization, admin actions, token validation failures, rate-limit hits. Use pseudonymous IDs, never email, name, or other personal data; never passwords, tokens, keys, or card data — redact centrally in the logger, not at each call site.
- Keep audit logs centralized, tamper-evident, and retained per policy; alert on thresholds (failed logins, denials, error spikes), don't just record them.

## Availability and abuse

- Rate-limit every public endpoint, stricter on authentication, password reset, signup, and expensive operations (HTTP: `429` + `Retry-After`).
- Cap request bodies, uploads, page sizes, and collection lengths; set timeouts on every outbound call; bound retries.
- Watch for expensive-by-design paths: regexes on untrusted input (ReDoS), password hashing itself (rate-limit login), unbounded graph queries, decompression.
