#!/usr/bin/env python3
"""Download fonts, Font Awesome, and Swiper for self-hosting."""
from __future__ import annotations

import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
WOFF2_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

FONTS_CSS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&"
    "family=Montserrat:wght@400;500;600;700&display=swap"
)
FA_CSS_URL = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
SWIPER_CSS_URL = "https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"
SWIPER_JS_URL = "https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"


def fetch(url: str, dest: Path) -> bytes:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": WOFF2_UA if "fonts" in url else UA})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return data


def setup_fonts() -> None:
    fonts_dir = VENDOR / "fonts"
    files_dir = fonts_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    css = fetch(FONTS_CSS_URL, fonts_dir / "google.css").decode("utf-8")
    urls = re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css)
    mapping: dict[str, str] = {}
    for url in urls:
        fname = Path(url.split("?", 1)[0]).name
        local = files_dir / fname
        if not local.exists():
            fetch(url, local)
            print(f"  font {fname}")
        mapping[url] = f"files/{fname}"

    local_css = css
    for remote, rel in mapping.items():
        local_css = local_css.replace(f"url({remote})", f"url({rel})")
    (fonts_dir / "fonts.css").write_text(local_css, encoding="utf-8")
    print(f"  wrote vendor/fonts/fonts.css ({len(mapping)} files)")


def setup_font_awesome() -> None:
    fa_dir = VENDOR / "font-awesome"
    css_path = fa_dir / "css" / "all.min.css"
    css = fetch(FA_CSS_URL, css_path).decode("utf-8")

    webfonts_dir = fa_dir / "webfonts"
    webfonts_dir.mkdir(parents=True, exist_ok=True)
    for match in re.finditer(r"url\(\.\./webfonts/([^)]+)\)", css):
        fname = match.group(1).split("?", 1)[0]
        remote = f"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/webfonts/{fname}"
        dest = webfonts_dir / fname
        if not dest.exists():
            fetch(remote, dest)
            print(f"  fa {fname}")

    # Paths in all.min.css are already ../webfonts/ - correct for css/all.min.css
    print("  wrote vendor/font-awesome/")


def setup_swiper() -> None:
    swiper_dir = VENDOR / "swiper"
    fetch(SWIPER_CSS_URL, swiper_dir / "swiper-bundle.min.css")
    fetch(SWIPER_JS_URL, swiper_dir / "swiper-bundle.min.js")
    print("  wrote vendor/swiper/")


def main() -> None:
    print("=== Fonts ===")
    setup_fonts()
    print("\n=== Font Awesome ===")
    setup_font_awesome()
    print("\n=== Swiper ===")
    setup_swiper()
    print("\nVendor assets ready.")


if __name__ == "__main__":
    main()
