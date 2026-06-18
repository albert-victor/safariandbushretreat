#!/usr/bin/env python3
"""Scrape safari package details from tanzaniatourism.com."""
from __future__ import annotations

import json
import re
import time
import urllib.request
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "safari-packages.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
BASE = "https://www.tanzaniatourism.com/safari/"

PACKAGES = [
    ("3-days-serengeti-ngorongoro", "3-days-to-serengeti-national-park-and-ngorongoro-crater", "Northern Circuit"),
    ("5-days-northern-classic", "5-days-tarangire-serengeti-ngorongoro-lake-manyara-safari", "Northern Circuit"),
    ("7-days-northern-grand", "7-days-manyara-serengeti-ngorongoro-crater-and-tarangire-safari", "Northern Circuit"),
    ("4-days-mikumi-udzungwa", "4-days-safari-to-mikumi-and-udzungwa-national-parks", "Eastern Circuit"),
    ("8-days-southern-wilderness", "8-days-safari-to-nyerere-mikumi-and-udzungwa-national-parks", "Southern Circuit"),
    ("6-days-gombe-primates", "3-4-days-safari-to-gombe-stream-national-parks", "Western Circuit"),
    ("5-days-zanzibar-beach", "5-days-zanzibar-beach-holiday", "Coastal & Islands"),
]

# Indicative starting prices (TT is enquiry-only; adapted for SBR)
PRICE_HINTS = {
    "3-days-serengeti-ngorongoro": "$2,150",
    "5-days-northern-classic": "$2,950",
    "7-days-northern-grand": "$4,200",
    "4-days-mikumi-udzungwa": "$1,650",
    "8-days-southern-wilderness": "$3,800",
    "6-days-gombe-primates": "$2,750",
    "5-days-zanzibar-beach": "$1,450",
}


def fetch(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  FAIL {url}: {e}")
        return None


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(re.sub(r"\s+", " ", text)).strip()


def parse_package(slug: str, tt_slug: str, circuit: str, html: str) -> dict:
    h1 = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    name = strip_html(h1.group(1)) if h1 else slug.replace("-", " ").title()

    duration = re.search(r"Duration:\s*([^<]+)", html)
    duration_text = strip_html(duration.group(1)) if duration else ""
    days_m = re.search(r"(\d+)\s*Days?", duration_text, re.I)
    days = int(days_m.group(1)) if days_m else None

    overview_m = re.search(r'Overview</h3>\s*<div[^>]*>(.*?)</div>\s*<div', html, re.S)
    if not overview_m:
        overview_m = re.search(r'class="[^"]*ee-body"><p>(.*?)</p>', html, re.S)
    overview = strip_html(overview_m.group(1)) if overview_m else ""

    activities = re.findall(r'Activities</h3>.*?<div class="row[^"]*">(.*?)</div>\s*</div>', html, re.S)
    activity_list = []
    if activities:
        activity_list = [strip_html(a) for a in re.findall(r'class="[^"]*">\s*([^<]+)\s*</div>', activities[0]) if strip_html(a)]

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

    if not itinerary:
        for day_m in re.finditer(r"Day\s*(\d+)</div>\s*<div[^>]*>([^<]+)</div>.*?<p>(.*?)</p>", html, re.S):
            itinerary.append({
                "day": int(day_m.group(1)),
                "title": strip_html(day_m.group(2)),
                "summary": strip_html(day_m.group(3))[:400],
            })

    dests = re.findall(r'Destination/s in this Safari.*?title="([^"]+)"', html, re.S)
    if not dests:
        dests = re.findall(r'####\s*([^<\n]+National Park[^<\n]*)', html)
        dests = [strip_html(d) for d in dests[:6]]

    hero = ""
    for img in re.findall(r'https://www\.tanzaniatourism\.com/images/uploads/[^"\']+\.(?:jpg|jpeg|png)', html):
        if "logo" not in img.lower():
            hero = img
            break
    if not hero:
        hero = "https://www.tanzaniatourism.com/images/uploads/Serengeti_Gnus_7765.jpg"

    features = activity_list[:6] if activity_list else [d for d in dests[:4]]
    if duration_text and duration_text not in features:
        features.insert(0, duration_text)
    if circuit not in str(features):
        features.append(circuit)

    return {
        "slug": slug,
        "tt_slug": tt_slug,
        "name": name,
        "circuit": circuit,
        "days": days,
        "duration": duration_text,
        "price": PRICE_HINTS.get(slug, "Enquire"),
        "overview": overview,
        "activities": activity_list,
        "destinations": dests[:6],
        "itinerary": itinerary[:8],
        "features": features[:6],
        "hero": hero,
        "featured": slug == "5-days-northern-classic",
        "source": BASE + tt_slug,
    }


def main():
    results = []
    for slug, tt_slug, circuit in PACKAGES:
        print(f"Scraping {slug}…")
        html = fetch(BASE + tt_slug)
        if html:
            pkg = parse_package(slug, tt_slug, circuit, html)
            results.append(pkg)
            print(f"  OK - {pkg.get('days')} days, {len(pkg.get('itinerary', []))} itinerary steps")
        time.sleep(0.5)

    OUT.write_text(
        json.dumps({"source": "https://www.tanzaniatourism.com/safaris", "packages": results}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {len(results)} packages to {OUT}")


if __name__ == "__main__":
    main()
