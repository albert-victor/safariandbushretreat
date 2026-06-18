#!/usr/bin/env python3
"""Rename display label Tanzania Oceanic Islands -> Oceanic Islands (slug unchanged)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OLD = "Tanzania Oceanic Islands"
NEW = "Oceanic Islands"
SKIP_DIRS = {".git", "node_modules", "vendor", ".cursor"}
EXTS = {".html", ".json", ".js", ".py", ".md"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def main():
    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path) or path.suffix not in EXTS:
            continue
        if path.name == "rename-oceanic-islands.py":
            continue
        text = path.read_text(encoding="utf-8")
        if OLD not in text:
            continue
        path.write_text(text.replace(OLD, NEW), encoding="utf-8")
        changed += 1
        print(path.relative_to(ROOT))
    print(f"\nUpdated {changed} files")


if __name__ == "__main__":
    main()
