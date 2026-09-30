"""Install only the pinned official Antigravity CLI (agy) binary, with SHA-512 integrity check."""

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import tempfile
import urllib.request

VERSION = "1.2.14"
# Versioned, immutable artifact from Google's official release manifest (linux_amd64), checked 30/09/2026.
URL = (
    "https://storage.googleapis.com/antigravity-public/antigravity-cli/"
    "1.2.14-4571742832820224/linux-x64/cli_linux_x64.tar.gz"
)
SHA512 = (
    "fd771dfc74ddd07b61c8b0a6fd7a238f53a3a098a51052583a01d97ab84ee60d"
    "b741ce5f041e87a9da3c1a9aabe95b053113374437df1e231773552781edaf09"
)


def install(destination, url=URL, expected=SHA512, opener=urllib.request.urlopen):
    destination = destination.resolve()
    if destination.exists():
        raise ValueError("Destination already exists; choose a fresh directory.")
    if not url.startswith(
        "https://storage.googleapis.com/antigravity-public/antigravity-cli/"
    ):
        raise ValueError("Unexpected package origin")
    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / "agy.tar.gz"
        digest = hashlib.sha512()
        size = 0
        with opener(url, timeout=120) as response, archive.open("wb") as out:
            while chunk := response.read(256 * 1024):
                size += len(chunk)
                if size > 400 * 1024 * 1024:
                    raise ValueError("Unexpected archive size")
                digest.update(chunk)
                out.write(chunk)
        if digest.hexdigest() != expected:
            raise ValueError("Package integrity check failed")
        with tarfile.open(archive) as package:
            member = package.getmember("antigravity")
            if not member.isfile():
                raise ValueError("Unexpected archive layout")
            destination.mkdir(parents=True)
            package.extract(member, destination, filter="data")
        binary = destination / "agy"
        (destination / "antigravity").rename(binary)
        binary.chmod(0o755)
    print(
        json.dumps(
            {
                "installed": VERSION,
                "sha512_verified": True,
                "archive_bytes": size,
                "binary": str(binary),
            }
        )
    )
    return binary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    install(parser.parse_args().destination)
