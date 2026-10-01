#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Busca las plantillas maestras más similares para los 3 casos en C:\Users\D\SystemHope\repo."""

import json
import os

idx_path = r"C:\Users\D\SystemHope\repo\docs\plantillas_maestras_index.json"
with open(idx_path, "r", encoding="utf-8") as f:
    plantillas = json.load(f)

print(f"Total plantillas maestras en índice: {len(plantillas)}")

def buscar(terminos, rama=None, top=6):
    res = []
    for p in plantillas:
        texto = json.dumps(p, ensure_ascii=False).lower()
        if rama and p.get("rama") != rama:
            continue
        score = sum(2 for t in terminos if t.lower() in texto)
        # Bonus si el proveedor coincide
        if "pacifico" in terminos and "pacifico" in texto:
            score += 3
        if "rimac" in terminos and "rimac" in texto:
            score += 3
        if "chubb" in terminos and "chubb" in texto:
            score += 3
        if score > 0:
            res.append((score, p))
    res.sort(key=lambda x: x[0], reverse=True)
    return res[:top]

print("\n=== CASO 3017: VIDA / INFORMACIÓN / TELEFÓNICA / PACÍFICO ===")
for sc, p in buscar(["telefonica", "vida", "informacion", "grabacion", "rescate", "pacifico"], rama="02_seguro_vida"):
    arch = p.get("archivo", "")
    subt = p.get("subtipo", "")
    print(f"  Score {sc}: {arch} | {subt}")

print("\n=== CASO 3057: DESGRAVAMEN / FALLECIMIENTO / PREEXISTENCIA / VIGENCIA / RÍMAC ===")
for sc, p in buscar(["fallecimiento", "desgravamen", "preexistencia", "vigencia", "rimac"], rama="03_seguro_desgravamen"):
    arch = p.get("archivo", "")
    subt = p.get("subtipo", "")
    print(f"  Score {sc}: {arch} | {subt}")

print("\n=== CASO 3075: DAÑOS MATERIALES / RUPTURA / CHUBB / INMUEBLES / RESPONSABILIDAD ===")
for sc, p in buscar(["daños", "inmueble", "responsabilidad civil", "chubb", "tubería"]):
    arch = p.get("archivo", "")
    rama = p.get("rama", "")
    print(f"  Score {sc}: {arch} | {rama}")
