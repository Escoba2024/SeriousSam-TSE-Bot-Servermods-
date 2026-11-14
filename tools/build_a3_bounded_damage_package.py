"""Create a NEW disabled source package; never launch/attach/install anything."""
from pathlib import Path
import argparse
import ast
import difflib
import hashlib
import json
import shutil

from a3_damage_quiescence_patch import patch as patch_hook

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--parent',type=Path,required=True)
parser.add_argument('--destination',type=Path,required=True)
args=parser.parse_args()
parent=args.parent.resolve(strict=True);dest=args.destination.resolve()
if dest.exists():raise SystemExit('new destination required; closed packages are immutable')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(parent/'source-manifest.json')=='7730510ef9f6e4ef8455f6b0de9fffed5afc750a1beb917abed685240982d269','exact disabled Hard2 parent'
old=json.loads((parent/'source-manifest.json').read_text())
assert old['runtime_reviewed']is False and old['qualified']is False
for relative,expected in old['sources'].items():assert sha(parent/relative)==expected,relative
for path,expected in old['runtime_dependencies'].items():assert sha(path)==expected,path
shutil.copytree(parent,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
repo=Path(__file__).resolve().parent
for name in ('original_damage_worker.py','original_damage_collector.py','a3_damage_quiescence_patch.py',
             'test_original_damage_worker.py','test_original_damage_collector.py','test_a3_damage_quiescence.py',
             'test_a3_bounded_damage_package.py','test_a3_direct_closed_fixture.py'):
 shutil.copy2(repo/name,dest/name)
original_hook=(parent/'frozen-v2/damage_readonly.js').read_text()
new_hook=patch_hook(original_hook);(dest/'frozen-v2/damage_readonly.js').write_text(new_hook)
source=(parent/'run-a3-direct020.py').read_text();s=source
def replace_once(old,new):
 global s
 assert s.count(old)==1,('unexpected parent region',old[:100],s.count(old));s=s.replace(old,new)
replace_once('from host_budget import HostBudget','from host_budget import HostBudget\nfrom original_damage_worker import WorkerProxy')
replace_once("FRIDA_PACKAGE=Path('/srv/tse-frida-probe-20261111/lib/python3.12/site-packages')\n",'')
replace_once('767a013ae896aa507d536e16f34ee3ed9bcc73121b41970ea329478f59381787',sha(dest/'frozen-v2/damage_readonly.js'))
replace_once('frida_session=None;frida_script=None;','damage_worker=None;')
replace_once("identity=record['identity'];assert identity and B.identity(role,unit(role))==identity", """identity=record['identity']
  if identity is None:
   if B.pid(unit(role))==0 and B.empty(unit(role)):
    B.quiescent(R/role);record.update(started=False,closed=True,close_evidence='own_unit_empty_and_root_quiescent');emit('closed_unstarted',role=role);return
   assert B.ready(role,unit(role)),'partial start has no strictly owned ready identity'
   identity=B.identity(role,unit(role));record['identity']=identity;record['started']=True
  assert B.identity(role,unit(role))==identity""")
replace_once("PREFIX=f'ssam-direct020-hard-pair{trial}","PREFIX=f'ssam-direct020-hard-worker-pair{trial}")
replace_once("E=BASE/f'direct020-hard-pair{trial}","E=BASE/f'direct020-hard-worker-pair{trial}")
archive="('public.ini','candidate.ini','initial-reference.json','source-manifest.json','controller_policy.py','a3_direct_controller_policy.py','a3_direct_tiers.py','stability_hard_rules.py')"
assert s.count(archive)==2
s=s.replace(archive,archive[:-1]+",'original_damage_worker.py','original_damage_collector.py')")
start=s.index('    sys.path.insert(0,str(FRIDA_PACKAGE))')
end=s.index('    frozen=FROZEN',start)
s=s[:start]+'    import zipfile,zlib\n'+s[end:]
replace_once("guard_module=imp('owned_damage_guard',frozen/'controller_guard.py');message_guard=guard_module.MessageGuard(report)","guard_module=imp('owned_damage_guard',frozen/'controller_guard.py')")
replace_once("hook_source=(frozen/'damage_readonly.js').read_text();report['frida_damage']={'version':frida.__version__", "report['frida_damage']={'version':'17.26.2'")
replace_once("frida_stream=(E/'frida-damage.jsonl').open('w');frida_started=time.perf_counter();frida_session=frida.get_local_device().attach(server[0]);damage_host.validate_damage_host(frida_reg)\n    frida_script=frida_session.create_script(hook_source)","""frida_stream=(E/'frida-damage.jsonl').open('w');frida_started=time.perf_counter()
    lockstat=(R/'runtime.lock').stat()
    worker_config={'controller_root':str(DRAFT),'arena':str(R),'evidence':str(E),'registry_file':str(registry_file),
     'parent':{'pid':os.getpid(),'start_ticks':int((Path('/proc')/str(os.getpid())/'stat').read_text().rsplit(') ',1)[1].split()[19]),'lock_file':[lockstat.st_dev,lockstat.st_ino]},
     'roles':{role:{'identity':list(rec['identity']),'unit':unit(role),'net_namespace_inode':(Path('/proc')/str(rec['identity'][0])/'ns/net').stat().st_ino}for role,rec in records.items()}}
    worker_config_file=E/'damage-worker-config.json';worker_config_file.write_text(json.dumps(worker_config,indent=2)+'\\n');worker_config_file.chmod(0o600)
    damage_worker=WorkerProxy.start(worker_config_file)
    report['damage_worker_identity']={'pid':damage_worker.pid,'start_ticks':damage_worker.start_ticks,'config_sha256':sha(worker_config_file),'worker_source_sha256':sha(DRAFT/'original_damage_worker.py')};save()""")
# Packet validation/attribution is unchanged; it can now accept final close packets.
replace_once("    def trace_drain(live=False):\n     message_guard.check()\n     damage_host.validate_damage_host(frida_reg);assert B.identity('server',unit('server'))==server and (process/'ns/net').stat().st_ino==frida_net\n     packet=frida_script.exports_sync.drain();message_guard.check();records=packet.pop('records');assert isinstance(records,list) and len(records)<=64", "    def accept_trace_packet(packet,live=False):\n     records=packet.pop('records');assert isinstance(records,list) and len(records)<=64")
replace_once("    frida_script.on('message',message_guard.on_message)\n    damage_host.validate_damage_host(frida_reg)", """    def trace_drain(live=False):
     damage_host.validate_damage_host(frida_reg);assert B.identity('server',unit('server'))==server and (process/'ns/net').stat().st_ino==frida_net
     accept_trace_packet(damage_worker.drain(),live)
    damage_host.validate_damage_host(frida_reg)""")
replace_once("    frida_script.load();frida_arm=frida_script.exports_sync.arm(arm)","    worker_arm=damage_worker.arm();frida_arm=worker_arm['arm_result'];report['frida_damage']['worker_arm']=worker_arm\n    assert worker_arm['frida_version']=='17.26.2' and worker_arm['pre_attach_original_bytes_verified']is True")
replace_once("assert frida_arm['armed'];report['frida_damage']['arm_result']=frida_arm;message_guard.check()", "assert frida_arm['armed'];report['frida_damage']['arm_result']=frida_arm")
s=s.replace('if frida_script:damage.check_window_budget','if damage_worker:damage.check_window_budget')
s=s.replace('if frida_script:trace_drain(True)','if damage_worker:trace_drain(True)')
start=s.index('   if frida_script:',s.index('   def pin_trace_host():'))
end=s.index("   if guard_module and report.get('frida_damage'",start)
s=s[:start]+"""   if damage_worker:
    def stop_trace():
     result=damage_worker.close()
     for packet in result.get('packets',[]):accept_trace_packet(packet)
     report['frida_damage']['worker_close']={k:v for k,v in result.items()if k!='packets'}
     report['frida_damage']['stop_result']=result.get('stop_result')
     report['frida_damage']['detached']=result.get('detached')is True
     report['errors'].extend('damage worker cleanup: '+str(e)for e in result.get('cleanup_errors',[]))
     assert result.get('closed')is True and result.get('idle_verified')is True and result.get('original_bytes_verified')is True,'damage worker close not proven'
    cleanup_steps([('damage worker bounded close',stop_trace)],report['errors'])
"""+s[end:]
replace_once('   if frida_script:\n    def finalize_damage_trace():','   if damage_worker:\n    def finalize_damage_trace():')
# Reaping follows the original normal-close loop; no game process is signalled.
marker='   if display and all(r[\'closed\'] for r in records.values()):'
replace_once(marker,"""   if damage_worker:
    try:
     normally_closed=set(records)=={'server','botA','botB','vanilla'}and all(r.get('closed')is True for r in records.values())
     if normally_closed:whole_quiescent()
     report['damage_worker_reaped']=damage_worker.finish(roles_closed=normally_closed)
    except BaseException as error:report['errors'].append('damage worker reap:'+repr(error))
"""+marker)
ast.parse(s)
assert 'exports_sync'not in s and 'import frida'not in s and 'frida_session'not in s and 'frida_script'not in s
(dest/'run-a3-direct020.py').write_text(s)
# The observer implementation is part of the equal-condition comparison. Both
# sources are archived by the controller; no different observer builds mix.
analysis=(parent/'analyze-direct020.py').read_text()
analysis=analysis.replace("'hard_rules_sha256':sha(P/'stability_hard_rules.py')}",
 "'hard_rules_sha256':sha(P/'stability_hard_rules.py'),'damage_observer':{'worker_sha256':sha(P/'original_damage_worker.py'),'collector_sha256':sha(P/'original_damage_collector.py'),'hook_sha256':f['hook_source_sha256'],'host_sha256':f['host_source_sha256'],'guard_sha256':f['guard_source_sha256'],'frida_version':f['version']}}")
ast.parse(analysis);(dest/'analyze-direct020.py').write_text(analysis)
for label,before,after in [('worker-controller.diff',source,s),('worker-hook.diff',original_hook,new_hook),
                          ('worker-analyzer.diff',(parent/'analyze-direct020.py').read_text(),analysis)]:
 (dest/label).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='hard020-parent/'+label,tofile='hard020-worker/'+label,n=0)))
m=json.loads(json.dumps(old));deps={}
for path,h in old['runtime_dependencies'].items():
 q=Path(path)
 if q.is_relative_to(parent):q=dest/q.relative_to(parent);h=sha(q)
 deps[str(q)]=h
for name in ('original_damage_worker.py','original_damage_collector.py'):deps[str(dest/name)]=sha(dest/name)
m.update(scope='DISABLED_DIRECT_BUILD020_HARD_BOUNDED_DAMAGE_WORKER',runtime_dependencies=deps,runtime_reviewed=False,qualified=False)
m['external_runtime_pins_reverified']=False;m['external_runtime_pins_verified_utc']=None
m['root_review']='PENDING independent bounded worker/JS lifecycle review and new Retail qualification'
m['author_offline_verification']={'bounded_worker_checks_pending':True,'native_started':False}
m['worker_derivation']={'parent_manifest_sha256':sha(parent/'source-manifest.json'),'parent':str(parent),
 'source_preparation_only':True,'frida_only_in_fresh_exec_worker':True,'arm_deadline_seconds':3,'drain_deadline_seconds':.1,'close_deadline_seconds':2,
 'idle_subdeadline_seconds':1,'hook_ttl_ms':125000,'binding_ms':2000,'queue_records':64,'max_calls':1024,
 'historical_getter_binding_body_unchanged':True,'retail_guard_header_unchanged':True,'automatic_retry':False,
 'hook_lifecycle_changed':True,'parent_hook_sha256':sha(parent/'frozen-v2/damage_readonly.js'),'new_hook_sha256':sha(dest/'frozen-v2/damage_readonly.js')}
m['direct_tiers']['same_damage_host_restore_files']=[n for n in old['direct_tiers']['same_damage_host_restore_files']if n!='frozen-v2/damage_readonly.js']
m['direct_tiers']['inherited_external_pins_fresh_check_pending']=True;m['direct_tiers']['new_controller_analyzer_tests_pending']=True
(dest/'HANDOFF.json').write_text(json.dumps({'status':'DISABLED_WORKER_ADAPTATION_PENDING_FOCUSED_CHECKS','runtime_reviewed':False,'native_started':False,'qualified':False,
 'parent':str(parent),'remaining':['focused source/worker/JS checks','fresh pins','independent review','Root freeze and separate native qualification']},indent=2)+'\n')
runplan=json.loads((dest/'RUNPLAN-disabled.json').read_text());runplan['runtime_allowed']=False;runplan['open']=['bounded worker review','fresh pins','new native qualification'];(dest/'RUNPLAN-disabled.json').write_text(json.dumps(runplan,indent=2)+'\n')
m['sources']={str(p.relative_to(dest)):sha(p)for p in dest.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.name!='source-manifest.json'}
(dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'package':str(dest),'manifest_sha256':sha(dest/'source-manifest.json'),'runtime_gate':False,'native_started':False}))
