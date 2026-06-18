#!/usr/bin/env python3
"""Inject Google Tag Manager snippets into all public HTML pages."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "site-config.json"
SKIP_DIRS = {"scripts", "vendor", "node_modules", "data", ".git", ".cursor"}

HEAD_START = "<!-- Google Tag Manager -->"
HEAD_END = "<!-- End Google Tag Manager -->"
BODY_START = "<!-- Google Tag Manager (noscript) -->"
BODY_END = "<!-- End Google Tag Manager (noscript) -->"

HEAD_RE = re.compile(
    rf"{re.escape(HEAD_START)}[\s\S]*?{re.escape(HEAD_END)}",
    re.IGNORECASE,
)
BODY_RE = re.compile(
    rf"{re.escape(BODY_START)}[\s\S]*?{re.escape(BODY_END)}",
    re.IGNORECASE,
)
CHARSET_RE = re.compile(r'<meta charset="UTF-8">', re.IGNORECASE)
BODY_TAG_RE = re.compile(r"<body[^>]*>", re.IGNORECASE)


def load_gtm_id() -> str:
    if not CONFIG.exists():
        raise SystemExit(f"Missing {CONFIG}")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    gtm_id = (cfg.get("gtmContainerId") or "").strip()
    if not gtm_id:
        raise SystemExit("Set gtmContainerId in data/site-config.json")
    return gtm_id


def gtm_head(gtm_id: str) -> str:
    return f"""  {HEAD_START}
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','{gtm_id}');</script>
  {HEAD_END}"""


def gtm_body(gtm_id: str) -> str:
    return f"""  {BODY_START}
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id}"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  {BODY_END}"""


def patch_html(html: str, gtm_id: str) -> tuple[str, bool]:
    changed = False
    head_snip = gtm_head(gtm_id)
    body_snip = gtm_body(gtm_id)

    if HEAD_RE.search(html):
        new_head = HEAD_RE.sub(head_snip, html, count=1)
        if new_head != html:
            html = new_head
            changed = True
    elif CHARSET_RE.search(html):
        html = CHARSET_RE.sub(lambda m: f"{m.group(0)}\n{head_snip}", html, count=1)
        changed = True
    else:
        return html, False

    if BODY_RE.search(html):
        new_body = BODY_RE.sub(body_snip, html, count=1)
        if new_body != html:
            html = new_body
            changed = True
    else:
        match = BODY_TAG_RE.search(html)
        if not match:
            return html, changed
        insert_at = match.end()
        html = html[:insert_at] + "\n" + body_snip + html[insert_at:]
        changed = True

    return html, changed


def iter_html_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def main() -> None:
    gtm_id = load_gtm_id()
    if gtm_id == "GTM-XXXXXXX":
        print("WARNING: Replace GTM-XXXXXXX in data/site-config.json with your real container ID.")

    updated = 0
    for path in iter_html_files():
        html = path.read_text(encoding="utf-8")
        new_html, changed = patch_html(html, gtm_id)
        if changed:
            path.write_text(new_html, encoding="utf-8")
            print(f"Updated {path.relative_to(ROOT)}")
            updated += 1

    print(f"\nGTM ({gtm_id}) applied to {updated} HTML files.")


if __name__ == "__main__":
    main()
