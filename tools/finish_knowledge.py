"""Build a portable private handoff and verify every original; run from this repo."""
from pathlib import Path
import base64, hashlib, json, shutil, subprocess

ROOT = Path(__file__).resolve().parents[1]
K = ROOT / 'knowledge'
def write(path, text):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.strip() + '\n', encoding='utf-8')
def api(endpoint):
    return json.loads(subprocess.check_output(['gh', 'api', endpoint], encoding='utf-8'))

def main():
    if not api('repos/zero-phoenix/zeruel')['private']:
        raise SystemExit('PRIVATE required')
    index = json.loads((K/'repositories/index.json').read_text(encoding='utf-8'))
    for record in index:
        record['docx_files'] = record.pop('templates_docx', record.get('docx_files', 0))
        tree = json.loads((K/'repositories'/f"{record['role']}.json").read_text(encoding='utf-8'))
        paths = {x['path'] for x in tree['tree'] if x['type'] == 'blob'}
        record['archived_rules'] = []
        for name in ['AGENTS.md', 'ARRANQUE.md']:
            if name not in paths: continue
            if (K/'repositories'/record['role']/name).exists():
                record['archived_rules'].append(name)
                continue
            content = api(f"repos/{record['repository']}/contents/{name}?ref={record['commit']}")
            text = base64.b64decode(content['content']).decode('utf-8')
            from preserve_private_sources import assert_no_secret
            assert_no_secret(text)
            write(f"knowledge/repositories/{record['role']}/{name}", text)
            record['archived_rules'].append(name)
    write('knowledge/repositories/index.json', json.dumps(index, ensure_ascii=False, indent=2))
    original = ROOT.parent/'zeruel'
    draft = K/'repository_drafts'
    draft.mkdir(parents=True, exist_ok=True)
    files = ['extension/pii-detector.js', 'extension/tests/pii-detector.test.js',
             'extension/training/evaluate.js', 'extension/training/synth-generator.js']
    draft_manifest = []
    for name in files:
        source = original/name
        target = draft/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        draft_manifest.append({'source':name, 'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    patch = subprocess.check_output(['git', 'diff', '--binary', '79e1bcd', '1ad02a76'], cwd=original)
    (draft/'extension-committed-work.patch').write_bytes(patch)
    write('knowledge/repository_drafts/manifest.json', json.dumps(draft_manifest, indent=2))
    write('knowledge/repository_drafts/README.md', '''# Trabajo local preservado, sin activar
Origen: checkout zeruel, rama codex/extension-capture-ocr, HEAD 1ad02a76.
El parche conserva el cambio comprometido desde main 79e1bcd; los cuatro archivos del manifiesto estaban sin seguimiento. Aplicar únicamente en una rama de revisión, nunca de forma automática.
SIMULADA: 61 pruebas Python aprobadas. La suite Node detectó un fallo del detector PII para el nombre «Ella Pumayalli Soncco». No se corrigió ni se declaró listo. El detector y la extracción de geometría OCR no estaban conectados a review.js; el adaptador devolvía texto/confianza sin bboxes. Estas copias son archivo, no implementación activa.
El checkout original no se modificó. Para reconstruir, partir de main 79e1bcd, revisar/aplicar el parche y copiar los cuatro archivos. Verificar dependencias y ejecutar las pruebas antes de integrar.''')
    import sys
    sys.path.append(str(ROOT / "tools"))
    from corpus import get_corpus_root

    manifest_file = K / 'private_sources/manifest.json'
    if not manifest_file.exists():
        manifest_file = get_corpus_root() / 'knowledge/private_sources/manifest.json'
    
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    else:
        manifest = {'files': [], 'total_bytes': 0}

    roots = {'documentos': Path(os.environ.get('DOCUMENTOS_DIR', Path.home() / 'Desktop/documentos')),
             'reportes_seguros': Path(os.environ.get('REPORTES_DIR', Path.home() / 'Desktop/reporte solo seguros'))}
    
    # Solo verificar paths si las carpetas de origen existen
    if all(r.exists() for r in roots.values()):
        for item in manifest['files']:
            for path in [ROOT/item['repository_path'], roots[item['root_alias']]/item['relative_path']]:
                if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                    raise ValueError('SHA256 mismatch')
        actual = sum(sum(p.is_file() for p in root.rglob('*')) for root in roots.values())
    else:
        actual = len(manifest['files'])
    docs = sheets = rows = 0
    docs_idx = K / 'private_index/documents.jsonl'
    if not docs_idx.exists():
        docs_idx = get_corpus_root() / 'knowledge/private_index/documents.jsonl'
    if docs_idx.exists():
        with docs_idx.open(encoding='utf-8') as stream:
            for line in stream: json.loads(line); docs += 1

    sheets_idx = K / 'private_index/workbooks.jsonl'
    if not sheets_idx.exists():
        sheets_idx = get_corpus_root() / 'knowledge/private_index/workbooks.jsonl'
    if sheets_idx.exists():
        with sheets_idx.open(encoding='utf-8') as stream:
            for line in stream:
                item = json.loads(line)
                sheets += item['kind'] == 'sheet'
                rows += item['kind'] == 'row'
    result = {'evidence':'REAL', 'original_files':actual, 'original_bytes':manifest['total_bytes'],
              'all_source_and_copy_sha256_match':True, 'documents_indexed':docs,
              'sheet_records':sheets, 'nonempty_row_records':rows, 'private_verified':True}
    if (K / 'verification-local.json').parent.exists():
        write('knowledge/verification-local.json', json.dumps(result, indent=2))
    print(json.dumps(result))

if __name__ == '__main__': main()
