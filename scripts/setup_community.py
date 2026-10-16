"""Check/provision public game issue boards. Default is read-only; --apply enables setup."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    'site-guestbook': dict(color='C98A61', description='작은 게임방 담벼락에 남긴 게임별 방명록'),
    'site-bug': dict(color='4B705D', description='작은 게임방 칠판에 적은 게임별 버그 신고'),
}
TEMPLATES = ['site-guestbook.md', 'site-bug-report.md']


def api(path, method='GET', data=None, missing=False):
    cmd = ['gh', 'api', path, '--method', method]
    if data is not None:
        cmd += ['--input', '-']
    result = subprocess.run(cmd, input=json.dumps(data, ensure_ascii=False) if data is not None else None,
                            text=True, encoding='utf-8', capture_output=True)
    if result.returncode:
        if missing and '404' in result.stderr:
            return None
        raise RuntimeError(f'{method} {path}: {result.stderr.strip()}')
    if method != 'GET':
        time.sleep(.8)  # Keep content-generating requests below secondary API limits.
    return json.loads(result.stdout) if result.stdout.strip() else None


def inspect_repo(game):
    slug = game['id']
    if not re.fullmatch(r'[a-z0-9-]+', slug) or game.get('repository') != 'https://github.com/akuma815/' + slug:
        raise ValueError('Only catalogued public akuma815 game repositories are supported')
    path = 'repos/akuma815/' + slug
    repo = api(path)
    if repo['private'] or repo['archived']:
        raise ValueError('Repository must be public and writable: ' + slug)
    labels = {row['name'] for row in api(path + '/labels?per_page=100')}
    branch = repo['default_branch']
    ref = api(path + '/git/ref/heads/' + branch)
    commit = api(path + '/git/commits/' + ref['object']['sha'])
    tree = api(path + '/git/trees/' + commit['tree']['sha'] + '?recursive=1')
    if tree.get('truncated'):
        raise ValueError('Incomplete repository tree: ' + slug)
    blobs = {row['path']: row['sha'] for row in tree['tree']}
    changes = []
    for name in TEMPLATES:
        content = (ROOT / 'community-templates' / name).read_text(encoding='utf-8')
        raw = content.encode('utf-8')
        expected = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        target = '.github/ISSUE_TEMPLATE/' + name
        current = blobs.get(target)
        if current and current != expected:
            import base64
            existing = api(path + '/git/blobs/' + current)
            if b'managed-by:akuma815-site-community' not in base64.b64decode(existing['content']):
                raise ValueError('Refusing to replace an unmanaged template: ' + slug + '/' + name)
        if current != expected:
            changes.append(dict(path=target, mode='100644', type='blob', content=content))
    return dict(game=slug, path=path, issues_enabled=repo['has_issues'], missing_labels=sorted(set(LABELS) - labels),
                branch=branch, parent=ref['object']['sha'], base_tree=commit['tree']['sha'], changes=changes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    games = [g for g in json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))['games'] if g['available']]
    with ThreadPoolExecutor(max_workers=4) as pool:
        plans = list(pool.map(inspect_repo, games))
    results = []
    output = ROOT / 'qa/community'
    output.mkdir(parents=True, exist_ok=True)
    for plan in plans:
        path = plan['path']
        row = dict(game=plan['game'], issues_enabled=plan['issues_enabled'], missing_labels=plan['missing_labels'],
                   changed_templates=[r['path'] for r in plan['changes']], applied=False)
        if args.apply:
            if not plan['issues_enabled']:
                api(path, 'PATCH', {'has_issues': True})
            for label in plan['missing_labels']:
                api(path + '/labels', 'POST', dict(name=label, **LABELS[label]))
            if plan['changes']:
                # The base tree and non-forced ref update preserve every other file.
                tree = api(path + '/git/trees', 'POST', dict(base_tree=plan['base_tree'], tree=plan['changes']))
                commit = api(path + '/git/commits', 'POST', dict(message='Add website guestbook and bug report templates', tree=tree['sha'], parents=[plan['parent']]))
                api(path + '/git/refs/heads/' + plan['branch'], 'PATCH', dict(sha=commit['sha'], force=False))
                row['commit'] = commit['sha']
            row.update(applied=True, issues_enabled=True, missing_labels=[])
        results.append(row)
        (output / ('setup_applied.json' if args.apply else 'setup_check.json')).write_text(json.dumps(results, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
