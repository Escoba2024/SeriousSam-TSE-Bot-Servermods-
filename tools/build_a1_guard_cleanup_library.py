"""Prepare only a new disabled library; no Frida import, attach or game start."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import build_a1_input_guards

PARENT=Path('/srv/tse-a1-input-trace-timer-guard-library-20261114')
PARENT_SHA='2e2a7981ee349eda407983746bc22787bb273b34b75aa0a057122f454b12f3ea'
ORIGINALS=Path('/srv/tse-a1-colt-pitch-analysis-20261112/evidence/static-originals')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def prepare(destination):
 dest=Path(destination).resolve();tools=Path(__file__).resolve().parent
 if dest.exists():raise ValueError('new destination required; old packages immutable')
 assert sha(PARENT/'source-manifest.json')==PARENT_SHA
 m=json.loads((PARENT/'source-manifest.json').read_text());pins={}
 authored=tools.resolve()
 for p,h in m['source_pins'].items():
  path=Path(p)
  if path.parent==authored:
   # The historical authored files are intentionally being revised. Their old
   # byte-identical copies remain verified inside the immutable parent library.
   assert sha(PARENT/path.name)==h
   continue
  assert sha(path)==h,('unchanged parent/external pin',p)
  if not path.is_relative_to(PARENT):pins[p]=h
 dest.mkdir(mode=0o700)
 for name in ('a1_original_input_collector.py','a1_original_input_readonly.js','a1_input_worker.py'):
  raw=(tools/name).read_text()
  if name=='a1_original_input_collector.py':
   expected="PRIVATE = Path('/srv/tse-a1-input-trace-guard-cleanup-library-20261114')"
   assert raw.count(expected)==1
   raw=raw.replace(expected,'PRIVATE = Path('+repr(str(dest))+')')
  (dest/name).write_text(raw)
  pins[str(dest/name)]=sha(dest/name)
  pins[str(tools/name)]=sha(tools/name)
 guard=build_a1_input_guards.generate(ORIGINALS,dest/'original-input-guards.json')
 assert guard['sha256']=='3d2b237a787869fee27b02ac22a84f5bdf4e3528e8e2fee2981f05d3e8d7e9d1'
 pins[str(dest/'original-input-guards.json')]=sha(dest/'original-input-guards.json')
 m.update(schema='a1-original-input-guard-cleanup-disabled-v2',runtime_reviewed=False,
          native_abi_qualified=False,source_pins=dict(sorted(pins.items())),
          original_guards_sha256=guard['sha256'],no_runtime_executed=True)
 m['timer_guard_extension']=dict(parent_manifest_sha256=PARENT_SHA,new_hook_sites=0,new_inputs=0,
     bounds_changed=False,actual_branch_proven=False,caller_register_binding_proven=False,
     static_generator=str(tools/'build_a1_input_guards.py'),
     static_generator_sha256=sha(tools/'build_a1_input_guards.py'),guard_ranges=10,
     game_binding='ARM global and lifetime; EDI diagnostic per callback only')
 m['cleanup_receipt_extension']=dict(actual_full_original_flag=True,
     sticky_errors_preserved=True,journal_before_stream_close=True,
     outer_worker_must_be_replaced_and_runtime_pinned=True,
     worker_path=str(dest/'a1_input_worker.py'),worker_sha256=sha(dest/'a1_input_worker.py'))
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for p,h in m['source_pins'].items():assert sha(p)==h,p
 return dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),
             pins=len(pins),runtime_reviewed=False,native_started=False)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(parser.parse_args().destination),indent=2))
