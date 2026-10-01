#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/summarize_diffs.py: Resume de forma legible en Markdown las diferencias
extraídas de documentos de aprendizaje."""

import sys
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def summarize(input_path: Path = None, output_path: Path = None):
    in_file = input_path or (ROOT / 'knowledge' / 'diferencias_aprendizaje.json')
    out_file = output_path or (ROOT / 'knowledge' / 'diff_summary.md')

    if not in_file.exists():
        print(f"[WARN] Archivo de entrada no encontrado: {in_file}")
        return

    with open(in_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as out_f:
        for caso, info in data.items():
            out_f.write(f"==================================================\n")
            out_f.write(f"CASO: {caso}\n")
            out_f.write(f"==================================================\n")
            diffs = info.get('diferencias', [])
            out_f.write(f"Total bloques modificados: {len(diffs)}\n")
            for idx, d in enumerate(diffs):
                tipo = d.get('tipo', 'cambio')
                out_f.write(f"\n--- Bloque {idx+1} ({tipo}) ---\n")
                if d.get('borrador_lineas'):
                    out_f.write("BORRADOR:\n")
                    for l in d['borrador_lineas']:
                        out_f.write(f"  [-] {l}\n")
                if d.get('corregido_lineas'):
                    out_f.write("CORREGIDO (LSQ):\n")
                    for l in d['corregido_lineas']:
                        out_f.write(f"  [+] {l}\n")
            out_f.write("\n")

    print(f"Resumen generado exitosamente en: {out_file}")


def main():
    parser = argparse.ArgumentParser(description="Genera resumen Markdown de diferencias de aprendizaje.")
    parser.add_argument("--input", type=Path, default=None, help="Archivo JSON de diferencias de entrada")
    parser.add_argument("--output", type=Path, default=None, help="Archivo Markdown de salida")
    args = parser.parse_args()
    summarize(args.input, args.output)


if __name__ == '__main__':
    main()
