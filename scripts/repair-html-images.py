#!/usr/bin/env python3
"""Repair malformed image markup and destination asset paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def repair_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    fixed = text.replace("<imgdecoding=", "<img decoding=")
    fixed = fixed.replace("<imgsizes=", "<img sizes=")

    if "destinations" in path.parts:
        fixed = fixed.replace(", assets/images/opt/", ", ../assets/images/opt/")
        fixed = fixed.replace('srcset="assets/images/opt/', 'srcset="../assets/images/opt/')

    if path.name == "index.html":
        fixed = fixed.replace(
            '<link rel="stylesheet" href="css/destination-page.css">',
            "",
        )

    if "destinations" in path.parts and "performance.css" not in fixed:
        fixed = fixed.replace(
            '<link rel="stylesheet" href="../css/destination-page.css">',
            '<link rel="stylesheet" href="../css/destination-page.css">\n'
            '  <link rel="stylesheet" href="../css/performance.css">',
        )

    if fixed != text:
        path.write_text(fixed, encoding="utf-8")
        return True
    return False


def main() -> None:
    targets = [ROOT / "index.html"]
    targets.extend((ROOT / "destinations").glob("*.html"))
    changed = 0
    for path in targets:
        if path.exists() and repair_file(path):
            print(f"Repaired {path.relative_to(ROOT)}")
            changed += 1
    print(f"Repaired {changed} files.")


if __name__ == "__main__":
    main()
