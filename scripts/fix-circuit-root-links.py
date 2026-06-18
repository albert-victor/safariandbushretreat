"""Fix circuit page links that break under clean URLs (/circuits without trailing slash)."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CIRCUITS = ROOT / 'circuits'

BACK_OLD = re.compile(
    r'href="index\.html" class="dest-page__back"'
)
BACK_NEW = 'href="/circuits/index.html" class="dest-page__back"'

OVERVIEW_OLD = re.compile(
    r'(<a href="../index\.html#destinations" class="mobile-menu__dest-overview">)View all destinations(</a>)'
)
OVERVIEW_NEW = r'\1View all circuits\2'

# Fix overview href on circuit sub-pages
OVERVIEW_HREF_OLD = re.compile(
    r'href="../index\.html#destinations" class="mobile-menu__dest-overview">View all circuits'
)
OVERVIEW_HREF_NEW = 'href="/circuits/index.html" class="mobile-menu__dest-overview">View all circuits'

OVERVIEW_HREF_OLD2 = re.compile(
    r'href="../index\.html#destinations" class="mobile-menu__dest-overview">View all destinations'
)
OVERVIEW_HREF_NEW2 = 'href="/circuits/index.html" class="mobile-menu__dest-overview">View all circuits'


def main():
    count = 0
    for path in CIRCUITS.glob('*.html'):
        if path.name == 'index.html':
            continue
        text = path.read_text(encoding='utf-8')
        new = BACK_OLD.sub(BACK_NEW, text)
        new = OVERVIEW_OLD.sub(OVERVIEW_NEW, new)
        new = OVERVIEW_HREF_OLD.sub(OVERVIEW_HREF_NEW, new)
        new = OVERVIEW_HREF_OLD2.sub(OVERVIEW_HREF_NEW2, new)
        if new != text:
            path.write_text(new, encoding='utf-8')
            count += 1
            print('fixed', path.name)
    print(f'Done: {count} circuit pages')


if __name__ == '__main__':
    main()
