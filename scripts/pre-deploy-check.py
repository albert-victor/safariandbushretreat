#!/usr/bin/env python3
"""Pre-deploy quality gate for Cloudflare launch."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"scripts", "vendor", "node_modules", ".git", ".cursor"}
ATTR = re.compile(r'(?:href|src|srcset)="([^"]+)"')
SKIP_URL = ("http://", "https://", "//", "mailto:", "tel:", "javascript:", "data:", "#")
LONG_TITLE = 60


def load_audit():
    spec = importlib.util.spec_from_file_location("audit", ROOT / "scripts" / "audit-links.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def decode_broken(broken: list[tuple[str, str]]) -> list[tuple[str, str]]:
    real: list[tuple[str, str]] = []
    for page, ref in broken:
        decoded = unquote(ref)
        target = (ROOT / page).parent / decoded
        try:
            target = target.resolve()
        except OSError:
            real.append((page, ref))
            continue
        if not target.exists():
            real.append((page, ref))
    return real


def check_favicon() -> list[str]:
    issues = []
    for name in ("favicon.png", "apple-touch-icon.png"):
        if not (ROOT / "assets" / "images" / name).exists():
            issues.append(f"Missing assets/images/{name}")
    return issues


def check_titles() -> list[str]:
    long_titles = []
    for html in ROOT.rglob("*.html"):
        if any(p in SKIP for p in html.parts):
            continue
        m = re.search(r"<title>([^<]+)</title>", html.read_text(encoding="utf-8"), re.I)
        if m and len(m.group(1)) > LONG_TITLE:
            long_titles.append((str(html.relative_to(ROOT)), len(m.group(1)), m.group(1)))
    long_titles.sort(key=lambda x: -x[1])
    return [
        f"{page}: {length} chars — {title[:70]}{'…' if len(title) > 70 else ''}"
        for page, length, title in long_titles[:8]
    ]


def check_gtm() -> list[str]:
    cfg = json.loads((ROOT / "data" / "site-config.json").read_text(encoding="utf-8"))
    gtm = (cfg.get("gtmContainerId") or "").strip()
    if not gtm or gtm == "GTM-XXXXXXX":
        return ["GTM container ID is still placeholder (GTM-XXXXXXX) — set real ID before launch"]
    return []


def main() -> int:
    print("=== Safari & Bush Retreats — Pre-deploy check ===\n")
    failures = 0

    subprocess.run([sys.executable, str(ROOT / "scripts" / "setup-deploy-assets.py")], check=True, cwd=ROOT)

    audit = load_audit()
    broken_all: list[tuple[str, str]] = []
    suspicious_all: list[tuple[str, str]] = []
    for ext in ("*.html", "*.js"):
        for f in ROOT.rglob(ext):
            if any(part in SKIP for part in f.parts):
                continue
            b, s = audit.audit_file(f)
            broken_all.extend(b)
            suspicious_all.extend(s)

    broken = decode_broken(broken_all)
    nav_broken = [x for x in broken if "categories/../" in x[1] or x[1].startswith("/circuits/")]
    img_broken = [x for x in broken if x not in nav_broken and not x[1].startswith("${")]

    print(f"Broken links (decoded): {len(broken)}")
    if nav_broken:
        print(f"  Nav/path issues: {len(nav_broken)}")
        for page, ref in nav_broken[:5]:
            print(f"    {page} -> {ref}")
    if img_broken:
        failures += 1
        print(f"  Missing images/assets: {len(img_broken)}")
        for page, ref in img_broken[:12]:
            print(f"    {page} -> {ref}")
    else:
        print("  Missing images: none")

    fav = check_favicon()
    if fav:
        failures += 1
        for item in fav:
            print(f"Favicon: {item}")
    else:
        print("Favicon: OK (favicon.png + apple-touch-icon.png)")

    gtm = check_gtm()
    for item in gtm:
        print(f"GTM: {item}")

    long_t = check_titles()
    print(f"\nLong titles (>{LONG_TITLE} chars): {len(long_t)} pages (informational)")
    for line in long_t[:5]:
        print(f"  {line}")

    suspicious_nav = [s for s in suspicious_all if "categories/../" in s[1] or "double-prefix" in s[1]]
    print(f"\nSuspicious nav patterns: {len(suspicious_nav)}")

    print("\n=== Summary ===")
    if failures:
        print(f"BLOCKERS: {failures} issue group(s) — fix before deploy")
        return 1
    print("Ready for Cloudflare deploy (fix GTM ID if still placeholder).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
