"""Pin related repository metadata, complete tree and README without cloning large repos."""
import base64
import json
from pathlib import Path
import re
import subprocess

REPOSITORIES = [
    ('admisorios', 'SystemHope-ResAdmis'),
    ('requerimientos', 'elaboracion-de-resoluciones-de-requerimiento'),
    ('improcedencia_susalud', 'elaboracion-de-resoluciones-de-improcedencia-a-susalud'),
    ('apelaciones', 'elaboracion-de-r1-de-expedientes-de-apelaciones-en-la-cc1-de-indecopi'),
]

def api(endpoint):
    return json.loads(subprocess.check_output(['gh', 'api', endpoint], text=True, encoding='utf-8'))

SECRET = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
                    r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}|'
                    r'\bBearer\s+eyJ[A-Za-z0-9_-]{20,}\.|'
                    r'"refresh_token"\s*:\s*"[^"\s]{15,}"')

def assert_no_secret(text):
    if SECRET.search(text):
        raise ValueError('Possible credential found; manual private review required')

def main():
    if not api('repos/zero-phoenix/zeruel').get('private'):
        raise SystemExit('Zeruel must remain private')
    dest = Path(__file__).resolve().parents[1] / 'knowledge' / 'repositories'
    dest.mkdir(parents=True, exist_ok=True)
    summary = []
    for role, name in REPOSITORIES:
        repo = api('repos/zero-phoenix/' + name)
        branch = repo['default_branch']
        commit = api(f'repos/zero-phoenix/{name}/commits/{branch}')['sha']
        tree = api(f'repos/zero-phoenix/{name}/git/trees/{commit}?recursive=1')
        if tree.get('truncated'): raise ValueError('Incomplete remote tree; must not report complete inventory')
        record = {'role': role, 'repository': 'zero-phoenix/' + name, 'private': repo['private'],
                  'default_branch': branch, 'commit': commit, 'tree': tree['tree']}
        (dest / (role + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        readme = api(f'repos/zero-phoenix/{name}/readme?ref={commit}')
        text = base64.b64decode(readme['content']).decode('utf-8')
        assert_no_secret(text)
        (dest / (role + '-README.md')).write_text(text, encoding='utf-8')
        source_paths = [x['path'] for x in tree['tree'] if x['type'] == 'blob' and
                        x['path'].endswith(('.py', '.ps1', '.js', '.mjs', '.gs'))]
        summary.append({'role': role, 'repository': record['repository'], 'commit': commit,
                        'tree_entries': len(tree['tree']), 'code_files': source_paths,
                        'docx_files': sum(x['path'].lower().endswith('.docx') for x in tree['tree'])})
    (dest / 'index.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == '__main__': main()
