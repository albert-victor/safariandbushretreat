#!/usr/bin/env python3
"""Rename Zanzibar & Islands to Oceanic Islands; enrich Zanzibar from TT; mirror images."""
from __future__ import annotations

import importlib.util
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

OLD_CIRCUIT = "Zanzibar & Islands"
NEW_CIRCUIT = "Oceanic Islands"

OCEAN_INTRO = (
    "Oceanic Islands brings together Indian Ocean marine reserves, sandbars and "
    "conservation areas - from boat day trips off Dar es Salaam to Chumbe and Mnemba near Zanzibar."
)

# All destinations billed under Oceanic Islands circuit in package data
OCEAN_CIRCUIT_SLUGS = {
    "zanzibar", "pemba", "prison-island", "chumbe-island", "mnemba-island",
    "mbudya-island", "bongoyo-island", "pangavini-island", "maziwe-island", "kirui-island",
    "kwale-island", "sinda-island", "toten-island", "ulenge-island", "yambe-island",
    "mwewe-island", "fungu-yasin-sand-bar",
    "kilwa", "kilwa-kisiwani", "kilwa-kivinje", "songo-mnara",
}

ZANZIBAR_ATTRACTIONS = [
    "UNESCO Stone Town",
    "Spice plantation tours",
    "Nungwi & Kendwa beaches",
    "Jozani Chwaka Bay National Park",
    "Prison Island giant tortoises",
    "Forodhani night food market",
]

ZANZIBAR_ACTIVITIES = [
    "Stone Town walking tours",
    "Spice farm visits",
    "Snorkelling & scuba diving",
    "Dhow sunset cruises",
    "Safari Blue sailing",
    "Dolphin tours",
    "Deep sea fishing",
]

spec = importlib.util.spec_from_file_location("sc", ROOT / "scripts" / "scrape-tourism-content.py")
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


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
            return False
        dest.write_bytes(data)
        print(f"  saved {dest.name}")
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"  FAIL {url}: {exc}")
        return False


def mirror(slug: str, url: str) -> str | None:
    if not url or not url.startswith("http"):
        return url or None
    fname = Path(url.split("?", 1)[0]).name
    dest = TT_DIR / f"{slug}-{fname}"
    if download(url, dest):
        return f"external/tt/{slug}-{fname}"
    return None


def enrich_zanzibar(dest: dict) -> None:
    raw = sc.scrape_one("zanzibar", "zanzibar-island", NEW_CIRCUIT)
    if not raw:
        return
    if raw.get("paragraphs"):
        dest["paragraphs"] = raw["paragraphs"]
        dest["card_desc"] = raw["card_desc"]
        dest["shortDescription"] = raw["card_desc"]
    dest["keyAttractions"] = ZANZIBAR_ATTRACTIONS
    dest["activities"] = ZANZIBAR_ACTIVITIES
    if raw.get("faqs"):
        dest["faqs"] = raw["faqs"]
    hero_url = raw.get("hero", "")
    if hero_url.startswith("http"):
        local = mirror("zanzibar", hero_url)
        if local:
            dest["hero"] = local
    gallery = []
    for i, gurl in enumerate(raw.get("gallery") or []):
        if not gurl.startswith("http"):
            continue
        glocal = mirror(f"zanzibar-g{i}", gurl)
        if glocal and glocal != dest.get("hero"):
            gallery.append(glocal)
    if gallery:
        dest["gallery"] = gallery[:4]
    # TT gallery fallback images
    for i, url in enumerate([
        "https://www.tanzaniatourism.com/images/uploads/Zanzibar_Island_Stone_Town_01.jpg",
        "https://www.tanzaniatourism.com/images/uploads/Zanzibar_Island_Spice_Tour_01.jpg",
        "https://www.tanzaniatourism.com/images/uploads/Zanzibar_Island_Nungwi_Beach_01.jpg",
    ]):
        if len(dest.get("gallery", [])) >= 4:
            break
        glocal = mirror(f"zanzibar-g{len(dest.get('gallery', []))}", url)
        if glocal and glocal not in dest.get("gallery", []) and glocal != dest.get("hero"):
            dest.setdefault("gallery", []).append(glocal)


def enrich_pemba(dest: dict) -> None:
    raw = sc.scrape_one("pemba", "pemba-island", NEW_CIRCUIT)
    if not raw:
        return
    if raw.get("paragraphs"):
        dest["paragraphs"] = raw["paragraphs"]
        dest["card_desc"] = raw["card_desc"]
        dest["shortDescription"] = raw["card_desc"]
    hero_url = raw.get("hero", "")
    if hero_url.startswith("http"):
        local = mirror("pemba", hero_url)
        if local:
            dest["hero"] = local


def main():
    core = json.loads(CORE.read_text(encoding="utf-8"))

    for legacy in (OLD_CIRCUIT, "Coastal & Islands", "Ocean Islands"):
        if legacy in core["circuits"]:
            del core["circuits"][legacy]
    core["circuits"][NEW_CIRCUIT] = [
        OCEAN_INTRO,
        "Snorkel coral gardens, picnic on uninhabited sandbars and explore protected reefs where sea turtles, reef fish and dolphins thrive along the Swahili coast.",
    ]

    for d in core["destinations"]:
        if d["slug"] in OCEAN_CIRCUIT_SLUGS or d.get("circuit") in (OLD_CIRCUIT, "Ocean Islands"):
            d["circuit"] = NEW_CIRCUIT

    for p in core["packages"]:
        if p.get("circuit") in (OLD_CIRCUIT, "Coastal & Islands", "Zanzibar Island"):
            p["circuit"] = NEW_CIRCUIT
        elif p.get("circuit") in ("Ocean Islands", "Oceanic Islands"):
            p["circuit"] = NEW_CIRCUIT

    by_slug = {d["slug"]: d for d in core["destinations"]}
    if "zanzibar" in by_slug:
        enrich_zanzibar(by_slug["zanzibar"])
    if "pemba" in by_slug:
        enrich_pemba(by_slug["pemba"])

    core["destinations"] = sorted(by_slug.values(), key=lambda d: (d["circuit"], d["name"]))
    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n_dests = sum(1 for d in core["destinations"] if d["circuit"] == NEW_CIRCUIT)
    n_pkgs = sum(1 for p in core["packages"] if p.get("circuit") == NEW_CIRCUIT)
    print(f"{NEW_CIRCUIT}: {n_dests} destinations, {n_pkgs} packages")


if __name__ == "__main__":
    main()
