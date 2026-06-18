#!/usr/bin/env python3
"""Build client-side search index for site-wide AJAX search."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"
KENYA = ROOT / "data" / "kenya-data.json"
UGANDA = ROOT / "data" / "uganda-data.json"
RWANDA = ROOT / "data" / "rwanda-data.json"
ACCOMMODATIONS = ROOT / "data" / "accommodations.json"
SAFARI_PACKAGES = ROOT / "data" / "safari-packages.json"
EAST_AFRICA_PACKAGES = ROOT / "data" / "east-africa-packages.json"
OUT = ROOT / "data" / "search-index.json"

CIRCUIT_PAGES = {
    "Northern Circuit": "circuits/northern-circuit.html",
    "Southern Circuit": "circuits/southern-circuit.html",
    "Eastern Circuit": "circuits/eastern-circuit.html",
    "Western Circuit": "circuits/western-circuit.html",
    "Oceanic Islands": "circuits/tanzania-oceanic-islands.html",
    "Zanzibar": "circuits/zanzibar.html",
    "Mafia Island": "circuits/mafia-island.html",
    "Southern Highlands & Culture": "circuits/southern-highlands.html",
}

INDEX_SECTIONS = [
    ("Home", "index.html#home", "Safari and Bush Retreats homepage"),
    ("Safari Packages", "index.html#safaris", "All curated safari itineraries"),
    ("Book Safari", "index.html#bookingForm", "Contact form and safari inquiry"),
    ("Experiences", "index.html#experiences", "Game drives, hiking, beach, culture"),
    ("Accommodation", "index.html#accommodation", "Lodges, camps and villas"),
    ("Gallery", "index.html#gallery", "Photo gallery"),
    ("Kenya Safaris", "kenya.html", "Masai Mara, Amboseli and Kenya coast"),
    ("Uganda Safaris", "uganda.html", "Gorillas, Murchison Falls and Nile adventures"),
    ("Rwanda Safaris", "rwanda.html", "Volcanoes gorillas, Akagera and Lake Kivu"),
]


def item(title: str, url: str, type_: str, subtitle: str = "", keywords: str = "") -> dict:
    blob = " ".join(filter(None, [title, subtitle, keywords, type_])).lower()
    return {
        "title": title,
        "url": url,
        "type": type_,
        "subtitle": subtitle,
        "keywords": keywords,
        "search": blob,
    }


def main() -> None:
    core = json.loads(CORE.read_text(encoding="utf-8"))
    entries: list[dict] = []

    for title, url, desc in INDEX_SECTIONS:
        entries.append(item(title, url, "Page", desc))

    for circuit, url in CIRCUIT_PAGES.items():
        entries.append(item(circuit, url, "Circuit", f"Tanzania {circuit} destinations"))

    for d in core["destinations"]:
        entries.append(
            item(
                d["name"],
                f"destinations/{d['slug']}.html",
                "Destination",
                d.get("circuit", ""),
                d.get("card_desc", "")[:120],
            )
        )

    for p in core["packages"]:
        circuit = p.get("circuit", "")
        if circuit in ("Coastal & Islands", "Zanzibar & Islands", "Ocean Islands"):
            circuit = "Oceanic Islands"
        entries.append(
            item(
                p["name"],
                f"safaris/{p['slug']}.html",
                "Safari Package",
                f"{p.get('duration', '')} · {circuit}",
                p.get("overview", "")[:140],
            )
        )

    if ACCOMMODATIONS.exists():
        accommodations = json.loads(ACCOMMODATIONS.read_text(encoding="utf-8"))
        for cat in accommodations.get("categories", []):
            entries.append(
                item(
                    cat["name"],
                    f"accommodations/{cat['slug']}.html",
                    "Accommodation",
                    cat.get("shortDescription", "")[:120],
                )
            )
        for group in accommodations.get("groups", []):
            entries.append(
                item(
                    group["name"],
                    f"accommodations/{group['slug']}.html",
                    "Safari Lodge",
                    f"{group.get('country', '')} · {group.get('category', '')}",
                    group.get("shortDescription", "")[:140],
                )
            )

    extra_packages: list[dict] = []
    if EAST_AFRICA_PACKAGES.exists():
        extra_packages.extend(json.loads(EAST_AFRICA_PACKAGES.read_text(encoding="utf-8")).get("packages", []))
    for p in extra_packages:
        entries.append(
            item(
                p["name"],
                f"safaris/{p['slug']}.html",
                "Safari Package",
                f"{p.get('duration', '')} · {p.get('circuit', '')}",
                p.get("overview", "")[:140],
            )
        )

    if KENYA.exists():
        kenya = json.loads(KENYA.read_text(encoding="utf-8"))
        entries.append(item("Kenya Safaris", "kenya.html", "Page", kenya.get("kenya", {}).get("meta", "")))
        for d in kenya.get("destinations", []):
            entries.append(
                item(
                    d["name"],
                    f"kenya/{d['slug']}.html",
                    "Kenya",
                    d.get("meta", ""),
                    d.get("card_desc", "")[:120],
                )
            )

    for data_path, country_slug, type_label in (
        (UGANDA, "uganda", "Uganda"),
        (RWANDA, "rwanda", "Rwanda"),
    ):
        if not data_path.exists():
            continue
        country_data = json.loads(data_path.read_text(encoding="utf-8"))
        overview = country_data.get(country_slug, {})
        entries.append(
            item(
                overview.get("name", f"{country_slug.title()} Safaris"),
                f"{country_slug}.html",
                "Page",
                overview.get("meta", ""),
            )
        )
        for d in country_data.get("destinations", []):
            entries.append(
                item(
                    d["name"],
                    f"{country_slug}/{d['slug']}.html",
                    type_label,
                    d.get("meta", ""),
                    d.get("card_desc", "")[:120],
                )
            )

    OUT.write_text(json.dumps({"items": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built search index with {len(entries)} items -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
