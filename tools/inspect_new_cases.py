#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Extrae y resume el contenido de cada caso de C:\Users\D\Desktop\Nuevas correcciones."""

import os
import fitz
import docx

def parse_case(folder_name):
    base = os.path.join(r"C:\Users\D\Desktop\Nuevas correcciones", folder_name)
    print(f"\n=======================================================")
    print(f"ANÁLISIS DETALLADO DEL CASO: {folder_name}")
    print(f"=======================================================")
    
    # 1. Leer el borrador Word
    doc_path = os.path.join(base, f"ADM {folder_name} R2 borrador.docx")
    if os.path.exists(doc_path):
        doc = docx.Document(doc_path)
        print(f"\n--- BORRADOR WORD: {len(doc.paragraphs)} párrafos ---")
        for i, p in enumerate(doc.paragraphs):
            t = p.text.strip()
            if t:
                # Filtrar encabezados, hechos, imputaciones y requerimientos
                if any(k in t.upper() for k in ["EXPEDIENTE", "DENUNCIANTE", "DENUNCIADO", "MATERIA", "RESOLUCIÓN", "HECHOS", "INFRACCIÓN", "ARTÍCULO", "RESUELVE", "PRIMERO", "SEGUNDO", "TERCERO", "CUARTO", "QUINTO", "DÉCIMO"]):
                    print(f"  [P{i:02d}] {t[:140]}")
                elif "consistente en que" in t or "reclamo" in t.lower() or "siniestro" in t.lower():
                    print(f"  [P{i:02d}] {t[:140]}")
    else:
        print(f"No se encontró borrador: {doc_path}")

    # 2. Leer los PDFs
    print(f"\n--- DOCUMENTOS PDF DEL EXPEDIENTE ---")
    for f in sorted(os.listdir(base)):
        if f.endswith(".pdf"):
            ppath = os.path.join(base, f)
            pdf = fitz.open(ppath)
            full_text = ""
            for page in pdf:
                full_text += page.get_text() + "\n"
            print(f"\n* PDF: {f} ({len(pdf)} págs, {len(full_text)} caracteres)")
            # Mostrar los primeros 300 caracteres limpios
            limpio = " ".join(full_text.split())
            print(f"  Inicio: {limpio[:350]}")

if __name__ == "__main__":
    for c in ["3017-2026", "3057-2026", "3075-2026"]:
        parse_case(c)
