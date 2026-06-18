"""Ensure + icon sits after Circuits/Safaris label in mobile menu triggers."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

CIRCUITS_BLOCK = re.compile(
    r'(<button type="button" class="mobile-menu__link mobile-menu__dest-trigger" '
    r'aria-expanded="false" aria-controls="mobileDestPanel">\s*\n\s*)'
    r'(?:<span class="mobile-menu__dest-plus" aria-hidden="true">\+</span>\s*\n\s*)?'
    r'<span>Circuits</span>\s*\n'
    r'(?:\s*<span class="mobile-menu__dest-plus" aria-hidden="true">\+</span>\s*\n)*',
    re.MULTILINE,
)
SAFARIS_BLOCK = re.compile(
    r'(<button type="button" class="mobile-menu__link mobile-menu__dest-trigger" '
    r'aria-expanded="false" aria-controls="mobileSafariPanel">\s*\n\s*)'
    r'(?:<span class="mobile-menu__dest-plus" aria-hidden="true">\+</span>\s*\n\s*)?'
    r'<span>Safaris</span>\s*\n'
    r'(?:\s*<span class="mobile-menu__dest-plus" aria-hidden="true">\+</span>\s*\n)*',
    re.MULTILINE,
)
CIRCUITS_REPLACEMENT = (
    r'\1<span>Circuits</span>\n'
    r'              <span class="mobile-menu__dest-plus" aria-hidden="true">+</span>\n'
)
SAFARIS_REPLACEMENT = (
    r'\1<span>Safaris</span>\n'
    r'              <span class="mobile-menu__dest-plus" aria-hidden="true">+</span>\n'
)


def main():
    count = 0
    for path in ROOT.rglob('*.html'):
        if 'scripts' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        new = CIRCUITS_BLOCK.sub(CIRCUITS_REPLACEMENT, text)
        new = SAFARIS_BLOCK.sub(SAFARIS_REPLACEMENT, new)
        if new != text:
            path.write_text(new, encoding='utf-8')
            count += 1
    print(f'Updated {count} HTML files')


if __name__ == '__main__':
    main()
