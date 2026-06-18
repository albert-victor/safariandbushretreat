#!/usr/bin/env python3
"""Generate Kenya overview and destination pages from data/kenya-data.json."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "kenya-data.json"
OUT = ROOT / "kenya"

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)


def build_kenya_overview(k: dict, destinations: list) -> str:
    paras = "".join(f"            <p>{p}</p>\n" for p in k.get("paragraphs", []))
    highlights = "".join(
        f'              <li><i class="fa-solid fa-check" aria-hidden="true"></i> {h}</li>\n'
        for h in k.get("highlights", [])
    )
    packages = pt.packages_html(k.get("packages", []), "index.html#bookingForm", "")
    grid = pt.dest_card_grid(destinations, "kenya/", img_prefix="")
    hero = pt.img_src(k.get("hero", ""), "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(k['name'] + ' | Safari and Bush Retreats', k.get('card_desc', ''), '')}
</head>
<body>
{pt.nav_html('', active='kenya', kenya_active=True)}

  <main id="main-content">
    <article class="dest-page circuit-page kenya-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="Kenya safari landscape" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="index.html#home" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Home</a>
          <span class="dest-page__badge">{k.get('badge', 'Kenya')}</span>
          <h1 class="dest-page__title">{k['name']}</h1>
          <p class="dest-page__meta">{k.get('meta', '')}</p>
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
{grid}{packages}          <div class="dest-page__cta">
            <p>Combine Kenya with your Tanzania safari for the ultimate East Africa journey.</p>
            <a href="index.html#bookingForm" class="btn btn--primary btn--lg">Plan Your Kenya Safari</a>
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


def build_kenya_dest(d: dict) -> str:
    paras = "".join(f"            <p>{p}</p>\n" for p in d.get("paragraphs", []))
    hero = pt.img_src(d.get("hero", ""), "../")
    gallery = pt.gallery_html(d.get("gallery", []), d["name"], "../")
    packages = pt.packages_html(d.get("packages", []), "../index.html#bookingForm", "../")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{pt.head_block(d['name'] + ' | Kenya Safaris', d.get('card_desc', ''), '../')}
</head>
<body>
{pt.nav_html('../', active='kenya', kenya_active=True)}

  <main id="main-content">
    <article class="dest-page kenya-page">
      <header class="dest-page__hero">
        <img src="{hero}" alt="{d['name']}" class="dest-page__hero-img" width="1400" height="700" decoding="async" referrerpolicy="no-referrer">
        <div class="dest-page__hero-overlay"></div>
        <div class="container dest-page__hero-content">
          <a href="../kenya.html" class="dest-page__back"><i class="fa-solid fa-arrow-left" aria-hidden="true"></i> Kenya Safaris</a>
          <span class="dest-page__badge">{d.get('badge', 'Kenya')}</span>
          <h1 class="dest-page__title">{d['name']}</h1>
          <p class="dest-page__meta">{d.get('meta', '')}</p>
        </div>
      </header>
      <section class="dest-page__body section">
        <div class="container dest-page__layout">
          <div class="dest-page__copy">
{paras}          </div>
{gallery}{packages}          <div class="dest-page__cta">
            <p>Ready to explore {d['name']}?</p>
            <a href="../index.html#bookingForm" class="btn btn--primary btn--lg">Plan Your Kenya Safari</a>
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
    k = data["kenya"]
    dests = data.get("destinations", [])
    OUT.mkdir(exist_ok=True)
    (ROOT / "kenya.html").write_text(build_kenya_overview(k, dests), encoding="utf-8")
    print("Wrote kenya.html")
    for d in dests:
        (OUT / f"{d['slug']}.html").write_text(build_kenya_dest(d), encoding="utf-8")
        print(f"Wrote kenya/{d['slug']}.html")
    print(f"Generated Kenya overview + {len(dests)} destination pages.")


if __name__ == "__main__":
    main()
