#!/usr/bin/env python3
"""
Pre-deploy pipeline: regenerate pages, optimize images, SEO files.
Run from project root: python scripts/prepare-deploy.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ("Setup deploy assets (favicon, branded images)", "setup-deploy-assets.py"),
    ("Regenerate all tourism pages", "generate-all.py"),
    ("Optimize images (WebP)", "optimize-images.py"),
    ("Enhance HTML with responsive images", "enhance-html-images.py"),
    ("Inject Google Tag Manager", "patch-gtm.py"),
    ("Build search index", "build-search-index.py"),
    ("Build sitemap.xml", "build-sitemap.py"),
    ("Build robots.txt", "build-robots.py"),
]


def run(script: str) -> None:
    path = ROOT / "scripts" / script
    print(f"\n=== {script} ===")
    subprocess.run([sys.executable, str(path)], check=True, cwd=str(ROOT))


def main() -> None:
    print("Safari and Bush Retreats - prepare deploy")
    for label, script in STEPS:
        print(f"\n>> {label}")
        run(script)
    print("\nDeploy prep complete.")
    print("Next: git add -A && git commit && git push origin main")


if __name__ == "__main__":
    main()
