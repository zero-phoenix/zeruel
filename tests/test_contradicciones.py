"""Pruebas de las contradicciones resueltas (docs/tractatus/contradicciones.md)."""
import pathlib, re, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class Contradicciones(unittest.TestCase):
    def test_c1_cloud_gate_never_true_in_source(self):
        pat = re.compile(r"""["']cloud_gate_passed["']\s*:\s*(True|true)|cloud_gate_passed\s*=\s*(True|true)""")
        hits = [str(p.relative_to(ROOT)) for d in ("zeruel", "web", "apps-script", "tools")
                for p in (ROOT / d).rglob("*") if p.is_file() and p.suffix in (".py", ".js", ".gs")
                and pat.search(p.read_text(encoding="utf-8", errors="ignore"))]
        self.assertEqual(hits, [])

    def test_c2_pings_only_as_temporary_exception(self):
        no_keepalive = (ROOT / "docs/HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("sin keepalive artificial", no_keepalive)
        for p in (ROOT / "docs").glob("*.md"):
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                if re.search(r"/healthz`? cada \d+ ?min", line):
                    self.assertIn("excepción temporal", line, p.name)
        for d in ("web", "apps-script", "zeruel"):
            for p in (ROOT / d).rglob("*"):
                if p.is_file() and p.suffix in (".js", ".gs"):
                    self.assertNotIn("healthz", p.read_text(encoding="utf-8", errors="ignore"), p.name)


if __name__ == "__main__":
    unittest.main()
