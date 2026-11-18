# Client security

What code running on the user's side must do — a browser page, a webview, a mobile app, a desktop app, a CLI that talks to your API. The client is hostile territory: everything shipped to it can be read and changed by the user, by another program on the device, or by injected code. The client protects the user's session and the data on screen; it never protects the server — that is `server.md`.

The first section applies to every client. The later sections apply when the client renders web content (a browser, an embedded webview, an Electron-style shell) or runs on a mobile/desktop OS.

## Every client

**Everything shipped is public.** Bundles, binaries, config files, environment values baked in at build time, and source maps can all be extracted. No secret keys (payment, email, LLM, database service roles, signing keys) ever ship in a client; the client calls your server, which holds them. Build-time variables meant for the client are public by definition — in web toolchains that is every variable with a public prefix (`NEXT_PUBLIC_`, `VITE_`, `PUBLIC_`, `REACT_APP_`, `EXPO_PUBLIC_`, or your toolchain's equivalent). Publishable keys meant for clients are restricted by the provider to your app/origin and the minimum scope.

**Client validation is UX.** It gives fast feedback; an attacker bypasses it by calling the API directly. Every rule enforced in a form is enforced again on the server. Don't validate with block-lists (rejecting `<script>`): they miss event handlers, `javascript:` URLs, SVG, and encodings, and they reject legitimate input. Cap input length before running any regex, and avoid nested quantifiers like `(a+)+` on untrusted input — catastrophic backtracking is exponential (observed: about 2.6 s for 28 characters with a backtracking engine).

**Client authorization is cosmetic.** Hiding a button, guarding a route, or checking a role locally decides what to *show*, not what is *allowed*. Every action is re-authorized by the server for the specific object. Never send data the user may not see and hide it in the UI; never derive a role from a value the client can edit (a decoded token claim, local storage, a query parameter) for anything beyond display.

**Credentials never sit in readable storage.** Browser web storage (`localStorage`, `sessionStorage`, IndexedDB), plain preference files, and unencrypted app databases are readable by injected scripts or other code on the device. Browser session credentials belong in `HttpOnly` cookies or behind a backend-for-frontend (`browser-boundary.md`); native apps use the OS credential store (Keychain, Keystore, or the platform equivalent). "Encrypting" a value with a key that ships in the same client protects nothing, and Base64 is encoding, not encryption. Store only what the UI needs, and clear user data on logout.

**Transport is verified.** All traffic uses TLS, and certificate validation is never disabled — not in production, not "temporarily", not behind a debug flag that can ship.

**Links, redirects, and deep links are untrusted input.** A `next`/`returnTo` parameter, an app deep link, or a custom URL scheme is followed only to destinations you allow. "Starts with `/`" is not that check: the WHATWG URL parser resolves both `//evil.com` and `/\evil.com` to `evil.com`, and Chromium and Firefox followed a `Location: /\evil.com` redirect off-site (observed; WebKit percent-encoded the backslash). Resolve the value against your own origin with a real URL parser and require the resolved origin to be yours (or map the parameter to a fixed allow-list of named destinations); reject any explicit scheme. The server applies the same rule when it issues a redirect.

**Requests the client builds stay inside its intent.** Never take the target or body of a state-changing request from URL parameters or deep-link input — your own code would attach the user's credentials and CSRF token to an attacker-chosen action. URL input may drive read-only filters and navigation. Build URLs with the platform's URL/query builder, never by concatenating raw values. Send credentials only to your own API.

**Third-party client code runs with your privileges.** Every analytics, chat, A/B, ads, or crash-reporting SDK or script can read what your app can read. Minimize them, keep them off authentication, payment, and account-settings screens, and pin versions (`supply-chain.md`).

**Security UX.** Show active sessions and devices with "sign out everywhere"; notify on new-device logins and on password, email, or MFA changes (to the old address too); require re-authentication or step-up MFA before changing email, password, payout details, or deleting the account; never reveal whether an account exists (`server.md` → user enumeration).

## Clients that render web content (browsers, webviews, web-based desktop shells)

### XSS — data rendered as code

One successful payload rides the victim's session: it reads the page, calls the API as the user (cookies attach automatically), and rewrites what the user sees. `HttpOnly` stops it from *stealing* the session cookie, not from *using* the session.

| Kind | Where the payload lives | Who can stop it |
|---|---|---|
| Stored | Database, served to every viewer | Output encoding at render; sanitizing at render for rich content |
| Reflected | A request parameter echoed into the response | Output encoding wherever the response is built |
| DOM-based | A client-side source (`location.hash`, `postMessage`, web storage, `document.referrer`) written to a sink | Only the client — a URL fragment never reaches the server, so server filters and WAFs never see it |

- Render untrusted values as **text**: the template engine's default escaping, or `textContent` in the DOM. That covers almost every case.
- **Raw-markup sinks** are a short, explicit list per stack, and untrusted data never reaches them unsanitized. In the DOM: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`, string arguments to `setTimeout`/`setInterval`. Every UI framework and template engine has its own raw-output escape hatch (for example `dangerouslySetInnerHTML`, `v-html`, `{@html}`, `bypassSecurityTrust*`, `|safe`, `html_safe`, `{!! !!}`, `Html.Raw`) — know your stack's, and treat every use as a review item.
- **Rich content** (users author HTML or Markdown) is the one case for sanitizing. Markdown renderers are not sanitizers (observed: `marked` passes `<img onerror>` and `javascript:` links straight through). Render to HTML, then run a maintained allow-list sanitizer (DOMPurify in JavaScript, or your platform's vetted equivalent) **immediately before insertion**, even if the server already sanitized — stored rows may be legacy, imported, or written before a fix. Configure allowed tags, attributes, and URI schemes; never write your own sanitizer; keep it updated.
- **URLs are a sink.** Escaping text doesn't validate URL semantics. Frameworks differ and change between versions (observed: Vue 3.5 renders `href="javascript:alert(1)"` unchanged; React 19 replaces it with a URL that throws). Parse every user-supplied URL and allow only the schemes you intend (`https:`, plus `http:`/`mailto:` where wanted) before it reaches `href`, `src`, `action`, or `formaction`.
- **Server state inlined into a page** must be serialized with an encoder that escapes `<`, `>`, `&`, U+2028, and U+2029 — plain JSON serialization leaves `</script>` intact and lets a value break out of the script block (observed with `JSON.stringify`).
- A strict CSP and Trusted Types (`browser-boundary.md`) turn most escaping mistakes into blocked, reported events. They are containment, not a substitute.

### Windows, frames, and messages

- Links that open a new window to an untrusted destination carry `rel="noopener noreferrer"`. Current browsers already imply `noopener` for `target="_blank"` (observed in Chromium, Firefox, and WebKit), but `noreferrer` also stops leaking the current URL.
- **Cross-window messages** (`postMessage` and its equivalents in webview bridges): send with an exact target origin, never a wildcard when the message carries data. On receipt, compare the sender's origin with an exact allow-list (string equality — not `includes` or `endsWith`), then validate the payload against a schema. Message data never reaches a sink.
- **Embedding third-party content:** sandbox it with the minimum capabilities. Never combine script execution with same-origin privileges for content served from your own origin — the framed document can read the parent and remove its own sandbox (observed in all three engines). Restrict what may be framed with CSP `frame-src`.
- **Being embedded (clickjacking)** is controlled by the server's `frame-ancestors` header (`browser-boundary.md`); script-based frame-busting is bypassable.
- **Webview bridges** that expose native functions to JavaScript are reachable by any script the webview loads — expose them only to your own content, never to arbitrary URLs.

### Language-runtime traps

- **Prototype pollution (JavaScript runtimes):** a recursive merge of parsed JSON into a plain object can set `Object.prototype` properties app-wide when the payload carries a `__proto__` key (observed with a hand-rolled merge; current lodash `merge` skips the key — fixed across 4.17.5–4.17.19). Validate input with a schema that drops unknown keys, use maps or null-prototype objects for user-keyed dictionaries, and use merge utilities that skip `__proto__`, `constructor`, and `prototype`. Freezing `Object.prototype` breaks libraries and is not the fix.
- Other dynamic languages have their equivalents (mass attribute binding, magic methods on deserialization) — see `server.md`.

### Third-party scripts and offline storage in the browser

- Every script tag runs with your origin's full privileges, and so does anything it loads; payment-page skimming has come from a single modified third-party script. Self-host and pin libraries; when loading a fixed version from a CDN, add Subresource Integrity (`integrity` + `crossorigin`). SRI can't protect a vendor tag that changes in place — keep those off sensitive pages, isolate them in a sandboxed frame, and allow them in CSP by nonce, never by broad host. Pages that take card data fall under PCI DSS 4.0 requirements 6.4.3 (authorize and inventory every payment-page script and assure its integrity) and 11.6.1 (detect unauthorized changes), mandatory since 31 March 2025.
- Service workers register over HTTPS with the narrowest scope; authenticated or personalized responses are not kept in offline caches unless cleared on logout, and sensitive responses carry `Cache-Control: no-store`.
- Don't serve production source maps publicly unless it's a deliberate choice; upload them privately to the error tracker.

## Native mobile and desktop clients

Grounded in OWASP MASVS v2.1 and its weakness catalog (MASWE); the same principles apply to desktop apps.

- Treat the package as readable: "anyone who downloads the package can recover" hardcoded API keys and secrets (MASWE-0004). Business rules the server doesn't re-check are just as exposed.
- Store sensitive data securely (MASVS-STORAGE-1): keys and tokens in the platform keystore (Android Keystore, iOS Keychain, or the desktop OS credential store), not in preferences, plain files, or logs.
- Handle inter-process messages and deep links as untrusted input (MASVS-PLATFORM-1): custom URL schemes can be claimed by any app, so prefer verified App Links/Universal Links, and validate the incoming URL and parameters before acting. Never perform a state-changing action from a link without the user confirming it.
- Use WebViews securely (MASVS-PLATFORM-2): load only your own content, and expose native bridges only to it.
- Log in through the system browser, never an embedded webview: RFC 8252 requires that "only external user-agents like the browser are used for OAuth by native apps", with Authorization Code + PKCE.
- Validate certificates for all traffic (MASWE-0027: disabling or bypassing validation, or ignoring hostname verification, breaks TLS's guarantees), and pin the identity of endpoints you control (MASVS-NETWORK-2), with a rotation plan for pinned keys.
