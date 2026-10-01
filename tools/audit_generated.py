#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/audit_generated.py: Auditoría estructural de resoluciones generadas vs modelos.
Comprueba marcas de resaltado residuales (<w:highlight>), conteo de párrafos y palabras clave.
"""

import sys
import argparse
import zipfile
import re
from pathlib import Path
import docx


def audit_file(path: Path, keywords: list = None):
    p_str = str(path)
    print(f"=== AUDITORÍA ARCHIVO: {path.name} ===")
    if not path.exists():
        print(f"[ERROR] Archivo no encontrado: {path}")
        return

    with zipfile.ZipFile(p_str) as z:
        doc_xml = z.read('word/document.xml').decode('utf-8', 'replace')

    hl = re.findall(r'<w:highlight\b', doc_xml)
    print(f"Highlights restantes: {len(hl)}")

    doc = docx.Document(p_str)
    print(f"Párrafos totales: {len(doc.paragraphs)}")

    if keywords:
        for kw in keywords:
            count = doc_xml.lower().count(kw.lower())
            print(f"Menciones de '{kw}': {count}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Auditoría estructural de documentos DOCX.")
    parser.add_argument("files", nargs="*", type=Path, help="Archivos DOCX a auditar")
    parser.add_argument("--dir", type=Path, default=None, help="Directorio con documentos a auditar")
    parser.add_argument("--keywords", nargs="*", default=["remolque", "transferido a Rímac"], help="Palabras clave a buscar")
    args = parser.parse_args()

    target_files = list(args.files)
    if args.dir and args.dir.exists():
        target_files.extend(args.dir.glob("*.docx"))

    if not target_files:
        print("No se especificaron archivos DOCX para auditar.")
        sys.exit(0)

    for f in target_files:
        audit_file(f, args.keywords)


if __name__ == "__main__":
    main()
