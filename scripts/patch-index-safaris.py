#!/usr/bin/env python3
"""Inject circuit-grouped safari packages into index.html from safari-packages.json."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "safari-packages.json"
INDEX = ROOT / "index.html"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)

CIRCUIT_ORDER = [
    ("Northern Circuit", "safaris-northern", "northern-circuit"),
    ("Southern Circuit", "safaris-southern", "southern-circuit"),
    ("Eastern Circuit", "safaris-eastern", "eastern-circuit"),
    ("Western Circuit", "safaris-western", "western-circuit"),
    ("Oceanic Islands", "safaris-ocean", "tanzania-oceanic-islands"),
    ("Mafia Island", "safaris-mafia", "mafia-island"),
]

NAV_SAFARIS = """          <li class="navbar__item navbar__item--has-dropdown">
            <a href="#safaris" class="navbar__link" data-nav="safaris">Safaris <i class="fa-solid fa-chevron-down navbar__dropdown-icon" aria-hidden="true"></i></a>
            <ul class="navbar__dropdown" role="menu">
              <li><a href="#safaris-northern" role="menuitem">Northern Circuit</a></li>
              <li><a href="#safaris-southern" role="menuitem">Southern Circuit</a></li>
              <li><a href="#safaris-eastern" role="menuitem">Eastern Circuit</a></li>
              <li><a href="#safaris-western" role="menuitem">Western Circuit</a></li>
              <li><a href="#safaris-ocean" role="menuitem">Oceanic Islands</a></li>
              <li><a href="#safaris-mafia" role="menuitem">Mafia Island</a></li>
              <li><a href="safaris/5-days-northern-classic.html" role="menuitem">5-Day Northern Classic</a></li>
            </ul>
          </li>"""

MOBILE_SAFARIS = """          <li class="mobile-menu__item mobile-menu__item--dest">
            <button type="button" class="mobile-menu__link mobile-menu__dest-trigger" aria-expanded="false" aria-controls="mobileSafariPanel">
              <span>Safaris</span>
              <i class="fa-solid fa-chevron-down mobile-menu__dest-chevron" aria-hidden="true"></i>
            </button>
            <div class="mobile-menu__dest-panel" id="mobileSafariPanel">
              <a href="#safaris" class="mobile-menu__dest-overview">All safari packages</a>
              <ul class="mobile-menu__dest-grid">
                <li><a href="#safaris-northern">Northern Circuit</a></li>
                <li><a href="#safaris-southern">Southern Circuit</a></li>
                <li><a href="#safaris-eastern">Eastern Circuit</a></li>
                <li><a href="#safaris-western">Western Circuit</a></li>
                <li><a href="#safaris-ocean">Oceanic Islands</a></li>
                <li><a href="#safaris-mafia">Mafia Island</a></li>
                <li><a href="safaris/5-days-northern-classic.html">5-Day Northern Classic</a></li>
              </ul>
            </div>
          </li>"""


def card(p: dict) -> str:
    featured = ' package-card--featured' if p.get("featured") else ""
    badge = '\n              <div class="package-card__badge">Most Popular</div>' if p.get("featured") else ""
    btn_class = "btn--outline"
    book_btn_class = "btn--primary"
    features = "".join(f"              <li>{f}</li>\n" for f in p.get("features", [])[:5])
    hero = pt.img_src(p.get("hero", ""), "")
    return f"""          <article class="package-card{featured}">
            <div class="package-card__visual">
              <img src="{hero}" alt="{p['name']}" class="package-card__img" loading="lazy" decoding="async" width="600" height="340" referrerpolicy="no-referrer">
              <div class="package-card__visual-overlay"></div>{badge}
            </div>
            <div class="package-card__body">
            <div class="package-card__header">
              <span class="package-card__duration">{p.get('duration', p.get('days', ''))}</span>
              <h3 class="package-card__title">{p['name']}</h3>
              <p class="package-card__price">From <span>{p['price']}</span> / person</p>
            </div>
            <ul class="package-card__features">
{features}            </ul>
            <div class="package-card__actions">
              <a href="safaris/{p['slug']}.html" class="btn {btn_class} package-card__btn">View Itinerary</a>
              <a href="?package={p['slug']}#bookingForm" class="btn {book_btn_class} package-card__btn">Request Package</a>
            </div>
            </div>
          </article>
"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    by_circuit: dict[str, list] = {}
    for p in data["packages"]:
        circuit = p["circuit"]
        if circuit in ("Coastal & Islands", "Zanzibar & Islands"):
            circuit = "Oceanic Islands"
        by_circuit.setdefault(circuit, []).append(p)

    blocks = ""
    for circuit, anchor, circuit_slug in CIRCUIT_ORDER:
        pkgs = by_circuit.get(circuit, [])
        if not pkgs:
            continue
        cards = "".join(card(p) for p in pkgs)
        blocks += f"""        <div class="safaris-circuit-block" id="{anchor}">
          <h3 class="safaris-circuit-block__title"><span>{circuit}</span><a href="circuits/{circuit_slug}.html">{len(pkgs)} curated packages</a></h3>
          <div class="packages__grid">
{cards}          </div>
        </div>

"""

    html = INDEX.read_text(encoding="utf-8")
    html = re.sub(
        r'          <li><a href="#safaris" class="navbar__link" data-nav="safaris">Safaris</a></li>',
        NAV_SAFARIS,
        html,
        count=1,
    )
    html = re.sub(
        r'          <li><a href="#safaris" class="mobile-menu__link">Safaris</a></li>',
        MOBILE_SAFARIS,
        html,
        count=1,
    )
    html = re.sub(
        r'          <p class="section__subtitle">Handcrafted itineraries designed for the discerning traveler</p>',
        '          <p class="section__subtitle">Curated multi-day itineraries across Tanzania\'s safari circuits - parks, lodges and bush camps for every style of traveller</p>',
        html,
        count=1,
    )
    html = re.sub(
        r'        <div class="safaris-circuit-block".*?</div>\s*\n        <div class="packages__cta">',
        blocks + '        <div class="packages__cta">',
        html,
        count=1,
        flags=re.S,
    )
    INDEX.write_text(html, encoding="utf-8")
    print("Updated index.html safari packages and nav.")


if __name__ == "__main__":
    main()
