#!/usr/bin/env python3
"""Point booking CTAs at the booking form anchor (#bookingForm)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"scripts", "vendor", "node_modules", ".git"}


def patch_html(text: str) -> str:
    text = text.replace("../index.html#contact", "../index.html#bookingForm")
    text = text.replace("index.html#contact", "index.html#bookingForm")
    text = text.replace('href="#contact"', 'href="#bookingForm"')
    return text


def main() -> None:
    updated = 0
    for path in ROOT.rglob("*.html"):
        if SKIP.intersection(path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        patched = patch_html(original)
        if patched != original:
            path.write_text(patched, encoding="utf-8")
            updated += 1
    print(f"Patched booking links in {updated} HTML files")


if __name__ == "__main__":
    main()
