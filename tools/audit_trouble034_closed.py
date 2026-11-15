"""Exact closed Trouble034-case adapter over the unchanged prior pure reader."""
import ast,hashlib,json,os
from pathlib import Path
BASE=Path(__file__).with_name('audit_hole031_closed.py')
BASE_SHA='475ddc0a9ea17020873e6733964b3d93abdb8c3a8005e6871fe338db466e0f0e'
PAIRS=[
 ('One bounded closed Hole031 audit','One bounded closed Trouble034 audit'),
 ('/srv/tse-milestone-a-evidence-20261111/nav20-031-hole-root-hole-20261115-141204','/srv/tse-milestone-a-evidence-20261111/nav20-034-trouble-root-trouble-20261115-183149'),
 ('/srv/tse-nav20-031-hole600-diag1-root-frozen-20261115','/srv/tse-nav20-034-trouble300-diag1-root-frozen-20261115'),
 ('/srv/tse-hole031-closed-audit-evidence-20261115','/srv/tse-trouble034-closed-audit-evidence-20261115'),
 ('7e581f512eaf9717221d18eeb9b5091e11ed72d83b8960d282858c3bc00262a4','bb91a86973a2241ef0eddaf541c3f3160c73ec380811236534068dbf92a458e5'),
 ("map='hole'","map='trouble'"),
 ('/srv/tse-cecil-rollout-evidence-20261114/navigation031-hole-host/receipt.json','/srv/tse-cecil-rollout-evidence-20261114/navigation034-trouble-host/receipt.json'),
 ('/srv/tse-cecil-rollout-evidence-20261114/navigation031-hole-root-restore.json','/srv/tse-cecil-rollout-evidence-20261114/navigation034-trouble-root-restore.json'),
 ('OUTPUT=5*1024*1024','OUTPUT=8*1024*1024'),
 ('5MiB output/8GiB+64MiB reserve','8MiB output/8GiB+64MiB reserve'),
 ('COMPLETE_CANONICAL_HOLE031_CLOSED_AUDIT_ONLY','COMPLETE_CANONICAL_TROUBLE034_CLOSED_AUDIT_ONLY'),
]
STATE={}
def digest(raw):return hashlib.sha256(raw).hexdigest()
def adapt(raw,reverse=False):
 if not reverse and digest(raw)!=BASE_SHA:raise ValueError('exact corrected Hole031 pure reader required')
 text=raw.decode()
 for a,b in(reversed(PAIRS)if reverse else PAIRS):
  if reverse:a,b=b,a
  if text.count(a)!=1 or(not reverse and b in text):raise ValueError('exact unique closed-case literal required')
  text=text.replace(a,b,1)
 changed=text.encode();ast.parse(changed)
 if reverse and digest(changed)!=BASE_SHA:raise ValueError('complete reader inverse differs')
 return changed

def namespace():
 with os.fdopen(os.open(BASE.resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:raw=f.read(1024*1024+1)
 if len(raw)>1024*1024:raise ValueError('small reader-source bound')
 transformed=adapt(raw)
 if adapt(transformed,True)!=raw:raise ValueError('whole case-source inverse')
 scope={'__name__':'closed_trouble034_pure_reader','__file__':str(Path(__file__).resolve())}
 exec(compile(transformed,str(BASE)+'[exact-closed-Trouble-case]', 'exec'),scope)
 scope['account'](BASE,raw)
 scope['G']['cache'][str(BASE)]=raw
 STATE.update(scope=scope,base_sha256=digest(raw),transformed_sha256=digest(transformed))
 return scope

C=None

def save(name,value):
 # Reuse the original unchanged exclusive0600/fsync/8GiB+64MiB disk guard.
 return C['save'](name,value)

def stat_budget(scope):
 names=['inventory.jsonl','read-attempts.jsonl','session-health.jsonl']+[r+'-closed.log'for r in ['server','botA','botB','vanilla']]
 sizes={n:(scope['CASE']/n).stat().st_size for n in names}
 if any(v>64*1024*1024 for v in sizes.values())or sum(sizes.values())>128*1024*1024:raise ValueError('approved aggregate/stream budget')
 logbytes=[v for n,v in sizes.items()if n.endswith('-closed.log')]
 if max(logbytes)>16*1024*1024 or sum(logbytes)>32*1024*1024:raise ValueError('approved closed-log budget')
 return sizes

def bind_line(role,fields,line):
 """Existing life join plus a conservative neighboring same-life WPO interval."""
 from decimal import Decimal
 g=C['G'];bound=g['bind'](role,fields,line)
 if bound.get('status')!='BOUND_SOURCE_LIFE':return bound
 if bound.get('native_interval')is not None:return bound
 local=bound['local'];gen=bound['generation'];key=(role,local)
 rows=[r for r in g['source'][role]if r['tag']=='CecilWeaponObserve'and int(r['local'])==local and int(r['generation'])==gen]
 a=[r for r in rows if r['line']<=line];z=[r for r in rows if r['line']>=line]
 if not a or not z:return bound
 a=max(a,key=lambda r:r['line']);z=min(z,key=lambda r:r['line'])
 lo=Decimal(a['native_time'])-Decimal('.0000005');hi=Decimal(z['native_time'])+Decimal('.0000005')
 life=next(l for l in g['lives'][key]if l['spawn_clock']==bound['native_spawn'])
 if life['last_alive_observed_tick']is not None and Decimal(str(life['spawn_clock']))<=lo<=hi<=Decimal(str(life['last_alive_observed_tick'])):
  bound['native_interval']=dict(low=str(lo),high=str(hi),kind='WHOLE_SAME_ACTOR_WPO_LINE_INTERVAL',wpo_lines=[a['line'],z['line']])
 return bound

def history_audit():
 import collections
 import transit_history_custody_audit as history
 g=C['G'];rows=[];malformed=[];total=0
 for role in ['botA','botB']:
  for line,text in enumerate(g['logs'][role].splitlines(),1):
   if not text.startswith('[CecilItemTransitHistory]'):continue
   total+=1
   if len(rows)>=2048:
    malformed.append(dict(role=role,line=line,reason='two_process_row_bound',raw_sha256=digest(text.encode('latin1'))));continue
   try:value=history.parse(text)
   except ValueError as error:
    malformed.append(dict(role=role,line=line,reason=str(error),raw=text[:1024],raw_sha256=digest(text.encode('latin1'))));continue
   value.update(role=role,line=line)
   f=value['fields'];value['binding']=dict(status='GLOBAL_PROCESS_COVERAGE_ROW')if f['event']in('CAP_REACHED','FORMAT_FAULT')else bind_line(role,f,line)
   rows.append(value)
 result=history.assemble(rows);result.update(raw_history_rows=total,malformed_rows=malformed,event_counts=dict(collections.Counter(v['fields']['event']for v in rows)),reason_counts=dict(collections.Counter(v['fields']['reason']for v in rows)),binding_counts=dict(collections.Counter(v['binding']['status']for v in rows)),typed_rows=rows,client_world_not_server_world=True,printed_clock_is_not_binary_double_identity=True)
 if malformed:result['status']='FAIL_INCOMPLETE'
 return result

def transition_chains(history):
 import collections
 from decimal import Decimal
 from audit_a4_native_fire_observer_v2 import USEFUL
 g=C['G'];extra=g['supplement']['all_extra_events'];aborts=[e for e in extra if e['tag']=='CecilItemTransitEnd'];out=[]
 for abort in aborts:
  f=abort['fields'];role=abort['role'];ab=bind_line(role,f,abort['line']);abort['binding']=ab
  entry=dict(abort=abort,chain_status='UNKNOWN_MISSING_HISTORY_OR_LIFE',causal_pickup_ack=False)
  candidates=[]
  for d in history['domains']:
   key=d['key'];events=d['events'];arm=next((v for v in events if v['fields']['event']=='ARM'),None);end=next((v for v in events if v['fields']['event']=='END'),None)
   if (key[0]==role and key[1]==int(f['entity'])and key[2]==int(f['generation'])and key[3]==int(f['goal_entity'])and key[4]==int(f['goal'])and arm and arm['line']<abort['line']and(end is None or abort['line']<end['line'])):candidates.append(d)
  entry['matching_history_domains']=len(candidates)
  if len(candidates)==1:entry['history_domain']=candidates[0]
  if ab.get('status')!='BOUND_SOURCE_LIFE':out.append(entry);continue
  local=ab['local'];spawn=ab['native_spawn'];life=next(l for l in g['lives'][(role,local)]if l['spawn_clock']==spawn)
  entry['life']=dict(slot=ab['slot'],spawn_clock=spawn,ending=life['ending'],last_alive=life['last_alive_observed_tick'],first_dead=life['first_dead_observed_tick'])
  goals=[e for e in extra if e['tag']=='CecilGoal'and e['role']==role and e['line']>abort['line']and e['binding'].get('local')==local and e['binding'].get('native_spawn')==spawn]
  if not goals:entry['chain_status']='UNKNOWN_NO_LATER_SAME_LIFE_GOAL';out.append(entry);continue
  goal=min(goals,key=lambda e:e['line']);gb=bind_line(role,goal['fields'],goal['line']);goal=dict(goal,binding=gb);entry['next_goal']=goal
  entry['replacement_item_differs']=int(goal['fields']['entity'])!=int(f['goal_entity'])
  if gb.get('native_interval')is None:entry['chain_status']='UNKNOWN_NEW_GOAL_NATIVE_INTERVAL';out.append(entry);continue
  low=Decimal(gb['native_interval']['high']);tail=[e for e in extra if e['role']==role and e['line']>goal['line']and e['tag']in('CecilGoal','CecilGoalEnd','CecilItemTransitEnd')and e['binding'].get('local')==local and e['binding'].get('native_spawn')==spawn]
  end=min(tail,key=lambda e:e['line'])if tail else None;endbind=bind_line(role,end['fields'],end['line'])if end else None
  entry['following_source_boundary']=dict(event=end,binding=endbind)if end else None
  observations=[r for r in g['native'][(role,local)]if r['good']and r['spawn']==spawn]
  gains=[]
  for a,b in zip(observations,observations[1:]):
   old=a['weapons']['owned'];new=b['weapons']['owned']
   if old is None or new is None or not a['tick']<b['tick']or Decimal(str(a['tick']))<low:continue
   gained=new&~old&USEFUL
   if not gained:continue
   before_boundary=bool(endbind and endbind.get('native_interval')and Decimal(str(b['tick']))<=Decimal(endbind['native_interval']['low']))
   if end and not before_boundary:continue
   weapon=int(goal['fields'].get('weapon','0'));mask=(1<<(weapon-1))if 1<=weapon<=14 else 0
   gains.append(dict(read_serials=[a['read_serial'],b['read_serial']],native_ticks=[a['tick'],b['tick']],old_owned=old,new_owned=new,gained_mask=gained,target_weapon_bit=mask,target_weapon_gained=bool(mask&gained),within_source_boundary=before_boundary if end else'UNKNOWN_RIGHT_CENSORED_SOURCE_GOAL'))
  entry['observed_useful_gains_after_new_goal']=gains
  entry['chain_status']='OBSERVED_TRANSITION_AND_SAME_LIFE_USEFUL_GAIN_NOT_PICKUP_ACK'if gains and len(candidates)==1 and f['reason']=='revisited_edges'else('OBSERVED_NEXT_GOAL_NO_BOUND_GAIN'if len(candidates)==1 else'UNKNOWN_HISTORY_DOMAIN')
  out.append(entry)
 return dict(total_transit_aborts=len(out),revisited_edges=sum(v['abort']['fields'].get('reason')=='revisited_edges'for v in out),chains=out,status_counts=dict(collections.Counter(v['chain_status']for v in out)),no_marker_status='UNEXERCISED'if not any(v['abort']['fields'].get('reason')=='revisited_edges'for v in out)else'OBSERVED_MARKER_ONLY_UNTIL_BOUND_CHAIN',never_shot_or_pickup_ack=True)

def main():
 global C
 C=namespace()
 C['EXTRA_EVENTS'].add('CecilItemTransitEnd')
 print('DECLARED_STAT_BUDGET',json.dumps(stat_budget(C)),flush=True)
 C['acquire']();C['derive']()
 # Source-only proof inputs, never re-open Native streams.
 for name in ['audit_trouble034_closed.py','transit_history_custody_audit.py','test_transit_history_custody_audit.py']:
  C['read'](Path(__file__).with_name(name))
 header=Path('/srv/tse-milestone-a-build-034-20261115/Sources/Game/BotSupplyNative.h')
 if digest(C['read'](header))!='652bb66d266d2e52bf961a3b6141112a7fe8abce4c8501032e2c1e3c3e0264dd':raise ValueError('exact034 diagnostic Source')
 C['read'](Path(__file__).parents[1]/'poc/candidates/redstation-supply-20261107/cecil_rules.h')
 C['outputs']();C['G']['supplement']=C['supplement']();C['behavior_hazards']()
 h=history_audit();chains=transition_chains(h)
 hp=save('transit-history-custody.json',h);cp=save('transit-transition-chains.json',chains)
 files={p.name:dict(bytes=p.stat().st_size,sha256=digest(p.read_bytes()))for p in sorted(C['OUT'].iterdir())if p.is_file()}
 value=dict(status='COMPLETE_CLOSED034_OBSERVATION_AUDIT_NOT_A4_PASS',result_sha256=C['RESULT'],history_status=h['status'],history_events=h['event_counts'],transit_chains={k:v for k,v in chains.items()if k!='chains'},original_status_unchanged=C['G']['report']['status'],qualified=False,a4_pass=False,stream_passes=1,old_raw_replays=0,input_pins=C['G']['pins'],input_bytes=C['G']['sizes'],actual_total_read_bytes=C['G']['read_bytes'],source_inverse_parent=STATE['base_sha256'],adapted_reader_sha256=STATE['transformed_sha256'],own_reader_sha256=digest(Path(__file__).read_bytes()),input_limit=128*1024*1024,output_limit=8*1024*1024,output_pins=files,all_native_raw_handles_closed=True)
 pin=save('complete034-final-receipt.json',value)
 print('COMPLETE034',json.dumps(dict(receipt=pin,history=hp,chains=cp,event_counts=h['event_counts'],history_status=h['status'],transition_counts=chains['status_counts'],revisited_edges=chains['revisited_edges'],total_read=C['G']['read_bytes'],output_bytes=C['G']['written'])),flush=True)
if __name__=='__main__':main()
