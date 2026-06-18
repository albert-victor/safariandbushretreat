#!/usr/bin/env python3
"""Remove Serengeti/footer pollution from packages and destination copy in tanzania-core.json."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"
ASSETS = ROOT / "assets"
IMAGES = ROOT / "assets" / "images"

FOOTER_HIGHLIGHTS = frozenset({
    "Serengeti National Park",
    "Mount Kilimanjaro National Park",
    "Arusha National Park",
    "Lake Manyara National Park",
})
FOOTER_DEST_SLUGS = frozenset({
    "serengeti", "kilimanjaro", "arusha", "lake-manyara",
    "ngorongoro", "tarangire", "nyerere", "lake-natron",
})

LOCAL_IMAGE_COPIES = {
    "pemba island.jpg": "pemba-island.jpg",
    "prison island main.jpg": "prison-island.jpg",
    "prison island.jpg": "prison-island-alt.jpg",
    "scuba diving.jpg": "scuba-diving-zanzibar.jpg",
}

PACKAGE_HERO_OVERRIDES = {
    "scuba-diving-in-zanzibar": "scuba-diving-zanzibar.jpg",
    "prison-island-zanzibar": "prison-island.jpg",
    "nungwi-experience": "external/tt/zanzibar-g1-Zanzibar_Prestine_Beach_04.jpg",
}

DESTINATION_HERO_OVERRIDES = {
    "pemba": "pemba-island.jpg",
    "prison-island": "prison-island.jpg",
}

PEMBA_COPY = {
    "card_desc": (
        "Pemba Island - spice plantations, pristine reefs and quiet Swahili villages "
        "in the Zanzibar archipelago north of Unguja."
    ),
    "paragraphs": [
        "Pemba Island lies north of Zanzibar (Unguja) in the Zanzibar Archipelago. "
        "Known as the Green Island for its lush clove plantations and hilly interior, "
        "it offers a slower pace than Stone Town with excellent diving and snorkelling.",
        "Pemba's reefs include Misali Island and surrounding channels rated among "
        "East Africa's best dive sites. Visitors explore spice farms, dhow harbours "
        "and fishing villages while basing in Chake Chake or smaller coastal lodges.",
    ],
}

PRISON_ISLAND_COPY = {
    "card_desc": (
        "Prison Island (Changuu) - giant Aldabra tortoises, snorkelling and a short "
        "dhow ride from Stone Town."
    ),
    "paragraphs": [
        "Prison Island, also known as Changuu, sits off Stone Town on Zanzibar's west coast. "
        "A short boat ride brings you to giant Aldabra tortoises, turquoise shallows "
        "and the ruins of a 19th-century prison that never held inmates.",
        "Half-day trips combine tortoise viewing with snorkelling on nearby reefs. "
        "The island is a popular add-on after a Stone Town walking tour.",
    ],
}


def copy_local_images() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    for src_name, dest_name in LOCAL_IMAGE_COPIES.items():
        src = ASSETS / src_name
        if src.exists():
            shutil.copy2(src, IMAGES / dest_name)
            print(f"  copied {src_name} -> images/{dest_name}")


def highlights_polluted(highlights: list | None) -> bool:
    return bool(highlights) and FOOTER_HIGHLIGHTS.issubset(set(highlights))


def dest_slugs_polluted(slugs: list | None) -> bool:
    if not slugs or len(slugs) < 4:
        return False
    return len(FOOTER_DEST_SLUGS.intersection(slugs)) >= 4


def serengeti_boilerplate(text: str) -> bool:
    return "Serengeti National Park is undoubtedly" in text


def infer_highlights(p: dict, dest_by_slug: dict) -> list[str]:
    name = p.get("name", "")
    overview = (p.get("overview") or "").lower()
    nlower = name.lower()
    out: list[str] = []

    keyword_rules = [
        (("snorkel", "snorkelling"), "Snorkelling"),
        (("scuba", "diving", "dive"), "Scuba diving"),
        (("nungwi",), "Nungwi village & beaches"),
        (("mnemba",), "Mnemba Atoll"),
        (("prison", "changuu", "tortoise"), "Giant tortoise visit"),
        (("stone town",), "Stone Town tour"),
        (("spice",), "Spice tour"),
        (("dhow", "sunset cruise"), "Dhow cruise"),
        (("dolphin",), "Dolphin watching"),
        (("whale shark",), "Whale shark snorkelling"),
        (("kilimanjaro", "climb", "trek", "summit"), "Mountain trekking"),
        (("meru",), "Mount Meru hike"),
        (("gorilla",), "Gorilla trekking"),
        (("chimp",), "Chimpanzee tracking"),
        (("cultural", "village", "museum", "ruins", "fort", "cave"), "Cultural sightseeing"),
        (("beach", "island", "sandbank"), "Beach & island time"),
        (("fish",), "Deep-sea fishing"),
        (("safari", "game drive"), "Game drives"),
        (("crater",), "Ngorongoro Crater"),
        (("balloon",), "Hot-air balloon"),
        (("hike", "hiking", "waterfall"), "Guided hiking"),
    ]
    blob = f"{nlower} {overview}"
    for keys, label in keyword_rules:
        if any(k in blob for k in keys) and label not in out:
            out.append(label)

    for slug in p.get("destinationSlugs") or []:
        if slug in FOOTER_DEST_SLUGS and len(p.get("destinationSlugs") or []) > 2:
            continue
        dname = dest_by_slug.get(slug, {}).get("name")
        if dname and dname not in out:
            out.append(dname)

    if not out and p.get("destinations"):
        out = [d for d in p["destinations"] if d not in FOOTER_HIGHLIGHTS][:4]

    if not out:
        circuit = p.get("circuit", "")
        out = [circuit] if circuit else [name]

    return out[:6]


def sanitize_destinations(slugs: list, names: list, dest_by_slug: dict) -> tuple[list[str], list[str]]:
    if not dest_slugs_polluted(slugs):
        return names, slugs
    clean_slugs: list[str] = []
    clean_names: list[str] = []
    for slug, name in zip(slugs, names):
        if slug in FOOTER_DEST_SLUGS and len(slugs) >= 4:
            continue
        if slug not in clean_slugs:
            clean_slugs.append(slug)
            clean_names.append(name or dest_by_slug.get(slug, {}).get("name", slug))
    return clean_names, clean_slugs


def fix_destination(d: dict) -> bool:
    changed = False
    slug = d["slug"]
    text_blob = " ".join(d.get("paragraphs") or []) + d.get("card_desc", "")
    if slug != "serengeti" and serengeti_boilerplate(text_blob):
        if slug == "pemba":
            d.update(PEMBA_COPY)
        elif slug == "prison-island":
            d.update(PRISON_ISLAND_COPY)
        else:
            d["paragraphs"] = [d.get("card_desc") or f"Discover {d['name']} with Safari and Bush Retreats."]
        d["shortDescription"] = d["card_desc"]
        changed = True

    if slug in DESTINATION_HERO_OVERRIDES:
        hero = DESTINATION_HERO_OVERRIDES[slug]
        if d.get("hero") != hero:
            d["hero"] = hero
            changed = True
    return changed


def fix_package(p: dict, dest_by_slug: dict) -> bool:
    changed = False

    names, slugs = sanitize_destinations(
        p.get("destinationSlugs") or [],
        p.get("destinations") or [],
        dest_by_slug,
    )
    if slugs != p.get("destinationSlugs"):
        p["destinationSlugs"] = slugs
        p["destinations"] = names
        changed = True
        primary = dest_by_slug.get(slugs[0], {}) if slugs else {}
        if primary.get("circuit"):
            p["circuit"] = primary["circuit"]

    if highlights_polluted(p.get("highlights")):
        p["highlights"] = infer_highlights(p, dest_by_slug)
        changed = True

    if highlights_polluted(p.get("activities")) or not p.get("activities"):
        p["activities"] = p.get("highlights", [])
        changed = True

    slug = p.get("slug", "")
    if slug in PACKAGE_HERO_OVERRIDES and p.get("hero") != PACKAGE_HERO_OVERRIDES[slug]:
        p["hero"] = PACKAGE_HERO_OVERRIDES[slug]
        changed = True

    return changed


def sync_nested_package_heroes(core: dict) -> int:
    by_slug = {p["slug"]: p for p in core["packages"]}
    n = 0
    for d in core["destinations"]:
        for pkg in d.get("packages") or []:
            master = by_slug.get(pkg.get("slug", ""))
            if not master:
                continue
            hero = master.get("hero", "")
            if hero and pkg.get("hero") != hero:
                pkg["hero"] = hero
                n += 1
    return n


def main() -> None:
    print("Copying local image assets...")
    copy_local_images()

    core = json.loads(CORE.read_text(encoding="utf-8"))
    dest_by_slug = {d["slug"]: d for d in core["destinations"]}

    dest_fixed = sum(1 for d in core["destinations"] if fix_destination(d))
    pkg_fixed = sum(1 for p in core["packages"] if fix_package(p, dest_by_slug))
    nested = sync_nested_package_heroes(core)

    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Fixed {dest_fixed} destinations")
    print(f"Fixed {pkg_fixed} packages (highlights/destinations/heroes)")
    print(f"Synced {nested} nested destination package heroes")


if __name__ == "__main__":
    main()
