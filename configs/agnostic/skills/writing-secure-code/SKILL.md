---
name: writing-secure-code
description: Write client-side and server-side code that is secure by construction, in any language, framework, or architecture — safe rendering of untrusted data, credentials and sessions, CSRF/CORS/CSP and security headers, injection-proof data access, authentication, passwords, tokens, object- and function-level authorization, SSRF, uploads and parsers, secrets, crypto, logging, and supply chain. Use whenever the code being written or changed touches user input, rendering of untrusted data, login/session/token handling, cookies, CORS, CSP or security headers, permissions or ownership checks, building queries/commands/templates, outbound requests to user-supplied URLs, uploads, secrets, password storage, or a new dependency — even if the user never says "security". Triggers: "secure this", "is this safe", XSS, CSRF, CORS, CSP, JWT, session, cookie, auth, login, password, IDOR, BOLA, SSRF, injection, upload, sanitize. For an audit of existing code use security-review; for design-time analysis use threat-modeling; for reviewing a diff use reviewing-code.
license: MIT
---

# Writing secure code

Build-time security for both sides of a system and the boundary between them. **Language-, framework-, and architecture-agnostic:** every rule is a principle that holds for any stack — monolith, microservices, or serverless; server-rendered pages, SPAs, mobile, or desktop clients. A named library or framework is only an example of "your stack's equivalent", or a behavior that was observed in a test and labeled with its version (`references/sources.md` → Empirical verification).

This skill is the single source of truth for **how to write it**: `security-review` audits what already exists, `threat-modeling` decides what to protect before building, and `reviewing-code` checks a diff against the same rules.

## Read first (always)

List `learnings/` and read every file relevant to the stack and the change. Stack-specific conventions — the project's framework, auth provider, CDN, cookie domain, database — belong there and override the defaults here; mention the conflict to the user.

Then open only the references the change touches:

| The change touches… | Read |
|---|---|
| Any client: what ships to users' devices, rendering untrusted data, links and redirects, local storage of credentials, embedded content, third-party client code | `references/client.md` |
| HTTP between a browser and a server: cookies, sessions, CSRF, CORS, CSP, security headers, OAuth in browser apps, transport | `references/browser-boundary.md` |
| Any server, service, or function: input validation, queries and commands, authentication, passwords, tokens, authorization, SSRF, files and parsers, secrets, crypto, errors, logs, abuse limits, service-to-service calls | `references/server.md` |
| Dependencies, lockfiles, CI/CD, build and release | `references/supply-chain.md` |
| Where a rule came from, which popular advice was rejected, and what was tested | `references/sources.md` |

## The five invariants

Every rule in the references applies one of these. When a case isn't covered, reason from them.

1. **Data never becomes code.** User data is never concatenated into anything another interpreter parses — a query language, a query object, a shell, a template, markup, a URL, a header, a log line, an LLM prompt. Use the API that keeps structure and data apart (bound parameters, argument arrays, text-only rendering, URL builders). Values that can't be bound, like identifiers, are picked from an allow-list.
2. **The server decides.** Identity comes from the verified session or token, never from the request body. Authorization runs server-side on every request, at the point of data access, deny-by-default. Prices, totals, roles, and ownership are computed server-side. Anything a client enforces is UX — and in a multi-service system, every service enforces it again instead of trusting the caller.
3. **Validate early, encode late, sanitize only rich content.** Validate shape at the boundary with an allow-list schema and reject what doesn't fit. Store the raw value. Encode for the exact output context at the last moment. Sanitize markup only when users author markup, right before it is rendered.
4. **Secrets stay server-side, short-lived, and out of reach of client code.** Nothing shipped to a device — bundle, binary, config — holds a secret. Session credentials live where client scripts can't read them. Every credential can be rotated, and a leaked one is rotated, not just deleted.
5. **Fail closed, and tell an attacker nothing useful.** An erroring check denies. Clients get a generic error with a stable code; details go to server logs, without secrets or personal data. A missing header or an unknown field is a reason to reject, not to guess.

## Workflow

1. **Name the trust boundaries the change crosses** — client→server, service→service, server→database, server→OS, server→third party, one user's content→another user's screen. Each crossing is where an invariant applies.
   → verify: you can list every value in the change that an attacker controls.
2. **Pick the rule from the reference** for each crossing, and implement it from the authoritative source (OWASP cheat sheet, the framework's or provider's official docs) rather than a tutorial or memory. When a rule depends on how a specific library or browser behaves, **check it** — write a small script or test against the version the project uses instead of assuming.
   → verify: no rule in the change rests on "I think this is how it works".
3. **Write the abuse test alongside the happy-path test.** User A requests user B's object and gets 404; `' OR '1'='1` is stored literally; an `<img onerror>` payload renders as text; a cross-site POST without a token is rejected; a URL resolving to `169.254.169.254` is refused.
   → verify: each control in the change has a test that fails if the control is removed.
4. **Run the scope audit** (`guarding-scope`): fix security defects in the lines you're changing; report the ones elsewhere instead of rewriting neighbours.

## Defaults when the project hasn't decided

These are architecture choices; take them unless the project's constraints say otherwise, and record a deviation in `learnings/`.

- **Browser sessions:** a server-side session referenced by a `__Host-` cookie (`Secure; HttpOnly; SameSite=Lax; Path=/`). Self-contained tokens (JWT) only when stateless verification is a real requirement.
- **Browser apps using OAuth/OIDC:** a backend-for-frontend holds the tokens and the browser holds only a session cookie; when the browser must hold tokens, Authorization Code + PKCE, never the implicit grant.
- **Native and desktop apps:** tokens in the OS credential store; system browser for login with Authorization Code + PKCE.
- **Passwords:** a managed identity provider, or Argon2id (m=19 MiB, t=2, p=1). Passkeys/WebAuthn offered; TOTP as fallback; SMS last.
- **Service-to-service:** every call is authenticated (mTLS or signed short-lived tokens) and authorized; the internal network is not a trust boundary.
- **Browser hardening:** a strict nonce-based CSP, HSTS, `nosniff`, `frame-ancestors`, `Referrer-Policy`, `Permissions-Policy`, set once in middleware or at the edge.
- **CSRF:** the framework's token-based protection, or Fetch Metadata with a mandatory `Origin` fallback; `SameSite` as defense in depth, never the only control.

## Output

Code plus the tests that prove the controls. When a control needs a rollout (CSP, rate limits, cookie changes, database row-level policies), say so and follow `security-review/references/safe-remediation.md` — report-only first, staging before production.

## Capture a learning

A project-specific trap — a cookie domain quirk, a proxy that strips headers, an auth provider's claim format, a library default that differs from these references — goes in `learnings/YYYY-MM-DD-slug.md` (or `/learn`).

## See also

- `skills/security-review` — audit existing code (OWASP Top 10 2025) with a safe-remediation protocol.
- `skills/threat-modeling` — STRIDE and abuse cases before building.
- `skills/reviewing-code` → `references/web-security-checks.md` (the same rules as diff checks) and `references/pr-pentest.md` (minimal dynamic probes for a PR).
- `skills/api-design` → `references/security.md` — the API-surface floor (BOLA, BFLA, mass assignment, rate limits).
- `skills/developing-features` → `references/security.md` — AI/LLM guardrails and third-party webhook verification; `references/untrusted-content.md` — prompt injection.
- `skills/building-frontend-ui` — the UI layer this skill secures.
