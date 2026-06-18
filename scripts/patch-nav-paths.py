#!/usr/bin/env python3
"""Fix broken nav paths across generated HTML."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"scripts", "vendor", "node_modules", ".git", ".cursor"}

REPLACEMENTS = [
    ("categories/../safaris/", "safaris/"),
    ('href="/circuits/index.html"', 'href="index.html"'),
    ('href="/circuits/', 'href="'),
]


def main() -> None:
    n = 0
    for path in ROOT.rglob("*.html"):
        if any(p in SKIP for p in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        new = text
        for old, rep in REPLACEMENTS:
            new = new.replace(old, rep)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
    print(f"Patched nav paths in {n} HTML files.")


if __name__ == "__main__":
    main()
