"""Mutaciones automáticas (Popper): cada regla crítica, rota a propósito, debe hacer fallar su prueba.

Trabaja sobre una copia temporal del repositorio; nunca toca el árbol real.
Uso: python tools/mutate.py  (sale con 1 si algún mutante sobrevive o no aplica).
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider"]
NODE = ["node", "--test"]

GATE_OK = '"cloud_gate_passed": False})\n            if self.path == "/":'

# (proposición, archivo, texto original, texto mutado, comando que debe FALLAR)
MUTANTES = [
    (
        "3.11",
        "zeruel/probe.py",
        'EXPECTED = {"marker": "ZERUEL_OK", "sum": 42}',
        'EXPECTED = {"marker": "ZERUEL_OK", "sum": 43}',
        PY + ["tests/test_probe.py"],
    ),
    (
        "3.16",
        "zeruel/probe.py",
        "result = {key: env[key] for key in allowed if key in env}",
        "result = dict(env)",
        PY + ["tests/test_probe.py"],
    ),
    (
        "3.21-3.23",
        "apps-script/SyntheticCheckpoint.gs",
        "return reply({ok:true,claimed:false,record:{state:'paused_uncertain',cloud_gate_passed:false}});",
        "{}",
        NODE + ["tests/checkpoint.test.cjs"],
    ),
    (
        "3.45",
        "zeruel/google_auth.py",
        '        if claims is None:\n            return False, "malformed"\n        if not self.accepted(claims, now):',
        '        if False:\n            return False, "malformed"\n        if claims and not self.accepted(claims, now):',
        PY + ["tests/test_google_auth.py"],
    ),
    (
        "3.47",
        "zeruel/server.py",
        GATE_OK,
        GATE_OK.replace("False", "True"),  # al vuelo: el guardia C2 prohíbe el literal
        PY + ["tests/test_http.py", "tests/test_contradicciones.py"],
    ),
    (
        "3.53",
        "web/app.js",
        "if (claims.nonce !== flow.nonce) return show({state: 'google_nonce_mismatch'});",
        "",
        NODE + ["tests/web.test.cjs"],
    ),
    (
        "3.61",
        "tools/corpus.py",
        "if actual_hash != expected_hash:",
        "if False:",
        PY + ["tests/test_corpus_verify_tamper.py"],
    ),
    (
        "3.64",
        "tools/corpus.py",
        "if rel not in expected_files:",
        "if False:",
        PY + ["tests/test_corpus_popper.py"],
    ),
    (
        "3.63",
        "tools/tractatus.py",
        'if "Falsador:" not in cuerpo:',
        "if False:",
        PY + ["tests/test_tractatus.py"],
    ),
]


def copia():
    destino = Path(tempfile.mkdtemp(prefix="zeruel-mut-"))
    shutil.copytree(
        ROOT,
        destino / "r",
        ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__", "work"),
    )
    return destino / "r"


def ejecutar(mutantes=MUTANTES):
    resultados = []
    for prop, archivo, original, mutado, comando in mutantes:
        repo = copia()
        try:
            ruta = repo / archivo
            texto = ruta.read_text(encoding="utf-8")
            if texto.count(original) != 1:
                resultados.append((prop, archivo, "NO_APLICA"))
                continue
            ruta.write_text(texto.replace(original, mutado), encoding="utf-8")
            r = subprocess.run(
                comando, cwd=repo, capture_output=True, text=True, timeout=600
            )
            resultados.append(
                (prop, archivo, "ELIMINADO" if r.returncode != 0 else "SOBREVIVE")
            )
        finally:
            shutil.rmtree(repo.parent, ignore_errors=True)
    return resultados


def main():
    res = ejecutar()
    for prop, archivo, estado in res:
        print(f"{estado:10} {prop:10} {archivo}")
    malos = [r for r in res if r[2] != "ELIMINADO"]
    print(
        f"mutantes={len(res)} eliminados={len(res) - len(malos)} supervivientes_o_no_aplica={len(malos)}"
    )
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
