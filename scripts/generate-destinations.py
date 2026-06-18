#!/usr/bin/env python3
"""Generate destination detail pages from data/destinations.json."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "destinations.json"
OUT = ROOT / "destinations"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)


def list_section(title: str, items: list) -> str:
    if not items:
        return ""
    lis = "".join(
        f'              <li><i class="fa-solid fa-check" aria-hidden="true"></i> {x}</li>\n'
        for x in items
    )
    return f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">{title}</h2>
            <ul class="circuit-page__highlights">
{lis}            </ul>
          </div>
"""


def visit_info(d: dict) -> str:
    rows = []
    for label, key in [
        ("Best time to visit", "bestTime"),
        ("Recommended duration", "duration"),
        ("Entry cost", "entryCost"),
    ]:
        val = d.get(key)
        if val:
            rows.append(f"            <p><strong>{label}:</strong> {val}</p>\n")
    return "".join(rows)


def build_page(d: dict) -> str:
    circuit = d.get("circuit", "")
    circuit_slug, back_label = pt.destination_back_link(d)
    if not back_label:
        back_label = circuit
    meta = pt.clean_meta(d.get("meta", ""), circuit)
    paras = "".join(f"            <p>{p}</p>\n" for p in d.get("paragraphs", []))
    info = visit_info(d)
    attractions = list_section("Key Attractions", d.get("keyAttractions", []))
    activities = list_section("Activities", d.get("activities", []))
    hero = pt.img_src(d.get("hero", ""), "../")
    gallery = pt.gallery_html(d.get("gallery", []), d["name"], "../")
    packages = pt.packages_html(d.get("packages", []), "../index.html#bookingForm", "../")
    faqs = pt.faqs_html(d.get("faqs", []))
    tour_count = len(d.get("packages") or d.get("relatedPackages") or [])
    tour_meta = f" · {tour_count} tour{'s' if tour_count != 1 else ''}" if tour_count else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(d['name'] + ' | Safari and Bush Retreats', d.get('card_desc', ''), '../')}
</head>
<body>
{pt.nav_html('../', active='circuits')}

  <main id="main-content">
    <article class="dest-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{d['name']}" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="../circuits/{circuit_slug}" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> {back_label}</a>
          <span class="dest-page__badge">{d.get('badge', 'Explore')}</span>
          <h1 class="dest-page__title">{d['name']}</h1>
          <p class="dest-page__meta">{meta}{tour_meta}</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
{paras}{info}          </div>
{attractions}{activities}{gallery}{packages}{faqs}          <div class="dest-page__cta">
            <p>Ready to explore {d['name']}?</p>
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


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    for d in data["destinations"]:
        (OUT / f"{d['slug']}.html").write_text(build_page(d), encoding="utf-8")
        print(f"Wrote destinations/{d['slug']}.html")
    print(f"Generated {len(data['destinations'])} destination pages.")


if __name__ == "__main__":
    main()
