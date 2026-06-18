#!/usr/bin/env python3
"""Configure Mafia Island as a standalone circuit with sub-destinations and tours."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"

MAFIA_CIRCUIT = "Mafia Island"
OCEAN_INTRO = (
    "Indian Ocean archipelago - Zanzibar's Stone Town and spice coast, Pemba's clove "
    "islands, Kilwa's UNESCO ruins and Tanzania's marine reserves from Chumbe to Mnemba."
)
MAFIA_INTRO = (
    "Tanzania's best-kept marine secret - whale sharks, world-class diving, Chole Bay "
    "and the Mafia archipelago, reached by light aircraft from Dar es Salaam or Zanzibar."
)

MAFIA_DEST_SLUGS = {
    "mafia", "chole-island", "bwejuu-island", "jibondo-island", "juani-island", "chole-bay",
}

MAFIA_PACKAGE_SLUGS = {
    "2-5-days-mafia-island-holiday",
    "bwejuu-island-mafia",
    "chole-bay-snorkelling-mafia-island",
    "chole-island-tour",
    "day-trip-to-mafia-island",
    "deep-sea-fishing-mafia-island",
    "fisherman-island-mafia",
    "humpback-whale-watching",
    "jibondo-island-mafia",
    "kua-ruins-tour-mafia-island",
    "mafia-island-sunset-cruise",
    "mange-sandbank-mafia-island",
    "marimbani-sandbank-mafia",
    "scuba-diving-in-mafia-island",
    "turtle-hatchling-mafia-island",
    "visit-to-hidden-lagoon-mafia-island",
    "whale-sharks-snorkeling",
}

PACKAGE_DEST_MAP = {
    "chole-island-tour": ["mafia", "chole-island"],
    "bwejuu-island-mafia": ["mafia", "bwejuu-island"],
    "jibondo-island-mafia": ["mafia", "jibondo-island"],
    "kua-ruins-tour-mafia-island": ["mafia", "juani-island"],
    "chole-bay-snorkelling-mafia-island": ["mafia", "chole-bay"],
    "visit-to-hidden-lagoon-mafia-island": ["mafia", "juani-island"],
}

MAFIA_SUB_DESTINATIONS = [
    {
        "slug": "chole-island",
        "name": "Chole Island",
        "package_slug": "chole-island-tour",
        "badge": "Heritage",
        "keyAttractions": [
            "Historic Swahili ruins",
            "Mangrove forests and baobab groves",
            "Former archipelago capital",
        ],
        "activities": ["Island walking tour", "Village visits", "Bird watching"],
        "duration": "Half day",
    },
    {
        "slug": "chole-bay",
        "name": "Chole Bay & Marine Park",
        "package_slug": "chole-bay-snorkelling-mafia-island",
        "badge": "Marine Park",
        "keyAttractions": [
            "Mafia Island Marine Park (822 km²)",
            "400+ fish species and 50 coral types",
            "Sea turtle nesting beaches",
        ],
        "activities": ["Snorkelling", "Scuba diving", "Whale shark swimming", "Dhow cruises"],
        "duration": "2 - 5 days recommended",
        "bestTime": "Oct - Feb (best visibility) · Jun - Sep (coolest)",
    },
    {
        "slug": "bwejuu-island",
        "name": "Bwejuu Island",
        "package_slug": "bwejuu-island-mafia",
        "badge": "Coastal",
        "keyAttractions": [
            "Pristine fringing reef",
            "Barracuda schools",
            "Secluded sandbanks",
        ],
        "activities": ["Snorkelling", "Diving", "Beach relaxation", "Boat excursions"],
        "duration": "Full day",
    },
    {
        "slug": "jibondo-island",
        "name": "Jibondo Island",
        "package_slug": "jibondo-island-mafia",
        "badge": "Culture",
        "keyAttractions": [
            "Traditional boat-building centre",
            "Historic mosque door frame from Kua",
            "Fishing village life",
        ],
        "activities": ["Village walks", "Bird watching", "Cultural encounters"],
        "duration": "Half day",
    },
    {
        "slug": "juani-island",
        "name": "Juani Island",
        "package_slug": "kua-ruins-tour-mafia-island",
        "badge": "Heritage",
        "keyAttractions": [
            "Kua ruins (11th-century settlement)",
            "Hidden Blue Lagoon",
            "Coral reef protection for Chole Bay",
        ],
        "activities": ["Ruins tour", "Lagoon visits", "Snorkelling"],
        "duration": "Half day",
    },
]

MAFIA_KEY_ATTRACTIONS = [
    "Mafia Island Marine Park",
    "Chole Bay anchorage",
    "Kua ruins on Juani Island",
    "Whale shark migration (Oct - Feb)",
    "Historic trade-route antiquities",
]

MAFIA_ACTIVITIES = [
    "Scuba diving",
    "Snorkelling with whale sharks",
    "Deep sea fishing",
    "Dhow sunset cruises",
    "Island and ruins tours",
    "Sandbank excursions",
]

MAFIA_FAQS = [
    {
        "q": "How do you get to Mafia Island?",
        "a": "Light aircraft from Dar es Salaam or Zanzibar (Coastal Aviation and Auric Air offer multiple daily flights, approximately 30-50 minutes). Flights also connect from parks such as Nyerere National Park.",
    },
    {
        "q": "How far is Mafia Island from Zanzibar?",
        "a": "About 198 km by air. Flight time is roughly 30-40 minutes from Zanzibar or Dar es Salaam.",
    },
    {
        "q": "When is the best time to visit Mafia Island?",
        "a": "October to February offers the best underwater visibility and whale shark season. June to September is the coolest period. The island has two rainy seasons: November-December and March-May.",
    },
]

spec = importlib.util.spec_from_file_location("sc", ROOT / "scripts" / "scrape-tourism-content.py")
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


def local_hero(url: str, slug: str) -> str:
    if not url:
        return ""
    if url.startswith("external/"):
        return url
    m = re.search(r"/([^/]+\.(?:jpg|jpeg|png|webp))", url, re.I)
    if m:
        return f"external/tt/{slug}-{m.group(1)}"
    return url


def pkg_by_slug(packages: list) -> dict:
    return {p["slug"]: p for p in packages}


def build_sub_destination(cfg: dict, pkg: dict) -> dict:
    overview = pkg.get("overview", "")
    paras = [overview[:500]] if overview else [f"Explore {cfg['name']} in the Mafia archipelago."]
    hero = pkg.get("hero", "")
    if hero.startswith("http"):
        hero = local_hero(hero, cfg["slug"])
    gallery = [hero] if hero else []
    return {
        "slug": cfg["slug"],
        "name": cfg["name"],
        "circuit": MAFIA_CIRCUIT,
        "badge": cfg["badge"],
        "meta": f"{cfg['badge']} · {MAFIA_CIRCUIT}",
        "card_desc": overview[:200] if overview else cfg["name"],
        "shortDescription": overview[:200] if overview else cfg["name"],
        "hero": hero,
        "gallery": gallery,
        "keyAttractions": cfg.get("keyAttractions", []),
        "activities": cfg.get("activities", []),
        "bestTime": cfg.get("bestTime", "Year-round - enquire for seasonal highlights"),
        "duration": cfg.get("duration", "1 - 3 days recommended"),
        "entryCost": "Marine park fees vary - contact us for current rates",
        "paragraphs": paras,
        "relatedPackages": [cfg["package_slug"]],
        "tt_slug": cfg.get("tt_slug", cfg["slug"]),
        "packages": [],
        "faqs": [],
    }


def enrich_mafia(dest: dict, packages: dict) -> None:
    dest["circuit"] = MAFIA_CIRCUIT
    dest["keyAttractions"] = MAFIA_KEY_ATTRACTIONS
    dest["activities"] = MAFIA_ACTIVITIES
    dest["faqs"] = MAFIA_FAQS
    dest["bestTime"] = "Oct - Feb (whale sharks & visibility) · Jun - Sep (coolest)"
    extra = (
        "Surrounded by a protected marine park, the diving, fishing and snorkelling here are among "
        "the best in the region. Mafia is known for migratory whale sharks - spotting these gentle "
        "giants is an unforgettable experience. With over 50 coral types and 400 fish species, the "
        "archipelago offers one of the world's finest opportunities for snorkelling with whale sharks."
    )
    paras = dest.get("paragraphs", [])
    if extra not in " ".join(paras):
        paras.append(extra)
    dest["paragraphs"] = paras
    dest["relatedPackages"] = [
        s for s in dest.get("relatedPackages", [])
        if s in MAFIA_PACKAGE_SLUGS and s != "5-days-zanzibar-beach"
    ]
    dest["packages"] = [
        p for p in dest.get("packages", [])
        if p.get("slug") in MAFIA_PACKAGE_SLUGS
    ]


def main():
    core = json.loads(CORE.read_text(encoding="utf-8"))
    packages = pkg_by_slug(core["packages"])
    by_slug = {d["slug"]: d for d in core["destinations"]}

    for legacy in ("Zanzibar & Islands", "Ocean Islands"):
        if legacy in core["circuits"]:
            del core["circuits"][legacy]
    core["circuits"]["Oceanic Islands"] = [OCEAN_INTRO]
    core["circuits"][MAFIA_CIRCUIT] = [MAFIA_INTRO]

    if "mafia" in by_slug:
        enrich_mafia(by_slug["mafia"], packages)

    for cfg in MAFIA_SUB_DESTINATIONS:
        pkg = packages.get(cfg["package_slug"])
        if not pkg:
            print(f"  Warning: package {cfg['package_slug']} not found")
            continue
        entry = build_sub_destination(cfg, pkg)
        by_slug[cfg["slug"]] = entry

    for slug in MAFIA_DEST_SLUGS:
        if slug in by_slug:
            by_slug[slug]["circuit"] = MAFIA_CIRCUIT

    zanzibar_beach = packages.get("5-days-zanzibar-beach")
    if zanzibar_beach:
        zanzibar_beach["circuit"] = "Oceanic Islands"
        zanzibar_beach["destinationSlugs"] = ["zanzibar"]
        zanzibar_beach["destinations"] = ["Zanzibar"]

    for p in core["packages"]:
        if p["slug"] in MAFIA_PACKAGE_SLUGS:
            p["circuit"] = MAFIA_CIRCUIT
            p["highlights"] = [
                x for x in p.get("highlights", [])
                if "serengeti" not in x.lower() and "kilimanjaro" not in x.lower()
            ]
            if not p["highlights"]:
                p["highlights"] = ["Mafia Island Marine Park", "Indian Ocean", "Snorkelling & diving"]
            if p["slug"] in PACKAGE_DEST_MAP:
                p["destinationSlugs"] = PACKAGE_DEST_MAP[p["slug"]]
            elif "mafia" not in p.get("destinationSlugs", []):
                p["destinationSlugs"] = ["mafia"] + p.get("destinationSlugs", [])

    core["destinations"] = sorted(by_slug.values(), key=lambda d: (d["circuit"], d["name"]))
    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    mafia_pkgs = sum(1 for p in core["packages"] if p["circuit"] == MAFIA_CIRCUIT)
    mafia_dests = sum(1 for d in core["destinations"] if d["circuit"] == MAFIA_CIRCUIT)
    print(f"Mafia Island circuit: {mafia_dests} destinations, {mafia_pkgs} packages")


if __name__ == "__main__":
    main()
