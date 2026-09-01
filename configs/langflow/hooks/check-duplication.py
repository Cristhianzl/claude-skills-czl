#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

SOURCE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".go", ".rs",
    ".java", ".kt", ".rb", ".php", ".cs", ".swift", ".c", ".cc", ".cpp",
    ".h", ".hpp", ".vue", ".svelte", ".scala", ".ex", ".exs",
}
TEST_MARKERS = ("test_", "_test.", ".test.", ".spec.", "_spec.", "conftest")
GENERIC_NAMES = {
    "setup", "index", "render", "config", "build", "start", "close",
    "execute", "process", "handle", "parse", "apply", "reset", "clear",
    "props", "state", "value", "error", "result", "constructor",
}

DEF_PATTERNS = [
    re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w{4,})\s*\(", re.M),
    re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([$A-Za-z_]\w{4,})\b", re.M),
    re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([$A-Za-z_]\w{4,})\s*\(", re.M),
    re.compile(r"^\s*(?:export\s+)?const\s+([$A-Za-z_]\w{4,})\s*=\s*(?:async\s*)?(?:\(|function\b)", re.M),
    re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?fn\s+([a-z_]\w{4,})\s*[(<]", re.M),
    re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w{4,})\s*\(", re.M),
]

MAX_NAMES = 15
MAX_REPORTED = 4


def is_test_file(path: str) -> bool:
    base = Path(path).name.lower()
    return any(m in base for m in TEST_MARKERS)


def new_content_from(data: dict) -> str:
    tool_input = data.get("tool_input") or {}
    if data.get("tool_name") == "Write":
        return tool_input.get("content") or ""
    if data.get("tool_name") == "Edit":
        return tool_input.get("new_string") or ""
    if data.get("tool_name") == "MultiEdit":
        return "\n".join((e.get("new_string") or "") for e in tool_input.get("edits") or [])
    return ""


def defined_names(content: str) -> List[str]:
    names: List[str] = []
    for pattern in DEF_PATTERNS:
        for name in pattern.findall(content):
            lowered = name.lower().lstrip("_$")
            if lowered in GENERIC_NAMES or lowered.startswith("test"):
                continue
            if name not in names:
                names.append(name)
    return names[:MAX_NAMES]


def existing_definition(name: str, rel_path: str, cwd: str) -> Optional[str]:
    escaped = re.escape(name)
    pattern = (
        f"(def|fn|func)[[:space:]]+{escaped}[[:space:]]*[(<]"
        f"|function[[:space:]]+{escaped}[[:space:]]*\\("
        f"|class[[:space:]]+{escaped}([^A-Za-z0-9_]|$)"
        f"|const[[:space:]]+{escaped}[[:space:]]*="
    )
    try:
        result = subprocess.run(
            ["git", "grep", "-nIE", pattern, "--", ".", f":!{rel_path}"],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )
    except Exception:
        return None
    for line in result.stdout.splitlines():
        location = line.split(":", 2)
        if len(location) < 2:
            continue
        hit_path = location[0]
        if is_test_file(hit_path) or Path(hit_path).suffix.lower() not in SOURCE_EXTS:
            continue
        return f"{hit_path}:{location[1]}"
    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = (data.get("tool_input") or {}).get("file_path") or ""
    cwd = data.get("cwd") or os.getcwd()
    if not file_path or Path(file_path).suffix.lower() not in SOURCE_EXTS:
        sys.exit(0)
    if is_test_file(file_path):
        sys.exit(0)

    try:
        rel_path = os.path.relpath(file_path, cwd)
    except ValueError:
        sys.exit(0)
    if rel_path.startswith(".."):
        sys.exit(0)

    content = new_content_from(data)
    if not content:
        sys.exit(0)

    findings: List[str] = []
    for name in defined_names(content):
        location = existing_definition(name, rel_path, cwd)
        if location:
            findings.append(f"  - `{name}` already defined at {location}")
        if len(findings) >= MAX_REPORTED:
            break

    if not findings:
        sys.exit(0)

    print("Possible duplication — these symbols already exist in the codebase:", file=sys.stderr)
    print("\n".join(findings), file=sys.stderr)
    print(
        "Read the existing definition first. Reuse or extend it, or state briefly why a "
        "separate one is needed (rung 2 of the reuse ladder). Do not leave two copies of the same logic.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
