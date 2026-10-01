#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import zipfile
import re
import docx

cases = [
    ('3017', r'C:\Users\D\Desktop\Nuevas correcciones\3017-2026\ADM 3017-2026 R2.docx'),
    ('3057', r'C:\Users\D\Desktop\Nuevas correcciones\3057-2026\ADM 3057-2026 R2.docx'),
    ('3075', r'C:\Users\D\Desktop\Nuevas correcciones\3075-2026\ADM 3075-2026 R2.docx'),
]

for c, p in cases:
    print(f"=== AUDITORÍA CASO {c} ===")
    z = zipfile.ZipFile(p)
    doc_xml = z.read('word/document.xml').decode('utf-8', 'replace')
    hl = re.findall(r'<w:highlight\b', doc_xml)
    print(f"Highlights restantes: {len(hl)}")
    doc = docx.Document(p)
    print(f"Párrafos totales: {len(doc.paragraphs)}")
    
    # Buscar palabras clave residuales
    for bad in ['remolque', 'transferido a Rímac']:
        count = doc_xml.lower().count(bad.lower())
        print(f"Menciones de '{bad}': {count}")
    
    # En caso 3075, lucro cesante solo debe aparecer en el considerando de descarte/incompetencia
    if c == '3075':
        lc_count = doc_xml.lower().count('lucro cesante')
        print(f"Menciones de 'lucro cesante' (debe ser 1 en descarte): {lc_count}")
    print()
