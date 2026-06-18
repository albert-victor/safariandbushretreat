#!/usr/bin/env python3
"""Convert homepage destinations grid to auto-swiping carousel with 8 iconic picks."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

KEEP_SLUGS = [
    "serengeti", "ngorongoro", "tarangire", "kilimanjaro",
    "ruaha", "mikumi", "mahale", "zanzibar",
]

START = '        <div class="destinations__slider-wrap">'
END = '      <!-- Signature Experiences Carousel'


def main():
    text = INDEX.read_text(encoding="utf-8")
    start_idx = text.index(START)
    end_idx = text.index(END)

    block = text[start_idx:end_idx]
    cards = re.findall(r"<article class=\"destination-card\">.*?</article>", block, re.DOTALL)

    kept = []
    for card in cards:
        for slug in KEEP_SLUGS:
            if f"destinations/{slug}.html" in card:
                kept.append(f'              <div class="swiper-slide">\n{card}\n              </div>')
                break

    if len(kept) != len(KEEP_SLUGS):
        found = []
        for card in cards:
            for slug in KEEP_SLUGS:
                if f"destinations/{slug}.html" in card:
                    found.append(slug)
        raise SystemExit(f"Expected {len(KEEP_SLUGS)} cards, got {len(kept)}. Found: {found}")

    new_block = f"""{START}
          <div class="swiper destinations-swiper" id="destinationsSwiper">
            <div class="swiper-wrapper">
{chr(10).join(kept)}
            </div>
          </div>
          <div class="destinations-pagination swiper-pagination"></div>
        </div>
      </div>

"""

    INDEX.write_text(text[:start_idx] + new_block + text[end_idx:], encoding="utf-8")
    print(f"Patched index.html with {len(kept)} destination slides.")


if __name__ == "__main__":
    main()
