#!/usr/bin/env python3
"""Import all safari packages from tanzaniatourism.com sitemap into tanzania-core.json."""
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
CACHE = ROOT / "data" / "tt-safaris-cache.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
BASE = "https://www.tanzaniatourism.com/safari/"

# Existing hand-crafted packages mapped to TT slugs (skip re-import)
EXISTING_TT_SLUGS = {
    "3-days-to-serengeti-national-park-and-ngorongoro-crater": "3-days-serengeti-ngorongoro",
    "5-days-tarangire-serengeti-ngorongoro-lake-manyara-safari": "5-days-northern-classic",
    "7-days-manyara-serengeti-ngorongoro-crater-and-tarangire-safari": "7-days-northern-circuit",
    "5-days-zanzibar-beach-holiday": "5-days-zanzibar-beach",
    "3-4-days-safari-to-gombe-stream-national-parks": "western-primates-safari",
    "8-days-safari-to-nyerere-mikumi-and-udzungwa-national-parks": "10-days-southern-explorer",
}

CIRCUIT_ALIASES = {
    "Coastal & Islands": "Oceanic Islands",
    "Ocean Islands": "Oceanic Islands",
    "Zanzibar Island": "Oceanic Islands",
    "Zanzibar & Islands": "Oceanic Islands",
    "Mafia Island": "Mafia Island",
    "Central Circuit": "Southern Circuit",
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
    "udzungwa-mountains-park": "udzungwa",
    "udzungwa-mountains-national-park": "udzungwa",
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
    "lake-chala": "lake-chala",
    "lake-jipe": "lake-jipe",
    "lake-natron": "lake-natron",
    "mount-meru": "mount-meru",
    "selous-game-reserve": "nyerere",
}

PRICE_PER_DAY = {
    "Northern Circuit": 580,
    "Southern Circuit": 520,
    "Eastern Circuit": 420,
    "Western Circuit": 620,
    "Oceanic Islands": 290,
    "Southern Highlands & Culture": 380,
}


def fetch(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        print(f"  FAIL {url}: {exc}")
        return None


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(re.sub(r"\s+", " ", text)).strip()


def tt_slug_to_dest_slug(tt_slug: str) -> str:
    if tt_slug in SLUG_MAP:
        return SLUG_MAP[tt_slug]
    s = tt_slug
    for suffix in (
        "-national-park", "-conservation-area", "-marine-reserve",
        "-marine-sanctuary", "-game-controlled-area", "-game-reserve",
    ):
        s = s.replace(suffix, "")
    return s


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80]


def estimate_price(days: int | None, circuit: str) -> str:
    if not days or days < 1:
        return "Enquire"
    rate = PRICE_PER_DAY.get(circuit, 500)
    low = days * int(rate * 0.85)
    high = days * int(rate * 1.35)
    mid = (low + high) // 2
    return f"${mid:,}"


def sitemap_safari_urls() -> list[str]:
    xml = fetch("https://www.tanzaniatourism.com/sitemap.xml")
    if not xml:
        return []
    urls = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
        if "/safari/" not in loc:
            continue
        tt_slug = loc.rstrip("/").split("/safari/")[-1]
        if tt_slug and tt_slug not in ("safaris",):
            urls.append(tt_slug)
    return sorted(set(urls))


def safari_destinations_block(html: str) -> str:
    """Isolate the 'Destinations in this Safari' section - ignore site-wide footer links."""
    m = re.search(
        r"Destination/s in this Safari(.*?)(?:"
        r"Relates?\s+Tours|Related\s+Tours|"
        r"<h2[^>]*>Reviews|id=\"reviews\"|"
        r"Tours\s*&\s*Safaris</h5>|"
        r"Your Travel Journey Starts Here"
        r")",
        html,
        re.S | re.I,
    )
    if m:
        return m.group(1)
    # Fallback: cards grid only (citiesCard near destinations heading)
    m2 = re.search(
        r"Destination/s in this Safari.*?(<div class=\"row[^\"]*\">.*?</div>\s*</div>)",
        html,
        re.S | re.I,
    )
    return m2.group(1) if m2 else ""


def parse_destinations(html: str, dest_by_slug: dict) -> tuple[list[str], list[str]]:
    names: list[str] = []
    slugs: list[str] = []
    block = safari_destinations_block(html)
    if not block:
        return names, slugs

    for tt_slug, title in re.findall(
        r'href="https://www\.tanzaniatourism\.com/destination/([^"]+)"[^>]*(?:title="([^"]*)")?',
        block,
        re.I,
    ):
        slug = tt_slug_to_dest_slug(tt_slug)
        if slug in dest_by_slug and slug not in slugs:
            slugs.append(slug)
            label = strip_html(title) if title else dest_by_slug[slug]["name"]
            names.append(label)

    if not slugs:
        for title in re.findall(r'title="([^"]+)"', block):
            t = strip_html(title)
            for d in dest_by_slug.values():
                if t.lower() == d["name"].lower() or (
                    len(t) > 8 and (t.lower() in d["name"].lower() or d["name"].lower() in t.lower())
                ):
                    if d["slug"] not in slugs:
                        slugs.append(d["slug"])
                        names.append(d["name"])
                    break
    return names, slugs


def parse_circuit(html: str) -> str:
    for label in (
        "Northern Circuit", "Southern Circuit", "Eastern Circuit",
        "Western Circuit", "Oceanic Islands", "Zanzibar Island", "Mafia Island",
        "Southern Highlands & Culture",
    ):
        if label in html[:8000]:
            return CIRCUIT_ALIASES.get(label, label)
    m = re.search(r"(Northern|Southern|Eastern|Western) Circuit", html)
    if m:
        return f"{m.group(1)} Circuit"
    if "Zanzibar" in html[:5000] or "Ocean Islands" in html[:5000]:
        return "Oceanic Islands"
    return "Northern Circuit"


def parse_package(tt_slug: str, html: str, dest_by_slug: dict) -> dict | None:
    h1 = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    name = strip_html(h1.group(1)) if h1 else tt_slug.replace("-", " ").title()

    duration_m = re.search(r"Duration:\s*([^<]+)", html)
    duration_text = strip_html(duration_m.group(1)) if duration_m else ""
    days_m = re.search(r"(\d+)\s*Days?", duration_text, re.I)
    days = int(days_m.group(1)) if days_m else None
    if not days and "day trip" in name.lower():
        days = 1
        duration_text = duration_text or "Day Trip"
    nights = max(0, days - 1) if days else None

    overview_m = re.search(r'Overview</h3>\s*<div[^>]*>(.*?)</div>\s*<div', html, re.S)
    if not overview_m:
        overview_m = re.search(r'class="[^"]*ee-body"><p>(.*?)</p>', html, re.S)
    overview = strip_html(overview_m.group(1)) if overview_m else f"Safari package: {name}."

    activities_block = re.findall(
        r'Activities</h3>.*?<div class="row[^"]*">(.*?)</div>\s*</div>', html, re.S
    )
    activity_list = []
    if activities_block:
        activity_list = [
            strip_html(a) for a in re.findall(r'class="[^"]*">\s*([^<]+)\s*</div>', activities_block[0])
            if strip_html(a)
        ]

    itinerary = []
    for day_m in re.finditer(
        r'<div class="col-12">\s*<div class="fw-600[^"]*">Day\s*(\d+)</div>\s*<div[^>]*>(.*?)</div>\s*<div class="col-12">\s*<div class="text-15[^"]*">(.*?)</div>',
        html,
        re.S,
    ):
        itinerary.append({
            "day": int(day_m.group(1)),
            "title": strip_html(day_m.group(2)),
            "summary": strip_html(day_m.group(3))[:400],
        })

    highlights = activity_list[:6] if activity_list else []
    if not highlights:
        _, dest_slugs_preview = parse_destinations(html, dest_by_slug)
        highlights = [
            dest_by_slug[s]["name"] for s in dest_slugs_preview[:4] if s in dest_by_slug
        ]
    if not highlights:
        highlights = [name.split(" to ")[-1] if " to " in name else "Safari experience"]

    dest_names, dest_slugs = parse_destinations(html, dest_by_slug)
    circuit = parse_circuit(html)
    if dest_slugs:
        primary = dest_by_slug.get(dest_slugs[0], {})
        if primary.get("circuit"):
            circuit = primary["circuit"]

    hero = ""
    for img in re.findall(
        r'https://www\.tanzaniatourism\.com/images/uploads/[^"\']+\.(?:jpg|jpeg|png|webp)',
        html,
    ):
        if "logo" not in img.lower():
            hero = img
            break
    if dest_slugs and not hero:
        hero = dest_by_slug.get(dest_slugs[0], {}).get("hero", "")

    slug = EXISTING_TT_SLUGS.get(tt_slug) or slugify(name)
    price = estimate_price(days, circuit)

    return {
        "slug": slug,
        "tt_slug": tt_slug,
        "name": name,
        "circuit": circuit,
        "days": days,
        "nights": nights,
        "duration": duration_text or (f"{days} Days / {nights} Nights" if days and nights is not None else ""),
        "price": price,
        "priceRange": price if price == "Enquire" else price,
        "overview": overview[:600],
        "highlights": highlights[:6],
        "destinations": dest_names or [dest_by_slug[s]["name"] for s in dest_slugs if s in dest_by_slug],
        "destinationSlugs": dest_slugs,
        "hero": hero,
        "featured": False,
        "itinerary": itinerary[:12] or [
            {"day": 1, "title": name, "summary": overview[:300]}
        ],
        "category": infer_category(name, activity_list, circuit),
    }


def infer_category(name: str, activities: list[str], circuit: str) -> str:
    n = name.lower()
    acts = " ".join(activities).lower()
    if any(x in n or x in acts for x in ("kilimanjaro", "climb", "trek", "summit", "marangu", "machame", "umbwe")):
        return "mountain-climbing"
    if any(x in n or x in acts for x in ("beach", "zanzibar", "island", "snorkel", "pemba", "mafia")):
        return "beach-holiday"
    if any(x in n or x in acts for x in ("walk", "hike", "waterfall", "forest")):
        return "walking-safaris"
    if any(x in n or x in acts for x in ("cultural", "hadzabe", "datoga", "historical", "ruins", "cave")):
        return "tourist-attractions"
    if any(x in n or x in acts for x in ("chimp", "primate", "gombe", "mahale")):
        return "adventure-safaris"
    return "tanzania-safaris"


def sync_related_packages(core: dict) -> None:
    by_slug = {p["slug"]: p for p in core["packages"]}
    dest_index: dict[str, list[str]] = {}
    for p in core["packages"]:
        for ds in p.get("destinationSlugs", []):
            dest_index.setdefault(ds, []).append(p["slug"])

    for d in core["destinations"]:
        slugs = sorted(set(dest_index.get(d["slug"], [])))
        d["relatedPackages"] = slugs
        d["packages"] = []
        for s in slugs:
            if s in by_slug:
                p = by_slug[s]
                d["packages"].append({
                    "name": p["name"],
                    "slug": p["slug"],
                    "days": p.get("days"),
                    "price": p.get("price", "Enquire"),
                    "description": p.get("overview", "")[:180],
                })


def main():
    core = json.loads(CORE.read_text(encoding="utf-8"))
    dest_by_slug = {d["slug"]: d for d in core["destinations"]}
    existing_by_slug = {p["slug"]: p for p in core["packages"]}
    existing_tt = {p.get("tt_slug"): p["slug"] for p in core["packages"] if p.get("tt_slug")}
    existing_tt.update({k: v for k, v in EXISTING_TT_SLUGS.items()})

    tt_slugs = sitemap_safari_urls()
    print(f"Found {len(tt_slugs)} safari URLs in sitemap")

    cache: dict = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))

    added = 0
    skipped = 0
    for i, tt_slug in enumerate(tt_slugs, 1):
        if tt_slug in existing_tt:
            skipped += 1
            continue

        if tt_slug in cache:
            pkg = cache[tt_slug]
        else:
            url = BASE + tt_slug
            print(f"[{i}/{len(tt_slugs)}] {tt_slug}")
            html = fetch(url)
            if not html:
                continue
            pkg = parse_package(tt_slug, html, dest_by_slug)
            if not pkg:
                continue
            cache[tt_slug] = pkg
            CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
            time.sleep(0.35)

        if pkg["slug"] in existing_by_slug:
            skipped += 1
            continue

        core["packages"].append(pkg)
        existing_by_slug[pkg["slug"]] = pkg
        added += 1

    # Tag existing packages with tt_slug where known
    for p in core["packages"]:
        if not p.get("tt_slug"):
            for tt, our in EXISTING_TT_SLUGS.items():
                if p["slug"] == our:
                    p["tt_slug"] = tt

    sync_related_packages(core)
    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = {}
    for p in core["packages"]:
        for ds in p.get("destinationSlugs", []):
            counts[ds] = counts.get(ds, 0) + 1
    with_tours = sum(1 for c in counts.values() if c > 0)
    print(f"\nAdded {added} new packages, skipped {skipped} duplicates")
    print(f"Total packages: {len(core['packages'])}")
    print(f"Destinations with tours: {with_tours}")
    top = sorted(counts.items(), key=lambda x: -x[1])[:10]
    for slug, n in top:
        print(f"  {slug}: {n} tours")


if __name__ == "__main__":
    main()
