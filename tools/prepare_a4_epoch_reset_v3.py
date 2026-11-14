"""Offline disabled derivation of the reviewed three-round reset controller."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-milestone-a-continuation-evidence-20261112/a4-build018-extended-root-frozen')
PARENT_SHA='9064439561caac5deed96b1be4e546d8fa0c69ac6fbdf24a5c836b3538d0817c'
V3=Path('/srv/tse-a4-build020-hard-ordered-memory-clean-final-20261114')
V3_SHA='a4568cbe60716887e195f7996ffeed774c1035cadcb11660b644c1fe64b4b2d9'
BUILD=Path('/srv/tse-milestone-a-build-020-20261114')
BUILD_SHA='3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6'
DLL='094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0'
SOURCE='e5f7a65502fbea683014ef8fcc95ecdd2a927b6a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(text,old,new):
 if text.count(old)!=1:raise ValueError('nonunique reviewed source anchor: '+old)
 return text.replace(old,new,1)


def observer_sources():
 """Exact V3 reuse; only generalize the already-supported core epoch0/1/2."""
 groups=(V3/'a4_canonical_native_groups.py').read_text()
 groups=once(groups,'def declare(mapping, server_identity, log_offsets):','def declare(mapping, server_identity, log_offsets, phase):')
 groups=once(groups,'observer_epoch=core.epoch(0, server_identity, log_offsets),','observer_epoch=core.epoch(phase, server_identity, log_offsets),')
 groups=once(groups,"epoch.get('server_identity', []), epoch.get('log_offsets', {}))","epoch.get('server_identity', []), epoch.get('log_offsets', {}), epoch.get('phase'))")
 groups=once(groups,'core.bind_sample(sample, 0, epoch[\'server_identity\'],','core.bind_sample(sample, epoch[\'phase\'], epoch[\'server_identity\'],')
 groups=once(groups,"registry.get('phase') == 0 and registry.get('native_fire_epoch') == epoch,","registry.get('phase') == epoch['phase'] and registry.get('native_fire_epoch') == epoch,")
 ordered=(V3/'a4_ordered_memory_v3.py').read_text()
 ordered=once(ordered,'import a4_canonical_native_groups as groups','import a4_reset_groups_v3 as groups')
 return {'a4_reset_groups_v3.py':groups,'a4_reset_ordered_memory_v3.py':ordered}


def rule_sources():
 s=(V3/'stability_hard_rules.py').read_text()
 s=once(s,'def validate_session(sample):',"def validate_session(sample, phase):\n    if type(phase) is not int or phase not in (0, 1, 2):\n        raise ValueError('reset phase0/1/2 required')\n    expected = dict(EXPECTED, timelimit=(2, 2, 0)[phase])")
 s=once(s,'if values != EXPECTED:','if values != expected:')
 return {'a4_reset_hard_rules.py':s}


def reset_source():
 s=(PARENT/'reset_policy.py').read_text()
 s=once(s,'import copy,math,re','import copy,math,re\nimport a4_reset_hard_rules as hard_rules')
 s=once(s,'gam_iStartDifficulty=3;','gam_iStartDifficulty=2;')
 s=once(s,'PRIVATE A4 RESET 013','PRIVATE A4 RESET 020')
 # Same native bytes already read by the inherited function, no new read.
 s=once(s,'    for role, snapshot in peers.items():','    for role, snapshot in peers.items():\n        hard_rules.validate_session(snapshot, phase)')
 return s


def transform_controller(s):
 s=once(s,'import phase_inventory','import phase_inventory\nimport a4_reset_hard_rules as hard_rules\nfrom a4_epoch_reset_observation import PhaseReads, validate_sequence')
 s=once(s,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
 s=once(s,'/srv/tse-milestone-a-build-018-20261112/Sources/Game/GameMP.dll',str(BUILD/'Sources/Game/GameMP.dll'))
 s=once(s,'duration==480 and diag==1','duration==480 and diag==0')
 s=once(s,"PREFIX='ssam-a4-reset018-extended-20261112'","PREFIX='ssam-a4-reset020-v3-20261114'")
 s=once(s,"E=BASE/f'a4-reset018-extended-","E=BASE/f'a4-reset020-v3-")
 s=once(s,'inventory_stream=None;transaction=None','inventory_stream=None;attempt_streams=[];phase_reads=None;transaction=None')
 s=once(s," (directory/'preflight-query-before.json').write_text(json.dumps(query,indent=2))"," (directory/'preflight-query-before.json').write_text(json.dumps(query,indent=2))\n hard_rules.validate_query(query)")
 s=once(s,' def unit(role):',""" def checked_query(pending=False):
  query=B.query(server[0])
  if not query and pending:return query
  hard_rules.validate_query(query)
  return query
 def begin_read_epoch(phase,mapping,offsets):
  if phase_reads is not None:
   assert phase_reads.finished,'previous observation epoch not finalized'
   phase_reads.journal.stream.close()
  attempt_stream=(E/('phase-'+str(phase)+'-read-attempts.jsonl')).open('x');attempt_streams.append(attempt_stream)
  return PhaseReads(phase,mapping,server,{r:offsets[r]for r in observer.PERSISTENT},attempt_stream)
 def unit(role):""")
 s=once(s,'try:sample=inventory.sample(tuple(capture.mapping[group]))',"try:sample=phase_reads.sample(inventory.sample,tuple(capture.mapping[group]),group+'_actual')")
 s=once(s,'  nonlocal inventory,early_capture','  nonlocal inventory,early_capture,phase_reads')
 anchor="   inventory=InventoryReader(server[0],server[1],R/'server','1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208')"
 s=once(s,anchor,"   phase_reads=begin_read_epoch(phase,next_mapping,early_capture.epoch['log_offsets'])\n"+anchor)
 s=once(s,"def count(n):B.wait(lambda:B.query(server[0]).get('numplayers')", "def count(n):B.wait(lambda:checked_query(pending=True).get('numplayers')")
 anchor="   groups=[('botA_actual',tuple(mapping['botA'])),('botB_actual',tuple(mapping['botB'])),('vanilla_plus_overlap',tuple(mapping['vanilla']+mapping['botA'][:3]))]"
 s=once(s,anchor,"   phase_reads=begin_read_epoch(0,mapping,dict(server=0,botA=0,botB=0))\n   groups=list(phase_reads.contract['groups'].items())")
 s=once(s,'snap=inventory.sample(slots);',"snap=phase_reads.sample(inventory.sample,slots,group,'paused_smoke');")
 anchor="    result.update(phase=protocol.index,map=rotation.MAPS[protocol.index],ended_elapsed=elapsed,first_simulation_state_proven=False,round_script_execution=dict(report['round_script_execution']))"
 s=once(s,anchor,"    result=phase_reads.apply(result,{r:phase_log[r]for r in ('botA','botB')},mapping,phase_rows,phase_registry,server)\n    (phase_directory/'memory-observation-contract.json').write_text(json.dumps(phase_reads.contract,indent=2))\n"+anchor)
 s=once(s,'closed_query=B.query(server[0])','closed_query=checked_query()')
 s=once(s,'latest_query=B.query(server[0]);queries.append(archive_live_query(E,elapsed,protocol.index,protocol.state,latest_query))',"latest_query=checked_query(pending=protocol.state=='waiting');queries.append(archive_live_query(E,elapsed,protocol.index,protocol.state,latest_query))")
 s=once(s,"latest_query=B.query(server[0]);queries.append(archive_live_query(E,elapsed,protocol.index,'fresh_observer_launched',latest_query))","latest_query=checked_query(pending=True);queries.append(archive_live_query(E,elapsed,protocol.index,'fresh_observer_launched',latest_query))")
 anchor="next_offsets['vanilla']=0;phase_offsets=next_offsets;mapping=next_mapping;groups=[('slots0to3',(0,1,2,3)),('slots4to7',(4,5,6,7)),('slot8plusoverlap',(8,0,1,2))]"
 s=once(s,anchor,"next_offsets['vanilla']=0;phase_offsets=next_offsets;mapping=next_mapping;groups=list(phase_reads.contract['groups'].items())")
 s=once(s,'try:sampled=inventory.sample(slots)','try:sampled=phase_reads.sample(inventory.sample,slots,group)')
 s=once(s,'       if phase_capture is not None:phase_capture.confirm_registry(reg)',"       if phase_capture is not None:\n        phase_capture.confirm_registry(reg);reg['reset_epoch_receipt']=json.loads(json.dumps(phase_capture.receipt))\n       reg['round_begin_order']=[int(n)for n in report['round_script_execution']['observed_begin_names']]\n       reg['persistent_identities']=persistent;phase_reads.bind_registry(reg)")
 s=once(s,"   report['active_evidence_missing']={", "   report['reset_observation_sequence']=validate_sequence(phase_results,persistent)\n   report['active_evidence_missing']={")
 s=once(s,"[('inventory',inventory),('inventory_stream',inventory_stream)]:", "[('inventory',inventory),('inventory_stream',inventory_stream)]+[('attempt_stream',s)for s in attempt_streams]:")
 s=once(s,"main('redstation',480,1)","main('redstation',480,0)")
 ast.parse(s)
 return s


V3_FILES=('a4_fire_observer_v2.py','audit_a4_native_fire_observer_v2.py',
          'audit_a4_ordered_memory_v3.py')
V3_TEST_FILES=('a4_canonical_native_groups.py','a4_ordered_memory_v3.py',
               'test_a4_fire_observer_v2.py','test_a4_canonical_native_groups.py',
               'test_a4_ordered_memory_v3.py','test_audit_a4_native_fire_observer_v2.py')
ADDITIONS=('a4_epoch_reset_observation.py','prepare_a4_epoch_reset_v3.py',
           'test_a4_epoch_reset_v3.py','test_prepare_a4_epoch_reset_v3.py')


def legacy_fixture_sources():
 """Retarget only old synthetic session/config fixtures, retain their assertions."""
 extended=(PARENT/'test_extended_protocol.py').read_text()
 extended=once(extended,'import reset_policy as r','import reset_policy as r\nimport a4_reset_hard_rules as hard_rules')
 extended=once(extended,"   raw=bytearray(156);struct.pack_into('<i',raw,0x30,minutes)","   raw=bytearray(156)\n   for key,(fmt,offset)in hard_rules.FIELDS.items():struct.pack_into(fmt,raw,offset,hard_rules.EXPECTED[key])\n   struct.pack_into('<i',raw,0x30,minutes)")
 # The reviewed runtime protocol now deliberately requires diagnostics0.
 extended=extended.replace('480,1','480,0').replace('duration,1','duration,0')
 # The original terminal-cap test isolates its clock boundary. The independent
 # new sequence tests exercise the real proof validator; no native proof here.
 extended=once(extended,"'checks':{role:","'persistent':IDS,'validate_sequence':lambda phases,ids:{'portable_cap_test_only':True},'checks':{role:")
 early=(PARENT/'test_phase_inventory.py').read_text()
 early=once(early,'import reset_policy as rotation','import reset_policy as rotation\nimport a4_reset_hard_rules as hard_rules')
 early=once(early,'        raw = bytearray(156)','        raw = bytearray(156)\n        for key,(fmt,offset)in hard_rules.FIELDS.items():struct.pack_into(fmt,raw,offset,hard_rules.EXPECTED[key])')
 anchor="                if name=='reset_policy.py':\n"
 new=anchor+"                    actual=actual.replace('import copy,math,re\\nimport a4_reset_hard_rules as hard_rules','import copy,math,re').replace('        hard_rules.validate_session(snapshot, phase)\\n','').replace('gam_iStartDifficulty=2;','gam_iStartDifficulty=3;').replace('PRIVATE A4 RESET 020','PRIVATE A4 RESET 013')\n"
 early=once(early,anchor,new)
 early=once(early,"        self.assertEqual((HERE/'adapter_policy.py').read_text(),expected)","        self.assertEqual((HERE/'adapter_policy.py').read_text().replace('"+DLL+"','6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a'),expected)")
 return {'test_extended_protocol.py':extended,'test_phase_inventory.py':early}


def checked_manifest(root,expected):
 if sha(root/'source-manifest.json')!=expected:raise ValueError('parent manifest pin: '+str(root))
 m=json.loads((root/'source-manifest.json').read_text())
 for name,h in m['sources'].items():
  if sha(root/name)!=h:raise ValueError('parent source pin: '+name)
 for p,h in m['runtime_dependencies'].items():
  if sha(p)!=h:raise ValueError('parent runtime pin: '+p)
 for name,h in m.get('verification_sources',{}).items():
  if sha(root/name)!=h:raise ValueError('parent verification pin: '+name)
 return m


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh package destination required')
 parent=checked_manifest(PARENT,PARENT_SHA);vm=checked_manifest(V3,V3_SHA)
 if sha(BUILD/'manifest.json')!=BUILD_SHA:raise ValueError('build manifest pin')
 build=json.loads((BUILD/'manifest.json').read_text())
 if build['build_ok']is not True or build['repo_commit']!=SOURCE or build['dll_sha256']!=DLL:raise ValueError('build provenance')
 buildpins={str(BUILD/'manifest.json'):BUILD_SHA,str(BUILD/'Sources/Game/GameMP.dll'):DLL}
 for key,folder in [('source_sha256','Sources/Game'),('overlay_sha256','overlay')]:
  for name,h in build[key].items():buildpins[str(BUILD/folder/name)]=h
 for p,h in buildpins.items():
  if sha(p)!=h:raise ValueError('build input pin: '+p)
 old=(PARENT/'run-mapreset.py').read_text();source=transform_controller(old)
 sources={**observer_sources(),**rule_sources(),**legacy_fixture_sources(),'reset_policy.py':reset_source(),'run-mapreset.py':source}
 sources['adapter_policy.py']=once((PARENT/'adapter_policy.py').read_text(),parent['candidate']['dll_sha256'],DLL)
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name,text in sources.items():
  ast.parse(text);(dest/name).write_text(text)
 for name in V3_FILES:shutil.copy2(V3/name,dest/name)
 for name in V3_TEST_FILES:shutil.copy2(V3/name,dest/name)
 tools=Path(__file__).resolve().parent
 for name in ADDITIONS:shutil.copy2(tools/name,dest/name)
 for name in ('a4_canonical_native_groups.py','a4_ordered_memory_v3.py'):
  shutil.copy2(V3/name,dest/('parent-v3-'+name))
 (dest/'reset-v3-runtime.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),source.splitlines(True),fromfile='parent018/run-mapreset.py',tofile='disabled020/run-mapreset.py')))
 (dest/'reset-v3-policy.diff').write_text(''.join(difflib.unified_diff((PARENT/'reset_policy.py').read_text().splitlines(True),sources['reset_policy.py'].splitlines(True),fromfile='parent018/reset_policy.py',tofile='disabled020/reset_policy.py')))
 deps={}
 for p,h in parent['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to('/srv/tse-milestone-a-build-018-20261112'):continue
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
  deps[str(q)]=h
 for name in (*sources,*V3_FILES,'a4_epoch_reset_observation.py'):
  if not name.startswith('test_'):deps[str(dest/name)]=sha(dest/name)
 deps.update(buildpins)
 m=json.loads(json.dumps(parent))
 m['inherited_reset_parent_metadata']={k:v for k,v in parent.items()if k not in ('runtime_dependencies','sources','verification_sources')}
 m.update(scope='DISABLED_BUILD020_HARD_RED_RED_RED480_ORDERED_MEMORY_V3',runtime_reviewed=False,runtime_performed=False,
          qualified=False,functional_pass=False,map_reset_proven=False,original_auto_rejoin_proven=False,
          runtime_dependencies=dict(sorted(deps.items())),candidate=dict(vm['candidate'],repo_tree=build['repo_tree']))
 m['root_review']=dict(approved_for_private_a4=False,automatic_retry=False,maximum_native_runs=1,reference='PENDING independent review and Root-only freeze/preflight')
 m['derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,ordered_parent=str(V3),ordered_parent_manifest_sha256=V3_SHA,
    independent_review='PENDING',native_started=False,frida_used=False,hard_difficulty=2,diagnostics=0,
    duration_seconds=480,phases=3,actual_resets=2,bot_slotphases=24,original_restarts=2,
    terminal_watchdog_positive_native_case='NOT_EXERCISED',first_simulation_state_proven=False,
    old_v2_sha256={n:sha(V3/n)for n in V3_FILES},source_inputs_verified=len(build['source_sha256']),overlay_inputs_verified=len(build['overlay_sha256']))
 m['read_contract']=dict(vm['read_contract'],serial_scope='per_actual_reset_epoch_all_inventory_attempts',new_native_reads=0,new_gameplay_inputs=0,new_sleeps=0)
 excluded={'source-manifest.json','HANDOFF-disabled.json'}
 m['sources']={str(p.relative_to(dest)):sha(p)for p in sorted(dest.rglob('*'))if p.is_file()and p.name not in excluded and '__pycache__'not in p.parts}
 m['draft_source_sha256']={p.name:sha(p)for p in dest.glob('*.py')}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(dict(runtime_authorized=False,native_started=False,qualified=False,functional_pass=False,
    source_manifest_sha256=sha(dest/'source-manifest.json'),launcher=str(dest/'run-mapreset.py'),
    next='independent review; Root-only own namespace/gate freeze and fresh preflight; one480s window; no auto retry'),indent=2)+'\n')
 return dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(deps),
             source_pins=len(m['sources']),build_source_pins=len(build['source_sha256']),build_overlay_pins=len(build['overlay_sha256']),native_started=False)


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
