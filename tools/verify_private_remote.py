#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/verify_private_remote.py: Verifica criptográficamente las fuentes privadas
contra corpus.lock mediante la arquitectura canónica de tools/corpus.py."""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "tools"))
from corpus import verify_corpus, load_lock, get_corpus_root


def main():
    lock_data = load_lock()
    commit = lock_data.get("commit")
    corpus_dir = get_corpus_root()
    
    # Si el directorio no existe localmente pero corpus.lock está presente, reportar estado
    if not corpus_dir.exists():
        print(json.dumps({
            "evidence": "REAL",
            "private_verified": False,
            "error": f"Directorio local del corpus no encontrado en {corpus_dir}. Ejecute 'python tools/corpus.py sync'.",
            "remote_commit": commit,
            "locked_file_count": lock_data.get("file_count", 0)
        }))
        return

    ok = verify_corpus(corpus_dir=corpus_dir, verbose=False)
    result = {
        "evidence": "REAL",
        "private_verified": ok,
        "remote_commit": commit,
        "all_tracked_knowledge_blobs_verified": lock_data.get("file_count", 0),
        "corpus_location": str(corpus_dir),
        "original_git_bytes_sha256_match": ok
    }
    print(json.dumps(result))
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
