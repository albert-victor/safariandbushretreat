#!/usr/bin/env python3
"""Download external images and rewrite JSON/HTML to use local paths."""
from __future__ import annotations

import json
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
KENYA_DATA = ROOT / "data" / "kenya-data.json"
TANZANIA_CORE = ROOT / "data" / "tanzania-core.json"
INDEX_HTML = ROOT / "index.html"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DIRS = {
    "kenya": ROOT / "assets" / "images" / "external" / "kenya",
    "unsplash": ROOT / "assets" / "images" / "external" / "unsplash",
    "tt": ROOT / "assets" / "images" / "external" / "tt",
}

UNSPLASH_PHOTO_RE = re.compile(r"photo-\d+-[a-f0-9]+")
URL_RE = re.compile(r"https?://[^\s\"'<>]+")


def filename_from_url(url: str, category: str) -> str:
    parsed = urlparse(url.split("?", 1)[0])
    name = Path(unquote(parsed.path)).name or "image.jpg"
    if category == "unsplash":
        match = UNSPLASH_PHOTO_RE.search(url)
        if match:
            return f"{match.group(0)}.jpg"
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")
    return name or "image.jpg"


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  exists {dest.name}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            data = resp.read()
        if len(data) < 500:
            print(f"  WARN small file {dest.name} ({len(data)} bytes)")
        dest.write_bytes(data)
        print(f"  saved {dest.name} ({len(data) // 1024} KB)")
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"  FAIL {url}: {exc}")
        return False


def local_path(category: str, filename: str) -> str:
    return f"external/{category}/{filename}"


def mirror_url(url: str, category: str, cache: dict[str, str]) -> str:
    if not url.startswith("http"):
        return url
    if url in cache:
        return cache[url]
    fname = filename_from_url(url, category)
    dest = DIRS[category] / fname
    if download(url, dest):
        rel = local_path(category, fname)
        cache[url] = rel
        return rel
    return url


def walk_json_strings(obj, category: str, cache: dict[str, str]):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ("source",) and isinstance(value, str) and value.startswith("http"):
                continue
            obj[key] = walk_json_strings(value, category, cache)
        return obj
    if isinstance(obj, list):
        return [walk_json_strings(item, category, cache) for item in obj]
    if isinstance(obj, str) and obj.startswith("http"):
        if "unsplash.com" in obj:
            cat = "unsplash"
        elif "tanzaniatourism.com" in obj:
            cat = "tt"
        elif "safarijunctions.com" in obj or "i0.wp.com" in obj:
            cat = "kenya"
        else:
            return obj
        return mirror_url(obj, cat, cache)
    return obj


def unsplash_best_url(photo_id: str) -> str:
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1920&q=85"


def mirror_index_unsplash(cache: dict[str, str]) -> None:
    html = INDEX_HTML.read_text(encoding="utf-8")
    photo_ids = sorted(set(UNSPLASH_PHOTO_RE.findall(html)))
    print(f"\nindex.html: {len(photo_ids)} unique Unsplash photos")
    replacements: dict[str, str] = {}
    for photo_id in photo_ids:
        url = unsplash_best_url(photo_id)
        rel = mirror_url(url, "unsplash", cache)
        if rel.startswith("external/"):
            local_src = f"assets/images/{rel}"
            replacements[f"https://images.unsplash.com/{photo_id}"] = local_src
            # Also handle encoded ampersands in older markup
            replacements[f"https://images.unsplash.com/{photo_id}?auto=format&amp;fit=crop&amp;w=800&amp;q=85"] = (
                f"assets/images/{rel.replace(' ', '%20')}"
            )

    for old_prefix, new_prefix in replacements.items():
        html = html.replace(old_prefix, new_prefix)

    # Strip Unsplash-specific query strings now pointing at local files
    html = re.sub(
        r'(assets/images/external/unsplash/photo-\d+-[a-f0-9]+\.jpg)\?[^"\s>]+',
        r"\1",
        html,
    )
    INDEX_HTML.write_text(html, encoding="utf-8")
    print("  updated index.html")


def main() -> None:
    cache: dict[str, str] = {}

    print("=== Kenya data ===")
    kenya = json.loads(KENYA_DATA.read_text(encoding="utf-8"))
    kenya = walk_json_strings(kenya, "kenya", cache)
    KENYA_DATA.write_text(json.dumps(kenya, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  updated {KENYA_DATA.relative_to(ROOT)}")

    print("\n=== Tanzania core (TT heroes) ===")
    core = json.loads(TANZANIA_CORE.read_text(encoding="utf-8"))
    core = walk_json_strings(core, "tt", cache)
    TANZANIA_CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  updated {TANZANIA_CORE.relative_to(ROOT)}")

    mirror_index_unsplash(cache)

    manifest = ROOT / "data" / "external-mirror-map.json"
    manifest.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    print(f"\nMirrored {len(cache)} URLs -> {manifest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
