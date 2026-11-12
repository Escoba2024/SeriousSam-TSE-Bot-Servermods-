#!/usr/bin/env python3
"""Read retained diagnostic logs only. Intended/composed angles are not executed aim.
No runtime access, interpolation, hidden target lookup or native pass verdict.
"""
import argparse,json,math,re
from pathlib import Path
FIELDS=re.compile(r'(\w+)=(\([^)]*\)|\S+)')
def pair(row,key):
 raw=row[key]
 if not raw.startswith('(')or not raw.endswith(')'):raise ValueError('invalid pair '+key)
 values=tuple(float(x)for x in raw[1:-1].split(','))
 if len(values)!=2 or not all(math.isfinite(v)for v in values):raise ValueError('nonfinite/invalid pair '+key)
 return values
def minus(a,b):return [x-y for x,y in zip(a,b)]
def analyze(text):
 aims={};transport={}
 for line in text.splitlines():
  tag=re.match(r'^\[(BotAimTrace|BotAimTransport)\] ',line)
  if not tag:continue
  row=dict(FIELDS.findall(line));key=(int(row['local']),int(row['tick']))
  target=aims if tag[1]=='BotAimTrace'else transport
  if key in target:raise ValueError('duplicate diagnostic key')
  target[key]=row
 result={'scope':'PASSIVE_INTENT_AND_COMPOSED_TRANSPORT_ONLY','native_execution_proven':False,'cause_proven':False,'matched':0,'missing_transport':len(aims.keys()-transport.keys()),'missing_aim':len(transport.keys()-aims.keys()),'consecutive_pairs':0,'events':[]}
 previous={}
 for key in sorted(aims.keys()&transport.keys()):
  a,t=aims[key],transport[key]
  if a['entity']!=t['entity']:raise ValueError('aim/transport identity mismatch')
  values={k:pair(t,k)for k in ('last','local_before','requested','precompose','local_after','composed')}
  intent=pair(a,'intent');pair(a,'residual')
  e={'local':key[0],'tick':key[1],'generation':int(a['generation']),'target':int(a['target']),'nav':int(t['nav']),
     'local_accumulator_delta':minus(values['composed'],values['local_before']),
     'accumulator_minus_last':minus(values['local_before'],values['last']),
     'composer_to_request_error':minus(values['composed'],values['requested']),
     'composer_to_local_error':minus(values['composed'],values['local_after']),
     'policy_to_request_error':None,'prior_packet_delta':None,
     'human_fire':int(a['human_fire']),'final_fire':int(t['final_fire'])}
  if a['valid']=='1'and e['target']>=0 and e['nav']==0:
   e['policy_to_request_error']=minus(minus(values['requested'],values['last']),intent)
  old=previous.get(key[0]);identity=(a['entity'],a['generation'])
  if old and old[0]+1==key[1]and old[1]==identity:
   e['prior_packet_delta']=minus(values['composed'],old[2]);result['consecutive_pairs']+=1
  previous[key[0]]=(key[1],identity,values['composed'])
  result['events'].append(e);result['matched']+=1
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',type=Path);args=p.parse_args()
 print(json.dumps(analyze(args.log.read_text(errors='strict')),indent=2))
