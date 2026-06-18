#!/usr/bin/env python3
"""Sync destination circuit assignments from tanzaniatourism.com circuit listing pages."""
from __future__ import annotations

import json
import re
import time
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "destinations.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

CIRCUIT_PAGES = [
    ("Northern Circuit", "https://www.tanzaniatourism.com/destinations/northern-circuit"),
    ("Southern Circuit", "https://www.tanzaniatourism.com/destinations/southern-circuit"),
    ("Eastern Circuit", "https://www.tanzaniatourism.com/destinations/eastern-circuit"),
    ("Western Circuit", "https://www.tanzaniatourism.com/destinations/western-circuit"),
    ("Coastal & Islands", "https://www.tanzaniatourism.com/destinations/ocean-islands"),
    ("Coastal & Islands", "https://www.tanzaniatourism.com/destinations/zanzibar-island"),
]

LABEL_TO_CIRCUIT = {
    "Northern Circuit": "Northern Circuit",
    "Southern Circuit": "Southern Circuit",
    "Eastern Circuit": "Eastern Circuit",
    "Western Circuit": "Western Circuit",
    "Central Circuit": "Central Circuit",
    "Ocean Islands": "Coastal & Islands",
    "Zanzibar Island": "Coastal & Islands",
}

SLUG_MAP = {
    "serengeti-national-park": "serengeti",
    "mount-kilimanjaro-national-park": "kilimanjaro",
    "arusha-national-park": "arusha",
    "lake-manyara-national-park": "lake-manyara",
    "ngorongoro-crater": "ngorongoro",
    "ngorongoro-conservation-area": "ngorongoro",
    "tarangire-national-park": "tarangire",
    "mount-oldoinyo-lengai": "oldonyo-lengai",
    "kondoa-rock-art-sites": "kondoa-rock-art",
    "igeleke-rock-art-site": "igelegke-rock-art",
    "udzungwa-mountains-park": "udzungwa",
    "gombe-stream-national-park": "gombe",
    "mahale-mountains-national-park": "mahale",
    "zanzibar-island": "zanzibar",
    "pemba-island": "pemba",
    "mafia-island": "mafia",
    "prison-island-changuu": "prison-island",
    "mnazi-bay-ruvuma-estuary-marine-park": "mnazi-bay",
    "isimila-stone-age-site": "isimila",
    "mikumi-national-park": "mikumi",
    "bagamoyo-historical-town": "bagamoyo",
    "mbudya-island-marine-reserve": "mbudya-island",
    "bongoyo-island-marine-reserve": "bongoyo-island",
    "pangavini-island-marine-reserve": "pangavini-island",
    "chumbe-island-marine-sanctuary": "chumbe-island",
    "mnemba-island-conservation-area": "mnemba-island",
    "tanga-marine-park-and-reserves": "tanga-marine",
    "usambara-mountains": "usambara",
    "amani-nature-forest-reserves": "amani-forest",
    "amboni-caves": "amboni-caves",
    "uluguru-mountains": "uluguru",
    "pugu-kazimzumbwi-nature-forest-reserve": "pugu-kazimzumbwi",
    "kilwa-kisiwani": "kilwa-kisiwani",
    "kilwa-kivinje": "kilwa-kivinje",
    "songo-mnara": "songo-mnara",
    "pangani": "pangani",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", errors="replace")


def tt_slug_to_slug(tt_slug: str) -> str:
    if tt_slug in SLUG_MAP:
        return SLUG_MAP[tt_slug]
    s = tt_slug
    for suffix in ("-national-park", "-conservation-area", "-marine-reserve", "-marine-sanctuary"):
        s = s.replace(suffix, "")
    return s


def parse_listing(html: str, page_circuit: str) -> tuple[dict[str, str], dict[str, str]]:
    """Return (slug->circuit, slug->tt_slug) from cards. Card label is authoritative."""
    circuits: dict[str, str] = {}
    tt_slugs: dict[str, str] = {}
    blocks = re.findall(
        r'href="https://www\.tanzaniatourism\.com/destination/([^"]+)" class="hotelsCard[^"]*" title="([^"]+)"'
        r'(.*?)</a>',
        html,
        re.S,
    )
    for tt_slug, title, body in blocks:
        slug = tt_slug_to_slug(tt_slug)
        tt_slugs[slug] = tt_slug
        label_m = re.search(
            r'<p class="text-light-1[^"]*">\s*([^|<]+?)\s*\|',
            body,
        )
        label = unescape(label_m.group(1).strip()) if label_m else page_circuit
        circuit = LABEL_TO_CIRCUIT.get(label, page_circuit)
        if circuit == "Central Circuit":
            continue
        if slug not in circuits:
            circuits[slug] = circuit
    return circuits, tt_slugs


def main():
    all_circuits: dict[str, str] = {}
    all_tt: dict[str, str] = {}

    for page_circuit, url in CIRCUIT_PAGES:
        print(f"Fetching {url} …")
        html = fetch(url)
        circuits, tt_slugs = parse_listing(html, page_circuit)
        for slug, circuit in circuits.items():
            if slug not in all_circuits:
                all_circuits[slug] = circuit
        all_tt.update(tt_slugs)
        print(f"  {len(circuits)} cards on page")
        time.sleep(0.4)

    data = json.loads(DATA.read_text(encoding="utf-8"))
    by_slug = {d["slug"]: d for d in data["destinations"]}
    updated = 0
    missing = []

    for slug, circuit in sorted(all_circuits.items()):
        if slug in by_slug:
            if by_slug[slug]["circuit"] != circuit:
                print(f"  {slug}: {by_slug[slug]['circuit']} -> {circuit}")
                by_slug[slug]["circuit"] = circuit
                updated += 1
            if slug in all_tt:
                by_slug[slug]["tt_slug"] = all_tt[slug]
        else:
            missing.append((slug, circuit, all_tt.get(slug, slug)))

    data["destinations"] = sorted(by_slug.values(), key=lambda d: (d["circuit"], d["name"]))
    data["circuit_assignments"] = all_circuits
    data["missing_from_site"] = [{"slug": s, "circuit": c, "tt_slug": t} for s, c, t in missing]
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nUpdated {updated} assignments. Missing {len(missing)} destinations to scrape.")


if __name__ == "__main__":
    main()
