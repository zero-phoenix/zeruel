"""Finalize portable notes without altering historical evidence."""
from pathlib import Path
import json, re, socket
ROOT = Path(__file__).resolve().parents[1]
host = socket.gethostname()
update = f'''# Relevo vigente: archivo privado integral — 30/09/2026

- Host: {host}. Rama codex/seguros-knowledge, base main 79e1bcd. Ver git log para commit publicado y PR de archivo. El checkout original codex/extension-capture-ocr (1ad02a76) permanece intacto.
- REAL: repositorio cambiado a PRIVATE y verificado. Los 182 originales de documentos y reporte solo seguros están completos, con hashes de fuente/copia iguales (30.193.970 bytes). Índices: 177 documentos, 23 hojas, 9.229 filas no vacías, incluyendo encabezados. Esto no equivale a 9.229 expedientes. Ver knowledge/verification-local.json.
- Leer knowledge/README.md, WORKLOAD.md y PROMPT-continuacion.md. Archivo privado autorizado expresamente por el propietario; sustituye la anterior prohibición general de guardar expedientes solamente dentro de este archivo privado. No autoriza exponerlos en nube pública ni ejecutar actuaciones. Cambios de privacidad pueden requerir nueva conexión privada autorizada para futuros deploys de Render; no volver público para resolverlo.
- REAL: PR #22 fusionado en 8662fb894 y PR #23 en 79e1bcd; el sitio respondió 200 y contiene autorun/recuperación, pero SHA de despliegue no comprobada. PR #21 no autorizado y sigue aparte.
- REAL móvil manual: ID 0a079423ff3c3fcc25f255e6a1058255, synthetic_success, ZERUEL_OK/suma42, completed=1790810077 UTC, Windows encendido. No demuestra autorun ni ambas PCs apagadas. ADB cerrado, sin ajustes modificados.
- SIMULADA histórica: 61 Python aprobadas. Suite Node del trabajo local de extensión con fallo PII para «Ella Pumayalli Soncco»; archivado sin corregir/activar. La preservación documental no añadió ni acreditó nuevas pruebas OAuth/inferencia.
- cloud_gate_passed=false. Pendientes: toda fila REAL aún faltante de matriz, autorun móvil nuevo ID, diferidos 60/120/600s, intervalo de PCs apagadas demostrado, renovación checkpoint T1+61..70min y no reinicios, verificación versión Render y resto de bloqueos históricos.
- Procesos auxiliares activos de esta tarea: ninguno. No borrados, reinicios ni modificaciones del teléfono. El propietario formatea por su cuenta; antes debe poder recuperar desde GitHub el PR/rama de archivo o su merge autorizado.

Los registros siguientes se conservan como historia; esta actualización corrige afirmaciones anteriores de repositorio público, ausencia de archivo real, PR #22/#23 pendiente y autorun inexistente.

---

'''
for name in ['docs/STATUS.md', 'docs/HANDOFF.md']:
    path = ROOT/name
    text = path.read_text(encoding='utf-8')
    if not text.startswith('# Relevo vigente: archivo privado integral'):
        path.write_text(update+text, encoding='utf-8')
section = '''
## 12. Memoria integral de seguros antes del formateo

La fuente de arranque es knowledge/README.md y knowledge/PROMPT-continuacion.md. Se preservaron completos ambos directorios autorizados, no solamente resúmenes anonimizados. WORKLOAD integra calificación/admisión 20 días hábiles, procedimiento primera instancia 120 días hábiles, FECHA LÍMITE final, requerimientos/subsanación/inadmisibilidad, improcedencia por causal, apelaciones CC1 antiguas primero y vínculo resolución-cédula-notificación. Copias/reglas de sistemas especializados y trabajo local pendiente están documentados. Cada reloj requiere fuente, notificación, calendario y suspensiones por expediente. No confundir archivo privado con motor operativo ni con aprobación del hito cloud.
'''
path = ROOT/'docs/HANDOFF.md'
text = path.read_text(encoding='utf-8')
if '## 12. Memoria integral de seguros antes del formateo' not in text:
    path.write_text(text+section, encoding='utf-8')
matrix = ROOT/'docs/first-milestone.md'
text = matrix.read_text(encoding='utf-8')
notice = '''> Actualización 30/09/2026: el archivo integral privado se conserva en knowledge/; no satisface ninguna fila técnica adicional de esta matriz. La prueba manual REAL móvil registrada en HANDOFF ocurrió con Windows encendido. Autorun real, apagado de ambas PCs y renovación permanecen pendientes. cloud_gate_passed=false.\n\n'''
if not text.startswith(notice): matrix.write_text(notice+text, encoding='utf-8')
catalog = []
patterns = {'admisión':r'admitir|admisorio', 'subsanación':r'subsan',
            'inadmisibilidad':r'inadmisib', 'improcedencia':r'improceden',
            'apelación':r'apelaci[oó]n', 'cédula':r'c[eé]dula',
            'notificación':r'notific', 'confidencialidad':r'confidencial|reserva',
            'SUSALUD':r'susalud'}
with (ROOT/'knowledge/private_index/documents.jsonl').open(encoding='utf-8') as stream:
    for line in stream:
        doc = json.loads(line)
        text = '\n'.join(doc.get('pages', [])) if doc['format'] == '.pdf' else '\n'.join(
            p['text'] for part in doc['parts'] for p in part['paragraphs'])
        catalog.append({'source':doc['source'], 'sha256':doc['sha256'], 'format':doc['format'],
            'text_characters':len(text), 'lexical_tags_not_legal_classification':[
                key for key,pattern in patterns.items() if re.search(pattern,text,re.I)],
            'opening_text_for_retrieval':text[:900]})
(ROOT/'knowledge/private_index/catalog.json').write_text(
    json.dumps({'classification':'nonexclusive lexical retrieval only','documents':catalog},
               ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['tools/analyze_workload.py', 'tools/snapshot_related_repositories.py']:
    path = ROOT/name
    text = path.read_text(encoding='utf-8').replace('autre_ou_inconnue','otra_o_desconocida').replace('templates_docx','docx_files')
    text = re.sub(r"^        paras = \[''\.join\(p\.itertext\(\)\) for p in \[\]\].*\n",'',text,flags=re.M)
    path.write_text(text,encoding='utf-8')
print(json.dumps({'portable_notes':True,'retrieval_catalog_documents':len(catalog)}))
