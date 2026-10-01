"""Verify all tracked archive blobs match a complete private GitHub commit tree."""
import hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def api(endpoint):
    return json.loads(subprocess.check_output(['gh','api',endpoint],encoding='utf-8'))
def verify_original_git_bytes():
    manifest = json.loads((ROOT/'knowledge/private_sources/manifest.json').read_text(encoding='utf-8'))
    entries = git('ls-files','--stage','-z','knowledge/private_sources').split(b'\0')
    ids = {}
    for entry in entries:
        if entry:
            header,name = entry.split(b'\t',1)
            ids[name.decode('utf-8')] = header.split()[1].decode()
    process = subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    process.stdin.write(('\n'.join(ids[x['repository_path']] for x in manifest['files'])+'\n').encode())
    process.stdin.close()
    for item in manifest['files']:
        header = process.stdout.readline().split()
        remaining = int(header[2])
        h = hashlib.sha256()
        while remaining:
            block = process.stdout.read(min(remaining,1024*1024))
            if not block: raise ValueError('Incomplete Git blob')
            h.update(block); remaining -= len(block)
        process.stdout.read(1)
        if h.hexdigest()!=item['sha256']: raise ValueError('Original bytes altered by Git')
    if process.wait()!=0: raise ValueError('Git validation failed')
    return manifest
def main():
    if not api('repos/zero-phoenix/zeruel')['private']: raise SystemExit('PRIVATE required')
    head = git('rev-parse','HEAD').decode().strip()
    tree = api(f'repos/zero-phoenix/zeruel/git/trees/{head}?recursive=1')
    if tree.get('truncated'): raise ValueError('Incomplete remote inventory')
    remote = {x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'}
    local = {}
    for entry in git('ls-files','--stage','-z','knowledge').split(b'\0'):
        if not entry: continue
        header,name = entry.split(b'\t',1)
        local[name.decode('utf-8')] = header.split()[1].decode()
    if not local: raise ValueError('Empty archive')
    if any(remote.get(name)!=sha for name,sha in local.items()):
        raise ValueError('Remote archive mismatch')
    manifest = verify_original_git_bytes()
    if any(x['repository_path'] not in local for x in manifest['files']):
        raise ValueError('Original missing from Git index')
    result = {'evidence':'REAL','private_verified':True,'remote_commit':head,
              'all_tracked_knowledge_blobs_verified':len(local),
              'original_files_verified_remote':len(manifest['files']), 'original_git_bytes_sha256_match':True,
              'tree_truncated':False}
    print(json.dumps(result))
    (ROOT/'knowledge/verification-remote.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__': main()
