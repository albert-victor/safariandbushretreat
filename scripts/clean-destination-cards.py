#!/usr/bin/env python3
"""Normalize destination card meta and card_desc (TT scrape duplicates)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"

CIRCUIT_SHORT = {
    "Northern Circuit": "Northern Tanzania",
    "Southern Circuit": "Southern Tanzania",
    "Eastern Circuit": "Eastern Tanzania",
    "Western Circuit": "Western Tanzania",
    "Ocean Islands": "Oceanic Islands",
    "Zanzibar & Islands": "Oceanic Islands",
    "Southern Highlands & Culture": "Southern Highlands",
}

GENERIC_BADGES = {"Explore", "Conservation", "Coastal", "Kilwa", "Island", "Songo"}


def is_scraped_meta(meta: str, name: str) -> bool:
    if not meta or len(meta) > 55:
        return True
    if name and meta.lower().startswith(name.lower()[:12]):
        return True
    if re.match(r"^[A-Z][a-z]+ (is|was|are|has|have|borders|situated|or )", meta):
        return True
    return False


def short_meta(d: dict) -> str:
    badge = d.get("badge", "").strip()
    circuit = d.get("circuit", "")
    region = CIRCUIT_SHORT.get(circuit, circuit.replace(" Circuit", ""))
    meta = d.get("meta", "").strip()

    if not is_scraped_meta(meta, d.get("name", "")):
        return meta[:60]

    if badge and badge not in GENERIC_BADGES:
        return f"{badge} · {region}"
    if badge == "Island":
        return f"Island · {region}"
    if badge == "Coastal":
        return f"Coastal · {region}"
    if badge == "Kilwa":
        return f"Historic Kilwa · {region}"
    if badge == "Songo":
        return f"Swahili ruins · {region}"

    name = d.get("name", "")
    if "National Park" in name or "Reserve" in name:
        return f"National Park · {region}"
    if "Island" in name:
        return f"Island · {region}"
    if "Lake" in name:
        return f"Lake · {region}"
    if "Mount" in name:
        return f"Mountain · {region}"
    return region


def same_start(a: str, b: str, n: int = 35) -> bool:
    if not a or not b:
        return False
    return a[:n].lower() == b[:n].lower()


def normalize_desc(d: dict, meta_line: str) -> str:
    desc = (d.get("card_desc") or d.get("shortDescription") or "").strip()
    meta_raw = d.get("meta", "").strip()
    paras = d.get("paragraphs") or []

    if same_start(desc, meta_raw) or same_start(desc, meta_line):
        for p in paras[1:]:
            p = p.strip()
            if len(p) > 40 and not same_start(p, meta_raw):
                desc = p
                break
        else:
            name = d.get("name", "this destination")
            desc = f"Discover {name} - tailored safari days and local highlights with Safari and Bush Retreats."

    if len(desc) > 130:
        cut = desc[:130]
        last = max(cut.rfind(". "), cut.rfind(", "))
        if last > 60:
            desc = cut[: last + 1].strip()
        else:
            desc = cut.strip() + "…"
    return desc


def main():
    core = json.loads(CORE.read_text(encoding="utf-8"))
    updated = 0
    for d in core["destinations"]:
        new_meta = short_meta(d)
        new_desc = normalize_desc(d, new_meta)
        if d.get("meta") != new_meta:
            d["meta"] = new_meta
            updated += 1
        if d.get("card_desc") != new_desc:
            d["card_desc"] = new_desc
            d["shortDescription"] = new_desc[:200]
            updated += 1
    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Cleaned destination card fields ({updated} updates)")


if __name__ == "__main__":
    main()
