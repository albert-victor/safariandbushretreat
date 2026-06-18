#!/usr/bin/env python3
"""Fix broken Kenya nav links and escaped href quotes across all HTML pages."""
from __future__ import annotations

import re
from pathlib import Path

# fix-nav-links: run after regenerating pages to catch nav path bugs site-wide.

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"scripts", "vendor", "node_modules"}


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    kenya = f"{prefix_for(path)}kenya.html"

    # Broken double-prefix paths (e.g. ../circuits/../kenya.html)
    text = re.sub(
        r"\.\./(?:circuits|categories|destinations|safaris|accommodations|kenya)/\.\./",
        prefix_for(path),
        text,
    )
    text = text.replace("circuits/kenya.html", kenya)
    text = text.replace('href=\\"', 'href="')
    text = text.replace('\\">', '">')
    # Kenya pages wrongly placed under destinations/
    text = text.replace(f"{prefix_for(path)}destinations/masai-mara.html", f"{prefix_for(path)}kenya/masai-mara.html")
    text = text.replace(f"{prefix_for(path)}destinations/amboseli.html", f"{prefix_for(path)}kenya/amboseli.html")
    text = text.replace(f"{prefix_for(path)}destinations/samburu.html", f"{prefix_for(path)}kenya/samburu.html")
    text = text.replace(f"{prefix_for(path)}destinations/lake-nakuru.html", f"{prefix_for(path)}kenya/lake-nakuru.html")
    text = text.replace(f"{prefix_for(path)}destinations/lake-naivasha.html", f"{prefix_for(path)}kenya/lake-naivasha.html")
    text = text.replace(f"{prefix_for(path)}destinations/diani-beach.html", f"{prefix_for(path)}kenya/diani-beach.html")

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for html in ROOT.rglob("*.html"):
        if any(part in SKIP for part in html.parts):
            continue
        if fix_file(html):
            print(f"Fixed {html.relative_to(ROOT)}")
            changed += 1
    print(f"Done. {changed} files updated.")


if __name__ == "__main__":
    main()
