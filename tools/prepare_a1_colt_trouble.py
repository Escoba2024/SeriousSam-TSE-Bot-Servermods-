"""Offline NEW LittleTrouble030 normal-respawn condition; never enable/run."""
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
    s=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

B=module('prepare_a1_original_respawn')
read=B.read;digest=B.digest;encoded=B.encoded;require=B.require;sha_file=B.sha_file
PARENT=Path('/srv/tse-a1-original-respawn-fixedtarget030-v5-disabled-20261115')
PARENT_SHA='6ca287db33640b859b2854df19dfd1acd78b6b4f91ab2fc3879b1d8d2a33a9a7'
CONDITION='NORMAL_ORIGINAL_RESPAWN030_COLT_LITTLE_TROUBLE_V1'
STARTUP_REL=Path('server/Scripts/Dedicated/BotTest/1_begin.ini')
STARTUP_FIXTURE=Path('/srv/tse-arena-isolated-20261111')/STARTUP_REL
NAV=Path('/srv/tse-cecil-full-private-assets-20261107/DM_LittleTrouble_6C64BF87.nav')
NAV_SHA='252d7e4c003804fe9ae2afef359843feb39b5dda29c1d6eadb0835fbe64a30ac'
WORLD_SHA='e74e48e99bcc6e945500e1f28921c443515898791bfbca4d7ebf1ae61a26593c'
CATALOG=Path('/srv/tse-nav20-030-skulls600-diag1-timestamps-disabled-20261115/map-catalog.json')
CATALOG_SHA='11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3'
PARENT_SOURCE={n:n for n in('run_dual.py','first_state_natural_ai.py','method-api/first_state_natural_ai.py','natural-ai/active.ini')}
PARENT_SOURCE.update({'a1_colt_trouble_method.py':'a1_original_respawn_method.py','a1_colt_trouble_policy.py':'a1_original_respawn_policy.py'})
SOURCES=('a1_colt_trouble_condition.py','prepare_a1_colt_trouble.py','test_a1_colt_trouble_condition.py','test_prepare_a1_colt_trouble.py')
SAFETY=64*1024**2
METADATA=64*1024**2
RAW_RESERVE=512*1024**2
CASE_RESERVE=64*1024**2
NATIVE_MINIMUM=8*1024**3+SAFETY+METADATA+RAW_RESERVE+CASE_RESERVE

def fragments(name):
    config=digest(read(PARENT/'natural-ai/active.ini').replace(b'bot_fMoveFactor=1;',b'bot_fMoveFactor=0;'))
    if name=='natural-ai/active.ini':return [('bot_fMoveFactor=1;','bot_fMoveFactor=0;')]
    if name=='run_dual.py':return [
      ('import a1_original_respawn_method as RP','import a1_colt_trouble_method as RP\nimport a1_colt_trouble_condition as TC'),
      ("def main(duration=90,mode='first-state-method',arm=None):","def main(duration=90,mode='first-state-method',arm=None,evidence_ram_base=None):"),
      ('ssam-a1-original-respawn030-disabled-20261115','ssam-a1-colt-trouble030-disabled-20261115'),
      (" E=BASE/('a1-original-respawn030-disabled-'", " CASE_BASE,case_volume_receipt=TC.select_case_base(BASE,evidence_ram_base)\n E=CASE_BASE/('a1-original-respawn030-disabled-'"),
      ("'a1-original-respawn030-disabled-'","'a1-colt-trouble030-disabled-'"),
      ('NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_COLT_V1',CONDITION),
      ("q.get('mapname')=='Red Station'","q.get('mapname')=='Little Trouble'"),
      (" report['native_summary_scope']='JOIN_PREARM_ONLY'"," report['evidence_volume']=case_volume_receipt\n report['native_summary_scope']='JOIN_PREARM_ONLY'"),
      ("  try:return budget.add(time.monotonic(),Path('/proc/stat').read_text().splitlines()[0],int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024,shutil.disk_usage('/srv').free)",
       "  try:\n   host_sample=budget.add(time.monotonic(),Path('/proc/stat').read_text().splitlines()[0],int(next(x.split()[1]for x in Path('/proc/meminfo').read_text().splitlines()if x.startswith('MemAvailable:')))*1024,shutil.disk_usage('/srv').free)\n   ram_volume=os.statvfs(CASE_BASE)if evidence_ram_base is not None else None\n   ram_free=ram_volume.f_bavail*ram_volume.f_frsize if ram_volume is not None else None\n   volume_sample={'host_sample':host_sample,'ram_free_bytes':ram_free}\n   report.setdefault('evidence_volume_samples',[]).append(volume_sample)\n   volume_sample['accepted_reserves']=TC.volume_budget(host_sample,evidence_ram_base is not None,ram_free)\n   return host_sample"),
      ("args=parser.parse_args();main(args.seconds,args.mode,args.arm)","parser.add_argument('--evidence-ram-base');args=parser.parse_args();main(args.seconds,args.mode,args.arm,args.evidence_ram_base)"),
      ("report['natural_ai_staging']=NAI.stage_candidate(transaction,R,DRAFT,E);save()",
       "report['natural_ai_staging']=NAI.stage_candidate(transaction,R,DRAFT,E);save()\n   report['little_trouble_staging']=TC.stage_startup(transaction,R,E);save()")]
    if name=='a1_colt_trouble_method.py':return [
      ('import copy','import copy\nimport a1_colt_trouble_condition as TC'),
      ('OWNERSHIP_TOTAL_LIMIT=2*OWNERSHIP_RECEIPT_LIMIT','OWNERSHIP_TOTAL_LIMIT=TC.OWNERSHIP_PAYLOAD_LIMIT'),
      ('a1_original_respawn_policy','a1_colt_trouble_policy'),
      ('                bind_replica(native,frame)','                bind_replica(native,frame)\n                row[\'normal_role_geometry\']=TC.role_geometry(native,frame)'),
      ('                    self.frame=self.read_roles()',"                    self.record['pre_arm_hp_drop']=TC.require_hp_drop(first,self.record['readiness_reads'])\n                    self.frame=self.read_roles()"),
      ("    r=window.record", "    r=window.record\n    if r.get('pre_arm_hp_drop',{}).get('hp_drop_observed')is not True:return 'FAIL'"),
      ('NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_COLT_V1',CONDITION),
      ('PASS_LIMITED_NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_','PASS_LIMITED_NORMAL_ORIGINAL_RESPAWN_LITTLE_TROUBLE030_')]
    if name=='a1_colt_trouble_policy.py':return [('NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_COLT_V1',CONDITION)]
    return [('cdf68caf9ff559de56b2808f2db12acefb8c87c8d002187aaf29adb674bb3261',config),
      ('70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6',NAV_SHA),
      ('RedStation_5AF1A276.nav','DM_LittleTrouble_6C64BF87.nav'),
      ('ORIGINAL_RESPAWN030_STAGING_V1','ORIGINAL_COLT_TROUBLE030_STAGING_V1'),
      ('ORIGINAL_RESPAWN030_SOURCE_OWNERSHIP_V1','ORIGINAL_COLT_TROUBLE030_SOURCE_OWNERSHIP_V1'),
      ("RedStation.wld','1','193','ff3776e0','e4571656'","DM_LittleTrouble.wld','1','110','4060d0dd','980013d4'"),
      ('actual Red Nav loaded','actual LittleTrouble Nav loaded')]

def transform(name,data,reverse=False):
    text=data.decode();original=read(PARENT/PARENT_SOURCE[name]).decode()
    pairs=[p for p in fragments(name)if p[0]!=p[1]]
    for a,b in reversed(pairs)if reverse else pairs:
        old,new=(b,a)if reverse else(a,b)
        count=original.count(a)
        require(count>0 and text.count(old)==count,'exact LittleTrouble fragment '+name+': '+old[:70])
        text=text.replace(old,new)
    return text.encode()

def generated_sources():
    require(sha_file(PARENT/'source-manifest.json')==PARENT_SHA,'exact D5 parent')
    result={n:transform(n,read(PARENT/p))for n,p in PARENT_SOURCE.items()}
    for n,b in result.items():require(reverse_source(n,b)==read(PARENT/PARENT_SOURCE[n]),'whole source inverse')
    return result

def reverse_source(name,data):
    result=transform(name,data,True)
    require(result==read(PARENT/PARENT_SOURCE[name]),'complete exact parent inverse '+name)
    return result

def repin(pins,dest,files):
    out={}
    for name,pin in pins.items():
        path=Path(name)
        if path.is_relative_to(PARENT):
            rel=str(path.relative_to(PARENT));require(rel in files,'copied dependency')
            name=str(dest/rel);pin=digest(files[rel])
        require(name not in out,'duplicate dependency');out[name]=pin
    return out

def source_ownership_metadata(source):
    """Bind active metadata to actual generated NAI literals, never old notes."""
    literals={}
    for node in ast.parse(source).body:
        if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in('NAV_SHA','TARGETS'):
            require(node.targets[0].id not in literals,'one NAI metadata assignment')
            literals[node.targets[0].id]=ast.literal_eval(node.value)
    require(literals.get('NAV_SHA')==NAV_SHA,'generated exact LittleTrouble NAV hash')
    targets=literals.get('TARGETS')
    require(type(targets)is tuple and len(targets)==6 and targets[2]=='botA/Scripts/Cecil/DM_LittleTrouble_6C64BF87.nav','generated exact LittleTrouble snapshot target')
    return {'nav_sha256':literals['NAV_SHA'],'snapshots_before_seal':list(targets)}

def prepare(destination):
    dest=Path(destination).resolve();require(not dest.exists()and not dest.is_relative_to(PARENT),'fresh disabled destination')
    generated=generated_sources();m=json.loads(read(PARENT/'source-manifest.json'));nm=json.loads(read(PARENT/'method-api/source-manifest.json'))
    require(m['runtime_reviewed']is False and nm['runtime_reviewed']is False and m['native_ready']is False,'disabled parent')
    cm=json.loads(read(PARENT/'collector/source-manifest.json'))
    for pins in(m['runtime_dependencies'],nm['runtime_dependencies'],cm['source_pins']):
        for name,pin in pins.items():require(sha_file(name)==pin,'actual complete parent pin '+name)
    require(sha_file(NAV)==NAV_SHA,'exact existing LittleTrouble Nav')
    require(sha_file(CATALOG)==CATALOG_SHA,'existing reviewed complete map catalog')
    binding=json.loads(read(CATALOG))['maps']['trouble']
    require(binding['world_sha256']==WORLD_SHA and binding['nav_sha256']==NAV_SHA and binding['nodes']==110
      and binding['query_name']=='Little Trouble'and binding['world_crc32']=='4060d0dd'and binding['nav_crc32']=='980013d4'
      and binding['world_path']=='Levels\\LevelsMP\\Deathmatch\\DM_LittleTrouble.wld'
      and binding['private_nav_source']==str(NAV),'exact complete LittleTrouble binding')
    TC=module('a1_colt_trouble_condition');require(sha_file(STARTUP_FIXTURE)==TC.STARTUP_SHA,'actual unchanged Startup3 fixture')
    files={str(p.relative_to(PARENT)):read(p)for p in sorted(PARENT.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix!='.pyc'}
    before=dict(files);files.update(generated)
    for n in SOURCES:files[n]=read(Path(__file__).with_name(n))
    collector='collector/a1_original_input_collector.py';c=files[collector].decode();matches=re.findall(r'^PRIVATE = Path\([^\n]+\)$',c,re.M)
    require(len(matches)==1,'one unused collector path');files[collector]=c.replace(matches[0],f'PRIVATE = Path({str(dest/"collector")!r})').encode()
    condition=copy.deepcopy(m['original_respawn_condition']);condition.update(condition=CONDITION,new_condition=True,
      map='Levels/LevelsMP/Deathmatch/DM_LittleTrouble.wld',world_sha256=WORLD_SHA,nav_sha256=NAV_SHA,
      start_difficulty=3,spawn_invulnerability=0,move_factor=0,normal_spawns=True,spawn_marker_selected=False,
      observed_hp_drop_required=True,los_proven=False,ownership_aggregate_receipt_payload_bytes=METADATA,
      ownership_1024_receipts_fit_guaranteed=False,operative_metadata_reserve_changed=True,
      old_rp_source_unchanged=True,damage_tolerances_changed=False)
    condition.update(optional_ram_evidence_only=True,ram_fixture_disk_minimum_bytes=TC.RAM_FIXTURE_DISK_MINIMUM,
      ram_mem_available_minimum_bytes=TC.RAM_MEMORY_MINIMUM,ram_volume_minimum_bytes=TC.RAM_VOLUME_MINIMUM,
      existing_host_samples_reused=True,fixture_tools_runtime_remain_on_disk=True,postclose_persistent_exact_copy_required=True)
    for item in(m,nm):
        item.update(runtime_reviewed=False,native_qualified=False,scope='DISABLED_NORMAL_ORIGINAL_COLT_LITTLE_TROUBLE030_NOT_A1_QUALIFICATION',
          little_trouble_condition=copy.deepcopy(condition))
        item['registered_damage_contract']['condition']=CONDITION
        item['natural_ai_condition'].update(config_sha256=digest(files['natural-ai/active.ini']),test_target=0,
          ownership_schema='ORIGINAL_COLT_TROUBLE030_SOURCE_OWNERSHIP_V1',
          **source_ownership_metadata(files['first_state_natural_ai.py']))
        item['natural_ai_condition'].update(parent_control_status_historical_only=True,
          inputs_scope='HISTORICAL_PREARM_AI_OWNERSHIP_ONLY_NOT_CURRENT_CONDITION_TOTAL',
          historical_parent_context_reference='outer natural_ai_condition control_status/inputs; not current method status/input total',
          current_condition=CONDITION,current_condition_native_input_attempts=2)
        item['original_respawn_condition']['historical_parent_condition_only']=True
    m.update(native_ready=False,new_matched_control_required=True,little_trouble_parent={'path':str(PARENT),'manifest_sha256':PARENT_SHA},
      prospective_disk_reserves={'floor_bytes':8*1024**3,'safety_bytes':SAFETY,'ownership_payload_bytes':METADATA,
        'raw_journal_bytes':RAW_RESERVE,'operative_case_and_ancillary_bytes':CASE_RESERVE,
        'minimum_free_bytes':NATIVE_MINIMUM,'output_upper_bound_proven':False,
        'backup_reserve_required_separately':True,'native_ready':False})
    cm['runtime_reviewed']=False;cm['source_pins']=repin(cm['source_pins'],dest,files);files['collector/source-manifest.json']=encoded(cm)
    nm['runtime_dependencies']=repin(nm['runtime_dependencies'],dest,files);files['method-api/source-manifest.json']=encoded(nm)
    m['runtime_dependencies']=repin(m['runtime_dependencies'],dest,files)
    for n in tuple(SOURCES)+('a1_colt_trouble_method.py','a1_colt_trouble_policy.py'):m['runtime_dependencies'][str(dest/n)]=digest(files[n])
    m['runtime_dependencies'][str(NAV)]=NAV_SHA
    m['runtime_dependencies'][str(CATALOG)]=CATALOG_SHA
    m['method_api']={'root':str(dest/'method-api'),'manifest_sha256':digest(files['method-api/source-manifest.json']),'runtime_reviewed':False}
    m['little_trouble_source_pins']={str(Path(__file__).with_name(n)):digest(files[n])for n in SOURCES}
    files['source-manifest.json']=encoded(m)
    gate=rb'^\s*(?:const )?RUNTIME_REVIEWED\s*=\s*(?:True|true|False|false)\b'
    for n,b in before.items():
        if n.endswith(('.py','.js')):require(re.findall(gate,b,re.M)==re.findall(gate,files[n],re.M),'old code gates exact')
        if n.startswith('passive-core/')or n in('a1_original_respawn_method.py','a1_original_respawn_policy.py'):require(b==files[n],'old RP/four Core immutable')
    for n,b in files.items():
        if n.endswith('.py'):ast.parse(b.decode())
    total=sum(map(len,files.values()));v=os.statvfs(dest.parent);free=v.f_bavail*v.f_frsize
    require(free>=8*1024**3+SAFETY+total,'offline copy floor+64MiB+actual bounded copy')
    dest.mkdir(mode=0o700)
    for n,b in files.items():
        p=dest/n;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(b);f.flush();os.fsync(f.fileno())
    return {'destination':str(dest),'manifest_sha256':digest(files['source-manifest.json']),
      'nested_manifest_sha256':digest(files['method-api/source-manifest.json']),'controller_sha256':digest(files['run_dual.py']),
      'runtime_pins':len(m['runtime_dependencies']),'nested_pins':len(nm['runtime_dependencies']),'collector_pins':len(cm['source_pins']),
      'changed_parent_files':[n for n in before if before[n]!=files[n]],'unchanged_parent_files':sum(before[n]==files[n]for n in before),
      'new_files':[n for n in files if n not in before],'copied_bytes':total,'free_before':free,
      'prospective_native_minimum_before_case_and_ancillary':NATIVE_MINIMUM,'runtime_reviewed':False,'native_ready':False,'qualified':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    print(json.dumps(prepare(p.parse_args().output),sort_keys=True,indent=2))
