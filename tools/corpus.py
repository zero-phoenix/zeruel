#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/corpus.py: Sincronización, verificación e inmutabilidad del Apéndice Acéfalo.

Gobierna el desacoplamiento estricto entre el Cerebro (zero-phoenix/zeruel)
y el Apéndice Acéfalo de hechos (zero-phoenix/zeruel-corpus), garantizando
reproducibilidad criptográfica mediante corpus.lock y verificación SHA-256.
"""

import os
import sys
import json
import hashlib
import argparse
import subprocess
from pathlib import Path

DEFAULT_LOCK_PATH = Path(__file__).resolve().parent.parent / "corpus.lock"
DEFAULT_CORPUS_DIR = Path.home() / ".zeruel-private" / "corpus"


def get_corpus_root() -> Path:
    """Retorna la ruta al directorio raíz local del corpus sincronizado."""
    env_path = os.environ.get("ZERUEL_CORPUS_DIR")
    if env_path:
        return Path(env_path).resolve()
    return DEFAULT_CORPUS_DIR.resolve()


def sha256_file(filepath: Path) -> str:
    """Calcula el hash SHA-256 de un archivo en bloques de 64 KB."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def load_lock(lock_path: Path = DEFAULT_LOCK_PATH) -> dict:
    """Carga y valida el archivo corpus.lock."""
    if not lock_path.exists():
        raise FileNotFoundError(f"No se encontró corpus.lock en: {lock_path}")
    with open(lock_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "commit" not in data or "files" not in data:
        raise ValueError(
            "corpus.lock inválido: faltan campos obligatorios 'commit' o 'files'"
        )
    return data


def verify_corpus(
    corpus_dir: Path = None, lock_path: Path = DEFAULT_LOCK_PATH, verbose: bool = True
) -> bool:
    """Verifica criptográficamente que cada archivo del corpus coincida con corpus.lock."""
    if corpus_dir is None:
        corpus_dir = get_corpus_root()

    lock_data = load_lock(lock_path)
    expected_files = lock_data["files"]
    commit = lock_data.get("commit", "desconocido")
    repo = lock_data.get("repo", "zero-phoenix/zeruel-corpus")

    if verbose:
        print("=== VERIFICACIÓN CRIPTOGRÁFICA DEL CORPUS ACÉFALO ===")
        print(f"Directorio local: {corpus_dir}")
        print(f"Repositorio:      {repo}")
        print(f"Commit fijado:    {commit}")
        print(f"Total archivos:   {len(expected_files)}")

    errors = []
    checked_count = 0

    for rel_path, expected_hash in sorted(expected_files.items()):
        full_path = corpus_dir / rel_path
        if not full_path.exists():
            errors.append(f"FALTANTE: {rel_path} no existe en {corpus_dir}")
            continue

        actual_hash = sha256_file(full_path)
        if actual_hash != expected_hash:
            errors.append(
                f"CORRUPTO: {rel_path}\n"
                f"  Esperado: {expected_hash}\n"
                f"  Actual:   {actual_hash}"
            )
        else:
            checked_count += 1

    # Popper: también refutan la integridad un recuento distinto, archivos de más y otro commit.
    if "file_count" in lock_data and lock_data["file_count"] != len(expected_files):
        errors.append(
            f"RECUENTO: file_count={lock_data['file_count']} pero el lock lista {len(expected_files)}"
        )
    lock_resuelto = Path(lock_path).resolve()
    for root, dirs, filenames in os.walk(corpus_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for fname in filenames:
            fpath = Path(root) / fname
            if fpath.resolve() == lock_resuelto:
                continue
            rel = fpath.relative_to(corpus_dir).as_posix()
            if rel not in expected_files:
                errors.append(f"SOBRANTE: {rel} no figura en corpus.lock")
    if (Path(corpus_dir) / ".git").exists():
        head = subprocess.run(
            ["git", "-C", str(corpus_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
        if head.returncode != 0 or head.stdout.strip() != commit:
            errors.append(
                f"COMMIT: HEAD={head.stdout.strip() or '?'} distinto del fijado {commit}"
            )

    if errors:
        print(
            f"\n[ERROR] Falló la verificación de integridad ({len(errors)} incidencias):"
        )
        for err in errors:
            print(f"  - {err}")
        return False

    if verbose:
        print(
            f"\n[OK] Verificación exitosa: {checked_count}/{len(expected_files)} archivos íntegros."
        )
    return True


def sync_corpus(target_dir: Path = None, lock_path: Path = DEFAULT_LOCK_PATH) -> bool:
    """Clona o actualiza el corpus al commit fijado en corpus.lock y valida integridad."""
    if target_dir is None:
        target_dir = get_corpus_root()

    lock_data = load_lock(lock_path)
    repo = lock_data.get("repo", "zero-phoenix/zeruel-corpus")
    commit = lock_data["commit"]
    repo_url = f"https://github.com/{repo}.git"

    target_dir.parent.mkdir(parents=True, exist_ok=True)

    if not (target_dir / ".git").exists():
        print(f"Clonando {repo_url} en {target_dir}...")
        res = subprocess.run(
            ["git", "clone", repo_url, str(target_dir)], capture_output=True, text=True
        )
        if res.returncode != 0:
            # Reintentar vía gh CLI si git HTTPS directo requiere auth
            print("Intento con git clone falló, usando gh repo clone...")
            res_gh = subprocess.run(
                ["gh", "repo", "clone", repo, str(target_dir)],
                capture_output=True,
                text=True,
            )
            if res_gh.returncode != 0:
                print(
                    f"[ERROR] No se pudo clonar el corpus:\n{res.stderr}\n{res_gh.stderr}"
                )
                return False
    else:
        print(f"Actualizando repositorio existente en {target_dir}...")
        subprocess.run(["git", "-C", str(target_dir), "fetch", "origin"], check=True)

    print(f"Fijando commit {commit} en {target_dir}...")
    res_co = subprocess.run(
        ["git", "-C", str(target_dir), "checkout", "--detach", commit],
        capture_output=True,
        text=True,
    )
    if res_co.returncode != 0:
        print(
            f"[ERROR] No se pudo hacer checkout del commit {commit}:\n{res_co.stderr}"
        )
        return False

    return verify_corpus(corpus_dir=target_dir, lock_path=lock_path, verbose=True)


def pin_corpus(
    source_dir: Path,
    repo: str = "zero-phoenix/zeruel-corpus",
    commit: str = None,
    lock_path: Path = DEFAULT_LOCK_PATH,
) -> bool:
    """Genera o actualiza corpus.lock con los hashes SHA-256 de los archivos en source_dir."""
    source_dir = Path(source_dir).resolve()
    if not source_dir.exists():
        raise FileNotFoundError(f"Directorio fuente no existe: {source_dir}")

    if not commit:
        # Intentar obtener commit git de source_dir
        res = subprocess.run(
            ["git", "-C", str(source_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            commit = res.stdout.strip()
        else:
            raise ValueError(
                "No se especificó commit y source_dir no es un repositorio git válido."
            )

    files_map = {}
    for root, _, filenames in os.walk(source_dir):
        # Excluir .git
        rel_root = Path(root).relative_to(source_dir)
        if any(part == ".git" for part in rel_root.parts):
            continue

        for fname in sorted(filenames):
            fpath = Path(root) / fname
            rel_path = (rel_root / fname).as_posix()
            if rel_path.startswith("./"):
                rel_path = rel_path[2:]
            files_map[rel_path] = sha256_file(fpath)

    lock_payload = {
        "version": 1,
        "repo": repo,
        "commit": commit,
        "file_count": len(files_map),
        "files": dict(sorted(files_map.items())),
    }

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w", encoding="utf-8") as f:
        json.dump(lock_payload, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(
        f"[OK] corpus.lock generado exitosamente en {lock_path} ({len(files_map)} archivos fijados en commit {commit})."
    )
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Gestor de integridad y sincronización del Corpus Acéfalo de Zeruel."
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcomando sync
    sync_p = subparsers.add_parser(
        "sync", help="Sincroniza y clona el corpus al commit fijado en corpus.lock."
    )
    sync_p.add_argument(
        "--target",
        type=Path,
        default=None,
        help="Directorio destino (default: %USERPROFILE%/.zeruel-private/corpus)",
    )
    sync_p.add_argument(
        "--lock",
        type=Path,
        default=DEFAULT_LOCK_PATH,
        help="Ruta al archivo corpus.lock",
    )

    # Subcomando verify
    verify_p = subparsers.add_parser(
        "verify", help="Verifica integridad criptográfica SHA-256 contra corpus.lock."
    )
    verify_p.add_argument(
        "--corpus-dir", type=Path, default=None, help="Directorio a verificar"
    )
    verify_p.add_argument(
        "--lock",
        type=Path,
        default=DEFAULT_LOCK_PATH,
        help="Ruta al archivo corpus.lock",
    )

    # Subcomando pin
    pin_p = subparsers.add_parser(
        "pin", help="Genera corpus.lock escaneando un directorio y fijando hashes."
    )
    pin_p.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Directorio fuente de datos del corpus",
    )
    pin_p.add_argument(
        "--repo",
        type=str,
        default="zero-phoenix/zeruel-corpus",
        help="Nombre del repositorio GitHub",
    )
    pin_p.add_argument("--commit", type=str, default=None, help="Commit SHA fijado")
    pin_p.add_argument(
        "--lock",
        type=Path,
        default=DEFAULT_LOCK_PATH,
        help="Ruta al archivo corpus.lock de salida",
    )

    args = parser.parse_args()

    if args.subcommand == "sync":
        ok = sync_corpus(target_dir=args.target, lock_path=args.lock)
        sys.exit(0 if ok else 1)
    elif args.subcommand == "verify":
        ok = verify_corpus(corpus_dir=args.corpus_dir, lock_path=args.lock)
        sys.exit(0 if ok else 1)
    elif args.subcommand == "pin":
        ok = pin_corpus(
            source_dir=args.source,
            repo=args.repo,
            commit=args.commit,
            lock_path=args.lock,
        )
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
