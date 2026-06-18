#!/usr/bin/env python3
"""Assign unique local Kenya images."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KENYA_DATA = ROOT / "data" / "kenya-data.json"

KENYA_IMAGES = {
    "kenya": {
        "hero": "external/kenya/kenya-overview-cropped-enock-mzungu-scaled-1.png.jpg",
        "gallery": [
            "external/kenya/kenya-gallery-1-enock-mzungu-scaled.png.jpg",
            "external/kenya/sneha-cecil-DEBrMzu-D8I-unsplash-1-scaled.jpg",
        ],
    },
    "masai-mara": {
        "hero": "external/kenya/grace-nandi-2WnwPUTAcao-unsplash-scaled.jpg",
        "gallery": [
            "external/kenya/redcharlie-WQRdXOBJLV0-unsplash-scaled.jpg",
            "external/kenya/kenya-gallery-1-enock-mzungu-scaled.png.jpg",
        ],
    },
    "amboseli": {
        "hero": "external/kenya/wolfgang-hasselmann-czm3hOW1mMk-unsplash-scaled.jpg",
        "gallery": [
            "external/kenya/amboseli-gal-0-photo-1568605117036-5fe5e7bab0b7.jpg",
            "external/kenya/IMG-20250504-WA0029.jpg",
        ],
    },
    "samburu": {
        "hero": "external/kenya/jasper-gribble-IZIJdYq6elY-unsplash-scaled.jpg",
        "gallery": [
            "external/kenya/kadyn-pierce-FhXf_8o5jTs-unsplash-1-scaled.jpg",
            "external/kenya/mike-setchell-pf97TYdQlWM-unsplash.jpg",
        ],
    },
    "lake-nakuru": {
        "hero": "external/kenya/6048440574685591845_121.jpg",
        "gallery": ["external/kenya/6048440574685591842_121.jpg"],
    },
    "lake-naivasha": {
        "hero": "external/kenya/lake-naivasha-photo-1505142468610-359e7d316be0.jpg",
        "gallery": ["external/kenya/jay-wennington-s-fD5Tpew2k-unsplash.jpg"],
    },
    "diani-beach": {
        "hero": "external/kenya/diani-beach-photo-1559827260-dc66d52bef19.jpg",
        "gallery": [
            "external/kenya/diani-beach-gal-1-photo-1519046904884-53103b34b206.jpg",
            "external/kenya/sneha-cecil-DEBrMzu-D8I-unsplash-1-scaled.jpg",
        ],
    },
}


def main():
    kenya = json.loads(KENYA_DATA.read_text(encoding="utf-8"))
    overview = KENYA_IMAGES["kenya"]
    kenya["kenya"]["hero"] = overview["hero"]
    kenya["kenya"]["gallery"] = overview["gallery"]
    for d in kenya["destinations"]:
        imgs = KENYA_IMAGES.get(d["slug"])
        if imgs:
            d["hero"] = imgs["hero"]
            d["gallery"] = imgs["gallery"]
    KENYA_DATA.write_text(json.dumps(kenya, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Updated Kenya image assignments")


if __name__ == "__main__":
    main()
