#!/usr/bin/env python3
"""Remove generated HTML pages not in canonical JSON data."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST_DATA = ROOT / "data" / "destinations.json"
PKG_DATA = ROOT / "data" / "safari-packages.json"
DEST_OUT = ROOT / "destinations"
SAFARI_OUT = ROOT / "safaris"


def main():
    dest_slugs = {d["slug"] for d in json.loads(DEST_DATA.read_text(encoding="utf-8"))["destinations"]}
    pkg_slugs = {p["slug"] for p in json.loads(PKG_DATA.read_text(encoding="utf-8"))["packages"]}

    removed = 0
    for legacy_name in ("coastal-islands.html", "zanzibar-islands.html", "ocean-islands.html"):
        legacy = ROOT / "circuits" / legacy_name
        if legacy.exists():
            legacy.unlink()
            print(f"Removed circuits/{legacy_name} (replaced by tanzania-oceanic-islands.html)")
            removed += 1

    for path in DEST_OUT.glob("*.html"):
        if path.stem not in dest_slugs:
            path.unlink()
            print(f"Removed destinations/{path.name}")
            removed += 1

    for path in SAFARI_OUT.glob("*.html"):
        if path.stem not in pkg_slugs:
            path.unlink()
            print(f"Removed safaris/{path.name}")
            removed += 1

    print(f"Cleanup complete - removed {removed} orphaned pages.")


if __name__ == "__main__":
    main()
