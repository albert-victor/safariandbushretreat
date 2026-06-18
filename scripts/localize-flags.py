#!/usr/bin/env python3
"""Download testimonial flag images and rewrite index.html to use local paths."""
from __future__ import annotations

import re
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAGS_DIR = ROOT / "assets" / "images" / "flags"
INDEX = ROOT / "index.html"

CODES = ("us", "gb", "de", "fr", "au", "jp", "za", "nl", "ca", "it", "se", "br", "es", "il", "in")
UA = "Mozilla/5.0 (compatible; SafariBushLocalize/1.0)"


def download(code: str) -> None:
    dest = FLAGS_DIR / f"{code}.png"
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  exists {code}.png")
        return
    url = f"https://flagcdn.com/w40/{code}.png"
    FLAGS_DIR.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        dest.write_bytes(resp.read())
    print(f"  saved {code}.png")


def main() -> None:
    print("Downloading flags...")
    for code in CODES:
        download(code)

    text = INDEX.read_text(encoding="utf-8")
    updated = re.sub(
        r"https://flagcdn\.com/w40/([a-z]{2})\.png",
        r"assets/images/flags/\1.png",
        text,
    )
    if updated != text:
        INDEX.write_text(updated, encoding="utf-8")
        print("Updated index.html flag paths.")
    else:
        print("index.html already uses local flags.")


if __name__ == "__main__":
    main()
