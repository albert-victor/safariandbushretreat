#!/usr/bin/env python3
"""Build destinations.json and safari-packages.json from tanzania-core.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"
DEST_OUT = ROOT / "data" / "destinations.json"
PKG_OUT = ROOT / "data" / "safari-packages.json"
REG_OUT = ROOT / "data" / "image-registry.json"

CIRCUIT_ALIASES = {
    "Coastal & Islands": "Oceanic Islands",
    "Zanzibar & Islands": "Oceanic Islands",
    "Zanzibar Island": "Oceanic Islands",
    "Ocean Islands": "Oceanic Islands",
}


def normalize_circuit(name: str) -> str:
    return CIRCUIT_ALIASES.get(name, name)


PACKAGE_HERO = {
    "3-days-mikumi-safari": "mikumi park.jpg",
    "5-days-ruaha-safari": "baobab-trees-ruaha.jpg",
    "7-days-northern-circuit": "Serengeti-National-Park-1-1.jpg",
    "6-days-serengeti-ngorongoro": "serengeti.jpg",
    "kilimanjaro-machame-7": "mount kilimanjaro.jpg",
    "5-days-zanzibar-beach": "zanzibar.jpg",
    "10-days-southern-explorer": "ruaha_national_park_river_2.jpg",
    "western-primates-safari": "gombe-4.webp",
    "3-days-serengeti-ngorongoro": "ngorongoro-crater.jpg",
    "5-days-northern-classic": "serengeti3.jpg",
    "4-days-tarangire-manyara": "lake manyara.webp",
    "4-days-saadani-bush-beach": "external/tt/saadani-Saadani_National_Park_Hippos_29.jpg",
    "4-days-lake-eyasi-cultural": "external/tt/lake-eyasi-Lake_Eyasi_x_29.jpg",
    "6-days-katavi-wilderness": "external/tt/katavi-Katavi_National_Park_x_70.jpg",
}


def assign_package_heroes(core: dict) -> dict:
    dest_by_slug = {d["slug"]: d for d in core["destinations"]}
    used: set[str] = set()
    for p in core["packages"]:
        slug = p["slug"]
        if slug in PACKAGE_HERO:
            p["hero"] = PACKAGE_HERO[slug]
        hero = p.get("hero", "")
        if hero in used:
            for ds in p.get("destinationSlugs", []):
                candidate = dest_by_slug.get(ds, {}).get("hero", "")
                if candidate and candidate not in used:
                    p["hero"] = candidate
                    hero = candidate
                    break
        used.add(p["hero"])
    return core


def resolve_packages(core: dict) -> dict:
    by_slug = {p["slug"]: p for p in core["packages"]}
    dest_index: dict[str, list[str]] = {}
    for p in core["packages"]:
        for ds in p.get("destinationSlugs", []):
            dest_index.setdefault(ds, []).append(p["slug"])

    mafia_sub = {"chole-island", "bwejuu-island", "jibondo-island", "juani-island", "chole-bay"}

    for d in core["destinations"]:
        manual = d.get("relatedPackages", [])
        auto = dest_index.get(d["slug"], [])
        slugs = sorted(set(manual + auto))
        if d["slug"] == "mafia":
            slugs = [s for s in slugs if by_slug.get(s, {}).get("circuit") == "Mafia Island"]
        elif d["slug"] in mafia_sub:
            slugs = [s for s in slugs if by_slug.get(s, {}).get("circuit") == "Mafia Island"]
        d["relatedPackages"] = slugs
        d["packages"] = []
        for s in slugs:
            if s in by_slug:
                p = by_slug[s]
                d["packages"].append({
                    "name": p["name"],
                    "slug": p["slug"],
                    "days": p["days"],
                    "price": p["price"],
                    "hero": p.get("hero", ""),
                    "description": p["overview"][:180],
                })
    return core


def build_registry(core: dict) -> dict:
    used = {"destinations": {}, "packages": {}, "external": []}
    for d in core["destinations"]:
        hero = d["hero"]
        used["destinations"][d["slug"]] = {
            "hero": hero,
            "gallery": d.get("gallery", []),
            "source": "external" if hero.startswith("http") else "local",
        }
        if hero.startswith("http"):
            used["external"].append({"slug": d["slug"], "type": "destination-hero", "url": hero})
    for p in core["packages"]:
        hero = p["hero"]
        used["packages"][p["slug"]] = {
            "hero": hero,
            "source": "external" if hero.startswith("http") else "local",
        }
    return used


def to_legacy_destination(d: dict) -> dict:
    return {
        "slug": d["slug"],
        "name": d["name"],
        "circuit": d["circuit"],
        "badge": d["badge"],
        "meta": d["meta"],
        "card_desc": d["card_desc"],
        "hero": d["hero"],
        "gallery": d.get("gallery", [])[:4],
        "paragraphs": d.get("paragraphs", []),
        "shortDescription": d.get("shortDescription", d["card_desc"]),
        "keyAttractions": d.get("keyAttractions", []),
        "activities": d.get("activities", []),
        "bestTime": d.get("bestTime", ""),
        "duration": d.get("duration", ""),
        "entryCost": d.get("entryCost", ""),
        "packages": d.get("packages", []),
        "relatedPackages": d.get("relatedPackages", []),
        "faqs": d.get("faqs", []),
    }


def to_legacy_package(p: dict) -> dict:
    return {
        "slug": p["slug"],
        "name": p["name"],
        "circuit": normalize_circuit(p["circuit"]),
        "days": p["days"],
        "nights": p.get("nights"),
        "duration": p["duration"],
        "price": p["price"],
        "priceRange": p.get("priceRange", p["price"]),
        "overview": p["overview"],
        "highlights": p.get("highlights", []),
        "activities": p.get("activities") or p.get("highlights", []),
        "destinations": p.get("destinations", []),
        "destinationSlugs": p.get("destinationSlugs", []),
        "features": p.get("highlights", []),
        "itinerary": p.get("itinerary", []),
        "hero": p["hero"],
        "featured": p.get("featured", False),
    }


def main():
    core = json.loads(CORE.read_text(encoding="utf-8"))
    core = assign_package_heroes(core)
    core = resolve_packages(core)
    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    dest_data = {
        "source": "data/tanzania-core.json",
        "circuits": core["circuits"],
        "destinations": [to_legacy_destination(d) for d in core["destinations"]],
    }
    pkg_data = {
        "source": "data/tanzania-core.json",
        "packages": [to_legacy_package(p) for p in core["packages"]],
    }
    registry = build_registry(core)

    DEST_OUT.write_text(json.dumps(dest_data, indent=2, ensure_ascii=False), encoding="utf-8")
    PKG_OUT.write_text(json.dumps(pkg_data, indent=2, ensure_ascii=False), encoding="utf-8")
    REG_OUT.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")

    local_dest = sum(1 for v in registry["destinations"].values() if v["source"] == "local")
    ext_dest = sum(1 for v in registry["destinations"].values() if v["source"] == "external")
    print(f"Built {len(dest_data['destinations'])} destinations ({local_dest} local heroes, {ext_dest} external)")
    print(f"Built {len(pkg_data['packages'])} packages")
    print(f"Image registry -> {REG_OUT}")


if __name__ == "__main__":
    main()
