#!/usr/bin/env python3
"""Download and assign verified Tanzania Tourism images for Mafia Island circuit."""
from __future__ import annotations

import json
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"
TT_DIR = ROOT / "assets" / "images" / "external" / "tt"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

MAFIA_SLUGS = {"mafia", "chole-island", "chole-bay", "bwejuu-island", "jibondo-island", "juani-island"}

# Curated heroes/galleries from TT (verified Mafia uploads)
DEST_IMAGES = {
    "mafia": {
        "hero": "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Whale_Shark_04.jpg",
        "gallery": [
            "https://www.tanzaniatourism.com/images/uploads/Chole_Bay_Snorkeling_Mafia_Island.jpg",
            "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Diving_01.jpg",
            "https://www.tanzaniatourism.com/images/uploads/Kua_Ruins_Mosque_Mafia_2_2018.jpg",
            "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Sunset_Cruise.jpg",
        ],
    },
    "chole-bay": {
        "hero": "https://www.tanzaniatourism.com/images/uploads/Chole_Bay_Snorkeling_Mafia_Island.jpg",
        "gallery": [
            "https://www.tanzaniatourism.com/images/uploads/Scuba_Diving_in_Mafia_Island.jpg",
            "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Whale_Shark_04.jpg",
        ],
    },
    "chole-island": {
        "hero": "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Chole_Mjini.jpg",
        "gallery": [
            "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Ancient_Hindu_Temple_Built_in_1890_Under_Ficus_Roots_02.jpg",
        ],
    },
    "bwejuu-island": {
        "hero": "https://www.tanzaniatourism.com/images/uploads/Bwejuu_Island_in_Mafia_Island.jpg",
        "gallery": [
            "https://www.tanzaniatourism.com/images/uploads/Marimbani_Sandbanks_in_Mafia_Island_1.jpg",
        ],
    },
    "jibondo-island": {
        "hero": "https://www.tanzaniatourism.com/images/uploads/Jibondo_Island_Coconut_Trees_in_Mafia_Islands.jpg",
        "gallery": [
            "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Sailing_Boat_03.jpg",
        ],
    },
    "juani-island": {
        "hero": "https://www.tanzaniatourism.com/images/uploads/Kua_Ruins_Mosque_Mafia_2_2018.jpg",
        "gallery": [
            "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Hidden_Lagoon.jpg",
        ],
    },
}


def fname_from_url(url: str) -> str:
    return Path(url.split("?", 1)[0]).name


def local_ref(slug: str, url: str) -> str:
    return f"external/tt/{slug}-{fname_from_url(url)}"


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 2000:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            data = resp.read()
        if len(data) < 500:
            print(f"  WARN small: {dest.name} ({len(data)} bytes)")
            return False
        dest.write_bytes(data)
        print(f"  saved {dest.name} ({len(data) // 1024} KB)")
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"  FAIL {url}: {exc}")
        return False


def mirror(slug: str, url: str) -> str | None:
    if not url.startswith("http"):
        return url if url else None
    fname = fname_from_url(url)
    dest = TT_DIR / f"{slug}-{fname}"
    if download(url, dest):
        return local_ref(slug, url)
    return None


def main():
    core = json.loads(CORE.read_text(encoding="utf-8"))
    by_slug = {d["slug"]: d for d in core["destinations"]}
    downloaded = 0

    for slug, cfg in DEST_IMAGES.items():
        dest = by_slug.get(slug)
        if not dest:
            continue
        hero_url = cfg["hero"]
        hero_local = mirror(slug, hero_url)
        if hero_local:
            dest["hero"] = hero_local
            downloaded += 1
        gallery_locals = []
        for i, gurl in enumerate(cfg.get("gallery", [])):
            gslug = slug if i == 0 else f"{slug}-g{i}"
            glocal = mirror(gslug, gurl)
            if glocal and glocal not in gallery_locals and glocal != hero_local:
                gallery_locals.append(glocal)
        if gallery_locals:
            dest["gallery"] = gallery_locals[:4]

    # Mirror all Mafia circuit package heroes
    for p in core["packages"]:
        if p.get("circuit") != "Mafia Island":
            continue
        hero = p.get("hero", "")
        if not hero.startswith("http"):
            continue
        slug = p["slug"]
        local = mirror(slug, hero)
        if local:
            p["hero"] = local
            downloaded += 1

    # Fix chole-island-tour package hero (was wrongly aliased to mafia hero file)
    chole_pkg = next((p for p in core["packages"] if p["slug"] == "chole-island-tour"), None)
    if chole_pkg:
        url = "https://www.tanzaniatourism.com/images/uploads/Mafia_Island_Chole_Mjini.jpg"
        local = mirror("chole-island-tour", url)
        if local:
            chole_pkg["hero"] = local

    core["destinations"] = sorted(by_slug.values(), key=lambda d: (d["circuit"], d["name"]))
    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Mafia images updated ({downloaded} assets mirrored)")


if __name__ == "__main__":
    main()
