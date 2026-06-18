#!/usr/bin/env python3
"""Build sitemap.xml for all public HTML pages."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "site-config.json"
OUT = ROOT / "sitemap.xml"

SKIP_DIRS = {"scripts", "data", "vendor", "node_modules", ".git", ".cursor"}
SKIP_FILES = {"404.html"}

PRIORITY = {
    "index.html": 1.0,
    "about.html": 0.8,
    "kenya.html": 0.9,
    "uganda.html": 0.9,
    "rwanda.html": 0.9,
}


def priority_for(path: Path) -> str:
    name = path.name
    if name in PRIORITY:
        return f"{PRIORITY[name]:.1f}"
    parts = path.parts
    if "circuits" in parts and name == "index.html":
        return "0.9"
    if "circuits" in parts:
        return "0.8"
    if name == "index.html" and len(parts) > 1:
        return "0.7"
    if "safaris" in parts:
        return "0.75"
    if any(p in parts for p in ("kenya", "uganda", "rwanda", "destinations")):
        return "0.7"
    if "accommodations" in parts or "categories" in parts:
        return "0.65"
    return "0.6"


def changefreq_for(path: Path) -> str:
    if path.name == "index.html" and path.parent == ROOT:
        return "weekly"
    if path.parent.name in ("kenya", "uganda", "rwanda", "destinations", "safaris"):
        return "monthly"
    return "monthly"


def loc_for(path: Path, base: str) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return base + "/"
    return f"{base}/{rel}"


def main() -> None:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    base = cfg["siteUrl"].rstrip("/")
    today = date.today().isoformat()

    urls: list[tuple[str, str, str]] = []
    for html in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in html.parts):
            continue
        if html.name in SKIP_FILES:
            continue
        urls.append(
            (
                loc_for(html, base),
                changefreq_for(html),
                priority_for(html),
            )
        )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, freq, prio in urls:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{escape(loc)}</loc>",
                f"    <lastmod>{today}</lastmod>",
                f"    <changefreq>{freq}</changefreq>",
                f"    <priority>{prio}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Built sitemap with {len(urls)} URLs -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
