#!/usr/bin/env python3
"""Structural checks for the configs in this repo. Run from the repo root."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONFIGS = REPO / "configs"
BASELINE = "agnostic"
SHARED_LIB = "_hooklib.py"
# Why: a focused config (a reviewer, say) deliberately ships a subset, so baseline parity must not apply to it.
STANDALONE = "standalone"
HOOK_REF = re.compile(r"\$CLAUDE_PROJECT_DIR/\.claude/hooks/([\w.-]+)")
LOCAL_PATH = re.compile(r"/(?:Users|home)/[A-Za-z0-9_.-]+/")

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def frontmatter(skill: Path) -> dict[str, str]:
    lines = skill.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep and not key.startswith((" ", "\t")):
            fields[key.strip()] = value.strip()
    return fields


def variant_lines(config: Path) -> list[str]:
    variant = config / ".variant"
    if not variant.is_file():
        return []
    return [line.strip() for line in variant.read_text(encoding="utf-8").splitlines() if line.strip()]


def is_standalone(config: Path) -> bool:
    return STANDALONE in variant_lines(config)[1:]


def check_variant(config: Path) -> None:
    lines = variant_lines(config)
    if not lines:
        fail(f"{rel(config)}: missing or empty .variant")
        return
    if lines[0] != config.name:
        fail(f"{rel(config)}/.variant: first line must be '{config.name}'")
    for extra in lines[1:]:
        if extra != STANDALONE:
            fail(f"{rel(config)}/.variant: unknown marker '{extra}' (only '{STANDALONE}' is allowed)")


def check_settings(config: Path) -> None:
    settings = config / "settings.json"
    if not settings.is_file():
        fail(f"{rel(config)}: missing settings.json")
        return
    raw = settings.read_text(encoding="utf-8")
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"{rel(settings)}: invalid JSON — {exc}")
        return
    for name in sorted(set(HOOK_REF.findall(raw))):
        if not (config / "hooks" / name).is_file():
            fail(f"{rel(settings)}: references hooks/{name}, which does not exist")


def check_hooks_executable(config: Path) -> None:
    for hook in sorted((config / "hooks").glob("*.sh")):
        if not hook.stat().st_mode & 0o111:
            fail(f"{rel(hook)}: shell hook is not executable (chmod +x)")


def check_skills(config: Path) -> None:
    for skill_dir in sorted((config / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        skill = skill_dir / "SKILL.md"
        if not skill.is_file():
            fail(f"{rel(skill_dir)}: missing SKILL.md")
            continue
        fields = frontmatter(skill)
        if not fields:
            fail(f"{rel(skill)}: missing YAML frontmatter")
            continue
        if fields.get("name") != skill_dir.name:
            fail(f"{rel(skill)}: frontmatter name '{fields.get('name')}' != directory '{skill_dir.name}'")
        if not fields.get("description"):
            fail(f"{rel(skill)}: frontmatter has no description")


def check_parity(configs: list[Path]) -> None:
    baseline = CONFIGS / BASELINE
    for config in configs:
        if config == baseline or is_standalone(config):
            continue
        for kind, pattern in (("skills", "*/SKILL.md"), ("commands", "*.md")):
            base_names = {p.parent.name if kind == "skills" else p.stem for p in (baseline / kind).glob(pattern)}
            names = {p.parent.name if kind == "skills" else p.stem for p in (config / kind).glob(pattern)}
            for missing in sorted(base_names - names):
                fail(f"configs/{config.name}/{kind}: '{missing}' exists in {BASELINE} but not here — keep them in sync")


def check_readme(configs: list[Path]) -> None:
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    for config in configs:
        for skill_dir in sorted((config / "skills").iterdir()):
            if skill_dir.is_dir() and skill_dir.name not in readme:
                fail(f"README.md: skill '{skill_dir.name}' is not documented")
        for command in sorted((config / "commands").glob("*.md")):
            if f"/{command.stem}" not in readme:
                fail(f"README.md: command '/{command.stem}' is not documented")
        for hook in sorted((config / "hooks").iterdir()):
            if hook.is_file() and hook.name != SHARED_LIB and hook.name not in readme:
                fail(f"README.md: hook '{hook.name}' is not documented")


def check_local_paths() -> None:
    for path in sorted(REPO.rglob("*")):
        if not path.is_file() or ".git/" in f"{path.relative_to(REPO)}/":
            continue
        if path.suffix not in {".md", ".py", ".sh", ".json", ".yml", ".yaml"}:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if LOCAL_PATH.search(line):
                fail(f"{rel(path)}:{number}: absolute local path — use a repo-relative path or $CLAUDE_PROJECT_DIR")


def main() -> int:
    configs = sorted(c for c in CONFIGS.iterdir() if c.is_dir())
    if not configs:
        print("no configs found", file=sys.stderr)
        return 1
    for config in configs:
        check_variant(config)
        check_settings(config)
        check_hooks_executable(config)
        check_skills(config)
    check_parity(configs)
    check_readme(configs)
    check_local_paths()

    if errors:
        for error in errors:
            print(f"✗ {error}", file=sys.stderr)
        print(f"\n{len(errors)} problem(s) found.", file=sys.stderr)
        return 1
    print(f"✓ {len(configs)} config(s) validated: {', '.join(c.name for c in configs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
