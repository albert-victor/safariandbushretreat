#!/usr/bin/env python3
"""Move Kenya into Circuits dropdown; replace top-level Kenya with About Us."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KENYA_TOP = re.compile(
    r'\s*<li><a href="[^"]*kenya\.html" class="navbar__link[^"]*">Kenya</a></li>\s*',
    re.IGNORECASE,
)

KENYA_MOBILE_TOP = re.compile(
    r'\s*<li><a href="[^"]*kenya\.html" class="mobile-menu__link">Kenya</a></li>\s*',
    re.IGNORECASE,
)


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth


def patch_file(path: Path) -> bool:
    if path.name == "about.html":
        return False

    text = path.read_text(encoding="utf-8")
    original = text
    prefix = prefix_for(path)
    kenya = f"{prefix}kenya.html"

    if "About Us" not in text:
        text = KENYA_TOP.sub(
            f'          <li><a href="{prefix}about.html" class="navbar__link">About Us</a></li>\n',
            text,
            count=1,
        )
        text = KENYA_MOBILE_TOP.sub(
            f'          <li><a href="{prefix}about.html" class="mobile-menu__link">About Us</a></li>\n',
            text,
            count=1,
        )

    if f'href="{kenya}" role="menuitem">Kenya</a>' not in text:
        text = text.replace(
            "Ocean Islands</a></li>\n",
            f"Ocean Islands</a></li>\n              <li><a href=\"{kenya}\" role=\"menuitem\">Kenya</a></li>\n",
            1,
        )

    if f'href="{kenya}">Kenya</a>' not in text and "mobile-menu__dest-grid" in text:
        def _add_kenya_mobile(match: re.Match) -> str:
            return match.group(1) + f'                <li><a href="{kenya}">Kenya</a></li>\n'

        text = re.sub(
            r'(<li><a href="[^"]*ocean-islands\.html">Ocean Islands</a></li>\s*)',
            _add_kenya_mobile,
            text,
            count=1,
        )

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
