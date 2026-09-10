#!/usr/bin/env python3
import colorsys
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

STYLE_EXTS = {".css", ".scss", ".less"}
COMPONENT_EXTS = {".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".html", ".astro"}
TOKEN_FILE_HINTS = ("token", "theme", "tailwind.config", "variables", "palette", "colors")
TEST_MARKERS = ("test_", "_test.", ".test.", ".spec.", "_spec.", "__tests__", "stories")
NEAR_DISTANCE = 40.0
MAX_PALETTE_FILES = 200
MAX_READ = 256 * 1024
MAX_REPORTED = 6

HEX_RE = re.compile(r"#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b")
RGB_FN_RE = re.compile(r"rgba?\(\s*(\d{1,3})[ ,]+(\d{1,3})[ ,]+(\d{1,3})")
HSL_TRIPLET_RE = re.compile(r":\s*([\d.]+)[, ]\s*([\d.]+)%[, ]\s*([\d.]+)%")
VAR_DEF_RE = re.compile(r"(--[\w-]+)\s*:")

RGB = Tuple[int, int, int]


def hex_to_rgb(raw: str) -> RGB:
    h = raw[:4] if len(raw) == 4 else raw
    if len(h) <= 4:
        h = "".join(c * 2 for c in h[:3])
    else:
        h = h[:6]
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def hsl_to_rgb(h: float, s: float, lightness: float) -> RGB:
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, lightness / 100.0, s / 100.0)
    return (round(r * 255), round(g * 255), round(b * 255))


def distance(a: RGB, b: RGB) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def colors_in_line(line: str) -> List[Tuple[RGB, str]]:
    found = []
    for m in HEX_RE.finditer(line):
        found.append((hex_to_rgb(m.group(1)), f"#{m.group(1)}"))
    for m in RGB_FN_RE.finditer(line):
        rgb = tuple(min(255, int(v)) for v in m.groups())
        found.append((rgb, f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"))
    if not found and VAR_DEF_RE.search(line):
        m = HSL_TRIPLET_RE.search(line)
        if m:
            h, s, lightness = (float(v) for v in m.groups())
            if s <= 100 and lightness <= 100:
                found.append((hsl_to_rgb(h, s, lightness), f"hsl({m.group(1)} {m.group(2)}% {m.group(3)}%)"))
    return found


def is_token_context(path: Path, line: str) -> bool:
    name = path.name.lower()
    if any(hint in name for hint in TOKEN_FILE_HINTS):
        return True
    return bool(VAR_DEF_RE.search(line))


def style_files(cwd: str) -> List[str]:
    try:
        res = subprocess.run(
            ["git", "ls-files", "-z", "--", "*.css", "*.scss", "*.less",
             "*tailwind.config*", "*theme*", "*tokens*"],
            capture_output=True, text=True, cwd=cwd, timeout=10,
        )
    except Exception:
        return []
    return [p for p in res.stdout.split("\0") if p][:MAX_PALETTE_FILES]


def project_palette(cwd: str) -> Dict[RGB, Tuple[str, str]]:
    palette: Dict[RGB, Tuple[str, str]] = {}
    for rel in style_files(cwd):
        try:
            text = (Path(cwd) / rel).read_text(encoding="utf-8", errors="ignore")[:MAX_READ]
        except Exception:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            var = VAR_DEF_RE.search(line)
            label = var.group(1) if var else f"{Path(rel).name}:{line_no}"
            for rgb, _ in colors_in_line(line):
                palette.setdefault(rgb, (label, f"{rel}:{line_no}"))
    return palette


def nearest(rgb: RGB, palette: Dict[RGB, Tuple[str, str]]) -> Optional[Tuple[float, RGB, Tuple[str, str]]]:
    best = None
    for existing, meta in palette.items():
        d = distance(rgb, existing)
        if best is None or d < best[0]:
            best = (d, existing, meta)
    return best


def new_content_from(data: dict) -> str:
    tool_input = data.get("tool_input") or {}
    if data.get("tool_name") == "Write":
        return tool_input.get("content") or ""
    if data.get("tool_name") == "Edit":
        return tool_input.get("new_string") or ""
    if data.get("tool_name") == "MultiEdit":
        return "\n".join((e.get("new_string") or "") for e in tool_input.get("edits") or [])
    return ""


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = (data.get("tool_input") or {}).get("file_path") or ""
    path = Path(file_path)
    ext = path.suffix.lower()
    if ext not in STYLE_EXTS | COMPONENT_EXTS:
        sys.exit(0)
    lowered = path.name.lower()
    if any(m in lowered for m in TEST_MARKERS):
        sys.exit(0)

    content = new_content_from(data)
    if not content or not (HEX_RE.search(content) or RGB_FN_RE.search(content)
                           or (VAR_DEF_RE.search(content) and HSL_TRIPLET_RE.search(content))):
        sys.exit(0)

    cwd = data.get("cwd") or "."
    palette = project_palette(cwd)

    findings: List[str] = []
    seen: set = set()
    for line in content.splitlines():
        token_context = is_token_context(path, line)
        var = VAR_DEF_RE.search(line)
        var_name = var.group(1) if var else None
        for rgb, literal in colors_in_line(line):
            key = (rgb, var_name, token_context)
            if key in seen:
                continue
            seen.add(key)
            if not token_context:
                match = nearest(rgb, palette)
                hint = ""
                if match and match[0] <= NEAR_DISTANCE:
                    hint = f" (existing token: {match[2][0]} at {match[2][1]})"
                findings.append(f"  - {literal} hardcoded in {path.name} — use a design token{hint}")
            else:
                match = nearest(rgb, palette)
                if match is None:
                    continue
                d, _, meta = match
                if meta[0] == var_name:
                    continue
                if d == 0:
                    findings.append(
                        f"  - {literal} ({var_name or path.name}) is IDENTICAL to existing "
                        f"{meta[0]} ({meta[1]}) — reuse it, do not define a duplicate")
                elif d <= NEAR_DISTANCE:
                    findings.append(
                        f"  - {literal} ({var_name or path.name}) is nearly identical to existing "
                        f"{meta[0]} ({meta[1]}) — reuse it or justify a distinct color")
            if len(findings) >= MAX_REPORTED:
                break
        if len(findings) >= MAX_REPORTED:
            break

    if not findings:
        sys.exit(0)

    print("Design-token check — colors that break the existing system:", file=sys.stderr)
    print("\n".join(findings), file=sys.stderr)
    print(
        "The existing design system is the law: reuse its tokens (grep the token source first). "
        "A genuinely new color gets a ROLE name in the token file, derived from the project's scale — "
        "never a raw literal in a component and never a duplicate of a color that already has a name.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
