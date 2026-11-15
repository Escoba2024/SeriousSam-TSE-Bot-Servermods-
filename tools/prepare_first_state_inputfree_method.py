"""Fresh disabled PitchRoot derivative: two separate input-free method arms.

No old runner or immutable binding is edited. Source inverse must recover the
entire pinned PitchRoot runner, including all unchanged startup/restore guards.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

PARENT=Path('/srv/tse-a1-pitch-feedback-root-frozen-20261115')
PARENT_SHA='a2fa65092236f1b16a8fe3f2a93199e22a530ee7c61da82cfa9599e8e7d66aa7'
RUNNER_SHA='5b348963edd8333aa500bde864675fc167cc0d4fdae07445dae3de5c2fc0051a'
API=Path('/srv/tse-a1-first-state-method-adapter-final-disabled-20261115')
API_SHA='1e59d3268806f0ce92780c42548c876eb0ee4a09b25cb08d46532f091f86f707'
TOOLS=Path(__file__).resolve().parent
OUTPUT=Path('/srv/tse-a1-first-state-inputfree-method-final-disabled-20261115')
HELPER_SHA='6ec98fa31f2280285a0fb41d0afc5bf0b51e9efe2ba005efb3642aba32e131e2'
UNUSED=('a1_input_worker.py','a1_passive_xrecord.py','a1_passive_xrecord_worker.py','a1_xres_attribution.py','a1_xres_attribution_worker.py','collector/a1_original_input_collector.py')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb')as stream:stream.write(data)
def dump(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def once(text,old,new):
    require(text.count(old)==1,'runner source anchor differs');return text.replace(old,new,1)


OLD=(PARENT/'run_dual.py').read_text()
require(hashlib.sha256(OLD.encode()).hexdigest()==RUNNER_SHA,'PitchRoot runner pin differs')
OLD_ENDPOINT=OLD[OLD.index('   for role in P.CLIENTS:\n    own_identity(role);number='):OLD.index("   assert P.profiles(R)==profile,'profiles changed during original join'")]
NEW_ENDPOINT="""   for role in P.CLIENTS:
    own_identity(role);number=int(P.DISPLAYS[role][1:]);display_guard(number)
    method_windows[role]=window(role)
   report['own_method_windows']=dict(method_windows)
"""
OLD_OBSERVATION=OLD[OLD.index('   def bounded_step('):OLD.index('  except BaseException as error:\n   report[\'status\']=\'FAIL\'',OLD.index('   def bounded_step('))]
NEW_OBSERVATION="""   method=MW.MethodWindow(mode=arm,api_root=DRAFT/'method-api',arena=R,evidence=E,parent_started=parent_started,
    frame=native_roles(),records=records,pins=pins,own_identity=own_identity,unit=unit,periodic=periodic,save=save,
    record=report.setdefault('first_state_method',{}))
   NIP.run_after_verified_controls(vanilla_inventory,report,E/'controls-effective.json',save,method.run)
   host('end');query(2);report['native_summary']=P.summarize(samples,mapping);report['observed_seconds']=time.monotonic()-started
   CP.check_window(started,time.monotonic())
   report['parent_elapsed_before_cleanup']=time.monotonic()-parent_started
   assert report['parent_elapsed_before_cleanup']<=90,'method admission/observation budget exceeded'
   report.update(diagnostic_only=True,normal_route_or_fire=False,input_once_proven=False,foreign_hit_proven=False,
    duration_bound_seconds=duration,full_requested_window_observed=False,completed_input_program=False)
   report['frames']=frames;report['status']='CLEANUP_PENDING'
"""
OLD_PRECLEANUP=OLD[OLD.index('   if passive is not None:\n',OLD.index('  finally:\n   if passive')):OLD.index('   for e in endpoints.values():',OLD.index('  finally:\n   if passive'))]
NEW_PRECLEANUP="""   if method is not None:
    try:report['first_state_method_cleanup']=method.finish_before_roles()
    except BaseException as error:report['errors'].append('method observer cleanup:'+repr(error))
"""
OLD_REAP=OLD[OLD.index('   if collector is not None:\n    try:\n     quiescent();'):OLD.index("   report['cleanup']=records;report['displays']=displays;report['frames']=frames")]
NEW_REAP="""   try:
    quiescent();assert set(records)==set(P.ROLES) and all(rec.get('closed')is True for rec in records.values()),'all three own normal roles/units required'
    report['units_closed_verified']=True
    if method is not None:report['method_worker']=method.finish_after_roles_closed(roles_closed=True)
   except BaseException as error:report['errors'].append('method worker retained/normal roles incomplete:'+repr(error))
"""
OLD_FINAL=OLD[OLD.index("   if report['status']=='CLEANUP_PENDING':"):OLD.index(' return report\nif __name__')]
NEW_FINAL="""   report['status']=MW.candidate_status(report,method)
   verdict=finalize_trial_evidence(report,expected_roles=P.ROLES)
   report['generic_trial_accepted']=verdict.accepted;report['final_evidence_reasons']=list(verdict.reasons)
   report['trace_evidence_complete']=False;report['first_state_method_evidence_complete']=verdict.accepted and report['status']!='FAIL'
   if not report['first_state_method_evidence_complete']:report['status']='FAIL'
   save()
   if not report['first_state_method_evidence_complete']:raise RuntimeError('input-free method evidence incomplete; see '+str(E/'result.json'))
"""
OLD_CLI=OLD[OLD.index(" parser=argparse.ArgumentParser(description="):]
NEW_CLI=""" parser=argparse.ArgumentParser(description='Disabled input-free two-Original method comparison; separate declared control/trace arms');parser.add_argument('--seconds',type=int,default=90,choices=(90,));parser.add_argument('--mode',choices=('first-state-method',),default='first-state-method');parser.add_argument('--arm',choices=('control','trace'),required=True);args=parser.parse_args();main(args.seconds,args.mode,args.arm)
"""
CHANGES=[
 ("from a1_input_worker import WorkerProxy,start_ticks\nfrom a1_trace_scope import InputScope,trace_complete\nfrom a1_mapping_failure_receipt import preserve_mapping_failure\nfrom a1_passive_xrecord import instrument_transport,prepare_xtest_transport\nimport a1_pitch_feedback as PF", "from a1_mapping_failure_receipt import preserve_mapping_failure\nimport first_state_inputfree_method as MW"),
 ('RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False'),
 ("PREFIX='ssam-a1-pitch-feedback-root-20261115'","PREFIX='ssam-a1-first-state-method-disabled-20261115'\nMETHOD_ARM_USED=False"),
 ("def main(duration=90,mode='pitch-feedback'):\n assert mode=='pitch-feedback','fixed normal mouse pitch-feedback diagnostic mode'", "def main(duration=90,mode='first-state-method',arm=None):\n global PREFIX,METHOD_ARM_USED\n parent_started=time.monotonic()\n assert mode=='first-state-method'and arm in('control','trace'),'fixed input-free method arm required'"),
 (" if not RUNTIME_REVIEWED:raise RuntimeError('OFFLINE review draft; Root frozen copy required')", " if not RUNTIME_REVIEWED:raise RuntimeError('OFFLINE review draft; Root frozen copy required')\n assert not METHOD_ARM_USED,'one declared method arm per process; no retry'\n METHOD_ARM_USED=True;PREFIX=PREFIX+'-'+arm"),
 ("E=BASE/('a1-pitch-feedback-root-'", "E=BASE/('a1-first-state-method-disabled-'+arm+'-'"),
 ("input_scope=PF.FeedbackScope();", "input_scope=None;method=None;method_windows={};"),
 ("'scope':'OWN_ORIGINAL_BOUNDED_PITCH_FEEDBACK_RETURN_NO_FIRE'", "'scope':'OWN_TWO_ORIGINAL_INPUTFREE_FIRST_STATE_METHOD_ONLY','method_arm':arm,'input_emissions':0,'admission_started':parent_started"),
 ("   for r,e in endpoints.items():assert window(r)==e.pin.window,'own window identity changed'", "   for r,wid in method_windows.items():assert window(r)==wid,'own window identity changed'"),
 (OLD_ENDPOINT,NEW_ENDPOINT),
 ("   for e in endpoints.values():e.verify();e.check_focus()\n   rotation_attempt_stream=", "   for r,wid in method_windows.items():own_identity(r);assert window(r)==wid,'own method window changed'\n   rotation_attempt_stream="),
 (OLD_OBSERVATION,NEW_OBSERVATION),
 (OLD_PRECLEANUP,NEW_PRECLEANUP),
 (OLD_REAP,NEW_REAP),
 (OLD_FINAL,NEW_FINAL),
 (OLD_CLI,NEW_CLI),
]


def patch_runner(text):
    require(hashlib.sha256(text.encode()).hexdigest()==RUNNER_SHA,'Pitch runner parent pin differs')
    for old,new in CHANGES:text=once(text,old,new)
    return text


def reverse_runner(text):
    for old,new in reversed(CHANGES):text=once(text,new,old)
    require(hashlib.sha256(text.encode()).hexdigest()==RUNNER_SHA,'Pitch runner full inverse differs')
    return text


def expected_runtime(root,parent,api):
    result={}
    for name,want in parent['runtime_dependencies'].items():result[str(root/Path(name).relative_to(PARENT))if Path(name).is_relative_to(PARENT)else name]=want
    for name,want in api['runtime_dependencies'].items():
        mapped=str(root/'method-api'/Path(name).relative_to(API))if Path(name).is_relative_to(API)else name
        if mapped in result:require(result[mapped]==want,'parents disagree on external dependency:'+mapped)
        result[mapped]=want
    result[str(root/'run_dual.py')]=hashlib.sha256(patch_runner(OLD).encode()).hexdigest()
    result[str(root/'method-api/source-manifest.json')]=hashlib.sha256(dump(nested_manifest(root,api))).hexdigest()
    result[str(root/'first_state_inputfree_method.py')]=HELPER_SHA
    return result


def nested_manifest(root,api):
    nested=dict(api)
    nested['runtime_dependencies']={str(root/'method-api'/Path(name).relative_to(API))if Path(name).is_relative_to(API)else name:want for name,want in api['runtime_dependencies'].items()}
    return nested


def verify_package(root):
    root=Path(root).resolve(strict=True);m=json.loads((root/'source-manifest.json').read_text())
    require(m['runtime_reviewed']is False and m['scope']=='DISABLED_INPUTFREE_TWO_ORIGINAL_METHOD_COMPARISON','disabled window gate/scope')
    require(sha(PARENT/'source-manifest.json')==PARENT_SHA and sha(API/'source-manifest.json')==API_SHA,'immutable parent manifests changed')
    parent=json.loads((PARENT/'source-manifest.json').read_text());api=json.loads((API/'source-manifest.json').read_text())
    require(m['runtime_dependencies']==expected_runtime(root,parent,api),'full expected window/method closure hash values differ')
    for path,want in m['runtime_dependencies'].items():require(sha(path)==want,'window dependency pin:'+path)
    require(reverse_runner((root/'run_dual.py').read_text())==(PARENT/'run_dual.py').read_text(),'full runner inverse differs')
    require('RUNTIME_REVIEWED=False'in(root/'run_dual.py').read_text(),'window runtime gate')
    for name in UNUSED:require('RUNTIME_REVIEWED=False'in(root/name).read_text().replace(' = ','='),'unused input/collector gate:'+name)
    require((root/'method-api/run_first_state.py').read_bytes()==(API/'run_first_state.py').read_bytes(),'old FirstState runner changed')
    require((root/'method-api/original_damage_worker.py').read_bytes()==(API/'original_damage_worker.py').read_bytes(),'unused base CLI changed')
    nested=json.loads((root/'method-api/source-manifest.json').read_text());require(nested==nested_manifest(root,api),'exact nested method manifest/mapping/hash values differ')
    require(nested['runtime_reviewed']is False,'method manifest false required')
    require(len(nested['runtime_dependencies'])==72,'all72method pins required')
    return {'verified':True,'runtime_pins':len(m['runtime_dependencies']),'method_runtime_pins':72,'runner_inverse_sha256':RUNNER_SHA}


def build(output=OUTPUT,*,parent_manifest_sha256=PARENT_SHA):
    require(sha(PARENT/'source-manifest.json')==parent_manifest_sha256==PARENT_SHA,'PitchRoot manifest pin')
    require(sha(API/'source-manifest.json')==API_SHA,'method API manifest pin')
    parent=json.loads((PARENT/'source-manifest.json').read_text());api=json.loads((API/'source-manifest.json').read_text())
    runtime=expected_runtime(Path(output).absolute(),parent,api)
    for source,want in parent['runtime_dependencies'].items():require(sha(source)==want,'PitchRoot source pin:'+source)
    for source,want in api['runtime_dependencies'].items():require(sha(source)==want,'method API source pin:'+source)
    output=Path(output).absolute();output.mkdir(mode=0o700)
    for source in parent['runtime_dependencies']:
        source=Path(source)
        if source.is_relative_to(PARENT):
            relative=source.relative_to(PARENT);data=patch_runner(source.read_text()).encode()if relative==Path('run_dual.py')else source.read_bytes();write(output/relative,data)
    for source in api['runtime_dependencies']:
        source=Path(source)
        if source.is_relative_to(API):write(output/'method-api'/source.relative_to(API),source.read_bytes())
    nested=nested_manifest(output,api)
    write(output/'method-api/source-manifest.json',dump(nested))
    write(output/'first_state_inputfree_method.py',(TOOLS/'first_state_inputfree_method.py').read_bytes())
    require(sha(TOOLS/'first_state_inputfree_method.py')==HELPER_SHA,'method helper source pin differs')
    require(all(sha(path)==want for path,want in runtime.items()),'actual authored package differs from expected source closure')
    manifest={key:parent[key]for key in('host_budget','executable_resolution','world','fixture_preflight_pins','originals','port','runtime_root','displays','existing_profiles')}
    manifest.update(schema='a1.first-state.inputfree-method-window.v1',scope='DISABLED_INPUTFREE_TWO_ORIGINAL_METHOD_COMPARISON',runtime_reviewed=False,native_qualified=False,first_processed_state_proven=False,
      runtime_dependencies=runtime,fixed_modes=['first-state-method'],fixed_arms=['control','trace'],automatic_retry=False,automatic_sequence=False,active_seconds=10,admission_budget_seconds=90,inner_budget_seconds=85,
      parent_package={'path':str(PARENT),'manifest_sha256':PARENT_SHA},method_api_parent={'path':str(API),'manifest_sha256':API_SHA},
      method_api={'root':str(output/'method-api'),'manifest_sha256':sha(output/'method-api/source-manifest.json'),'runtime_reviewed':False},
      boundaries={'no_inputs':True,'no_ai_population':True,'no_gain_or_ack_change':True,'observed_callbacks_only':True,'no_a1_qualification':True,'startup_cleanup_separately_bounded_no_hard_kill_watchdog':True},
      source_pins={str(TOOLS/name):sha(TOOLS/name)for name in('prepare_first_state_inputfree_method.py','first_state_inputfree_method.py')})
    write(output/'source-manifest.json',dump(manifest));receipt={**verify_package(output),'manifest_sha256':sha(output/'source-manifest.json'),'status':'DISABLED_INPUTFREE_METHOD_PAIR_PREPARATION_ONLY'}
    write(output/'build-receipt.json',dump(receipt));return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=OUTPUT);args=parser.parse_args();print(json.dumps(build(args.output),sort_keys=True))
