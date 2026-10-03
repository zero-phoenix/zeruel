"""Falsadores adicionales del corpus: sobrantes, recuento, commit distinto y ida y vuelta pin/sync."""
import hashlib
import json
import subprocess
from pathlib import Path

from tools.corpus import pin_corpus, sync_corpus, verify_corpus


def _lock(tmp, files, commit="c0ffee", count=None):
    lock = tmp / "corpus.lock"
    hashes = {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}
    lock.write_text(json.dumps({"version": 1, "repo": "x/y", "commit": commit,
                                "file_count": len(hashes) if count is None else count,
                                "files": hashes}), encoding="utf-8")
    return lock


def _git(*args, cwd):
    subprocess.run(["git", "-c", "user.email=t@example.test", "-c", "user.name=t", *args],
                   cwd=cwd, check=True, capture_output=True)


def test_corpus_verify_fails_on_extra_file(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"a")
    lock = _lock(tmp_path, {"a.txt": b"a"})
    assert verify_corpus(tmp_path, lock, verbose=False) is True
    (tmp_path / "intruso.txt").write_bytes(b"x")
    assert verify_corpus(tmp_path, lock, verbose=False) is False


def test_corpus_verify_fails_on_file_count_mismatch(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"a")
    assert verify_corpus(tmp_path, _lock(tmp_path, {"a.txt": b"a"}, count=2), verbose=False) is False


def test_corpus_verify_fails_when_head_moves(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.txt").write_bytes(b"a")
    _git("init", "-q", cwd=repo); _git("add", ".", cwd=repo); _git("commit", "-qm", "1", cwd=repo)
    lock = tmp_path / "corpus.lock"
    assert pin_corpus(repo, repo="x/y", lock_path=lock)
    assert verify_corpus(repo, lock, verbose=False) is True
    (repo / "a.txt").write_bytes(b"a")  # mismo contenido, nuevo commit
    _git("commit", "-q", "--allow-empty", "-m", "2", cwd=repo)
    assert verify_corpus(repo, lock, verbose=False) is False


def test_corpus_pin_then_sync_roundtrip(tmp_path, monkeypatch):
    origen = tmp_path / "origen"
    origen.mkdir()
    (origen / "hecho.txt").write_bytes(b"hecho atomico")
    _git("init", "-q", cwd=origen); _git("add", ".", cwd=origen); _git("commit", "-qm", "1", cwd=origen)
    lock = tmp_path / "corpus.lock"
    assert pin_corpus(origen, repo="x/y", lock_path=lock)
    # sync clona desde una URL de GitHub; se redirige a la copia local sin red.
    real_run = subprocess.run
    def run(cmd, *a, **k):
        if cmd[:2] == ["git", "clone"]:
            cmd = ["git", "clone", str(origen), cmd[3]]
        return real_run(cmd, *a, **k)
    monkeypatch.setattr("tools.corpus.subprocess.run", run)
    destino = tmp_path / "destino"
    assert sync_corpus(destino, lock) is True
    (destino / "hecho.txt").write_bytes(b"hecho alterado")
    assert verify_corpus(destino, lock, verbose=False) is False


def test_brain_runtime_never_references_corpus():
    """4.4: el cerebro en ejecución (zeruel/) no lee ni escribe el corpus; solo tools/corpus.py lo toca."""
    raiz = Path(__file__).resolve().parents[1] / "zeruel"
    tocan = [p.name for p in raiz.rglob("*.py") if "corpus" in p.read_text(encoding="utf-8").lower()]
    assert tocan == []


def test_corpus_lock_schema():
    """2.4: la figura de corpus.lock: versión 1, repo, commit SHA-1, recuento coherente y SHA-256 por archivo."""
    import re
    lock = json.loads((Path(__file__).resolve().parents[1] / "corpus.lock").read_text(encoding="utf-8"))
    assert lock["version"] == 1 and re.fullmatch(r"[\w.-]+/[\w.-]+", lock["repo"])
    assert re.fullmatch(r"[0-9a-f]{40}", lock["commit"])
    assert lock["file_count"] == len(lock["files"]) > 0
    assert all(re.fullmatch(r"[0-9a-f]{64}", h) and not k.startswith(("/", "..")) for k, h in lock["files"].items())
