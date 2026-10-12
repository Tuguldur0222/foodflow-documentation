"""Generate a Sphinx catalog of supporting documents without duplicating content."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
index = (ROOT / 'docs/index.md').read_text(encoding='utf-8')
included = set()
for line in re.search(r'```\{toctree\}(.*?)```', index, re.S).group(1).splitlines():
    line = line.strip()
    if line and not line.startswith(':'):
        included.add('docs/' + line)
paths = list((ROOT / 'docs').rglob('*.md'))
paths += list((ROOT / 'review').glob('*.md'))
paths += list((ROOT / 'examples').rglob('README.md'))
paths += list((ROOT / 'templates').glob('*.md'))
paths += list((ROOT / 'sources').glob('*.md'))
extras = []
for path in sorted(paths):
    relative = path.relative_to(ROOT).with_suffix('').as_posix()
    if relative not in included and relative != 'docs/index':
        extras.append('../../' + relative)
catalog = 'Дагалдах баримтууд\n==================\n\n'
catalog += '.. toctree::\n   :maxdepth: 1\n\n'
catalog += ''.join('   ' + path + '\n' for path in extras)
(ROOT / 'docs/project/catalog.rst').write_text(catalog, encoding='utf-8')
print(f'Catalog includes {len(extras)} supporting documents.')
