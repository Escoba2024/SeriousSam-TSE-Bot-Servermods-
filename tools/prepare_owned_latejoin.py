"""Offline-only disabled OwnNS eight-first latejoin package derivation."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-owned-sync018-fd-churn-disabled-20261114')
PARENT_SHA='3c30151507cf336cd3e23522828de5f3392552f594334e7bb61841846b13851d'
ADDITIONS=('owned_sync_capture.py','owned_latejoin_capture.py','owned_latejoin_capture_exec.py',
 'ownns_latejoin_preflight.py','ownns_latejoin_local_mapping.py','ownns_latejoin_runtime.py',
 'prepare_owned_latejoin.py','test_owned_latejoin_capture.py','test_ownns_latejoin_preflight.py',
 'test_ownns_latejoin_local_mapping.py','test_ownns_latejoin_runtime.py','test_ownns_latejoin_readiness.py','test_prepare_owned_latejoin.py')
RUNTIME_ADDITIONS=ADDITIONS[:6]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(source,old,new):
 if source.count(old)!=1:raise ValueError('unique reviewed latejoin anchor: '+old[:100])
 return source.replace(old,new,1)


def transform(source):
 if sha(PARENT/'run-a4.py')!=json.loads((PARENT/'source-manifest.json').read_text())['sources']['run-a4.py']:raise ValueError('parent controller pin')
 if source!=(PARENT/'run-a4.py').read_text():raise ValueError('exact parent controller source required')
 source=once(source,'from owned_sync_capture import OwnedSyncCapture',
  'from owned_latejoin_capture import OwnedLatejoinCapture\nfrom ownns_latejoin_runtime import LatejoinRuntime,sync_activity')
 source=once(source,"PREFIX='ssam-own-sync018-yodeller-20261114'","PREFIX='ssam-own-latejoin018-yodeller-20261114'")
 source=once(source,"E=BASE/f'own-sync018-yodeller-","E=BASE/f'own-latejoin018-yodeller-")
 source=once(source,'gam_strSessionName="PRIVATE A4 020 HARD";','gam_strSessionName="PRIVATE LATEJOIN 018 HARD";')
 source=once(source,";bootstrap=policy.bootstrap()",'')
 source=once(source,"'functional_pass':False,","'functional_pass':False,'a4_accepted':False,")
 source=once(source,"  subprocess.run(args+['/bin/bash',str(R/('launch-'+role+'.sh'))],check=True,timeout=20)",
  "  late.run_command(args+['/bin/bash',str(R/('launch-'+role+'.sh'))],20)")
 source=once(source,"  B.wait(lambda:B.ready(role,unit(role)),45,'own role not ready '+role)","  late.wait(lambda:B.ready(role,unit(role)),45,'own role not ready '+role)")
 source=once(source,"receipt=wait_native_identity(B,role,unit(role));","receipt=wait_native_identity(B,role,unit(role),timeout=late.remaining(15),monotonic=late.clock);")
 source=once(source,"  B.wait(lambda:str(R/role/'Bin/GameMP.dll')", "  late.wait(lambda:str(R/role/'Bin/GameMP.dll')")
 source=once(source,"  B.wait(ready,100,'count not reached '+str(n))","  late.wait(ready,100,'count not reached '+str(n))")
 # Remove the otherwise-unused input capability, not merely its call sites.
 start=source.index(' def control(kind,val,seconds):');end=source.index(' def whole_quiescent():',start)
 source=source[:start]+source[end:]
 source=once(source," def whole_quiescent():\n", " def whole_quiescent():\n  assert all(p.poll()is not None for p in late.launch_helpers),'own launcher child remains'\n")
 anchor=" with (R/'runtime.lock').open('a') as lock:"
 setup=""" late=LatejoinRuntime(root=R,evidence=E,backend=B,records=records,module_pins=module_pins,unit=unit,probe=probe,pauseprobe=pauseprobe,map_name=map_data['query_name'],slot_mapping=policy.slot_mapping,sample_host=sample_host,host_budget=host_budget)
"""
 source=once(source,anchor,setup+anchor)
 source=once(source,'  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)','  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);late.lock=lock')
 source=once(source,"   try:save_initial_observations(E,initial)","   report['latejoin_launcher_children']=late.launcher_receipts()\n   if any(not c['ended']for c in report['latejoin_launcher_children']):report['errors'].append('own launcher child remains')\n   try:save_initial_observations(E,initial)")
 source=once(source,"from qualify_integrated_wine import configure_count;configure_count(R/'botA',1)","from qualify_integrated_wine import configure_count")
 source=once(source,"'analyze_retail_sync_pcap.py'):","'analyze_retail_sync_pcap.py','owned_latejoin_capture.py','owned_latejoin_capture_exec.py','ownns_latejoin_preflight.py','ownns_latejoin_local_mapping.py','ownns_latejoin_runtime.py'):")
 begin=source.index("   bootstrap_cfg=R/'botA/Scripts/Integrated.ini'")
 end=source.index("   groups=[('botA_actual'",begin)
 block="""   cohort=True
   for physical in ('botA','botB'):
    selection=cohorts[physical];policy.checked_bytes(CANDIDATE_DLL,selection['game_sha256'])
    cfg=R/physical/'Scripts/Integrated.ini';cfg.write_text(selection['config']);assert sha(cfg)==selection['config_sha256']
   configure_count(R/'botA',4);configure_count(R/'botB',4)
   order=('botA','botB')
   launch('server');count(0);launch('botA');count(4);launch('botB');count(8)
   prejoin_mapping=policy.slot_mapping((R/'botA/SeriousSam.log').read_text(errors='replace'),(R/'botB/SeriousSam.log').read_text(errors='replace'));prejoin_mapping.pop('vanilla')
   load_logs={role:(R/role/'SeriousSam.log').read_text(errors='replace')for role in ('botA','botB')}
   policy.prepared.check_loads(map_data,load_logs,(R/'server/Dedicated_BotTest.log').read_text(errors='replace'));report['prejoin_profile_migration']=policy.check_tiers(load_logs)
   sys.path.insert(0,'/srv/tse-milestone-a-20261111/tools');from retail_inventory_readonly import InventoryReader,EvidenceError
   report['prejoin_readiness']=late.prejoin_readiness(InventoryReader,EvidenceError,policy.active_evidence,prejoin_mapping)
   first_prestart=late.private_prestart()
   capture=OwnedLatejoinCapture(E,{r:{'identity':list(rec['identity']),'unit':unit(r)}for r,rec in records.items()})
   late.capture=capture;capture.start()
   prestart=late.private_prestart(first_prestart['names']);late.original_prestart=prestart
   late.validate_current_prestart(prestart);capture.begin_admission(unit('vanilla'))
   vanilla=launch('vanilla');count(9)
   sys.path.insert(0,'/srv/tse-milestone-a-20261111/tools');from retail_inventory_readonly import InventoryReader,EvidenceError
   report['latejoin_admission']=late.admission(prestart['names'],InventoryReader)
   mapping=policy.slot_mapping((R/'botA/SeriousSam.log').read_text(errors='replace'),(R/'botB/SeriousSam.log').read_text(errors='replace'))
   assert mapping==dict(botA=[0,1,2,3],botB=[4,5,6,7],vanilla=[8]),'actual latejoin mapping differs'
   report['actual_slot_mapping']=mapping
   capture.admit(dict(identity=list(records['vanilla']['identity']),unit=unit('vanilla')))
"""
 source=source[:begin]+block+source[end:]
 # The old enum paused_smoke belongs to the old paused protocol; no false pause
 # label or new periodic inventory cadence is introduced in this new setup.
 begin=source.index('    for group,slots in groups:');end=source.index('   load_logs=',begin)
 source=source[:begin]+source[end:]
 begin=source.index('   capture=OwnedSyncCapture(');end=source.index('   def usage():',begin)
 source=source[:begin]+"""   capture.mark_postjoin_start()
   report['owned_sync_capture']=capture.receipt;save()
   sample_host('latejoin-before600')
   report['observer_input_schedule']='none; own Original late and stationary; all8 bots unpaused before join'
   report['scope']='PRIVATE_LATEJOIN_SAMPLED_SYNC_ONLY_REQUIRES_REVIEW';report['cohort_order']=order
   report['cohort_config_sha256']={role:sha(R/role/'Scripts/Integrated.ini')for role in ('botA','botB')}
"""+source[end:]
 source=once(source,'start=time.monotonic();lastquery=-100;','start=capture.post_started;lastquery=-100;')
 source=once(source,'     for snapshot in snapshots.values():hard_rules.validate_session(snapshot)',"     for snapshot in snapshots.values():hard_rules.validate_session(snapshot)\n     assert all(sorted(p['slot']for p in x['players'])==list(range(9))for x in snapshots.values()),'native nine-slot roster changed'")
 begin=source.index("   if report['active_evidence']['missing_activity']:");end=source.index("   report['sync_checks']=checks;",begin)
 source=source[:begin]+"""   report['latejoin_sync_activity']=sync_activity(report['active_evidence'],active_snapshots,mapping)
   report['a4_diagnostic_status']='OPEN_OR_NOT_APPLICABLE_TO_SYNC_PROTOCOL'
   report['a4_accepted']=False
"""+source[end:]
 source=source.replace('PASS_LIMITED_OWN_SAMPLED_SYNC_PROTOCOL_REVIEW_REQUIRED','PASS_LIMITED_PRIVATE_LATEJOIN_SAMPLED_SYNC_REVIEW_REQUIRED')
 source=once(source,'Private018 own sync protocol, stationary Original, no qualification','Private018 late Original slot8 sampled sync only, no A4 qualification')
 # Empty own unit after a failed CLI start is not a foreign-process lease.
 source=once(source,"  if identity is None:\n   assert B.ready(role,unit(role))", "  if identity is None:\n   if B.pid(unit(role))==0 and B.empty(unit(role)):\n    record['started']=False;record['closed']=True;emit('not_started',role=role);return\n   assert B.ready(role,unit(role))")
 ast.parse(source);return source


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh destination required; previous packages/evidence immutable')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('reviewed FD parent manifest')
 parent=json.loads((PARENT/'source-manifest.json').read_text())
 for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
  for p,h in parent[key].items():
   if sha(PARENT/p if relative else p)!=h:raise ValueError('inherited external/source pin '+p)
 build=json.loads(Path(parent['candidate']['build_manifest']).read_text())
 if not(build['build_ok']is True and build['dll_sha256']==parent['candidate']['dll_sha256']and build['repo_commit']==parent['candidate']['source_commit']):raise ValueError('018 source/candidate provenance')
 buildroot=Path(parent['candidate']['build_manifest']).parent
 for key,base in [('source_sha256',buildroot/'Sources/Game'),('overlay_sha256',buildroot/'overlay')]:
  for name,digest in build[key].items():
   if sha(base/name)!=digest:raise ValueError('018 source pin '+str(base/name))
 tools=Path(__file__).resolve().parent
 # The Retail decoder and both external preflight files are read-only inherited
 # dependencies. This builder neither changes them nor issues an external test.
 if sha(tools/'analyze_retail_sync_pcap.py')!=sha(PARENT/'analyze_retail_sync_pcap.py'):raise ValueError('Retail decoder must stay byte-identical')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(tools/name,dest/name)
 old=(PARENT/'run-a4.py').read_text();new=transform(old);(dest/'run-a4.py').write_text(new)
 (dest/'latejoin-controller.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='fd-disabled-parent/run-a4.py',tofile='latejoin-disabled/run-a4.py')))
 m=json.loads(json.dumps(parent));m.update(scope='DISABLED_PRIVATE_OWNNS_018_EIGHT_FIRST_ORIGINAL_SLOT8_SAMPLED_SYNC_ONLY',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,a4_accepted=False)
 m['runtime_dependencies']={str(dest/Path(p).relative_to(PARENT)if Path(p).is_relative_to(PARENT)else p):sha(dest/Path(p).relative_to(PARENT)if Path(p).is_relative_to(PARENT)else p)for p in parent['runtime_dependencies']}
 for name in RUNTIME_ADDITIONS:m['runtime_dependencies'][str(dest/name)]=sha(dest/name)
 m['runtime_dependencies']=dict(sorted(m['runtime_dependencies'].items()))
 m['latejoin_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,plan_commit='3c7be9ad7525c173e4065adb3e756c1c7d22d3fd',root_plan_integration='31004b9',independent_review='PENDING',runtime_performed=False,
  protocol='PRIVATE_OWNNS_018_EIGHT_THEN_ORIGINAL_SLOT8_V1',bot_slots=list(range(8)),original_local=0,original_global=8,original_input=False,pause_input=False,bootstrap=False,
  duration_after_admission_seconds=600,admission_deadline_seconds=30,capture_seconds=640,capture_normal_stop_seconds=10,prejoin_readiness_seconds_max=20,prejoin_combat='all8 native1m motion; at least one bound V3 FIREflag/sourcegrowth plus own kill OR positive own frag; no pickup/A4 gate',automatic_retry=False,original_decoder_unchanged=True,external_one_bot_preflights_unchanged=True,
  a4_acceptance=False,legacy_a4_diagnostics='OPEN_OR_NOT_APPLICABLE_TO_SYNC_PROTOCOL',new_local_source_probe_native_qualification=False,periodic_inventory_sampling_unchanged=True)
 m['capture']=dict(parent['capture'],initial_role_count=3,admitted_role_count=4,initial_handshake='raw capture armed before own Original launch; no reliable/connect decoder qualification',source_ports='actual PID/start/FD/inode/NetNS before CRC outcomes; old3 immutable',epoch='prospectively fixed complete-record storage offsets, not atomic engine time')
 m.pop('root_freeze',None);m['root_review']=dict(approved_for_private_a4=False,approved_for_private_latejoin=False,reference='PENDING independent review, Root freeze, fresh private-eight gate, actual Original-local0/global8 cross-check')
 m['sources']={p.name:sha(p)for p in dest.iterdir()if p.is_file()and p.name not in ('source-manifest.json','HANDOFF-capture.json','HANDOFF-latejoin.json')}
 m['draft_source_sha256']={p.name:sha(p)for p in dest.glob('*.py')}
 for name in ('run-a4.py','owned_sync_capture.py','owned_latejoin_capture.py','owned_latejoin_capture_exec.py'):
  if 'RUNTIME_REVIEWED=False'not in(dest/name).read_text():raise ValueError('disabled execution gate '+name)
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),qualified=False,functional_pass=False,a4_accepted=False,native_started=False,runtime_authorized=False)
 (dest/'HANDOFF-latejoin.json').write_text(json.dumps(dict(**receipt,next='independent review; Root-only gate/path freeze and one separately controlled run, no retry'),indent=2)+'\n')
 return receipt


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',required=True,type=Path)
 print(json.dumps(prepare(parser.parse_args().destination),indent=2))
