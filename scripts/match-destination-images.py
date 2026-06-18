#!/usr/bin/env python3
"""Match destination heroes/galleries to image filenames; assign Oceanic Islands circuit."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "data" / "tanzania-core.json"
PKG = ROOT / "data" / "safari-packages.json"
IMAGE_ROOT = ROOT / "assets" / "images"
IMAGE_DIRS = [IMAGE_ROOT, IMAGE_ROOT / "external" / "tt", IMAGE_ROOT / "external" / "kenya"]

OCEAN_ISLANDS_CIRCUIT = "Oceanic Islands"
MAFIA_CIRCUIT = "Mafia Island"
MAFIA_SLUGS = {
    "mafia", "chole-island", "bwejuu-island", "jibondo-island", "juani-island", "chole-bay",
}
OCEAN_CIRCUIT_SLUGS = {
    "zanzibar", "pemba", "prison-island", "chumbe-island", "mnemba-island",
    "mbudya-island", "bongoyo-island", "pangavini-island", "maziwe-island", "kirui-island",
    "kwale-island", "sinda-island", "toten-island", "ulenge-island", "yambe-island",
    "mwewe-island", "fungu-yasin-sand-bar",
    "kilwa", "kilwa-kisiwani", "kilwa-kivinje", "songo-mnara",
}

GENERIC_BAD = re.compile(
    r"(culture\s*tours?|camping|beach-holiday|beach2|beach\s*destination|"
    r"^nature\d*\.|^masai\.|serengeti(?!-)|^mountains\.|national\s*park\.jpg$|"
    r"bachelor|tourism-and-cultural|degree-in-tourism)",
    re.I,
)

SLUG_ALIASES: dict[str, list[str]] = {
    "lake-manyara": ["lake manyara", "manyara"],
    "lake-eyasi": ["lake eyasi", "lake_eyasi", "eyasi"],
    "lake-natron": ["lake natron", "natron"],
    "lake-chala": ["lake chala", "chala"],
    "lake-jipe": ["lake jipe", "jipe"],
    "lake-ngozi": ["lake ngozi", "ngozi"],
    "lake-nyasa": ["lake nyasa", "nyasa"],
    "lake-tanganyika": ["lake tanganyika", "tanganyika"],
    "lake-victoria": ["lake victoria", "victoria"],
    "mount-meru": ["mount meru", "meru"],
    "oldonyo-lengai": ["oldonyo lengai", "oldoinyo", "lengai"],
    "ngorongoro": ["ngorongoro"],
    "mpanga-kipengere": ["mpanga kipengere", "mpanga", "kipengere"],
    "nyerere": ["nyerere", "selous"],
    "gangilonga": ["gangilonga", "iringa"],
    "isimila": ["isimila", "iringa"],
    "prison-island": ["changuu", "prison"],
    "pemba": ["pemba"],
    "mkomazi": ["mkomazi"],
    "katavi": ["katavi"],
    "ruaha": ["ruaha"],
    "mikumi": ["mikumi"],
    "kitulo": ["kitulo"],
    "udzungwa": ["udzungwa"],
    "gombe": ["gombe"],
    "mahale": ["mahale"],
    "kilimanjaro": ["kilimanjaro", "kili"],
    "serengeti": ["serengeti"],
    "tarangire": ["tarangire"],
    "arusha": ["arusha"],
    "bagamoyo": ["bagamoyo"],
    "saadani": ["saadani"],
    "zanzibar": ["zanzibar", "stone town", "unguja"],
}


def rel_path(path: Path) -> str:
    return str(path.relative_to(IMAGE_ROOT)).replace("\\", "/")


def collect_images() -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for base in IMAGE_DIRS:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if "opt" in p.parts:
                continue
            if p.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                continue
            out.append((rel_path(p), p))
    return out


def tokens(slug: str, name: str) -> list[str]:
    parts = slug.replace("_", "-").split("-")
    aliases = SLUG_ALIASES.get(slug, [])
    name_bits = re.findall(r"[a-z]{3,}", name.lower())
    raw = parts + aliases + name_bits
    seen: set[str] = set()
    out: list[str] = []
    for t in raw:
        t = t.strip().lower()
        if len(t) < 3 or t in {"national", "park", "island", "lake", "mount", "mountains"}:
            continue
        if t not in seen:
            seen.add(t)
            out.append(t)
    # full slug phrase
    phrase = slug.replace("-", " ")
    if phrase not in seen:
        out.insert(0, phrase)
    return out


def score_image(rel: str, slug: str, toks: list[str], for_hero: bool = False) -> int:
    base = Path(rel).stem.lower().replace("_", " ").replace("-", " ")
    if GENERIC_BAD.search(base) and slug not in base.replace(" ", "-"):
        return -100
    wrong_hints = ["serengeti", "migration", "gnus"]
    if slug not in ("serengeti",) and any(w in base for w in wrong_hints):
        return -100

    score = 0
    if rel.startswith(f"external/tt/{slug}-"):
        score += 200
    if slug.replace("-", " ") in base or slug.replace("-", "_") in base:
        score += 150
    for t in toks:
        if t in base:
            score += 30 + len(t)
    if for_hero and re.search(r"-g\d+-", rel):
        score -= 80
    return score


def pick_images(slug: str, name: str, pool: list[tuple[str, Path]], used: set[str]) -> tuple[str, list[str]]:
    toks = tokens(slug, name)
    ranked = sorted(
        ((rel, score_image(rel, slug, toks, for_hero=True)) for rel, _ in pool),
        key=lambda x: x[1],
        reverse=True,
    )
    hero = ""
    gallery: list[str] = []
    for rel, sc in ranked:
        if sc < 20 or rel in used:
            continue
        if not hero:
            hero = rel
            used.add(rel)
            continue
        if len(gallery) < 2:
            gscore = score_image(rel, slug, toks)
            base = Path(rel).stem.lower().replace("_", " ").replace("-", " ")
            if gscore >= 15 and any(t in base for t in toks):
                gallery.append(rel)
                used.add(rel)
        if hero and len(gallery) >= 2:
            break
    return hero, gallery


def fix_corrupt_entries(by_slug: dict) -> None:
    """Re-scrape entries where TT returned wrong Serengeti placeholder content."""
    import importlib.util

    spec_sc = importlib.util.spec_from_file_location("sc", ROOT / "scripts" / "scrape-tourism-content.py")
    sc = importlib.util.module_from_spec(spec_sc)
    spec_sc.loader.exec_module(sc)

    fixes = {
        "pemba": ("pemba-island", OCEAN_ISLANDS_CIRCUIT, "Pemba Island"),
        "prison-island": ("prison-island-changuu", OCEAN_ISLANDS_CIRCUIT, "Prison Island (Changuu)"),
        "bagamoyo": ("bagamoyo-historical-town", "Eastern Circuit", "Bagamoyo Historical Town"),
    }
    for slug, (tt_slug, circuit, proper_name) in fixes.items():
        d = by_slug.get(slug)
        corrupt = d and (
            "Serengeti National Park" in d.get("name", "")
            or "Serengeti" in d.get("card_desc", "")
            or any("Serengeti National Park is undoubtedly" in p for p in d.get("paragraphs", []))
            or (slug == "bagamoyo" and "Bagamoyo" not in d.get("name", ""))
        )
        if not corrupt:
            continue
        print(f"  fixing corrupt content: {slug}")
        raw = sc.scrape_one(slug, tt_slug, circuit)
        if raw and "Serengeti National Park" not in raw.get("name", ""):
            d["name"] = raw["name"]
            d["meta"] = raw.get("meta", circuit)
            d["card_desc"] = raw["card_desc"][:200]
            d["shortDescription"] = d["card_desc"]
            d["paragraphs"] = raw.get("paragraphs", [])[:3] or [d["card_desc"]]
            d["badge"] = raw.get("badge", "Coastal")
        else:
            d["name"] = proper_name
            if slug == "pemba":
                d["meta"] = "Indian Ocean · Spice islands · Year-round"
                d["card_desc"] = (
                    f"{proper_name} - spice plantations, coral reefs and Swahili culture in the Zanzibar archipelago."
                )
                d["badge"] = "Island"
            elif slug == "prison-island":
                d["meta"] = "Zanzibar · Half-day dhow trip · Giant tortoises"
                d["card_desc"] = (
                    f"{proper_name} - giant tortoises, snorkelling and a short dhow ride from Stone Town."
                )
                d["badge"] = "Island"
            else:
                d["meta"] = "Heritage · Swahili coast · Year-round"
                d["card_desc"] = (
                    "UNESCO-listed Swahili trading town - slave-trade history, Kaole ruins and coastal culture north of Dar es Salaam."
                )
                d["badge"] = "Heritage"
                d["hero"] = "bagamoyo1.jpg"
                d["gallery"] = ["bagamoyo2.jpg", "Ruins_of_Old_Port_in_Bagamoyo_02.jpg"]
            d["shortDescription"] = d["card_desc"]
            d["paragraphs"] = [d["card_desc"]]
        d["circuit"] = circuit

    # Pemba / Prison Island - use dedicated local photos
    if "pemba" in by_slug:
        by_slug["pemba"]["hero"] = "pemba-island.jpg"
        by_slug["pemba"]["gallery"] = ["zanzibar.jpg", "Zanzibar_Island_Stone_Town_01.jpg"]
    if "prison-island" in by_slug:
        by_slug["prison-island"]["hero"] = "prison-island.jpg"
        by_slug["prison-island"]["gallery"] = [
            "prison-island-alt.jpg",
            "external/tt/chumbe-island-Zanzibar_Chumbe_Island_03.jpg",
        ]


def assign_zanzibar_circuit(core: dict) -> None:
    core["circuits"][OCEAN_ISLANDS_CIRCUIT] = [
        "Oceanic Islands brings together Indian Ocean marine reserves, sandbars and conservation areas along the Swahili coast - from boat day trips off Dar es Salaam to Chumbe and Mnemba.",
        "Snorkel coral gardens, picnic on uninhabited sandbars and explore protected reefs where sea turtles, reef fish and dolphins thrive along the Swahili coast.",
    ]
    core["circuits"][MAFIA_CIRCUIT] = [
        "Tanzania's best-kept marine secret - whale sharks, world-class diving, Chole Bay and the Mafia archipelago, reached by light aircraft from Dar es Salaam or Zanzibar.",
    ]
    if "Coastal & Islands" in core["circuits"]:
        del core["circuits"]["Coastal & Islands"]

    core["circuits"]["Eastern Circuit"] = [
        "Rainforest hiking, bush-beach safaris and Swahili history - Saadani, Usambara, Bagamoyo and the Tanga coast.",
    ]

    for d in core["destinations"]:
        if d["slug"] in MAFIA_SLUGS:
            d["circuit"] = MAFIA_CIRCUIT
        elif d["slug"] in OCEAN_CIRCUIT_SLUGS:
            d["circuit"] = OCEAN_ISLANDS_CIRCUIT
        elif d["circuit"] == "Coastal & Islands":
            d["circuit"] = OCEAN_ISLANDS_CIRCUIT


def main():
    import importlib.util

    core = json.loads(CORE.read_text(encoding="utf-8"))
    by_slug = {d["slug"]: d for d in core["destinations"]}
    pool = collect_images()
    used: set[str] = set()
    updated = 0

    assign_zanzibar_circuit(core)
    fix_corrupt_entries(by_slug)

    spec_exp = importlib.util.spec_from_file_location("exp", ROOT / "scripts" / "expand-tanzania-core.py")
    exp = importlib.util.module_from_spec(spec_exp)
    spec_exp.loader.exec_module(exp)
    spec_sc = importlib.util.spec_from_file_location("sc", ROOT / "scripts" / "scrape-tourism-content.py")
    sc = importlib.util.module_from_spec(spec_sc)
    spec_sc.loader.exec_module(sc)

    if "mkomazi" in by_slug:
        raw = sc.scrape_one("mkomazi", "mkomazi-national-park", "Northern Circuit")
        if raw and raw.get("hero", "").startswith("http"):
            by_slug["mkomazi"]["hero"] = exp.download_tt_hero(raw["hero"], "mkomazi")

    skip_auto = {"pemba", "prison-island"}
    manual = {
        "isimila": (
            "Isimila-Stone-Age-Site-and-Natural-Pillars-in-Iringa.jpg",
            ["external/tt/igelegke-rock-art-Igeleke_Rock_Paintings_Iringa_17.jpg"],
        ),
        "gangilonga": (
            "Gangilonga_Rock_Iringa_3.jpg",
            ["Isimila-Stone-Age-Site-and-Natural-Pillars-in-Iringa.jpg"],
        ),
        "zanzibar": ("zanzibar.jpg", ["Zanzibar_Island_Stone_Town_01.jpg", "zanzibar2.jpg"]),
        "pemba": ("pemba-island.jpg", ["zanzibar.jpg", "Zanzibar_Island_Stone_Town_01.jpg"]),
        "prison-island": (
            "prison-island.jpg",
            ["prison-island-alt.jpg", "external/tt/chumbe-island-Zanzibar_Chumbe_Island_03.jpg"],
        ),
        "kilwa": (
            "external/tt/kilwa-g0-Kilwa_Kivinje_Beach_25.jpg",
            ["external/tt/kilwa-g1-Fishing_Harbour_01_Makubuli_Kilwa_Masoko.jpg"],
        ),
        "kilwa-kisiwani": (
            "external/tt/kilwa-kisiwani-Husuni_Kubwa_Sultans_Palace_14th__Century_04_Kilwa_Kisiwani.jpg",
            ["external/tt/kilwa-kisiwani-g1-Old_Fort_Gereza_12_Kilwa_Kisiwani.jpg"],
        ),
        "kilwa-kivinje": (
            "external/tt/kilwa-kivinje-Kilwa_Kivinje_Ruins_31.jpg",
            ["external/tt/kilwa-kivinje-g1-Fishing_Boats_in_Kilwa_Kivinje.jpg"],
        ),
        "songo-mnara": (
            "external/tt/songo-mnara-The_Palace_Ruins_02_Songo_Mnara_Kilwa.jpg",
            ["external/tt/songo-mnara-g1-Large_House_Ruins_01_Songo_Mnara_Kilwa.jpg"],
        ),
    }
    for slug, (hero, gallery) in manual.items():
        if slug in by_slug:
            by_slug[slug]["hero"] = hero
            by_slug[slug]["gallery"] = gallery
            used.add(hero)
            for g in gallery:
                used.add(g)
            skip_auto.add(slug)

    if "katavi" in by_slug:
        raw = sc.scrape_one("katavi", "katavi-national-park", "Western Circuit")
        if raw and raw.get("hero", "").startswith("http"):
            by_slug["katavi"]["hero"] = exp.download_tt_hero(raw["hero"], "katavi")
    for d in core["destinations"]:
        if d["slug"] in skip_auto:
            used.add(d["hero"])
            for g in d.get("gallery", []):
                used.add(g)
            continue
        hero, gallery = pick_images(d["slug"], d["name"], pool, used)
        if hero:
            if d.get("hero") != hero:
                updated += 1
            d["hero"] = hero
        d["gallery"] = gallery

    CORE.write_text(json.dumps(core, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Matched images for {len(core['destinations'])} destinations ({updated} heroes updated)")

    if PKG.exists():
        pkg_data = json.loads(PKG.read_text(encoding="utf-8"))
        for p in pkg_data.get("packages", []):
            if p.get("circuit") in ("Coastal & Islands", "Zanzibar & Islands", OCEAN_ISLANDS_CIRCUIT):
                p["circuit"] = OCEAN_ISLANDS_CIRCUIT
        PKG.write_text(json.dumps(pkg_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Updated safari-packages.json circuit labels")


if __name__ == "__main__":
    main()
