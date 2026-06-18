#!/usr/bin/env python3
"""Generate safari category pages and circuits overview from data/destinations.json."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "destinations.json"
CAT_OUT = ROOT / "categories"
CIRCUIT_OUT = ROOT / "circuits"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)

CATEGORY_META = {
    "tanzania-safaris": (
        "Tanzania Safaris",
        "Wildlife",
        "National Parks & Game Reserves",
        "Classic wildlife safaris across Tanzania's finest national parks - Serengeti, Ngorongoro, Ruaha and beyond.",
        "serengeti",
    ),
    "adventure-safaris": (
        "Adventure Safaris",
        "Adventure",
        "Remote & Cultural",
        "Off-the-beaten-track adventures - chimpanzee trekking, cultural encounters and remote wilderness.",
        "mahale",
    ),
    "mountain-climbing": (
        "Mountain Climbing",
        "Peaks",
        "Kilimanjaro to Eastern Arc",
        "From Kilimanjaro's summit to Usambara forest trails - Tanzania's greatest mountain experiences.",
        "kilimanjaro",
    ),
    "beach-holiday": (
        "Beach Holiday",
        "Coastal",
        "Islands & Indian Ocean",
        "Pristine beaches, spice islands and Swahili coast retreats across Zanzibar, Pemba and Kilwa.",
        "zanzibar",
    ),
    "walking-safaris": (
        "Walking Safaris",
        "On Foot",
        "Forest & Bush Trails",
        "Guided bush walks and forest treks through Tanzania's untamed landscapes.",
        "amani-forest",
    ),
    "tourist-attractions": (
        "Tourist Attractions",
        "Heritage",
        "Culture & History",
        "Rock art, ancient ruins, caves and cultural landmarks across Tanzania.",
        "kondoa-rock-art",
    ),
}

SLUG_TO_CATEGORY: dict[str, str] = {}
for slug in (
    "serengeti", "ngorongoro", "tarangire", "lake-manyara", "arusha", "mikumi", "ruaha",
    "katavi", "nyerere", "saadani", "mkomazi", "burigi-chato", "ibanda-kyerwa",
    "ngurdoto-crater", "saanane",
):
    SLUG_TO_CATEGORY[slug] = "tanzania-safaris"
for slug in ("mahale", "gombe", "rubondo", "lake-eyasi", "lake-natron"):
    SLUG_TO_CATEGORY[slug] = "adventure-safaris"
for slug in (
    "kilimanjaro", "mount-meru", "oldonyo-lengai", "usambara", "uluguru", "pare-mountains",
    "udzungwa", "kitulo", "mpanga-kipengere", "kaporogwe-falls", "kalambo-falls", "lake-ngozi",
):
    SLUG_TO_CATEGORY[slug] = "mountain-climbing"
for slug in (
    "zanzibar", "pemba", "bongoyo-island", "chumbe-island", "fungu-yasin-sand-bar",
    "kilwa", "kilwa-kisiwani", "kilwa-kivinje", "kirui-island", "kwale-island", "maziwe-island",
    "mbudya-island", "mnemba-island", "mwewe-island", "pangavini-island", "sinda-island",
    "toten-island", "ulenge-island", "yambe-island", "prison-island", "pangani", "matema-beach",
    "mnazi-bay", "tanga-marine", "ukerewe",
):
    SLUG_TO_CATEGORY[slug] = "beach-holiday"
for slug in ("mafia", "chole-island", "bwejuu-island", "jibondo-island", "juani-island", "chole-bay"):
    SLUG_TO_CATEGORY[slug] = "beach-holiday"
for slug in ("amani-forest", "pugu-kazimzumbwi"):
    SLUG_TO_CATEGORY[slug] = "walking-safaris"
for slug in (
    "bagamoyo", "amboni-caves", "kondoa-rock-art", "igelegke-rock-art", "isimila", "gangilonga",
    "mbozi-meteorite", "lake-chala", "lake-jipe", "lake-nyasa", "lake-tanganyika", "lake-victoria",
    "songo-mnara",
):
    SLUG_TO_CATEGORY[slug] = "tourist-attractions"

CIRCUIT_INDEX = [
    ("northern-circuit", "Northern Circuit", "Most Popular", "Jun - Oct · Classic Tanzania", "serengeti"),
    ("southern-circuit", "Southern Circuit", "Remote Wilderness", "May - Nov · Uncrowded", "ruaha"),
    ("eastern-circuit", "Eastern Circuit", "Rainforest & Coast", "Year-round · Adventure", "saadani"),
    ("western-circuit", "Western Circuit", "Primates", "May - Oct · Lake Tanganyika", "mahale"),
    ("tanzania-oceanic-islands", "Oceanic Islands", "Marine Reserves", "Dec - Mar · Indian Ocean", "chumbe-island"),
    ("mafia-island", "Mafia Island", "Marine Paradise", "Oct - Feb · Whale sharks", "mafia"),
    ("southern-highlands", "Southern Highlands & Culture", "Heritage & Highlands", "Year-round · Iringa", "isimila"),
]


def by_slug(destinations: list) -> dict:
    return {d["slug"]: d for d in destinations}


def build_category_page(slug: str, title: str, badge: str, meta: str, intro: str, destinations: list) -> str:
    hero_dest = next((d for d in destinations if d.get("slug") == CATEGORY_META[slug][4]), destinations[0] if destinations else {})
    hero = pt.img_src(hero_dest.get("hero", ""), "../")
    if not hero:
        hero = pt.img_src("nature.jpg", "../")
    grid = pt.dest_card_grid(destinations, "../destinations/", heading=f"Destinations · {title}")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(title + ' | Safari and Bush Retreats', intro, '../')}
</head>
<body>
{pt.nav_html('../', active='safaris')}

  <main id="main-content">
    <article class="dest-page circuit-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{title}" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="../index.html#safaris" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> All Safaris</a>
          <span class="dest-page__badge">{badge}</span>
          <h1 class="dest-page__title">{title}</h1>
          <p class="dest-page__meta">{meta} · {len(destinations)} destinations</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
            <p>{intro}</p>
          </div>
{grid}          <div class="dest-page__cta">
            <p>Ready to plan your {title.lower()}?</p>
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


def build_circuits_index(dest_by_slug: dict, dest_count: int) -> str:
    cards = ""
    for slug, name, badge, meta, hero_slug in CIRCUIT_INDEX:
        hero_dest = dest_by_slug.get(hero_slug, {})
        hero = pt.img_src(hero_dest.get("hero", ""), "../")
        if not hero:
            hero = pt.img_src("nature.jpg", "../")
        cards += f"""            <article class="circuit-dest-card">
              <a href="{slug}.html" class="circuit-dest-card__link">
                <div class="circuit-dest-card__img-wrap">
                  <img src="{hero}" alt="{name}" loading="lazy" decoding="async" width="400" height="260" referrerpolicy="no-referrer">
                </div>
                <div class="circuit-dest-card__body">
                  <span class="circuit-dest-card__meta">{badge}</span>
                  <h3 class="circuit-dest-card__title">{name}</h3>
                  <p class="circuit-dest-card__desc">{meta}</p>
                </div>
              </a>
            </article>\n"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block('All Circuits | Safari and Bush Retreats', "Explore all Tanzania safari circuits - Northern, Southern, Eastern, Western, Oceanic Islands, Mafia Island and Southern Highlands.", '../')}
</head>
<body>
{pt.nav_html('../', active='circuits')}

  <main id="main-content">
    <article class="dest-page circuit-page">
      <header class="dest-page__hero">
        <img src="{pt.img_src('serengeti3.jpg', '../')}" alt="Tanzania Safari Circuits" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="../index.html#destinations" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Home</a>
          <span class="dest-page__badge">Explore Tanzania</span>
          <h1 class="dest-page__title">All Safari Circuits</h1>
          <p class="dest-page__meta">{len(CIRCUIT_INDEX)} circuits · {dest_count} destinations</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
            <p>Choose your circuit to browse every destination - from the iconic Northern plains to remote Western chimp forests and Zanzibar's spice islands.</p>
          </div>
          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Safari Circuits</h2>
            <div class="circuit-dest-grid">
{cards}            </div>
          </div>
          <div class="dest-page__cta">
            <p>Not sure which circuit suits you?</p>
            <a href="../index.html#bookingForm" class="btn btn--primary btn--lg">Get Expert Advice</a>
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
    destinations = data["destinations"]
    dest_by_slug = by_slug(destinations)

    unassigned = [d["slug"] for d in destinations if d["slug"] not in SLUG_TO_CATEGORY]
    if unassigned:
        raise SystemExit(f"Unassigned destinations: {unassigned}")

    by_cat: dict[str, list] = {k: [] for k in CATEGORY_META}
    for d in destinations:
        by_cat[SLUG_TO_CATEGORY[d["slug"]]].append(d)

    CAT_OUT.mkdir(exist_ok=True)
    for slug, (title, badge, meta, intro, _) in CATEGORY_META.items():
        page = build_category_page(slug, title, badge, meta, intro, by_cat[slug])
        (CAT_OUT / f"{slug}.html").write_text(page, encoding="utf-8")
        print(f"Wrote categories/{slug}.html ({len(by_cat[slug])} destinations)")

    index_page = build_circuits_index(dest_by_slug, len(destinations))
    (CIRCUIT_OUT / "index.html").write_text(index_page, encoding="utf-8")
    print("Wrote circuits/index.html")


if __name__ == "__main__":
    main()
