"""Strict Source/memory prefix reconciliation, never synthetic life evidence."""
import collections
import math
import re

from a3_closed_damage_components import load_components


def require(ok,message):
 if not ok:raise ValueError('Inventory reconciliation: '+message)


def parsed_events(text,local):
 events=collections.defaultdict(list);ordered=[]
 for line,raw in enumerate(text.splitlines(),1):
  match=re.match(r'\[(CecilSpawn|CecilDeath|CecilPickup|CecilState)\]',raw)
  if not match:continue
  fields={k:int(v)for k,v in re.findall(r'\b(local|entity|generation|tick|owned|respawns|deaths)=(\d+)',raw)}
  require('local'in fields,'missing event local')
  require(fields['local']in range(4),'source event has unmapped local')
  if fields['local']!=local:continue
  kind=match[1];require('tick'in fields,'missing event tick');fields['line']=line
  events[kind].append(fields);ordered.append((kind,fields))
 return events,ordered


def source_cycles(text,local):
 events,ordered=parsed_events(text,local);sp=events['CecilSpawn'];require(sp,'missing source spawn')
 entity=sp[0].get('entity');require(entity is not None,'missing entity');current=None;last_tick=-1;respawns=0;deaths=0;cycles=[]
 for kind,e in ordered:
  require(e['tick']>=last_tick,'source tick reversed');last_tick=e['tick']
  if current is None and kind=='CecilState':
   require(e.get('respawns')==0 and e.get('deaths')==0,'unexplained pre-spawn counters');continue
  if kind=='CecilSpawn':
   require(e.get('entity')==entity and 'generation'in e,'spawn entity/generation differs')
   require(current is None or current['death']is not None,'spawn without preceding death')
   require(current is None or e['generation']==current['spawn']['generation']+1,'generation gap')
   respawns+=1;require(e.get('respawns')==respawns,'respawn counter gap')
   current=dict(spawn=e,death=None);cycles.append(current)
  elif kind=='CecilDeath':
   require(current is not None and current['death']is None,'unmatched or duplicate death')
   require(e.get('entity')==entity and e.get('generation')==current['spawn']['generation'],'death identity/generation differs')
   deaths+=1;require(e.get('deaths')==deaths,'death counter gap');current['death']=e
  elif kind=='CecilState':
   require(current is not None and e.get('entity')==entity and e.get('generation')==current['spawn']['generation'],'state identity/generation differs')
   require(e.get('respawns')==respawns and e.get('deaths')==deaths,'state counter differs')
  else:require(current is not None,'pickup before first spawn')
 return events,cycles


def reconcile_local(lives,text,role,local,checks=None):
 require(lives and all(x['role']==role and x['local']==local for x in lives),'wrong or missing memory local')
 ordered=sorted(lives,key=lambda x:x['spawn_clock']);events,cycles=source_cycles(text,local)
 sp=events['CecilSpawn'];require(len(cycles)in(len(ordered),len(ordered)+1),'inner or multiple missing lives')
 require(len({x['entity_id']for x in ordered})==1,'memory entity changes')
 require(all(math.isfinite(x['spawn_clock'])and x['spawn_clock']>0 and not x['corpse_only']for x in ordered),'invalid/corpse-only memory life')
 require(all(b['spawn_clock']>a['spawn_clock']for a,b in zip(ordered,ordered[1:])),'memory life clocks not strictly increasing')
 if checks is None:checks,_=load_components()
 for index,(item,cycle)in enumerate(zip(ordered,cycles)):
  require(item['entity_id']==cycle['spawn']['entity'],'memory/source entity differs')
  try:checks.matched_life(item,cycle['spawn'],sp,index,events,local)
  except AssertionError as error:raise ValueError('Inventory reconciliation: existing entity/death/pickup check failed')from error
 unknown=[]
 if len(cycles)>len(ordered):
  require(not ordered[-1]['right_censored'],'unobserved suffix without completed memory prefix')
  require(all(c['death']is not None for c in cycles[:-1])and cycles[-1]['death']is None,'unobserved suffix not uniquely open')
  e=cycles[-1]['spawn'];unknown.append(dict(status='UNKNOWN_UNOBSERVED_SOURCE_LIFE',role=role,local=local,source_generation=e['generation'],source_line=e['line'],source_driver_tick=e['tick'],server_spawn_clock=None,window_membership=None,useful_weapon_outcome=None,observed_seconds=None,included_in_life_denominator=False))
 return dict(role=role,local=local,status='PARTIAL_INVENTORY_REPORT'if unknown else'COMPLETE_EXISTING_INVENTORY_OBSERVATIONS',observed_lives=len(ordered),unknown_source_lives=len(unknown),unobserved=unknown,
  known_completed_without_useful=sum(not x['right_censored']and x['first_useful_owned_age']is None for x in ordered),matched_prefix=[dict(source_generation=x['cecil_generation'],source_spawn_line=x['cecil_spawn_line'],first_inventory_line=x['first_inventory_line'],last_inventory_line=x['last_inventory_line'])for x in ordered])


def validate_memory_order(observations):
 by_slot=collections.defaultdict(list)
 for(slot,entity,spawn),rows in observations.items():
  for row in rows:by_slot[slot].append((row['line'],spawn,entity,row['tick']))
 for slot,rows in by_slot.items():
  ordered=sorted(rows);require(len({x[2]for x in ordered})==1,'slot entity changed')
  for row in ordered:require(math.isfinite(row[1])and math.isfinite(row[3])and 0<row[1]<=row[3],'invalid memory clock')
  require(all(b[1]>=a[1]and b[3]>=a[3]for a,b in zip(ordered,ordered[1:])),'memory life/tick reversal or inner return')
