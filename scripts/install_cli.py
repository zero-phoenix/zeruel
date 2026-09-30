"""Install only the pinned official standalone npm bundle, with integrity check."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import tarfile
import tempfile
import urllib.request

VERSION = "0.62.0"


def install(destination):
    destination = destination.resolve()
    if destination.exists():
        raise ValueError("Destination already exists; choose a fresh directory.")
    with urllib.request.urlopen(
        f"https://registry.npmjs.org/@google%2fgemini-cli/{VERSION}", timeout=30
    ) as response:
        metadata = json.load(response)
    distribution = metadata["dist"]
    url = distribution["tarball"]
    if not url.startswith("https://registry.npmjs.org/@google/gemini-cli/-/"):
        raise ValueError("Unexpected package origin")
    algorithm, expected = distribution["integrity"].split("-", 1)
    if algorithm != "sha512":
        raise ValueError("Expected SHA-512 integrity metadata")
    with tempfile.TemporaryDirectory() as temp:
        archive = Path(temp) / "cli.tgz"
        digest = hashlib.sha512()
        size = 0
        with urllib.request.urlopen(url, timeout=60) as response, archive.open("wb") as out:
            while chunk := response.read(256 * 1024):
                size += len(chunk)
                if size > 150 * 1024 * 1024:
                    raise ValueError("Unexpected archive size")
                digest.update(chunk)
                out.write(chunk)
        if base64.b64encode(digest.digest()).decode() != expected:
            raise ValueError("Package integrity check failed")
        destination.mkdir(parents=True)
        with tarfile.open(archive) as package:
            package.extractall(destination, filter="data")
    print(json.dumps({"installed": VERSION, "sha512_verified": True,
                      "archive_bytes": size, "destination": str(destination)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    install(parser.parse_args().destination)
