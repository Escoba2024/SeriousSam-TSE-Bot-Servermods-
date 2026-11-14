"""Guarded private latejoin adapter. Importing launches/reads nothing.

Only the reviewed controller calls this under its existing runtime flock.
Model tests inject every process boundary; Root alone performs native reads.
"""
import copy
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import time

from owned_latejoin_capture import observe_three_roles,exclusive_json
from owned_sync_capture import observe_roles
from ownns_latejoin_preflight import (PROTOCOL,ORIGINALS,FRESH_SECONDS,require,
 validate_prestart,validate_frames,validate_query)
import ownns_latejoin_local_mapping as local_source


def private_stream(path):
 return os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')


def run_owned_launcher(argv,timeout,progress,owners,*,popen=subprocess.Popen,monotonic=time.monotonic):
 require(0<timeout<=20,'existing20s launcher bound')
 child=popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
 owners.append(child) # Retain before first poll/guard can fail.
 end=monotonic()+timeout
 try:
  while True:
   progress();remaining=end-monotonic()
   if remaining<=0:raise TimeoutError('own launcher deadline')
   try:out,err=child.communicate(timeout=min(.1,remaining))
   except subprocess.TimeoutExpired:continue
   require(len(out.encode())+len(err.encode())<=65536,'own launcher log bound')
   require(child.returncode==0,'own launcher failed');return
 finally:
  # This Popen is systemd-run CLI only, never a game or Wine process.
  if child.poll()is None:
   child.terminate()
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:child.kill();child.wait(timeout=3)


def moved_slots(samples):
 anchors={};moved=set()
 for sample in samples:
  for row in sample['players']:
   slot=row['slot'];clock=row.get('spawned_tick',0)
   if slot not in range(8)or not row.get('present')or row.get('health',0)<=0 or clock<=0:continue
   key=(slot,row['entity_id'],row['entity_pointer'],row['world_pointer'],clock)
   point=row['placement'][:3];require(len(point)==3 and all(math.isfinite(v)for v in point),'finite movement observation')
   before=anchors.setdefault(key,point)
   if sum((a-b)**2 for a,b in zip(before,point))>1:moved.add(slot) # Existing A4 one-metre motion boundary.
 return moved


def sync_activity(active,samples,mapping):
 require(mapping==dict(botA=[0,1,2,3],botB=[4,5,6,7],vanilla=[8]),'actual latejoin slot mapping')
 moved=moved_slots(samples);require(moved==set(range(8)),'each own bot needs actual same-life movement')
 for role in ('botA','botB'):
  for local in range(4):
   proof=active['slots'][role+':'+str(local)].get('memory_flag_observations',{})
   count=proof.get('native_fire_flag_observations_with_same_life_source_growth')
   require(type(count)is int and count>0,'each own bot needs bound native fire flag/source growth')
 require(bool(active['server_reported_foreign_kills']),'actual server-reported kill required')
 require('score_change_not_observed'not in active['missing_activity'],'actual query score change required')
 return dict(scope=PROTOCOL,sync_activity_observed=True,qualified=False,functional_pass=False,a4_accepted=False,
  moved_global_slots=sorted(moved),weapon_function_call_proven=False,
  open_a4_diagnostics=copy.deepcopy(active['missing_activity']),a4_diagnostic_status='OPEN_OR_NOT_APPLICABLE_TO_SYNC_PROTOCOL')


def readiness_evidence(*,logs,mapping,samples,queries,contract,attempts,server_log,active_evidence):
 import a4_ordered_memory_v3 as ordered
 import audit_a4_ordered_memory_v3 as audit
 import a4_fire_observer_v2 as original
 require(mapping==dict(botA=[0,1,2,3],botB=[4,5,6,7]),'prejoin actual eight-slot map')
 require(contract['schema']=='OWNNS_PREJOIN8_ORDERED_V1'and contract['groups']==dict(botA_actual=list(range(4)),botB_actual=list(range(4,8))),'closed prejoin read contract')
 expected={r['slot']:r for r in contract['entities']};require(set(expected)==set(range(8)),'eight native entities required')
 require(len(contract['entities'])==8,'no duplicate prejoin entity slots')
 for key in audit.IDENTITY:require(all(type(r[key])is int for r in expected.values()),'typed current native entity')
 for key in ('entity_id','entity_pointer'):require(all(r[key]>0 for r in expected.values())and len({r[key]for r in expected.values()})==8,'unique current prejoin entity')
 require(len({r['world_pointer']for r in expected.values()})==1 and next(iter(expected.values()))['world_pointer']>=0x10000,'current prejoin world')
 journal=ordered.check_attempts(attempts,contract);seen=set();numbered=[];last=0;last_tick=None
 for sample in samples:
  original.check_sample(sample,contract['server_identity']);observation=sample['prejoin_observation'];serial=observation['read_serial']
  require(type(serial)is int and serial>last and serial in journal,'prejoin read serial')
  begin,end=journal[serial];group=observation['group'];require(group in contract['groups'],'prejoin group')
  require(observation==dict(group=begin['group'],read_serial=serial,monotonic_start=begin['monotonic_start'],monotonic_end=end['monotonic_end'])and end['status']=='ok'and begin['phase']=='gameplay','prejoin attempt binding')
  require([r['slot']for r in sample['players']]==contract['groups'][group]and sample['all_selected_present']is True,'complete actual prejoin read group')
  for row in sample['players']:
   require(row.get('present')is True and all(row[k]==expected[row['slot']][k]for k in audit.IDENTITY),'prejoin entity/world changed')
   if row.get('spawned_tick',0)>0:audit.stamp(row['spawned_tick'])
  audit.stamp(sample['game_tick']);require(last_tick is None or sample['game_tick']>=last_tick,'prejoin native clock reversed')
  numbered.append((serial,sample));seen.add(serial);last=serial;last_tick=sample['game_tick']
 require(seen=={s for s,(_,e)in journal.items()if e['status']=='ok'},'successful prejoin read omitted')
 proof={}
 for role in ('botA','botB'):
  source=audit.source_rows(logs[role])
  for local,slot in enumerate(mapping[role]):proof[slot]=audit.slot_evidence(source,numbered,local,slot,expected[slot])
 firing=sorted(s for s,p in proof.items()if p['native_fire_flag_observations_with_same_life_source_growth']>0)
 names={v for k,v in queries[0].items()if re.fullmatch(r'player_\d+',k)}
 for query in queries:validate_query(query,names,queries[0]['mapname'])
 def scores(query):return {query[k]:int(query['frags_'+k[7:]])for k in query if re.fullmatch(r'player_\d+',k)}
 first,last=scores(queries[0]),scores(queries[-1]);positive=any(last[name]>first[name]for name in names)
 current=active_evidence(logs,mapping,samples,[dict(elapsed=i,query=q)for i,q in enumerate(queries)],server_log)
 kills=len(current['server_reported_foreign_kills']);moved=sorted(moved_slots(samples))
 return dict(scope='PRIVATE_PREJOIN20S_READINESS_ONLY',ready=moved==list(range(8))and bool(firing)and(bool(kills)or positive),moved_slots=moved,firing_slots=firing,
  bound_fire_proof=proof,server_reported_own_kills=kills,positive_own_query_frag_delta=positive,qualified=False,functional_pass=False,a4_accepted=False,weapon_function_call_proven=False)


class LatejoinRuntime:
 def __init__(self,*,root,evidence,backend,records,module_pins,unit,probe,pauseprobe,map_name,slot_mapping,sample_host,host_budget):
  self.root=Path(root);self.evidence=Path(evidence);self.B=backend;self.records=records;self.module_pins=module_pins;self.unit=unit
  self.probe=probe;self.pauseprobe=pauseprobe;self.map_name=map_name;self.slot_mapping=slot_mapping
  self.sample_host=sample_host;self.host_budget=host_budget;self.capture=None;self.lock=None;self.check_serial=0;self.last_guard=0.;self.launch_helpers=[]
  self.original_prestart=None;self.original_launch_consumed=False
  self.frame_serial=0
  self.prejoin_binding=None
 def role_guard(self,role):
  identity=self.records[role]['identity'];require(identity is not None,'role not yet bound')
  require(self.B.identity(role,self.unit(role))==identity and self.B.same(identity),'own native role identity changed')
  self.B.verify_modules(role,identity,self.module_pins[role])
  server=self.records['server']['identity'];self.B.same_namespace(identity[0],server[0])
  return list(identity)
 def progress(self):
  now=time.monotonic()
  previous=self.host_budget.previous
  if previous is not None and now-previous[0]>=1:self.sample_host('latejoin-startup')
  if now-self.last_guard>=1:
   for role in tuple(self.module_pins):self.role_guard(role)
   if 'server'in self.module_pins:self.B.isolated_server(self.records['server']['identity'][0])
   if self.capture is None and self.prejoin_binding is not None:
    registry={r:dict(identity=list(v['identity']),unit=self.unit(r))for r,v in self.records.items()}
    require(observe_three_roles(registry)==self.prejoin_binding,'prejoin UDP role binding changed')
   if self.capture is not None and self.capture.owner is not None:self.capture.guard()
   self.last_guard=now
  if self.capture is not None and self.capture.stage!='FOUR_ROLES':self.capture.admission_remaining()
 def clock(self):self.progress();return time.monotonic()
 def remaining(self,maximum):
  return min(maximum,self.capture.admission_remaining())if self.capture is not None else maximum
 def wait(self,check,timeout,message):
  end=time.monotonic()+self.remaining(timeout)
  while True:
   self.progress();require(time.monotonic()<end,message)
   ready=check();self.progress();require(time.monotonic()<end,message)
   if ready:return
   time.sleep(min(.2,max(0,end-time.monotonic())))
 def run_command(self,args,timeout):
  if args[-1]==str(self.root/'launch-vanilla.sh'):
   require(self.capture is not None and self.capture.stage=='ADMITTING','Original requires armed admission stage')
   require(not self.original_launch_consumed and self.original_prestart is not None,'Original launch cannot retry or lack private prestart')
   self.validate_current_prestart(self.original_prestart);self.original_launch_consumed=True
  return run_owned_launcher(args,self.remaining(timeout),self.progress,self.launch_helpers)
 def launcher_receipts(self):
  return [dict(pid=p.pid,returncode=p.poll(),ended=p.poll()is not None)for p in self.launch_helpers]
 def native_frame(self,role):
  self.frame_serial+=1;receipt=dict(role=role,requested_identity=list(self.records[role]['identity']),started=time.monotonic(),status='FAIL')
  try:
   before=self.role_guard(role);identity=self.records[role]['identity'];receipt['identity_before']=before
   first=self.probe.read(identity[0],self.root/role);receipt['native_first']=first
   second=self.probe.read(identity[0],self.root/role);receipt['native_second']=second
   after=self.role_guard(role);receipt['identity_after']=after
   first.update(process_identity_before=before,process_identity_after=after,
    hashes={name:pin['sha256']for name,pin in self.module_pins[role].items()},read_interval=[receipt['started'],time.monotonic()],
    slot_binding_before=[[p['slot'],p['entity_pointer']]for p in first['players']],slot_binding_after=[[p['slot'],p['entity_pointer']]for p in second['players']])
   receipt['status']='GUARDED_READ_COMPLETE_NOT_ATOMIC';return first
  except BaseException as error:receipt['error']=repr(error);raise
  finally:
   receipt['ended']=time.monotonic();exclusive_json(self.evidence/f'private-native-frame-{self.frame_serial}-{role}.json',receipt)
 def frames(self,roles):
  first={r:self.native_frame(r)for r in roles};self.progress()
  time.sleep(min(.2,self.remaining(.2)));self.progress()
  return [first,{r:self.native_frame(r)for r in roles}]
 def admission_frames(self,registry,binding,started,history):
  from ownns_latejoin_preflight import CANDIDATE,finite
  from stability_hard_rules import validate_session
  require(set(registry)=={'server','botA','botB','vanilla'}and self.capture.stage=='ADMITTING','own admission observations only')
  require({r:binding[r]for r in ('server','botA','botB')}==self.capture.before,'old role binding changed before readiness')
  old=self.original_prestart['evidence']['frames'][-1]
  pointers={r:{p['slot']:p['entity_pointer']for p in old[r]['players']}for r in ('server','botA','botB')};pointers['vanilla']={}
  clocks={};previous=None
  while True:
   self.progress();self.capture.admission_remaining()
   require(observe_roles(registry)==binding,'admission endpoint binding changed while waiting')
   frame={};complete=True;first_serial=self.frame_serial+1
   for role in registry:
    sample=self.native_frame(role);frame[role]=sample;self.capture.admission_remaining()
    require(sample['process_identity_before']==binding[role]['identity']==sample['process_identity_after'],'admission frame PID/start changed')
    require(sample['hashes']=={n:CANDIDATE if n=='GameMP.dll'and role in('botA','botB')else ORIGINALS[n]for n in('Engine.dll','EntitiesMP.dll','GameMP.dll')},'admission frame loaded hashes changed')
    begin,end=sample['read_interval'];require(finite(begin)and finite(end)and started<=begin<=end<=time.monotonic(),'admission read interval')
    validate_session(sample);tick=sample['game_tick'];require(finite(tick)and(role not in clocks or tick>=clocks[role]),'admission native clock reversed')
    clocks[role]=tick
    pairs=[[p['slot'],p['entity_pointer']]for p in sample['players']]
    require(sample['slot_binding_before']==pairs,'admission first slot binding differs')
    for position,observed in enumerate((pairs,sample['slot_binding_after'])):
     slots=[p[0]for p in observed]
     allowed=[list(range(9))]
     if role=='vanilla'and 8 not in pointers[role]:allowed.append(list(range(8)))
     require(all(type(s)is int for s in slots)and slots in allowed,'unexpected admission native slots')
     for slot,pointer in observed:
      require(type(pointer)is int and pointer>0x10000,'admission entity pointer bound')
      require(slot not in pointers[role]or pointer==pointers[role][slot],'admission slot/entity changed')
      pointers[role].setdefault(slot,pointer)
     if slots!=list(range(9)):complete=False
    self.progress()
   history.append(dict(first_raw_frame_serial=first_serial,last_raw_frame_serial=self.frame_serial,complete_nine=complete,native_ticks={r:s['game_tick']for r,s in frame.items()}))
   if complete:
    if previous is not None and all(frame[r]['game_tick']>previous[r]['game_tick']for r in registry):
     validate_frames([previous,frame],binding,range(9),[started,time.monotonic()])
     require(observe_roles(registry)==binding,'admission endpoint binding changed after readiness')
     self.progress();self.capture.admission_remaining();return [previous,frame]
    previous=frame
   else:previous=None
   self.progress();time.sleep(min(.2,self.remaining(.2)));self.progress()
 def original_hashes(self):
  result={}
  for name in ORIGINALS:
   p=self.root/'vanilla/Bin'/name;require(p.resolve(strict=True)==p and not p.is_symlink(),'exact Original file path')
   st=p.stat();signature=(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
   result[name]=hashlib.sha256(p.read_bytes()).hexdigest();after=p.stat()
   require(signature==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Original file changed during hash')
  return result
 def private_prestart(self,expected_names=None):
  started=time.monotonic();self.progress()
  require(self.lock is not None and not self.lock.closed,'held runtime lock required')
  want=self.root/'runtime.lock';st=want.stat();fd=os.fstat(self.lock.fileno())
  require((fd.st_dev,fd.st_ino)==(st.st_dev,st.st_ino),'runtime lock file identity')
  fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  require(set(self.records)=={'server','botA','botB'},'Original must not be launched during prestart')
  self.B.quiescent(self.root/'vanilla');require(self.B.pid(self.unit('vanilla'))==0 and self.B.empty(self.unit('vanilla')),'Original unit occupied')
  registry={r:dict(identity=list(v['identity']),unit=self.unit(r))for r,v in self.records.items()}
  before=observe_three_roles(registry);hashes=self.original_hashes()
  frames=self.frames(tuple(registry));query=self.B.query(self.records['server']['identity'][0]);self.progress()
  pauses={r:self.pauseprobe.read_pause(v['identity'][0],self.root/r)['actual_pause']for r,v in self.records.items()}
  mapping=self.slot_mapping((self.root/'botA/SeriousSam.log').read_text(errors='replace'),(self.root/'botB/SeriousSam.log').read_text(errors='replace'));mapping.pop('vanilla')
  self.B.quiescent(self.root/'vanilla');require(hashes==self.original_hashes(),'Original hashes changed during check')
  after=observe_three_roles(registry);ended=time.monotonic()
  names=sorted(v for k,v in query.items()if re.fullmatch(r'player_\d+',k))if expected_names is None else list(expected_names)
  deadline=min(ended+FRESH_SECONDS,self.capture.started+30 if self.capture is not None else ended+FRESH_SECONDS)
  evidence=dict(protocol=PROTOCOL,window=[started,ended],deadline=deadline,binding_before=before,binding_after=after,
   host_namespace=Path('/proc/1/ns/net').stat().st_ino,query=query,map_name=self.map_name,mapping=mapping,frames=frames,pauses=pauses,
   original_hashes=hashes,vanilla_quiescent=True,lock_held=True,resources=self.host_budget.samples[-1])
  self.check_serial+=1
  try:verdict=validate_prestart(evidence,expected_names=names,now=time.monotonic())
  except BaseException as error:
   exclusive_json(self.evidence/f'private-eight-prestart-{self.check_serial}.json',dict(evidence=evidence,status='FAIL',error=repr(error)));raise
  exclusive_json(self.evidence/f'private-eight-prestart-{self.check_serial}.json',dict(evidence=evidence,verdict=verdict))
  return dict(evidence=evidence,names=names,verdict=verdict)
 def validate_current_prestart(self,check):
  return validate_prestart(check['evidence'],expected_names=check['names'],now=time.monotonic())
 def prejoin_readiness(self,reader_type,evidence_error,active_evidence,mapping):
  import a4_ordered_memory_v3 as ordered
  from stability_hard_rules import validate_session
  require(mapping==dict(botA=[0,1,2,3],botB=[4,5,6,7]),'actual prejoin eight-slot mapping')
  require(self.capture is None and set(self.records)=={'server','botA','botB'},'readiness before Original and capture only')
  started=time.monotonic();end=started+20;identity=self.records['server']['identity']
  registry={r:dict(identity=list(v['identity']),unit=self.unit(r))for r,v in self.records.items()};self.prejoin_binding=observe_three_roles(registry)
  log_paths={r:self.root/r/('Dedicated_BotTest.log'if r=='server'else'SeriousSam.log')for r in self.records}
  offsets={r:len(p.read_bytes())for r,p in log_paths.items()}
  def raw_logs():
   out={}
   for role,path in log_paths.items():
    raw=path.read_bytes();require(len(raw)>=offsets[role],'prejoin log truncated')
    require(not re.search(rb'SYNCBAD|Too many bad syncs|CRC check failed|Access violation|Fatal Error|Cannot join game:|\[CecilInvalidAction\]',raw,re.I),'prejoin sync/crash log event')
    out[role]=raw[offsets[role]:].decode(errors='replace')
   return out
  first_query=self.B.query(identity[0]);names=[v for k,v in first_query.items()if re.fullmatch(r'player_\d+',k)]
  validate_query(first_query,names,self.map_name);queries=[first_query];samples=[];entities={};serial=0;last_query=0.;last_proof=-100.;proof=None
  contract=dict(schema='OWNNS_PREJOIN8_ORDERED_V1',server_identity=list(identity),groups=dict(botA_actual=list(range(4)),botB_actual=list(range(4,8))),entities=[],source_log_offsets=offsets,started_monotonic=started)
  receipt=dict(status='FAIL',scope='PRIVATE_PREJOIN20S_READINESS_ONLY',started_monotonic=started,deadline_monotonic=end,qualified=False,functional_pass=False,a4_accepted=False)
  try:
   with private_stream(self.evidence/'prejoin-inventory.jsonl')as stream,private_stream(self.evidence/'prejoin-read-attempts.jsonl')as attempts,reader_type(identity[0],identity[1],self.root/'server',ORIGINALS['GameMP.dll'])as reader:
    journal=ordered.AttemptJournal(attempts)
    while True:
     self.progress();now=time.monotonic();require(now<end,'prejoin readiness20s deadline')
     snapshots={r:self.probe.read(v['identity'][0],self.root/r)for r,v in self.records.items()}
     for snap in snapshots.values():
      validate_session(snap);require(sorted(p['slot']for p in snap['players'])==list(range(8)),'prejoin native slots changed')
     for group,slots in contract['groups'].items():
      serial+=1;a=time.monotonic();journal.begin(serial,group,a,'gameplay')
      try:sample=reader.sample(tuple(slots))
      except evidence_error as error:
       journal.end(serial,time.monotonic(),False,str(error)[:256])
       if str(error)not in('state changed during read','tick changed during read'):raise
      except BaseException as error:journal.end(serial,time.monotonic(),False,repr(error)[:256]);raise
      else:
       b=time.monotonic();journal.end(serial,b,True)
       sample['prejoin_observation']=dict(group=group,read_serial=serial,monotonic_start=a,monotonic_end=b)
       require(sample['all_selected_present']is True,'missing actual prejoin bot')
       for row in sample['players']:entities.setdefault(row['slot'],{k:row[k]for k in ('slot','entity_id','entity_pointer','world_pointer')})
       samples.append(sample);stream.write(json.dumps(sample,allow_nan=False)+'\n');stream.flush()
     elapsed=time.monotonic()-started
     if elapsed-last_query>=2:
      query=self.B.query(identity[0]);validate_query(query,names,self.map_name);queries.append(query);last_query=elapsed
     if elapsed-last_proof>=1:
      logs=raw_logs()
      for role,v in self.records.items():require(self.pauseprobe.read_pause(v['identity'][0],self.root/role)['actual_pause']==0,'prejoin native pause')
      if set(entities)==set(range(8)):
       contract['entities']=[entities[s]for s in range(8)]
       proof=readiness_evidence(logs={r:logs[r]for r in ('botA','botB')},mapping=mapping,samples=samples,queries=queries,contract=contract,attempts=journal.records,server_log=logs['server'],active_evidence=active_evidence)
       receipt.update(proof=proof,contract=contract,observed_seconds=time.monotonic()-started)
       if proof['ready']:
        self.progress();require(time.monotonic()<end,'readiness completed after20s deadline')
        require(observe_three_roles(registry)==self.prejoin_binding,'prejoin ports changed at completion')
        receipt['status']='PRIVATE_PREJOIN_READINESS_OBSERVED_NOT_A4';return receipt
      last_proof=elapsed
     self.progress();time.sleep(.015 if elapsed<2 else .1)
  except BaseException as error:receipt.update(status='FAIL',error=repr(error));raise
  finally:
   receipt.update(ended_monotonic=time.monotonic(),query_observations=queries,source_log_offsets=offsets)
   exclusive_json(self.evidence/'private-prejoin-readiness.json',receipt)
 def admission(self,names,reader_type):
  started=time.monotonic();receipt=dict(protocol=PROTOCOL,status='FAIL',started_monotonic=started,readiness_rounds=[],frames=[],partial_inventory={},local_source=None,first_raw_frame_serial=self.frame_serial+1,qualified=False,functional_pass=False,a4_accepted=False)
  try:
   self.progress();require(set(self.records)=={'server','botA','botB','vanilla'},'exact four actual roles')
   registry={r:dict(identity=list(v['identity']),unit=self.unit(r))for r,v in self.records.items()};binding=observe_roles(registry);receipt['binding']=binding
   exclusive_json(self.evidence/'private-original-endpoint-before-schema.json',dict(status='ENDPOINT_OBSERVED_NOT_ADMITTED',binding=binding,qualified=False,functional_pass=False,a4_accepted=False))
   frames=self.admission_frames(registry,binding,started,receipt['readiness_rounds']);receipt['frames']=frames
   query=self.B.query(self.records['server']['identity'][0]);receipt['query']=query;self.progress()
   all_names=[v for k,v in query.items()if re.fullmatch(r'player_\d+',k)]
   require(set(names)<=set(all_names)and len(set(all_names)-set(names))==1,'exact retained eight plus one Original name')
   validate_query(query,all_names,self.map_name,9)
   for role,v in self.records.items():require(self.pauseprobe.read_pause(v['identity'][0],self.root/role)['actual_pause']==0,'latejoin native pause')
   native=receipt['partial_inventory']
   for role in ('server','vanilla'):
    identity=self.records[role]['identity']
    with reader_type(identity[0],identity[1],self.root/role,ORIGINALS['GameMP.dll'])as reader:
     if role=='vanilla':
      local=local_source.sample(reader);receipt['local_source']=local
      exclusive_json(self.evidence/'private-original-local-source-sample.json',dict(raw_sample=local,validation_pending=True,qualified=False))
     selected=reader.sample((8,0,1,2));native[role]=selected
     exclusive_json(self.evidence/f'private-original-slot8-{role}-inventory.json',dict(raw_sample=selected,validation_pending=True,qualified=False))
     row=next(p for p in selected['players']if p['slot']==8)
     require(selected['process_identity']==list(identity)and selected['hashes']=={k:ORIGINALS[k]for k in ('Engine.dll','EntitiesMP.dll','GameMP.dll')},'Original/server slot8 sample provenance')
     require(row['present']is True and row['entity_pointer']==next(p['entity_pointer']for p in frames[-1][role]['players']if p['slot']==8),'slot8 entity changed during admission')
   require(local['process_identity']==registry['vanilla']['identity'],'Original local0 probe identity')
   rows={r:next(p for p in s['players']if p['slot']==8)for r,s in native.items()}
   require(rows['server']['entity_id']==rows['vanilla']['entity_id'],'server/Original actual slot8 entity ID differs')
   ended=time.monotonic();validate_frames(frames,binding,range(9),[started,ended])
   require(observe_roles(registry)==binding,'admission role rebaseline forbidden')
   self.progress()
   result=dict(protocol=PROTOCOL,window=[started,ended],binding=binding,query=query,frames=frames,readiness_rounds=receipt['readiness_rounds'],original_local_mapping=local,slot8_inventory=native,qualified=False,functional_pass=False,a4_accepted=False)
   exclusive_json(self.evidence/'private-original-slot8-admission.json',result);return result
  except BaseException as error:
   receipt.update(error=repr(error),ended_monotonic=time.monotonic(),last_raw_frame_serial=self.frame_serial)
   if getattr(error,'local_source_evidence',None)is not None:receipt['local_source_failure']=error.local_source_evidence
   exclusive_json(self.evidence/'private-original-slot8-failure.json',receipt);raise
