"""Check local Markdown links, table shape and canonical requirement IDs."""
import re
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'!?\[[^\]]*\]\(([^\n)]+)\)')


def markdown_files():
    paths = [ROOT / name for name in ('README.md', 'CONTRIBUTING.md', 'CHANGELOG.md')]
    paths += list((ROOT / 'docs').rglob('*.md'))
    paths += list((ROOT / 'review').glob('*.md'))
    paths += list((ROOT / 'templates').glob('*.md'))
    paths += list((ROOT / 'examples').rglob('README.md'))
    paths += [ROOT / 'sources/README.md', ROOT / 'reports/README.md']
    return sorted(set(path for path in paths if path.exists()))


def main():
    errors, count = [], 0
    for path in markdown_files():
        content = path.read_text(encoding='utf-8')
        # Code examples may contain illustrative paths, not navigation links.
        prose = re.sub(r'```.*?```', '', content, flags=re.S)
        for match in LINK.finditer(prose):
            value = match.group(1).split(' "')[0].strip('<>')
            parsed = urlsplit(value)
            if parsed.scheme or value.startswith('#'):
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            count += 1
            if not target.exists():
                errors.append(f'{path.relative_to(ROOT)}: missing {value}')
        if '\ufffd' in content:
            errors.append(f'{path.relative_to(ROOT)}: replacement character')
    srs = (ROOT / 'docs/requirements/srs.md').read_text(encoding='utf-8')
    for prefix, maximum in [('FR', 15), ('NFR', 5)]:
        for number in range(1, maximum + 1):
            if f'{prefix}-{number:02}' not in srs:
                errors.append(f'SRS missing {prefix}-{number:02}')
    for number in range(1, 7):
        if not (ROOT / f'docs/semesters/week-{number:02}.md').exists():
            errors.append(f'Missing semester {number}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'{len(markdown_files())} Markdown files; {count} local links OK; 15 FR + 5 NFR present.')


if __name__ == '__main__':
    main()
