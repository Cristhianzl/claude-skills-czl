#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

KNOWN_AI_SDKS = ("openai", "anthropic", "google", "cohere", "mistral", "chromadb", "pinecone", "qdrant_client", "weaviate", "litellm", "langchain_openai", "langchain_anthropic", "langchain_community")

API_KEY_MESSAGETEXTINPUT_RE = re.compile(
    r"""MessageTextInput\s*\(\s*[^)]*\bname\s*=\s*["'](api[_-]?key|secret[_-]?key|token|password|access[_-]?token)["']""",
    re.IGNORECASE | re.DOTALL,
)
TOP_LEVEL_ASSIGN_RE = re.compile(
    r"^(?P<var>[a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?P<rhs>[a-zA-Z_][a-zA-Z0-9_\.]*)\s*\(",
)
PY_DOCSTRING_DELIM = re.compile(r'^\s*("""|\'\'\')')
PHASE_RE = re.compile(r"^\s*(#|\"\"\"|''')?\s*Phase:\s*(EXPAND|MIGRATE|CONTRACT)\b", re.IGNORECASE | re.MULTILINE)


def in_components_dir(path: Path) -> bool:
    return "components" in path.parts and path.suffix == ".py"


def in_alembic_versions(path: Path) -> bool:
    return "alembic" in path.parts and "versions" in path.parts and path.suffix == ".py"


def in_test_dir(path: Path) -> bool:
    return any(p in {"tests", "test", "__tests__"} for p in path.parts)


def check_api_key_input(content: str, path: Path) -> list[tuple[int, str]]:
    hits = []
    for match in API_KEY_MESSAGETEXTINPUT_RE.finditer(content):
        line_no = content.count("\n", 0, match.start()) + 1
        hits.append((line_no, match.group(0)[:120]))
    return hits


def check_top_level_sdk_init(content: str, path: Path) -> list[tuple[int, str]]:
    hits = []
    in_docstring = False
    indent_of_class = None
    for lineno, raw in enumerate(content.splitlines(), start=1):
        if PY_DOCSTRING_DELIM.match(raw) and raw.count('"""') == 1 and raw.count("'''") == 0:
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if not raw or raw.startswith((" ", "\t", "#")):
            continue
        m = TOP_LEVEL_ASSIGN_RE.match(raw)
        if not m:
            continue
        rhs = m.group("rhs").lower()
        if any(rhs.startswith(sdk + ".") or rhs == sdk for sdk in KNOWN_AI_SDKS):
            hits.append((lineno, raw.strip()[:120]))
    return hits


def check_alembic_phase(content: str, path: Path) -> list[tuple[int, str]]:
    if PHASE_RE.search(content):
        return []
    return [(1, f"Migration {path.name} has no 'Phase: EXPAND|MIGRATE|CONTRACT' marker in the docstring/comments.")]


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("tool_name") not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path")
    if not file_path:
        sys.exit(0)

    path = Path(file_path)
    if not path.exists() or in_test_dir(path):
        sys.exit(0)

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        sys.exit(0)

    issues: list[str] = []

    if in_components_dir(path):
        for ln, snippet in check_api_key_input(content, path):
            issues.append(f"  - {path}:{ln} [api-key-as-text] {snippet}\n    → API keys must use SecretStrInput, not MessageTextInput (encrypted at rest, masked in UI).")
        for ln, snippet in check_top_level_sdk_init(content, path):
            issues.append(f"  - {path}:{ln} [top-level-sdk] {snippet}\n    → SDK instantiation at module top-level is forbidden in components. Move inside the output method (lazy import + lazy init).")

    if in_alembic_versions(path):
        for ln, msg in check_alembic_phase(content, path):
            issues.append(f"  - {path}:{ln} [alembic-phase] {msg}\n    → Add a docstring line: 'Phase: EXPAND' or 'Phase: MIGRATE' or 'Phase: CONTRACT'.")

    if issues:
        print("Langflow rule violation:", file=sys.stderr)
        for issue in issues:
            print(issue, file=sys.stderr)
        print("\nSee .claude/skills/building-langflow-components/ and .claude/skills/reviewing-code/learnings/langflow-review-blockers.md.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
