"""El Tractatus es ejecutable: cada proposición 3.x tiene falsador y pruebas existentes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import tractatus  # noqa: E402

# Trinquete: las pruebas huérfanas solo pueden disminuir (fase F2 las lleva a 0).
MAX_HUERFANAS = 85


def test_tractatus_lint_passes():
    assert tractatus.fallos() == []


def test_lint_detects_missing_cited_test():
    texto = "- **3.11** Regla. Falsador: x. Prueba: `test_que_no_existe`."
    assert any("no existe" in f for f in tractatus.fallos(texto, existentes=set()))


def test_lint_detects_missing_falsifier_and_duplicate_numbering():
    texto = (
        "- **3.11** Regla. Prueba: `test_a`.\n"
        "- **3.11** Regla. Falsador: x. Prueba: `test_a`."
    )
    f = tractatus.fallos(texto, existentes={"test_a"})
    assert any("sin falsador" in x for x in f)
    assert any("duplicada" in x for x in f)


def test_lint_detects_gap_in_numbering():
    texto = (
        "- **3.11** R. Falsador: x. Prueba: `test_a`.\n"
        "- **3.13** R. Falsador: x. Prueba: `test_a`."
    )
    assert any(
        "no consecutiva" in x for x in tractatus.fallos(texto, existentes={"test_a"})
    )


def test_orphan_tests_do_not_grow():
    assert len(tractatus.huerfanas()) <= MAX_HUERFANAS


def test_mutants_apply_to_current_sources():
    """Cada mutante de tools/mutate.py encuentra su texto exactamente una vez (la lista no caduca)."""
    import mutate
    for prop, archivo, original, _, _ in mutate.MUTANTES:
        texto = (mutate.ROOT / archivo).read_text(encoding="utf-8")
        assert texto.count(original) == 1, (prop, archivo)
