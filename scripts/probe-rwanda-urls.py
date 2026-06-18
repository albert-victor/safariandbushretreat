#!/usr/bin/env python3
import re, ssl, urllib.request
UA = "Mozilla/5.0"
ctx = ssl.create_default_context()

def urls(page):
    html = urllib.request.urlopen(
        urllib.request.Request(page, headers={"User-Agent": UA}),
        context=ctx, timeout=45,
    ).read().decode("utf-8", "replace")
    found = re.findall(r"https://visitrwanda\.com/wp-content/uploads/fly-images/\d+/[^\s\"'<>]+", html)
    return sorted(set(u.rstrip(")") for u in found))

for page in [
    "https://www.visitrwanda.com/tourism/destinations/towns/",
    "https://www.visitrwanda.com/",
]:
    print(f"\n=== {page} ===")
    for u in urls(page):
        if any(k in u.lower() for k in ("kigali", "nyanza", "huye", "rubavu", "musanze", "rusizi", "kibeho", "karongi", "kivu", "1650", "1920", "kayak", "fishermen", "img_0729")):
            print(u)
