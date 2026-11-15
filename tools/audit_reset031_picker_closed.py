"""ONE bounded closed031 audit. No process/memory/display/game access."""
import ast
import collections
import copy
from decimal import Decimal
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
import audit_reset030_closed as prior
import picker_custody_audit as picker

CASE=Path('/srv/tse-milestone-a-evidence-20261111/a4-reset031-diag1-v3-root-20261115-130242')
PACKAGE=Path('/srv/tse-a4-build031-hard-reset-v3-diag1-root-frozen-20261115')
OUT=Path('/srv/tse-reset031-picker-closed-audit-evidence-20261115')
RESULT_SHA='848c701b029969d4431b92a39add588eabd0bfac7fc68271ec4b7200fd136fc0'
MAX_OUTPUT=5*1024*1024
pins={};sizes={};source_bytes=0;written=0;G={}


def read(path,source=False):
 global source_bytes
 cap=32*1024*1024 if source else 2*1024*1024
 with prior.opened(path)as stream:raw=stream.read(cap+1)
 if len(raw)>cap:raise ValueError('declared per-source/small-read budget')
 if source:
  source_bytes+=len(raw)
  if source_bytes>64*1024*1024:raise ValueError('64MiB aggregate031 Source budget')
 pins[str(path)]=hashlib.sha256(raw).hexdigest();sizes[str(path)]=len(raw)
 return raw


def load(path):return json.loads(read(path))


def rows(path):
 total=0;h=hashlib.sha256()
 with prior.opened(path)as stream:
  for raw in stream:
   total+=len(raw)
   if total>64*1024*1024 or len(raw)>262144:raise ValueError('unchanged archived64MiB stream bound')
   h.update(raw);yield json.loads(raw)
 pins[str(path)]=h.hexdigest();sizes[str(path)]=total


def save(name,value):
 global written
 data=(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
 v=os.statvfs('/srv')
 if written+len(data)>MAX_OUTPUT or v.f_bavail*v.f_frsize<2**33+2**26+len(data):raise ValueError('5MiB total /8GiB+64MiB write reserve')
 with os.fdopen(os.open(OUT/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as stream:
  stream.write(data);stream.flush();os.fsync(stream.fileno())
 written+=len(data)


def binding_prefix(module,source):
 """Expose locals from UNCHANGED original ordered-core source/life join prefix."""
 tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='slot_evidence')
 cut=next(i for i,n in enumerate(node.body)if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Tuple)and [v.id for v in n.targets[0].elts]==['growth','previous','invalid'])
 prefix=copy.deepcopy(node.body[:cut]);fingerprint=hashlib.sha256(ast.dump(ast.Module(body=prefix,type_ignores=[]),include_attributes=False).encode()).hexdigest()
 node.body=prefix+[ast.parse('return dict(joins=joins,invalid=sorted(invalid_joins),rejected=rejected_times)').body[0]];node.name='bindings'
 scope=dict(module.__dict__);exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),'unchanged-qualified-join-prefix','exec'),scope)
 return scope['bindings'],fingerprint


def geometry(native,life):
 seen=[r for r in native if r['spawn']==life['spawn_clock']and r['good']]
 exact=one=None;exact_best=one_best=0.;maxgap=0.;chords=0.
 for index,r in enumerate(seen):
  if index:
   old=seen[index-1];gap=r['tick']-old['tick'];maxgap=max(maxgap,gap)
   if 0<gap<=.5:chords+=math.dist(old['position'],r['position'])
  else:gap=0
  if r['translation']!=[0,0,0]:exact=None
  elif exact is None or not 0<gap<=.5 or r['position']!=exact['position']:exact=r
  else:exact_best=max(exact_best,r['tick']-exact['tick'])
  if one is None or not 0<gap<=.5 or math.dist(one['position'],r['position'])>1:one=r
  else:one_best=max(one_best,r['tick']-one['tick'])
 return dict(exact_position_zero_translation_span=exact_best,stationary_1m_span=one_best,observed_position_chords=chords,max_gap=maxgap,continuous_trace=False)


def main():
 if OUT.exists():raise ValueError('fresh output only')
 result=load(CASE/'result.json');manifest=load(CASE/'source-manifest.json');controller=read(CASE/'controller-source.py')
 if pins[str(CASE/'result.json')]!=RESULT_SHA or result['status']!='PASS_LIMITED_BOT_RESET_FRESH_OBSERVER_REVIEW_REQUIRED' or result['active_evidence_missing']!={} or not all(v['closed']for v in result['cleanup'].values()):raise ValueError('exact031 closed technical status')
 if hashlib.sha256(controller).hexdigest()!=result['controller_sha256']:raise ValueError('executed controller pin')
 modules=('a4_reset_ordered_memory_v3.py','a4_reset_groups_v3.py','a4_epoch_reset_observation.py','audit_a4_ordered_memory_v3.py','audit_a4_native_fire_observer_v2.py','a4_fire_observer_v2.py','reset_policy.py','a4_reset_hard_rules.py')
 sources={name:read(PACKAGE/name)for name in modules}
 if any(hashlib.sha256(raw).hexdigest()!=manifest['draft_source_sha256'][name]for name,raw in sources.items()):raise ValueError('pinned unchanged archived helpers')
 life_path=Path(__file__).with_name('navigation_life_summary.py');life_source=read(life_path)
 if hashlib.sha256(life_source).hexdigest()!='6f4a2f150368ddddefb530afa2b40ba210a3d648dc6b323fe41430bbb4b9b65c':raise ValueError('unchanged life helper required')
 sys.path.insert(0,str(PACKAGE))
 import a4_reset_ordered_memory_v3 as v3
 import a4_epoch_reset_observation as epochs
 import reset_policy
 spec=importlib.util.spec_from_file_location('qualified031life',life_path);life=importlib.util.module_from_spec(spec);spec.loader.exec_module(life)
 bindings,prefix_sha=binding_prefix(v3.audit,sources['audit_a4_ordered_memory_v3.py'].decode())
 streams={i:[]for i in range(3)};smokes=[];wrappers=collections.Counter()
 for outer in rows(CASE/'inventory.jsonl'):
  group=outer['group'];sample=outer['snapshot'];phase=sample['observer_epoch']['phase']
  if group.startswith('early-'):
   if group not in ('early-botA','early-botB')or type(outer.get('early_attempt'))is not int:raise ValueError('typed early physical wrapper')
   group=group.removeprefix('early-')+'_actual'
  if group!=sample['native_group_provenance']['name']:raise ValueError('outer/inner actual provenance')
  if outer['phase']=='paused_smoke':
   if phase!=0 or sample['memory_observation']['phase']!='paused_smoke':raise ValueError('paused epoch')
   smokes.append(sample)
  else:
   if type(outer['phase'])is not int or outer['phase']!=phase or sample['memory_observation']['phase']!='gameplay':raise ValueError('typed actual phase')
   streams[phase].append(sample)
  wrappers[str(outer['phase'])+':'+outer['group']]+=1
 G['streams']=streams;G['smokes']=smokes
 phases=[];slotphases=[];all_batches=[];native_by_key={};life_by_key={};sources_by_phase={};joins_by_key={}
 for phase in range(3):
  folder=CASE/f'phase-{phase}-redstation';active=load(folder/'active-evidence.json');registry=load(folder/'registry.json');contract=load(folder/'memory-observation-contract.json');mapping=registry['actual_slot_mapping'];identity=registry['native_fire_epoch']['server_identity']
  attempts=list(rows(CASE/f'phase-{phase}-read-attempts.jsonl'));samples=streams[phase]
  counts,journal=v3.validate_all(samples,registry,mapping,identity,contract,attempts)
  if phase==0:
   v3.groups.validate_all(smokes+samples,registry,mapping,identity,contract)
   ids=set()
   for sample in smokes:
    obs=sample['memory_observation'];serial=obs['read_serial'];group=sample['native_group_provenance']['name'];begin,end=journal[serial]
    expected=dict(schema='ordered-readonly-memory-v3',read_serial=serial,monotonic_start=begin['monotonic_start'],monotonic_end=end['monotonic_end'],phase='paused_smoke',id=v3.observation_id(contract,group,serial))
    if v3.groups.digest(obs)!=v3.groups.digest(expected)or begin['group']!=group or begin['phase']!='paused_smoke'or end['status']!='ok'or serial in ids:raise ValueError('unchanged paused actual attempt')
    ids.add(serial)
   if ids!={n for n,(b,e)in journal.items()if b['phase']=='paused_smoke'and e['status']=='ok'}:raise ValueError('paused coverage')
  logs={role:read(folder/(role+'.log'),True).decode('latin1')for role in ('botA','botB','server')}
  if reset_policy.slot_mapping(logs)!=mapping:raise ValueError('actual Source slot mapping')
  replay=v3.apply(copy.deepcopy(active),logs,mapping,samples,registry,identity,contract,attempts)
  if replay['memory_observation']!=active['memory_observation']or any(replay['slots'][k]['memory_flag_observations']!=v['memory_flag_observations']for k,v in active['slots'].items()):raise ValueError('unchanged V3 replay differs')
  canonical=[s for s in samples if s['native_group_provenance']['name']in contract['fixed_sources'].values()]
  own=set(mapping['botA']+mapping['botB']);expected={r['slot']:r for r in registry['players']if r['slot']in own}
  denominator=life.summarize(canonical,expected)
  phaseout=dict(phase=phase,mapping=mapping,epoch=registry['native_fire_epoch'],attempts=len(journal),failed_attempts=sum(e['status']=='error'for b,e in journal.values()),failure_reasons=dict(collections.Counter(e.get('error')for b,e in journal.values()if e['status']=='error')),canonical_samples=len(canonical),groups=counts,life_summary={k:v for k,v in denominator.items()if k!='lives'},lives=denominator['lives'],missing=active['missing_activity'],active=active['slots'])
  phases.append(phaseout);sources_by_phase[phase]=logs
  source={role:v3.audit.source_rows(logs[role])for role in ('botA','botB')}
  typed=[];source_meta={}
  for role in ('botA','botB'):
   for line_no,text in enumerate(logs[role].splitlines(),1):
    row=picker.parse(text)
    if row is not None:row.update(phase=phase,role=role,line=line_no);typed.append(row)
   for local,slot in enumerate(mapping[role]):
    key=(phase,role,local);bound=bindings(source[role],[(s['memory_observation']['read_serial'],s)for s in canonical],local,slot,expected[slot]);joins_by_key[key]=bound
    lives=[l for l in denominator['lives']if l['slot']==slot];life_by_key[key]=lives
    native=[]
    for s in canonical:
     for r in s['players']:
      if r['slot']!=slot:continue
      clock=r.get('spawned_tick',0);ref=next((l for l in lives if l['spawn_clock']==clock),None)
      good=v3.audit.good_player(r,expected[slot],s['game_tick'])and(ref is not None and(ref['first_dead_observed_tick']is None or s['game_tick']<ref['first_dead_observed_tick']))
      w=r.get('weapons')or{}
      native.append(dict(read_serial=s['memory_observation']['read_serial'],tick=s['game_tick'],spawn=clock,entity=r['entity_id'],good=good,health=r.get('health'),position=r.get('placement',[])[:3],translation=r.get('current_translation_absolute'),last_buttons=r.get('last_buttons'),weapons={k:w.get(k)for k in ('owned','current','wanted','has_ammo','fire_requested')}))
    native_by_key[key]=native
    for l in lives:l.update(geometry=geometry(native,l))
    slotphases.append(dict(phase=phase,role=role,local=local,slot=slot,lives=len(lives),useful_possession_lives=sum(l['first_useful_observed_tick']is not None for l in lives),useful_gains=sum(l['useful_gain_events']for l in lives),bound_native_fire_flags=active['slots'][role+':'+str(local)]['memory_flag_observations']['native_fire_flag_observations_with_same_life_source_growth'],max_stationary_1m=max((l['geometry']['stationary_1m_span']for l in lives),default=0),max_exact_nulltranslation=max((l['geometry']['exact_position_zero_translation_span']for l in lives),default=0)))
  batches=picker.assemble(typed)
  for b in batches:
   _,role,local,actor,generation,tick=b['key'];key=(phase,role,local);slot=mapping[role][local];d=b['decision']['fields'];j=joins_by_key[key];clock=j['joins'].get(generation)
   matches=[l for l in life_by_key[key]if l['spawn_clock']==clock]
   sr=[r for r in source[role]if int(r['local'])==local and int(r.get('entity',0))==actor and int(r.get('generation',0))==generation]
   spawns=[r for r in sr if r['tag']=='CecilSpawn'];wpo=[r for r in sr if r['tag']=='CecilWeaponObserve']
   source_ok=actor==expected[slot]['entity_id']and len(spawns)==1 and int(spawns[0]['tick'])<=tick
   b['binding']=dict(slot=slot,source_spawn_line=spawns[0]['line']if len(spawns)==1 else None,native_spawn=clock if source_ok and len(matches)==1 else None,status='BOUND'if source_ok and len(matches)==1 else'UNKNOWN_MISSING_SPAWN_OR_WPO_LIFE')
   before=[r for r in wpo if int(r['tick'])<=tick];after=[r for r in wpo if int(r['tick'])>=tick]
   interval=None
   if source_ok and len(matches)==1 and before and after:
    a=max(before,key=lambda r:int(r['tick']));z=min(after,key=lambda r:int(r['tick']))
    lo=Decimal(a['native_time'])-Decimal('.0000005');hi=Decimal(z['native_time'])+Decimal('.0000005');l=matches[0]
    if v3.audit.stamp(clock)<=lo<=hi<=v3.audit.stamp(l['last_alive_observed_tick']):interval=dict(low=str(lo),high=str(hi),wpo_lines=[a['line'],z['line']],wpo_ticks=[int(a['tick']),int(z['tick'])],same_source_tick=int(a['tick'])==tick==int(z['tick']))
   b['native_interval']=interval
   # A visible DriverFinal at this SAME call proves SetAction reached. Missing
   # independent admission cannot be reconstructed from absent arbitration.
   final=[n for n,text in enumerate(logs[role].splitlines(),1)if text.startswith('[CecilDriverFinalV1] ')and re.search(r' local='+str(local)+r' tick='+str(tick)+r' actor='+str(actor)+r' ',text)]
   if final and b['arbitration']is None:raise ValueError('missing known-admitted SameCall arbitration')
   b['arbitration_admission']='RECORDED_SUBMIT_NOT_ACK'if b['arbitration']else'UNKNOWN_NO_FINAL_ADMISSION_WITNESS'
   # Decision precedes the later retained-goal ReadItem refresh; Arbitration
   # observes its post-Supply value. Preserve both, never equate these phases.
  all_batches+=batches
 G.update(phases=phases,batches=all_batches,native=native_by_key,lives=life_by_key,sources=sources_by_phase,joins=joins_by_key)
 sequence=epochs.validate_sequence([load(CASE/f'phase-{i}-redstation/active-evidence.json')for i in range(3)],result['persistent_identities'])
 closed={};closed_texts={}
 for role in ('server','botA','botB','vanilla'):
  raw=read(CASE/(role+'-closed.log'),True);closed_texts[role]=raw.decode('latin1');closed[role]=dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),syncbad=len(re.findall(rb'SYNCBAD',raw)),disconnect=len(re.findall(rb'Too many bad syncs',raw)))
 health={}
 for row in rows(CASE/'session-health.jsonl'):
  h=health.setdefault(str(row['phase']),dict(rows=0,spawn_values={},session_hashes=set()));h['rows']+=1
  for role,value in row['roles'].items():h['spawn_values'].setdefault(role,set()).add(value['spawn_value']);h['session_hashes'].add(value['session156_sha256'])
 for h in health.values():h['spawn_values']={k:sorted(v)for k,v in h['spawn_values'].items()};h['session_hashes']=sorted(h['session_hashes'])
 OUT.mkdir(mode=0o700)
 compact=[]
 for b in all_batches:
  d=b['decision'];a=b['arbitration']
  compact.append(dict(key=b['key'],lines=[d['line'],b['origin']['line']]+[r['line']for r in b['attempts']]+([a['line']]if a else[]),binding=b['binding'],native_interval=b['native_interval'],decision=d['fields'],attempts=[dict(line=r['line'],index=r['fields']['attempt'],end=r['fields']['end'],item=r['fields']['item'],kind=r['fields']['kind'],weapon=r['fields']['weapon'],visibility=r['fields']['visibility'][0],nearest=r['fields']['nearest'],path=r['fields']['path'])for r in b['attempts']],arbitration=a['fields']if a else None,arbitration_admission=b['arbitration_admission']))
 long=[]
 for key,lives in life_by_key.items():
  for l in lives:
   if l['first_alive_observed_tick']is not None and l['first_useful_observed_tick']is None:
    long.append(dict(phase=key[0],role=key[1],local=key[2],**l))
 long.sort(key=lambda x:x['observed_alive_span_seconds'],reverse=True)
 focus=[]
 for l in long[:6]:
  key=(l['phase'],l['role'],l['local']);related=[b for b in all_batches if tuple(b['key'][:3])==key and b['binding']['native_spawn']==l['spawn_clock']]
  focus.append(dict(life=l,batches=related,native_rows=[r for r in native_by_key[key]if r['spawn']==l['spawn_clock']]))
 save('life-and-all24.json',dict(phases=phases,slotphases=slotphases,sequence=sequence,smokes=len(smokes),wrapper_counts=dict(wrappers),health=health,long_no_useful=long,original_status=result['status'],qualified=False))
 save('all-picker-batches.json',dict(batches=compact,source_clock_not_native=True,proposal_is_not_movement_or_pickup=True))
 save('long-no-useful-focus.json',focus)
 summary=dict(status='CLOSED031_AUDIT_ONLY_NO_A4_ACCEPTANCE',result_sha256=RESULT_SHA,input_pins=pins,input_bytes=sizes,closed_logs=closed,source_bytes=source_bytes,output_bytes_before_receipt=written,qualified=False,native_access=False,all24_slotphases=len(slotphases),phases=[dict(phase=p['phase'],life_summary=p['life_summary'],attempts=p['attempts'],failed=p['failed_attempts'])for p in phases],custody_rows=dict(collections.Counter(r['tag']for b in all_batches for r in[b['decision'],b['origin']]+b['attempts']+([b['arbitration']]if b['arbitration']else[]))),batches=len(all_batches),bound_batches=sum(b['binding']['status']=='BOUND'for b in all_batches),native_bracketed_batches=sum(b['native_interval']is not None for b in all_batches),reason_counts=dict(collections.Counter(b['decision']['fields']['reason']for b in all_batches)),attempt_ends=dict(collections.Counter(r['fields']['end']for b in all_batches for r in b['attempts'])),binding_prefix_ast_sha256=prefix_sha,longest_no_useful=long[:6],limitations=['1Hz throttling: not a complete picker-call list.','Same-call submit is not ACK/physics or inventory gain.','Unknown source-generation/native-clock mappings are not interpolated.','No claim regarding older030 failures or A4/FirstState/strength acceptance.'])
 save('audit-receipt.json',summary);G['summary']=summary
 finish_detail(closed_texts)
 print(json.dumps({k:v for k,v in summary.items()if k not in('input_pins','input_bytes','longest_no_useful')},indent=2))


def closed_custody(texts):
 """All CLOSED bot-source custody, including non-observed reset pauses/tails."""
 typed=[];ranges={};closed_counts=collections.Counter()
 for role in ('botA','botB'):
  raw=texts[role].encode('latin1')
  for phase in range(3):
   part=G['sources'][phase][role].encode('latin1');start=raw.find(part)
   if start<0 or raw.find(part,start+1)>=0:raise ValueError('unique whole archived Source slice')
   ranges[(phase,role)]=(start,start+len(part))
  boundaries=[(p,G['phases'][p]['epoch']['log_offsets'][role])for p in range(3)]
  offset=0
  for number,line in enumerate(texts[role].splitlines(True),1):
   r=picker.parse(line.rstrip('\r\n'))
   if r is not None:
    possible=[p for p,start in boundaries if offset>=start]
    if not possible:raise ValueError('Source before initial declared offset')
    phase=max(possible);r.update(role=role,phase=phase,line=number,closed_byte_offset=offset)
    typed.append(r);closed_counts[r['tag']]+=1
   offset+=len(line.encode('latin1'))
 batches=picker.assemble(typed);lookup={tuple(b['key']):b for b in batches}
 for b in G['batches']:
  other=lookup.get(tuple(b['key']))
  if other is None:raise ValueError('active custody omitted from CLOSED source')
  for field in ('decision','origin','arbitration'):
   a,z=b[field],other[field]
   if(a is None)!=(z is None)or(a is not None and a['fields']!=z['fields']):raise ValueError('active/closed full typed custody differs')
  if [a['fields']for a in b['attempts']]!=[a['fields']for a in other['attempts']]:raise ValueError('active/closed attempt custody differs')
 active={tuple(b['key'])for b in G['batches']}
 outside=[dict(key=b['key'],lines=[b['decision']['line'],b['origin']['line']]+[a['line']for a in b['attempts']]+([b['arbitration']['line']]if b['arbitration']else[]),reason=b['decision']['fields']['reason'],status='UNKNOWN_OUTSIDE_ARCHIVED_GAMEPLAY_PHASE_NOT_NATIVE_EVIDENCE')for b in batches if tuple(b['key'])not in active]
 return dict(all_closed_row_counts=dict(closed_counts),all_closed_batches=len(batches),active_batches=len(active),outside_batches=outside,phase_byte_ranges={str(k):list(v)for k,v in ranges.items()},format_faults=0,declared_overflows=0)


def finish_detail(texts):
 """Deterministic semantic finalizer; IO retry provenance stays in erratum."""
 for key,lives in G['lives'].items():
  for l in lives:l['geometry']=geometry(G['native'][key],l)
 top=[]
 for key,lives in G['lives'].items():
  for l in lives:
   if l['first_useful_observed_tick']is None and l['first_alive_observed_tick']is not None:top.append(dict(phase=key[0],role=key[1],local=key[2],**l))
 top.sort(key=lambda l:l['observed_alive_span_seconds'],reverse=True)
 focus=top[0];key=(focus['phase'],focus['role'],focus['local']);related=[b for b in G['batches']if tuple(b['key'][:3])==key and b['binding']['native_spawn']==focus['spawn_clock']]
 generations={b['key'][4]for b in related}
 source=G['sources'][key[0]][key[1]].splitlines();events=[];source_spawns=[];source_deaths=[]
 for n,line in enumerate(source,1):
  if not line.startswith('['):continue
  tag=line.split(']',1)[0][1:];v=dict(re.findall(r'(\w+)=([^\s]+)',line))
  if v.get('local')!=str(key[2]):continue
  if tag=='CecilSpawn'and int(v['generation'])in generations:source_spawns.append((n,v))
  if tag=='CecilDeath'and int(v['generation'])in generations:source_deaths.append((n,v))
 if len(generations)!=1 or len(source_spawns)!=1:raise ValueError('strict longest Source life missing/contradictory')
 start=int(source_spawns[0][1]['tick']);end=min((int(v['tick'])for n,v in source_deaths),default=2**31)
 for n,line in enumerate(source,1):
  tag=line.split(']',1)[0][1:];v=dict(re.findall(r'(\w+)=([^\s]+)',line))
  if v.get('local')==str(key[2])and start<=int(v.get('tick',-1))<=end and tag in('CecilGoal','CecilGoalEnd','CecilSupplyDiagUnavailable','CecilPickup','CecilGroundReplan'):
   events.append(dict(line=n,tag=tag,fields=v))
 geometry_rows=[dict(key=list(k),spawn=l['spawn_clock'],geometry=l['geometry'])for k,lives in G['lives'].items()for l in lives]
 summary={k:v for k,v in G['summary'].items()if k not in('source_bytes','output_bytes_before_receipt','longest_no_useful')}
 # Sizes refer to unique input files. Actual extra semantic-only CLOSED reads
 # used during author debugging are separately preserved, never hidden here.
 summary['source_unique_bytes']=sum(n for p,n in sizes.items()if p.endswith('.log'))
 summary['longest_no_useful']=top[:6]
 summary['all24_slotphase_table']=[]
 for phase in G['phases']:
  for role in ('botA','botB'):
   for local,slot in enumerate(phase['mapping'][role]):
    k=(phase['phase'],role,local);ls=G['lives'][k];a=phase['active'][role+':'+str(local)]
    summary['all24_slotphase_table'].append(dict(phase=k[0],role=role,local=local,slot=slot,lives=len(ls),useful_possession_lives=sum(l['first_useful_observed_tick']is not None for l in ls),useful_gains=sum(l['useful_gain_events']for l in ls),bound_native_fire_flags=a['memory_flag_observations']['native_fire_flag_observations_with_same_life_source_growth'],stationary_1m_max=max((l['geometry']['stationary_1m_span']for l in ls),default=0),exact_nulltranslation_max=max((l['geometry']['exact_position_zero_translation_span']for l in ls),default=0)))
 summary['corrected_all_life_geometry']=geometry_rows
 summary['closed_custody']=closed_custody(texts)
 summary['longest_life_picker']=dict(life=focus,source_spawn=source_spawns,source_death=source_deaths,admitted_batches=len(related),source_generations=sorted(generations),reason_counts=dict(collections.Counter(b['decision']['fields']['reason']for b in related)),gates_mapped_counts={str(k):v for k,v in collections.Counter((tuple(b['decision']['fields']['gates']),tuple(b['decision']['fields']['mapped']))for b in related).items()},scanning_batches=sum(bool(b['decision']['fields']['scan'][0])for b in related),input_owned_usable_counts={str(k):v for k,v in collections.Counter(tuple(b['decision']['fields']['input'][1:3])for b in related).items()},scan_totals=[sum(b['decision']['fields']['scan'][i]for b in related)for i in range(9)],attempts=[dict(tick=b['key'][5],line=a['line'],fields=a['fields'])for b in related for a in b['attempts']],arbitration_taken=sum(b['arbitration']is not None and b['arbitration']['fields']['taken']==1 for b in related),source_goal_events=events,unobserved_picker_calls='UNKNOWN_1HZ_THROTTLE',item_pickup_culprit='UNKNOWN_NO_OTHER_ACTOR_PICKUP_WITNESS')
 mapped=[]
 for n,line in enumerate(source,1):
  tag=line.split(']',1)[0][1:];v=dict(re.findall(r'(\w+)=([^\s]+)',line))
  if tag in('CecilSupplyDiagCandidate','CecilSupplyDiagSelection','CecilSupplyDiagConnector')and v.get('local')==str(key[2])and start<=int(v.get('tick',-1))<=end:
   if 'generation'in v and int(v['generation'])not in generations:raise ValueError('mapped diagnostic generation differs')
   mapped.append(dict(line=n,tag=tag,fields=v))
 summary['longest_life_picker']['existing_mapped_diagnostics']=mapped
 native=[r for r in G['native'][key]if r['spawn']==focus['spawn_clock']and r['good']]
 summary['longest_life_picker']['native_alive_samples']=len(native)
 summary['longest_life_picker']['native_owned_counts']=dict(collections.Counter(str(r['weapons']['owned'])for r in native))
 summary['longest_life_picker']['native_current_counts']=dict(collections.Counter(str(r['weapons']['current'])for r in native))
 summary['longest_life_picker']['observed_hp_increases']=[dict(old_serial=a['read_serial'],new_serial=z['read_serial'],old_tick=a['tick'],new_tick=z['tick'],old_hp=a['health'],new_hp=z['health'],position=z['position'],item_attribution='UNKNOWN_NO_ITEM_PICKUP_CALL_WITNESS')for a,z in zip(native,native[1:])if z['health']>a['health']]
 save('canonical-final-receipt-v2.json',summary);G['canonical']=summary


if __name__=='__main__':main()
