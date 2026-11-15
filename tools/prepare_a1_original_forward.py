"""Offline exact application for ONE disabled normal W translation condition."""
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

PARENT=Path('/srv/tse-a1-original-colt-trouble030-v3-disabled-20261115')
PARENT_SHA='9bd7202c269634ff90c09ffccf24b4b8cecb3cd50878aa595df87720bbede9f2'
SOURCES=('a1_original_forward.py','prepare_a1_original_forward.py','test_a1_original_forward.py','test_a1_original_forward_ports.py','test_a1_original_forward_window.py','test_prepare_a1_original_forward.py')

def need(ok,why):
    if not ok:raise ValueError('forward preparation: '+why)
def read(path):
    p=Path(path).resolve(strict=True)
    with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:return f.read()
def digest(data):return hashlib.sha256(data).hexdigest()
def sha(path):return digest(read(path))
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()

def fragments():return [
 ('import a1_colt_trouble_condition as TC','import a1_colt_trouble_condition as TC\nimport a1_original_forward as WF'),
 ('MW=RP.bind(IMW)','MW=WF.bind(IMW,RP)'),
 ('first-state-method','original-forward'),
 ("arm in('control','trace')","arm=='control'"),
 ('fixed normal Original respawn condition arm required','one normal Original forward control required'),
 ('ssam-a1-colt-trouble030-disabled-20261115','ssam-a1-forward-disabled-20261115'),
 ("'a1-colt-trouble030-disabled-'","'a1-forward-disabled-'"),
 ('NORMAL_ORIGINAL_RESPAWN030_COLT_LITTLE_TROUBLE_V1','ORIGINAL_FORWARD_TRANSLATION_V1'),
 ('TC.select_case_base(BASE,evidence_ram_base)','WF.select_case_base(BASE,evidence_ram_base)'),
 ('TC.volume_budget(host_sample,evidence_ram_base is not None,ram_free)','WF.volume_budget(host_sample,evidence_ram_base is not None,ram_free)'),
 (" def save():(E/'result.json').write_text(json.dumps(report,indent=2))"," def save():WF.save_report(E/'result.json',report)"),
 ("fire_journal=RP.FireJournal(time.monotonic);FireTransport=RP.make_transport_class(X11Transport)","fire_journal=RP.FireJournal(time.monotonic);FireTransport=WF.make_transport_class(X11Transport)"),
 ("endpoints[role]=Endpoint(pin,t,lambda:own_identity('vanilla'),lambda:display_guard(number))","endpoints[role]=WF.make_endpoint_class(Endpoint)(pin,t,lambda:own_identity('vanilla'),lambda:display_guard(number))"),
 ("   rotation_attempt_stream=(E/'rotation-read-attempts.jsonl').open('w');streams.append(rotation_attempt_stream)","   raw_budget=WF.JournalBudget()\n   rotation_attempt_stream=WF.open_journal(E/'rotation-read-attempts.jsonl',raw_budget);streams.append(rotation_attempt_stream)"),
 ("rotation_stream=(E/'rotation-pairs.jsonl').open('w')","rotation_stream=WF.open_journal(E/'rotation-pairs.jsonl',raw_budget)"),
 ("sample_stream=(E/'inventory.jsonl').open('w')","sample_stream=WF.open_journal(E/'inventory.jsonl',raw_budget)"),
 ('ownership_reads=RP.OwnershipReads(E,time.monotonic,parent_started+85.)','ownership_reads=WF.ownership_reads(RP,E,time.monotonic,parent_started+85.)'),
 ('normal_respawn_fire_only=True','normal_forward_only=True'),
 ('RP.publish_attempts(report,method)','WF.publish_attempts(report,method)'),
 ("   report['status']=MW.candidate_status(report,method)","   try:report['case_output_budget']=WF.require_case_budget(E)\n   except BaseException as error:report['errors'].append('case output budget:'+repr(error))\n   report['status']=MW.candidate_status(report,method)"),
 ('first_state_method','forward_method'),
 ('normal Original respawn condition incomplete','normal Original forward condition incomplete'),
 ('Disabled normal Original respawn FIXEDTARGET030 condition; separate control/trace arms','Disabled ONE normal Original W translation condition; control only'),
 ("choices=('control','trace')","choices=('control',)"),
 ("parser.add_argument('--evidence-ram-base');args=parser.parse_args();main(args.seconds,args.mode,args.arm,args.evidence_ram_base)","args=parser.parse_args();main(args.seconds,args.mode,args.arm)")]

def transform_runner(data,reverse=False):
    original=read(PARENT/'run_dual.py').decode();text=data.decode()
    # Counts refer to each sequential application, including fragments inserted
    # by earlier steps, rather than broad removal of diagnostic/source lines.
    snapshots=[];working=original
    for old,new in fragments():
        count=working.count(old);need(count>0,'exact original fragment '+old[:65]);snapshots.append((old,new,count));working=working.replace(old,new)
    for a,b,count in reversed(snapshots)if reverse else snapshots:
        old,new=(b,a)if reverse else(a,b)
        need(text.count(old)==count,'unambiguous source fragment '+old[:65]);text=text.replace(old,new)
    if reverse:need(text==original,'whole Runner inverse')
    else:need(text==working,'whole Runner application')
    return text.encode()

def segment(data,name):
    tree=ast.parse(data);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
    return '\n'.join(data.decode().splitlines()[n.lineno-1:n.end_lineno])

def prove_primitives():
    source=read(PARENT/'a1_colt_trouble_method.py');new=read(Path(__file__).with_name('a1_original_forward.py'));proof={}
    transforms={
      'fire_pulse':('forward_pulse', [('def fire_pulse(', 'def forward_pulse('),("endpoint.down('fire'","endpoint.down('forward'"),("endpoint.up('fire'","endpoint.up('forward'"),("endpoint.released('fire'","endpoint.released('forward'"),('native_respawn_proven=False','exact_action_ack_proven=False')]),
      'make_transport_class':('make_transport_class',[('FireTransport','ForwardTransport'),('normal XTest Button1 path','normal XTest W Key path'),("control=='fire'","control=='forward'"),('only original normal Fire','only original normal W'),('self.t.XTestFakeButtonEvent','self.t.XTestFakeKeyEvent'),('args=(self.d,1,int(down),0)',"args=(self.d,self.keys['forward'],int(down),0)")])}
    for old,(name,pairs)in transforms.items():
        body=segment(source,old);expected=body
        for a,b in pairs:need(a in expected,'primitive source fragment');expected=expected.replace(a,b)
        actual=segment(new,name);need(actual==expected,'exact production primitive derivation '+old)
        for a,b in reversed(pairs):actual=actual.replace(b,a)
        need(actual==body,'whole primitive inverse '+old)
        proof[name]={'parent_body_sha256':digest(body.encode()),'new_body_sha256':digest(expected.encode()),'exact_whole_inverse':True}
    return proof

def rebase(pins,destination,files):
    out={}
    for name,pin in pins.items():
        p=Path(name)
        if p.is_relative_to(PARENT):
            rel=str(p.relative_to(PARENT));need(rel in files,'copied actual dependency');name=str(destination/rel);pin=digest(files[rel])
        need(name not in out,'unique pin');out[name]=pin
    return out

def files_for(destination):
    destination=Path(destination);need(sha(PARENT/'source-manifest.json')==PARENT_SHA,'exact immutable D3 parent')
    primitive=prove_primitives()
    files={str(p.relative_to(PARENT)):read(p)for p in sorted(PARENT.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix!='.pyc'}
    before=dict(files);files['run_dual.py']=transform_runner(files['run_dual.py'])
    need(transform_runner(files['run_dual.py'],True)==before['run_dual.py'],'whole inverse')
    for name in SOURCES:files[name]=read(Path(__file__).with_name(name))
    collector='collector/a1_original_input_collector.py';c=files[collector].decode();matches=re.findall(r'^PRIVATE = Path\([^\n]+\)$',c,re.M)
    need(len(matches)==1,'one unused Collector private path');files[collector]=c.replace(matches[0],f'PRIVATE = Path({str(destination/"collector")!r})').encode()
    m=json.loads(files['source-manifest.json']);nm=json.loads(files['method-api/source-manifest.json']);cm=json.loads(files['collector/source-manifest.json'])
    need(m['runtime_reviewed']is False and nm['runtime_reviewed']is False and cm['runtime_reviewed']is False,'all parent active manifests disabled')
    condition=dict(condition='ORIGINAL_FORWARD_TRANSLATION_V1',new_condition=True,requested_seconds=.1,actual_native_input_calls=2,control='forward',maximum_actions=1,maximum_role_read_attempts_including_initial=16,
      ownership_payload_cap_bytes=24*1024**2,raw_journal_cap_bytes=64*1024**2,total_case_cap_bytes=152*1024**2,minimum_disk_free_bytes=8816427008,minimum_mem_available_bytes=1744830464,
      persistent_evidence_only=True,no_trace=True,no_mouse=True,no_fire=True,exact_action_ack_proven=False,direction_calibrated=False,first_valid_state_damage_proven=False,
      parent_difficulty=3,parent_difficulty_name='Serious',parent_difficulty_unchanged=True,hard2_proven=False,automatic_retry=False)
    for item in(m,nm):
        item.update(runtime_reviewed=False,native_qualified=False,scope='DISABLED_ORIGINAL_FORWARD_TRANSLATION_V1_NOT_A1',forward_condition=copy.deepcopy(condition),fixed_arms=['control'],fixed_modes=['original-forward'])
        for key in('little_trouble_condition','original_respawn_condition','registered_damage_contract','natural_ai_condition'):
            if key in item:item[key]['historical_parent_condition_only']=True
        item['active_seconds']=None
    m.update(native_ready=False,forward_parent={'path':str(PARENT),'manifest_sha256':PARENT_SHA},forward_primitive_proof=primitive,
      prospective_disk_reserves={'floor_bytes':8*1024**3,'ownership_bytes':24*1024**2,'raw_journal_bytes':64*1024**2,'case_bytes':64*1024**2,'safety_bytes':64*1024**2,'minimum_free_bytes':8816427008,'native_ready':False,'separate_backup_capacity_required':True},
      native_summary_scope='JOIN_AND_FORWARD_TRANSLATION_ONLY',prior_control_transfer_authorized=False)
    cm['source_pins']=rebase(cm['source_pins'],destination,files);files['collector/source-manifest.json']=encoded(cm)
    nm['runtime_dependencies']=rebase(nm['runtime_dependencies'],destination,files);files['method-api/source-manifest.json']=encoded(nm)
    m['runtime_dependencies']=rebase(m['runtime_dependencies'],destination,files)
    for name in SOURCES:m['runtime_dependencies'][str(destination/name)]=digest(files[name])
    m['method_api']={'root':str(destination/'method-api'),'manifest_sha256':digest(files['method-api/source-manifest.json']),'runtime_reviewed':False}
    m['forward_source_pins']={str(Path(__file__).with_name(name)):digest(files[name])for name in SOURCES}
    files['source-manifest.json']=encoded(m)
    immutable=[n for n in before if n not in('run_dual.py','source-manifest.json','method-api/source-manifest.json',collector,'collector/source-manifest.json')]
    need(all(files[n]==before[n]for n in immutable),'all other parent files byte identical')
    for name,data in files.items():
        if name.endswith('.py'):ast.parse(data)
    return files,{'primitive_inverses':primitive,'immutable_parent_files':immutable,'unchanged_parent_files':len(immutable),'changed_parent_files':[n for n in before if files[n]!=before[n]],'new_files':list(SOURCES)}

def prepare(destination):
    destination=Path(destination).resolve();need(not destination.exists()and not destination.is_relative_to(PARENT),'fresh isolated disabled destination')
    files,proof=files_for(destination)
    # Every actual original parent dependency is verified; no rebaseline.
    for manifest,key in(('source-manifest.json','runtime_dependencies'),('method-api/source-manifest.json','runtime_dependencies'),('collector/source-manifest.json','source_pins')):
        for name,pin in json.loads(read(PARENT/manifest))[key].items():need(sha(name)==pin,'actual parent pin '+name)
    outer=json.loads(files['source-manifest.json']);nested=json.loads(files['method-api/source-manifest.json']);cm=json.loads(files['collector/source-manifest.json'])
    for pins in(outer['runtime_dependencies'],nested['runtime_dependencies'],cm['source_pins']):
        for name,pin in pins.items():
            p=Path(name);value=digest(files[str(p.relative_to(destination))])if p.is_relative_to(destination)else sha(p)
            need(value==pin,'complete generated actual pin '+name)
    total=sum(len(b)for b in files.values());v=os.statvfs(destination.parent);free=v.f_bavail*v.f_frsize
    need(free>=8*1024**3+64*1024**2+total,'8GiB+64MiB+exact offline copy')
    destination.mkdir(mode=0o700)
    for name,data in files.items():
        p=destination/name;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    return dict(destination=str(destination),manifest_sha256=digest(files['source-manifest.json']),controller_sha256=digest(files['run_dual.py']),nested_manifest_sha256=digest(files['method-api/source-manifest.json']),
      runtime_pins=len(outer['runtime_dependencies']),nested_pins=len(nested['runtime_dependencies']),collector_pins=len(cm['source_pins']),copied_bytes=total,free_before=free,runtime_reviewed=False,native_ready=False,qualified=False,proof=proof)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);print(json.dumps(prepare(p.parse_args().output),sort_keys=True,indent=2))
