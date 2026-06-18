#!/usr/bin/env python3
"""Sync Circuits dropdown in index.html and about.html only."""
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("pt", ROOT / "scripts" / "page-templates.py")
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)

PATCH_TARGETS = {
    "index.html": {
        "circuits_href": "#destinations",
        "circuits_extra": ' <i class="fa-solid fa-chevron-down navbar__dropdown-icon" aria-hidden="true"></i>',
        "circuits_attrs": ' class="navbar__link" data-nav="destinations"',
        "dropdown_class": "navbar__dropdown",
        "circuit_p": "circuits/",
        "dest_p": "destinations/",
        "kenya": "kenya.html",
        "uganda": "uganda.html",
        "rwanda": "rwanda.html",
        "about_href": "about.html",
        "mobile": True,
    },
    "about.html": {
        "circuits_href": "index.html#destinations",
        "circuits_extra": "",
        "circuits_attrs": ' class="navbar__link active"',
        "dropdown_class": "navbar__dropdown",
        "circuit_p": "circuits/",
        "dest_p": "destinations/",
        "kenya": "kenya.html",
        "uganda": "uganda.html",
        "rwanda": "rwanda.html",
        "about_href": "about.html",
        "mobile": True,
    },
}


def build_circuits_li(cfg: dict) -> str:
    nav = pt.build_circuit_nav(
        cfg["circuit_p"], cfg["dest_p"], cfg["kenya"], cfg["uganda"], cfg["rwanda"], mobile=False
    )
    return (
        f'          <li class="navbar__item navbar__item--has-dropdown">\n'
        f'            <a href="{cfg["circuits_href"]}"{cfg["circuits_attrs"]}>Circuits{cfg["circuits_extra"]}</a>\n'
        f'            <ul class="{cfg["dropdown_class"]}" role="menu">\n'
        f"{nav}\n"
        f"            </ul>\n"
        f"          </li>"
    )


def build_mobile_circuits(cfg: dict) -> str:
    return pt.build_circuit_nav(
        cfg["circuit_p"], cfg["dest_p"], cfg["kenya"], cfg["uganda"], cfg["rwanda"], mobile=True
    )


def patch_file(name: str, cfg: dict) -> bool:
    path = ROOT / name
    html = path.read_text(encoding="utf-8")
    original = html
    circuits_li = build_circuits_li(cfg)
    html = re.sub(
        r"<li class=\"navbar__item navbar__item--has-dropdown\">\s*"
        r"<a href=\"[^\"]*\"[^>]*>Circuits[\s\S]*?</a>\s*"
        r"<ul class=\"navbar__dropdown[^\"]*\" role=\"menu\">[\s\S]*</ul>\s*</li>"
        rf"(?=\s*<li><a href=\"{re.escape(cfg['about_href'])}\")",
        circuits_li,
        html,
        count=1,
        flags=re.S,
    )
    if cfg["mobile"]:
        mobile_nav = build_mobile_circuits(cfg)
        html = re.sub(
            r"(<ul class=\"mobile-menu__dest-grid\">).*</ul>"
            r"(?=\s*</div>\s*</li>\s*<li><a href=\"[^\"]*about\.html\")",
            rf"\1\n{mobile_nav}\n              </ul>",
            html,
            count=1,
            flags=re.S,
        )
    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main():
    changed = 0
    for name, cfg in PATCH_TARGETS.items():
        if patch_file(name, cfg):
            print(f"Updated {name} circuit navigation.")
            changed += 1
    print(f"Done. {changed} files updated." if changed else "No changes needed.")


if __name__ == "__main__":
    main()
