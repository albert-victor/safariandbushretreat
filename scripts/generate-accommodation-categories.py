#!/usr/bin/env python3
"""Generate accommodation category listing pages from data/accommodations.json."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "accommodations.json"
OUT = ROOT / "accommodations"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)

COUNTRY_ORDER = {"Tanzania": 0, "Kenya": 1, "Uganda": 2, "Rwanda": 3}


def groups_for_category(groups: list, category_slug: str) -> list:
    matched = [g for g in groups if g.get("categorySlug") == category_slug]
    return sorted(
        matched,
        key=lambda g: (COUNTRY_ORDER.get(g.get("country", ""), 9), not g.get("featured", False), g["name"]),
    )


def country_section(country: str, items: list) -> str:
    cards = ""
    for g in items:
        hero = pt.img_src(g.get("image", ""), "../")
        meta = f"{g.get('country', '')} · {g.get('category', '')}"
        cards += f"""            <article class="circuit-dest-card">
              <a href="{g['slug']}.html" class="circuit-dest-card__link">
                <div class="circuit-dest-card__img-wrap">
                  <img src="{hero}" alt="{g['name']}" loading="lazy" decoding="async" width="400" height="260" referrerpolicy="no-referrer">
                </div>
                <div class="circuit-dest-card__body">
                  <span class="circuit-dest-card__meta">{meta}</span>
                  <h3 class="circuit-dest-card__title">{g['name']}</h3>
                  <p class="circuit-dest-card__desc">{g.get('shortDescription', '')[:120]}</p>
                </div>
              </a>
            </article>
"""
    return f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">{country}</h2>
            <div class="circuit-dest-grid">
{cards}            </div>
          </div>
"""


def build_page(cat: dict, groups: list) -> str:
    hero = pt.img_src(cat.get("image", ""), "../")
    by_country: dict[str, list] = {}
    for g in groups:
        by_country.setdefault(g.get("country", "Other"), []).append(g)

    sections = ""
    for country in ("Tanzania", "Kenya", "Uganda", "Rwanda"):
        if country in by_country:
            sections += country_section(country, by_country[country])

    highlights = "".join(
        f'              <li><i class="fa-solid fa-check" aria-hidden="true"></i> {h}</li>\n'
        for h in cat.get("highlights", [])
    )
    highlights_html = ""
    if highlights:
        highlights_html = f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Highlights</h2>
            <ul class="circuit-page__highlights">
{highlights}            </ul>
          </div>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(cat['name'] + ' | Safari and Bush Retreats', cat.get('shortDescription', ''), '../')}
</head>
<body>
{pt.nav_html('../', active='accommodation')}

  <main id="main-content">
    <article class="dest-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{cat['name']}" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="../index.html#accommodation" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Accommodation</a>
          <span class="dest-page__badge">{cat.get('tag', 'Safari')}</span>
          <h1 class="dest-page__title">{cat['name']}</h1>
          <p class="dest-page__meta">East Africa Safari Lodges · {len(groups)} partner groups</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
            <p>{cat['shortDescription']}</p>
          </div>
{highlights_html}{sections}          <div class="dest-page__cta">
            <p>Need help choosing the right {cat['name'].lower()} for your safari?</p>
            <a href="../index.html#bookingForm" class="btn btn--primary btn--lg">Request a Quote</a>
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
    for cat in data["categories"]:
        groups = groups_for_category(data["groups"], cat["slug"])
        (OUT / f"{cat['slug']}.html").write_text(build_page(cat, groups), encoding="utf-8")
        print(f"Wrote accommodations/{cat['slug']}.html ({len(groups)} groups)")
    print(f"Generated {len(data['categories'])} accommodation category pages.")


if __name__ == "__main__":
    main()
