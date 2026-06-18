#!/usr/bin/env python3
"""Re-parse destinationSlugs for imported TT packages (fixes footer link pollution)."""
from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"

spec = importlib.util.spec_from_file_location("imp", ROOT / "scripts" / "import-tt-safaris.py")
imp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(imp)


def main():
    core = json.loads(CORE.read_text(encoding="utf-8"))
    dest_by_slug = {d["slug"]: d for d in core["destinations"]}
    fixed = 0

    for p in core["packages"]:
        tt_slug = p.get("tt_slug")
        if not tt_slug:
            continue
        url = imp.BASE + tt_slug
        html = imp.fetch(url)
        if not html:
            continue
        names, slugs = imp.parse_destinations(html, dest_by_slug)
        if slugs:
            p["destinations"] = names
            p["destinationSlugs"] = slugs
            primary = dest_by_slug.get(slugs[0], {})
            if primary.get("circuit"):
                p["circuit"] = primary["circuit"]
            fixed += 1
        time.sleep(0.25)

    imp.sync_related_packages(core)
    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Fixed destinationSlugs on {fixed} packages")


if __name__ == "__main__":
    main()
