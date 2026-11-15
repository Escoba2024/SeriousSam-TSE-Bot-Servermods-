"""Offline NEW registered-scope fork of pinned NaturalAI030. Never enables/runs."""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat

PARENT=Path('/srv/tse-a1-natural-ai030-two-actor-status-v2-disabled-20261115')
PARENT_SHA='2c43de1f91809d591a8631a7aeac2c03f02ee365c0b33d00993803c88a4d26b9'
SCOPE='REGISTERED_FIRST_STATE_DAMAGE_V1'
CHANGED=('method-api/observer_body.js','method-api/vendor/observer/observer.js',
 'method-api/vendor/observer/observer_policy.py','method-api/vendor/observer/event-schema.json',
 'method-api/source_loader.py','first_state_inputfree_method.py','run_dual.py')
PINS={'method-api/source_loader.py':'bde6cb3d224dac3c8bfd4b5b634940e6a078a67ccf6d0e553302dec5378cb283',
      'first_state_inputfree_method.py':'9217c35a4653ccf3aa5370a242fc5295dcf1c0b42265f4ca8280ec956b1d2339',
      'run_dual.py':'b86e0a1855e24b696352c133cb816144b69237364c019a00b23a0145df74da4c'}
SOURCES=('first_state_registered_damage_patch.py','first_state_registered_damage_policy.py',
 'prepare_first_state_registered_damage.py','test_first_state_registered_damage_patch.py',
 'test_first_state_registered_damage_policy.py','test_prepare_first_state_registered_damage.py')

def module(name):
    s=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
P=module('first_state_registered_damage_patch')
V=module('first_state_registered_damage_policy')

METHOD=[
 ('Disabled-runner helper for an input-free two-Original method comparison.',
  'Disabled registered-damage-scope helper for input-free NaturalAI030/Original victim.'),
 ('self.record.update(mode=mode,qualified=False,',
  "self.record.update(measurement_scope='REGISTERED_FIRST_STATE_DAMAGE_V1',cutoff_sequence_domain='full_row_sequence',native_sequence_domain='original_native_edge',mode=mode,qualified=False,"),
 ("return 'PASS_LIMITED_FIRST_STATE_METHOD_OBSERVED_CALLBACKS_ONLY'",
  "return 'PASS_LIMITED_REGISTERED_FIRST_STATE_DAMAGE_METHOD_CALLBACKS_ONLY'")]
RUNNER=[
 ("PREFIX='ssam-a1-natural-ai030-disabled-20261115'","PREFIX='ssam-a1-registered-damage-disabled-20261115'"),
 ("'a1-first-state-autodrain-disabled-'","'a1-registered-damage-disabled-'"),
 ('Disabled input-free two-Original method comparison; separate declared control/trace arms',
  'Disabled registered damage scope NaturalAI030/Original victim; separate control/trace arms')]
LOADER=[('a1_frozen_observer_policy','a1_registered_first_state_damage_v1_policy')]

def require(ok,s):
    if not ok:raise ValueError(s)
def digest(b):return hashlib.sha256(b).hexdigest()
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()

def read(path,maximum=16*1024*1024):
    p=Path(path).resolve(strict=True)
    with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:
        before=os.fstat(f.fileno());require(stat.S_ISREG(before.st_mode)and before.st_size<=maximum,'bounded regular source')
        out=f.read(maximum+1);after=os.fstat(f.fileno())
    require(len(out)<=maximum and(before.st_dev,before.st_ino,before.st_size,before.st_atime_ns,before.st_mtime_ns)==
            (after.st_dev,after.st_ino,after.st_size,after.st_atime_ns,after.st_mtime_ns),'stable no-atime read')
    return out

def sha_file(path):
    p=Path(path).resolve(strict=True)
    with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:
        a=os.fstat(f.fileno());h=hashlib.sha256()
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        z=os.fstat(f.fileno())
    require(stat.S_ISREG(a.st_mode)and(a.st_dev,a.st_ino,a.st_size,a.st_atime_ns,a.st_mtime_ns)==
            (z.st_dev,z.st_ino,z.st_size,z.st_atime_ns,z.st_mtime_ns),'stable pinned file')
    return h.hexdigest()

def simple(n,s,reverse=False):
    pairs={'method-api/source_loader.py':LOADER,'first_state_inputfree_method.py':METHOD,'run_dual.py':RUNNER}[n]
    for a,b in reversed(pairs)if reverse else pairs:
        old,new=(b,a)if reverse else(a,b);require(s.count(old)==1,'exact new-scope source fragment');s=s.replace(old,new,1)
    return s

def reverse_source(n,b):
    s=b.decode()
    if n.endswith('observer_body.js'):return P.reverse_body(s).encode()
    if n.endswith('/observer.js'):return P.reverse_compiled(s).encode()
    if n.endswith('observer_policy.py'):return V.reverse_policy(s).encode()
    if n.endswith('event-schema.json'):return V.reverse_schema(s,read(PARENT/n).decode()).encode()
    old=simple(n,s,True);require(digest(old.encode())==PINS[n],'whole new-scope source inverse');return old.encode()

def changed_sources(files):
    require(set(files)==set(CHANGED),'exact seven changed sources')
    result={}
    for n,b in files.items():
        s=b.decode()
        if n.endswith('observer_body.js'):new=P.patch_body(s)
        elif n.endswith('/observer.js'):new=P.patch_compiled(s)
        elif n.endswith('observer_policy.py'):new=V.patch_policy(s)
        elif n.endswith('event-schema.json'):new=V.patch_schema(s)
        else:
            require(digest(b)==PINS[n],'exact source parent pin');new=simple(n,s)
        result[n]=new.encode();require(reverse_source(n,result[n])==b,'whole source inverse')
    return result

def contracts(outer,nested):
    a,b=copy.deepcopy(outer),copy.deepcopy(nested)
    contract={'measurement_scope':SCOPE,'wire_schema':V.WIRE,'new_condition':True,'full18_replay_accepted':False,
      'queue_full_rows':64,'max_native_edges':16384,'old_limits_unchanged':True,'inputs':0,
      'excluded_only_after_real_leave':True,'pending_relevant_descendant':'INCOMPLETE_FAIL_NO_BACKFILL',
      'explicit_false_chain_or_respawn_source':'INCOMPLETE_FAIL; missing/nonapplicable optional fields not invented',
      'receive_damage_required':'actual nonnull inflictor and chain_bound true on both Enter/Leave',
      'native_sequence':'original unchanged','row_sequence':'separate contiguous retained rows',
      'positive_cutoff':'S full_row_sequence and native counters from that exact raw packet',
      'final_denominator':'F exact final raw packet; no rewriting S or F',
      'after_S_admitted_cleanup_leaves':'raw retained through F; never added to positive S window',
      'first_state_semantic_full18_validator_transfer_authorized':False,
      'first_state_proven':False,'damage_proven':False,'native_qualified':False}
    for x in(a,b):
        x.update(runtime_reviewed=False,native_qualified=False,first_processed_state_proven=False,
                 scope='DISABLED_REGISTERED_FIRST_STATE_DAMAGE_METHOD_NOT_A1_QUALIFICATION',
                 registered_damage_contract=copy.deepcopy(contract))
    a.update(native_ready=False,prior_control_transfer_authorized=False,new_matched_control_required=True)
    a['natural_ai_condition']['guard_deadline_or_js_changes']=True
    a['natural_ai_condition']['registered_scope_note']='JS/schema changed by new registered measurement; guards/deadlines/staging unchanged'
    a['registered_damage_parent']={'path':str(PARENT),'manifest_sha256':PARENT_SHA}
    b['qualified']=False
    return a,b

def repin(pins,dest,files):
    out={}
    for name,pin in pins.items():
        p=Path(name)
        if p.is_relative_to(PARENT):
            n=str(p.relative_to(PARENT));require(n in files,'missing copied dependency');name=str(dest/n);pin=digest(files[n])
        require(name not in out,'duplicate rebased dependency');out[name]=pin
    return out

def prepare(destination):
    dest=Path(destination).resolve();require(not dest.exists()and not dest.is_relative_to(PARENT),'fresh destination only')
    require(digest(read(PARENT/'source-manifest.json'))==PARENT_SHA,'exact NaturalAI030 statusV2 parent')
    m=json.loads(read(PARENT/'source-manifest.json'));nm=json.loads(read(PARENT/'method-api/source-manifest.json'))
    require(m['runtime_reviewed']is False and nm['runtime_reviewed']is False,'disabled parent gates')
    for pins in(m['runtime_dependencies'],nm['runtime_dependencies']):
        for path,pin in pins.items():require(sha_file(path)==pin,'parent dependency changed: '+path)
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
    m['registered_damage_source_pins']={str(Path(__file__).with_name(n)):digest(files[n])for n in SOURCES}
    files['source-manifest.json']=encoded(m)
    expression=rb'^\s*(?:const )?RUNTIME_REVIEWED\s*=\s*(?:True|true|False|false)\b'
    for n,b in before.items():
        if n.endswith(('.py','.js')):
            require(re.findall(expression,b,re.M)==re.findall(expression,files[n],re.M),'no code gate changes')
        if n.startswith('passive-core/'):require(b==files[n],'immutable passive core')
    for n,b in files.items():
        if n.endswith('.py'):ast.parse(b.decode())
    total=sum(map(len,files.values()));free=os.statvfs(dest.parent).f_bavail*os.statvfs(dest.parent).f_frsize
    require(free>=8*1024**3+64*1024**2+total,'8GiB floor plus64MiB reserve and full output')
    dest.mkdir(mode=0o700)
    for n,b in files.items():
        p=dest/n;p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(b);f.flush();os.fsync(f.fileno())
    return {'destination':str(dest),'manifest_sha256':digest(files['source-manifest.json']),
      'nested_manifest_sha256':digest(files['method-api/source-manifest.json']),
      'controller_sha256':digest(files['run_dual.py']),'observer_sha256':digest(files['method-api/vendor/observer/observer.js']),
      'runtime_pins':len(m['runtime_dependencies']),'nested_pins':len(nm['runtime_dependencies']),
      'collector_pins':len(cm['source_pins']),'changed_parent_files':[n for n in before if before[n]!=files[n]],
      'unchanged_parent_files':sum(before[n]==files[n]for n in before),'bytes_written':total,
      'measurement_scope':SCOPE,'runtime_reviewed':False,'native_qualified':False,'first_state_proven':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    print(json.dumps(prepare(p.parse_args().output),sort_keys=True,indent=2))
