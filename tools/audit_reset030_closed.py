"""Bounded closed Reset030 audit; no process/display/memory/runtime access."""
import collections
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True  # Archive helpers are read-only; never create package caches.

CASE=Path('/srv/tse-milestone-a-evidence-20261111/a4-reset030-v3-root-20261115-110253')
PACKAGE=Path('/srv/tse-a4-build030-hard-reset-v3-timestamps-disabled-20261115')
OUT=Path('/srv/tse-reset030-closed-audit-evidence-20261115')
RESULT_SHA='dc38ebb2f86fb3364ae5bd64bf77a47c7f1aebb3df1f200b4e58f4903c97ce7a'
MAX_OUTPUT=10*1024*1024
input_pins={};bytes_written=0


def opened(path):
 return os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')


def read(path):
 with opened(path)as f:data=f.read(2*1024*1024+1)
 if len(data)>2*1024*1024:raise ValueError('small source/metadata bound')
 input_pins[str(path)]=hashlib.sha256(data).hexdigest();return data


def load(path):return json.loads(read(path))


def rows(path,limit=64*1024*1024):
 total=0;h=hashlib.sha256()
 with opened(path)as f:
  for line in f:
   total+=len(line)
   if total>limit or len(line)>262144:raise ValueError('bounded archived stream')
   h.update(line);yield json.loads(line)
 input_pins[str(path)]=h.hexdigest()


def save(name,value):
 global bytes_written
 data=(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
 if bytes_written+len(data)>MAX_OUTPUT:raise ValueError('derived output cap')
 with os.fdopen(os.open(OUT/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:
  f.write(data);f.flush();os.fsync(f.fileno())
 bytes_written+=len(data)


def focus_geometry(focus):
 """Observed endpoints only; no duration integration or source-clock conversion."""
 out={}
 for key,f in focus.items():
  lives=[]
  for life in f['life_denominators']:
   ss=[r for r in f['native_rows']if r['spawn']==life['spawn_clock']and r['good']and (life['first_dead_observed_tick']is None or r['tick']<life['first_dead_observed_tick'])]
   if not ss:continue
   positions=[r['position']for r in ss];distance=lambda a,b:math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
   pairs=[(a,b)for a,b in zip(ss,ss[1:])if 0<b['tick']-a['tick']<=.5]
   runs=[];run=None
   for r in ss:
    current=r['weapons']['current'];fire=bool(r['last_buttons']&1)
    if fire:
     if run is None or run['current']!=current or not 0<r['tick']-run['last_tick']<=.5:
      run=dict(current=current,first_tick=r['tick'],last_tick=r['tick'],samples=1);runs.append(run)
     else:run['last_tick']=r['tick'];run['samples']+=1
    else:run=None
   for run in runs:run['endpoint_span_not_continuous_duration']=run['last_tick']-run['first_tick']
   lives.append(dict(spawn=life['spawn_clock'],first_tick=ss[0]['tick'],last_tick=ss[-1]['tick'],first_position=positions[0],last_position=positions[-1],world_y_range=[min(p[1]for p in positions),max(p[1]for p in positions)],endpoint_displacement=distance(positions[0],positions[-1]),sampled_chords_with_old_halfsecond_gap_rule=sum(distance(a['position'],b['position'])for a,b in pairs),position_change_pairs=sum(a['position']!=b['position']for a,b in pairs),max_gap=life['max_observation_gap_seconds'],dead_tick=life['first_dead_observed_tick'],ending=life['ending'],current_counts=dict(collections.Counter(str(r['weapons']['current'])for r in ss)),wanted_counts=dict(collections.Counter(str(r['weapons']['wanted'])for r in ss)),fire_samples_by_current=dict(collections.Counter(str(r['weapons']['current'])for r in ss if r['last_buttons']&1)),fire_runs=runs))
  out[key]=dict(lives=lives,continuous_fire_duration='UNKNOWN; only sampled flag-run endpoint spans provided',position_distance='observed chords only, not an actual route/continuous speed claim')
 return out


def closed_reset_source():
 p=CASE/'botA-closed.log';h=hashlib.sha256();total=0;selected=[];tagcounts=collections.Counter()
 with opened(p)as f:
  for n,line in enumerate(f,1):
   total+=len(line)
   if total>4*1024*1024 or len(line)>65536:raise ValueError('bounded closed source scan')
   h.update(line);text=line.decode('latin1').rstrip()
   if text.startswith('[')and']'in text:
    tag=text.split(']',1)[0]+']';tagcounts[tag]+=1
    if tag in ('[CecilLoad]','[CecilReset]','[CecilReady]','[CecilMap]'):selected.append(dict(line=n,text=text))
 input_pins[str(p)]=h.hexdigest()
 return dict(bytes=total,sha256=h.hexdigest(),selected=selected,tagcounts=dict(tagcounts),bounded_source_only=True)


def main():
 if OUT.exists():raise ValueError('fresh output only; no repeated full raw pass')
 v=os.statvfs('/srv');free=v.f_bavail*v.f_frsize
 if free<2**33+2**26+MAX_OUTPUT:raise ValueError('8GiB+64MiB+output budget required')
 result=load(CASE/'result.json')
 if input_pins[str(CASE/'result.json')]!=RESULT_SHA or result['status']!='FAIL':raise ValueError('exact closed FAIL required')
 if not all(x['closed']for x in result['cleanup'].values()):raise ValueError('closed own roles required')
 manifest=load(CASE/'source-manifest.json');controller=read(CASE/'controller-source.py')
 if hashlib.sha256(controller).hexdigest()!=result['controller_sha256']:raise ValueError('archived executed controller differs')
 for name in ('a4_reset_ordered_memory_v3.py','a4_reset_groups_v3.py','a4_epoch_reset_observation.py',
              'audit_a4_ordered_memory_v3.py','audit_a4_native_fire_observer_v2.py','a4_fire_observer_v2.py','reset_policy.py','a4_reset_hard_rules.py'):
  data=read(PACKAGE/name)
  if hashlib.sha256(data).hexdigest()!=manifest['draft_source_sha256'][name]:raise ValueError('native helper source pin differs')
 life_path='/srv/tse-cecil-rollout-a-b-20261114/tools/navigation_life_summary.py'
 if hashlib.sha256(read(life_path)).hexdigest()!='6f4a2f150368ddddefb530afa2b40ba210a3d648dc6b323fe41430bbb4b9b65c':raise ValueError('qualified life helper source differs')
 sys.path.insert(0,str(PACKAGE))
 import a4_reset_ordered_memory_v3 as v3
 import a4_epoch_reset_observation as epochs
 import reset_policy
 spec=importlib.util.spec_from_file_location('qualified_life_summary',life_path)
 life=importlib.util.module_from_spec(spec);spec.loader.exec_module(life)
 streams={i:[]for i in range(3)};smokes=[];early=collections.Counter();wrappers=collections.Counter()
 for row in rows(CASE/'inventory.jsonl'):
  group=row['group'];sample=row['snapshot'];wrappers[str(row['phase'])+':'+group]+=1
  if group.startswith('early-'):
   early[str(row['phase'])+':'+group]+=1
   if group not in ('early-botA','early-botB')or type(row.get('early_attempt'))is not int:
    raise ValueError('typed early physical wrapper required')
   group=group.removeprefix('early-')+'_actual'
  phase=sample['observer_epoch']['phase']
  if group!=sample['native_group_provenance']['name']:raise ValueError('physical outer/inner group differs')
  m=sample['memory_observation']
  if row['phase']=='paused_smoke':
   if m['phase']!='paused_smoke' or phase!=0:raise ValueError('paused epoch differs')
   smokes.append(sample)
  else:
   if type(row['phase'])is not int or row['phase']!=phase or m['phase']!='gameplay':raise ValueError('gameplay epoch differs')
   streams[phase].append(sample)
 phases=[];focus={};slotphases=[]
 for phase in range(3):
  directory=CASE/f'phase-{phase}-redstation';active=load(directory/'active-evidence.json');registry=load(directory/'registry.json')
  contract=load(directory/'memory-observation-contract.json');mapping=registry['actual_slot_mapping'];identity=registry['native_fire_epoch']['server_identity']
  attempts=list(rows(CASE/f'phase-{phase}-read-attempts.jsonl'));samples=streams[phase]
  counts,journal=v3.validate_all(samples,registry,mapping,identity,contract,attempts)
  if phase==0:
   v3.groups.validate_all(smokes+samples,registry,mapping,identity,contract)
   smoke_serials=set()
   for s in smokes:
    m=s['memory_observation'];serial=m['read_serial'];group=s['native_group_provenance']['name'];begin,end=journal[serial]
    expected=dict(schema='ordered-readonly-memory-v3',read_serial=serial,monotonic_start=begin['monotonic_start'],monotonic_end=end['monotonic_end'],phase='paused_smoke',id=v3.observation_id(contract,group,serial))
    if v3.groups.digest(m)!=v3.groups.digest(expected)or begin['group']!=group or begin['phase']!='paused_smoke'or end['status']!='ok'or serial in smoke_serials:raise ValueError('smoke exact typed envelope/attempt differs')
    smoke_serials.add(serial)
   if smoke_serials!={n for n,(b,e)in journal.items()if b['phase']=='paused_smoke'and e['status']=='ok'}:raise ValueError('smoke success omitted')
  logs={r:read(directory/(r+'.log')).decode('latin1')for r in ('botA','botB','server')}
  if reset_policy.slot_mapping(logs)!=mapping:raise ValueError('source local/global mapping differs')
  replay=v3.apply(copy.deepcopy(active),logs,mapping,samples,registry,identity,contract,attempts)
  if replay['memory_observation']!=active['memory_observation']or any(replay['slots'][k]['memory_flag_observations']!=v['memory_flag_observations']for k,v in active['slots'].items()):raise ValueError('closed V3 replay differs')
  canonical=[s for s in samples if s['native_group_provenance']['name']in contract['fixed_sources'].values()]
  bot_slots={s for r in ('botA','botB')for s in mapping[r]};expected={r['slot']:r for r in registry['players']if r['slot']in bot_slots}
  denom=life.summarize(canonical,expected)
  failures=collections.Counter(e.get('error')for b,e in journal.values()if e['status']=='error')
  source={r:v3.audit.source_rows(logs[r])for r in ('botA','botB')}
  phase_out=dict(phase=phase,epoch=registry['native_fire_epoch'],mapping=mapping,reset_proof=registry['reset_observation_proof'],attempts=len(journal),failed_attempts=sum(failures.values()),failure_reasons=dict(failures),gameplay_groups=counts,canonical_samples=len(canonical),missing=active['missing_activity'],server_foreign_kill_rows=len(active['server_reported_foreign_kills']),life_summary={k:v for k,v in denom.items()if k!='lives'},lives=denom['lives'],load_lines={r:[x for x in logs[r].splitlines()if x.startswith('[CecilLoad]')]for r in ('botA','botB')},score_first_last_changed=bool(active['score_trajectory']and active['score_trajectory'][0]['query_index_scores']!=active['score_trajectory'][-1]['query_index_scores']))
  phases.append(phase_out)
  for role in ('botA','botB'):
   for local,slot in enumerate(mapping[role]):
    key=f'{role}:{local}';native_lives=[x for x in denom['lives']if x['slot']==slot]
    slotphases.append(dict(phase=phase,role=role,local=local,global_slot=slot,archived_counters=active['slots'][key],canonical_lives=len(native_lives),canonical_left_censored=sum(x['left_censored']for x in native_lives),canonical_right_censored=sum(x['ending']=='right_censored'for x in native_lives),canonical_deaths=sum(x['first_dead_observed_tick']is not None for x in native_lives),canonical_useful_possession_lives=sum(x['first_useful_observed_tick']is not None for x in native_lives),canonical_useful_gains=sum(x['useful_gain_events']for x in native_lives)))
    if (phase,role,local)not in ((1,'botA',1),(2,'botA',2)):continue
    native=[];current=collections.Counter();owned=collections.Counter();flagcounts=collections.Counter()
    for sample in canonical:
     for p in sample['players']:
      if p['slot']!=slot:continue
      w=p.get('weapons')or{};good=v3.audit.good_player(p,expected[slot],sample['game_tick'])
      if good:
       current[str(w.get('current'))]+=1;owned[str(w.get('owned'))]+=1
       flagcounts['alive']+=1;flagcounts['fire_requested']+=w.get('fire_requested')==1;flagcounts['last_buttons_FIRE']+=bool(p.get('last_buttons',0)&1);flagcounts['strict_native_ranged_fire']+=v3.audit.native_fire(p)
      native.append(dict(read_serial=sample['memory_observation']['read_serial'],read_start=sample['memory_observation']['monotonic_start'],read_end=sample['memory_observation']['monotonic_end'],tick=sample['game_tick'],spawn=p.get('spawned_tick'),entity=p['entity_id'],health=p.get('health'),render=p.get('render_type'),position=p.get('placement',[])[:3],last_buttons=p.get('last_buttons'),weapons={k:w.get(k)for k in ('owned','current','wanted','has_ammo','fire_requested')},good=good))
    source_local=[r for r in source[role]if int(r['local'])==local]
    focus[f'{phase}:{key}']=dict(phase=phase,role=role,local=local,slot=slot,registry_identity=expected[slot],life_denominators=native_lives,archived_slot=active['slots'][key],current_counts=dict(current),owned_counts=dict(owned),flag_counts=dict(flagcounts),source_rows=source_local,native_rows=native,missing_ack_or_picker_custody='diag0 has no DriverFinal/Candidate/Selection receipts; source wishes and sampled buttons are not weapon-function ACK or continuous firing/ownership trace')
 OUT.mkdir(mode=0o700)
 save('focus.json',focus)
 save('focus-geometry.json',focus_geometry(focus))
 save('closed-source-reset-metadata.json',closed_reset_source())
 sequence=epochs.validate_sequence([load(CASE/f'phase-{i}-redstation/active-evidence.json')for i in range(3)],result['persistent_identities'])
 health={};health_rows=0
 for row in rows(CASE/'session-health.jsonl'):
  health_rows+=1;p=str(row['phase']);x=health.setdefault(p,dict(rows=0,spawn_values={},session_hashes=set(),game_ticks={}))
  x['rows']+=1
  for role,s in row['roles'].items():
   x['spawn_values'].setdefault(role,set()).add(s['spawn_value']);x['session_hashes'].add(s['session156_sha256'])
   x['game_ticks'].setdefault(role,[s['game_tick'],s['game_tick']])[1]=s['game_tick']
 for x in health.values():x['session_hashes']=sorted(x['session_hashes']);x['spawn_values']={k:sorted(v)for k,v in x['spawn_values'].items()}
 save('life-and-slotphase-receipt.json',dict(phases=phases,slotphases=slotphases,sequence=sequence,smokes=len(smokes),early_wrapper_counts=dict(early),wrapper_counts=dict(wrappers),health=health,health_rows=health_rows,conditions={k:result.get(k)for k in ('candidate_sha256','cohort_config_sha256','actual_map_binding_checked','actual_profile_migration','barrier_time_limits','persistent_identities','observer_history','active_time_limits')},qualified=False,original_status='FAIL'))
 save('audit-receipt.json',dict(status='CLOSED_FAIL_PRESERVED_ALL24_SLOTPHASES_REPLAYED',result_sha256=RESULT_SHA,input_pins=input_pins,slotphases=24,sequence=sequence,qualified=False,functional_pass=False,raw_read_passes=1,source_read_only=True,no_clock_fusion=True,no_runtime_access=True,output_bytes_before_this_receipt=bytes_written,initial_disk_free_bytes=free,missing=result['active_evidence_missing'],limitations=['Canonical life counts differ from legacy active counters using overlapping groups; both retained.','No fire pulse in sampled rows is not proof no actual firing occurred.','No picker custody/final submission ACK can be reconstructed from diag0.','Early wrapper counts are descriptive; actual bound early serials/groups remain included in the unchanged V3 gameplay stream.','Root restore independent claim not re-run here.']))
 print(json.dumps(dict(output=str(OUT),bytes=bytes_written,phases=[dict(phase=x['phase'],life_summary=x['life_summary'],attempts=x['attempts'],failed=x['failed_attempts'],missing=x['missing'])for x in phases])))


if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,default=OUT)
 OUT=parser.parse_args().output.resolve()
 main()
