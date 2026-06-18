#!/usr/bin/env python3
"""Add Uganda and Rwanda links to Circuits dropdown across all HTML pages."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DESKTOP_KENYA = re.compile(
    r'(<li><a href="[^"]*kenya\.html" role="menuitem">Kenya</a></li>)\s*',
    re.IGNORECASE,
)
MOBILE_KENYA = re.compile(
    r'(<li><a href="[^"]*kenya\.html">Kenya</a></li>)\s*',
    re.IGNORECASE,
)


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    prefix = prefix_for(path)
    uganda = f"{prefix}uganda.html"
    rwanda = f"{prefix}rwanda.html"

    if f'href="{uganda}" role="menuitem">Uganda</a>' not in text:

        def add_desktop(match: re.Match) -> str:
            return (
                match.group(1) + "\n"
                f'              <li><a href="{uganda}" role="menuitem">Uganda</a></li>\n'
                f'              <li><a href="{rwanda}" role="menuitem">Rwanda</a></li>\n'
            )

        text = DESKTOP_KENYA.sub(add_desktop, text, count=1)

    if f'href="{uganda}">Uganda</a>' not in text and "mobile-menu__dest-grid" in text:

        def add_mobile(match: re.Match) -> str:
            return (
                match.group(1) + "\n"
                f'                <li><a href="{uganda}">Uganda</a></li>\n'
                f'                <li><a href="{rwanda}">Rwanda</a></li>\n'
            )

        text = MOBILE_KENYA.sub(add_mobile, text, count=1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    changed = 0
    for html in ROOT.rglob("*.html"):
        if "scripts" in html.parts:
            continue
        if patch_file(html):
            print(f"Patched {html.relative_to(ROOT)}")
            changed += 1
    print(f"Done. {changed} files updated.")


if __name__ == "__main__":
    main()
