"""Download public OCR assets only. No image, text or credentials leave the device."""
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'extension' / 'vendor'
PACKAGES = {
    'tesseract.js': ('7.0.0', ['dist/tesseract.min.js', 'dist/worker.min.js', 'dist/tesseract.min.js.LICENSE.txt', 'dist/worker.min.js.LICENSE.txt', 'LICENSE.md']),
    'tesseract.js-core': ('7.0.0', ['tesseract-core-lstm.wasm.js', 'tesseract-core-lstm.wasm', 'LICENSE']),
}


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def main():
    DEST.mkdir(exist_ok=True)
    manifest = {}
    for name, (version, files) in PACKAGES.items():
        metadata = json.loads(fetch(f'https://registry.npmjs.org/{name}/{version}'))
        dist = metadata['dist']
        if not dist['tarball'].startswith(f'https://registry.npmjs.org/{name}/-/'):
            raise ValueError('Unexpected package source')
        archive = fetch(dist['tarball'])
        expected = 'sha512-' + base64.b64encode(hashlib.sha512(archive).digest()).decode()
        if dist['integrity'] != expected:
            raise ValueError('Package integrity mismatch')
        with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as package:
            for relative in files:
                member = package.getmember('package/' + relative)
                if not member.isfile():
                    raise ValueError('Not a regular asset')
                data = package.extractfile(member).read()
                target = DEST / (f'{name}-LICENSE' if relative.startswith('LICENSE') else Path(relative).name)
                target.write_bytes(data)
                manifest[target.name] = {'source': dist['tarball'], 'version': version, 'sha256': hashlib.sha256(data).hexdigest()}
    # Immutable public language revision. No downloads at recognition time.
    commit = '87416418657359cb625c412a48b6e1d6d41c29bd'
    for name in ['spa.traineddata', 'LICENSE']:
        url = f'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/{commit}/{name}'
        data = fetch(url)
        expected_hash = {'spa.traineddata': '6f2e04d02774a18f01bed44b1111f2cd7f3ba7ac9dc4373cd3f898a40ea6b464', 'LICENSE': 'cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30'}[name]
        if hashlib.sha256(data).hexdigest() != expected_hash:
            raise ValueError('Language asset integrity mismatch')
        target = DEST / ('tessdata-LICENSE' if name == 'LICENSE' else name)
        target.write_bytes(data)
        manifest[target.name] = {'source': url, 'revision': commit, 'sha256': hashlib.sha256(data).hexdigest()}
    (DEST / 'assets.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'OCR assets prepared locally: {sum(p.stat().st_size for p in DEST.iterdir() if p.is_file()) / 1048576:.1f} MB')


if __name__ == '__main__':
    main()
