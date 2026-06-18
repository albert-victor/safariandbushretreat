#!/usr/bin/env python3
"""Replace typographic dashes (em/en) with keyboard hyphen-minus (-) across source files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "vendor", "node_modules", "assets"}
TEXT_EXT = {".html", ".json", ".py", ".js", ".css", ".md", ".xml", ".txt"}
REPLACEMENTS = (
    ("\u2014", "-"),  # em dash -
    ("\u2013", "-"),  # en dash -
)


def normalize_text(text: str) -> tuple[str, int]:
    count = 0
    for old, new in REPLACEMENTS:
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            count += n
    return text, count


def should_scan(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_EXT:
        return False
    return not any(part in SKIP_DIRS for part in path.parts)


def main():
    total_files = 0
    total_replacements = 0
    hits: list[tuple[str, int]] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or not should_scan(path):
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        updated, n = normalize_text(raw)
        if n:
            path.write_text(updated, encoding="utf-8")
            rel = path.relative_to(ROOT).as_posix()
            hits.append((rel, n))
            total_files += 1
            total_replacements += n

    print(f"Normalized {total_replacements} dashes in {total_files} files")
    for rel, n in hits[:30]:
        print(f"  {n:4d}  {rel}")
    if len(hits) > 30:
        print(f"  ... and {len(hits) - 30} more files")

    report = ROOT / "data" / "dash-normalize-report.json"
    report.write_text(
        json.dumps({"files": len(hits), "replacements": total_replacements, "hits": hits}, indent=2),
        encoding="utf-8",
    )
    print(f"Report -> {report}")


if __name__ == "__main__":
    main()
