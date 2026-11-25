#!/usr/bin/env python3
# Why: the user's own pull requests are reviewed in the chat only; this guard makes posting on one impossible, whatever the agent decides.
from __future__ import annotations

import json
import re
import subprocess
import sys
from typing import NoReturn

SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\|")
API_TARGET = re.compile(r"(?:^|\s)/?repos/([^/\s]+)/([^/\s]+)/(pulls|issues)/(\d+)/(reviews|comments)(?:/|\s|$)")
PR_CMD = re.compile(r"\bgh\s+pr\s+(review|comment)\b(.*)")
PR_URL = re.compile(r"https://github\.com/([^/\s]+)/([^/\s]+)/pull/(\d+)")
REPO_FLAG = re.compile(r"(?:-R|--repo)[\s=]+([^/\s]+/[^/\s]+)")
EXPLICIT_WRITE = re.compile(r"(?:-X|--method)[\s=]*(POST|PATCH|PUT|DELETE)", re.IGNORECASE)
EXPLICIT_READ = re.compile(r"(?:-X|--method)[\s=]*(GET|HEAD)", re.IGNORECASE)
IMPLICIT_POST = re.compile(r"(?:^|\s)(?:-f|-F|--field|--raw-field|--input)(?:[\s=]|$)")


def gh(args: list[str]) -> str | None:
    try:
        result = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def is_api_write(segment: str) -> bool:
    if EXPLICIT_WRITE.search(segment):
        return True
    return not EXPLICIT_READ.search(segment) and bool(IMPLICIT_POST.search(segment))


def api_target(segment: str) -> tuple[str, str, str, str] | None:
    if "gh api" not in segment or not is_api_write(segment):
        return None
    match = API_TARGET.search(segment)
    return (match.group(1), match.group(2), match.group(3), match.group(4)) if match else None


def pr_cmd_target(segment: str) -> tuple[str | None, str | None] | None:
    match = PR_CMD.search(segment)
    if not match:
        return None
    rest = match.group(2)
    url = PR_URL.search(rest)
    if url:
        return f"{url.group(1)}/{url.group(2)}", url.group(3)
    repo = REPO_FLAG.search(rest)
    number = re.search(r"(?:^|\s)(\d+)(?:\s|$)", rest)
    return (repo.group(1) if repo else None), (number.group(1) if number else None)


def api_target_author(owner: str, repo: str, kind: str, number: str) -> tuple[bool, str | None]:
    if kind == "pulls":
        return True, gh(["api", f"repos/{owner}/{repo}/pulls/{number}", "--jq", ".user.login"])
    info = gh(["api", f"repos/{owner}/{repo}/issues/{number}", "--jq", '"\\(.pull_request != null) \\(.user.login)"'])
    if info is None:
        return True, None
    is_pr, _, login = info.partition(" ")
    return is_pr == "true", login or None


def author_of_pr_cmd(repo: str | None, number: str | None) -> str | None:
    args = ["pr", "view"] + ([number] if number else []) + (["-R", repo] if repo else []) + ["--json", "author", "--jq", ".author.login"]
    return gh(args)


def deny(reason: str) -> NoReturn:
    sys.stderr.write(f"BLOCKED (own pull request): {reason}\n")
    sys.stderr.write("The user's own PRs are reviewed in the chat only. Give the review in the chat, in the same shape, and post nothing on the PR.\n")
    sys.exit(2)


def check_segment(segment: str, viewer: list[str | None]) -> None:
    target = api_target(segment)
    if target:
        is_pr, author = api_target_author(*target)
    else:
        cmd = pr_cmd_target(segment)
        if cmd is None:
            return
        author = author_of_pr_cmd(*cmd)
        is_pr = True
    if not is_pr:
        return
    if not viewer:
        viewer.append(gh(["api", "user", "--jq", ".login"]))
    if author is None or viewer[0] is None:
        deny("could not verify who authored this pull request, so nothing is posted")
    if author.lower() == viewer[0].lower():
        deny(f"this pull request was opened by {author}, the account running this session")


def main() -> None:
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, AttributeError):
        sys.exit(0)
    viewer: list[str | None] = []
    for segment in SEGMENT_SPLIT.split(command.replace("\n", " ")):
        check_segment(segment, viewer)
    sys.exit(0)


if __name__ == "__main__":
    main()
