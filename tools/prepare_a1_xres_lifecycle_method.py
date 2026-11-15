"""Prepare one DISABLED own167 lifecycle method; never execute native helpers."""
import argparse
import json
from pathlib import Path
import shutil
from prepare_a1_xres_attribution import SOURCE,PARENT,PARENT_SHA,PID_PARENT,PID_PARENT_SHA,PID_RESULT_SHA,CORE_FILES,ADAPTER_FILES,TEST_FILES,copy_dependencies,verify_parents,package_fingerprints,write,sha


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh disabled method destination required')
 old,cm,pm=verify_parents();dest.mkdir(mode=0o700);copy_dependencies(dest)
 for name in('a1_passive_xrecord.py','a1_passive_xrecord_worker.py','a1_passive_xrecord_evidence.py'):
  shutil.copy2(PARENT/name,dest/name)
  if name!='a1_passive_xrecord_evidence.py':
   path=dest/name;path.write_text(path.read_text().replace('RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False',1))
 shutil.copytree(PARENT/'passive-core',dest/'passive-core',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 from a1_xres_lifecycle_method import LIMITS
 runtime={str(p):sha(p)for p in dest.rglob('*.py')}
 m=dict(schema='OWN_XRES_RECORD_LIFECYCLE_METHOD_V1',runtime_reviewed=False,runtime_enabled=False,limits=LIMITS,abi_layout=pm['abi_layout'],library_sha256=pm['library_sha256'],header_sha256=pm['header_sha256'],evidence_sha256=pm['evidence_sha256'],runtime_dependencies=runtime,xres_attribution=dict(allowed_scope='OWN_METHOD_167',abi_layout=pm['abi_layout'],library_sha256=pm['library_sha256']),parent_manifest_sha256=PARENT_SHA,pid_parent_manifest_sha256=PID_PARENT_SHA,pid_method_result_sha256=PID_RESULT_SHA,qualified=False,a1_pass=False,gain_fixed=False,old_u_attributed=False,root_prerequisites=['source/pin/input-free review','all project locks plus fresh own167 lock','fresh display/socket/PID/namespace/disk preflight','backup/exclusive bounded window','one Root method only; no automatic retry'])
 write(dest/'source-manifest.json',m)
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(runtime),library_pins=len(m['library_sha256']),header_pins=len(m['header_sha256']),evidence_pins=len(m['evidence_sha256']),fingerprints=package_fingerprints(dest),runtime_reviewed=False,native_performed=False,qualified=False)
 write(dest/'METHOD-HANDOFF.json',receipt)
 for p in dest.rglob('*'):
  if p.is_file():p.chmod(0o600)
 return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);print(json.dumps(prepare(p.parse_args().destination),indent=2))
