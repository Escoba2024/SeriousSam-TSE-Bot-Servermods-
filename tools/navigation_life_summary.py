"""Offline denominators after ordered-native-frame validation; never qualification.

Use actual game_tick/spawned_tick values, not elapsed wrappers or AI tick/20.
Frames remain ordered observations, not atomic snapshots or continuous traces.
"""
import math
from audit_a4_native_fire_observer_v2 import IDENTITY,USEFUL


def clock(value):
 if type(value)not in(int,float)or not math.isfinite(value)or value<0:
  raise ValueError('finite native clock required')
 return value


def summarize(samples,expected):
 lives={};previous={}
 for sample in samples:
  tick=clock(sample['game_tick'])
  for row in sample['players']:
   slot=row['slot']
   if slot not in expected or row.get('present')is not True:continue
   spawn=clock(row.get('spawned_tick',0))
   if not spawn:continue
   if tick<spawn or any(row.get(k)!=expected[slot][k]for k in IDENTITY):
    raise ValueError('native life/identity differs')
   if type(row.get('health'))not in(int,float)or not math.isfinite(row['health']):
    raise ValueError('finite health required')
   key=(slot,spawn);life=lives.get(key)
   if life is None:
    life=lives[key]=dict(slot=slot,spawn_clock=spawn,first_observed_tick=tick,
     last_observed_tick=tick,first_alive_observed_tick=None,last_alive_observed_tick=None,
     first_dead_observed_tick=None,first_useful_observed_tick=None,useful_gain_events=0,
     max_observation_gap_seconds=0,alive_after_dead_samples=0,
     continuous_observation_proven=False)
   if tick<life['last_observed_tick']:raise ValueError('native life clock moved backwards')
   life['max_observation_gap_seconds']=max(life['max_observation_gap_seconds'],tick-life['last_observed_tick'])
   life['last_observed_tick']=tick
   alive=row['health']>0 and row.get('render_type')==3
   weapons=row.get('weapons');owned=weapons.get('owned')if isinstance(weapons,dict)else None
   if owned is not None and(type(owned)is not int or not 0<=owned<=0xffffffff):
    raise ValueError('native inventory mask differs')
   if alive:
    if life['first_dead_observed_tick']is not None:
     life['alive_after_dead_samples']+=1;previous[key]=(tick,False,None);continue
    if life['first_alive_observed_tick']is None:life['first_alive_observed_tick']=tick
    life['last_alive_observed_tick']=tick
    if owned is not None and owned&USEFUL and life['first_useful_observed_tick']is None:
     life['first_useful_observed_tick']=tick
    old=previous.get(key)
    if old is not None and old[0]<tick and old[1]and old[2]is not None and owned is not None and owned&~old[2]&USEFUL:
     life['useful_gain_events']+=1
   elif row['health']<=0 and life['first_dead_observed_tick']is None:
    life['first_dead_observed_tick']=tick
   previous[key]=(tick,alive,owned)
 for slot in expected:
  ordered=sorted((x for x in lives.values()if x['slot']==slot),key=lambda x:x['spawn_clock'])
  for i,life in enumerate(ordered):
   life['left_censored']=life['first_observed_tick']>life['spawn_clock']
   life['ending']='observed_death'if life['first_dead_observed_tick']is not None else('next_spawn_observed'if i+1<len(ordered)else'right_censored')
   first,last=life['first_alive_observed_tick'],life['last_alive_observed_tick']
   life['observed_alive_span_seconds']=None if first is None else last-first
   useful=life['first_useful_observed_tick']
   life['useful_possession_age_upper_bound']=None if useful is None else useful-life['spawn_clock']
 out=sorted(lives.values(),key=lambda x:(x['slot'],x['spawn_clock']))
 return dict(observed_lives=len(out),expected_slots=len(expected),
  unobserved_slots=sorted(set(expected)-{x['slot']for x in out}),
  corpse_only_lives=sum(x['first_alive_observed_tick']is None for x in out),
  ambiguous_health_order_lives=sum(x['alive_after_dead_samples']>0 for x in out),
  left_censored_lives=sum(x['left_censored']for x in out),
  right_censored_lives=sum(x['ending']=='right_censored'for x in out),
  observed_death_lives=sum(x['ending']=='observed_death'for x in out),
  useful_possession_lives=sum(x['first_useful_observed_tick']is not None for x in out),
  useful_gain_events=sum(x['useful_gain_events']for x in out),lives=out,
  qualified=False,route_acceptance=False,
  scope='ORDERED_NATIVE_LIFE_DENOMINATORS_ONLY_NO_CONTINUOUS_OR_ROUTE_PROOF')


def validated_summary(samples,registry,mapping,identity,contract,attempts):
 import a4_ordered_memory_v3 as ordered
 # The archived stream also retains paused smoke reads. Validate their typed
 # raw envelopes, but never pass them as gameplay evidence to unchanged V3.
 raw_counts=ordered.groups.validate_all(samples,registry,mapping,identity,contract)
 journal=ordered.check_attempts(attempts,contract);smokes=set()
 for sample in samples:
  m=sample['memory_observation']
  if m['phase']=='gameplay':continue
  serial=m['read_serial'];group=sample['native_group_provenance']['name']
  if type(serial)is not int or serial not in journal or serial in smokes:
   raise ValueError('paused smoke serial missing/repeated')
  begin,end=journal[serial]
  ordered.clock(m['monotonic_start']);ordered.clock(m['monotonic_end'])
  if (set(m)!={'schema','read_serial','monotonic_start','monotonic_end','phase','id'}
      or m['schema']!='ordered-readonly-memory-v3' or m['phase']!='paused_smoke'
      or begin['phase']!='paused_smoke' or begin['group']!=group or end['status']!='ok'
      or ordered.groups.digest(m['id'])!=ordered.groups.digest(ordered.observation_id(contract,group,serial))
      or m['monotonic_start']!=begin['monotonic_start']or m['monotonic_end']!=end['monotonic_end']):
   raise ValueError('paused smoke envelope/attempt differs')
  smokes.add(serial)
 if smokes!={serial for serial,(begin,end)in journal.items()if begin['phase']=='paused_smoke'and end['status']=='ok'}:
  raise ValueError('successful paused smoke missing from archive')
 gameplay=[s for s in samples if s['memory_observation']['phase']=='gameplay']
 counts,journal=ordered.validate_all(gameplay,registry,mapping,identity,contract,attempts)
 slots={slot for role in('botA','botB')for slot in mapping[role]}
 expected={p['slot']:p for p in registry['players']if p['slot']in slots}
 if len(slots)!=8 or set(expected)!=slots:raise ValueError('eight bound own slots required')
 selected=[s for s in samples if s['native_group_provenance']['name']in contract['fixed_sources'].values()
           and s['memory_observation']['phase']=='gameplay']
 result=summarize(selected,expected)
 result['raw_group_samples']=raw_counts;result['gameplay_group_samples']=counts;result['paused_smoke_samples']=len(smokes);result['attempt_count']=len(journal)
 result['failed_attempts']=sum(end['status']=='error'for begin,end in journal.values())
 return result


def unpack_rows(rows):
 out=[]
 for outer in rows:
  keys=set(outer)
  if keys not in({'phase','group','snapshot'},{'elapsed','group','snapshot'}):
   raise ValueError('actual archived envelope required')
  sample=outer['snapshot']
  if outer['group']!=sample['native_group_provenance']['name']:
   raise ValueError('outer/inner native group differs')
  if 'phase'in outer:
   if outer['phase']!=sample['memory_observation']['phase']:raise ValueError('outer/inner observation phase differs')
  else:
   clock(outer['elapsed'])
   if sample['memory_observation']['phase']!='gameplay':raise ValueError('elapsed wrapper requires gameplay')
  out.append(sample)
 return out


if __name__=='__main__':
 import argparse,hashlib,json
 from pathlib import Path
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('evidence',type=Path)
 args=parser.parse_args();root=args.evidence.resolve()
 names=['result.json','registry.json','inventory.jsonl','read-attempts.jsonl']
 raw={name:(root/name).read_bytes()for name in names}
 report=json.loads(raw['result.json']);registry=json.loads(raw['registry.json'])
 if report['status']!='PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED' or not report['cleanup'] or not all(r['closed']for r in report['cleanup'].values()):
  raise ValueError('closed limited observation required; no failed/active run requalification')
 samples=unpack_rows([json.loads(line)for line in raw['inventory.jsonl'].splitlines()])
 attempts=[json.loads(line)for line in raw['read-attempts.jsonl'].splitlines()]
 contract=report['native_group_contract']
 result=validated_summary(samples,registry,report['actual_slot_mapping'],
  registry['native_fire_epoch']['server_identity'],contract,attempts)
 result['input_sha256']={name:hashlib.sha256(data).hexdigest()for name,data in raw.items()}
 result['original_status_unchanged']=report['status']
 print(json.dumps(result,allow_nan=False,indent=2))
