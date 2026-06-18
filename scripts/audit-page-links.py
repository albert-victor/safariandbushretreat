#!/usr/bin/env python3
"""Audit HTML page links and suspicious path patterns site-wide."""
from __future__ import annotations

import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"scripts", "vendor", "node_modules"}

SUSPICIOUS_PATTERNS = [
    (re.compile(r'href=\\"'), "escaped href quote"),
    (re.compile(r'\.\./\w+/\.\./'), "double-prefix path"),
    (re.compile(r'href="(?:circuits|destinations|safaris|categories|accommodations)/[^"]*kenya\.html"'), "kenya under wrong folder"),
]


def resolve_href(source: Path, href: str) -> Path:
    ref = urllib.parse.unquote(href.split("?")[0].split("#")[0].strip())
    return (source.parent / ref).resolve()


def main() -> None:
    broken_pages: list[tuple[str, str]] = []
    suspicious: list[tuple[str, str]] = []
    seen_suspicious: set[tuple[str, str]] = set()

    for html in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in html.parts):
            continue
        text = html.read_text(encoding="utf-8")
        rel = str(html.relative_to(ROOT))

        for pattern, label in SUSPICIOUS_PATTERNS:
            if pattern.search(text):
                key = (rel, label)
                if key not in seen_suspicious:
                    seen_suspicious.add(key)
                    suspicious.append(key)

        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "#")):
                continue
            path_part = href.split("?")[0].split("#")[0]
            if ".html" not in path_part:
                continue
            target = resolve_href(html, href)
            if not target.exists():
                broken_pages.append((rel, href))

    # Search index URLs (root-relative)
    search_index = ROOT / "data" / "search-index.json"
    if search_index.exists():
        import json

        data = json.loads(search_index.read_text(encoding="utf-8"))
        for item in data.get("items", []):
            url = item.get("url", "")
            path_part = urllib.parse.unquote(url.split("?")[0].split("#")[0])
            if not path_part.endswith(".html"):
                continue
            target = (ROOT / path_part).resolve()
            if not target.exists():
                broken_pages.append(("data/search-index.json", url))

    if suspicious:
        print("SUSPICIOUS PATTERNS:")
        for path, label in suspicious:
            print(f"  {path} -> {label}")
        print(f"\nTOTAL suspicious: {len(suspicious)}\n")

    if broken_pages:
        print("BROKEN PAGE LINKS:")
        for path, href in broken_pages:
            print(f"  {path} -> {href}")
        print(f"\nTOTAL broken pages: {len(broken_pages)}")
    else:
        print("BROKEN PAGE LINKS: none")
        print("TOTAL broken pages: 0")


if __name__ == "__main__":
    main()
