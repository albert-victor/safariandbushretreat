#!/usr/bin/env python3
"""Report broken relative links and suspicious path patterns in HTML/JS/JSON."""
from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"scripts", "vendor", "node_modules"}

ATTR_PATTERNS = [
    re.compile(r'href="([^"]+)"'),
    re.compile(r'src="([^"]+)"'),
    re.compile(r'srcset="([^"]+)"'),
]

SUSPICIOUS = [
    (re.compile(r'href=\\"'), "escaped href quote"),
    (re.compile(r'\.\./\w+/\.\./'), "double-prefix path (e.g. ../circuits/../)"),
    (re.compile(r'href="(?:circuits|destinations|safaris|categories|accommodations|kenya)/[^"]*kenya\.html"'), "kenya page under wrong folder"),
    (re.compile(r'href="[^"]*//[^"]*"'), "double-slash in path"),
    (re.compile(r'\\'), "backslash in HTML attribute"),
]

SKIP_URL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "javascript:", "data:", "#")


def urls_from_srcset(value: str) -> list[str]:
    return [part.strip().split()[0] for part in value.split(",") if part.strip()]


def resolve_ref(source: Path, ref: str) -> Path | None:
    ref = ref.split("?")[0].split("#")[0].strip()
    if not ref or ref.startswith(SKIP_URL_PREFIXES):
        return None
    return (source.parent / ref).resolve()


def audit_file(path: Path) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    broken: list[tuple[str, str]] = []
    suspicious: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT))

    for pattern, label in SUSPICIOUS:
        if pattern.search(text):
            suspicious.append((rel, label))

    refs: set[str] = set()
    for rx in ATTR_PATTERNS:
        for match in rx.finditer(text):
            value = match.group(1)
            if rx.pattern.startswith("srcset"):
                refs.update(urls_from_srcset(value))
            else:
                refs.add(value)

    for ref in sorted(refs):
        target = resolve_ref(path, ref)
        if target is None:
            continue
        if not target.exists():
            broken.append((rel, ref))
    return broken, suspicious


def main() -> None:
    broken_all: list[tuple[str, str]] = []
    suspicious_all: list[tuple[str, str]] = []

    for ext in ("*.html", "*.js", "*.json"):
        for f in ROOT.rglob(ext):
            if any(part in SKIP for part in f.parts):
                continue
            if f.name == "package-lock.json":
                continue
            broken, suspicious = audit_file(f)
            broken_all.extend(broken)
            suspicious_all.extend(suspicious)

    if suspicious_all:
        print("SUSPICIOUS PATTERNS:")
        seen = set()
        for path, label in suspicious_all:
            key = (path, label)
            if key in seen:
                continue
            seen.add(key)
            print(f"  {path} -> {label}")
        print(f"\nTOTAL suspicious: {len(seen)}")
        print()

    if broken_all:
        print("BROKEN LINKS:")
        for path, ref in broken_all:
            print(f"  {path} -> {ref}")
        print(f"\nTOTAL broken: {len(broken_all)}")
    else:
        print("BROKEN LINKS: none")
        print("TOTAL broken: 0")


if __name__ == "__main__":
    main()
