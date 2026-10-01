#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resume de forma legible las diferencias para cada uno de los 8 pares."""

import json

def summarize():
    with open('knowledge/diferencias_aprendizaje.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for caso, info in data.items():
        print(f"==================================================")
        print(f"CASO: {caso}")
        print(f"==================================================")
        diffs = info['diferencias']
        print(f"Total bloques modificados: {len(diffs)}")
        for idx, d in enumerate(diffs):
            tipo = d['tipo']
            print(f"\n--- Bloque {idx+1} ({tipo}) ---")
            if d['borrador_lineas']:
                print("BORRADOR:")
                for l in d['borrador_lineas']:
                    print(f"  [-] {l}")
            if d['corregido_lineas']:
                print("CORREGIDO (LSQ):")
                for l in d['corregido_lineas']:
                    print(f"  [+] {l}")
        print("\n")

    with open('knowledge/diff_summary.md', 'w', encoding='utf-8') as out_f:
        for caso, info in data.items():
            out_f.write(f"==================================================\n")
            out_f.write(f"CASO: {caso}\n")
            out_f.write(f"==================================================\n")
            diffs = info['diferencias']
            out_f.write(f"Total bloques modificados: {len(diffs)}\n")
            for idx, d in enumerate(diffs):
                tipo = d['tipo']
                out_f.write(f"\n--- Bloque {idx+1} ({tipo}) ---\n")
                if d['borrador_lineas']:
                    out_f.write("BORRADOR:\n")
                    for l in d['borrador_lineas']:
                        out_f.write(f"  [-] {l}\n")
                if d['corregido_lineas']:
                    out_f.write("CORREGIDO (LSQ):\n")
                    for l in d['corregido_lineas']:
                        out_f.write(f"  [+] {l}\n")
    print("Guardado en knowledge/diff_summary.md")

if __name__ == '__main__':
    summarize()

