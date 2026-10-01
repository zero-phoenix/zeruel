#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrae y estructura todas las diferencias entre borradores y corregidos por la jefa (LSQ)."""

import os
import json
import difflib
import zipfile
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def abrir(ruta):
    z = zipfile.ZipFile(ruta)
    xml = z.read('word/document.xml')
    root = ET.fromstring(xml)
    parrafos = []
    for p in root.iter(W + 'p'):
        piezas = []
        for r in p.iter(W + 'r'):
            rpr = r.find(W + 'rPr')
            b = rpr.find(W + 'b') if rpr is not None else None
            bold = b is not None and b.get(W + 'val') not in ('0', 'false')
            t = ''.join(x.text or '' for x in r.iter(W + 't'))
            for fr in r.iter(W + 'footnoteReference'):
                fn_id = fr.get(W + 'id')
                t += f'[^fn:{fn_id}]'
            if bold and t.strip():
                t = f'**{t}**'
            piezas.append(t)
        texto = ''.join(piezas).strip()
        if texto:
            parrafos.append(texto)
    
    footnotes = {}
    if 'word/footnotes.xml' in z.namelist():
        fn_root = ET.fromstring(z.read('word/footnotes.xml'))
        for fn in fn_root.iter(W + 'footnote'):
            fid = fn.get(W + 'id')
            if fn.get(W + 'type') in ('separator', 'continuationSeparator', 'continuationNotice'):
                continue
            f_text = ''.join(t.text or '' for t in fn.iter(W + 't')).strip()
            if f_text:
                footnotes[fid] = f_text
    return parrafos, footnotes

def extraer_todos():
    b_dir = r'C:\Users\D\Desktop\Aprendizaje\borradores de agosto sin correccion'
    c_dir = r'C:\Users\D\Desktop\Aprendizaje\corregidos'

    pairs = [
        ('2693-2026 R2', os.path.join(b_dir, 'ADM 2693-2026 R2.docx'), os.path.join(c_dir, 'ADM 2693-2026 R2 - LSQok.docx')),
        ('2723-2026 R2', os.path.join(b_dir, 'ADM 2723-2026 R2.docx'), os.path.join(c_dir, 'ADM 2723-2026 R2 - LSQok.docx')),
        ('2739-2026 R2', os.path.join(b_dir, 'ADM 2739-2026 R2.docx'), os.path.join(c_dir, 'ADM 2739-2026 R2 - LSQok.docx')),
        ('2847-2026 R2', os.path.join(b_dir, 'ADM 2847-2026 R2.docx'), os.path.join(c_dir, 'ADM 2847-2026 R2 - LSQok.docx')),
        ('2873-2026 R1', os.path.join(b_dir, 'ADM 2873-2026 R1.docx'), os.path.join(c_dir, 'ADM 2873-2026 R1 - LSQok.docx')),
        ('2953-2026 R1', os.path.join(b_dir, 'ADM 2953-2026 R1.docx'), os.path.join(c_dir, 'ADM 2953-2026 R1 - LSQok.docx')),
        ('2972-2026 R1', os.path.join(b_dir, 'ADM 2972-2026 R1.docx'), os.path.join(c_dir, 'ADM 2972-2026 R1 - LSQok.docx')),
        ('3038-2026 R1', os.path.join(b_dir, 'ADM  3038-2026 R1.docx'), os.path.join(c_dir, 'ADM 3038-2026 R1 - LSQok.docx')),
    ]

    reporte = {}
    for name, pb, pc in pairs:
        pb_pars, pb_fns = abrir(pb)
        pc_pars, pc_fns = abrir(pc)
        
        matcher = difflib.SequenceMatcher(None, pb_pars, pc_pars)
        opcodes = matcher.get_opcodes()
        
        diff_items = []
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                continue
            item = {
                'tipo': tag,
                'borrador_lineas': pb_pars[i1:i2],
                'corregido_lineas': pc_pars[j1:j2]
            }
            diff_items.append(item)
            
        reporte[name] = {
            'borrador_path': pb,
            'corregido_path': pc,
            'parrafos_borrador': len(pb_pars),
            'parrafos_corregido': len(pc_pars),
            'diferencias': diff_items,
            'footnotes_borrador': pb_fns,
            'footnotes_corregido': pc_fns
        }
    
    out_path = r'C:\Users\D\Documents\antigravity\eager-hertz\zeruel\knowledge\diferencias_aprendizaje.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    print(f"Reporte de diferencias generado exitosamente en {out_path}")

if __name__ == '__main__':
    extraer_todos()
