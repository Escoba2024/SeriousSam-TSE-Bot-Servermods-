#!/usr/bin/env python3
"""Materialize source-only pinned upstreams inside this candidate; never deploy."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DEST = HERE / '.build' / 'upstream'

def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])

def prepare(patched=True):
    # Fixed candidate-owned path: callers cannot point cleanup at a runtime tree.
    if DEST.is_symlink() or (HERE / '.build').is_symlink():
        raise RuntimeError('refusing symlinked candidate build directory')
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    pins = json.loads((HERE / 'pins.json').read_text())
    manifest = {'patched': patched, 'trees': pins, 'files': {}}
    for pin in pins:
        tree = git('rev-parse', pin['commit'] + ':' + pin['path']).decode().strip()
        if tree != pin['tree']:
            raise RuntimeError('pinned Git tree mismatch: ' + pin['path'])
        with tarfile.open(fileobj=io.BytesIO(git('archive', pin['commit'], pin['path']))) as archive:
            for member in archive:
                path = Path(member.name)
                if path.is_absolute() or '..' in path.parts or not (member.isdir() or member.isfile()):
                    raise RuntimeError('unexpected archive entry: ' + member.name)
                out = DEST / path
                if member.isdir():
                    out.mkdir(parents=True, exist_ok=True)
                else:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(archive.extractfile(member).read())
                    out.chmod(member.mode & 0o777)
    if patched:
        subprocess.run(['patch', '--batch', '--fuzz=0', '--no-backup-if-mismatch',
                        '-p1', '-d', str(DEST), '-i', str(HERE / 'integration.patch')], check=True)
    # Mirrors are deliberately absent: REQUIRE_UPSTREAM cannot silently fall back.
    if patched:
        shutil.rmtree(DEST / 'poc/research/nav-item-bridge/include/upstream')
    for path in sorted(DEST.rglob('*')):
        if path.is_file():
            manifest['files'][str(path.relative_to(DEST))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (HERE / '.build' / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('prepared patched=' + str(patched) + ' at ' + str(DEST))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', action='store_true', help='unpatched upstream for regression reproduction')
    args = parser.parse_args()
    prepare(not args.original)
