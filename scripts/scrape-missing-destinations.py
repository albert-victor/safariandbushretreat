#!/usr/bin/env python3
"""Scrape and append missing destinations listed in circuit sync."""
import importlib.util
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "destinations.json"

spec = importlib.util.spec_from_file_location("sc", ROOT / "scripts" / "scrape-tourism-content.py")
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    existing = {d["slug"] for d in data["destinations"]}
    missing = data.get("missing_from_site", [])
    added = 0
    for item in missing:
        slug = item["slug"]
        if slug in existing:
            continue
        print(f"Scraping {slug}…")
        dest = sc.scrape_one(slug, item["tt_slug"], item["circuit"])
        if dest:
            data["destinations"].append(dest)
            existing.add(slug)
            added += 1
        time.sleep(0.6)
    data["destinations"] = sorted(data["destinations"], key=lambda d: (d["circuit"], d["name"]))
    data.pop("missing_from_site", None)
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Added {added} destinations. Total: {len(data['destinations'])}")


if __name__ == "__main__":
    main()
