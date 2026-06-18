#!/usr/bin/env python3
"""Replace em dash and en dash with ASCII hyphen (-) in text files."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "vendor", "node_modules", "__pycache__"}
EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".htaccess",
}
EXTRA_FILES = {"AGENTS.md", "README.md", ".htaccess"}
REPLACEMENTS = (
    ("\u2014", "-"),  # em dash -
    ("\u2013", "-"),  # en dash -
)


def should_process(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.suffix.lower() in EXTENSIONS:
        return True
    return path.name in EXTRA_FILES


def main() -> None:
    changed_files = 0
    em_count = 0
    en_count = 0

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not should_process(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        original = text
        em = text.count("\u2014")
        en = text.count("\u2013")
        if em or en:
            for old, new in REPLACEMENTS:
                text = text.replace(old, new)
            path.write_text(text, encoding="utf-8")
            changed_files += 1
            em_count += em
            en_count += en
            rel = path.relative_to(ROOT)
            print(f"  {rel}: {em} em, {en} en")

    print(f"\nUpdated {changed_files} files ({em_count} em dashes, {en_count} en dashes)")


if __name__ == "__main__":
    main()
