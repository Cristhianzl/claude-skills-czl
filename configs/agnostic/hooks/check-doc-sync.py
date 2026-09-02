#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

DOC_EXTS = {".md", ".mdx", ".rst", ".adoc"}
DOC_NAME_HINTS = ("readme", "changelog", "contributing", "architecture")
DOC_DIRS = {"docs", "documentation", "doc"}
SOURCE_EXTS = {
    ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".rs",
    ".java", ".kt", ".cs", ".rb", ".swift", ".php", ".scala", ".c", ".cc",
    ".cpp", ".h", ".hpp", ".m", ".mm", ".vue", ".svelte", ".sql",
}
DOC_PATHSPECS = ("*.md", "*.mdx", "*.rst", "*.adoc", "*README*", "*CHANGELOG*")
MAX_READ = 256 * 1024
MAX_DOCS = 4000
COMMIT_LINE = (
    "End with ONE commit suggestion for this turn's changes — a single `type: subject` line "
    "(<= 50 chars, English), no alternatives, no character counting. You never run git."
)
DOC_LINE = (
    "Update only the docs this change made inaccurate and name just those; "
    "say nothing about docs that are still correct."
)


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
    tokens, dirs = set(), set()
    for rel in source:
        p = Path(rel)
        tokens.add(rel.lower())
        if len(p.name) >= 5:
            tokens.add(p.name.lower())
        parent = p.parent.as_posix()
        if parent not in ("", "."):
            dirs.add(parent)
    return tokens, dirs


def state_path(cwd: str) -> Optional[Path]:
    git_dir = git(cwd, "rev-parse", "--git-dir").stdout.strip()
    if not git_dir:
        return None
    p = Path(git_dir)
    if not p.is_absolute():
        p = Path(cwd) / p
    return p / "claude-doc-sync-state"


def tree_fingerprint(cwd: str) -> str:
    status = git(cwd, "status", "--porcelain").stdout
    stat = git(cwd, "diff", "--stat", "HEAD").stdout
    untracked = []
    for line in status.splitlines():
        if line.startswith("??"):
            rel = line[3:].strip().strip('"')
            try:
                meta = (Path(cwd) / rel).stat()
                untracked.append(f"{rel}:{meta.st_size}:{meta.st_mtime_ns}")
            except Exception:
                continue
    payload = "\n".join([status, stat, *untracked])
    return hashlib.sha256(payload.encode("utf-8", "replace")).hexdigest()


def tree_changed_since_last_stop(cwd: str) -> bool:
    fingerprint = tree_fingerprint(cwd)
    path = state_path(cwd)
    if path is None:
        return True
    try:
        if path.read_text(encoding="utf-8").strip() == fingerprint:
            return False
    except Exception:
        pass
    try:
        path.write_text(fingerprint, encoding="utf-8")
    except Exception:
        pass
    return True


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

    if not tree_changed_since_last_stop(cwd):
        sys.exit(0)

    changed = changed_paths(cwd)
    source = [p for p in changed if is_source(p)]
    if not source:
        sys.exit(0)
    docs_touched = {p for p in changed if is_doc(p)}

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

    if related:
        list_path = state_path(cwd)
        doc_list_file = None
        if list_path is not None:
            doc_list_file = list_path.with_name("claude-doc-sync-docs")
            try:
                doc_list_file.write_text("\n".join(related) + "\n", encoding="utf-8")
            except Exception:
                doc_list_file = None
        if doc_list_file is not None:
            lines = [
                f"Doc-sync: {len(related)} doc(s) may reference this turn's change — read the list in "
                f"{doc_list_file} (do not print it). {DOC_LINE}",
                COMMIT_LINE,
            ]
        else:
            lines = [
                f"Doc-sync: check docs related to this turn's changed files. {DOC_LINE}",
                COMMIT_LINE,
            ]
    else:
        lines = [COMMIT_LINE]
    print(json.dumps({
        "decision": "block",
        "reason": "\n".join(lines),
        "suppressOutput": True,
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
