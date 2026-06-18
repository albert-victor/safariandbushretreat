#!/usr/bin/env python3
"""Generate robots.txt with sitemap reference."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "site-config.json"
OUT = ROOT / "robots.txt"


def main() -> None:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    base = cfg["siteUrl"].rstrip("/")
    content = f"""# Safari and Bush Retreats - crawler rules
User-agent: *
Allow: /

# Build tooling & data (not public pages)
Disallow: /scripts/
Disallow: /data/

# Utility page
Disallow: /404.html

# Sitemap
Sitemap: {base}/sitemap.xml
"""
    OUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
