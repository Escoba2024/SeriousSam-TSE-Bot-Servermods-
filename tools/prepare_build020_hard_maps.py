"""Offline derivation of the pinned single-map600s controller. Never launches it."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-combat-a4-build013-preflight-draft-20261112')
BUILD=Path('/srv/tse-milestone-a-build-020-20261114')
V2=Path('/srv/tse-a4-fire020-v2-controller-20261114')
PARENT_SHA='ab364a9a4107686a66c5f94b3e90a6406033084ec48cac789afc1b2b525278f9'
V2_SHA='86662c479b4a0928ba140fc8437ac7ea8f8683a9145dc9e69204606aa316329f'
BUILD_SHA='3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6'
DLL='094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0'
OLD_DLL='3a8d84c9c04e4839ee08d5d8ec879c37f25265df267c03e966ec869754a81f93'
SOURCE='e5f7a65502fbea683014ef8fcc95ecdd2a927b6a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def once(text,old,new):
 if text.count(old)!=1:raise ValueError('nonunique inherited anchor '+old)
 return text.replace(old,new,1)

def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('new destination required; existing packages immutable')
 assert sha(PARENT/'source-manifest.json')==PARENT_SHA
 parent=json.loads((PARENT/'source-manifest.json').read_text())
 for p,h in parent['runtime_dependencies'].items():assert sha(p)==h,('parent runtime pin',p)
 assert sha(V2/'source-manifest.json')==V2_SHA
 vm=json.loads((V2/'source-manifest.json').read_text())
 assert sha(BUILD/'manifest.json')==BUILD_SHA
 build=json.loads((BUILD/'manifest.json').read_text())
 assert build['build_ok']is True and build['qualified']is False and build['repo_commit']==SOURCE
 assert sha(BUILD/'Sources/Game/GameMP.dll')==build['dll_sha256']==DLL
 for key,base in [('source_sha256',BUILD/'Sources/Game'),('overlay_sha256',BUILD/'overlay')]:
  for p,h in build[key].items():assert sha(base/p)==h,('build source pin',p)
 tools=Path(__file__).resolve().parent
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 # Existing policies remain byte-identical. Pin copies directly to reviewed V2 runtime dependencies.
 copied=['a4_fire_observer_v2.py','audit_a4_native_fire_observer_v2.py','reset_policy.py',
         'test_a4_fire_observer_v2.py','test_audit_a4_native_fire_observer_v2.py']
 for n in copied:
  if str(V2/n)in vm['runtime_dependencies']:assert sha(V2/n)==vm['runtime_dependencies'][str(V2/n)]
  else:assert sha(V2/n)==vm['sources'][n],('V2 source',n)
  shutil.copy2(V2/n,dest/n)
 for n in ('a4_hard_map_policy.py','test_a4_hard_maps.py','stability_hard_rules.py','test_stability_hard_rules.py'):
  shutil.copy2(tools/n,dest/n)
 old=(PARENT/'run-a4.py').read_text();s=old
 s=once(s,'import adapter_policy as policy','import adapter_policy as policy\nimport a4_hard_map_policy as hardmap\nimport stability_hard_rules as hard_rules\nimport a4_fire_observer_v2 as native_fire\nimport reset_policy as rotation')
 for a,b in [('/srv/tse-milestone-a-build-013-20261111',str(BUILD)),('ssam-a4-013-{map_key}-20261112','ssam-a4-020-hard-{map_key}-20261114'),("E=BASE/f'a4-013-","E=BASE/f'a4-020-hard-"),('PRIVATE A4 013','PRIVATE A4 020 HARD'),('candidate013 normal gameplay','candidate020 Hard normal gameplay'),('gam_iStartDifficulty=3;','gam_iStartDifficulty=2;'),('default=120','default=600')]:s=once(s,a,b)
 s=once(s,'policy.options(map_key,duration,diag);','policy.options(map_key,duration,diag);hardmap.options(map_key,duration,diag,policy.prepared.catalog()[\'maps\']);')
 s=once(s,"(directory/'preflight-query-before.json').write_text(json.dumps(query,indent=2))","(directory/'preflight-query-before.json').write_text(json.dumps(query,indent=2))\n hard_rules.validate_query(query)")
 s=once(s," def count(n):B.wait(lambda:B.query(server[0]).get('numplayers')==str(n),100,'count not reached '+str(n))", " def checked_query():\n  query=B.query(server[0]);hard_rules.validate_query(query);return query\n def count(n):\n  def ready():\n   query=B.query(server[0])\n   with (E/'startup-query-attempts.jsonl').open('a')as output:output.write(json.dumps(dict(expected_players=n,monotonic=time.monotonic(),query=query))+'\\n')\n   return hardmap.startup_count(query,n,hard_rules.validate_query)\n  B.wait(ready,100,'count not reached '+str(n))")
 s=once(s,'q=B.query(server[0]);assert','q=checked_query();assert')
 s=once(s,"identity=record['identity'];assert identity and B.identity(role,unit(role))==identity", "identity=record['identity']\n  if identity is None:\n   assert B.ready(role,unit(role)),'partial start has no strictly owned ready identity'\n   identity=B.identity(role,unit(role));record['identity']=identity\n  assert B.identity(role,unit(role))==identity")
 # Same safe partial-start close as reviewed V2, without its irrelevant rotation operation guard.
 s=once(s,'subprocess.run(args+[\'/bin/bash\',str(R/(\'launch-\'+role+\'.sh\'))],check=True)',"subprocess.run(args+['/bin/bash',str(R/('launch-'+role+'.sh'))],check=True,timeout=20)")
 s=once(s,"paused_samples.append(probe.read(server[0],R/'server'));time.sleep(.3)","paused_samples.append(probe.read(server[0],R/'server'));hard_rules.validate_session(paused_samples[-1]);time.sleep(.3)")
 s=once(s,"observations={role:probe.read(rec['identity'][0],R/role)for role,rec in records.items()}","observations={role:probe.read(rec['identity'][0],R/role)for role,rec in records.items()}\n    for snapshot in observations.values():hard_rules.validate_session(snapshot)")
 s=once(s,"barrier={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}","barrier={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}\n   for snapshot in barrier.values():hard_rules.validate_session(snapshot)")
 s=once(s,"snapshots={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}","snapshots={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}\n     for snapshot in snapshots.values():hard_rules.validate_session(snapshot)")
 s=once(s,'active_snapshots=[];module_pins={}',"active_snapshots=[];native_registry=None;log_offsets=dict(server=0,botA=0,botB=0);module_pins={}")
 s=once(s,'     if inventory:\n      for group,slots in groups:', '     if inventory:\n      current_rows={}\n      for group,slots in groups:')
 s=once(s,"report['inventory']['valid_samples']+=1;inventory_stream.write(json.dumps({'elapsed':elapsed,'group':group,'snapshot':sampled})", "sampled=native_fire.bind_sample(sampled,0,server,log_offsets);report['inventory']['valid_samples']+=1;inventory_stream.write(json.dumps({'elapsed':elapsed,'group':group,'snapshot':sampled})")
 s=once(s,'initial.add(sampled,elapsed);active_snapshots.append(sampled)',"initial.add(sampled,elapsed);active_snapshots.append(sampled)\n        for row in sampled['players']:current_rows[row['slot']]=row")
 anchor="     if not initial_validated and (len(initial.players)==9 or elapsed>2):"
 s=once(s,anchor,"     if native_registry is None and inventory and set(current_rows)==set(range(9)):\n      native_registry=hardmap.registry(rotation.registry,list(current_rows.values()),mapping,server)\n      (E/'registry.json').write_text(json.dumps(native_registry,indent=2))\n"+anchor)
 anchor="   report['active_evidence']=policy.active_evidence({role:(R/role/'SeriousSam.log').read_text(errors='replace')for role in ('botA','botB')},mapping,active_snapshots,queries,(R/'server/Dedicated_BotTest.log').read_text(errors='replace')); (E/'active-evidence.json').write_text(json.dumps(report['active_evidence'],indent=2))"
 replacement="   assert native_registry is not None,'no complete current native registry'\n   logs={role:(R/role/'SeriousSam.log').read_text(errors='replace')for role in ('botA','botB')}\n   report['active_evidence']=policy.active_evidence(logs,mapping,active_snapshots,queries,(R/'server/Dedicated_BotTest.log').read_text(errors='replace'))\n   report['active_evidence']=native_fire.apply(report['active_evidence'],logs,mapping,active_snapshots,native_registry,server)\n   (E/'active-evidence.json').write_text(json.dumps(report['active_evidence'],indent=2))"
 s=once(s,anchor,replacement)
 # Preserve normal-close logs for every role that actually started even when
 # startup aborts early. The final trial still requires all four roles.
 s=once(s,"    roles=('server','botA','botB','vanilla')\n    post=archive_closed_role_logs", "    roles=tuple(records)\n    post=archive_closed_role_logs")
 # Archive the exact additional pure runtime policies; no hook or Frida imported.
 s=once(s,"'strict_backend.py','transaction.py'):","'strict_backend.py','transaction.py','a4_hard_map_policy.py','stability_hard_rules.py','a4_fire_observer_v2.py','audit_a4_native_fire_observer_v2.py','reset_policy.py'):")
 fixture=(PARENT/'test_preflight_startup.py').read_text()
 fixture=once(fixture,"'numplayers':'1',","'difficulty':'Hard','numplayers':'1',")
 fixture=once(fixture,"backend.query.return_value={};m.archive_preflight_query(pathlib.Path(td),backend,123)","backend.query.return_value={}\n   with self.assertRaises(ValueError):m.archive_preflight_query(pathlib.Path(td),backend,123)")
 (dest/'test_preflight_startup.py').write_text(fixture)
 ast.parse(s);(dest/'run-a4.py').write_text(s)
 a=(PARENT/'adapter_policy.py').read_text();a=once(a,OLD_DLL,DLL);(dest/'adapter_policy.py').write_text(a)
 (dest/'runtime.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='parent013/run-a4.py',tofile='hard020/run-a4.py')))
 m=json.loads(json.dumps(parent));deps={}
 for p,h in m['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  elif q.is_relative_to('/srv/tse-milestone-a-build-013-20261111'):q=BUILD/q.relative_to('/srv/tse-milestone-a-build-013-20261111');h=sha(q)
  deps[str(q)]=h
 for n in copied[:3]+['a4_hard_map_policy.py','stability_hard_rules.py']:deps[str(dest/n)]=sha(dest/n)
 m.update(scope='DISABLED_BUILD020_HARD_SINGLE_MAP600S_NATIVE_FIRE_V2',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['candidate']=dict(dll_sha256=DLL,source_commit=SOURCE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['runtime_dependencies']=dict(sorted(deps.items()))
 m['derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,v2_source=str(V2),v2_manifest_sha256=V2_SHA,frida_used=False,native_started=False,independent_review='PENDING',duration_seconds=600,diagnostics=0,hard_difficulty=2)
 m['root_review']=dict(approved_for_private_a4=False,reference='PENDING independent review and new Root freeze/preflight')
 m['inherited_parent_metadata']=dict(sources=m.pop('sources'),root_changes=m.pop('root_changes',None))
 m['sources']={p.name:sha(p)for p in dest.iterdir()if p.is_file()and p.name not in ('source-manifest.json','HANDOFF-disabled.json')}
 m['draft_source_sha256']={p.name:sha(p)for p in dest.glob('*.py')}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(dict(runtime_authorized=False,native_started=False,qualified=False,functional_pass=False,frida_used=False,scope='singlemap600s; no native strength/route/stability acceptance',next='independent review then Root-only freeze/preflight',source_manifest_sha256=sha(dest/'source-manifest.json')),indent=2)+'\n')
 return dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(deps),native_started=False)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',required=True,type=Path);args=parser.parse_args()
 print(json.dumps(prepare(args.destination),indent=2))

if __name__=='__main__':main()
