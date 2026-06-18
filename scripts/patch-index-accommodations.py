#!/usr/bin/env python3
"""Restore homepage accommodation category cards from data/accommodations.json."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "accommodations.json"
INDEX = ROOT / "index.html"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)

COUNTRY_ORDER = {"Tanzania": 0, "Kenya": 1, "Uganda": 2, "Rwanda": 3}


def picture_tag(image: str, alt: str) -> str:
    """Use picture element for jpg assets with webp opt variants; plain img for webp."""
    if image.endswith(".webp"):
        src = pt.img_src(image, "")
        return f'<img src="{src}" alt="{alt}" class="accommodation-card__image parallax-img" loading="lazy" width="800" height="600" decoding="async">'
    slug = Path(image).stem.replace(" ", "-").replace("+", "-plus-").lower()
    base = pt.img_src(image, "")
    return (
        f'<picture><source type="image/webp" '
        f'srcset="assets/images/opt/{slug}-480.webp 480w, '
        f'assets/images/opt/{slug}-800.webp 800w, '
        f'assets/images/opt/{slug}-1200.webp 1200w, '
        f'assets/images/opt/{slug}-1920.webp 1920w" '
        f'sizes="(max-width: 767px) 100vw, 50vw">'
        f'<img sizes="(max-width: 767px) 100vw, 50vw" src="{base}" alt="{alt}" '
        f'class="accommodation-card__image parallax-img" loading="lazy" width="800" height="600" decoding="async">'
        f"</picture>"
    )


def category_card(cat: dict, index: int) -> str:
    reverse = " accommodation-card--reverse" if index % 2 == 1 else ""
    img = picture_tag(cat["image"], cat.get("imageAlt", cat["name"]))
    highlights = "".join(
        f"              <li><i class=\"fa-solid fa-check\" aria-hidden=\"true\"></i> {h}</li>\n"
        for h in cat.get("highlights", [])
    )
    highlights_block = ""
    if highlights:
        highlights_block = f"""              <ul class="accommodation-card__highlights">
{highlights}              </ul>
"""
    cta_label = {
        "luxury-lodges": "View Lodges",
        "tented-camps": "View Camps",
        "bush-retreats": "View Retreats",
        "private-villas": "View Villas",
    }.get(cat["slug"], "View More")
    return f"""          <article class="accommodation-card{reverse}">
            <div class="accommodation-card__image-wrap parallax-wrap">
              {img}
              <div class="accommodation-card__overlay"></div>
            </div>
            <div class="accommodation-card__content glass-card">
              <span class="accommodation-card__tag">{cat['tag']}</span>
              <h3 class="accommodation-card__title">{cat['name']}</h3>
              <p class="accommodation-card__desc">{cat['shortDescription']}</p>
{highlights_block}              <a href="accommodations/{cat['slug']}.html" class="btn btn--ghost">{cta_label} <span aria-hidden="true"><i class="fa-solid fa-arrow-right"></i></span></a>
            </div>
          </article>
"""


def featured_card(group: dict, index: int) -> str:
    reverse = " accommodation-card--reverse" if index % 2 == 1 else ""
    hero = pt.img_src(group.get("image", ""), "")
    return f"""          <article class="accommodation-card{reverse}">
            <div class="accommodation-card__image-wrap parallax-wrap">
              <img src="{hero}" alt="{group['name']} safari accommodation" class="accommodation-card__image parallax-img" loading="lazy" width="800" height="600" decoding="async" referrerpolicy="no-referrer">
              <div class="accommodation-card__overlay"></div>
            </div>
            <div class="accommodation-card__content glass-card">
              <span class="accommodation-card__tag">{group.get('tag', group.get('category', 'Safari'))}</span>
              <h3 class="accommodation-card__title">{group['name']}</h3>
              <p class="accommodation-card__desc">{group.get('shortDescription', '')}</p>
              <a href="accommodations/{group['slug']}.html" class="btn btn--ghost">View More <span aria-hidden="true"><i class="fa-solid fa-arrow-right"></i></span></a>
            </div>
          </article>
"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    categories = data["categories"]
    category_cards = "\n".join(category_card(c, i) for i, c in enumerate(categories))

    featured = sorted(
        [g for g in data["groups"] if g.get("featured") and g.get("country") == "Tanzania"],
        key=lambda g: g.get("name", ""),
    )[:4]
    featured_block = ""
    if featured:
        featured_cards = "\n".join(featured_card(g, i) for i, g in enumerate(featured))
        featured_block = f"""
        <header class="section__header section__header--compact">
          <p class="section__eyebrow">Featured Partners</p>
          <h3 class="section__title section__title--sm">Tanzania Safari Lodges</h3>
          <p class="section__subtitle">Trusted accommodation groups across Tanzania's northern, southern and western circuits</p>
        </header>
        <div class="accommodation__grid accommodation__grid--featured">
{featured_cards}
        </div>
"""

    html = INDEX.read_text(encoding="utf-8")
    replacement = (
        f'        <div class="accommodation__grid">\n{category_cards}\n        </div>\n'
        f"{featured_block}"
        f"      </div>\n    </section>\n\n    <!-- Gallery Section -->"
    )
    html = re.sub(
        r'        <div class="accommodation__grid">.*?</div>\s*\n      </div>\s*\n    </section>\s*\n\n    <!-- Gallery Section -->',
        replacement,
        html,
        count=1,
        flags=re.S,
    )
    INDEX.write_text(html, encoding="utf-8")
    print(f"Updated index.html: {len(categories)} category cards + {len(featured)} featured Tanzania groups.")


if __name__ == "__main__":
    main()
