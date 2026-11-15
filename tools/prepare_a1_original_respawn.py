"""Offline exact normal-respawn/FIXEDTARGET030 fork; never enable or execute."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re

def module(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'))
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

B=module('prepare_first_state_registered_damage')
read=B.read;sha_file=B.sha_file;encoded=B.encoded;require=B.require;digest=B.digest
PARENT=Path('/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115')
PARENT_SHA='1b58376cc824a597fd16be43fb8f7a956467dc05dfa1300c364a5fa37d92809b'
CONDITION='NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_COLT_V1'
PINS={
 'run_dual.py':'683a1b1364cdc6057e05781b479251d5005b21b3eaac626b45dcfd4cd75a3f0c',
 'first_state_natural_ai.py':'b7a8c08840acf8ce20ae06a97cb0bbaff37ff58a54d6e537b4a799c32ebdcddf',
 'method-api/first_state_natural_ai.py':'b7a8c08840acf8ce20ae06a97cb0bbaff37ff58a54d6e537b4a799c32ebdcddf',
 'natural-ai/active.ini':'9bd131be6123dd8bde705be92fcd866f2aae431a995ba0328bcfb0110e4f6053'}
CHANGED=tuple(PINS)
SOURCES=('a1_original_respawn_policy.py','a1_original_respawn_method.py','prepare_a1_original_respawn.py',
         'test_a1_original_respawn_policy.py','test_a1_original_respawn_method.py','test_prepare_a1_original_respawn.py')

RUNNER=[
 ('import first_state_inputfree_method as MW','import first_state_inputfree_method as IMW\nimport a1_original_respawn_method as RP\nMW=RP.bind(IMW)'),
 ("PREFIX='ssam-a1-registered-damage-disabled-20261115'","PREFIX='ssam-a1-original-respawn030-disabled-20261115'"),
 ("'a1-registered-damage-disabled-'","'a1-original-respawn030-disabled-'"),
 ('fixed input-free method arm required','fixed normal Original respawn condition arm required'),
 ("'scope':'OWN_TWO_ORIGINAL_INPUTFREE_FIRST_STATE_METHOD_ONLY'","'scope':'NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_COLT_V1'"),
 ('rotation_diagnostics=True,colt_preparation=True)','rotation_diagnostics=True,colt_preparation=False)'),
 ('rotation_diagnostics=True,colt_preparation=True,mouse_input_profile=True)','rotation_diagnostics=True,colt_preparation=False,mouse_input_profile=False)'),
 ('# Join discovery uses the unchanged reader. Enable actual fire geometry only\n    # for the paired, fully joined observation phase; both readers remain read-only.',
  '# New DEAD_READY basis-reader condition; optional live Colt geometry is not\n    # requested. Both unchanged Reader implementations remain strictly read-only.'),
 ("    report['own_method_windows']=dict(method_windows)",
  "    report['own_method_windows']=dict(method_windows)\n    role='vanilla';number=154;ident=records[role]['identity'];di=displays[number]['identity'];wid=method_windows[role]\n    pin=Pin(role,*ident,str(R/role),P.DISPLAYS[role],*di,wid,str(R/('prefix-'+role)))\n    fire_journal=RP.FireJournal(time.monotonic);FireTransport=RP.make_transport_class(X11Transport)\n    t=FireTransport(pin,lambda:display_guard(number),journal=fire_journal)\n    endpoints[role]=Endpoint(pin,t,lambda:own_identity('vanilla'),lambda:display_guard(number))\n    t.focus();time.sleep(.25);endpoints[role].check_focus();assert window(role)==wid"),
 ("    def native_roles():", "    ownership_reads=RP.OwnershipReads(E,time.monotonic,parent_started+85.)\n    report['ownership_reads']=ownership_reads.receipt\n    def native_roles():\n     return ownership_reads.read(native_roles_in_scope)\n    def native_roles_in_scope(ownership_evidence):"),
 ("NAI.capture_ownership(R,E,frame,records,pins,mapping,entity_ids,report['natural_ai_staging'])",
  "NAI.capture_ownership(R,ownership_evidence,frame,records,pins,mapping,entity_ids,report['natural_ai_staging'])"),
 ("     own_identity('botA')\n     frame['natural_ai_ownership']", "     frame['original_replica']=pair['vanilla']\n     own_identity('botA')\n     frame['natural_ai_ownership']"),
 ("     record=report.setdefault('first_state_method',{}))", "     record=report.setdefault('first_state_method',{}),read_roles=native_roles,endpoint=endpoints['vanilla'],journal=fire_journal)"),
 ('report.update(diagnostic_only=True,normal_route_or_fire=False,input_once_proven=False,foreign_hit_proven=False,',
  'report.update(diagnostic_only=True,normal_respawn_fire_only=True,input_once_proven=False,foreign_hit_proven=False,'),
 ('    for e in endpoints.values():\n','    RP.publish_attempts(report,method)\n    for e in endpoints.values():\n'),
 ('input-free method evidence incomplete; see ','normal Original respawn condition incomplete; see '),
 ('Disabled registered damage scope NaturalAI030/Original victim; separate control/trace arms',
  'Disabled normal Original respawn FIXEDTARGET030 condition; separate control/trace arms')]
# Main's actual protected block is indented three spaces, its nested frame four.
RUNNER=[tuple('\n'.join(line[1:]if line.startswith('    ')else line for line in text.split('\n'))
              for text in pair)for pair in RUNNER]

def substitutions(name,config_sha):
    if name=='run_dual.py':return RUNNER
    if name=='natural-ai/active.ini':return [('bot_iTestTarget=-1;','bot_iTestTarget=0;')]
    return [(PINS['natural-ai/active.ini'],config_sha),
      ('NATURAL_AI030_STAGING_V1','ORIGINAL_RESPAWN030_STAGING_V1'),
      ('NATURAL_AI030_SOURCE_OWNERSHIP_V1','ORIGINAL_RESPAWN030_SOURCE_OWNERSHIP_V1')]

def transform(name,data,config_sha,reverse=False):
    text=data.decode()
    pairs=substitutions(name,config_sha)
    for a,b in reversed(pairs)if reverse else pairs:
        old,new=(b,a)if reverse else(a,b)
        expected=2 if old.endswith(('STAGING_V1','SOURCE_OWNERSHIP_V1'))else 1
        require(text.count(old)==expected,'exact condition fragment '+name+': '+old[:90])
        text=text.replace(old,new)
    return text.encode()

def config_hash():
    original=read(PARENT/'natural-ai/active.ini')
    require(digest(original)==PINS['natural-ai/active.ini'],'exact original active config')
    return digest(original.replace(b'bot_iTestTarget=-1;',b'bot_iTestTarget=0;'))

def changed_sources(sources):
    require(set(sources)==set(CHANGED),'exact four source changes')
    require(all(digest(b)==PINS[n]for n,b in sources.items()),'exact complete source pins')
    sha=config_hash();result={n:transform(n,b,sha)for n,b in sources.items()}
    for n,b in result.items():require(reverse_source(n,b)==sources[n],'complete source inverse')
    return result

def reverse_source(name,data):
    require(name in PINS,'known inverse source')
    result=transform(name,data,config_hash(),True)
    require(digest(result)==PINS[name],'whole source inverse pin')
    return result

def contracts(outer,nested):
    a,b=copy.deepcopy(outer),copy.deepcopy(nested)
    condition={'condition':CONDITION,'new_condition':True,'readiness_changed':True,
      'native_input_attempts':2,'ownership_read_namespace_changed':True,
      'ownership_reads_including_initial_max':1024,'ownership_single_receipt_bytes':1536*1024,
      'ownership_aggregate_receipt_payload_bytes':2*1536*1024,
      'ownership_full_single_receipt_reserved_before_each_read':True,
      'ownership_capture_validator_and_private_json_unchanged':True,
      'requested_fire_seconds':.1,'actual_hold_and_release':'measured; no100ms ACK promise',
      'preparation':'real observed positive health then dead MayRespawn2/neutral before Arm, otherwise FAIL',
      'reader':'unchanged basis Reader without optional live Colt geometry; no fallback',
      'basis_reader_colt_preparation':False,'basis_reader_mouse_input_profile':False,
      'per_frame_mouse_gain_prescan_globals_requested':False,
      'startup_mouse_intervention_and_markers_unchanged':True,
      'separate_nosmooth_controls_effective_double_read_unchanged':True,
      'bot_build':'030','fixed_test_target_global_slot':0,'actual_actors':2,'os_roles':3,
      'actual_client_fire_and_server_ack_required':True,'normal_and_fatal_colt_chain_required':True,
      'first_valid_state_damage_proven':False,'bot_victim_proven':False,'aim_or_gain_qualified':False,
      'native_observation_seconds':10,'ttl_seconds':15,'ack_seconds':2,'hold_ceiling_seconds':.35,
      'frame_acquisition_seconds':.2,'frame_acquisition_attempts':8,'input_reserve_seconds':2.35,
      'actions_ceiling':48,'input_attempts_ceiling':96,'inner_seconds':85,'outer_seconds':90,
      'unchanged_original_reader_core_js_schema_limits':True,'qualified':False}
    for item in(a,b):
        item.update(runtime_reviewed=False,native_qualified=False,first_processed_state_proven=False,
          scope='DISABLED_NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_NOT_A1_QUALIFICATION',original_respawn_condition=copy.deepcopy(condition))
        item['registered_damage_contract']['inputs']=2
        item['registered_damage_contract']['inputfree_parent_only']=False
        item['registered_damage_contract']['condition']=CONDITION
        item['natural_ai_condition'].update(config_sha256=config_hash(),test_target=0,ownership_schema='ORIGINAL_RESPAWN030_SOURCE_OWNERSHIP_V1')
    a.update(native_ready=False,prior_control_transfer_authorized=False,new_matched_control_required=True)
    a['original_respawn_parent']={'path':str(PARENT),'manifest_sha256':PARENT_SHA}
    b['qualified']=False
    return a,b

def repin(pins,dest,files):
    result={}
    for name,pin in pins.items():
        path=Path(name)
        if path.is_relative_to(PARENT):
            relative=str(path.relative_to(PARENT));require(relative in files,'copied pin absent')
            name=str(dest/relative);pin=digest(files[relative])
        require(name not in result,'duplicate rebased dependency');result[name]=pin
    return result

def prepare(destination):
    dest=Path(destination).resolve();require(not dest.exists()and not dest.is_relative_to(PARENT),'fresh separate destination')
    require(digest(read(PARENT/'source-manifest.json'))==PARENT_SHA,'exact disabled registered v3 parent')
    m=json.loads(read(PARENT/'source-manifest.json'));nm=json.loads(read(PARENT/'method-api/source-manifest.json'))
    require(m['runtime_reviewed']is False and nm['runtime_reviewed']is False and m['native_ready']is False,'disabled parent')
    for pins in(m['runtime_dependencies'],nm['runtime_dependencies']):
        for name,pin in pins.items():require(sha_file(name)==pin,'unchanged parent dependency: '+name)
    files={str(p.relative_to(PARENT)):read(p)for p in sorted(PARENT.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix!='.pyc'}
    before=dict(files);files.update(changed_sources({n:files[n]for n in CHANGED}))
    collector='collector/a1_original_input_collector.py';c=files[collector].decode()
    matches=re.findall(r'^PRIVATE = Path\([^\n]+\)$',c,re.M);require(len(matches)==1,'unused collector private path')
    files[collector]=c.replace(matches[0],f'PRIVATE = Path({str(dest/"collector")!r})').encode()
    for n in SOURCES:files[n]=read(Path(__file__).with_name(n))
    m,nm=contracts(m,nm)
    cm=json.loads(files['collector/source-manifest.json']);cm['runtime_reviewed']=False
    cm['source_pins']=repin(cm['source_pins'],dest,files);files['collector/source-manifest.json']=encoded(cm)
    nm['runtime_dependencies']=repin(nm['runtime_dependencies'],dest,files)
    files['method-api/source-manifest.json']=encoded(nm)
    m['runtime_dependencies']=repin(m['runtime_dependencies'],dest,files)
    for n in SOURCES:m['runtime_dependencies'][str(dest/n)]=digest(files[n])
    m['method_api']={'root':str(dest/'method-api'),'manifest_sha256':digest(files['method-api/source-manifest.json']),'runtime_reviewed':False}
    m['original_respawn_source_pins']={str(Path(__file__).with_name(n)):digest(files[n])for n in SOURCES}
    files['source-manifest.json']=encoded(m)
    expression=rb'^\s*(?:const )?RUNTIME_REVIEWED\s*=\s*(?:True|true|False|false)\b'
    for n,data in before.items():
        if n.endswith(('.py','.js')):require(re.findall(expression,data,re.M)==re.findall(expression,files[n],re.M),'inherited codegate fingerprints')
        if n.startswith('passive-core/'):require(data==files[n],'four immutable qualified Core files')
    require(files['first_state_inputfree_method.py']==before['first_state_inputfree_method.py'],'old inputfree Source immutable')
    for n,data in files.items():
        if n.endswith('.py'):ast.parse(data.decode())
    total=sum(map(len,files.values()));v=os.statvfs(dest.parent)
    require(v.f_bavail*v.f_frsize>=8*1024**3+64*1024**2+total,'8GiB plus64MiB and full copy reserve')
    dest.mkdir(mode=0o700)
    for n,data in files.items():
        p=dest/n;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    return {'destination':str(dest),'manifest_sha256':digest(files['source-manifest.json']),
      'nested_manifest_sha256':digest(files['method-api/source-manifest.json']),'controller_sha256':digest(files['run_dual.py']),
      'runtime_pins':len(m['runtime_dependencies']),'nested_pins':len(nm['runtime_dependencies']),'collector_pins':len(cm['source_pins']),
      'changed_parent_files':[n for n in before if before[n]!=files[n]],'unchanged_parent_files':sum(before[n]==files[n]for n in before),
      'copied_bytes':total,'condition':CONDITION,'runtime_reviewed':False,'native_ready':False,'qualified':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    print(json.dumps(prepare(p.parse_args().output),sort_keys=True,indent=2))
