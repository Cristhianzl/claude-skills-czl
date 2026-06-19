---
trigger: Any cross-platform decision in /Users/criszl/Documents/langflow — Windows, macOS, Linux, Docker, ARM, desktop.
---

# Langflow project context

**Context:** Langflow ships on multiple targets: PyPI (Python 3.10-3.13), Docker (linux/amd64 + linux/arm64), and a separate **Langflow Desktop** distribution for Windows and macOS. The CI matrix actively tests Ubuntu, macOS (Intel + Apple Silicon), and Windows for installation from PyPI AND from source wheels.

**Lesson:** Treat `AGENTS.md` at the repo root as canonical. The cross-platform reality of Langflow is documented in `.github/workflows/cross-platform-test.yml` — read it before assuming the matrix.

**Why:** The generic SKILL.md describes the defensive default (Linux + macOS + Windows + Docker). Langflow actually meets this in CI, but with specific tooling choices that change how you write portable code.

**Apply when:** Always, on any task involving filesystem, paths, encoding, subprocess, networking, or installation.

## Langflow's actual matrix

| Target                        | Matrix lane                                                                            |
|-------------------------------|----------------------------------------------------------------------------------------|
| Linux x86_64                  | `ubuntu-latest` (Ubuntu 22.04+)                                                        |
| macOS Intel x86_64            | `macos-13`                                                                              |
| macOS Apple Silicon arm64     | `macos-14` / `macos-latest`                                                            |
| Windows x86_64                | `windows-latest` (native, NOT WSL)                                                     |
| Docker linux/amd64            | Built by `.github/workflows/docker-build-v2.yml` (newer; the older v1 is deprecated)   |
| Docker linux/arm64            | Same workflow, multi-arch via `docker buildx`                                          |
| Desktop Windows               | Separate distribution; built outside this repo                                          |
| Desktop macOS                 | Separate distribution; built outside this repo                                          |

**WSL is not a substitute** for native Windows — Langflow tests `windows-latest` directly.

## Conventions to apply on top of the generic SKILL.md

- **Paths:** `pathlib.Path` always. Never `os.path.join` with string concatenation; never literal `/` or `\`.
- **Subprocess:** `subprocess.run([sys.executable, ...])`, never `shell=True`. The CI matrix catches `python3` (Windows uses `python` or `py`).
- **Temp / config:** `tempfile.TemporaryDirectory()` and `platformdirs.user_*_dir(...)`. Never `/tmp` or `~/.config` literals.
- **Encoding:** `open(..., encoding="utf-8")` always.
- **Line endings:** `.gitattributes` enforces `* text=auto eol=lf` (CRLF only for `.bat`, `.cmd`, `.ps1`).
- **Docker:** Use the v2 workflow. The v1 (`docker-build.yml`) is deprecated; new code should not depend on it.
- **Desktop**: do not assume desktop-specific code paths in core Langflow. The desktop app is a wrapper; core must work without it.

## Common Langflow-specific platform traps

- **A test that hardcodes `/tmp/langflow_test_*`** — passes on Linux/macOS, fails on Windows. Use `tmp_path` fixture.
- **A migration script that uses `os.fork()`** — passes everywhere except Windows.
- **A test that asserts filename equality after `os.listdir`** — fails on case-insensitive macOS volumes. Normalize with `.resolve()` before compare.
- **A frontend test that depends on a backend started in the same process** — Windows handles process spawning differently. Use Playwright with explicit server start.
- **A bundle with native deps (CUDA, Rust)** — must be a bundle, not in base. Document arch-specific install in `BUNDLE_API.md`.

## Cross-references

- `ensuring-cross-platform/references/patterns.md` — concrete code for paths, encoding, subprocess. Applies as-is.
- `ensuring-cross-platform/references/docker.md` — `.dockerignore` baseline. Langflow has its own `.dockerignore` — verify it before suggesting changes.
- `ensuring-cross-platform/references/platform-specific-code.md` — the Protocol + factory pattern. Apply when wrapping OS-specific APIs.
