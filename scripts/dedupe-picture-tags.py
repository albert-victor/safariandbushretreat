#!/usr/bin/env python3
"""Remove accidentally nested <picture> wrappers left by repeated enhance-html-images runs."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NESTED_PICTURE_RE = re.compile(
    r"<picture>(?:\s*<source[^>]*>|\s*<picture>)*\s*(<img\b[^>]*>)\s*(?:</picture>\s*)+",
    re.IGNORECASE | re.DOTALL,
)


def dedupe_block(match: re.Match[str]) -> str:
    block = match.group(0)
    img = match.group(1)
    sources = re.findall(r"<source[^>]*>", block, flags=re.IGNORECASE)
    if sources:
        return "<picture>" + sources[-1] + img + "</picture>"
    return img


def dedupe_html(html: str) -> str:
    prev = None
    current = html
    while prev != current:
        prev = current
        current = NESTED_PICTURE_RE.sub(dedupe_block, current)
    return current


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    fixed = dedupe_html(text)
    if fixed != text:
        path.write_text(fixed, encoding="utf-8")
        return True
    return False


def main() -> None:
    targets = [
        ROOT / "index.html",
        ROOT / "404.html",
        ROOT / "kenya.html",
        ROOT / "about.html",
    ]
    targets.extend((ROOT / "destinations").glob("*.html"))
    targets.extend((ROOT / "kenya").glob("*.html"))
    targets.extend((ROOT / "circuits").glob("*.html"))
    targets.extend((ROOT / "safaris").glob("*.html"))
    targets.extend((ROOT / "categories").glob("*.html"))

    changed = 0
    for path in targets:
        if path.exists() and process_file(path):
            print(f"Deduped {path.relative_to(ROOT)}")
            changed += 1
    print(f"Done. {changed} files updated.")


if __name__ == "__main__":
    main()
