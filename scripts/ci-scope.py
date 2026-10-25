#!/usr/bin/env python3
"""Select CI checks from changed paths; unknown inputs keep all checks enabled."""
import json
import os
from pathlib import Path
import re
import subprocess

COMPONENTS = ('tv', 'installer', 'android', 'setup', 'preview')


def components(paths):
    selected = set()
    for path in paths:
        if (path.startswith(('docs/', '.github/ISSUE_TEMPLATE/', '.github/PULL_REQUEST_TEMPLATE/'))
                or path.lower().endswith(('.md', '.rst'))
                or path == 'LICENSE'):
            continue
        if path.startswith('cytv/'):
            selected.add('installer')
            if Path(path).name not in ('desktop.py', 'desktop_entry.py', 'gui_style.py', 'build-requirements.txt'):
                selected.update(('android', 'setup'))
        elif path.startswith(('launcher/', 'root-edition/', 'native/', 'renewal-service/', 'updater-app/', 'updater-service/')):
            selected.update(('tv', 'installer', 'setup'))
            if path.startswith(('launcher/', 'root-edition/ui/', 'updater-app/')) or path == 'root-edition/preview.py':
                selected.add('preview')
        elif path.startswith(('android/',)):
            selected.add('android')
        elif path.startswith('tests/cytv/'):
            selected.add('installer')
        elif path.startswith('tests/setup/'):
            selected.add('setup')
        elif path.startswith('preview/') or path in ('scripts/preview.py', 'tests/test_preview.py', 'tests/preview-bridge.cjs'):
            selected.add('preview')
        elif path.startswith('tests/updates/'):
            selected.update(('tv', 'setup'))
        elif path.startswith('tests/'):
            selected.add('tv')
        else:
            selected.update(COMPONENTS)
    return selected


def is_candidate(plan, version, previous):
    def number(value):
        return tuple(map(int, value.split('.'))) if re.fullmatch(r'\d{1,4}\.\d{1,4}\.\d{1,4}', value or '') else ()
    acceptance = plan.get('acceptance')
    return bool(number(version) and number(previous) and plan.get('version') == version
                and isinstance(acceptance, str) and acceptance.strip() and number(version) > number(previous))


def git(*args):
    return subprocess.check_output(['git', *args])


def main():
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    kind = os.environ['GITHUB_EVENT_NAME']
    if kind == 'pull_request':
        pr = event['pull_request']
        diff = (pr['base']['sha'] + '...' + pr['head']['sha'],)
    elif kind == 'push' and event.get('before', '').strip('0'):
        diff = (event['before'], event['after'])
    else:
        diff = None
    selected = components(git('diff', '--name-only', '--no-renames', '-z', *diff).decode().split('\0')[:-1]) if diff and os.environ.get('CI_FULL_SUITE') != 'true' else set(COMPONENTS)
    candidate = False
    if (kind in ('push', 'workflow_dispatch')
            and os.environ.get('GITHUB_REF') == 'refs/heads/release/next'):
        plan = json.loads(Path('release-plan.json').read_text())
        version = json.loads(Path('release-versions.json').read_text())['release']
        previous = json.loads(git('show', 'origin/main:release-versions.json'))['release']
        candidate = is_candidate(plan, version, previous) and Path('docs/RELEASE-' + version + '.md').is_file()
    outputs = {name: name in selected for name in COMPONENTS}
    outputs.update(any=bool(selected), candidate=candidate)
    lines = ''.join(f'{name}={str(value).lower()}\n' for name, value in outputs.items())
    print(lines, end='')
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        output.write(lines)


if __name__ == '__main__':
    main()
