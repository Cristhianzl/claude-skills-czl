#!/usr/bin/env python3
# Why: scope creep is invisible to the agent that caused it; forcing a file-by-file audit of this turn's diff against the request at Stop is the only check that doesn't rely on the model remembering the rule.
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

MAX_LISTED = 30
AUDIT = (
    "Scope audit (skills/guarding-scope) — before finishing, for EACH file above name the part of "
    "the user's request that requires it. Revert any file or hunk with no answer: reformatting, "
    "renames, drive-by refactors, unrequested tests/docs/helpers/deps/config, edits to existing "
    "assertions. Remove slop you added (WHAT-comments, try/catch on trusted paths, casts, debug "
    "logs, temp files). In the wrap-up, list required extras under 'Beyond the literal request "
    "(required)' and ideas under 'Out of scope — noticed, not done'. Do not print this checklist."
)


def git(cwd: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=True)


def state_dir(cwd: str) -> Optional[Path]:
    git_dir = git(cwd, "rev-parse", "--git-dir").stdout.strip()
    if not git_dir:
        return None
    p = Path(git_dir)
    return p if p.is_absolute() else Path(cwd) / p


def dirty(cwd: str) -> dict[str, str]:
    files: dict[str, str] = {}
    for line in git(cwd, "status", "--porcelain", "--untracked-files=all").stdout.splitlines():
        code, rel = line[:2], line[3:].strip().strip('"')
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1].strip().strip('"')
        if not rel or rel.endswith("/"):
            continue
        try:
            digest = hashlib.sha256((Path(cwd) / rel).read_bytes()).hexdigest()
        except Exception:
            digest = "deleted"
        files[rel] = f"{code}:{digest}"
    return files


def load(path: Path) -> Optional[dict[str, str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save(path: Path, data: dict[str, str]) -> None:
    try:
        path.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


def describe(cwd: str, rel: str, code: str) -> str:
    if "?" in code or "A" in code:
        return f"  new      {rel}"
    if "D" in code:
        return f"  deleted  {rel}"
    stat = git(cwd, "diff", "--numstat", "HEAD", "--", rel).stdout.split()
    delta = f" (+{stat[0]} -{stat[1]})" if len(stat) >= 2 else ""
    return f"  modified {rel}{delta}"


def snapshot(data: dict) -> None:
    cwd = data.get("cwd") or "."
    base = state_dir(cwd)
    if base is not None:
        save(base / "claude-scope-baseline", dirty(cwd))


def audit(data: dict) -> None:
    if data.get("stop_hook_active"):
        return
    cwd = data.get("cwd") or "."
    base = state_dir(cwd)
    if base is None:
        return
    now = dirty(cwd)
    fingerprint = hashlib.sha256(json.dumps(now, sort_keys=True).encode("utf-8")).hexdigest()
    last = base / "claude-scope-last-audit"
    try:
        if last.read_text(encoding="utf-8").strip() == fingerprint:
            return
    except Exception:
        pass
    baseline = load(base / "claude-scope-baseline") or {}
    turn = {rel: v for rel, v in now.items() if baseline.get(rel) != v}
    try:
        last.write_text(fingerprint, encoding="utf-8")
    except Exception:
        pass
    if not turn:
        return
    rels = sorted(turn)
    lines = [f"This turn changed {len(rels)} file(s):"]
    lines += [describe(cwd, rel, turn[rel].split(":", 1)[0]) for rel in rels[:MAX_LISTED]]
    if len(rels) > MAX_LISTED:
        lines.append(f"  ... and {len(rels) - MAX_LISTED} more — a diff this wide needs explicit user approval.")
    lines.append(AUDIT)
    print(json.dumps({"decision": "block", "reason": "\n".join(lines), "suppressOutput": True}))


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    cwd = data.get("cwd") or "."
    if git(cwd, "rev-parse", "--is-inside-work-tree").returncode != 0:
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "snapshot":
        snapshot(data)
    else:
        audit(data)
    sys.exit(0)


if __name__ == "__main__":
    main()
