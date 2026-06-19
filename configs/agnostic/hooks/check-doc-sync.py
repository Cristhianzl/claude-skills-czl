#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

DOC_EXTS = {".md", ".mdx", ".rst", ".adoc"}
DOC_NAME_HINTS = ("readme", "changelog", "contributing", "architecture")
DOC_DIRS = {"docs", "documentation", "doc"}
NOISE = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "uv.lock", "poetry.lock", "Cargo.lock", "go.sum", "composer.lock", "Gemfile.lock"}
GENERIC = {"src", "app", "lib", "pkg", "index", "main", "mod", "init", "__init__", "utils", "util", "types", "type", "test", "tests", "spec", "api", "core", "common", "base", "components", "component", "helpers", "models", "services"}
DOC_PATHSPECS = ("*.md", "*.mdx", "*.rst", "*.adoc", "*README*", "*CHANGELOG*")
MAX_READ = 256 * 1024
MAX_DOCS = 4000
MAX_LIST = 25


def is_doc(rel: str) -> bool:
    p = Path(rel)
    if {x.lower() for x in p.parts} & DOC_DIRS:
        return True
    if p.suffix.lower() in DOC_EXTS:
        return True
    return any(h in p.name.lower() for h in DOC_NAME_HINTS)


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


def tokens_for(code: list[str]) -> tuple[set[str], set[str]]:
    names, codedirs = set(), set()
    for rel in code:
        p = Path(rel)
        codedirs.add(p.parent.as_posix())
        names.add(rel.lower())
        for tok in (p.name, p.stem, p.parent.name):
            t = tok.lower()
            if len(t) >= 4 and t not in GENERIC:
                names.add(t)
    return names, codedirs


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
    if not changed:
        sys.exit(0)
    code = [p for p in changed if not is_doc(p) and Path(p).name not in NOISE]
    docs_touched = {p for p in changed if is_doc(p)}
    if not code:
        sys.exit(0)

    repo = Path(cwd)
    names, codedirs = tokens_for(code)
    related = []
    for rel in all_doc_files(cwd):
        if rel in docs_touched:
            continue
        if Path(rel).parent.as_posix() in codedirs:
            related.append(rel)
            continue
        try:
            text = (repo / rel).read_text(encoding="utf-8", errors="ignore")[:MAX_READ].lower()
        except Exception:
            continue
        if any(tok in text for tok in names):
            related.append(rel)

    if not related:
        sys.exit(0)

    lines = ["Doc-sync check: code changed but related documentation was not updated.", "", "Changed (non-doc) files:"]
    lines += [f"  - {p}" for p in code[:MAX_LIST]]
    lines += ["", "Docs across the repo that reference (or sit beside) what you changed — review and update any now inaccurate:"]
    lines += [f"  - {p}" for p in related[:MAX_LIST]]
    if len(related) > MAX_LIST:
        lines.append(f"  ... and {len(related) - MAX_LIST} more")
    lines += ["", "Update the docs that drifted (for feature docs, follow the documenting-features skill). If none need changing, say so explicitly, then stop."]
    print("\n".join(lines), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
