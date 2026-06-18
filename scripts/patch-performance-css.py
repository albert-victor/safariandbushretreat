#!/usr/bin/env python3
"""Add performance.css to HTML pages that lack it."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"vendor", "node_modules", ".git"}


def main() -> None:
    count = 0
    for html in ROOT.rglob("*.html"):
        if any(p in SKIP for p in html.parts):
            continue
        text = html.read_text(encoding="utf-8")
        if "performance.css" in text:
            continue
        if "destination-page.css" not in text:
            continue
        depth = len(html.relative_to(ROOT).parts) - 1
        prefix = "../" * depth
        line_old = f'<link rel="stylesheet" href="{prefix}css/destination-page.css">'
        if line_old not in text:
            continue
        line_new = (
            line_old
            + f'\n  <link rel="stylesheet" href="{prefix}css/performance.css">'
        )
        html.write_text(text.replace(line_old, line_new, 1), encoding="utf-8")
        count += 1
    print(f"Patched {count} HTML files with performance.css")


if __name__ == "__main__":
    main()
