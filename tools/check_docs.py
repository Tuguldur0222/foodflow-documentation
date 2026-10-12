"""Check structured docs and pending inline debt in the reconstructed source."""
import inspect
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from foodflow import OrderService


def main():
    errors = []
    for name in ('__init__', 'place_order', 'get_order', 'cancel_order'):
        method = getattr(OrderService, name)
        text = inspect.getdoc(method) or ''
        sections = ('Args:', 'Returns:', 'Example:')
        if name != '__init__':
            sections += ('Raises:',)
        for section in sections:
            if section not in text:
                errors.append(f'{name}: missing {section}')
        for parameter in inspect.signature(method).parameters:
            if parameter != 'self' and not re.search(r'\b' + parameter + ':', text):
                errors.append(f'{name}: undocumented parameter {parameter}')
    debt = []
    for folder in ('foodflow', 'tests'):
        for path in (ROOT / folder).glob('*.py'):
            for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
                if re.search(r'#\s*(?:TODO|FIXME)\b', line):
                    debt.append(f'{path.relative_to(ROOT)}:{number}')
    if errors or debt:
        raise SystemExit('\n'.join(errors + debt))
    print('4/4 public callables have structured docs and named parameters.')
    print('0 inline TODO/FIXME comments in foodflow/ and tests/.')


if __name__ == '__main__':
    main()
