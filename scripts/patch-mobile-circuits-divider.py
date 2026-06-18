#!/usr/bin/env python3
"""Add East Africa divider before Kenya in mobile Circuits dropdown."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIVIDER = '            <li class="mobile-menu__dest-divider" aria-hidden="true"><span>East Africa</span></li>\n'
MARKER = 'mobile-menu__dest-divider'


def insert_divider(text: str) -> str:
    if MARKER in text or 'id="mobileDestPanel"' not in text:
        return text
    start = text.find('id="mobileDestPanel"')
    if start < 0:
        return text
    chunk = text[start:start + 4000]
    kenya = chunk.find('kenya.html">Kenya</a></li>')
    if kenya < 0:
        return text
    abs_kenya = start + kenya
    line_start = text.rfind('\n', start, abs_kenya) + 1
    return text[:line_start] + DIVIDER + text[line_start:]


def main():
    count = 0
    for path in ROOT.rglob("*.html"):
        if "scripts" in path.parts or "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new = insert_divider(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            count += 1
    print(f"Updated {count} files")


if __name__ == "__main__":
    main()
