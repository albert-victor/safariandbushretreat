#!/usr/bin/env python3
"""Replace old SVG logo/favicon references with new PNG assets."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"node_modules", "vendor", ".git"}


def patch_html(text: str) -> str:
    text = text.replace("logo-mark.svg", "logo-nav.png")
    text = text.replace(
        '<link rel="icon" type="image/svg+xml" href="assets/images/favicon.svg">',
        '<link rel="icon" type="image/png" href="assets/images/favicon.png">\n'
        '  <link rel="apple-touch-icon" href="assets/images/apple-touch-icon.png">',
    )
    text = text.replace(
        '<link rel="icon" type="image/svg+xml" href="../assets/images/favicon.svg">',
        '<link rel="icon" type="image/png" href="../assets/images/favicon.png">\n'
        '  <link rel="apple-touch-icon" href="../assets/images/apple-touch-icon.png">',
    )
    text = text.replace(
        '<link rel="apple-touch-icon" href="assets/images/favicon.svg">', ""
    )
    text = text.replace(
        '<link rel="apple-touch-icon" href="../assets/images/favicon.svg">', ""
    )
    text = text.replace("assets/images/favicon.svg", "assets/images/logo.png")
    text = text.replace("../assets/images/favicon.svg", "../assets/images/logo.png")
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
    print(f"Updated {updated} HTML files")


if __name__ == "__main__":
    main()
