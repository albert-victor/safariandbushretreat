#!/usr/bin/env python3
"""Generate safaris/index.html - all Tanzania safari packages grouped by circuit."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKG_DATA = ROOT / "data" / "safari-packages.json"
EAST_DATA = ROOT / "data" / "east-africa-packages.json"
OUT = ROOT / "safaris" / "index.html"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)

CIRCUIT_ORDER = [
    "Northern Circuit",
    "Southern Circuit",
    "Eastern Circuit",
    "Western Circuit",
    "Oceanic Islands",
    "Mafia Island",
    "Southern Highlands & Culture",
    "Kenya",
    "Uganda",
    "Rwanda",
]


def package_cards(packages: list, prefix: str = "../") -> str:
    items = ""
    for p in packages:
        days = p.get("days")
        days_label = f"{days} Days" if days else "Safari"
        price = p.get("price") or "Enquire"
        price_html = f'From <span>{price}</span> / person' if price != "Enquire" else "Price on request"
        slug = p.get("slug")
        href = f"{prefix}safaris/{slug}.html"
        hero = p.get("hero", "")
        img_block = ""
        if hero:
            src = pt.img_src(hero, prefix)
            img_block = f"""              <a href="{href}" class="circuit-page__package-img-link">
                <img src="{src}" alt="{p['name']}" class="circuit-page__package-img" loading="lazy" decoding="async" width="480" height="280" referrerpolicy="no-referrer">
              </a>\n"""
        items += f"""            <article class="circuit-page__package">
{img_block}              <div class="circuit-page__package-body">
                <div class="circuit-page__package-head">
                  <span class="circuit-page__package-days">{days_label}</span>
                  <h3 class="circuit-page__package-name">{p["name"]}</h3>
                  <p class="circuit-page__package-price">{price_html}</p>
                </div>
                <p class="circuit-page__package-desc">{p.get("overview", "")[:160]}…</p>
                <a href="{href}" class="btn btn--outline btn--sm">View Itinerary</a>
              </div>
            </article>\n"""
    return items


def main():
    packages: list[dict] = []
    for path in (PKG_DATA, EAST_DATA):
        if path.exists():
            packages.extend(json.loads(path.read_text(encoding="utf-8"))["packages"])

    by_circuit: dict[str, list] = {c: [] for c in CIRCUIT_ORDER}
    for p in packages:
        circuit = p.get("circuit", "Northern Circuit")
        if circuit not in by_circuit:
            by_circuit[circuit] = []
        by_circuit[circuit].append(p)

    sections = ""
    for circuit in CIRCUIT_ORDER:
        pkgs = by_circuit.get(circuit, [])
        if not pkgs:
            continue
        pkgs.sort(key=lambda x: (x.get("days") or 99, x.get("name", "")))
        circuit_slug = pt.CIRCUIT_SLUGS.get(circuit, "")
        circuit_link = (
            f' <a href="../circuits/{circuit_slug}.html" class="circuit-page__circuit-link">View circuit</a>'
            if circuit_slug else ""
        )
        sections += f"""          <div class="circuit-page__section" id="{circuit_slug or circuit.lower().replace(' ', '-')}">
            <h2 class="circuit-page__heading">{circuit} <span class="circuit-page__count">({len(pkgs)} packages)</span>{circuit_link}</h2>
            <div class="circuit-page__packages">
{package_cards(pkgs)}            </div>
          </div>\n"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block('All Safari Packages | Safari and Bush Retreats', f'Browse {len(packages)} safari packages across Tanzania and East Africa - wildlife, mountains, beaches and cultural tours.', '../')}
</head>
<body>
{pt.nav_html('../', active='safaris')}

  <main id="main-content">
    <article class="dest-page circuit-page">
      <header class="dest-page__hero">
        <img src="{pt.img_src('serengeti3.jpg', '../')}" alt="All Safari Packages" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="../index.html#safaris" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Home</a>
          <span class="dest-page__badge">Safari Packages</span>
          <h1 class="dest-page__title">All Tours &amp; Safaris</h1>
          <p class="dest-page__meta">{len(packages)} packages · Tanzania &amp; East Africa</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
            <p>Every safari package we offer - from day trips and Kilimanjaro treks to multi-park wildlife circuits and Zanzibar beach holidays. Each links to a full day-by-day itinerary.</p>
          </div>
{sections}          <div class="dest-page__cta">
            <p>Need help choosing the right package?</p>
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
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote safaris/index.html ({len(packages)} packages)")


if __name__ == "__main__":
    main()
