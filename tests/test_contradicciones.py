"""Pruebas de las contradicciones resueltas (docs/tractatus/contradicciones.md).

C1 = keepalive (pings solo como excepción temporal); C2 = cloud_gate_passed nunca true.
"""

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CODIGO = ("zeruel", "web", "apps-script", "tools", "scripts")
EXT = (".py", ".js", ".gs", ".ps1", ".sh")
# Una LLAMADA a /healthz (cliente), no la definición de la ruta en el servidor.
LLAMADA_HEALTHZ = re.compile(
    r"(fetch|urlopen|requests\.(get|head)|Invoke-WebRequest|Invoke-RestMethod|curl|wget)[^\n]{0,200}healthz",
    re.I,
)


def archivos():
    for d in CODIGO:
        for p in (ROOT / d).rglob("*"):
            if p.is_file() and p.suffix in EXT:
                yield p


class Contradicciones(unittest.TestCase):
    def test_c1_pings_only_as_temporary_exception(self):
        regla = next(
            l
            for l in (ROOT / "docs/HANDOFF.md").read_text(encoding="utf-8").splitlines()
            if "sin keepalive artificial" in l
        )
        # La regla única debe enunciar la excepción en el mismo lugar donde prohíbe.
        self.assertIn("excepción temporal", regla)
        # contradicciones.md cita la contradicción antigua para documentarla: no es una regla vigente.
        for p in (ROOT / "docs").rglob("*.md"):
            if p.name == "contradicciones.md":
                continue
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                if re.search(r"/healthz`? cada \d+ ?min", line):
                    self.assertIn("excepción temporal", line, p.name)
        llamadas = [
            str(p.relative_to(ROOT))
            for p in archivos()
            if LLAMADA_HEALTHZ.search(p.read_text(encoding="utf-8", errors="ignore"))
        ]
        self.assertEqual(llamadas, [], "código que hace pings a /healthz (keepalive)")

    def test_c2_cloud_gate_never_true_in_source(self):
        pat = re.compile(
            r"""["']cloud_gate_passed["']\s*:\s*(True|true)|cloud_gate_passed\s*=\s*(True|true)"""
        )
        hits = [
            str(p.relative_to(ROOT))
            for p in archivos()
            if pat.search(p.read_text(encoding="utf-8", errors="ignore"))
        ]
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
