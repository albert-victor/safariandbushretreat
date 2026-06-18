#!/usr/bin/env python3
"""Scrape and download unique Uganda/Rwanda images from official tourism sites."""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
UGANDA_DATA = ROOT / "data" / "uganda-data.json"
RWANDA_DATA = ROOT / "data" / "rwanda-data.json"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SKIP_WORDS = (
    "logo", "icon", "favicon", "avatar", "sprite", "placeholder",
    "lodge", "camp", "hotel", "resort", "sanctuary", "accommodation",
    "booking", "banner-ad",
)

# slug -> page URL to scrape (exploreuganda.com)
UGANDA_PAGES: dict[str, str | None] = {
    "uganda": "https://exploreuganda.com/national-parks/",
    "bwindi-impenetrable": "https://exploreuganda.com/national-parks/bwindi-impenetrable-national-park/",
    "murchison-falls": "https://exploreuganda.com/murchison-falls-national-park/",
    "kibale": "https://exploreuganda.com/kibale-valley-national-park/",
    "queen-elizabeth": "https://exploreuganda.com/queen-elizabeth-national-park/",
    "kidepo-valley": "https://exploreuganda.com/national-parks/",
    "lake-mburo": "https://exploreuganda.com/national-parks/",
    "mgahinga-gorilla": "https://exploreuganda.com/mgahinga-gorilla-national-park/",
    "rwenzori-mountains": "https://exploreuganda.com/rwenzori-mountains-national-park/",
    "mount-elgon": "https://exploreuganda.com/mount-elgon-national-park/",
    "semuliki": "https://exploreuganda.com/semuliki-national-park/",
    "kampala": "https://exploreuganda.com/cities/",
    "jinja": "https://exploreuganda.com/cities/",
    "entebbe": "https://exploreuganda.com/cities/",
    "mbarara": "https://exploreuganda.com/cities/",
    "mbale": "https://exploreuganda.com/cities/",
    "gulu": "https://exploreuganda.com/cities/",
}

# slug -> (hero_url, [gallery_urls]) direct from official CDN when scrape needs hints
UGANDA_DIRECT: dict[str, tuple[str, list[str]]] = {
    "uganda": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/Gorilla-Bwindi.jpg",
        [
            "https://exploreuganda.com/wp-content/uploads/2024/10/Murchison-falls-boat-cruise.jpg",
            "https://exploreuganda.com/wp-content/uploads/2024/10/chimpanzee-in-Kibale.jpg",
        ],
    ),
    "bwindi-impenetrable": (
        "https://exploreuganda.com/wp-content/uploads/2024/07/BINP-202-scaled.jpg",
        ["https://exploreuganda.com/wp-content/uploads/2024/10/Gorilla-Bwindi.jpg"],
    ),
    "murchison-falls": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/Murchison-top-of-the-falls.jpg",
        [
            "https://exploreuganda.com/wp-content/uploads/2024/10/Murchison-elephants.jpg",
            "https://exploreuganda.com/wp-content/uploads/2024/10/Murchison-Boat-cruise.jpg",
        ],
    ),
    "kibale": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/chimpanzee-in-Kibale.jpg",
        [
            "https://exploreuganda.com/wp-content/uploads/2024/10/Chimpanzee-in-Kibale-1.jpg",
            "https://exploreuganda.com/wp-content/uploads/2024/10/Kibale-birds-1.jpg",
        ],
    ),
    "queen-elizabeth": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/Leopard-Queen.jpg",
        [
            "https://exploreuganda.com/wp-content/uploads/2024/10/Queen-Elizabeth-Lion.jpg",
            "https://exploreuganda.com/wp-content/uploads/2024/10/Queen-Elizabeth-Elephants.jpg",
        ],
    ),
    "kidepo-valley": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/kidepo-Valley-NP-1.jpg",
        [],
    ),
    "lake-mburo": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/zebras-lake-mburo.jpg",
        [],
    ),
    "mgahinga-gorilla": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/mgahinga-gorilla-NP.jpg",
        [
            "https://exploreuganda.com/wp-content/uploads/2024/10/Mgahinga-Gorilla-.jpg",
            "https://exploreuganda.com/wp-content/uploads/2024/10/Mgahinga-Monkey.jpg",
        ],
    ),
    "rwenzori-mountains": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/Rwenzori-mountains-Stanley-Peak.jpg",
        [
            "https://exploreuganda.com/wp-content/uploads/2024/10/Mount-Rwenzori-Peak-1.jpg",
            "https://exploreuganda.com/wp-content/uploads/2024/10/Mount-Rwenzori-vegetation.jpg",
        ],
    ),
    "mount-elgon": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/SipiFalls.jpg",
        [
            "https://exploreuganda.com/wp-content/uploads/2024/10/Mount-Elgon-National-Park-1.jpg",
            "https://exploreuganda.com/wp-content/uploads/2024/10/Mount-Elgon-National-Park-Trail.jpg",
        ],
    ),
    "semuliki": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/Semuliki-National-Park-1.jpg",
        [
            "https://exploreuganda.com/wp-content/uploads/2024/10/Semuliki-National-Park-2-.jpg",
            "https://exploreuganda.com/wp-content/uploads/2024/10/Semuliki-birds-1.jpg",
        ],
    ),
    "kampala": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/kampala-road.jpg",
        ["https://exploreuganda.com/wp-content/uploads/2024/07/HDI_5548-scaled.jpg"],
    ),
    "jinja": (
        "https://exploreuganda.com/wp-content/uploads/2024/09/Whitewater-Kayak-Kayak-the-Nile-12-scaled.jpeg",
        [],
    ),
    "entebbe": (
        "https://exploreuganda.com/wp-content/uploads/2024/06/entebbe.jpeg",
        [],
    ),
    "mbarara": (
        "https://exploreuganda.com/wp-content/uploads/2024/10/mbarara.jpg",
        [],
    ),
    "mbale": (
        "https://exploreuganda.com/wp-content/uploads/2024/06/mbale.jpeg",
        [],
    ),
    "gulu": (
        "https://exploreuganda.com/wp-content/uploads/2024/06/gulu.jpeg",
        [],
    ),
}

RWANDA_DIRECT: dict[str, tuple[str, list[str]]] = {
    "rwanda": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/18304/Lake-Kivu-1920x1079.jpeg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1641/Visit-Rwanda-Volcano-1650x1100.jpg",
            "https://visitrwanda.com/wp-content/uploads/fly-images/1409/Visit-Rwanda-Akagera-from-Safari-Vehicle-1650x1100.jpg",
        ],
    ),
    "volcanoes": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1641/Visit-Rwanda-Volcano-1650x1100.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1536/Visit-Rwanda_-Volcanoes-National-Park-Silverback-in-Bamboo-1-700x467.jpg",
            "https://visitrwanda.com/wp-content/uploads/fly-images/1545/Visit-Rwanda-Kwita-Izina-Baby-Gorilla-2-700x467.jpg",
        ],
    ),
    "akagera": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1409/Visit-Rwanda-Akagera-from-Safari-Vehicle-1650x1100.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1418/Visit-Rwanda-Akagera-Lion-in-Tree-1-e1533313181412-700x461.jpg",
            "https://visitrwanda.com/wp-content/uploads/fly-images/1433/Visit-Rwanda-Akagera-Three-Zebra-700x467.jpg",
        ],
    ),
    "nyungwe": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/3619/canopy-1650x1014.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1336/Visit-Rwanda-NH_OO_Activities_Chimpanzee_Trek_6853_MASTER-700x467.jpg",
            "https://visitrwanda.com/wp-content/uploads/fly-images/1636/Visit-Rwanda-Canopy-Walkway-Trail-700x467.jpg",
        ],
    ),
    "gishwati-mukura": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/2421/Visit-Rwanda-Gishwati-Mukura-National-Park-1650x928.jpg",
        [],
    ),
    "kigali": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1203/Visit-Rwanda_-Kigali-Skyline-to-CBD-1280x853.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1212/Visit-Rwanda_-Kigali-Convention-Centre-1280x853.jpg",
        ],
    ),
    "nyanza": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1234/Visit-Rwanda-Kings-Palace-Nyanza-Front-1650x1100.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1781/Visit-Rwanda_-Nyanza-Traditional-Dancers-1280x853.jpg",
        ],
    ),
    "huye": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1248/Visit-Rwanda-Huye-Town-700x467.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1617/Visit-Rwanda-Paramotoring-Huye-700x467.jpg",
        ],
    ),
    "rubavu": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1265/Visit-Rwanda-Rubavu-Beach-Credit-Jule-Lumma-1650x1100.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1265/Visit-Rwanda-Rubavu-Beach-Credit-Jule-Lumma-700x467.jpg",
        ],
    ),
    "karongi": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/16387/IMG_0729-700x456.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1639/Visit-Rwanda-Singing-Fishermen-700x467.jpg",
            "https://visitrwanda.com/wp-content/uploads/fly-images/1654/Visit-Rwanda_-Lake-Kivu-Kayak-to-Islands-1-700x394.jpg",
        ],
    ),
    "musanze": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1523/Visit-Rwanda-Musanze-Drone-Sunset-700x525.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1611/Musanze-Caves-700x466.jpg",
        ],
    ),
    "rusizi": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1314/Visit-Rwanda-Rusizi-District-1650x1100.jpg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1314/Visit-Rwanda-Rusizi-District-700x467.jpg",
        ],
    ),
    "kibeho": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/1297/Visit-Rwanda-Kibeho-Church-Credit-Elena-Hermosa-700x467.jpg",
        [],
    ),
    "lake-kivu": (
        "https://visitrwanda.com/wp-content/uploads/fly-images/18304/Lake-Kivu-1920x1079.jpeg",
        [
            "https://visitrwanda.com/wp-content/uploads/fly-images/1181/Visit-Rwanda_-Lake-Kivu-Drone-of-Islands-700x525.jpg",
            "https://visitrwanda.com/wp-content/uploads/fly-images/1654/Visit-Rwanda_-Lake-Kivu-Kayak-to-Islands-1-700x394.jpg",
        ],
    ),
}

# Keywords to match listing-page images to slug when page is shared
UGANDA_KEYWORDS: dict[str, tuple[str, ...]] = {
    "kidepo-valley": ("kidepo",),
    "lake-mburo": ("mburo", "zebra"),
    "kampala": ("kampala",),
    "jinja": ("kayak", "nile", "whitewater"),
    "entebbe": ("entebbe",),
    "mbarara": ("mbarara",),
    "mbale": ("mbale",),
    "gulu": ("gulu",),
}


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_images(html: str, base_url: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    patterns = [
        r'(?:src|data-src|data-lazy-src|content)=["\']([^"\']+)["\']',
        r'"(https?://[^"]+\.(?:jpg|jpeg|png|webp)(?:\?[^"]*)?)"',
    ]
    for pat in patterns:
        for raw in re.findall(pat, html, re.I):
            u = raw.replace("\\/", "/").strip()
            if u.startswith("//"):
                u = "https:" + u
            elif u.startswith("/"):
                u = urljoin(base_url, u)
            if not re.search(r"\.(?:jpg|jpeg|png|webp)(?:\?|$)", u, re.I):
                continue
            low = u.lower()
            if any(w in low for w in SKIP_WORDS):
                continue
            if u not in seen:
                seen.add(u)
                found.append(u)
    return found


def image_score(url: str, keywords: tuple[str, ...]) -> int:
    name = urlparse(url).path.lower()
    score = 0
    if "scaled" in name or "1920" in name or "1650" in name or "1280" in name:
        score += 30
    if "wp-content/uploads" in name or "fly-images" in name:
        score += 10
    for kw in keywords:
        if kw in name:
            score += 50
    if any(x in name for x in ("gorilla", "falls", "lion", "elephant", "chimp", "zebra", "mountain", "lake", "beach", "town", "city", "palace", "church", "canopy", "akagera", "volcano", "nyungwe", "kivu")):
        score += 15
    return score


def pick_from_page(slug: str, html: str, base_url: str) -> tuple[str | None, list[str]]:
    keywords = UGANDA_KEYWORDS.get(slug, (slug.replace("-", " ").split()[0],))
    if slug.startswith("bwindi"):
        keywords = ("bwindi", "gorilla", "binp")
    elif slug == "murchison-falls":
        keywords = ("murchison", "falls")
    elif slug == "kibale":
        keywords = ("kibale", "chimp")
    elif slug == "queen-elizabeth":
        keywords = ("queen", "leopard", "lion")
    imgs = extract_images(html, base_url)
    ranked = sorted(imgs, key=lambda u: image_score(u, keywords), reverse=True)
    if not ranked:
        return None, []
    hero = ranked[0]
    gallery = []
    for u in ranked[1:]:
        if u != hero and u not in gallery:
            gallery.append(u)
        if len(gallery) >= 2:
            break
    return hero, gallery


def ext_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for e in (".jpeg", ".jpg", ".png", ".webp"):
        if path.endswith(e):
            return e if e != ".jpeg" else ".jpg"
    return ".jpg"


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": urlparse(url).scheme + "://" + urlparse(url).netloc})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
            data = resp.read()
        if len(data) < 3000:
            print(f"  WARN too small {dest.name} ({len(data)} bytes)")
            return False
        dest.write_bytes(data)
        print(f"  saved {dest.name} ({len(data) // 1024} KB) <- {url.split('/')[-1][:50]}")
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"  FAIL {dest.name}: {exc}")
        return False


def mirror(url: str, dest: Path) -> str | None:
    if download(url, dest):
        return str(dest.relative_to(ROOT / "assets" / "images")).replace("\\", "/")
    return None


def resolve_urls(slug: str, direct: tuple[str, list[str]], page_url: str | None) -> tuple[str, list[str]]:
    hero, gallery = direct[0], [g for g in direct[1] if g != direct[0]]
    # Only scrape individual park pages - never shared listing/city pages
    shared_pages = {
        "https://exploreuganda.com/national-parks/",
        "https://exploreuganda.com/cities/",
    }
    if page_url and page_url not in shared_pages:
        try:
            html = fetch_html(page_url)
            _, scraped_gal = pick_from_page(slug, html, page_url)
            if scraped_gal:
                gallery = scraped_gal
            time.sleep(0.3)
        except (urllib.error.URLError, OSError) as exc:
            print(f"  scrape skip {slug}: {exc}")
    gallery = [g for g in gallery if g != hero][:2]
    return hero, gallery


def apply_country(
    data: dict,
    country_key: str,
    direct_map: dict[str, tuple[str, list[str]]],
    page_map: dict[str, str | None],
    out_dir: Path,
) -> None:
    used_hashes: set[str] = set()

    def save_slug_images(slug: str, hero_url: str, gallery_urls: list[str]) -> tuple[str, list[str]]:
        ext = ext_from_url(hero_url)
        hero_dest = out_dir / f"{slug}{ext}"
        hero_path = mirror(hero_url, hero_dest)
        if not hero_path:
            raise RuntimeError(f"Could not download hero for {slug}")

        gal_paths = []
        for i, gurl in enumerate(gallery_urls):
            if gurl == hero_url:
                continue
            gext = ext_from_url(gurl)
            gdest = out_dir / f"{slug}-gal-{i}{gext}"
            gpath = mirror(gurl, gdest)
            if gpath and gpath != hero_path:
                gal_paths.append(gpath)
        return hero_path, gal_paths

    overview = data[country_key]
    slug = country_key
    hero_url, gal_urls = resolve_urls(slug, direct_map[slug], page_map.get(slug))
    overview["hero"], overview["gallery"] = save_slug_images(slug, hero_url, gal_urls)
    print(f"{slug}: hero={overview['hero']}")

    for d in data.get("destinations", []):
        dslug = d["slug"]
        if dslug not in direct_map:
            print(f"  skip unknown slug {dslug}")
            continue
        hero_url, gal_urls = resolve_urls(dslug, direct_map[dslug], page_map.get(dslug))
        d["hero"], d["gallery"] = save_slug_images(dslug, hero_url, gal_urls)
        print(f"  {dslug}: hero={d['hero']}")


def main() -> None:
    uganda_dir = ROOT / "assets" / "images" / "external" / "uganda"
    rwanda_dir = ROOT / "assets" / "images" / "external" / "rwanda"
    uganda_dir.mkdir(parents=True, exist_ok=True)
    rwanda_dir.mkdir(parents=True, exist_ok=True)

    uganda_data = json.loads(UGANDA_DATA.read_text(encoding="utf-8"))
    apply_country(uganda_data, "uganda", UGANDA_DIRECT, UGANDA_PAGES, uganda_dir)
    UGANDA_DATA.write_text(json.dumps(uganda_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {UGANDA_DATA.relative_to(ROOT)}\n")

    rwanda_data = json.loads(RWANDA_DATA.read_text(encoding="utf-8"))
    apply_country(rwanda_data, "rwanda", RWANDA_DIRECT, {}, rwanda_dir)
    RWANDA_DATA.write_text(json.dumps(rwanda_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {RWANDA_DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
