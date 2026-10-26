#!/usr/bin/env python3
"""Read another candidate's applier, build its headers in C2-owned scratch only."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--combat-applier',type=Path,required=True)
    args=parser.parse_args()
    applier=args.combat_applier.resolve()
    spec=importlib.util.spec_from_file_location('c1_apply',applier)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    target=HERE/'.build/c1-cross'
    if target.is_symlink() or (HERE/'.build').is_symlink():
        raise RuntimeError('symlinked C2 scratch refused')
    if target.exists(): shutil.rmtree(target)
    (target/'poc').mkdir(parents=True)
    source=HERE/'.build/upstream/poc'
    for tree in ('navigation-lab','research/item-utility/include','research/nav-item-bridge/include'):
        shutil.copytree(source/tree,target/'poc'/tree,ignore=shutil.ignore_patterns('build','*.o','__pycache__'))
    module.materialize(target/'poc/botcore',gamemp=False)
    manifest=json.loads((target/'poc/botcore/SOURCE_MANIFEST.json').read_text())
    (HERE/'.build/c1-cross-manifest.json').write_text(json.dumps({'applier_sha256':hashlib.sha256(applier.read_bytes()).hexdigest(),'combat':manifest},indent=2)+'\n')
    for name in ('test_regressions','test_controller','test_c1_ownership'):
        output=target/name
        subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',
            '-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM','-I'+str(HERE),
            '-I'+str(target/'poc/research/nav-item-bridge/include'),
            str(HERE/'tests'/str(name+'.cpp')),'-o',str(output)],check=True)
        subprocess.run([str(output)],check=True)
    print('PASS C1/C2 scratch cross-build; baseline upstream tree unchanged')
if __name__=='__main__': main()
