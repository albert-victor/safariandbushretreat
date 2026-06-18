#!/usr/bin/env python3
"""Remove duplicate circuit nav fragments left by broken patch-circuit-nav regex."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DESKTOP_DUP = re.compile(
    r"(\s*<li><a href=\"(?:\.\./)*circuits/mafia-island\.html\" role=\"menuitem\">Mafia Island</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*kenya\.html\" role=\"menuitem\">Kenya</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*uganda\.html\" role=\"menuitem\">Uganda</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*rwanda\.html\" role=\"menuitem\">Rwanda</a></li>\s*"
    r"</ul>\s*</li>)\s*"
    r"<li><a href=\"(?:\.\./)*circuits/mafia-island\.html\" role=\"menuitem\">Mafia Island</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*kenya\.html\" role=\"menuitem\">Kenya</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*uganda\.html\" role=\"menuitem\">Uganda</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*rwanda\.html\" role=\"menuitem\">Rwanda</a></li>\s*"
    r"</ul>\s*</li>",
    re.S,
)

MOBILE_DUP = re.compile(
    r"(<li><a href=\"(?:\.\./)*rwanda\.html\">Rwanda</a></li>)\s*"
    r"</ul>\s*</li>\s*"
    r"<li><a href=\"(?:\.\./)*circuits/mafia-island\.html\">Mafia Island</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*kenya\.html\">Kenya</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*uganda\.html\">Uganda</a></li>\s*"
    r"<li><a href=\"(?:\.\./)*rwanda\.html\">Rwanda</a></li>\s*"
    r"</ul>",
    re.S,
)

MOBILE_DUP_SUB = r"\1\n              </ul>"


def main():
    changed = 0
    for path in ROOT.rglob("*.html"):
        if "vendor" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        original = text
        text = DESKTOP_DUP.sub(r"\1", text)
        text = MOBILE_DUP.sub(MOBILE_DUP_SUB, text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"Fixed {path.relative_to(ROOT)}")
            changed += 1
    print(f"Done. {changed} files repaired.")


if __name__ == "__main__":
    main()
