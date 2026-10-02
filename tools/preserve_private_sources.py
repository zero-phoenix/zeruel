"""Preserve every file and build readable indexes, only in a verified PRIVATE repo.

Original bytes are authoritative. Indexes aid retrieval and do not replace OOXML/PDF
formatting, signatures, comments, drawings or Excel cached calculation semantics.
Never prints filenames, identities, source contents or sensitive error strings.
"""
import argparse
from collections import Counter
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
SECRET = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
                    r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}|'
                    r'\bBearer\s+eyJ[A-Za-z0-9_-]{20,}\.|'
                    r'"refresh_token"\s*:\s*"[^"\s]{15,}"')

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def default(value):
    if isinstance(value, (datetime, date)): return {'type': 'date', 'iso': value.isoformat()}
    return str(value)

def write_line(stream, value):
    stream.write(json.dumps(value, ensure_ascii=False, default=default) + '\n')

def assert_no_secret(text):
    if SECRET.search(text): raise ValueError('Possible credential found; manual private review required')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--documents', type=Path, required=True)
    ap.add_argument('--reports', type=Path, required=True)
    ap.add_argument('--repository', type=Path, required=True, help="Directorio del repositorio acéfalo zeruel-corpus")
    ap.add_argument('--repo-name', type=str, default='zero-phoenix/zeruel-corpus', help="Nombre del repo en GitHub a verificar")
    args = ap.parse_args()
    visibility = json.loads(subprocess.check_output(['gh', 'repo', 'view', args.repo_name,
        '--json', 'isPrivate,visibility'], text=True))
    if not visibility.get('isPrivate') or visibility.get('visibility') != 'PRIVATE':
        raise SystemExit(f'Repository privacy for {args.repo_name} is not verified; nothing copied')
    repo = args.repository.resolve()
    archive = repo / 'knowledge' / 'private_sources'
    indexes = repo / 'knowledge' / 'private_index'
    archive.mkdir(parents=True, exist_ok=True); indexes.mkdir(parents=True, exist_ok=True)
    manifest, counts = [], Counter()
    with (indexes / 'documents.jsonl').open('w', encoding='utf-8') as docs, \
         (indexes / 'workbooks.jsonl').open('w', encoding='utf-8') as sheets:
        for label, root in [('documentos', args.documents), ('reportes_seguros', args.reports)]:
            root = root.resolve()
            for source in sorted(root.rglob('*')):
                if not source.is_file(): continue
                source.resolve().relative_to(root)  # reject an external symlink target
                relative = source.relative_to(root)
                target = archive / label / relative
                target.resolve().relative_to(archive.resolve())
                target.parent.mkdir(parents=True, exist_ok=True)
                source_hash = digest(source)
                suffix = source.suffix.lower()
                index_count = 0
                if suffix == '.docx':
                    with zipfile.ZipFile(source) as package:
                        parts = []
                        for name in package.namelist():
                            if (name == 'word/document.xml' or
                                re.match(r'word/(header|footer|footnotes|endnotes|comments).*\.xml$', name)):
                                xml = ET.fromstring(package.read(name))
                                paragraphs = []
                                for p in xml.iter(W+'p'):
                                    texts = []
                                    for child in p.iter():
                                        if child.tag == W+'t': texts.append(child.text or '')
                                        elif child.tag == W+'tab': texts.append('\t')
                                        elif child.tag == W+'br': texts.append('\n')
                                    content = ''.join(texts)
                                    assert_no_secret(content)
                                    ppr = p.find(W+'pPr')
                                    paragraphs.append({'text': content,
                                        'paragraph_properties_xml': ET.tostring(ppr, encoding='unicode') if ppr is not None else None})
                                parts.append({'part': name, 'paragraphs': paragraphs})
                        # Effective formatting remains fully preserved in the original archive.
                        styles = package.read('word/styles.xml').decode('utf-8') if 'word/styles.xml' in package.namelist() else None
                        assert_no_secret(styles or '')
                        write_line(docs, {'source': target.relative_to(repo).as_posix(), 'sha256': source_hash,
                            'format': suffix, 'parts': parts, 'styles_xml': styles})
                        index_count = 1
                elif suffix == '.pdf':
                    from pypdf import PdfReader
                    reader = PdfReader(source)
                    pages = [page.extract_text() or '' for page in reader.pages]
                    for text in pages: assert_no_secret(text)
                    write_line(docs, {'source': target.relative_to(repo).as_posix(), 'sha256': source_hash,
                        'format': suffix, 'pages': pages, 'original_preserves_signatures': True})
                    index_count = 1
                elif suffix == '.xlsx':
                    from openpyxl import load_workbook
                    book = load_workbook(source, read_only=True, data_only=False)
                    try:
                        for sheet in book.worksheets:
                            write_line(sheets, {'source': target.relative_to(repo).as_posix(), 'sha256': source_hash,
                                'sheet': sheet.title, 'kind': 'sheet', 'state': sheet.sheet_state,
                                'rows': sheet.max_row, 'columns': sheet.max_column, 'epoch': book.epoch.isoformat()})
                            for row in sheet.iter_rows():
                                cells = []
                                for cell in row:
                                    if cell.value is None: continue
                                    if isinstance(cell.value, str): assert_no_secret(cell.value)
                                    cells.append({'coordinate': cell.coordinate, 'value': cell.value,
                                                  'type': cell.data_type, 'number_format': cell.number_format})
                                if cells:
                                    write_line(sheets, {'source': target.relative_to(repo).as_posix(),
                                        'sheet': sheet.title, 'kind': 'row', 'cells': cells})
                                    index_count += 1
                    finally: book.close()
                # Copy ALL file types; do not silently exclude a source.
                shutil.copy2(source, target)
                if digest(target) != source_hash: raise ValueError('Copy integrity mismatch')
                counts[suffix or 'no_extension'] += 1
                manifest.append({'root_alias': label, 'relative_path': relative.as_posix(),
                    'repository_path': target.relative_to(repo).as_posix(), 'bytes': source.stat().st_size,
                    'sha256': source_hash, 'indexed_records': index_count})
    result = {'schema': 1, 'repository_required_visibility': 'PRIVATE', 'copied_files': len(manifest),
        'total_bytes': sum(item['bytes'] for item in manifest), 'counts': dict(counts), 'files': manifest}
    (archive / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'private_verified': True, 'files': len(manifest), 'counts': dict(counts),
                      'bytes': result['total_bytes'], 'every_copy_sha256_verified': True}))

if __name__ == '__main__':
    main()
