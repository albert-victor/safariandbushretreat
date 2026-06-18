#!/usr/bin/env python3
"""Shared HTML templates for generated subpages."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Site contact - inquiries route to Safari & Bush Retreats team
SITE_OWNER = "Ally Shebe"
SITE_EMAIL = "info@safariandbushretreats.com"
SITE_PHONE = "+255 768 373 033"
SITE_WHATSAPP = "255768373033"

OCEANIC_CIRCUIT_NAME = "Oceanic Islands"
OCEANIC_CIRCUIT_SLUG = "tanzania-oceanic-islands"

# TT ocean-islands: marine reserves & sandbars (not Zanzibar/Pemba/Kilwa main islands)
OCEAN_ISLANDS_SLUGS = {
    "mbudya-island", "bongoyo-island", "pangavini-island", "fungu-yasin-sand-bar",
    "maziwe-island", "kirui-island", "kwale-island", "sinda-island", "toten-island",
    "ulenge-island", "yambe-island", "mwewe-island", "chumbe-island", "mnemba-island",
}

OCEAN_ISLANDS_GROUPS = [
    ("Dar es Salaam Marine Reserves", ["mbudya-island", "bongoyo-island", "pangavini-island", "fungu-yasin-sand-bar"]),
    ("Coastal Reef Sanctuaries", [
        "maziwe-island", "kirui-island", "kwale-island", "sinda-island",
        "toten-island", "ulenge-island", "yambe-island", "mwewe-island",
    ]),
    ("Zanzibar Marine Parks", ["chumbe-island", "mnemba-island"]),
]

OCEAN_ISLANDS_INTRO = [
    "Oceanic Islands brings together Indian Ocean marine reserves, sandbars and conservation areas along the Swahili coast - from boat day trips off Dar es Salaam to Chumbe and Mnemba.",
    "Snorkel coral gardens, picnic on uninhabited sandbars and explore protected reefs where sea turtles, reef fish and dolphins thrive along the Swahili coast.",
]

ZANZIBAR_HUB_SLUG = "zanzibar"
ZANZIBAR_HUB_SLUGS = {
    "zanzibar", "pemba", "prison-island",
    "kilwa", "kilwa-kisiwani", "kilwa-kivinje", "songo-mnara",
}

ZANZIBAR_HUB_GROUPS = [
    ("Main Islands", ["zanzibar", "pemba"]),
    ("Kilwa & Swahili Coast", ["kilwa", "kilwa-kisiwani", "kilwa-kivinje", "songo-mnara"]),
    ("Stone Town Day Trips", ["prison-island"]),
]

ZANZIBAR_HUB_INTRO = [
    "Zanzibar, Pemba and the historic Kilwa coast - Tanzania's spice islands and Swahili heritage on the Indian Ocean.",
    "From UNESCO Stone Town and clove-scented Pemba to the medieval ruins of Kilwa Kisiwani, this region pairs culture, beach and diving with easy access from Dar es Salaam.",
]


def build_circuit_nav(circuit_prefix: str, dest_prefix: str, kenya_href: str, uganda_href: str, rwanda_href: str, mobile: bool = False) -> str:
    """Flat circuits list - destinations live on hub pages, not nav submenus."""
    indent = "            " if mobile else "          "
    role = "" if mobile else ' role="menuitem"'
    lines = [
        f'{indent}<li><a href="{circuit_prefix}northern-circuit.html"{role}>Northern Circuit</a></li>',
        f'{indent}<li><a href="{circuit_prefix}southern-circuit.html"{role}>Southern Circuit</a></li>',
        f'{indent}<li><a href="{circuit_prefix}eastern-circuit.html"{role}>Eastern Circuit</a></li>',
        f'{indent}<li><a href="{circuit_prefix}western-circuit.html"{role}>Western Circuit</a></li>',
        f'{indent}<li><a href="{circuit_prefix}{OCEANIC_CIRCUIT_SLUG}.html"{role}>{OCEANIC_CIRCUIT_NAME}</a></li>',
        f'{indent}<li><a href="{circuit_prefix}zanzibar.html"{role}>Zanzibar</a></li>',
        f'{indent}<li><a href="{circuit_prefix}mafia-island.html"{role}>Mafia Island</a></li>',
    ]
    if mobile:
        lines.append(f'{indent}<li class="mobile-menu__dest-divider" aria-hidden="true"><span>East Africa</span></li>')
    lines.extend([
        f'{indent}<li><a href="{kenya_href}"{role}>Kenya</a></li>',
        f'{indent}<li><a href="{uganda_href}"{role}>Uganda</a></li>',
        f'{indent}<li><a href="{rwanda_href}"{role}>Rwanda</a></li>',
    ])
    return "\n".join(lines)

SAFARI_CATEGORY_NAV = """              <li><a href="{prefix}safaris/index.html" role="menuitem">All Packages</a></li>
              <li><a href="{category_prefix}tanzania-safaris.html" role="menuitem">Tanzania Safaris</a></li>
              <li><a href="{category_prefix}adventure-safaris.html" role="menuitem">Adventure Safaris</a></li>
              <li><a href="{category_prefix}mountain-climbing.html" role="menuitem">Mountain Climbing</a></li>
              <li><a href="{category_prefix}beach-holiday.html" role="menuitem">Beach Holiday</a></li>
              <li><a href="{category_prefix}walking-safaris.html" role="menuitem">Walking Safaris</a></li>
              <li><a href="{category_prefix}tourist-attractions.html" role="menuitem">Tourist Attractions</a></li>"""

MOBILE_SAFARI_CATEGORY_NAV = """                <li><a href="{prefix}safaris/index.html">All Packages</a></li>
                <li><a href="{category_prefix}tanzania-safaris.html">Tanzania Safaris</a></li>
                <li><a href="{category_prefix}adventure-safaris.html">Adventure Safaris</a></li>
                <li><a href="{category_prefix}mountain-climbing.html">Mountain Climbing</a></li>
                <li><a href="{category_prefix}beach-holiday.html">Beach Holiday</a></li>
                <li><a href="{category_prefix}walking-safaris.html">Walking Safaris</a></li>
                <li><a href="{category_prefix}tourist-attractions.html">Tourist Attractions</a></li>"""

CIRCUIT_SLUGS = {
    "Northern Circuit": "northern-circuit",
    "Southern Circuit": "southern-circuit",
    "Eastern Circuit": "eastern-circuit",
    "Western Circuit": "western-circuit",
    OCEANIC_CIRCUIT_NAME: OCEANIC_CIRCUIT_SLUG,
    "Mafia Island": "mafia-island",
    "Southern Highlands & Culture": "southern-highlands",
}


def clean_meta(meta: str, circuit: str) -> str:
    if not meta or ">" in meta or len(meta) < 8:
        return circuit
    return meta.replace('"', "").strip()


def card_meta_line(d: dict) -> str:
    meta = clean_meta(d.get("meta", ""), d.get("circuit", ""))
    name = d.get("name", "")
    if len(meta) > 55 or (name and meta.lower().startswith(name.lower()[:15])):
        badge = d.get("badge", "")
        circuit = d.get("circuit", "").replace(" Circuit", "").replace(" & Islands", "")
        if badge and badge not in ("Explore", "Conservation"):
            return f"{badge} · {circuit or 'Tanzania'}"
        return circuit or "Tanzania"
    return meta[:60]


def card_desc_text(d: dict) -> str:
    desc = (d.get("card_desc") or "").strip()
    meta = d.get("meta", "")
    if desc and meta and desc[:40].lower() == meta[:40].lower():
        paras = d.get("paragraphs") or []
        if len(paras) > 1:
            desc = paras[1].strip()
    if len(desc) <= 120:
        return desc
    trimmed = desc[:117].rsplit(" ", 1)[0]
    return trimmed + "…"


def img_src(path: str, prefix: str = "../") -> str:
    if not path:
        return ""
    if path.startswith("http"):
        return path
    return prefix + "assets/images/" + path.replace(" ", "%20").replace("+", "%2B")


def destination_back_link(d: dict) -> tuple[str, str]:
    slug = d.get("slug", "")
    if slug in ZANZIBAR_HUB_SLUGS:
        return "zanzibar.html", "Zanzibar"
    if slug in OCEAN_ISLANDS_SLUGS:
        return f"{OCEANIC_CIRCUIT_SLUG}.html", OCEANIC_CIRCUIT_NAME
    circuit = d.get("circuit", "")
    return CIRCUIT_SLUGS.get(circuit, "northern-circuit") + ".html", circuit


def nav_html(prefix: str = "../", active: str = "circuits", kenya_active: bool = False) -> str:
    circuits_active = ' active' if active in ("circuits", "kenya", "uganda", "rwanda") else ""
    about_active = ' active' if active == "about" else ""
    safaris_active = ' active' if active == "safaris" else ""
    accommodation_active = ' active' if active == "accommodation" else ""
    circuit_prefix = f"{prefix}circuits/"
    dest_prefix = f"{prefix}destinations/"
    category_prefix = f"{prefix}categories/"
    kenya_href = f"{prefix}kenya.html"
    uganda_href = f"{prefix}uganda.html"
    rwanda_href = f"{prefix}rwanda.html"
    circuit_nav = build_circuit_nav(circuit_prefix, dest_prefix, kenya_href, uganda_href, rwanda_href, mobile=False)
    mobile_circuit_nav = build_circuit_nav(circuit_prefix, dest_prefix, kenya_href, uganda_href, rwanda_href, mobile=True)
    return f"""  <header class="navbar navbar--solid navbar--scrolled" id="navbar" role="banner">
    <div class="container navbar__inner">
      <a href="{prefix}index.html#home" class="navbar__logo" aria-label="Safari and Bush Retreats - Home">
        <img src="{prefix}assets/images/logo-nav.png" alt="" class="navbar__logo-mark" width="40" height="40" decoding="async">
        <span class="navbar__logo-text">Safari &amp; Bush<span class="navbar__logo-accent">Retreats</span></span>
      </a>
      <nav class="navbar__nav" id="navbarNav" role="navigation" aria-label="Main navigation">
        <ul class="navbar__list">
          <li><a href="{prefix}index.html#home" class="navbar__link">Home</a></li>
          <li class="navbar__item navbar__item--has-dropdown">
            <a href="{prefix}index.html#destinations" class="navbar__link{circuits_active}">Circuits</a>
            <ul class="navbar__dropdown" role="menu">
{circuit_nav}
            </ul>
          </li>
          <li><a href="{prefix}about.html" class="navbar__link{about_active}">About Us</a></li>
          <li><a href="{prefix}index.html#experiences" class="navbar__link">Experiences</a></li>
          <li class="navbar__item navbar__item--has-dropdown">
            <a href="{prefix}index.html#safaris" class="navbar__link{safaris_active}">Safaris</a>
            <ul class="navbar__dropdown" role="menu">
{SAFARI_CATEGORY_NAV.format(prefix=prefix, category_prefix=category_prefix)}
            </ul>
          </li>
          <li><a href="{prefix}index.html#accommodation" class="navbar__link{accommodation_active}">Accommodation</a></li>
          <li><a href="{prefix}index.html#gallery" class="navbar__link">Gallery</a></li>
        </ul>
      </nav>
      <div class="navbar__tools">
        <button type="button" class="theme-toggle" id="themeToggle" aria-label="Switch theme" aria-pressed="false">
          <i class="fa-solid fa-moon theme-toggle__icon theme-toggle__icon--moon" aria-hidden="true"></i>
          <i class="fa-solid fa-sun theme-toggle__icon theme-toggle__icon--sun" aria-hidden="true"></i>
        </button>
        <a href="{prefix}index.html#bookingForm" class="btn btn--primary btn--sm navbar__cta">Book Safari</a>
        <button class="navbar__toggle" id="navbarToggle" aria-label="Open navigation menu" aria-expanded="false" aria-controls="mobileMenu">
          <span class="navbar__toggle-bar"></span>
          <span class="navbar__toggle-bar"></span>
          <span class="navbar__toggle-bar"></span>
        </button>
      </div>
    </div>
  </header>

  <div class="mobile-menu" id="mobileMenu" aria-hidden="true" role="dialog" aria-label="Mobile navigation">
    <div class="mobile-menu__overlay" id="mobileMenuOverlay"></div>
    <div class="mobile-menu__panel">
      <button class="mobile-menu__close" id="mobileMenuClose" aria-label="Close navigation menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M18 6L6 18M6 6l12 12"/></svg>
      </button>
      <div class="mobile-menu__theme">
        <button type="button" class="theme-toggle" id="themeToggleMobile" aria-label="Switch theme" aria-pressed="false">
          <i class="fa-solid fa-moon theme-toggle__icon theme-toggle__icon--moon" aria-hidden="true"></i>
          <i class="fa-solid fa-sun theme-toggle__icon theme-toggle__icon--sun" aria-hidden="true"></i>
        </button>
      </div>
      <nav aria-label="Mobile navigation">
        <ul class="mobile-menu__list">
          <li><a href="{prefix}index.html#home" class="mobile-menu__link">Home</a></li>
          <li class="mobile-menu__item mobile-menu__item--dest">
            <button type="button" class="mobile-menu__link mobile-menu__dest-trigger" aria-expanded="false" aria-controls="mobileDestPanel">
              <span>Circuits</span>
              <span class="mobile-menu__dest-plus" aria-hidden="true">+</span>
              <i class="fa-solid fa-chevron-down mobile-menu__dest-chevron" aria-hidden="true"></i>
            </button>
            <div class="mobile-menu__dest-panel" id="mobileDestPanel">
              <a href="{circuit_prefix}index.html" class="mobile-menu__dest-overview">View all circuits</a>
              <ul class="mobile-menu__dest-grid">
{mobile_circuit_nav}
              </ul>
            </div>
          </li>
          <li><a href="{prefix}about.html" class="mobile-menu__link">About Us</a></li>
          <li><a href="{prefix}index.html#experiences" class="mobile-menu__link">Experiences</a></li>
          <li class="mobile-menu__item mobile-menu__item--dest">
            <button type="button" class="mobile-menu__link mobile-menu__dest-trigger" aria-expanded="false" aria-controls="mobileSafariPanel">
              <span>Safaris</span>
              <span class="mobile-menu__dest-plus" aria-hidden="true">+</span>
              <i class="fa-solid fa-chevron-down mobile-menu__dest-chevron" aria-hidden="true"></i>
            </button>
            <div class="mobile-menu__dest-panel" id="mobileSafariPanel">
              <a href="{prefix}safaris/index.html" class="mobile-menu__dest-overview">All safari packages</a>
              <ul class="mobile-menu__dest-grid">
{MOBILE_SAFARI_CATEGORY_NAV.format(prefix=prefix, category_prefix=category_prefix)}
              </ul>
            </div>
          </li>
          <li><a href="{prefix}index.html#accommodation" class="mobile-menu__link">Accommodation</a></li>
          <li><a href="{prefix}index.html#gallery" class="mobile-menu__link">Gallery</a></li>
        </ul>
      </nav>
      <a href="{prefix}index.html#bookingForm" class="btn btn--primary mobile-menu__cta">Book Your Safari</a>
    </div>
  </div>"""


def _gtm_id() -> str:
    cfg = json.loads((ROOT / "data" / "site-config.json").read_text(encoding="utf-8"))
    return (cfg.get("gtmContainerId") or "").strip()


def gtm_head_snippet() -> str:
    gtm_id = _gtm_id()
    if not gtm_id:
        return ""
    return f"""  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','{gtm_id}');</script>
  <!-- End Google Tag Manager -->"""


def gtm_body_snippet() -> str:
    gtm_id = _gtm_id()
    if not gtm_id:
        return ""
    return f"""  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id}"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <!-- End Google Tag Manager (noscript) -->"""


def head_block(title: str, description: str, css_prefix: str) -> str:
    gtm = gtm_head_snippet()
    gtm_block = f"\n{gtm}" if gtm else ""
    return f"""  <meta charset="UTF-8">{gtm_block}
  <script>
    (function () {{
      try {{
        var t = localStorage.getItem('sbr-theme');
        if (t === 'light') document.documentElement.setAttribute('data-theme', 'light');
      }} catch (e) {{}}
    }})();
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{description[:160]}">
  <link rel="icon" type="image/png" href="{css_prefix}assets/images/favicon.png">
  <link rel="apple-touch-icon" href="{css_prefix}assets/images/apple-touch-icon.png">
  <link rel="stylesheet" href="{css_prefix}vendor/fonts/fonts.css">
  <link rel="stylesheet" href="{css_prefix}vendor/font-awesome/css/all.min.css">
  <link rel="stylesheet" href="{css_prefix}css/style.css">
  <link rel="stylesheet" href="{css_prefix}css/responsive.css">
  <link rel="stylesheet" href="{css_prefix}css/theme.css">
  <link rel="stylesheet" href="{css_prefix}css/destination-page.css">
  <link rel="stylesheet" href="{css_prefix}css/performance.css">"""


def dest_tags(d: dict) -> list[str]:
    tags = (d.get("keyAttractions") or d.get("activities") or [])[:3]
    if tags:
        return tags
    badge = d.get("badge", "")
    if badge and badge not in ("Explore", "Conservation"):
        return [badge]
    return []


def packages_html(packages: list, contact_href: str, prefix: str = "../") -> str:
    if not packages:
        return ""
    items = ""
    for p in packages:
        days = p.get("days")
        days_label = f'{days} Days' if days else "Safari"
        price = p.get("price") or "Enquire"
        price_html = f'From <span>{price}</span> / person' if price != "Enquire" else "Price on request"
        slug = p.get("slug")
        href = f"{prefix}safaris/{slug}.html" if slug else contact_href
        btn = "View Itinerary" if slug else "Enquire"
        hero = p.get("hero", "")
        img_block = ""
        if hero:
            src = img_src(hero, prefix)
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
                <p class="circuit-page__package-desc">{p.get("description", p["name"])}</p>
                <a href="{href}" class="btn btn--outline btn--sm">{btn}</a>
              </div>
            </article>\n"""
    return f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Safari Packages</h2>
            <div class="circuit-page__packages">
{items}            </div>
          </div>\n"""


def faqs_html(faqs: list) -> str:
    if not faqs:
        return ""
    items = ""
    for f in faqs:
        items += f"""            <details class="dest-page__faq">
              <summary>{f["q"]}</summary>
              <p>{f["a"]}</p>
            </details>\n"""
    return f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">Frequently Asked Questions</h2>
            <div class="dest-page__faqs">
{items}            </div>
          </div>\n"""


def gallery_html(gallery: list, name: str, prefix: str = "../") -> str:
    if not gallery:
        return ""
    figs = ""
    for g in gallery[:4]:
        src = img_src(g, prefix)
        if not src:
            continue
        figs += f"""          <figure class="dest-page__figure">
            <img src="{src}" alt="{name} landscape" loading="lazy" decoding="async" width="600" height="400" referrerpolicy="no-referrer">
          </figure>\n"""
    if not figs:
        return ""
    return f"""          <div class="dest-page__gallery">
{figs}          </div>\n"""


def dest_card_grid(
    destinations: list,
    dest_prefix: str = "../destinations/",
    img_prefix: str | None = None,
    heading: str = "Destinations in this Circuit",
) -> str:
    if img_prefix is None:
        img_prefix = dest_prefix.replace("destinations/", "")
    cards = ""
    for d in destinations:
        hero = img_src(d.get("hero", ""), img_prefix)
        tour_count = len(d.get("relatedPackages") or d.get("packages") or [])
        tours_html = ""
        if tour_count:
            tours_label = f"{tour_count} Tour{'s' if tour_count != 1 else ''}"
            tours_html = f'                    <span class="circuit-dest-card__tours"><i class="fa-solid fa-camera" aria-hidden="true"></i> {tours_label}</span>\n'
        tags = dest_tags(d)
        tags_html = ""
        if tags:
            tag_items = "".join(
                f'<span class="circuit-dest-card__tag">{t}</span>' for t in tags
            )
            tags_html = f'                  <div class="circuit-dest-card__tags">{tag_items}</div>\n'
        cards += f"""            <article class="circuit-dest-card">
              <a href="{dest_prefix}{d['slug']}.html" class="circuit-dest-card__link">
                <div class="circuit-dest-card__img-wrap">
                  <img src="{hero}" alt="{d['name']}" loading="lazy" decoding="async" width="400" height="260" referrerpolicy="no-referrer">
                </div>
                <div class="circuit-dest-card__body">
                  <span class="circuit-dest-card__meta">{card_meta_line(d)}</span>
                  <h3 class="circuit-dest-card__title">{d['name']}</h3>
                  <p class="circuit-dest-card__desc">{card_desc_text(d)}</p>
{tags_html}                  <div class="circuit-dest-card__footer">
{tours_html}                    <span class="circuit-dest-card__explore">Explore <i class="fa-solid fa-arrow-right" aria-hidden="true"></i></span>
                  </div>
                </div>
              </a>
            </article>\n"""
    return f"""          <div class="circuit-page__section">
            <h2 class="circuit-page__heading">{heading}</h2>
            <div class="circuit-dest-grid">
{cards}            </div>
          </div>\n"""
