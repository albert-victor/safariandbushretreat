#!/usr/bin/env python3
"""Replace old circuit-based Safaris dropdown with category links across all HTML pages."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OLD_DROPDOWN = re.compile(
    r'<ul class="navbar__dropdown" role="menu">\s*'
    r'<li><a href="[^"]*#safaris-northern"[^>]*>Northern Circuit</a></li>\s*'
    r'<li><a href="[^"]*#safaris-southern"[^>]*>Southern Circuit</a></li>\s*'
    r'<li><a href="[^"]*#safaris-eastern"[^>]*>Eastern Circuit</a></li>\s*'
    r'<li><a href="[^"]*#safaris-western"[^>]*>Western Circuit</a></li>\s*'
    r'<li><a href="[^"]*#safaris-zanzibar"[^>]*>Zanzibar &amp; Islands</a></li>\s*'
    r'(?:<li><a href="[^"]*5-days-northern-classic\.html"[^>]*>5-Day Northern Classic</a></li>\s*)?'
    r'</ul>',
    re.MULTILINE,
)

OLD_MOBILE = re.compile(
    r'<ul class="mobile-menu__dest-grid">\s*'
    r'<li><a href="[^"]*#safaris-northern"[^>]*>Northern Circuit</a></li>\s*'
    r'<li><a href="[^"]*#safaris-southern"[^>]*>Southern Circuit</a></li>\s*'
    r'<li><a href="[^"]*#safaris-eastern"[^>]*>Eastern Circuit</a></li>\s*'
    r'<li><a href="[^"]*#safaris-western"[^>]*>Western Circuit</a></li>\s*'
    r'<li><a href="[^"]*#safaris-zanzibar"[^>]*>Zanzibar &amp; Islands</a></li>\s*'
    r'(?:<li><a href="[^"]*5-days-northern-classic\.html"[^>]*>5-Day Northern Classic</a></li>\s*)?'
    r'</ul>',
    re.MULTILINE,
)

CATEGORIES = [
    ("tanzania-safaris.html", "Tanzania Safaris"),
    ("adventure-safaris.html", "Adventure Safaris"),
    ("mountain-climbing.html", "Mountain Climbing"),
    ("beach-holiday.html", "Beach Holiday"),
    ("walking-safaris.html", "Walking Safaris"),
    ("tourist-attractions.html", "Tourist Attractions"),
]


def category_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT)
    depth = len(rel.parts) - 1
    return "../" * depth + "categories/"


def build_dropdown(prefix: str, mobile: bool = False) -> str:
    items = []
    for href, label in CATEGORIES:
        url = prefix + href
        if mobile:
            items.append(f'                <li><a href="{url}">{label}</a></li>')
        else:
            items.append(f'              <li><a href="{url}" role="menuitem">{label}</a></li>')
    body = "\n".join(items)
    if mobile:
        return f'<ul class="mobile-menu__dest-grid">\n{body}\n              </ul>'
    return f'<ul class="navbar__dropdown" role="menu">\n{body}\n            </ul>'


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    prefix = category_prefix(path)

    text = OLD_DROPDOWN.sub(build_dropdown(prefix), text)
    text = OLD_MOBILE.sub(build_dropdown(prefix, mobile=True), text)

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
            changed += 1
            print(f"Patched {html.relative_to(ROOT)}")
    print(f"Done. {changed} files updated.")


if __name__ == "__main__":
    main()
