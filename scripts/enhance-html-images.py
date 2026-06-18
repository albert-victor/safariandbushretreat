#!/usr/bin/env python3
"""Add responsive WebP picture/srcset markup to local images in HTML files."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "assets" / "image-manifest.json"

SIZE_RULES = (
    (r'class="[^"]*hero-slide__img', '100vw'),
    (r'class="[^"]*dest-page__hero-img', '100vw'),
    (r'class="[^"]*destination-card__image', '(max-width: 767px) 100vw, 50vw'),
    (r'class="[^"]*experience-card__image', '(max-width: 767px) 92vw, 28vw'),
    (r'class="[^"]*package-card__img', '(max-width: 767px) 100vw, 50vw'),
    (r'class="[^"]*circuit-page__package-img', '(max-width: 767px) 100vw, 50vw'),
    (r'class="[^"]*accommodation-card__image', '(max-width: 767px) 100vw, 50vw'),
    (r'class="[^"]*dest-page__figure[^"]*"[\s\S]*?<img', '(max-width: 767px) 100vw, 45vw'),
    (r'class="[^"]*gallery__item', '(max-width: 767px) 100vw, 33vw'),
)
DEFAULT_SIZES = '(max-width: 767px) 100vw, 800px'

IMG_TAG_RE = re.compile(r'<img\b([^>]*?)>', re.IGNORECASE | re.DOTALL)
SRC_RE = re.compile(r'\bsrc="([^"]+)"', re.IGNORECASE)
CLASS_RE = re.compile(r'\bclass="([^"]+)"', re.IGNORECASE)


def normalize_local_src(src: str) -> str | None:
    if src.startswith("http://") or src.startswith("https://") or src.startswith("data:"):
        return None
    clean = unquote(src).lstrip("./")
    clean = clean.removeprefix("../")
    if clean.startswith("assets/images/"):
        return clean
    return None


def unsplash_srcset(src: str) -> str | None:
    if "images.unsplash.com" not in src:
        return None
    base = src.split("?")[0]
    params = ""
    if "?" in src:
        params = "&" + src.split("?", 1)[1]
    params = params.replace("&amp;", "&")
    if "auto=format" not in params:
        params += "&auto=format"
    widths = (480, 800, 1200, 1920)
    parts = []
    for w in widths:
        query = f"fit=crop&w={w}&q=82"
        if "fit=crop" in params:
            query = re.sub(r'w=\d+', f'w={w}', params.lstrip("&"))
        else:
            query = params.lstrip("&") + f"&{query}" if params else query
        parts.append(f"{base}?{query} {w}w")
    return ", ".join(parts)


def pick_sizes(tag: str, context: str) -> str:
    blob = context + tag
    for pattern, sizes in SIZE_RULES:
        if re.search(pattern, blob, re.IGNORECASE):
            return sizes
    return DEFAULT_SIZES


def upsert_attr(attrs: str, name: str, value: str) -> str:
    pattern = re.compile(rf'\b{name}="[^"]*"', re.IGNORECASE)
    if pattern.search(attrs):
        return pattern.sub(f'{name}="{value}"', attrs, count=1)
    return f'{name}="{value}" ' + attrs


def ensure_async(attrs: str) -> str:
    if re.search(r'\bdecoding=', attrs, re.IGNORECASE):
        return attrs
    return f'{attrs.strip()} decoding="async"'


def build_img_tag(attrs: str) -> str:
    cleaned = re.sub(r'\s+', ' ', attrs.strip())
    return f"<img {cleaned}>" if cleaned else "<img>"


def wrap_picture(img_tag: str, webp_srcset: str, sizes: str, fallback_srcset: str | None = None) -> str:
    attrs = IMG_TAG_RE.match(img_tag).group(1)
    attrs = upsert_attr(attrs, "sizes", sizes)
    if fallback_srcset:
        attrs = upsert_attr(attrs, "srcset", fallback_srcset)
    attrs = ensure_async(attrs)
    img = build_img_tag(attrs)
    return (
        "<picture>"
        f'<source type="image/webp" srcset="{webp_srcset}" sizes="{sizes}">'
        f"{img}"
        "</picture>"
    )


def asset_prefix(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth if depth else ""


def manifest_srcset(entry: dict, prefix: str) -> str:
    return ", ".join(
        f"{prefix}{v['url']} {v['width']}w" for v in entry["variants"]
    )


def enhance_file(path: Path, manifest: dict) -> bool:
    html = path.read_text(encoding="utf-8")
    prefix = asset_prefix(path)

    def replacer(match: re.Match[str]) -> str:
        tag = match.group(0)
        before = html[max(0, match.start() - 4000):match.start()]
        if re.search(r"<picture>\s*(?:<source[^>]*>\s*)*$", before, re.IGNORECASE | re.DOTALL):
            return tag
        if "</picture>" in html[match.end():match.end() + 40]:
            return tag
        src_match = SRC_RE.search(tag)
        if not src_match:
            return tag
        src = src_match.group(1).replace("&amp;", "&")
        context = html[max(0, match.start() - 220):match.start()]
        sizes = pick_sizes(tag, context)

        local = normalize_local_src(src)
        if local and local in manifest:
            entry = manifest[local]
            return wrap_picture(tag, manifest_srcset(entry, prefix), sizes)

        remote_set = unsplash_srcset(src)
        if remote_set:
            attrs = IMG_TAG_RE.match(tag).group(1)
            attrs = upsert_attr(attrs, "srcset", remote_set)
            attrs = upsert_attr(attrs, "sizes", sizes)
            attrs = ensure_async(attrs)
            return build_img_tag(attrs)

        return tag

    updated = IMG_TAG_RE.sub(replacer, html)
    if updated != html:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    if not MANIFEST_PATH.exists():
        raise SystemExit("Run optimize-images.py first.")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    targets = [ROOT / "index.html", ROOT / "404.html", ROOT / "kenya.html"]
    targets.extend((ROOT / "destinations").glob("*.html"))
    targets.extend((ROOT / "kenya").glob("*.html"))
    targets.extend((ROOT / "circuits").glob("*.html"))
    targets.extend((ROOT / "safaris").glob("*.html"))

    changed = 0
    for path in targets:
        if path.exists() and enhance_file(path, manifest):
            print(f"Updated {path.relative_to(ROOT)}")
            changed += 1
    print(f"Enhanced {changed} HTML files.")


if __name__ == "__main__":
    main()
