#!/usr/bin/env python3
"""Expand tanzania-core.json with TT destinations, fix image assignments, mirror heroes."""
from __future__ import annotations

import importlib.util
import json
import re
import time
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"
TT_DIR = ROOT / "assets" / "images" / "external" / "tt"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

CIRCUIT_PAGES = [
    ("Northern Circuit", "https://www.tanzaniatourism.com/destinations/northern-circuit"),
    ("Southern Circuit", "https://www.tanzaniatourism.com/destinations/southern-circuit"),
    ("Eastern Circuit", "https://www.tanzaniatourism.com/destinations/eastern-circuit"),
    ("Western Circuit", "https://www.tanzaniatourism.com/destinations/western-circuit"),
    ("Oceanic Islands", "https://www.tanzaniatourism.com/destinations/ocean-islands"),
    ("Oceanic Islands", "https://www.tanzaniatourism.com/destinations/zanzibar-island"),
]

LABEL_TO_CIRCUIT = {
    "Northern Circuit": "Northern Circuit",
    "Southern Circuit": "Southern Circuit",
    "Eastern Circuit": "Eastern Circuit",
    "Western Circuit": "Western Circuit",
    "Ocean Islands": "Oceanic Islands",
    "Zanzibar Island": "Oceanic Islands",
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
    "gangilonga-rock": "gangilonga",
    "mpanga-kipengere-game-controlled-area": "mpanga-kipengere",
    "nyerere-national-park": "nyerere",
    "kitulo-national-park": "kitulo",
    "katavi-national-park": "katavi",
    "ruaha-national-park": "ruaha",
    "saadani-national-park": "saadani",
    "lake-eyasi": "lake-eyasi",
    "mkomazi-national-park": "mkomazi",
    "rubondo-island-national-park": "rubondo",
    "saanane-island-national-park": "saanane",
    "burigi-chato-national-park": "burigi-chato",
    "ibanda-kyerwa-national-park": "ibanda-kyerwa",
    "lake-tanganyika": "lake-tanganyika",
    "ukerewe-island": "ukerewe",
}

# Prefer dedicated local files when present in assets/images
LOCAL_HERO_MAP: dict[str, str] = {
    "mpanga-kipengere": "MPANGA KIPENGERE.jpg",
    "mikumi": "mikumi2.jpg",
    "nyerere": "nyerere park hero image.jpg",
    "kitulo": "kitulo park hero image.jpg",
    "gangilonga": "Gangilonga_Rock_Iringa_3.jpg",
    "isimila": "Isimila-Stone-Age-Site-and-Natural-Pillars-in-Iringa.jpg",
    "bagamoyo": "Ruins_of_Old_Port_in_Bagamoyo_02.jpg",
    "oldonyo-lengai": "Mount_Oldonyo_Lengai_12.jpg",
    "arusha": "arusha national park.jpg",
}

LOCAL_GALLERY_MAP: dict[str, list[str]] = {
    "lake-eyasi": ["masai.jpg", "culture tours.jpg"],
    "mpanga-kipengere": ["mpanga kipengere2.jpg", "mpanga kipengere3.jpg"],
    "mikumi": ["mikumi park.jpg", "mikumi.jpg"],
    "nyerere": ["nyerere national park2.jpg", "nyerere park3.jpg"],
    "kitulo": ["kitulo park.jpg", "kitulo park2.jpg"],
    "gangilonga": ["culture tours4.jpg", "bachelor-of-arts-in-tourism-and-cultural-heritage-in-tanzania.jpg"],
    "isimila": ["culture tours3.jpg", "culture tours.jpg"],
    "bagamoyo": ["bagamoyo1.jpg", "bagamoyo2.jpg"],
}

CIRCUIT_INTROS = {
    "Northern Circuit": [
        "Tanzania's flagship safari corridor - endless plains, volcanic craters and Africa's highest peak, all within reach of Arusha and Kilimanjaro International Airport.",
    ],
    "Southern Circuit": [
        "Remote, uncrowded wilderness in Ruaha, Mikumi, Udzungwa and Nyerere - authentic safaris away from the northern crowds, ideal from Dar es Salaam or Iringa.",
    ],
    "Western Circuit": [
        "Tanzania's remotest frontier on Lake Tanganyika - Katavi's vast floodplains, Mahale's chimpanzees and Gombe's forest trails.",
    ],
    "Oceanic Islands": [
        "Oceanic Islands brings together Indian Ocean marine reserves, sandbars and conservation areas along the Swahili coast - from boat day trips off Dar es Salaam to Chumbe and Mnemba.",
        "Snorkel coral gardens, picnic on uninhabited sandbars and explore protected reefs where sea turtles, reef fish and dolphins thrive along the Swahili coast.",
    ],
    "Mafia Island": [
        "Tanzania's best-kept marine secret - whale sharks, world-class diving, Chole Bay and the Mafia archipelago, reached by light aircraft from Dar es Salaam or Zanzibar.",
    ],
    "Southern Highlands & Culture": [
        "The highlands around Iringa and Njombe - ancient rock art, archaeological sites and dramatic escarpments where Tanzania's human story began.",
    ],
    "Eastern Circuit": [
        "Rainforest hiking, bush-beach safaris and Swahili history - Saadani, Usambara, Udzungwa, Bagamoyo and the historic Kilwa coast.",
    ],
}

# Keep canonical circuit for core destinations (user spec overrides TT card labels)
CANONICAL_CIRCUIT = {
    "mikumi": "Southern Circuit",
    "udzungwa": "Southern Circuit",
    "nyerere": "Southern Circuit",
    "gangilonga": "Southern Highlands & Culture",
    "isimila": "Southern Highlands & Culture",
    "mpanga-kipengere": "Southern Circuit",
}

MAFIA_SLUGS = {
    "mafia", "chole-island", "bwejuu-island", "jibondo-island", "juani-island", "chole-bay",
}
for _s in MAFIA_SLUGS:
    CANONICAL_CIRCUIT[_s] = "Mafia Island"

OCEAN_CIRCUIT_SLUGS = {
    "zanzibar", "pemba", "prison-island", "chumbe-island", "mnemba-island",
    "mbudya-island", "bongoyo-island", "pangavini-island", "maziwe-island", "kirui-island",
    "kwale-island", "sinda-island", "toten-island", "ulenge-island", "yambe-island",
    "mwewe-island", "fungu-yasin-sand-bar",
    "kilwa", "kilwa-kisiwani", "kilwa-kivinje", "songo-mnara",
}
for _s in OCEAN_CIRCUIT_SLUGS:
    CANONICAL_CIRCUIT[_s] = "Oceanic Islands"

spec = importlib.util.spec_from_file_location("sc", ROOT / "scripts" / "scrape-tourism-content.py")
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


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


def parse_listing(html: str, page_circuit: str) -> dict[str, tuple[str, str]]:
    """slug -> (circuit, tt_slug)"""
    out: dict[str, tuple[str, str]] = {}
    blocks = re.findall(
        r'href="https://www\.tanzaniatourism\.com/destination/([^"]+)" class="hotelsCard[^"]*" title="([^"]+)"'
        r'(.*?)</a>',
        html,
        re.S,
    )
    for tt_slug, _title, body in blocks:
        slug = tt_slug_to_slug(tt_slug)
        label_m = re.search(r'<p class="text-light-1[^"]*">\s*([^|<]+?)\s*\|', body)
        label = unescape(label_m.group(1).strip()) if label_m else page_circuit
        circuit = LABEL_TO_CIRCUIT.get(label, page_circuit)
        if circuit == "Central Circuit":
            continue
        if slug in CANONICAL_CIRCUIT:
            circuit = CANONICAL_CIRCUIT[slug]
        if slug not in out:
            out[slug] = (circuit, tt_slug)
    return out


def download_tt_hero(url: str, slug: str) -> str:
    if not url.startswith("http"):
        return url
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(url.split("?")[0]).name).strip("-") or f"{slug}.jpg"
    dest = TT_DIR / f"{slug}-{name}"
    if not dest.exists() or dest.stat().st_size < 500:
        TT_DIR.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            if len(data) > 500:
                dest.write_bytes(data)
                print(f"  downloaded {dest.name}")
        except OSError as exc:
            print(f"  FAIL download {slug}: {exc}")
            return url
    return f"external/tt/{dest.name}"


def local_exists(rel: str) -> bool:
    return (ROOT / "assets" / "images" / rel).exists()


def assign_images(entry: dict) -> dict:
    slug = entry["slug"]
    if slug in LOCAL_HERO_MAP and local_exists(LOCAL_HERO_MAP[slug]):
        entry["hero"] = LOCAL_HERO_MAP[slug]
    elif entry.get("hero", "").startswith("http"):
        entry["hero"] = download_tt_hero(entry["hero"], slug)
    if slug in LOCAL_GALLERY_MAP:
        entry["gallery"] = [g for g in LOCAL_GALLERY_MAP[slug] if local_exists(g)][:2]
    elif entry.get("gallery"):
        entry["gallery"] = [
            download_tt_hero(g, f"{slug}-g{i}") if g.startswith("http") else g
            for i, g in enumerate(entry["gallery"][:2])
        ]
    return entry


def scraped_to_core(raw: dict) -> dict:
    paras = raw.get("paragraphs", [])
    card = raw.get("card_desc", "")
    return {
        "slug": raw["slug"],
        "name": raw["name"],
        "circuit": raw["circuit"],
        "badge": raw.get("badge", "Explore"),
        "meta": raw.get("meta", raw["circuit"]),
        "card_desc": card,
        "shortDescription": card[:200],
        "hero": raw.get("hero", ""),
        "gallery": raw.get("gallery", [])[:2],
        "keyAttractions": [],
        "activities": [],
        "bestTime": "Year-round - enquire for seasonal highlights",
        "duration": "1 - 3 days recommended",
        "entryCost": "Park fees vary - contact us for current rates",
        "paragraphs": paras[:3] if paras else [card],
        "relatedPackages": [],
        "tt_slug": raw.get("tt_slug", raw["slug"]),
    }


def enrich_from_scrape(entry: dict, raw: dict) -> None:
    """Fill empty fields on existing entries without overwriting rich content."""
    for key in ("meta", "card_desc", "shortDescription", "paragraphs"):
        if not entry.get(key) and raw.get(key if key != "shortDescription" else "card_desc"):
            val = raw.get(key if key != "shortDescription" else "card_desc")
            if key == "paragraphs":
                entry[key] = val[:3]
            else:
                entry[key] = val[:200] if key == "shortDescription" else val
    if not entry.get("hero") and raw.get("hero"):
        entry["hero"] = raw["hero"]
    if not entry.get("gallery") and raw.get("gallery"):
        entry["gallery"] = raw["gallery"][:2]


def main():
    listings: dict[str, tuple[str, str]] = {}
    for page_circuit, url in CIRCUIT_PAGES:
        print(f"Listing {url}")
        html = fetch(url)
        listings.update(parse_listing(html, page_circuit))
        time.sleep(0.35)
    print(f"Found {len(listings)} unique TT destinations")

    core = json.loads(CORE.read_text(encoding="utf-8"))
    by_slug = {d["slug"]: d for d in core["destinations"]}
    added = 0

    for slug, (circuit, tt_slug) in sorted(listings.items()):
        if slug in by_slug:
            if slug in CANONICAL_CIRCUIT:
                by_slug[slug]["circuit"] = CANONICAL_CIRCUIT[slug]
            elif by_slug[slug].get("circuit") != circuit and slug not in CANONICAL_CIRCUIT:
                pass  # preserve enriched circuit unless TT-only new
            assign_images(by_slug[slug])
            continue

        print(f"Scraping new: {slug}")
        raw = sc.scrape_one(slug, tt_slug, circuit)
        if not raw:
            continue
        raw["circuit"] = CANONICAL_CIRCUIT.get(slug, circuit)
        entry = scraped_to_core(raw)
        entry = assign_images(entry)
        by_slug[slug] = entry
        added += 1
        time.sleep(0.5)

    # Re-assign images for all existing canonical entries
    for slug, entry in by_slug.items():
        assign_images(entry)

    core["circuits"] = CIRCUIT_INTROS
    core["destinations"] = sorted(by_slug.values(), key=lambda d: (d["circuit"], d["name"]))
    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    circuits_count: dict[str, int] = {}
    for d in core["destinations"]:
        circuits_count[d["circuit"]] = circuits_count.get(d["circuit"], 0) + 1
    print(f"\nAdded {added} destinations. Total {len(core['destinations'])}")
    for c, n in sorted(circuits_count.items()):
        print(f"  {c}: {n}")


if __name__ == "__main__":
    main()
