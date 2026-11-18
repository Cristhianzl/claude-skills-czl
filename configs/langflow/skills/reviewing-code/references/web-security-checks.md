# Web security checks — client and server

The diff-level security lens for anything that renders data, handles a request, or crosses a client–server or service–service boundary, in any language, framework, or architecture. Examples name common APIs so the pattern is recognizable; look for your stack's equivalent. It complements `security-checks.md` (PII, secrets, AI, webhooks): that file is the always-on floor, this one is what to look for when the diff touches the web stack. Where the config ships the `writing-secure-code` skill, its references carry the full rationale; this file is self-contained so a review-only config can apply it as is. When an environment for the PR can be run, `pr-pentest.md` turns the most common of these checks into safe, dynamic probes.

Triage stays internal (see `SKILL.md`): an exploitable defect introduced or exposed by the diff is a **Blocker**; a missing layer of defense in depth is **Important**; hardening the PR didn't need to touch is a **follow-up**, never a blocker (`scope-checks.md`). Every finding names the attacker, the input they control, and what they get — "an attacker who controls `next` can redirect a logged-in user to any site", not "possible open redirect".

## How to read the diff

1. List the values in the diff an attacker controls: body, query, path params, headers, cookies, uploaded files, URL fragments, `postMessage` data, third-party API responses, database rows another user wrote, LLM output.
2. Follow each one to where it is **used**: a query, a shell, a template, the DOM, a URL, a redirect, an outbound fetch, an authorization decision, a log line.
3. At each use, check the rule below. A value that is validated at entry but concatenated at the sink is still a finding — validation isn't the injection defense.

## Client — what to look for

Applies to browser pages, webviews, and mobile or desktop apps; the rendering items apply wherever web content is rendered.

- **New raw-markup sink with untrusted data** — the stack's raw-output escape hatch (`innerHTML`/`outerHTML`/`insertAdjacentHTML`, `document.write`, `dangerouslySetInnerHTML`, `v-html`, `{@html}`, `bypassSecurityTrust*`, `|safe`, `html_safe`, `{!! !!}`, `Html.Raw`) or dynamic code (`eval`, `new Function`, string timers). Blocker unless the value goes through a maintained sanitizer right before rendering; "the server sanitizes it" is not enough.
- **User-controlled URL in `href`/`src`/`action`/`formaction`** without a scheme allow-list — `javascript:` executes, and frameworks differ (Vue 3.5 renders it unchanged, React 19 neutralizes it). Blocker when the URL comes from another user.
- **Inline state serialized with plain `JSON.stringify`** into a `<script>` during SSR — `</script>` breaks out. Blocker if any value is user-controlled.
- **Secrets or credentials where the client can read them** — tokens in web storage (`localStorage`, `sessionStorage`, IndexedDB) or plain app preferences instead of the OS keystore; a secret key in client code, a shipped config, or behind a public build-time prefix (`NEXT_PUBLIC_`, `VITE_`, `PUBLIC_`, `REACT_APP_`, `EXPO_PUBLIC_`, or the toolchain's equivalent). Blocker.
- **TLS validation weakened** — certificate or hostname verification disabled, a trust-all manager, an insecure flag that can ship. Blocker.
- **Authorization only in the UI** — a new admin view, action, or data field gated by a route guard or hidden button with no matching server check in the diff. Blocker; ask where the server enforces it.
- **`postMessage`** sent with `"*"` while carrying data, or a listener that doesn't compare `event.origin` exactly (string equality) before using `event.data`. Blocker when the data reaches a sink or a state change.
- **Open redirect or unvalidated deep link** — `?next=`/`?returnTo=`/`?redirect=`, a custom URL scheme, or an app link followed without resolving it and requiring your own origin ("starts with `/`" accepts `//evil.com` and `/\evil.com`). Important; Blocker on login and OAuth flows.
- **`<iframe>`** for untrusted content without `sandbox`, or with `allow-scripts allow-same-origin` on same-origin content. Important.
- **State-changing request built from URL parameters** (client-side CSRF). Blocker.
- **Deep merge of untrusted JSON** into plain objects (prototype pollution). Important.
- **New third-party `<script>`** — on login, payment, or account pages: Blocker unless justified; elsewhere: check it's pinned with SRI or nonce-allowed, and named in the PR description.
- **Regex on untrusted input with nested quantifiers** (`(a+)+`, `(.*)*`) and no length cap. Important (ReDoS).

## Browser–server boundary — what to look for

- **Cookie flags weakened or missing** on a session/auth cookie: no `HttpOnly`, no `Secure`, `SameSite=None` without a reason, a new `Domain` widening scope. Blocker.
- **State-changing endpoint reachable by cookie auth without CSRF protection** — no token check, no Fetch Metadata/`Origin` check, or exempted from the framework's CSRF middleware. Blocker. A `GET` that changes state is a Blocker on its own.
- **CORS widened** — `*` with credentials, origin reflected from the request, `null` allowed, a regex/`endsWith` origin match that also accepts `evil-example.com`. Blocker.
- **CSP loosened** — `'unsafe-inline'` or `'unsafe-eval'` added to `script-src`, a broad host or `https:` added, a static nonce, enforcement switched back to report-only without a plan. Blocker for `script-src` loosening; Important otherwise.
- **Security header removed or overridden per route** (HSTS, `nosniff`, `frame-ancestors`/`X-Frame-Options`, `Referrer-Policy`). Important.
- **Session ID not regenerated on login**, logout that only clears the client, password change that leaves other sessions alive. Important; Blocker on an auth rewrite.
- **Tokens in URLs** (query strings, fragments in redirects) — leak via logs, history, and `Referer`. Blocker for session or reset tokens.

## Server — what to look for

Applies to any server-side code: monoliths, services, serverless functions, workers, and gateways.

- **String-built queries** — f-strings, template literals, `+`, `.format`, `%` into SQL; ORM raw calls with interpolation; a sort/column name taken from the request without an allow-list; a request object passed straight into a NoSQL filter. Blocker.
- **Shell** — `shell=True`, `exec`/`system` with a command string, user input in argv without `--` or validation. Blocker.
- **Identity from the request** — `user_id`, `tenant_id`, `role`, `owner_id` read from body/query instead of the session. Blocker.
- **Trusting the caller inside the system** — a service that accepts an unsigned identity header (`X-User-Id`) or skips authorization because the call is "internal"; a gateway check treated as the only authorization. Blocker.
- **Unscoped object access (BOLA/IDOR)** — a read, update, or delete by ID without the owner/tenant condition in the same query; fetch-then-check that returns 403 and reveals existence. Blocker for missing scope; Recommended for 403-vs-404.
- **Missing function-level check (BFLA)** — new admin/privileged route with authentication but no role/permission check, or "protected" by an unlisted path. Blocker.
- **Mass assignment / overexposure** — request body spread into a model (`**body`, `Object.assign(entity, req.body)`, `update(req.body)`) or ORM entity serialized straight to the response. Blocker when a privileged field (`role`, `is_admin`, `tenant_id`, `balance`, `password_hash`) is reachable.
- **Client-trusted business values** — price, total, discount, quota from the request used without recomputation. Blocker.
- **Read-then-write on money, stock, coupons, or quotas** without a transaction/lock/conditional update/unique constraint. Important; Blocker for money.
- **Outbound fetch of a user-supplied URL** (webhook, preview, import, renderer) without scheme/host allow-list, private-range blocking on the resolved IP (including normalized IPv4-mapped forms like `[::ffff:7f00:1]`), and redirect control. Blocker (SSRF).
- **Uploads** — type from extension or client `Content-Type`, user-supplied filename used in a path, stored under the web root, served inline, SVG served as an image from the app origin, archive extraction without a path check. Blocker for path traversal or executable storage; Important otherwise.
- **Path built from input** without resolve-and-contain check. Blocker.
- **Unsafe parsers** — XML without DTD/external entities disabled, `pickle`, `yaml.load`, native deserialization on untrusted data. Blocker.
- **Password handling** — anything but Argon2id/scrypt/bcrypt/PBKDF2 with proper parameters; a fast hash (MD5, SHA-1, SHA-256) for passwords; reversible encryption; bcrypt with unbounded input length. Blocker.
- **JWT** — verify without a pinned algorithm list, missing `exp`/`aud`/`iss` validation, decode used where verify was needed, PII in claims, long-lived access tokens, refresh tokens without rotation. Blocker for verification gaps; Important for lifetimes.
- **Auth flows** — login/reset responses that differ for existing vs unknown accounts; reset tokens that are guessable, reusable, unexpiring, or stored in plain text; removed rate limiting on auth routes. Important; Blocker for token weaknesses.
- **Crypto** — `Math.random`/`random` for tokens or IDs, `==` on secrets, ECB/unauthenticated modes, hard-coded keys or IVs. Blocker.
- **Errors** — stack traces, SQL, or internal paths returned to clients; debug mode or verbose logging enabled for production. Important; Blocker if secrets reach the response.
- **Rate limits and size caps** removed or bypassed for a public or expensive endpoint. Important.

## PR-level changes that need a security read

- **New or upgraded dependency** — is it needed, is the name exact, does it run install scripts, is the lockfile updated in the same PR? A lockfile change with no manifest change deserves a question.
- **CI workflow change** — third-party action not pinned to a SHA, broader `permissions:`, `pull_request_target` with a checkout of the PR head, secrets exposed to forks. Blocker for the last two.
- **Migration touching permissions** — RLS disabled or a policy widened, `SECURITY DEFINER` added, grants broadened. Blocker unless the PR explains it.
- **A security test deleted, skipped, or weakened**, or a control's test missing for a new endpoint (no "user A can't read user B" test). Blocker per `scope-checks.md`.

## Grep starters

Run against the changed files, then read each hit in context — a hit is a lead, not a finding. The patterns cover common JavaScript/TypeScript and Python spellings; add your stack's equivalents.

```bash
git diff --name-only origin/main...HEAD | xargs grep -nE 'dangerouslySetInnerHTML|v-html|\{@html|innerHTML|outerHTML|insertAdjacentHTML|document\.write|bypassSecurityTrust|new Function|eval\('
git diff --name-only origin/main...HEAD | xargs grep -nE '(local|session)Storage\.setItem|NEXT_PUBLIC_|VITE_|REACT_APP_|EXPO_PUBLIC_'
git diff --name-only origin/main...HEAD | xargs grep -nE 'postMessage\(|addEventListener\(.message|[?&](next|returnTo|redirect|url)='
git diff --name-only origin/main...HEAD | xargs grep -nE 'Access-Control-Allow-Origin|cors\(|allow_origins|unsafe-inline|unsafe-eval|SameSite|httpOnly|HttpOnly|csrf'
git diff --name-only origin/main...HEAD | xargs grep -nE 'execute\(f|\$queryRawUnsafe|\.raw\(|text\(f|shell=True|child_process|os\.system|subprocess'
git diff --name-only origin/main...HEAD | xargs grep -nE 'req\.body\.(user_?id|role|tenant)|body\[.(user_id|role)|\*\*(body|data|payload)\b|Object\.assign\([^,]+, *req\.body'
git diff --name-only origin/main...HEAD | xargs grep -nE 'requests\.(get|post)\(|fetch\(|axios\.|httpx\.|urlopen\('
git diff --name-only origin/main...HEAD | xargs grep -nE 'pickle\.loads?|yaml\.load\(|XMLParser|etree\.parse|Math\.random|md5|sha1\(|jwt\.decode|algorithms'
```
