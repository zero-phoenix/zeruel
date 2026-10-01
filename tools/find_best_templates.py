#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/find_best_templates.py: Algoritmo de similitud léxica para búsqueda y selección
de plantillas maestras según términos y rama procesal."""

import os
import sys
import json
import argparse
from pathlib import Path

DEFAULT_INDEX_PATH = Path(os.environ.get("SYSTEMHOPE_TEMPLATES_INDEX", Path.home() / "SystemHope" / "repo" / "docs" / "plantillas_maestras_index.json"))


def buscar_plantillas(plantillas: list, terminos: list, rama: str = None, top: int = 6):
    res = []
    for p in plantillas:
        texto = json.dumps(p, ensure_ascii=False).lower()
        if rama and p.get("rama") != rama:
            continue
        score = sum(2 for t in terminos if t.lower() in texto)
        for prov in ["pacifico", "rimac", "chubb", "mapfre", "la positiva"]:
            if prov in terminos and prov in texto:
                score += 3
        if score > 0:
            res.append((score, p))
    res.sort(key=lambda x: x[0], reverse=True)
    return res[:top]


def main():
    parser = argparse.ArgumentParser(description="Busca plantillas maestras por similitud léxica.")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH, help="Ruta al archivo plantillas_maestras_index.json")
    parser.add_argument("--terms", nargs="*", default=None, help="Términos clave de búsqueda")
    parser.add_argument("--rama", type=str, default=None, help="Filtro de rama procesal")
    parser.add_argument("--top", type=int, default=6, help="Número máximo de resultados")
    args = parser.parse_args()

    if not args.index.exists():
        print(f"[WARN] Índice de plantillas no encontrado en: {args.index}")
        print("Especifique una ruta válida mediante --index o variable de entorno SYSTEMHOPE_TEMPLATES_INDEX.")
        sys.exit(0)

    with open(args.index, "r", encoding="utf-8") as f:
        plantillas = json.load(f)

    print(f"Total plantillas maestras en índice: {len(plantillas)}")

    if args.terms:
        resultados = buscar_plantillas(plantillas, args.terms, rama=args.rama, top=args.top)
        print(f"\nResultados para términos: {args.terms} (rama={args.rama}):")
        for sc, p in resultados:
            print(f"  Score {sc}: {p.get('archivo', '')} | {p.get('subtipo', p.get('rama', ''))}")
    else:
        # Búsquedas canónicas de demostración
        queries = [
            ("CASO 3017: VIDA / INFORMACIÓN / TELEFÓNICA / PACÍFICO", ["telefonica", "vida", "informacion", "grabacion", "rescate", "pacifico"], "02_seguro_vida"),
            ("CASO 3057: DESGRAVAMEN / FALLECIMIENTO / PREEXISTENCIA / RÍMAC", ["fallecimiento", "desgravamen", "preexistencia", "vigencia", "rimac"], "03_seguro_desgravamen"),
            ("CASO 3075: DAÑOS MATERIALES / RUPTURA / CHUBB / INMUEBLES", ["daños", "inmueble", "responsabilidad civil", "chubb", "tubería"], None),
        ]
        for desc, terms, rama in queries:
            print(f"\n=== {desc} ===")
            for sc, p in buscar_plantillas(plantillas, terms, rama=rama, top=args.top):
                print(f"  Score {sc}: {p.get('archivo', '')} | {p.get('subtipo', p.get('rama', ''))}")


if __name__ == "__main__":
    main()
