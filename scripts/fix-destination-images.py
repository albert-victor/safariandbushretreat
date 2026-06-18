#!/usr/bin/env python3
"""Fix destination entries with invalid hero/gallery URLs."""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "destinations.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"


def bad(url: str | None) -> bool:
    return not url or "logo" in url.lower() or "/logos/" in url


def fetch_images(tt_slug: str):
    url = f"https://www.tanzaniatourism.com/destination/{tt_slug}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  fetch fail {tt_slug}: {e}")
        return None, []
    og = re.search(r'property="og:image" content="([^"]+)"', html)
    hero = og.group(1) if og else None
    gallery = re.findall(
        r'href="(https://www\.tanzaniatourism\.com/images/uploads/[^"]+\.(?:jpg|jpeg|png))"',
        html,
    )
    gallery = [g for g in dict.fromkeys(gallery) if not bad(g)]
    if bad(hero):
        hero = gallery[0] if gallery else None
    return hero, gallery[:2]


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    fixed = 0
    for d in data["destinations"]:
        if bad(d.get("hero", "")) or any(bad(g) for g in d.get("gallery", [])):
            hero, gallery = fetch_images(d["tt_slug"])
            if hero:
                d["hero"] = hero
                d["gallery"] = gallery or [hero]
                fixed += 1
                print(f"Fixed {d['slug']}")
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Fixed {fixed} destinations.")


if __name__ == "__main__":
    main()
