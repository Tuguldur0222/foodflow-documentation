"""Run local checks and retain exact logs and a machine-readable result."""
import json
from pathlib import Path
import platform
import subprocess
import sys
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import sphinx

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    ('unit_tests', ['-m', 'unittest', 'discover', '-s', 'tests', '-v']),
    ('python_doctest', ['-m', 'doctest', '-v', 'foodflow/order_service.py']),
    ('doc_coverage', ['tools/check_docs.py']),
    ('repository_links', ['tools/check_repository.py']),
    ('sphinx_doctest', ['-m', 'sphinx', '-c', 'docs', '-E', '-n', '-W', '--keep-going',
                        '-b', 'doctest', '.', 'build/doctest']),
    ('sphinx_html', ['-m', 'sphinx', '-c', 'docs', '-E', '-a', '-n', '-W', '--keep-going',
                     '-b', 'html', '.', 'public']),
]


def main():
    subprocess.run([sys.executable, 'tools/prepare_docs.py'], cwd=ROOT, check=True)
    result = dict(date=datetime.now(ZoneInfo('Asia/Ulaanbaatar')).isoformat(), timezone='Asia/Ulaanbaatar',
                  python=platform.python_version(), sphinx=sphinx.__version__,
                  scope='FoodFlow seminars 01–06 documentation and teaching examples', checks=[])
    for name, arguments in COMMANDS:
        command = [sys.executable, *arguments]
        environment = dict(os.environ, PYTHONIOENCODING='utf-8')
        process = subprocess.run(command, cwd=ROOT, capture_output=True,
                                 text=True, encoding='utf-8', errors='replace', env=environment)
        output = process.stdout + process.stderr
        content = '$ ' + ' '.join(command) + '\n' + output
        content += '\nEXIT CODE: ' + str(process.returncode) + '\n'
        log = 'review/' + name + '_log.txt'
        (ROOT / log).write_text(content, encoding='utf-8')
        result['checks'].append(dict(name=name, exit_code=process.returncode, log=log))
        print(name, 'exit=', process.returncode)
        print(output[-500:])
    (ROOT / 'review/verification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    raise SystemExit(any(item['exit_code'] for item in result['checks']))


if __name__ == '__main__':
    main()
