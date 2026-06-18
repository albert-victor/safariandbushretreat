#!/usr/bin/env python3
"""Mirror Tanzania Tourism images for homepage experiences and write data/experiences.json."""
from __future__ import annotations

import json
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "images" / "experiences"
DATA_OUT = ROOT / "data" / "experiences.json"
TT_BASE = "https://www.tanzaniatourism.com/images/uploads/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

# Original homepage experiences — keep legacy images (do not mirror)
LEGACY_IMAGES = {
    "game-drives": "assets/images/Serengeti-National-Park-1-1.jpg",
    "hiking-walking": "assets/images/walking and hiking.jpg",
    "beach-holidays": "assets/images/beach holiday.jpg",
    "balloon-safaris": "assets/images/baloon safari.jpg",
    "family-adventures": "assets/images/family adventures2.jpg",
    "camping-safaris": "assets/images/camping safari.jpg",
    "culture-tours": "assets/images/masai.jpg",
    "nature-photography": "assets/images/serengeti.jpg",
    "honeymoon": "assets/images/honeymoon safari.jpg",
    "sport-fishing": "assets/images/sport fishing.jpg",
}

# TT activities — each gets a mirrored image in assets/images/experiences/{id}.jpg
EXPERIENCES = [
    # --- Original signature experiences (legacy images) ---
    {
        "id": "game-drives",
        "title": "Game Drives",
        "tab": "Game Drives",
        "icon": "fa-binoculars",
        "desc": "Private 4x4 safaris with expert guides across Tanzania's finest parks and reserves.",
        "highlights": ["Serengeti & Ngorongoro", "Ruaha & Nyerere", "Private guide & vehicle", "Big Five focus"],
        "alt": "Safari game drive on the Serengeti plains",
        "legacy": True,
    },
    {
        "id": "hiking-walking",
        "title": "Hiking & Walking",
        "tab": "Hiking",
        "icon": "fa-person-hiking",
        "desc": "Guided bush walks and scenic trails through untamed landscapes and highland forests.",
        "highlights": ["Usambara trails", "Ngorongoro highlands", "Udzungwa rainforest", "Guided bush walks"],
        "alt": "Walking safari in Tanzania",
        "legacy": True,
    },
    {
        "id": "beach-holidays",
        "title": "Beach Holidays",
        "tab": "Beach",
        "icon": "fa-umbrella-beach",
        "desc": "Pristine Indian Ocean coastlines paired with your safari adventure.",
        "highlights": ["Zanzibar & Pemba", "Mafia archipelago", "Resort & villa stays", "Bush-to-beach combos"],
        "alt": "Beach holiday on the Tanzanian coast",
        "legacy": True,
    },
    {
        "id": "balloon-safaris",
        "title": "Balloon Safaris",
        "tab": "Balloon",
        "icon": "fa-cloud-sun",
        "desc": "Sunrise flights over the Serengeti — a once-in-a-lifetime perspective on the plains.",
        "highlights": ["Dawn launch", "Champagne breakfast", "Migration views", "Serengeti only"],
        "alt": "Hot air balloon safari at sunrise",
        "legacy": True,
    },
    {
        "id": "family-adventures",
        "title": "Family Adventures",
        "tab": "Family",
        "icon": "fa-people-group",
        "desc": "Safe, engaging itineraries designed for families of all ages across every circuit.",
        "highlights": ["Child-friendly lodges", "Shorter drives", "Beach add-ons", "Educational guides"],
        "alt": "Family on safari in Tanzania",
        "legacy": True,
    },
    {
        "id": "camping-safaris",
        "title": "Camping Safaris",
        "tab": "Camping",
        "icon": "fa-campground",
        "desc": "Authentic bush camps with luxury comfort beneath the African stars.",
        "highlights": ["Mobile camps", "Fly-camping", "Bush dinners", "Remote wilderness"],
        "alt": "Luxury tented camp under African stars",
        "legacy": True,
    },
    {
        "id": "culture-tours",
        "title": "Culture Tours",
        "tab": "Culture",
        "icon": "fa-masks-theater",
        "desc": "Maasai villages, Stone Town heritage and living traditions across Tanzania.",
        "highlights": ["Maasai bomas", "Hadzabe visits", "Swahili coast", "Craft workshops"],
        "alt": "Maasai cultural experience",
        "legacy": True,
    },
    {
        "id": "nature-photography",
        "title": "Nature Photography",
        "tab": "Photography",
        "icon": "fa-camera",
        "desc": "Specialist photo safaris with prime wildlife viewing positions and golden-hour timing.",
        "highlights": ["Private vehicle", "Hide sessions", "Migration camps", "Pro tips"],
        "alt": "Wildlife photography on safari",
        "legacy": True,
    },
    {
        "id": "honeymoon",
        "title": "Honeymoon Safaris",
        "tab": "Honeymoon",
        "icon": "fa-heart",
        "desc": "Romantic bush retreats and private beach escapes crafted for two.",
        "highlights": ["Private dinners", "Bush & beach", "Luxury lodges", "Surprise touches"],
        "alt": "Romantic honeymoon sundowner safari",
        "legacy": True,
    },
    {
        "id": "sport-fishing",
        "title": "Sport Fishing",
        "tab": "Fishing",
        "icon": "fa-fish",
        "desc": "Deep-sea and lake fishing adventures along Tanzania's coasts and Rift Valley lakes.",
        "highlights": ["Deep-sea charters", "Lake Victoria", "Billfish season", "Catch & release"],
        "alt": "Sport fishing in Tanzania",
        "legacy": True,
    },
    # --- Curated TT activities (page 2 tabs) ---
    {
        "id": "museum-monuments",
        "title": "Museums & Monuments",
        "tab": "Museums",
        "icon": "fa-building-columns",
        "tt_image": f"{TT_BASE}Zanzibar_House_of_Wonders_Stone_Town_01.jpg",
        "desc": "Explore Stone Town palaces, Bagamoyo slave-trade sites and Tanzania's living museum heritage.",
        "highlights": ["House of Wonders", "Bagamoyo Old Fort", "Chief Mkwawa museum", "Guided tours"],
        "alt": "House of Wonders museum in Stone Town Zanzibar",
    },
    {
        "id": "boat-safaris",
        "title": "Boat Safaris",
        "tab": "Boat Safari",
        "icon": "fa-ship",
        "tt_image": f"{TT_BASE}Nyerere_National_Park_Boat_Safari_on_Rufiji_River_75.jpg",
        "desc": "Glide along the Rufiji, Wami and Lake Tanganyika shorelines for hippos, crocodiles and birdlife.",
        "highlights": ["Nyerere NP", "Saadani estuary", "Rufiji River", "Sunset cruises"],
        "alt": "Boat safari on the Rufiji River in Nyerere National Park",
    },
    {
        "id": "spice-farms",
        "title": "Spice Farm Tours",
        "tab": "Spice Farm",
        "icon": "fa-leaf",
        "tt_image": f"{TT_BASE}Zanzibar_Spice_Tour_Fresh_Nutmeg_Fruit.jpg",
        "desc": "Walk fragrant clove, vanilla and cinnamon plantations on Zanzibar and Pemba.",
        "highlights": ["Zanzibar farms", "Pemba cloves", "Tasting sessions", "Village guides"],
        "alt": "Fresh nutmeg on a Zanzibar spice farm tour",
    },
    {
        "id": "historical-visits",
        "title": "Historical Visits",
        "tab": "History",
        "icon": "fa-landmark",
        "tt_image": f"{TT_BASE}Kilwa/Husuni_Kubwa_Sultans_Palace_14th__Century_04_Kilwa_Kisiwani.jpg",
        "desc": "UNESCO ruins, slave-trade heritage and Swahili trading towns along the coast.",
        "highlights": ["Kilwa Kisiwani", "Bagamoyo", "Stone Town", "Songo Mnara"],
        "alt": "Historic Sultan's Palace ruins at Kilwa Kisiwani",
    },
    {
        "id": "city-tours",
        "title": "City Tours",
        "tab": "City",
        "icon": "fa-city",
        "tt_image": f"{TT_BASE}Zanzibar_Stone_Town_01.jpg",
        "desc": "Explore Dar es Salaam, Arusha and Zanzibar Stone Town with local expert guides.",
        "highlights": ["Stone Town walk", "Dar harbour", "Local markets", "Architecture & food"],
        "alt": "Stone Town Zanzibar city tour",
    },
    {
        "id": "hot-springs",
        "title": "Hot Springs & Geothermal Pools",
        "tab": "Hot Spring",
        "icon": "fa-hot-tub-person",
        "tt_image": f"{TT_BASE}Rundugai_Hotsprings_Kilimanjaro.jpg",
        "desc": "Swim in crystal-clear geothermal pools at Chemka and Rundugai — perfect rest after a Kilimanjaro trek or northern safari.",
        "highlights": ["Chemka oasis", "Rundugai springs", "Turquoise pools", "Moshi day trips"],
        "alt": "Chemka hot springs near Kilimanjaro",
    },
    {
        "id": "whale-watching",
        "title": "Whale Watching",
        "tab": "Whale",
        "icon": "fa-water",
        "tt_image": f"{TT_BASE}Mafia_Island_Humpback_Whale_02.jpg",
        "desc": "Seasonal humpback whale encounters off the southern coast and Mafia Island.",
        "highlights": ["Jul–Oct season", "Mafia & Kilwa coast", "Boat excursions", "Marine naturalists"],
        "alt": "Humpback whale off Mafia Island",
    },
    {
        "id": "dhow-cruises",
        "title": "Dhow Cruises",
        "tab": "Dhow Cruises",
        "icon": "fa-ship",
        "tt_image": f"{TT_BASE}Zanzibar_Dhow_Sunset_Cruise_01.jpg",
        "desc": "Traditional wooden dhow sails at sunset along Zanzibar, Kilwa and the Swahili coast.",
        "highlights": ["Sunset cruises", "Safari Blue", "Stone Town harbour", "Island hopping"],
        "alt": "Traditional dhow sunset cruise in Zanzibar",
    },
]


def local_tt_path(rel: str) -> Path | None:
    """Use already-mirrored TT file if present."""
    path = ROOT / "assets" / "images" / rel.replace("/", "\\") if "\\" not in rel else ROOT / "assets" / "images" / rel
    path = ROOT / "assets" / "images" / rel
    return path if path.exists() else None


def find_existing_tt(url: str) -> Path | None:
    """Match URL filename against assets/images/external/tt/."""
    fname = url.split("/")[-1]
    fname = fname.replace("%20", "_")
    tt_dir = ROOT / "assets" / "images" / "external" / "tt"
    if not tt_dir.exists():
        return None
    for path in tt_dir.iterdir():
        if fname in path.name:
            return path
    # Bagamoyo/Kilwa subpaths in URL
    base = re.sub(r"[^a-zA-Z0-9._-]+", "_", url.split("/")[-1])
    for path in tt_dir.iterdir():
        if base in path.name or path.name.endswith(base):
            return path
    return None


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
            print(f"  WARN small {dest.name} ({len(data)} bytes)")
            return False
        dest.write_bytes(data)
        print(f"  saved {dest.name} ({len(data) // 1024} KB)")
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"  FAIL {url}: {exc}")
        return False


def mirror_image(exp_id: str, url: str) -> str | None:
    dest = OUT_DIR / f"{exp_id}.jpg"
    existing = find_existing_tt(url)
    if existing and existing.stat().st_size > 2000:
        dest.write_bytes(existing.read_bytes())
        print(f"  copied {existing.name} -> experiences/{exp_id}.jpg")
        return f"assets/images/experiences/{exp_id}.jpg"
    if download(url, dest):
        return f"assets/images/experiences/{exp_id}.jpg"
    if existing:
        dest.write_bytes(existing.read_bytes())
        return f"assets/images/experiences/{exp_id}.jpg"
    return None


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_experiences = []
    ok = 0
    fail = 0

    for exp in EXPERIENCES:
        entry = {k: v for k, v in exp.items() if k not in ("legacy", "tt_image")}
        if exp.get("legacy"):
            entry["image"] = LEGACY_IMAGES[exp["id"]]
            entry["signature"] = True
            ok += 1
        else:
            url = exp.get("tt_image", "")
            local = mirror_image(exp["id"], url)
            if local:
                entry["image"] = local
                ok += 1
            else:
                print(f"  SKIP {exp['id']} — no image")
                fail += 1
                continue
        output_experiences.append(entry)

    DATA_OUT.write_text(
        json.dumps({"experiences": output_experiences}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {len(output_experiences)} experiences -> {DATA_OUT.relative_to(ROOT)}")
    print(f"Images OK: {ok}, failed: {fail}")


if __name__ == "__main__":
    main()
