# Sources, verification, and rejected advice

This skill was distilled from popular articles and talks, then checked two ways: every factual claim against a primary source, and every behavior claim with a test. Where a source was wrong or dated, the rule follows the authority, and the rejected advice is listed so nobody "fixes" the skill back to it.

## Authorities (win every conflict)

- OWASP Top 10 2025 (A01 Broken Access Control … A10 Mishandling of Exceptional Conditions), OWASP API Security Top 10 (2023), and the OWASP Cheat Sheet Series — XSS Prevention, CSRF Prevention, Content Security Policy, HTTP Headers, Session Management, Authentication, Password Storage, Authorization, SSRF Prevention, File Upload, Deserialization, GraphQL, Microservices Security, Logging.
- OWASP MAS — MASVS v2.1 and its weakness catalog (MASWE) for mobile clients; OWASP Web Security Testing Guide (WSTG) for the probes in `reviewing-code/references/pr-pentest.md`.
- The CSP specification (W3C), MDN Web Docs (cookies, CORS, CSP, Trusted Types, Fetch Metadata, browser compatibility data), web.dev (strict CSP).
- NIST SP 800-63B-4 (final, July 2025) — passwords and authenticators.
- IETF RFC 9700 (OAuth 2.0 Security BCP, January 2025), RFC 10017 (OAuth 2.0 for Browser-Based Applications, August 2026), RFC 8252 (OAuth 2.0 for Native Apps).
- PCI DSS 4.0 requirements 6.4.3 and 11.6.1 (mandatory since 31 March 2025).
- hstspreload.org requirements; GAO-18-559 (Equifax); CISA alert of 23 September 2025 (npm worm).

## Empirical verification

Run on macOS (arm64) with Node 24.11, Python 3.9.6 / 3.12.12 / 3.13.9, Playwright 1.65 driving Chromium 159, Firefox 159, and WebKit 27.2, against local servers on real-looking domains over HTTPS where cookies needed it. Re-test when your versions differ — that is the point of recording them.

| Area | What was observed |
|---|---|
| Cookies | `HttpOnly` hidden from `document.cookie`; `__Host-` with `Domain` rejected and a sibling subdomain unable to overwrite a `__Host-` cookie, while it could plant a same-named plain cookie (WebKit sent the planted one first); `SameSite=Lax` sent on cross-site top-level GET, withheld on cross-site POST and subresources; a POST from a sibling subdomain was `same-site` and carried `Lax` cookies — all three engines |
| `SameSite` default | Chromium stored an attribute-less cookie as `Lax` but still sent it on a cross-site top-level POST within two minutes; Firefox and WebKit stored it as `None` and sent it on cross-site form POSTs; Firefox also sent it on a cross-site `text/plain` fetch |
| CORS and CSRF | A cross-site `text/plain` POST executed on the server while the response read was blocked; an `application/json` POST sent only the preflight; `Sec-Fetch-Site: cross-site` and `same-site` sent by all three engines; Node `cors` with `origin: true` reflected any origin including `null` with credentials; an anchored `/example\.com$/` pattern accepted `evil-example.com` |
| CSP | With `'nonce-…' 'strict-dynamic'`: nonced script and its dynamically created script ran; injected inline script, injected same-origin `<script src>` without nonce, and inline handler blocked; `frame-ancestors` ignored in `<meta>`, enforced as a header — all three engines |
| Trusted Types | `innerHTML = string` threw under `require-trusted-types-for 'script'` in Chromium, Firefox, and WebKit |
| Frames and windows | Sandboxed frame with `allow-scripts` only couldn't touch the parent; adding `allow-same-origin` let same-origin content read the parent and remove its own `sandbox` attribute; `target="_blank"` opened with `window.opener === null` — all three engines |
| Redirects | WHATWG URL resolved `//evil.com` and `/\evil.com` to `evil.com`; Chromium and Firefox followed `Location: /\evil.example` off-site; WebKit percent-encoded the backslash |
| Rendering | DOMPurify removed `onerror` and `javascript:` hrefs; `marked` passed both through; `JSON.stringify` left `</script>` intact while `serialize-javascript` escaped it; Vue 3.5 SSR emitted `href="javascript:…"` unchanged; React 19.3 SSR replaced it with a throwing URL |
| JavaScript runtime | Hand-rolled deep merge polluted `Object.prototype`; lodash 4.18 `merge` didn't; `/^(a+)+$/` took ~2.6 s on 28 characters |
| Tokens | `jsonwebtoken` 9 rejected `alg: none` and an HS256-with-public-key forgery (with and without pinning); `jwt.decode` returned forged claims |
| Injection | String-built SQL returned all rows for `' OR '1'='1`, bound parameters none (SQLite); `{"$ne": null}` matched a user in a document-store filter (mongomock); `git log --output=<file>` passed as an argv element wrote a file, `--` stopped it |
| Parsers and files | `defusedxml` refused an external entity; `lxml` 6.1 refused it by default and read `/etc/hosts` with `resolve_entities=True`; PyYAML's unsafe loader executed `!!python/object/apply`, `safe_load` refused; Python `pathlib` and Node `path.resolve` let an absolute segment replace the base, Node `path.join` didn't, `../..` escaped in all |
| Passwords | Python `bcrypt` 5.0 rejected input over 72 bytes; `argon2-cffi` accepted m=19456, t=2, p=1 and embedded them in the hash |
| SSRF | Python 3.9 `ipaddress` didn't flag `::ffff:169.254.169.254` as link-local (3.12/3.13 did); `2852039166` resolved to `169.254.169.254`; WHATWG URL rewrote `[::ffff:127.0.0.1]` to `[::ffff:7f00:1]` and `2130706433`/`0x7f.1`/`127.1` to `127.0.0.1` |
| Review tooling | The 13 `pr-pentest.md` probes each flagged a deliberately vulnerable app and passed its fixed twin (26/26); every grep starter in `web-security-checks.md` compiled under ugrep and BSD grep and matched its sample; the banned-pattern hook blocks raw `dangerouslySetInnerHTML` and tokens in `localStorage`/`sessionStorage`, and allows a value passed through a sanitizer inside `__html` |

## Distilled sources

| Source | Kept |
|---|---|
| Zeeshan Ali, "Frontend Security — Frontend System Design Guide" (dev.to) | Sink list, iframe sandbox rules, `postMessage` origin checks, cookie decision tree, SRI, refresh-token rotation with reuse detection, header checklist |
| Nitin Mangrule, "Mastering Frontend Security, Part II" (Medium) | Nonce-based CSP, CSP reporting, SRI, dependency confusion, payment-page skimming (British Airways), metadata-credential theft (Capital One), patching (Equifax), MFA fatigue and number matching, signed releases |
| Fahri, "Securing the Frontend: A Practical Guide" (Medium) | XSS/CSRF/third-party threat framing; security events surfaced to users |
| Stefano Alvares, "The Backend Engineer's Cheat Sheet to Cybersecurity (2025)" (Medium) | Server as last line of defense, rate-limit auth routes, no root DB user, encrypted backups, least-privilege IAM and CI, secret scanning |
| Mainak Mukherjee, "Backend Security Fundamentals" (dev.to) | Attacker-assumption mindset, SQL/NoSQL/command injection, layered rate limits, BOLA vs BFLA, horizontal vs vertical escalation |
| djeada, Backend-Engineers-Guide — "Security Vulnerabilities" (GitHub) | XXE, insecure deserialization, misconfiguration, known-vulnerable components, security events to log, session invalidation on password change |
| Dmitriy Zhiganov, "Mastering Web Security" (YouTube) | DOM XSS invisible to the server; validate early / escape late / sanitize only rich content; store raw; sanitize at render even after server sanitization; client-side CSRF; CORS doesn't stop CSRF; form posts skip CORS; identifiers need allow-lists; `Origin` checks reject on mismatch, not absence |
| Sriniously, "Backend Security: Everything You Need to Know" (YouTube) | DML-only DB role; NoSQL structure injection; argv arrays; prefer stateful sessions; 404 instead of 403 for unowned objects; scope writes as well as reads; role checks separate from permissions; global failed-login cap; deny by default; authz tests in CI; log denials; rotate committed secrets; production log level |
| YouAccel, "Best Practices for Frontend Security" (YouTube) | HTTPS, CSP, CSRF tokens plus `SameSite`, `HttpOnly` session cookies, SAST/DAST and peer review |
| Fireship, "7 Security risks you should never take as a developer" (YouTube) | Patch known vulnerabilities, rotate and scope leaked keys, stored XSS (Samy worm), SQL injection (Heartland), fine-grained IAM, availability |
| InTruder Security, "Web Development or Cyber Security?" (YouTube) | Career comparison — nothing to extract |
| Cyber with Ben, "Which Cyber Security Job Is Right for You?" (YouTube) | Career paths — only the AppSec role description (secure SDLC, code review, API security) is relevant |
| ClickControl, "What is Backend Security" (YouTube) | Describes endpoint/device protection, not server application security — nothing applicable |

## Rejected advice

| Claim (source) | Why it's rejected | What the skill says instead |
|---|---|---|
| A fixed `'nonce-random123'` in the CSP config (Mangrule) | The spec requires a unique nonce per policy transmission | Fresh CSPRNG nonce per response, or hashes |
| `btoa(JSON.stringify(...))` into `localStorage` as "encryption" (Mangrule) | Base64 is encoding; the token is readable by any script | No credentials in web storage |
| `hmarr/auto-approve-action` as "require approval before deploy" (Mangrule) | It auto-approves PRs — the opposite | Protected environments with required reviewers |
| `--no-optional` / pinning one version to stop dependency confusion (Mangrule) | Doesn't stop resolution from the public registry | Owned namespace resolved only from the private registry, claimed publicly |
| Deny every login from a new location (Mangrule) | Locks out travelling users | Step-up verification and notification |
| Client-side role checks "ensure only authorized users access" (Mangrule, Ali) | The client can be modified | Client checks are cosmetic; the server authorizes every request |
| Host allow-list CSP as the primary XSS defense (Ali, Zhiganov) | Bypassable through allowed hosts; CSP is containment | Output encoding first; strict nonce/hash CSP as containment |
| `X-XSS-Protection` as a protection header | Chrome removed the auditor in version 78; OWASP recommends `0` | Omit it or send `0` |
| Sanitize before storing, as the main XSS fix (Ali, Sriniously, Fireship) | Corrupts data for other contexts; misses legacy and imported rows | Store raw, encode per output context, sanitize rich content at render |
| `SameSite` "not sent on cross-origin requests" (Ali) | It's per site; sibling subdomains are same-site (observed) | Origin vs site spelled out; a primary CSRF defense |
| "Browsers default to `SameSite=Lax`, so CSRF is minor" (Sriniously) | Only Chromium defaults to Lax (observed) | Explicit `SameSite` plus a primary CSRF defense |
| CORS as a CSRF defense (Sriniously, Mangrule) | Simple requests execute (observed) | CORS governs reading responses only |
| JWT in `localStorage` to "avoid CSRF" (Zhiganov) | Trades CSRF for token theft by any XSS | `HttpOnly` cookie or BFF, plus CSRF defense |
| 24 h account lockout after 5 failures (Sriniously, Mukherjee) | Lets anyone lock out any user | Progressive delays, CAPTCHA, alerting |
| UUIDs as the IDOR fix (Sriniously) | Obscurity; IDs leak | Scoped queries are the control |
| "Using an ORM keeps you safe from injection" (Fireship) | Raw-query escape hatches aren't parameterized | Bound parameters everywhere |
| Blocking input "surrounded by script tags" (Fireship, Zhiganov) | Block-lists miss handlers, `javascript:`, SVG, encodings | Allow-list validation plus contextual encoding |
| `jwt.verify` without an algorithm list; `403` for an invalid token (Mangrule) | Safety then depends on library defaults; wrong status | Pin algorithms, validate claims; invalid credential is `401` |
| `csurf` middleware for Express (Alvares) | Archived and deprecated (May 2025; last release 2020) | The framework's maintained CSRF protection or a Fetch Metadata check |
| Logging the user's email on failed logins (djeada) | Personal data in logs | Pseudonymous IDs only |
| "Encrypt sensitive data before storing it client-side" (YouAccel) | The key ships with the code | Keep it server-side, or in the OS keystore on native apps |
| `Object.freeze(Object.prototype)` as the prototype-pollution fix (Ali) | Breaks libraries; misses the cause | Schema validation, maps/null-prototype objects, safe merges |
| JavaScript frame-busting as a clickjacking fallback (Ali) | Bypassable | `frame-ancestors` plus `X-Frame-Options` |
| Argon2 at 500–1000 ms; SMS as a strong second factor (Zhiganov) | Excessive per-login cost; SIM swap | OWASP parameters; passkeys/TOTP before SMS |
| `report-uri` alone for CSP reporting | Deprecated | `report-to` + `Reporting-Endpoints`, with `report-uri` kept until Firefox 149+ is your floor |
| Preflight `max-age: 86400` (Ali, Zhiganov) | Chromium caps at 7200 s | Expect the cap |
| "SSRF was merged into Broken Access Control" (common summary of OWASP 2025) | SSRF is a CWE (918) mapped to A01, not a merged category | Stated as a mapping |
