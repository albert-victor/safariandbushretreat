#!/usr/bin/env python3
"""Ensure JSON data slugs map to existing HTML pages."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(name: str) -> dict | list:
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def main() -> None:
    missing: list[tuple[str, str, str]] = []

    # Destinations in tanzania-core
    core = load_json("tanzania-core.json")
    for d in core.get("destinations", []):
        slug = d.get("slug") or d.get("id", "")
        if not slug:
            continue
        path = ROOT / "destinations" / f"{slug}.html"
        if not path.exists():
            missing.append(("tanzania-core.json", slug, "destinations"))

    # Kenya destinations
    kenya = load_json("kenya-data.json")
    for d in kenya.get("destinations", []):
        slug = d.get("slug") or d.get("id", "")
        if not slug:
            continue
        path = ROOT / "kenya" / f"{slug}.html"
        if not path.exists():
            missing.append(("kenya-data.json", slug, "kenya"))

    # Safari packages
    safaris = load_json("safari-packages.json")
    for p in safaris.get("packages", safaris if isinstance(safaris, list) else []):
        if not isinstance(p, dict):
            continue
        slug = p.get("slug", "")
        if not slug:
            continue
        path = ROOT / "safaris" / f"{slug}.html"
        if not path.exists():
            missing.append(("safari-packages.json", slug, "safaris"))

    # Accommodations
    acc = load_json("accommodations.json")
    for a in acc.get("operators", acc.get("accommodations", [])):
        if not isinstance(a, dict):
            continue
        slug = a.get("slug", "")
        if not slug:
            continue
        path = ROOT / "accommodations" / f"{slug}.html"
        if not path.exists():
            missing.append(("accommodations.json", slug, "accommodations"))

    # Search index
    search = load_json("search-index.json")
    for item in search.get("items", []):
        url = item.get("url", "")
        path_part = url.split("?")[0].split("#")[0]
        if not path_part.endswith(".html"):
            continue
        path = ROOT / path_part
        if not path.exists():
            missing.append(("search-index.json", url, "search-index"))

    if missing:
        print("MISSING PAGES FOR DATA ENTRIES:")
        for source, slug, folder in missing:
            print(f"  {source} -> {folder}/{slug}")
        print(f"\nTOTAL missing: {len(missing)}")
    else:
        print("MISSING PAGES FOR DATA ENTRIES: none")
        print("TOTAL missing: 0")


if __name__ == "__main__":
    main()
