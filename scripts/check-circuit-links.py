"""Check circuit card and mobile nav links resolve to existing files."""
import pathlib
import re
from urllib.parse import urljoin

ROOT = pathlib.Path(__file__).resolve().parent.parent

def resolve(page: pathlib.Path, href: str) -> pathlib.Path:
    if href.startswith(('#', 'http://', 'https://', 'mailto:', 'tel:')):
        return None
    base = page.parent.as_uri() + '/'
    joined = urljoin(base, href)
    path = pathlib.Path(joined.replace('file:///', '').replace('file://', ''))
    try:
        return path.resolve()
    except OSError:
        return None

issues = []
for page in sorted(ROOT.glob('circuits/*.html')):
    text = page.read_text(encoding='utf-8')
    for href in re.findall(r'href="([^"]+)"[^>]*class="circuit-dest-card__link"', text):
        target = resolve(page, href)
        if target and not target.exists():
            issues.append((str(page.relative_to(ROOT)), href))

    for href in re.findall(r'href="([^"]+)"[^>]*class="mobile-menu__dest-grid[^"]*"', text):
        pass
    for href in re.findall(r'mobile-menu__dest-grid[\s\S]*?href="([^"]+)"', text):
        target = resolve(page, href)
        if target and not target.exists():
            issues.append((str(page.relative_to(ROOT)), f'mobile:{href}'))

print(f'Broken links: {len(issues)}')
for item in issues:
    print(' ', item[0], '->', item[1])
