#!/usr/bin/env python3
"""Generate safari package detail pages from data/safari-packages.json."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILES = [
    ROOT / "data" / "safari-packages.json",
    ROOT / "data" / "east-africa-packages.json",
]
OUT = ROOT / "safaris"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)


FOOTER_HIGHLIGHTS = frozenset({
    "Serengeti National Park",
    "Mount Kilimanjaro National Park",
    "Arusha National Park",
    "Lake Manyara National Park",
})


def build_page(p: dict) -> str:
    paras = f"            <p>{p['overview']}</p>\n"
    activities = p.get("activities") or []
    if activities and not FOOTER_HIGHLIGHTS.issubset(set(activities)):
        acts = ", ".join(activities)
        paras += f"            <p><strong>Activities:</strong> {acts}</p>\n"
    destinations = p.get("destinations") or []
    if destinations and not FOOTER_HIGHLIGHTS.issubset(set(destinations)):
        dests = ", ".join(destinations)
        paras += f"            <p><strong>Parks visited:</strong> {dests}</p>\n"

    itinerary = ""
    for step in p.get("itinerary", []):
        itinerary += f"""            <div class="safari-itinerary__day">
              <span class="safari-itinerary__num">Day {step['day']}</span>
              <div>
                <h3 class="safari-itinerary__title">{step['title']}</h3>
                <p class="safari-itinerary__text">{step['summary']}</p>
              </div>
            </div>\n"""

    features = "".join(f"              <li><i class=\"fa-solid fa-check\" aria-hidden=\"true\"></i> {f}</li>\n" for f in p.get("features", []))
    hero = pt.img_src(p.get("hero", ""), "../")
    circuit_slug = pt.CIRCUIT_SLUGS.get(p["circuit"])
    country_pages = {"Kenya": "kenya.html", "Uganda": "uganda.html", "Rwanda": "rwanda.html"}
    if circuit_slug:
        explore_href = f"../circuits/{circuit_slug}.html"
        explore_label = p["circuit"]
    elif p["circuit"] in country_pages:
        explore_href = f"../{country_pages[p['circuit']]}"
        explore_label = f"{p['circuit']} Safaris"
    else:
        explore_href = "../index.html#safaris"
        explore_label = "Safari Packages"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(p['name'] + ' | Safari Packages', p['overview'][:160], '../')}
</head>
<body>
{pt.nav_html('../', active='safaris')}

  <main id="main-content">
    <article class="dest-page safari-package-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{p['name']}" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="../index.html#safaris" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Safari Packages</a>
          <span class="dest-page__badge">{p['circuit']}</span>
          <h1 class="dest-page__title">{p['name']}</h1>
          <p class="dest-page__meta">{p.get('duration', '')} · From {p.get('price', 'Enquire')} / person</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
{paras}          </div>
          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Package Highlights</h2>
            <ul class="circuit-page__highlights">
{features}            </ul>
          </div>
          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Day-by-Day Itinerary</h2>
            <div class="safari-itinerary">
{itinerary}            </div>
          </div>
          <div class="dest-page__cta">
            <p>Ready to book the {p['name']}?</p>
            <a href="../index.html?package={p['slug']}#bookingForm" class="btn btn--primary btn--lg">Request This Package</a>
            <a href="{explore_href}" class="btn btn--outline btn--lg" style="margin-left:0.75rem">Explore {explore_label}</a>
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


def main():
    packages: list[dict] = []
    for path in DATA_FILES:
        if path.exists():
            packages.extend(json.loads(path.read_text(encoding="utf-8"))["packages"])
    OUT.mkdir(exist_ok=True)
    for p in packages:
        (OUT / f"{p['slug']}.html").write_text(build_page(p), encoding="utf-8")
        print(f"Wrote safaris/{p['slug']}.html")
    print(f"Generated {len(packages)} safari package pages.")


if __name__ == "__main__":
    main()
