#!/usr/bin/env python3
"""Generate circuit pages with full destination grids from data/destinations.json."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "destinations.json"
PKG_DATA = ROOT / "data" / "safari-packages.json"
OUT = ROOT / "circuits"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)

CIRCUIT_META = {
    "northern-circuit": ("Northern Circuit", "Most Popular", "Jun - Oct · Classic Tanzania"),
    "southern-circuit": ("Southern Circuit", "Remote Wilderness", "May - Nov · Uncrowded"),
    "eastern-circuit": ("Eastern Circuit", "Rainforest & Coast", "Year-round · Adventure"),
    "western-circuit": ("Western Circuit", "Primates", "May - Oct · Lake Tanganyika"),
    "tanzania-oceanic-islands": ("Oceanic Islands", "Marine Reserves", "Dec - Mar · Indian Ocean"),
    "mafia-island": ("Mafia Island", "Marine Paradise", "Oct - Feb · Whale sharks"),
    "southern-highlands": ("Southern Highlands & Culture", "Heritage & Highlands", "Year-round · Iringa region"),
}

CIRCUIT_HERO_SLUG = {
    "northern-circuit": "serengeti",
    "southern-circuit": "ruaha",
    "eastern-circuit": "saadani",
    "western-circuit": "mahale",
    "tanzania-oceanic-islands": "chumbe-island",
    "mafia-island": "mafia",
    "southern-highlands": "isimila",
}


def pick_hero_dest(circuit_slug: str, destinations: list) -> dict:
    hero_slug = CIRCUIT_HERO_SLUG.get(circuit_slug)
    if hero_slug:
        for d in destinations:
            if d.get("slug") == hero_slug:
                return d
    return destinations[0] if destinations else {}


def grouped_grids(destinations: list, groups: list[tuple[str, list[str]]], dest_prefix: str = "../destinations/") -> str:
    by_slug = {d["slug"]: d for d in destinations}
    html = ""
    for heading, slugs in groups:
        group_dests = [by_slug[s] for s in slugs if s in by_slug]
        if group_dests:
            html += pt.dest_card_grid(group_dests, dest_prefix, heading=heading)
    return html


def filter_packages_for_slugs(packages: list, slugs: set[str]) -> list:
    out = []
    for p in packages:
        dest_slugs = set(p.get("destinationSlugs") or [])
        if dest_slugs & slugs:
            out.append(p)
    return out


def build_circuit_page(
    slug: str,
    name: str,
    badge: str,
    meta: str,
    circuit_name: str,
    destinations: list,
    intros: list,
    packages: list | None = None,
    dest_grids: str | None = None,
    back_href: str | None = None,
    back_label: str | None = None,
    copy_extra: str = "",
) -> str:
    paras = copy_extra + "".join(f"            <p>{p}</p>\n" for p in intros)
    hero_dest = pick_hero_dest(slug, destinations)
    hero = pt.img_src(hero_dest.get("hero", ""), "../")
    if not hero:
        hero = pt.img_src("nature.jpg", "../")
    grid = dest_grids if dest_grids is not None else pt.dest_card_grid(destinations, "../destinations/")
    back_link = ""
    if back_href and back_label:
        back_link = f'          <a href="{back_href}" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> {back_label}</a>\n'
    else:
        back_link = '          <a href="index.html" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All Circuits</a>\n'
    tour_count = len(packages or [])
    tour_meta = f" · {tour_count} tour{'s' if tour_count != 1 else ''}" if tour_count else ""
    pkg_section = ""
    if packages:
        pkg_items = []
        for p in sorted(packages, key=lambda x: (x.get("days") or 99, x.get("name", ""))):
            pkg_items.append({
                "name": p["name"],
                "slug": p["slug"],
                "days": p.get("days"),
                "price": p.get("price"),
                "hero": p.get("hero", ""),
                "description": (p.get("overview") or "")[:180],
            })
        pkg_section = pt.packages_html(pkg_items, "../index.html#bookingForm", "../")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(name + ' | Safari and Bush Retreats', intros[0] if intros else name, '../')}
</head>
<body>
{pt.nav_html('../', active='circuits')}

  <main id="main-content">
    <article class="dest-page circuit-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{name}" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
{back_link}          <span class="dest-page__badge">{badge}</span>
          <h1 class="dest-page__title">{name}</h1>
          <p class="dest-page__meta">{meta} · {len(destinations)} destinations{tour_meta}</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
{paras}          </div>
{grid}{pkg_section}          <div class="dest-page__cta">
            <p>Ready to explore the {name}?</p>
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
    intros = data.get("circuits", {})
    by_circuit: dict[str, list] = {}
    for d in data["destinations"]:
        by_circuit.setdefault(d["circuit"], []).append(d)

    pkg_by_circuit: dict[str, list] = {}
    if PKG_DATA.exists():
        pkg_data = json.loads(PKG_DATA.read_text(encoding="utf-8"))
        for p in pkg_data.get("packages", []):
            circuit = p.get("circuit", "")
            if circuit in ("Coastal & Islands", "Zanzibar & Islands", "Ocean Islands"):
                circuit = pt.OCEANIC_CIRCUIT_NAME
            pkg_by_circuit.setdefault(circuit, []).append(p)

    OUT.mkdir(exist_ok=True)
    ocean_all = by_circuit.get(pt.OCEANIC_CIRCUIT_NAME, [])
    ocean_pkgs_all = pkg_by_circuit.get(pt.OCEANIC_CIRCUIT_NAME, [])
    ocean_dests = [d for d in ocean_all if d["slug"] in pt.OCEAN_ISLANDS_SLUGS]
    ocean_pkgs = filter_packages_for_slugs(ocean_pkgs_all, pt.OCEAN_ISLANDS_SLUGS)
    zanzibar_dests = [d for d in ocean_all if d["slug"] in pt.ZANZIBAR_HUB_SLUGS]
    zanzibar_pkgs = filter_packages_for_slugs(ocean_pkgs_all, pt.ZANZIBAR_HUB_SLUGS)

    for slug, (name, badge, meta) in CIRCUIT_META.items():
        circuit_name = name
        dests = by_circuit.get(circuit_name, [])
        circuit_intros = intros.get(circuit_name, [f"Explore Tanzania's {name}."])
        pkgs = pkg_by_circuit.get(circuit_name, [])
        dest_grids = None
        copy_extra = ""
        if slug == "tanzania-oceanic-islands":
            dests = ocean_dests
            pkgs = ocean_pkgs
            circuit_intros = intros.get(circuit_name, pt.OCEAN_ISLANDS_INTRO)
            copy_extra = (
                '            <p class="circuit-page__hub-link">'
                '<a href="zanzibar.html">Explore Pemba &amp; Kilwa coast <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></a></p>\n'
            )
            dest_grids = grouped_grids(dests, pt.OCEAN_ISLANDS_GROUPS)
        (OUT / f"{slug}.html").write_text(
            build_circuit_page(
                slug, name, badge, meta, circuit_name, dests, circuit_intros, pkgs,
                dest_grids=dest_grids, copy_extra=copy_extra,
            ),
            encoding="utf-8",
        )
        print(f"Wrote circuits/{slug}.html ({len(dests)} destinations, {len(pkgs)} tours)")

    zanzibar_grids = grouped_grids(zanzibar_dests, pt.ZANZIBAR_HUB_GROUPS)
    (OUT / "zanzibar.html").write_text(
        build_circuit_page(
            "zanzibar",
            "Zanzibar",
            "Spice Islands",
            "Stone Town · Pemba · Kilwa",
            "Zanzibar",
            zanzibar_dests,
            pt.ZANZIBAR_HUB_INTRO,
            zanzibar_pkgs,
            dest_grids=zanzibar_grids,
            back_href=f"{pt.OCEANIC_CIRCUIT_SLUG}.html",
            back_label=pt.OCEANIC_CIRCUIT_NAME,
        ),
        encoding="utf-8",
    )
    print(f"Wrote circuits/zanzibar.html ({len(zanzibar_dests)} destinations, {len(zanzibar_pkgs)} tours)")
    print(f"Generated {len(CIRCUIT_META) + 1} circuit pages.")


if __name__ == "__main__":
    main()
