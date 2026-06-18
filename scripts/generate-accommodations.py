#!/usr/bin/env python3
"""Generate accommodation group detail pages from data/accommodations.json."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "accommodations.json"
OUT = ROOT / "accommodations"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)


def amenities_section(amenities: list) -> str:
    if not amenities:
        return ""
    items = "".join(
        f'              <li><i class="fa-solid fa-check" aria-hidden="true"></i> {a}</li>\n'
        for a in amenities
    )
    return f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Amenities &amp; Highlights</h2>
            <ul class="circuit-page__highlights">
{items}            </ul>
          </div>
"""


KENYA_DEST_SLUGS = frozenset({
    "masai-mara", "amboseli", "diani-beach", "lake-naivasha", "lake-nakuru", "samburu",
})


def destination_link(group: dict, prefix: str) -> str:
    slug = group.get("destinationSlug")
    name = group.get("destination", "")
    if not slug or not name:
        return ""
    if slug in KENYA_DEST_SLUGS:
        href = f"{prefix}kenya/{slug}.html"
    else:
        href = f"{prefix}destinations/{slug}.html"
    return f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Related Destination</h2>
            <p>Explore the wilderness surrounding this property.</p>
            <a href="{href}" class="btn btn--outline btn--sm">
              <i class="fa-solid fa-location-dot" aria-hidden="true"></i> {name}
            </a>
          </div>
"""


def gallery_section(images: list[str], prefix: str, name: str) -> str:
    if not images:
        return ""
    figures = ""
    for img in images:
        src = pt.img_src(img, prefix)
        figures += f"""          <figure class="dest-page__figure">
            <img src="{src}" alt="{name}" loading="lazy" decoding="async" width="600" height="400" referrerpolicy="no-referrer">
          </figure>
"""
    return f"""          <div class="dest-page__gallery">
{figures}          </div>
"""


def build_page(group: dict) -> str:
    hero = pt.img_src(group.get("image", ""), "../")
    desc = group.get("description", group.get("shortDescription", ""))
    meta = f'{group.get("location", "")} · {group.get("country", "")} · {group.get("category", "")}'
    amenities = amenities_section(group.get("amenities", []))
    gallery = gallery_section(group.get("gallery", []), "../", group["name"])
    destination = destination_link(group, "../")
    website = group.get("officialWebsite", "#")
    category_slug = group.get("categorySlug", "")
    back_href = f"../accommodations/{category_slug}.html" if category_slug else "../index.html#accommodation"
    back_label = group.get("categorySlug", "Accommodation").replace("-", " ").title()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(group['name'] + ' | Safari and Bush Retreats', group.get('shortDescription', ''), '../')}
</head>
<body>
{pt.nav_html('../', active='accommodation')}

  <main id="main-content">
    <article class="dest-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{group['name']}" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="{back_href}" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> {back_label}</a>
          <span class="dest-page__badge">{group.get('category', 'Safari Lodge')}</span>
          <h1 class="dest-page__title">{group['name']}</h1>
          <p class="dest-page__meta">{meta}</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
            <p>{desc}</p>
          </div>
{amenities}{gallery}{destination}          <div class="dest-page__cta">
            <p>Plan your stay with {group['name']} through Safari &amp; Bush Retreats.</p>
            <a href="{website}" class="btn btn--primary btn--lg" target="_blank" rel="noopener noreferrer">
              Visit Official Website <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i>
            </a>
            <a href="../index.html#bookingForm" class="btn btn--outline btn--lg" style="margin-left:0.75rem">Request a Quote</a>
          </div>
        </div>
      </section>
    </article>
  </main>

  <footer class="footer" role="contentinfo">
    <div class="container">
      <p class="footer__bottom">&copy; 2026 Safari and Bush Retreats · <a href="../index.html#home">Home</a></p>
    </div>
  </footer>

  <script src="../js/main.js" defer></script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    for group in data["groups"]:
        (OUT / f"{group['slug']}.html").write_text(build_page(group), encoding="utf-8")
        print(f"Wrote accommodations/{group['slug']}.html")
    print(f"Generated {len(data['groups'])} accommodation group pages.")


if __name__ == "__main__":
    main()
