"""Bounded Build034 Source custody grammar; no runtime or evidence reads."""
import hashlib,re
from decimal import Decimal,InvalidOperation

REGULAR=set('event reason coverage serial entity entity_known generation item goal attempt deadline world_known world map_known map source hop edges cached_last cached_since event_time_known time accepted_known accepted current_point_known current_point clock'.split())
REASONS={'ARM':{'first_entry'},'UNADMITTED':{'eligibility_false'},'DISARM':{'external_unknown','gravity_changed','time_back','gap','history_full','edge_metadata_changed','goal_clear','flight_finish','eligibility_false','not_mapped_weapon','invalid_final','owner_lost','air_owner'},'END':{'goal_clear','domain_changed'},'CAP_REACHED':{'row_limit'},'FORMAT_FAULT':{'format_bounds'}}

def integer(raw,low,high):
 if not re.fullmatch(r'0|[1-9]\d*|-[1-9]\d*',raw):raise ValueError('canonical typed integer')
 value=int(raw)
 if not low<=value<=high:raise ValueError('integer bounds')
 return value

def number(raw,allow_nonfinite=False):
 if re.fullmatch(r'-?(?:inf|nan(?:\(ind\))?)',raw,re.I):
  if not allow_nonfinite:raise ValueError('finite Source field required')
  return dict(raw=raw,finite=False,decimal=None)
 if not re.fullmatch(r'-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',raw):raise ValueError('typed Source decimal')
 try:value=Decimal(raw)
 except InvalidOperation as error:raise ValueError('typed Source decimal')from error
 if not value.is_finite():raise ValueError('finite Source decimal')
 return dict(raw=raw,finite=True,decimal=str(value))

def pointer(raw):
 if raw=='(nil)':return 0
 if re.fullmatch(r'[0-9a-fA-F]{8}',raw):return int(raw,16)
 if re.fullmatch(r'0x[0-9a-fA-F]{1,8}',raw):return int(raw,16)
 raise ValueError('bounded IA32 pointer spelling')

def parse(line):
 if not line.startswith('[CecilItemTransitHistory]'):return None
 raw=line.rstrip('\r\n')
 if len(line.encode('latin1'))>=1024:raise ValueError('fixed Source row bound')
 if not raw.startswith('[CecilItemTransitHistory] '):raise ValueError('Source tag separator')
 fields={}
 for part in raw.split(' ')[1:]:
  if part.count('=')!=1:raise ValueError('Source key/value')
  key,value=part.split('=')
  if not key or not value or key in fields:raise ValueError('duplicate/missing Source key')
  fields[key]=value
 event=fields.get('event');reason=fields.get('reason')
 if event not in REASONS or reason not in REASONS[event]:raise ValueError('pinned Source event/reason')
 short=event in('CAP_REACHED','FORMAT_FAULT')
 if set(fields)!=({'event','reason','coverage','serial'}if short else REGULAR):raise ValueError('exact Source field schema')
 fields['serial']=integer(fields['serial'],1,1024)
 if fields['coverage']!=('incomplete'if short else'bounded'):raise ValueError('Source coverage')
 if (event=='CAP_REACHED')!=(fields['serial']==1024):raise ValueError('reserved cap row')
 out=dict(tag='CecilItemTransitHistory',fields=fields,raw_sha256=hashlib.sha256(line.encode('latin1')).hexdigest(),numeric={},world_value=None)
 if short:return out
 for key in ['entity','generation','item']:fields[key]=integer(fields[key],0,2**32-1)
 for key in ['goal','map','source','hop']:fields[key]=integer(fields[key],-2**31,2**31-1)
 fields['edges']=integer(fields['edges'],0,8)
 for key in ['entity_known','world_known','map_known','event_time_known','accepted_known','current_point_known']:fields[key]=integer(fields[key],0,1)
 if fields['entity_known']!=int(fields['entity']!=0):raise ValueError('Actor Knownbit')
 world=pointer(fields['world']);out['world_value']=world if fields['world_known']else None
 if not fields['world_known']and world!=0:raise ValueError('unknown world must remain uncapturedNULL')
 if not fields['map_known']and fields['map']!=-1:raise ValueError('unknown map sentinel')
 for name in ['accepted','current_point']:
  fields[name]=integer(fields[name],-1,1)
  if(fields[name]>=0)!=bool(fields[name+'_known']):raise ValueError('shortcircuit Knownbit')
 if fields['clock']!='source':raise ValueError('Source clock domain')
 for name in ['attempt','deadline','cached_last','cached_since','time']:
  out['numeric'][name]=number(fields[name],event=='UNADMITTED'and name in('attempt','deadline'))
 if not fields['event_time_known']and Decimal(fields['time'])!=0:raise ValueError('unknown current time sentinel')
 if event=='UNADMITTED':
  if fields['edges'] or fields['map_known'] or not fields['accepted_known']or not fields['current_point_known']:raise ValueError('pre-admission contract')
  if Decimal(fields['cached_last'])!=-1 or Decimal(fields['cached_since'])!=-1:raise ValueError('unadmitted cached clocks')
 elif not fields['world_known']or not fields['map_known']or fields['edges']<1:raise ValueError('admitted cached context')
 return out

def ss_key(row):
 f=row['fields'];return(row['role'],f['entity'],f['generation'],f['item'],f['goal'],f['attempt'],f['deadline'])

def assemble(rows):
 if len(rows)>2048:raise ValueError('two processes each bounded1024 rows')
 last={};faults=[];domains={};pre={}
 for row in rows:
  f=row['fields'];role=row['role'];event=f['event'];serial=f['serial']
  if role not in('botA','botB'):raise ValueError('own Source roles only')
  if serial!=last.get(role,0)+1:faults.append(dict(role=role,line=row['line'],reason='serial_gap_duplicate_or_reverse',expected=last.get(role,0)+1,actual=serial))
  last[role]=serial
  if event in('CAP_REACHED','FORMAT_FAULT'):
   faults.append(dict(role=role,line=row['line'],reason=event));continue
  key=ss_key(row)
  if event=='UNADMITTED':
   if key in pre:faults.append(dict(role=role,line=row['line'],reason='duplicate_unadmitted_ss_domain'))
   pre[key]=row;continue
  full=key+(row['world_value'],f['map'])
  domain=domains.setdefault(full,dict(key=list(full),events=[],has_arm=False,has_disarm=False,has_end=False))
  field={'ARM':'has_arm','DISARM':'has_disarm','END':'has_end'}[event]
  if domain[field]or domain['has_end']or(event!='ARM'and not domain['has_arm']):faults.append(dict(role=role,line=row['line'],reason='admitted_lifecycle_order_or_duplicate',event=event))
  domain[field]=True;domain['events'].append(row)
 return dict(status='FAIL_INCOMPLETE'if faults else('OBSERVED_BOUNDED_CUSTODY'if rows else'UNEXERCISED'),rows=len(rows),per_role_last_serial=last,critical_coverage_faults=faults,domains=list(domains.values()),unadmitted=list(pre.values()),open_admitted_domains=sum(d['has_arm']and not d['has_end']for d in domains.values()),open_tail_scope='UNKNOWN_RIGHT_CENSORED_OR_UNOBSERVED_END',native_or_pickup_proven=False)
