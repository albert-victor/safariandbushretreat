#!/usr/bin/env python3
"""Download one hero image per accommodation group from official websites (build time only)."""
from __future__ import annotations

import argparse
import json
import re
import ssl
import subprocess
import urllib.error
import urllib.request
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "accommodations.json"
OUT_DIR = ROOT / "assets" / "images" / "external" / "accommodations"
MIN_BYTES = 25_000

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Verified direct image URLs from each brand's official website/CDN.
DIRECT_IMAGES: dict[str, str] = {
    "singita": "https://images.ctfassets.net/wds1hqrprqxb/6iVCyzCDQlhymqwoSjsrX3/040ea3731c408fe18b689552cbe4a8e9/ellies_in_the_okavango_delta.jpg?w=1600&fm=jpg&q=90",
    "asilia-africa": "https://www.asiliaafrica.com/wp-content/uploads/2024/04/Asilia_Camp-Lodges_Highlands_Header-Images.jpg",
    "wilderness": "https://www.wildernessdestinations.com/media/uxlaotbx/lions-wilderness-botswana-vumbura-plains.jpg?rmode=max&width=1600",
    "elewana-collection": "https://www.elewanacollection.com/images/ttt/Tarangire-Treetops---accommodation---exterior-view-of-Treehouse-Suite.jpg",
    "serena-safari-lodges": "https://image-tc.galaxy.tf/wijpeg-exekalat0rqdwm3k6auc1e2gi/executive-room-2.jpg?width=1600",
    "lemala-camps": "https://www.lemalacamps.com/app/uploads/2021/10/Lemala-Ewanjan-34-min-scaled.jpg",
    "sanctuary-retreats": "https://cdn.abercrombiekent.com/images/bsiop5ln/production/85dc3ed43b1cf3f43ab3f0cb99f3b5215d52e4ae-2500x1667.jpg?w=1600&fm=jpg&fit=crop",
    "tanganyika-wilderness-camps": "https://twctanzania.com/wp-content/uploads/2023/08/AMP_7938-1024x683.jpg",
    "andbeyond": "https://www.andbeyond.com/wp-content/uploads/sites/5/Tanzania-Serengeti-Under-Canvas-SUC-Guest-Area-camp-exterior-with-lantern-walkway-and-Maasai-2_Website-1920x1080-fill-gravityauto-Q_AutoBest.jpg",
    "great-plains-conservation": "https://greatplainsconservation.com/wp-content/uploads/2023/09/GreatPlainsConservation-Brand-Refresh-Homepage-Hero.png",
    "nomad-tanzania": "https://www.nomad-tanzania.com/assets/uploads/images-craft/CS-090622-tangire-002.jpg",
    "sopa-lodges": "https://www.sopalodges.com/images/slider/tarangire.jpg",
    "governors-camp": "https://governorscamp.com/wp-content/uploads/2025/10/Website-1.jpg",
    "sarova-hotels": "https://www.sarovahotels.com/assets/images/memorable-exp-1.jpg",
    "porini-camps": "https://e8t95d9vg4g.exactdn.com/wp-content/uploads/2025/06/OKSC_CelineSacha_maasai_welcome_2024_1280x721.jpg",
    "heritage-hotels-kenya": "https://www.heritage-eastafrica.com/media/heritage-hotels-bannervoyager-68-1.webp",
    "volcanoes-safaris": "https://volcanoessafaris.com/storage/media-library/681/Gorilla-Trekking25042024_VolcanoesSafaris.jpg",
    "wilderness-rwanda": "https://www.wildernessdestinations.com/media/a4fn0oez/bisate_lodge_view.jpg?rmode=max&width=1600",
}

PROPERTY_PAGES: dict[str, list[str]] = {
    "singita": ["https://singita.com/lodge/singita-sasakwa/"],
    "asilia-africa": ["https://www.asiliaafrica.com/camps-lodges/the-highlands/"],
    "wilderness": ["https://www.wildernessdestinations.com/africa/tanzania"],
    "elewana-collection": ["https://www.elewanacollection.com/tarangire-treetops/"],
    "serena-safari-lodges": ["https://www.serenahotels.com/"],
    "lemala-camps": ["https://www.lemalacamps.com/stay/ewanjan-tented-camp/"],
    "sanctuary-retreats": ["https://www.sanctuaryretreats.com/sanctuary-kichakani-serengeti-camp"],
    "tanganyika-wilderness-camps": ["https://twctanzania.com/chada-camp-katavi/"],
    "andbeyond": ["https://www.andbeyond.com/our-lodges/africa/tanzania/serengeti-national-park/andbeyond-serengeti-under-canvas/"],
    "great-plains-conservation": ["https://greatplainsconservation.com/"],
    "nomad-tanzania": ["https://nomad-tanzania.com/camps-and-lodges/serengeti-safari-camp/"],
    "sopa-lodges": ["https://www.sopalodges.com/"],
    "governors-camp": ["https://governorscamp.com/"],
    "sarova-hotels": ["https://www.sarovahotels.com/sarova-mara-game-camp/"],
    "porini-camps": ["https://www.porini.com/"],
    "heritage-hotels-kenya": ["https://www.heritage-eastafrica.com/mount-kenya-safari-club/"],
    "volcanoes-safaris": ["https://volcanoessafaris.com/lodges/volcanoes-bwindi-lodge/"],
    "wilderness-rwanda": ["https://www.wildernessdestinations.com/africa/rwanda"],
}

INSECURE_SLUGS = {"volcanoes-safaris"}

META_PATTERNS = [
    re.compile(r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)["\']', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image(?::secure_url)?["\']', re.I),
    re.compile(r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)["\']', re.I),
]
IMG_RE = re.compile(r'(?:src|data-src)=["\']([^"\']+\.(?:jpg|jpeg|webp|png)[^"\']*)["\']', re.I)
SKIP = ("logo", "icon", "favicon", "sprite", "badge", "flag", "shield", "whatsapp", "pixel", "1x1", ".svg")
PREFER = ("lodge", "camp", "safari", "tent", "suite", "villa", "exterior", "aerial", "hero", "banner", "room", "accommodation", "treehouse", "gorilla", "migration")


def is_image(data: bytes) -> bool:
    if len(data) < MIN_BYTES:
        return False
    if data[:3] == b"\xff\xd8\xff":
        return True
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    if data[:4] == b"RIFF" and len(data) > 12 and data[8:12] == b"WEBP":
        return True
    return False


def curl_bytes(url: str) -> bytes | None:
    try:
        result = subprocess.run(
            ["curl.exe", "-sL", "-A", UA, url],
            capture_output=True,
            timeout=120,
            check=False,
        )
        return result.stdout if result.returncode == 0 and result.stdout else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def fetch_url(url: str, insecure: bool = False, referer: str | None = None) -> bytes | None:
    url = unescape(url.strip())
    headers = dict(HEADERS)
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=90, context=ctx) as resp:
            return resp.read()
    except (urllib.error.URLError, OSError):
        return curl_bytes(url)


def fetch_image(url: str, insecure: bool = False, referer: str | None = None) -> bytes | None:
    data = fetch_url(url, insecure=insecure, referer=referer)
    return data if data and is_image(data) else None


def ext_from_url(url: str) -> str:
    path = urlparse(url.split("?", 1)[0]).path.lower()
    for suffix in (".jpg", ".jpeg", ".png", ".webp"):
        if path.endswith(suffix):
            return suffix
    return ".jpg"


def save_bytes(slug: str, data: bytes, url: str) -> str:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob(f"{slug}.*"):
        old.unlink(missing_ok=True)
    ext = ext_from_url(url)
    dest = OUT_DIR / f"{slug}{ext}"
    dest.write_bytes(data)
    print(f"    OK {dest.name} ({len(data) // 1024} KB)")
    return f"external/accommodations/{dest.name}"


def score(url: str) -> int:
    lower = url.lower()
    if any(s in lower for s in SKIP):
        return -100
    s = 10
    if any(p in lower for p in PREFER):
        s += 20
    if any(x in lower for x in ("wp-content/uploads", "/media/", "/images/", "galaxy.tf", "ctfassets.net")):
        s += 15
    return s


def urls_from_html(html: str, base: str) -> list[str]:
    urls: list[str] = []
    for pattern in META_PATTERNS:
        for match in pattern.findall(html):
            urls.append(unescape(urljoin(base, match.strip())))
    for match in IMG_RE.findall(html):
        urls.append(unescape(urljoin(base, match.strip())))
    ranked = sorted(set(urls), key=score, reverse=True)
    return [u for u in ranked if score(u) > 0]


def collect_urls(group: dict) -> list[str]:
    slug = group["slug"]
    urls: list[str] = []
    if slug in DIRECT_IMAGES:
        urls.append(DIRECT_IMAGES[slug])
    for page in PROPERTY_PAGES.get(slug, []):
        html_bytes = fetch_url(page, insecure=slug in INSECURE_SLUGS)
        if html_bytes:
            html = html_bytes.decode("utf-8", errors="replace")
            urls.extend(urls_from_html(html, page))
    site = group.get("officialWebsite", "")
    if site:
        html_bytes = fetch_url(site, insecure=slug in INSECURE_SLUGS)
        if html_bytes:
            html = html_bytes.decode("utf-8", errors="replace")
            urls.extend(urls_from_html(html, site))
    seen: set[str] = set()
    ordered: list[str] = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            ordered.append(url)
    return ordered


def try_download(slug: str, urls: list[str]) -> str | None:
    insecure = slug in INSECURE_SLUGS
    referer = PROPERTY_PAGES.get(slug, [None])[0]
    for url in urls:
        if not url.startswith("http"):
            continue
        data = fetch_image(url, insecure=insecure, referer=referer or url)
        if data:
            return save_bytes(slug, data, url)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    payload = json.loads(DATA.read_text(encoding="utf-8"))
    updated = False

    # Fix outdated official URLs in data while fetching.
    official_fixes = {
        "lemala-camps": "https://www.lemalacamps.com/",
        "tanganyika-wilderness-camps": "https://twctanzania.com/",
    }

    for group in payload["groups"]:
        slug = group["slug"]
        if slug in official_fixes:
            group["officialWebsite"] = official_fixes[slug]
        print(f"\n{group['name']}")
        if not args.force:
            existing = list(OUT_DIR.glob(f"{slug}.*"))
            if existing and is_image(existing[0].read_bytes()[:32]):
                print(f"    keep {existing[0].name}")
                continue
        rel = try_download(slug, collect_urls(group))
        if rel:
            group["image"] = rel
            updated = True
        else:
            print(f"    WARN no image for {slug}")

    if updated:
        DATA.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("\nDone.")


if __name__ == "__main__":
    main()
