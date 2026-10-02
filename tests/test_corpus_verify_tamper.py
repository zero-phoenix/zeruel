import json
import hashlib
import tempfile
from pathlib import Path
import pytest

from tools.corpus import verify_corpus, sha256_file


def test_corpus_verify_passes_on_valid_data():
    """Valida que una estructura coincidente con corpus.lock pase la verificación."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_file = tmp_path / "fact.txt"
        test_file.write_bytes(b"Factual atomic evidence 12345")

        file_hash = hashlib.sha256(test_file.read_bytes()).hexdigest()
        lock_file = tmp_path / "corpus.lock"
        lock_data = {
            "version": 1,
            "repo": "zero-phoenix/zeruel-corpus",
            "commit": "mock-commit-sha",
            "file_count": 1,
            "files": {
                "fact.txt": file_hash
            }
        }
        lock_file.write_text(json.dumps(lock_data), encoding="utf-8")

        assert verify_corpus(corpus_dir=tmp_path, lock_path=lock_file, verbose=False) is True


def test_corpus_verify_fails_on_single_byte_tamper():
    """Falsacionismo de Popper: alterar exactamente 1 byte debe invalidar la verificación."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_file = tmp_path / "fact.txt"
        test_file.write_bytes(b"Factual atomic evidence 12345")

        file_hash = hashlib.sha256(test_file.read_bytes()).hexdigest()
        lock_file = tmp_path / "corpus.lock"
        lock_data = {
            "version": 1,
            "repo": "zero-phoenix/zeruel-corpus",
            "commit": "mock-commit-sha",
            "file_count": 1,
            "files": {
                "fact.txt": file_hash
            }
        }
        lock_file.write_text(json.dumps(lock_data), encoding="utf-8")

        # Mutación: alterar exactamente 1 byte (el último byte)
        original_bytes = test_file.read_bytes()
        tampered_bytes = original_bytes[:-1] + b"6"
        assert len(original_bytes) == len(tampered_bytes)
        assert sum(b1 != b2 for b1, b2 in zip(original_bytes, tampered_bytes)) == 1

        test_file.write_bytes(tampered_bytes)

        # La verificación DEBE fallar ante la mutación
        assert verify_corpus(corpus_dir=tmp_path, lock_path=lock_file, verbose=False) is False
