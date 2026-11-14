"""Offline copy/patch only: prepare the disabled private no-fire diagnosis.

Never invokes Python runners, imports Frida, starts roles or accesses game memory.
Private Original fixtures are copied, never published by this builder.
"""
import argparse,hashlib,json,os
from pathlib import Path
import shutil,subprocess

PARENT=Path('/srv/tse-a1-nosmooth-root-frozen-20261114')
LIBRARY=Path('/srv/tse-a1-input-trace-controller-20261114')
PARENT_MANIFEST_SHA='1f133437eee449e7b8356942dc749e9f226b36d4e42c84c4eb9e723fb30d4351'
PARENT_PINS={'run_dual.py':'8aa486237f59146c2debbf9bfd244b01f02bd5590ebeefe153b3f33046fd34c1',
 'colt_preparation.py':'a8b86fc863a9d3b06da7641df0744573b9de66a36af7f846b5a877fe1973d61e'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def refresh_manifest(root):
    root=Path(root).resolve(strict=True);manifest=json.loads((PARENT/'source-manifest.json').read_text())
    manifest.update(schema='a1-original-input-trace-disabled-v1',runtime_reviewed=False,
        runtime_performed=False,native_abi_qualified=False,input_cause_proven=False,
        gate='DISABLED_PENDING_MAIN_FREEZE_SMOKES_AND_FRESH_PREFLIGHT',
        scope='INHERITED_NOSMOOTH_CALIBRATION_TWO_FORWARD_ALIGNMENT_AND_AIM_NO_FIRE',
        collector_source=str(LIBRARY/'a1_original_input_collector.py'))
    manifest['runtime_dependencies']={str(root/Path(p).relative_to(PARENT))if Path(p).is_relative_to(PARENT)else p:d
        for p,d in manifest['runtime_dependencies'].items()}
    for p in list(manifest['runtime_dependencies']):
        if Path(p).is_relative_to(root):
            relative=str(Path(p).relative_to(root))
            if relative in ('run_dual.py','colt_preparation.py'):manifest['runtime_dependencies'][p]=sha(p)
            elif sha(p)!=manifest['runtime_dependencies'][p]:raise ValueError('copied inherited helper changed:'+relative)
    for name in('a1_input_worker.py','a1_trace_scope.py'):
        manifest['runtime_dependencies'][str(root/name)]=sha(root/name)
    library_manifest=json.loads((LIBRARY/'source-manifest.json').read_text())
    manifest['runtime_dependencies'].update(library_manifest['source_pins'])
    manifest['runtime_dependencies'][str(LIBRARY/'source-manifest.json')]=sha(LIBRARY/'source-manifest.json')
    manifest['diagnostic_source_sha256']={str(p.relative_to(root)):sha(p)for p in root.rglob('*')
        if p.is_file()and p.suffix in('.py','.js','.md','.ini')and '__pycache__'not in p.parts}
    manifest['trace_parent']={'path':str(PARENT),'source_pins':PARENT_PINS,
        'source_manifest_sha256':sha(PARENT/'source-manifest.json')}
    manifest['fixed_modes']=['instrumented-trace','uninstrumented-control']
    manifest['default_mode']='instrumented-trace'
    manifest['trace_supervision']={'fresh_subprocess':True,'frida_in_parent':False,
        'arm_ipc_deadline_seconds':3,'drain_and_before_input_ipc_deadline_seconds':.1,
        'close_ipc_deadline_seconds':2,'force_game_roles':False,
        'worker_termination_only_after_normal_role_close_and_fresh_quiescence':True}
    manifest['verification_boundary']='Offline only; Original hook method/control smoke, measured overhead, Root freeze and one bounded diagnosis pending. No A1 PASS.'
    (root/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def build(destination):
    destination=Path(destination).absolute()
    if destination.exists():raise ValueError('new private destination required')
    if sha(PARENT/'source-manifest.json')!=PARENT_MANIFEST_SHA:raise ValueError('frozen parent manifest changed')
    parent_manifest=json.loads((PARENT/'source-manifest.json').read_text())
    for source,digest in parent_manifest['runtime_dependencies'].items():
        if sha(source)!=digest:raise ValueError('inherited source/external pin changed:'+source)
    for name,digest in PARENT_PINS.items():
        if sha(PARENT/name)!=digest:raise ValueError('frozen parent changed:'+name)
    shutil.copytree(PARENT,destination,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    os.chmod(destination,0o700)
    repo=Path(__file__).resolve().parent.parent
    patch=repo/'docs/reports/a1-input-trace-20261114/controller.diff'
    subprocess.run(['/usr/bin/patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=destination,check=True,capture_output=True)
    for name in('a1_input_worker.py','a1_trace_scope.py'):shutil.copy2(repo/'tools'/name,destination/name)
    return refresh_manifest(destination)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    target=parser.parse_args().output;build(target)
    print(json.dumps({'prepared':str(target),'runtime_reviewed':False,'runtime_executed':False}))
