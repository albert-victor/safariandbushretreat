#!/usr/bin/env python3
"""Validate nav asset/index paths use correct depth prefix per page location."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"scripts", "vendor", "node_modules"}

CHECKS = [
    ("index.html#home", "home link"),
    ("index.html#destinations", "circuits anchor"),
    ("about.html", "about page"),
    ("assets/images/logo-nav.png", "logo"),
    ("js/main.js", "main.js"),
    ("css/style.css", "style.css"),
]


def expected_prefix(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth


def main() -> None:
    issues: list[tuple[str, str, str]] = []

    for html in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP for part in html.parts):
            continue
        text = html.read_text(encoding="utf-8")
        rel = str(html.relative_to(ROOT))
        prefix = expected_prefix(html)

        for target, label in CHECKS:
            good = f'href="{prefix}{target}"'
            if target.endswith((".png", ".js", ".css")):
                attr = "src" if target.endswith(".js") else ("href" if "css" in target else "src")
                good = f'{attr}="{prefix}{target}"'
                if good not in text:
                    # css uses link rel stylesheet
                    if target.endswith(".css"):
                        good = f'href="{prefix}{target}"'
            if good not in text:
                # Allow root pages without prefix
                if prefix == "" and f'href="{target}"' in text:
                    continue
                if prefix == "" and target.endswith(".css") and f'href="{target}"' in text:
                    continue
                if prefix == "" and target.endswith(".js") and f'src="{target}"' in text:
                    continue
                if prefix == "" and target.endswith(".png") and f'src="{target}"' in text:
                    continue
                issues.append((rel, label, f'expected {prefix}{target}'))

        # Nav must not contain double-prefix patterns
        if re.search(r'href="(?:\.\./)+(?:circuits|categories|destinations|safaris|accommodations|kenya)/\.\./', text):
            issues.append((rel, "nav", "double-prefix folder path"))

    if issues:
        print("NAV DEPTH ISSUES:")
        for path, label, detail in issues:
            print(f"  {path} [{label}] -> {detail}")
        print(f"\nTOTAL issues: {len(issues)}")
    else:
        print("NAV DEPTH ISSUES: none")
        print("TOTAL issues: 0")


if __name__ == "__main__":
    main()
