"""Offline derivation of a disabled600s controller; never starts any runtime."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-a4-build020-hard-canonical-envelope-final-20261114')
PARENT_SHA='293c7d49e590e28164caf2db52660f144f14ebd32eca0c60fece40a5adc26de9'
UNCHANGED=dict(a4_fire_observer_v2_py='201ca2d0f3098637ffb129162d84e126062df24790cfa865693781683732e5fc',
              audit_a4_native_fire_observer_v2_py='3ac187c8775b2bd1ed7021dc7b4037b0eeda6aec2a0292f9d87e47c9d8f4b466')
UNCHANGED={name[:-3]+'.py':h for name,h in UNCHANGED.items()}
ADDITIONS=('a4_ordered_memory_v3.py','audit_a4_ordered_memory_v3.py','prepare_a4_ordered_memory_v3.py',
           'test_a4_ordered_memory_v3.py','test_prepare_a4_ordered_memory_v3.py','check_a4_ordered_archive_design.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(s,old,new):
 if s.count(old)!=1:raise ValueError('nonunique inherited anchor '+old)
 return s.replace(old,new,1)


def transform(s):
 s=once(s,'import a4_canonical_native_groups as canonical_groups','import a4_ordered_memory_v3 as canonical_groups')
 s=once(s,"PREFIX=f'ssam-a4-020-hard-groups-{map_key}-20261114'","PREFIX=f'ssam-a4-020-hard-ordered-{map_key}-20261114'")
 s=once(s,"E=BASE/f'a4-020-hard-groups-","E=BASE/f'a4-020-hard-ordered-")
 s=once(s,'inventory_stream=None;transaction=None','inventory_stream=None;attempt_stream=None;read_attempts=None;read_serial=0;transaction=None')
 s=once(s,"report['native_group_contract']=native_group_contract", "report['native_group_contract']=native_group_contract\n   report['memory_observation_contract']=canonical_groups.read_contract(native_group_contract)\n   (E/'memory-observation-contract.json').write_text(json.dumps(report['memory_observation_contract'],indent=2))")
 s=once(s,"inventory_stream=(E/'inventory.jsonl').open('w')", "inventory_stream=(E/'inventory.jsonl').open('w')\n    attempt_stream=(E/'read-attempts.jsonl').open('w');read_attempts=canonical_groups.AttemptJournal(attempt_stream)\n    report['inventory']['new_instrumentation']='global readserial, bounded attempt metadata journal and monotonic interval; overhead subject to unchanged host/gap gates'")
 old="     snap=inventory.sample(slots);assert snap['all_selected_present'];snap=canonical_groups.bind_sample(snap,group,native_group_contract);inventory_stream.write(json.dumps({'phase':'paused_smoke','group':group,'snapshot':snap})+'\\n')"
 new="""     read_serial+=1;sample_start=time.perf_counter();read_attempts.begin(read_serial,group,sample_start,'paused_smoke')
     try:snap=inventory.sample(slots)
     except BaseException as err:
      read_attempts.end(read_serial,time.perf_counter(),False,repr(err)[:256]);raise
     sample_end=time.perf_counter();read_attempts.end(read_serial,sample_end,True)
     assert snap['all_selected_present'];snap=canonical_groups.bind_sample(snap,group,native_group_contract,read_serial,sample_start,sample_end,'paused_smoke');inventory_stream.write(json.dumps({'phase':'paused_smoke','group':group,'snapshot':snap})+'\\n')"""
 s=once(s,old,new)
 s=once(s,'       sample_start=time.perf_counter()',"       read_serial+=1;sample_start=time.perf_counter();read_attempts.begin(read_serial,group,sample_start,'gameplay')")
 s=once(s,'        sampled=inventory.sample(slots)','        sampled=inventory.sample(slots)\n        sample_end=time.perf_counter()')
 s=once(s,'       except EvidenceError as err:\n', '       except EvidenceError as err:\n        read_attempts.end(read_serial,time.perf_counter(),False,repr(err)[:256])\n')
 s=once(s,"        report['inventory']['discarded_changed']+=1\n       else:","        report['inventory']['discarded_changed']+=1\n       except BaseException as err:\n        read_attempts.end(read_serial,time.perf_counter(),False,repr(err)[:256]);raise\n       else:\n        read_attempts.end(read_serial,sample_end,True)")
 s=once(s,'canonical_groups.bind_sample(sampled,group,native_group_contract)',
          'canonical_groups.bind_sample(sampled,group,native_group_contract,read_serial,sample_start,sample_end)')
 s=once(s,"native_registry['native_group_contract']=native_group_contract", "native_registry['native_group_contract']=native_group_contract\n      native_registry['memory_observation_contract']=canonical_groups.read_contract(native_group_contract)")
 s=once(s,'native_registry,server,native_group_contract)','native_registry,server,native_group_contract,read_attempts.records)')
 s=once(s,"('inventory_stream',inventory_stream)]", "('inventory_stream',inventory_stream),('attempt_stream',attempt_stream)]")
 s=once(s,"'a4_canonical_native_groups.py'):","'a4_canonical_native_groups.py','a4_ordered_memory_v3.py','audit_a4_ordered_memory_v3.py'):")
 ast.parse(s);return s


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('new destination required; previous packages remain immutable')
 assert sha(PARENT/'source-manifest.json')==PARENT_SHA
 parent=json.loads((PARENT/'source-manifest.json').read_text())
 for p,h in parent['runtime_dependencies'].items():assert sha(p)==h,('parent runtime pin',p)
 for name,h in parent['sources'].items():assert sha(PARENT/name)==h,('parent source pin',name)
 for name,h in UNCHANGED.items():assert sha(PARENT/name)==h
 assert parent['runtime_reviewed']is False
 old=(PARENT/'run-a4.py').read_text();s=transform(old)
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 tools=Path(__file__).resolve().parent
 for name in ADDITIONS:shutil.copy2(tools/name,dest/name)
 (dest/'run-a4.py').write_text(s)
 fixture=(PARENT/'test_a4_hard_maps.py').read_text()
 fixture=once(fixture,"'canonical_groups.bind_sample(sampled,group,native_group_contract)'", "'canonical_groups.bind_sample(sampled,group,native_group_contract,read_serial,sample_start,sample_end)'")
 (dest/'test_a4_hard_maps.py').write_text(fixture)
 (dest/'ordered-runtime.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='canonical-parent/run-a4.py',tofile='ordered-disabled/run-a4.py')))
 deps={}
 for p,h in parent['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 for name in ADDITIONS[:2]:deps[str(dest/name)]=sha(dest/name)
 m=json.loads(json.dumps(parent));m['inherited_ordered_parent_metadata']=dict(scope=m['scope'],derivation=m['derivation'],sources=m['sources'],draft_source_sha256=m['draft_source_sha256'],root_review=m['root_review'])
 m.update(scope='DISABLED_BUILD020_HARD_SINGLE_MAP600S_ORDERED_MEMORY_FLAGS_V3',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=dict(sorted(deps.items())))
 m['derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,independent_review='PENDING',native_started=False,frida_used=False,duration_seconds=600,diagnostics=0,hard_difficulty=2,old_v2_sha256=UNCHANGED)
 m['read_contract']=dict(type='ordered_memory_observations_not_simulation_snapshots',max_attempts=100000,max_metadata_lines=200000,max_journal_bytes=67108864,atomic_snapshot=False,weapon_function_call_proven=False,overhead='new serial/journal/clock instrumentation; unchanged host and gap gates apply')
 m['root_review']=dict(approved_for_private_a4=False,reference='PENDING independent review, Root freeze and preflight')
 m['sources']={p.name:sha(p)for p in dest.iterdir()if p.is_file()and p.name not in('source-manifest.json','HANDOFF-disabled.json')}
 m['draft_source_sha256']={p.name:sha(p)for p in dest.glob('*.py')}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(dict(runtime_authorized=False,native_started=False,qualified=False,functional_pass=False,source_manifest_sha256=sha(dest/'source-manifest.json'),next='independent review then Root freeze/preflight; one prospective600s window, no auto retry'),indent=2)+'\n')
 return dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(deps),native_started=False)


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
