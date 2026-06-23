#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

DOC_EXTS = {".md", ".mdx", ".rst", ".adoc"}
DOC_NAME_HINTS = ("readme", "changelog", "contributing", "architecture")
DOC_DIRS = {"docs", "documentation", "doc"}
SOURCE_EXTS = {
    ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs",
    ".java", ".kt", ".cs", ".rb", ".swift", ".php", ".scala", ".c", ".cc",
    ".cpp", ".h", ".hpp", ".m", ".mm", ".vue", ".svelte", ".sql",
}
GENERIC = {
    "src", "app", "lib", "pkg", "index", "main", "mod", "init", "__init__",
    "utils", "util", "types", "type", "test", "tests", "spec", "api", "core",
    "common", "base", "components", "component", "helpers", "helper", "models",
    "model", "services", "service", "handler", "handlers", "routes", "router",
    "controller", "controllers", "schema", "schemas", "config", "client",
    "server", "module", "shared", "constants", "demo", "example", "draft",
}
DOC_PATHSPECS = ("*.md", "*.mdx", "*.rst", "*.adoc", "*README*", "*CHANGELOG*")
MAX_READ = 256 * 1024
MAX_DOCS = 4000
MAX_LIST = 20


def is_doc(rel: str) -> bool:
    p = Path(rel)
    if {x.lower() for x in p.parts} & DOC_DIRS:
        return True
    if p.suffix.lower() in DOC_EXTS:
        return True
    return any(h in p.name.lower() for h in DOC_NAME_HINTS)


def is_source(rel: str) -> bool:
    return Path(rel).suffix.lower() in SOURCE_EXTS


def git(cwd: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)


def changed_paths(cwd: str) -> list[str]:
    paths = []
    for line in git(cwd, "status", "--porcelain").stdout.splitlines():
        rel = line[3:].strip().strip('"')
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1].strip().strip('"')
        if rel and not rel.endswith("/"):
            paths.append(rel)
    return paths


def all_doc_files(cwd: str) -> list[str]:
    res = git(cwd, "ls-files", "-z", "--", *DOC_PATHSPECS)
    return [p for p in res.stdout.split("\0") if p][:MAX_DOCS]


def topic_from(source: list[str]) -> tuple[set[str], set[str]]:
    paths, names, dirs = set(), set(), set()
    for rel in source:
        p = Path(rel)
        paths.add(rel.lower())
        parent = p.parent.as_posix()
        if parent not in ("", "."):
            dirs.add(parent)
        t = p.stem.lower()
        if len(t) >= 5 and t not in GENERIC:
            names.add(t)
    return paths | names, dirs


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if data.get("stop_hook_active"):
        sys.exit(0)

    cwd = data.get("cwd") or "."
    if git(cwd, "rev-parse", "--is-inside-work-tree").returncode != 0:
        sys.exit(0)

    changed = changed_paths(cwd)
    source = [p for p in changed if is_source(p)]
    docs_touched = {p for p in changed if is_doc(p)}
    if not source:
        sys.exit(0)

    repo = Path(cwd)
    tokens, source_dirs = topic_from(source)
    related = []
    for rel in all_doc_files(cwd):
        if rel in docs_touched:
            continue
        if Path(rel).parent.as_posix() in source_dirs:
            related.append(rel)
            continue
        try:
            text = (repo / rel).read_text(encoding="utf-8", errors="ignore")[:MAX_READ].lower()
        except Exception:
            continue
        if any(tok in text for tok in tokens):
            related.append(rel)

    header = (
        "Doc-sync check: you changed source code — review the docs related to it."
        if related
        else "Wrap-up check: you changed source code this turn."
    )
    lines = [header, "", "Source files changed:"]
    lines += [f"  - {p}" for p in source[:MAX_LIST]]
    if len(source) > MAX_LIST:
        lines.append(f"  ... and {len(source) - MAX_LIST} more")
    if related:
        lines += ["", "Docs that reference (or sit beside) what you changed — update any now inaccurate:"]
        lines += [f"  - {p}" for p in related[:MAX_LIST]]
        if len(related) > MAX_LIST:
            lines.append(f"  ... and {len(related) - MAX_LIST} more (match looks broad — focus on the ones tied to this change)")
        lines += ["", "Update the docs that drifted (for feature docs, follow the documenting-features skill). If none apply to this change, say so explicitly."]
    lines += [
        "",
        "Then suggest a commit message scoped to the changes YOU made this turn — the list above is the",
        "whole working-tree delta, so exclude files you did not touch (pre-existing or unrelated edits).",
        "Conventional Commits format (`type: imperative subject`, subject <= 50 chars, English; add a body",
        "only if it explains why). A suggestion only; the human runs git — never run git add/commit/push.",
    ]
    print("\n".join(lines), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
