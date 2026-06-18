#!/usr/bin/env python3
"""Scrape destination content and image URLs from tanzaniatourism.com."""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "destinations.json"
BASE = "https://www.tanzaniatourism.com/destination/"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# slug, tanzaniatourism URL slug, circuit
DESTINATION_SOURCES = [
    # Northern Circuit
    ("serengeti", "serengeti-national-park", "Northern Circuit"),
    ("kilimanjaro", "mount-kilimanjaro-national-park", "Northern Circuit"),
    ("arusha", "arusha-national-park", "Northern Circuit"),
    ("lake-manyara", "lake-manyara-national-park", "Northern Circuit"),
    ("ngorongoro", "ngorongoro-conservation-area", "Northern Circuit"),
    ("tarangire", "tarangire-national-park", "Northern Circuit"),
    ("mkomazi", "mkomazi-national-park", "Northern Circuit"),
    ("oldonyo-lengai", "mount-oldoinyo-lengai", "Northern Circuit"),
    ("lake-natron", "lake-natron", "Northern Circuit"),
    ("kondoa-rock-art", "kondoa-rock-art-sites", "Northern Circuit"),
    ("lake-chala", "lake-chala", "Northern Circuit"),
    ("lake-jipe", "lake-jipe", "Northern Circuit"),
    ("lake-eyasi", "lake-eyasi", "Northern Circuit"),
    ("pare-mountains", "pare-mountains", "Northern Circuit"),
    ("mount-meru", "mount-meru", "Northern Circuit"),
    ("ngurdoto-crater", "ngurdoto-crater", "Northern Circuit"),
    # Southern Circuit
    ("ruaha", "ruaha-national-park", "Southern Circuit"),
    ("nyerere", "nyerere-national-park", "Southern Circuit"),
    ("kitulo", "kitulo-national-park", "Southern Circuit"),
    ("katavi", "katavi-national-park", "Southern Circuit"),
    ("kalambo-falls", "kalambo-falls", "Southern Circuit"),
    ("mbozi-meteorite", "mbozi-meteorite", "Southern Circuit"),
    ("lake-ngozi", "lake-ngozi", "Southern Circuit"),
    ("kaporogwe-falls", "kaporogwe-falls", "Southern Circuit"),
    ("matema-beach", "matema-beach", "Southern Circuit"),
    ("lake-nyasa", "lake-nyasa", "Southern Circuit"),
    ("mnazi-bay", "mnazi-bay-ruvuma-estuary-marine-park", "Southern Circuit"),
    ("igelegke-rock-art", "igeleke-rock-art-site", "Southern Circuit"),
    ("isimila", "isimila-stone-age-site", "Southern Circuit"),
    ("mikumi", "mikumi-national-park", "Southern Circuit"),
    # Eastern Circuit
    ("udzungwa", "udzungwa-mountains-park", "Eastern Circuit"),
    ("saadani", "saadani-national-park", "Eastern Circuit"),
    ("bagamoyo", "bagamoyo-historical-town", "Eastern Circuit"),
    # Western Circuit
    ("gombe", "gombe-stream-national-park", "Western Circuit"),
    ("mahale", "mahale-mountains-national-park", "Western Circuit"),
    ("saanane", "saanane-island-national-park", "Western Circuit"),
    ("rubondo", "rubondo-island-national-park", "Western Circuit"),
    ("ukerewe", "ukerewe-island", "Western Circuit"),
    ("burigi-chato", "burigi-chato-national-park", "Western Circuit"),
    ("ibanda-kyerwa", "ibanda-kyerwa-national-park", "Western Circuit"),
    ("lake-tanganyika", "lake-tanganyika", "Western Circuit"),
    # Coastal & Islands
    ("zanzibar", "zanzibar-island", "Coastal & Islands"),
    ("pemba", "pemba-island", "Coastal & Islands"),
    ("mafia", "mafia-island", "Coastal & Islands"),
    ("prison-island", "prison-island-changuu", "Coastal & Islands"),
]

CIRCUIT_INTROS = {
    "Northern Circuit": [
        "The Northern Circuit is Tanzania's most celebrated safari region, centred on Arusha and Kilimanjaro International Airport.",
        "World-famous parks - Serengeti, Ngorongoro, Tarangire and Lake Manyara - deliver the classic African safari alongside volcanic peaks, soda lakes and Maasai culture.",
    ],
    "Southern Circuit": [
        "The Southern Circuit rewards travellers who venture into Tanzania's largest and least crowded wilderness areas.",
        "Ruaha, Nyerere, Katavi and Mikumi protect vast baobab savannas, river systems and remote bush where elephant, lion and wild dog roam far from the crowds.",
    ],
    "Eastern Circuit": [
        "The Eastern Circuit blends Indian Ocean coastline with rainforest hiking, primate tracking and Swahili heritage.",
        "Saadani is Tanzania's only coastal national park; Udzungwa and Bagamoyo add waterfalls, colobus monkeys and centuries of history.",
    ],
    "Western Circuit": [
        "The Western Circuit is Tanzania's remotest safari frontier on the shores of Lake Tanganyika.",
        "Mahale and Gombe are world-renowned for chimpanzee trekking; Rubondo and Burigi-Chato offer island and lake wilderness.",
    ],
    "Coastal & Islands": [
        "Tanzania's Coastal and Islands circuit extends your safari with Swahili culture, spice plantations and Indian Ocean beaches.",
        "Zanzibar, Pemba and Mafia offer Stone Town heritage, reef snorkeling and barefoot luxury after mainland wildlife adventures.",
    ],
}


def fetch(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        print(f"  FAIL {url}: {e}")
        return None


def strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_meta(html: str) -> str:
    m = re.search(
        r"((?:National Parks|Conservation Areas|Tourist Attractions|Mountain Range|"
        r"Historical Sites|Beach Holiday|Ocean Islands)[^<]{0,30}\d[\d,.\s]*km²[^<]{0,80})",
        html,
    )
    if m:
        return strip_html(m.group(1))
    m = re.search(r'property="og:description" content="([^"]+)"', html)
    return strip_html(m.group(1))[:100] if m else ""


def parse_overview(html: str) -> list[str]:
    block = re.search(r'id="overview".*?class="[^"]*ee-body">(.*?)</div>\s*</div>', html, re.S)
    if not block:
        block = re.search(r'class="[^"]*ee-body"><p>.*?</div>', html, re.S)
    if not block:
        return []
    paras = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", block.group(1), re.S):
        clean = strip_html(p)
        if len(clean) > 40:
            paras.append(clean)
    return paras[:8]


def parse_faqs(html: str) -> list[dict]:
    faqs = []
    for m in re.finditer(
        r'<div class="accordion__item[^"]*">\s*<button[^>]*>(.*?)</button>\s*<div class="accordion__content[^"]*">\s*<div[^>]*>(.*?)</div>',
        html,
        re.S,
    ):
        q = strip_html(m.group(1))
        a_parts = [strip_html(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", m.group(2), re.S)]
        a = " ".join(p for p in a_parts if p)
        if q and a:
            faqs.append({"q": q, "a": a})
    return faqs[:6]


def parse_packages(html: str) -> list[dict]:
    packages = []
    for title in re.findall(r'title="([^"]+)" class="tourCard', html):
        days_m = re.match(r"(\d+)\s*Days?", title, re.I)
        days = int(days_m.group(1)) if days_m else None
        packages.append({"name": title, "days": days, "price": None, "description": title})
    seen = set()
    unique = []
    for p in packages:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)
    return unique[:8]


def parse_gallery(html: str) -> list[str]:
    imgs = re.findall(
        r'href="(https://www\.tanzaniatourism\.com/images/uploads/[^"]+\.(?:jpg|jpeg|png))"',
        html,
    )
    return [u for u in dict.fromkeys(imgs) if "logo" not in u.lower()][:4]


def parse_badge(meta: str, name: str) -> str:
    meta_l = meta.lower()
    if "unesco" in meta_l:
        return "UNESCO"
    if "national park" in meta_l:
        return "National Park"
    if "conservation" in meta_l:
        return "Conservation"
    if "mountain" in meta_l or "climbing" in meta_l:
        return "Mountains"
    if "beach" in meta_l or "island" in meta_l:
        return "Coastal"
    if "historical" in meta_l:
        return "Heritage"
    words = name.split()
    return words[0] if words else "Explore"


def scrape_one(slug: str, tt_slug: str, circuit: str) -> dict | None:
    url = BASE + tt_slug
    html = fetch(url)
    if not html:
        return None

    og = re.search(r'property="og:image" content="([^"]+)"', html)
    hero = og.group(1) if og else ""
    if hero and ("logo" in hero.lower() or "/logos/" in hero):
        hero = ""
    gallery = parse_gallery(html)
    if not hero and gallery:
        hero = gallery[0]

    h1 = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    name = strip_html(h1.group(1)) if h1 else slug.replace("-", " ").title()
    meta = parse_meta(html)
    paragraphs = parse_overview(html)
    if not paragraphs:
        desc = re.search(r'property="og:description" content="([^"]+)"', html)
        if desc:
            paragraphs = [desc.group(1)]

    card_desc = paragraphs[0][:200] if paragraphs else f"Explore {name} on the {circuit}."

    return {
        "slug": slug,
        "tt_slug": tt_slug,
        "name": name,
        "circuit": circuit,
        "badge": parse_badge(meta, name),
        "meta": meta or circuit,
        "card_desc": card_desc,
        "hero": hero,
        "gallery": gallery[:2] if gallery else ([hero] if hero else []),
        "paragraphs": paragraphs,
        "faqs": parse_faqs(html),
        "packages": parse_packages(html),
        "source": url,
    }


def main():
    results = []
    failed = []
    for slug, tt_slug, circuit in DESTINATION_SOURCES:
        print(f"Scraping {slug}...")
        item = scrape_one(slug, tt_slug, circuit)
        if item:
            results.append(item)
            print(f"  OK - {len(item['paragraphs'])} paras, {len(item['gallery'])} imgs")
        else:
            failed.append((slug, tt_slug))
        time.sleep(0.6)

    data = {
        "source": "https://www.tanzaniatourism.com",
        "circuits": CIRCUIT_INTROS,
        "destinations": results,
        "failed": failed,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(results)} destinations to {OUT}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(s[0] for s in failed)}")


if __name__ == "__main__":
    main()
