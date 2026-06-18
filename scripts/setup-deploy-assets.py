#!/usr/bin/env python3
"""Copy branded assets to web paths and generate favicon files."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
IMAGES = ROOT / "assets" / "images"
ABOUT = IMAGES / "about"

COPIES = {
    "about14.jpg": ABOUT / "about14.jpg",
    "about15.jpg": ABOUT / "about15.jpg",
    "about16.jpg": ABOUT / "about16.jpg",
    "about17.jpg": ABOUT / "about17.jpg",
    "about18.jpg": ABOUT / "about18.jpg",
    "about20 main.jpg": ABOUT / "about20-main.jpg",
    "about21 main.jpg": ABOUT / "about21-main.jpg",
    "about22.jpg": ABOUT / "about22.jpg",
    "about23.jpg": ABOUT / "about23.jpg",
    "about24 main.jpg": ABOUT / "about24-main.jpg",
    "about25.jpg": ABOUT / "about25.jpg",
    "about main image.jpg": IMAGES / "about-main-image.jpg",
    "about main pic.jpg": IMAGES / "about-main-pic.jpg",
    "about main pictures.jpg": IMAGES / "about-main-pictures.jpg",
    "about picture.jpg": IMAGES / "about-picture.jpg",
    "about picture1.jpg": IMAGES / "about-picture1.jpg",
    "about.jpg": IMAGES / "about.jpg",
    "singita main.jpg": IMAGES / "singita-main.jpg",
    "singita1.jpg": IMAGES / "singita1.jpg",
    "singita2.jpeg": IMAGES / "singita2.jpg",
    "singita3.jpg": IMAGES / "singita3.jpg",
}


def make_favicon() -> None:
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed - skip favicon generation")
        return
    src = IMAGES / "logo-nav.png"
    if not src.exists():
        src = IMAGES / "favicon.svg"
    if not src.exists():
        print("No logo source for favicon")
        return
    img = Image.open(src).convert("RGBA")
    for size, name in ((32, "favicon.png"), (180, "apple-touch-icon.png")):
        out = IMAGES / name
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(out, "PNG")
        print(f"Wrote {out.relative_to(ROOT)}")


def main() -> None:
    ABOUT.mkdir(parents=True, exist_ok=True)
    for src_name, dest in COPIES.items():
        src = ASSETS / src_name
        if not src.exists():
            src = IMAGES / src_name
        if src.exists() and src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
            print(f"Copied {src_name} -> {dest.relative_to(ROOT)}")
    make_favicon()


if __name__ == "__main__":
    main()
