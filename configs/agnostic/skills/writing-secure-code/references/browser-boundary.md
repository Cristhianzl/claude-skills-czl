# The browser–server boundary

Cookies, browser sessions, CSRF, CORS, CSP, and security headers. These are HTTP and browser semantics, so they are the same whatever language or framework produces the response: the server sets them, the browser enforces them, and most mistakes come from misunderstanding which side does what. Statements marked *observed* were tested in Chromium 159, Firefox 159, and WebKit 27.2 (`sources.md`).

## Same-origin vs same-site

- **Origin** = scheme + host + port. `https://app.example.com` and `https://api.example.com` are different origins. The Same-Origin Policy and CORS work on origins.
- **Site** = scheme + registrable domain. `app.example.com` and `evil.example.com` are the **same site**. `SameSite` cookies work on sites: a POST from a sibling subdomain is `same-site` and carries `SameSite=Lax` cookies (observed in all three engines). A compromised or user-content subdomain is inside your `SameSite` boundary.

## Cookies

The default for a session or auth cookie:

```http
Set-Cookie: __Host-session=<128-bit random value>; Secure; HttpOnly; SameSite=Lax; Path=/
```

- `HttpOnly` — invisible to `document.cookie` (observed), so an injected script can't exfiltrate it; it can still act within the page.
- `Secure` — sent only over HTTPS.
- `SameSite=Lax` — sent on top-level cross-site navigations (a user following a link to you), withheld on cross-site POSTs and cross-site subresource requests (observed). `Strict` withholds it even on a link click from another site. `None` is only for genuine cross-site embedding and requires `Secure` plus a CSRF defense.
- `__Host-` prefix — the browser rejects the cookie unless it is `Secure`, has `Path=/`, and has **no** `Domain` (observed on real domains in all three engines). A sibling subdomain can plant a same-named plain cookie that the browser then sends alongside yours — WebKit even sends the planted one first — but it cannot plant a `__Host-` cookie (observed). Use `__Secure-` only when a `Domain` is genuinely needed.
- Always set `SameSite` explicitly. Only Chromium treats a cookie without the attribute as `Lax`, and even then sends it on a top-level cross-site POST for its first two minutes; Firefox and WebKit store it as `None` and send it on cross-site form POSTs, and Firefox also sent it on a script-initiated cross-site `text/plain` POST (observed).
- No `Domain` unless subdomains must share the cookie; nothing sensitive in a non-`HttpOnly` cookie.

## Sessions and tokens in the browser

| Option | Verdict |
|---|---|
| Server-side session referenced by an `HttpOnly` cookie | **Default.** Revocable, invisible to scripts. Needs a CSRF defense. |
| Backend-for-frontend holding OAuth tokens; browser holds only a session cookie | **Default for browser apps using OAuth/OIDC** — RFC 10017 lists it first and strongly recommends it for business, sensitive, and personal-data apps. |
| Access token in memory + refresh token in an `HttpOnly`, path-scoped cookie | Acceptable without a BFF. Access tokens short-lived (5–15 min); refresh rotation with reuse detection (`server.md`). |
| Any token in `localStorage`/`sessionStorage`/IndexedDB | **Never.** Readable by any script on the origin. |

- Regenerate the session identifier on login and on every privilege change (session fixation).
- Expire sessions on an idle timeout and an absolute timeout; invalidate server-side on logout, on password change, and on "sign out everywhere".
- OAuth/OIDC in the browser: Authorization Code with PKCE and exact redirect-URI matching; validate `state` and, for OIDC, `nonce`. Browser clients must not use the implicit grant (RFC 10017), and the resource-owner password grant must not be used at all (RFC 9700).

## CSRF

A page on another site makes the victim's browser send a state-changing request to you, and the browser attaches your cookies. It applies to **every cookie-authenticated, state-changing endpoint**. A pure bearer-token API (token sent explicitly in a header, never in a cookie) is not exposed.

**Pick one primary defense per app** (OWASP CSRF Prevention Cheat Sheet) and apply it to every state-changing request:

- **Token-based** — the synchronizer token pattern for stateful apps (a CSPRNG token tied to the session, sent in a hidden field or a custom header, compared in constant time), or the **signed** double-submit cookie for stateless apps (an HMAC of the token bound to the session). Naive, unsigned double-submit is discouraged: anyone who can write cookies on your domain bypasses it, and a sibling subdomain can (observed above).
- **Fetch Metadata** — for apps targeting only modern browsers: reject state-changing requests whose `Sec-Fetch-Site` is `cross-site` (and `same-site` unless you trust every sibling subdomain). All three engines send it (observed). An `Origin` (fallback `Referer`) check against an exact allow-list is a **mandatory** fallback when the header is absent; reject on mismatch rather than on absence.
- **Custom request header** — for APIs called only by your own scripts: require a header a cross-site form can't send, which forces a CORS preflight. Any origin your CORS policy allows can still set it, so this is only as strong as that allow-list.

`SameSite` is defense in depth, not a replacement — it doesn't cover sibling subdomains, mutating GETs, or browsers that don't default it.

**Rules every defense depends on:**

- `GET`, `HEAD`, and `OPTIONS` never change state — `Lax` cookies ride top-level GET navigations.
- Endpoints that expect JSON reject `text/plain`, form encodings, and a missing `Content-Type`. Those are "simple" requests: they skip the preflight and execute on the server even when CORS then hides the response (observed in all three engines; Firefox also attached a cookie set without `SameSite`).
- Protect the login form too (login CSRF signs the victim into the attacker's account).
- High-impact actions also require re-authentication or step-up MFA.
- **XSS defeats every CSRF defense** — an injected script reads the token and sends a same-origin request. Fix XSS first.

## CORS

CORS is the server telling the browser which other origins may **read** its responses. It is not access control and not a CSRF defense.

- Only browsers enforce it; non-browser clients ignore it entirely.
- Simple requests are sent and executed even when the response read is blocked; a request that needs a preflight (for example `Content-Type: application/json`) is never sent if the preflight fails (observed). HTML form posts are not subject to CORS at all.
- Allow an explicit list of exact origins. Never reflect the request's `Origin` (observed: the popular Node `cors` middleware with `origin: true` reflects any origin, including `null`, with credentials), never allow `null`, never combine `*` with credentials, and never match origins with suffix checks or unanchored patterns (observed: a `/example\.com$/` pattern accepts `evil-example.com`). Send `Vary: Origin` when the allowed origin is chosen per request.
- List the methods and headers you accept. Browsers cap preflight caching (`Access-Control-Max-Age`): Chromium at 2 hours, Firefox at 24 hours.
- Use your framework's or gateway's CORS support rather than hand-written headers — it's easy to miss a route or the `OPTIONS` handler.
- Putting the app and the API on one site (subdomains of one domain) avoids most CORS and third-party-cookie complexity.

## Content Security Policy

CSP is containment: when an escaping mistake slips through, the browser refuses to run the injected script and reports it. It does not replace output encoding.

**Use a strict, nonce- or hash-based policy, not a host allow-list.** Allow-lists like `script-src 'self' https://cdn.example.com` are bypassable whenever an allowed host serves JSONP endpoints, old library versions, or user uploads.

```http
Content-Security-Policy: script-src 'nonce-{random}' 'strict-dynamic'; object-src 'none'; base-uri 'none'; frame-ancestors 'self'; form-action 'self'; report-uri https://example.com/csp; report-to csp
Reporting-Endpoints: csp="https://example.com/csp"
```

Observed with this policy in all three engines: the nonced script ran, the script it created ran (`'strict-dynamic'`), and an injected inline script, an injected same-origin `<script src>` without the nonce, and an inline event handler were all blocked.

- The nonce is unique for every response (the spec's MUST), unguessable, and at least 128 bits from a CSPRNG (the spec's SHOULD). A static nonce in configuration protects nothing. Pages that can't generate nonces use script hashes instead.
- `object-src 'none'` and `base-uri 'none'` close plugin and `<base>`-tag bypasses; `frame-ancestors` controls who may frame you.
- Never add `'unsafe-inline'` or `'unsafe-eval'` to `script-src`; refactor inline handlers and `javascript:` URLs out.
- Deliver CSP as a response header. A `<meta>` policy ignores `frame-ancestors`, `report-uri`, and `sandbox` (per the spec; observed: a page with `frame-ancestors 'none'` in `<meta>` was still framed, while the same directive in the header blocked it).
- Roll out with `Content-Security-Policy-Report-Only`, watch reports, then enforce. `report-uri` is deprecated in favor of `report-to` + `Reporting-Endpoints`, but Firefox supports `report-to` only from version 149, so send both until your supported browsers all have it.
- **Trusted Types** (`require-trusted-types-for 'script'`) makes DOM sinks reject plain strings, forcing every HTML write through a reviewed policy. Supported in Chromium 83+, Firefox 148+, and Safari 26+ (observed: `innerHTML = string` threw in all three test engines).

## Security headers

Set once — in your framework's security middleware, the gateway, the reverse proxy, or the CDN — so no route can forget them.

| Header | Value | Purpose |
|---|---|---|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains` — add `preload` only after every subdomain serves HTTPS (preload requires max-age ≥ 1 year, `includeSubDomains`, and `preload`) | Forces HTTPS after the first visit; preload covers the first visit too |
| `Content-Security-Policy` | the strict policy above | Script containment, framing, form targets |
| `X-Content-Type-Options` | `nosniff` | Stops content sniffing of uploads and API responses into scripts |
| `Referrer-Policy` | `strict-origin-when-cross-origin` (or `no-referrer`) | Stops leaking paths and query strings to other sites |
| `Permissions-Policy` | for example `camera=(), microphone=(), geolocation=()` | Disables browser features the app doesn't use |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Legacy fallback for `frame-ancestors`; send both |
| `Cross-Origin-Opener-Policy` | `same-origin` (or `same-origin-allow-popups` for OAuth popups) | Severs cross-origin `window.opener` access |
| `Cache-Control` | `no-store` on responses with personal or sensitive data | Keeps them out of browser and shared caches |

- `X-XSS-Protection`: omit it or send `0`. Chrome removed the auditor it controlled in version 78, and OWASP recommends `0`.
- Remove version banners (`X-Powered-By`, detailed `Server`).

## Transport

HTTPS everywhere, including public pages. Redirect HTTP to HTTPS permanently (308 preserves the method; 301 is fine for GET-only routes). TLS 1.2 minimum, 1.3 preferred; certificates from a trusted CA with automated renewal; no mixed content.
