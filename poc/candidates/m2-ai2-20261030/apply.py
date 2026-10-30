#!/usr/bin/env python3
"""Materialize a new M2 source candidate over the existing pinned C1 composition."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
HERE=Path(__file__).resolve().parent
C1=HERE.parent/'combat-master-20261026'/'apply.py'
spec=importlib.util.spec_from_file_location('m2_c1_apply',C1)
c1=importlib.util.module_from_spec(spec);spec.loader.exec_module(c1)

def materialize(output,gamemp=False):
    output=Path(output).absolute()
    if output.exists() or output.is_symlink():raise ValueError('target exists; refusing overwrite')
    if not output.parent.is_dir():raise ValueError('output parent must exist')
    with tempfile.TemporaryDirectory(prefix='.m2-compose-',dir=output.parent) as temp:
        target=c1.materialize(Path(temp)/'source',gamemp)
        patches=['aim.patch','policy.patch']+(['driver.patch','ammo.patch'] if gamemp else [])
        for name in patches:
            subprocess.run(['patch','--batch','--fuzz=0','-p0','-i',str(HERE/name)],cwd=target,check=True,stdout=subprocess.DEVNULL)
        manifest=json.loads((target/'SOURCE_MANIFEST.json').read_text())
        manifest['m2_inputs_sha256']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['apply.py',*patches]}
        manifest['output_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(target.iterdir()) if p.is_file() and p.name!='SOURCE_MANIFEST.json'}
        (target/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
        if output.exists() or output.is_symlink():raise ValueError('target appeared; refusing overwrite')
        target.rename(output)
    return output
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--gamemp',action='store_true');p.add_argument('output',type=Path);a=p.parse_args()
    print(materialize(a.output,a.gamemp))
