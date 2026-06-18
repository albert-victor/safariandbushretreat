#!/usr/bin/env python3
"""Generate responsive WebP variants for local raster images."""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "assets" / "images"
OUT_DIR = SRC_DIR / "opt"
MANIFEST = ROOT / "assets" / "image-manifest.json"

WIDTHS = (480, 800, 1200, 1920)
WEBP_QUALITY = 82
RASTER_EXT = {".jpg", ".jpeg", ".png"}


def slugify(name: str) -> str:
    base = Path(name).stem
    base = base.replace("+", "-plus-")
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", base).strip("-").lower() or "image"


def resize_and_save(src: Image.Image, width: int, out_path: Path) -> int:
    img = src.copy()
    if img.width > width:
        ratio = width / img.width
        height = max(1, round(img.height * ratio))
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    elif img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    img.save(out_path, "WEBP", quality=WEBP_QUALITY, method=6)
    return img.width


def process_image(path: Path) -> dict | None:
    rel = path.relative_to(SRC_DIR).as_posix()
    slug = slugify(path.name)
    variants: list[dict] = []

    try:
        with Image.open(path) as src:
            src.load()
            original_w = src.width
            for width in WIDTHS:
                if width > original_w and width != WIDTHS[-1]:
                    continue
                target_w = min(width, original_w)
                out_name = f"{slug}-{target_w}.webp"
                out_path = OUT_DIR / out_name
                actual_w = resize_and_save(src, target_w, out_path)
                variants.append(
                    {
                        "url": f"assets/images/opt/{out_name}",
                        "width": actual_w,
                        "bytes": out_path.stat().st_size,
                    }
                )
    except OSError as exc:
        print(f"SKIP {rel}: {exc}")
        return None

    if not variants:
        return None

    variants.sort(key=lambda item: item["width"])
    return {
        "source": f"assets/images/{rel}",
        "slug": slug,
        "variants": variants,
        "srcset": ", ".join(f"{v['url']} {v['width']}w" for v in variants),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {}
    total_before = 0
    total_after = 0
    count = 0

    for path in sorted(SRC_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in RASTER_EXT:
            continue
        rel = path.relative_to(SRC_DIR)
        if rel.parts[0] == "opt":
            continue
        if len(rel.parts) > 1 and rel.parts[0] != "external":
            continue
        total_before += path.stat().st_size
        entry = process_image(path)
        if not entry:
            continue
        manifest[entry["source"]] = entry
        total_after += sum(v["bytes"] for v in entry["variants"])
        count += 1
        print(f"OK {path.name}")

    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nProcessed {count} images")
    print(f"Source total: {total_before / 1024 / 1024:.2f} MB")
    print(f"WebP variants total: {total_after / 1024 / 1024:.2f} MB")
    print(f"Manifest: {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
