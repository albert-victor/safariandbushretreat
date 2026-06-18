#!/usr/bin/env python3
"""Regenerate all tourism subpages from JSON data."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = [
    "import-tt-safaris.py",
    "setup-mafia-circuit.py",
    "setup-ocean-islands-circuit.py",
    "expand-tanzania-core.py",
    "clean-destination-cards.py",
    "patch-images-and-destinations.py",
    "match-destination-images.py",
    "link-named-package-destinations.py",
    "fetch-mafia-images.py",
    "build-tourism-data.py",
    "fetch-accommodation-images.py",
    "generate-accommodation-categories.py",
    "generate-accommodations.py",
    "patch-index-accommodations.py",
    "build-search-index.py",
    "build-sitemap.py",
    "build-robots.py",
    "generate-destinations.py",
    "generate-circuits.py",
    "generate-safari-packages.py",
    "generate-all-packages.py",
    "patch-images-and-destinations.py",
    "generate-kenya.py",
    "fetch-uganda-rwanda-images.py",
    "generate-country.py",
    "patch-nav-uganda-rwanda.py",
    "cleanup-orphan-pages.py",
    "patch-index-safaris.py",
    "patch-circuit-nav.py",
    "mirror-external-assets.py",
    "normalize-dashes.py",
    "fix-content-pollution.py",
    "patch-nav-paths.py",
    "patch-gtm.py",
]


def main():
    for name in SCRIPTS:
        path = ROOT / "scripts" / name
        print(f"\n=== {name} ===")
        subprocess.run([sys.executable, str(path)], check=True)
    print("\nAll pages generated.")


if __name__ == "__main__":
    main()
