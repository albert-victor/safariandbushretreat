#!/usr/bin/env python3
import re, ssl, urllib.request
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
ctx = ssl.create_default_context()
BASE = "https://exploreuganda.com"

PARKS = [
    "bwindi-impenetrable-national-park",
    "murchison-falls-national-park",
    "kibale-valley-national-park",
    "queen-elizabeth-national-park",
    "mgahinga-gorilla-national-park",
    "rwenzori-mountains-national-park",
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

def imgs(html):
    out, seen = [], set()
    for u in re.findall(r'(?:src|data-src)=["\']([^"\']+wp-content/uploads[^"\']+)["\']', html, re.I):
        if any(x in u.lower() for x in ("logo", "icon")):
            continue
        if u not in seen:
            seen.add(u); out.append(u)
    return out

for slug in PARKS:
    url = f"{BASE}/{slug}/"
    try:
        found = imgs(fetch(url))
        print(f"\n{slug} ({len(found)})")
        for u in found[:4]:
            print(" ", u.split("/")[-1])
    except Exception as e:
        print(slug, e)
