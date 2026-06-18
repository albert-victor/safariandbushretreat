#!/usr/bin/env python3
"""Generate country overview and destination pages (Uganda, Rwanda, Kenya-style)."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)


def activities_html(activities: list) -> str:
    if not activities:
        return ""
    items = "".join(
        f'              <li><i class="fa-solid fa-check" aria-hidden="true"></i> {a}</li>\n'
        for a in activities
    )
    return f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Activities</h2>
            <ul class="circuit-page__highlights">
{items}            </ul>
          </div>\n"""


def section_grids(destinations: list, country: str, categories: dict[str, str]) -> str:
    grids = ""
    by_cat: dict[str, list] = {}
    for d in destinations:
        cat = d.get("category", "Destination")
        by_cat.setdefault(cat, []).append(d)
    order = ["National Park", "City", "Town", "Destination"]
    for cat in order:
        items = by_cat.get(cat)
        if not items:
            continue
        heading = categories.get(cat, f"{cat}s in {country.title()}")
        grids += pt.dest_card_grid(items, f"{country}/", img_prefix="", heading=heading)
    return grids


def build_overview(country: dict, destinations: list, country_slug: str, active: str) -> str:
    paras = "".join(f"            <p>{p}</p>\n" for p in country.get("paragraphs", []))
    highlights = "".join(
        f'              <li><i class="fa-solid fa-check" aria-hidden="true"></i> {h}</li>\n'
        for h in country.get("highlights", [])
    )
    packages = pt.packages_html(country.get("packages", []), "index.html#bookingForm", "")
    grids = section_grids(
        destinations,
        country_slug,
        {
            "National Park": "National Parks",
            "City": "Cities",
            "Town": "Towns & Cities",
            "Destination": "Highlights",
        },
    )
    hero = pt.img_src(country.get("hero", ""), "")
    cta_label = f"Plan Your {country['name']}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(country['name'] + ' | Safari and Bush Retreats', country.get('card_desc', ''), '')}
</head>
<body>
{pt.nav_html('', active=active)}

  <main id="main-content">
    <article class="dest-page circuit-page {country_slug}-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{country['name']} landscape" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="index.html#home" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Home</a>
          <span class="dest-page__badge">{country.get('badge', country_slug.title())}</span>
          <h1 class="dest-page__title">{country['name']}</h1>
          <p class="dest-page__meta">{country.get('meta', '')}</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
{paras}          </div>
          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Safari Highlights</h2>
            <ul class="circuit-page__highlights">
{highlights}            </ul>
          </div>
{grids}{packages}          <div class="dest-page__cta">
            <p>Combine {country_slug.title()} with your Tanzania safari for the ultimate East Africa journey.</p>
            <a href="index.html#bookingForm" class="btn btn--primary btn--lg">{cta_label}</a>
          </div>
        </div>
      </section>
    </article>
  </main>

  <footer class="footer" role="contentinfo">
    <div class="container">
      <p class="footer__bottom">&copy; 2026 Safari and Bush Retreats · <a href="index.html#home">Home</a></p>
    </div>
  </footer>

  <script src="js/main.js" defer></script>
</body>
</html>
"""


def build_dest(d: dict, country: dict, country_slug: str, active: str) -> str:
    paras = "".join(f"            <p>{p}</p>\n" for p in d.get("paragraphs", []))
    hero = pt.img_src(d.get("hero", ""), "../")
    gallery = pt.gallery_html(d.get("gallery", []), d["name"], "../")
    packages = pt.packages_html(d.get("packages", []), "../index.html#bookingForm", "../")
    activities = activities_html(d.get("activities", []))
    cta_label = f"Plan Your {country['name']}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(d['name'] + ' | ' + country['name'], d.get('card_desc', ''), '../')}
</head>
<body>
{pt.nav_html('../', active=active)}

  <main id="main-content">
    <article class="dest-page {country_slug}-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{d['name']}" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="../{country_slug}.html" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> {country['name']}</a>
          <span class="dest-page__badge">{d.get('badge', country_slug.title())}</span>
          <h1 class="dest-page__title">{d['name']}</h1>
          <p class="dest-page__meta">{d.get('meta', '')}</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
{paras}          </div>
{activities}{gallery}{packages}          <div class="dest-page__cta">
            <p>Ready to explore {d['name']}?</p>
            <a href="../index.html#bookingForm" class="btn btn--primary btn--lg">{cta_label}</a>
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


def generate(country_slug: str) -> None:
    data_path = ROOT / "data" / f"{country_slug}-data.json"
    if not data_path.exists():
        print(f"Missing {data_path}")
        sys.exit(1)
    data = json.loads(data_path.read_text(encoding="utf-8"))
    country = data[country_slug]
    dests = data.get("destinations", [])
    out_dir = ROOT / country_slug
    out_dir.mkdir(exist_ok=True)
    active = country_slug

    (ROOT / f"{country_slug}.html").write_text(
        build_overview(country, dests, country_slug, active), encoding="utf-8"
    )
    print(f"Wrote {country_slug}.html")
    for d in dests:
        (out_dir / f"{d['slug']}.html").write_text(
            build_dest(d, country, country_slug, active), encoding="utf-8"
        )
        print(f"Wrote {country_slug}/{d['slug']}.html")
    print(f"Generated {country_slug} overview + {len(dests)} destination pages.")


def main():
    targets = sys.argv[1:] or ["uganda", "rwanda"]
    for slug in targets:
        generate(slug)


if __name__ == "__main__":
    main()
