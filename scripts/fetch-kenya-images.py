#!/usr/bin/env python3
"""Download unique Kenya destination images from Safari Junctions and Unsplash."""
from __future__ import annotations

import json
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KENYA_DATA = ROOT / "data" / "kenya-data.json"
KENYA_DIR = ROOT / "assets" / "images" / "external" / "kenya"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Curated Unsplash images - one unique photo per Kenya destination
KENYA_UNSPLASH = {
    "kenya": "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=1920&q=85",
    "masai-mara": "https://images.unsplash.com/photo-1547972570-776740847382?auto=format&fit=crop&w=1920&q=85",
    "amboseli": "https://images.unsplash.com/photo-1589552819647-2f3d2079a8b7?auto=format&fit=crop&w=1920&q=85",
    "samburu": "https://images.unsplash.com/photo-1564760055775-d263b025a55a?auto=format&fit=crop&w=1920&q=85",
    "lake-nakuru": "https://images.unsplash.com/photo-1609137144813-7d992133a935?auto=format&fit=crop&w=1920&q=85",
    "lake-naivasha": "https://images.unsplash.com/photo-1505142468610-359e7d316be0?auto=format&fit=crop&w=1920&q=85",
    "diani-beach": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?auto=format&fit=crop&w=1920&q=85",
}

GALLERY_UNSPLASH = {
    "kenya": [
        "https://images.unsplash.com/photo-1635328637451-be137d8fae03?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1726075016723-6ea81c84925c?auto=format&fit=crop&w=1200&q=85",
    ],
    "masai-mara": [
        "https://images.unsplash.com/photo-1523805009345-7448845a9e3e?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1535338455202-70d239086763?auto=format&fit=crop&w=1200&q=85",
    ],
    "amboseli": [
        "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=1200&q=85",
    ],
    "samburu": [
        "https://images.unsplash.com/photo-1549366021-9f761d040562?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1564760055775-d263b025a55a?auto=format&fit=crop&w=1200&q=85",
    ],
    "lake-nakuru": [
        "https://images.unsplash.com/photo-1609137144813-7d992133a935?auto=format&fit=crop&w=1200&q=85",
    ],
    "lake-naivasha": [
        "https://images.unsplash.com/photo-1505142468610-359e7d316be0?auto=format&fit=crop&w=1200&q=85",
    ],
    "diani-beach": [
        "https://images.unsplash.com/photo-1559827260-dc66d52bef19?auto=format&fit=crop&w=1200&q=85",
        "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=85",
    ],
}


def photo_id(url: str) -> str:
    m = re.search(r"photo-\d+-[a-f0-9]+", url)
    return m.group(0) if m else re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(url.split("?")[0]).name)


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 2000:
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            data = resp.read()
        if len(data) < 1000:
            print(f"  WARN small {dest.name}")
            return False
        dest.write_bytes(data)
        print(f"  saved {dest.name} ({len(data) // 1024} KB)")
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"  FAIL {url}: {exc}")
        return False


def mirror(url: str, prefix: str) -> str:
    fname = f"{prefix}-{photo_id(url)}.jpg"
    dest = KENYA_DIR / fname
    if download(url, dest):
        return f"external/kenya/{fname}"
    return url


def scrape_sj_kenya() -> list[str]:
    url = "https://www.safarijunctions.com/destinations/kenya/"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    imgs = re.findall(
        r"https?://(?:www\.safarijunctions\.com|i0\.wp\.com)[^\s\"'<>]+\.(?:jpg|jpeg|png|webp)",
        html,
        re.I,
    )
    out = []
    seen = set()
    for u in imgs:
        u = u.split("?", 1)[0]
        if "logo" in u.lower() or u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out[:12]


def main():
    sj_imgs = scrape_sj_kenya()
    print(f"Safari Junction page: {len(sj_imgs)} images found")
    for i, u in enumerate(sj_imgs[:3]):
        print(f"  SJ[{i}]: {u[:90]}")

    data = json.loads(KENYA_DATA.read_text(encoding="utf-8"))

    # Overview hero from SJ if available, else Unsplash
    if sj_imgs:
        data["kenya"]["hero"] = mirror(sj_imgs[0], "kenya-overview")
        if len(sj_imgs) > 1:
            data["kenya"]["gallery"] = [
                mirror(sj_imgs[1], "kenya-gallery-1"),
                mirror(sj_imgs[2], "kenya-gallery-2") if len(sj_imgs) > 2 else mirror(KENYA_UNSPLASH["kenya"], "kenya-gallery-2"),
            ]
    else:
        data["kenya"]["hero"] = mirror(KENYA_UNSPLASH["kenya"], "kenya-overview")
        data["kenya"]["gallery"] = [mirror(u, f"kenya-gallery-{i}") for i, u in enumerate(GALLERY_UNSPLASH["kenya"])]

    for d in data["destinations"]:
        slug = d["slug"]
        hero_url = KENYA_UNSPLASH.get(slug)
        if hero_url:
            d["hero"] = mirror(hero_url, slug)
        gal_urls = GALLERY_UNSPLASH.get(slug, [])
        d["gallery"] = [mirror(u, f"{slug}-gal-{i}") for i, u in enumerate(gal_urls)]

    KENYA_DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nUpdated {KENYA_DATA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
