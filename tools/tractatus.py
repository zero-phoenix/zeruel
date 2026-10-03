"""Lint del Tractatus: cada proposición de 3.x tiene falsador y pruebas que existen.

Uso: python tools/tractatus.py  (sale con 1 si hay fallos; imprime las pruebas huérfanas).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSICIONES = ROOT / "docs" / "tractatus" / "3-proposiciones.md"
FUENTES_PY = sorted((ROOT / "tests").glob("test_*.py"))
FUENTES_JS = sorted((ROOT / "tests").glob("*.cjs")) + sorted(
    (ROOT / "extension" / "tests").glob("*.test.js")
)

ITEM = re.compile(r"^- \*\*(3\.\d+)\*\* (.*)$")
DEUDA = re.compile(r"^- \*\*(D\d+)\*\* (.*)$")
CITA = re.compile(r"`([^`]+)`")


def proposiciones(texto=None):
    """Lista de (numero, cuerpo) de las proposiciones 3.x, en orden de aparición."""
    texto = PROPOSICIONES.read_text(encoding="utf-8") if texto is None else texto
    return [m.groups() for m in map(ITEM.match, texto.splitlines()) if m]


def pruebas_citadas(cuerpo):
    """Nombres entre comillas invertidas tras «Prueba:»/«Pruebas:»."""
    m = re.search(r"Pruebas?:\s*(.*)$", cuerpo)
    return CITA.findall(m.group(1)) if m else []


def pruebas_existentes():
    """Nombres de prueba definidos: funciones test_* de Python y títulos literales de node:test."""
    nombres = set()
    for p in FUENTES_PY:
        nombres |= set(
            re.findall(r"^\s*def (test_\w+)\(", p.read_text(encoding="utf-8"), re.M)
        )
    for p in FUENTES_JS:
        nombres |= set(
            re.findall(
                r"""\btest\(\s*(['"])(.+?)\1\s*,""", p.read_text(encoding="utf-8")
            )
        )
    return {n if isinstance(n, str) else n[1] for n in nombres}


def fallos(texto=None, existentes=None):
    existentes = pruebas_existentes() if existentes is None else existentes
    archivos = {p.name for p in FUENTES_PY + FUENTES_JS}
    out, vistos = [], set()
    items = proposiciones(texto)
    if not items:
        return ["no se encontró ninguna proposición 3.x"]
    for numero, cuerpo in items:
        if numero in vistos:
            out.append(f"{numero}: numeración duplicada")
        vistos.add(numero)
        if "Falsador:" not in cuerpo:
            out.append(f"{numero}: sin falsador")
        citas = pruebas_citadas(cuerpo)
        if not citas:
            out.append(f"{numero}: sin prueba citada")
        for c in citas:
            if c not in existentes and c not in archivos:
                out.append(f"{numero}: la prueba citada no existe: {c}")
    # Dentro de cada sección 3.N la numeración es consecutiva (3.N1, 3.N2, ...).
    por_seccion = {}
    for numero, _ in items:
        por_seccion.setdefault(numero[:3], []).append(int(numero[3:]))
    for seccion, ns in por_seccion.items():
        if ns != list(range(1, len(ns) + 1)):
            out.append(f"{seccion}x: numeración no consecutiva {ns}")
    return out


def huerfanas(texto=None, existentes=None):
    """Pruebas definidas que ninguna proposición cita."""
    existentes = pruebas_existentes() if existentes is None else existentes
    citadas = {c for _, cuerpo in proposiciones(texto) for c in pruebas_citadas(cuerpo)}
    return sorted(existentes - citadas)


def main():
    f = fallos()
    for x in f:
        print("FALLO", x)
    h = huerfanas()
    print(f"proposiciones={len(proposiciones())} fallos={len(f)} huerfanas={len(h)}")
    for x in h:
        print("HUERFANA", x)
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main())
