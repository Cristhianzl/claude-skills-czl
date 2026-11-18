# Supply chain — dependencies, builds, and CI

Your software runs every line of every dependency with full privileges, and your pipeline runs with your deploy credentials. This applies to every ecosystem; the tool names below are examples.

Two reminders of the cost: at Equifax (2017), attackers were scanning for a just-disclosed Apache Struts flaw within days and began extracting data about two months later from a server that was still unpatched (GAO-18-559). In September 2025 a phished maintainer published malicious versions of widely used npm packages, taken down within hours of the public report, and a self-replicating worm ("Shai-Hulud") compromised more than 500 packages (CISA).

## Adding a dependency

- First ask whether the platform, the standard library, or an existing dependency already does it (`developing-features` reuse ladder). Every new package is attack surface.
- Check the package before installing: exact name (typosquatting), maintainers and their history, recent ownership transfers, release cadence, open advisories, and whether it runs install-time scripts.
- Prefer packages that publish provenance or signatures (npm provenance, Sigstore, SLSA attestations, or your registry's equivalent).

## Installing reproducibly

- Commit the lockfile and install in CI with the lockfile-enforcing command of your package manager (for example `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable`, `uv sync --locked`, `poetry install --sync`, `pip install --require-hashes`, `bundle install --frozen`, `go mod verify`, `cargo build --locked`).
- Block install-time scripts by default where the tooling allows it, and allow-list the few packages that need them. Examples: npm `ignore-scripts=true`; pnpm 10+ doesn't run dependency build scripts unless allow-listed (`onlyBuiltDependencies` in v10, `allowBuilds` from v11).
- **Dependency confusion:** internal packages live under a namespace you own, resolved only from your private registry (per-scope registry mapping, or your ecosystem's equivalent), and the namespace is claimed on the public registry so nobody else can publish into it.
- Delay adoption of brand-new releases so compromised versions are pulled before you install them: Renovate `minimumReleaseAge`, Dependabot `cooldown` (3 days by default), pnpm `minimumReleaseAge` (1 day by default in current versions).

## Staying patched

- Automated update PRs (Dependabot, Renovate, or equivalent) and an audit step in CI (for example `npm audit`, `pip-audit`, `osv-scanner`, `bundler-audit`, `govulncheck`); fail the build on reachable high/critical advisories.
- Upgrade one dependency per change; prefer security patches over major upgrades; read the changelog.
- Scan container images and keep base images current; generate an SBOM for what you ship.

## CI/CD

- Pin third-party actions/plugins/orbs to a full commit SHA or immutable digest, not a mutable tag.
- Give pipeline tokens the minimum permissions explicitly (in GitHub Actions, a top-level `permissions:` block defaulting to `contents: read`); grant write scopes per job.
- Never run untrusted contributor code with secrets: in GitHub Actions, avoid `pull_request_target` combined with checking out the PR head, and don't expose secrets to fork PRs.
- Deploy to cloud providers with OIDC federation instead of long-lived access keys; scope each role to one deployment.
- Protect the release path: required reviews on the default branch, protected environments with approval for production, signed tags and artifacts where supported.

## Third-party code loaded at runtime

Scripts and SDKs loaded at runtime bypass the lockfile entirely — see `client.md` for SRI, CSP, and isolation.
