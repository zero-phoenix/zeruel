import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_no_private_blobs_or_binary_facts():
    """Verifica que el repositorio del Cerebro (zero-phoenix/zeruel) permanezca
    estrictamente desacoplado de hechos privados, binarios pesados (.docx/.xlsx/.pdf)
    y fuentes de knowledge/private_*."""
    res = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True
    )
    tracked_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]

    forbidden_extensions = (".docx", ".xlsx", ".pdf")
    forbidden_prefixes = ("knowledge/private_", "knowledge/borrador_")

    violations = []
    for f in tracked_files:
        f_lower = f.lower()
        if any(f_lower.endswith(ext) for ext in forbidden_extensions):
            violations.append(f"Binario prohibido rastreado en git: {f}")
        if any(f.startswith(prefix) for prefix in forbidden_prefixes):
            violations.append(f"Archivo de fuentes privadas rastreado en git: {f}")

    assert not violations, "Violación del desacoplamiento Cerebro/Corpus:\n" + "\n".join(violations)
