#!/usr/bin/env python3
"""Report external runtime dependencies in live site files (not scrape templates)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"scripts", "vendor", "node_modules", "data"}

# Allowed external patterns (outbound links / SEO / form submit - not page assets)
ALLOW = (
    "schema.org",
    "safariandbushretreats.com",
    "wa.me/",
    "tripadvisor.com",
    "safaribookings.com",
    "formsubmit.co",
    "tanzaniatourism.com",
    "safarijunctions.com",
    "singita.com",
    "asiliaafrica.com",
    "wildernessdestinations.com",
    "elewanacollection.com",
    "serenahotels.com",
    "lemalacamps.com",
    "sanctuaryretreats.com",
    "twctanzania.com",
    "andbeyond.com",
    "greatplainsconservation.com",
    "nomad-tanzania.com",
    "sopalodges.com",
    "governorscamp.com",
    "sarovahotels.com",
    "porini.com",
    "heritage-eastafrica.com",
    "volcanoesafaris.com",
)

ATTR_RE = re.compile(
    r'(?:href|src|srcset|content|poster|data-[a-z-]+)=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s\"'<>]+")


def is_runtime_asset(url: str, attr: str) -> bool:
    if any(url.startswith("https://" + host) or host in url for host in ALLOW):
        return False
    if attr == "content" and ("og:" in attr or "twitter:" in attr or "canonical" in attr):
        return False
    return True


def main() -> None:
    issues: list[tuple[str, str, str]] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".html", ".css", ".js"}:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(ROOT))

        for match in ATTR_RE.finditer(text):
            value = match.group(1)
            for url in URL_RE.findall(value):
                if is_runtime_asset(url, match.group(0).split("=")[0].lower()):
                    issues.append((rel, url, match.group(0)[:40]))

        # CSS url()
        for url in re.findall(r"url\((https?://[^)]+)\)", text):
            if "fonts.gstatic.com" in url or "googleapis" in url:
                issues.append((rel, url, "css url()"))

    if issues:
        print("EXTERNAL RUNTIME DEPENDENCIES:")
        seen = set()
        for rel, url, ctx in issues:
            key = (rel, url)
            if key in seen:
                continue
            seen.add(key)
            print(f"  {rel}")
            print(f"    {url}")
        print(f"\nTOTAL: {len(seen)}")
    else:
        print("EXTERNAL RUNTIME DEPENDENCIES: none")
        print("Site assets are 100% local.")


if __name__ == "__main__":
    main()
