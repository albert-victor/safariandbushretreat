#!/usr/bin/env python3
"""Link TT packages to the correct destination slugs when name/slug clearly implies one."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"

# package slug -> destination slugs to add (keeps existing zanzibar parent where useful)
PACKAGE_DEST_ADD = {
    "gangilonga-stone-iringa": ["gangilonga"],
    "chumbe-island-coral-park": ["chumbe-island"],
    "prison-island-zanzibar": ["prison-island"],
    "magoroto-forest-estate": ["usambara"],
    "tongoni-ruins-tanga": ["pangani", "tanga-marine"],
    "nungwi-experience": ["mnemba-island"],
    "day-trip-to-isimila-stone-age-and-igeleke-rock-art-sites": ["gangilonga", "igelegke-rock-art"],
    "kalenga-historical-museum": ["gangilonga", "isimila"],
    "day-trip-hiking-to-uluguru-mountains-choma-waterfalls": ["uluguru"],
    "amboni-caves-tours-tanga": ["tanga-marine"],
    "galanos-hot-sulphur-springs-tours-tanga": ["tanga-marine"],
}

# package slug suffix/pattern -> destination
SLUG_SUFFIX_DEST = {
    "-kilwa": "kilwa",
}


def main():
    core = json.loads(CORE.read_text(encoding="utf-8"))
    dest_slugs = {d["slug"] for d in core["destinations"]}
    updated = 0

    for p in core["packages"]:
        slug = p["slug"]
        extra: list[str] = []

        if slug in PACKAGE_DEST_ADD:
            extra.extend(PACKAGE_DEST_ADD[slug])

        for suffix, dest in SLUG_SUFFIX_DEST.items():
            if slug.endswith(suffix) and dest in dest_slugs:
                extra.append(dest)

        if not extra:
            continue

        current = list(p.get("destinationSlugs", []))
        merged = current[:]
        for ds in extra:
            if ds in dest_slugs and ds not in merged:
                merged.append(ds)
        if merged != current:
            p["destinationSlugs"] = merged
            names = []
            by_slug = {d["slug"]: d["name"] for d in core["destinations"]}
            for ds in merged:
                names.append(by_slug.get(ds, ds.replace("-", " ").title()))
            p["destinations"] = names
            updated += 1

    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated destinationSlugs on {updated} packages")


if __name__ == "__main__":
    main()
