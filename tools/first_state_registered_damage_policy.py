"""Exact separate schema/validator copies for REGISTERED_FIRST_STATE_DAMAGE_V1."""
import copy
import hashlib
import json

POLICY_SHA='7b3f570cfe68a6ba429f4ea64ced3c3470d68898170f2cc5b6f82a5b6982c285'
SCHEMA_SHA='4b710cafbc3cc8420c9fbf999d3984948881a687fd740687e7dd6069dd20856a'
SCOPE='REGISTERED_FIRST_STATE_DAMAGE_V1'
WIRE='a1.registered-first-state-damage.observer.v1'
FIELDS=('entered_full','completed_full','entered_excluded','completed_excluded','pending','native_edges','rows_attempted','incomplete_closed')

def sha(s):return hashlib.sha256(s.encode()).hexdigest()

DENOM=""" s=packet['scope_counters']
 if s['incomplete_closed']:raise TraceRejected('candidate returned without complete guard/edge INCOMPLETE')
 if c['events_enqueued']+c['dropped']!=s['rows_attempted']:raise TraceRejected('full row denominator')
 if s['native_edges']!=c['events_attempted']or s['rows_attempted']+2*s['completed_excluded']+s['pending']!=c['events_attempted']:raise TraceRejected('native edge denominator')
 if s['entered_excluded']!=s['completed_excluded']:raise TraceRejected('excluded calls not finalized at actual leave')
 if s['entered_full']+s['entered_excluded']+s['pending']!=c['order_calls']:raise TraceRejected('full/excluded/pending entry denominator')
 if s['completed_full']+s['completed_excluded']!=c['completed_calls']:raise TraceRejected('full/excluded return denominator')
 if c['events_attempted']>bounds['max_events']:raise TraceRejected('native event bound')
 if c['non_main_calls']:raise TraceRejected('registered scope nonmain INCOMPLETE')"""

STREAM="""   s=packet['scope_counters']
   if s['entered_full']!=self.call_count or s['completed_full']!=self.call_count-len(self.open):raise TraceRejected('actual retained entry/return denominator')
   if c['order_calls']!=self.call_count+s['entered_excluded']+s['pending']or c['completed_calls']!=self.call_count-len(self.open)+s['completed_excluded']:raise TraceRejected('actual native call/return denominator')
   pending=[];full=[];seen=set();last_id=0;pending_seen=False
   for a in packet['active_calls']:
    cid=a['call_id']
    if cid in seen or cid<=last_id or cid>c['order_calls']:raise TraceRejected('active call identity/order')
    seen.add(cid);last_id=cid
    if cid in self.open:
     if pending_seen or self.open[cid]['kind']!=a['kind']:raise TraceRejected('retained child below pending worldcast')
     full.append(cid)
    else:
     pending_seen=True
     if a['kind']not in('cast_ray','continue_cast'):raise TraceRejected('noncast pending frame')
     pending.append(a)
   if full!=self.main_stack or len(pending)!=s['pending']:raise TraceRejected('actual pending stack denominator')
   excluded=0
   for kind,counts in c['by_kind'].items():
    e=counts['entered']-self.full_kinds[kind]['entered'];r=counts['completed']-self.full_kinds[kind]['completed']
    pending_kind=sum(a['kind']==kind for a in pending)
    if e<0 or r<0 or e!=r+pending_kind or(kind not in('cast_ray','continue_cast')and e):raise TraceRejected('actual excluded kind denominator')
    excluded+=r
   if excluded!=s['completed_excluded']:raise TraceRejected('excluded kind closure')
   if self.last:
    old=self.last['scope_counters']
    if any(s[k]<old[k]for k in s if k!='pending'):raise TraceRejected('scope counter reversed')"""

DELTAS=[
 (" if c['events_enqueued']+c['dropped']!=c['events_attempted']:raise TraceRejected('event denominator')",DENOM),
 ('self.call_count=0;self.tick_ordinal=0;',"self.call_count=0;self.full_kinds={k:{'entered':0,'completed':0}for k in KINDS};self.tick_ordinal=0;"),
 ("   if c['order_calls']!=self.call_count or c['completed_calls']!=self.call_count-len(self.open):raise TraceRejected('actual call/return denominator')",STREAM),
 ("  if e['sequence']!=len(self.events)+1:raise TraceRejected('ordered event sequence gap/repeat')", """  if e['row_sequence']!=len(self.events)+1:raise TraceRejected('ordered full row sequence gap/repeat')
  if e['sequence']!=e['row_sequence']+2*e['excluded_calls_before']+e['pending_before']:raise TraceRejected('actual native edge sequence')
  if e['excluded_calls_before']>p['scope_counters']['entered_excluded']or e['pending_before']:raise TraceRejected('pending/unknown full row ancestry')
  if self.events and e['sequence']<=self.events[-1]['sequence']:raise TraceRejected('native sequence reversed')"""),
 ("  if e['edge']=='enter':\n   if cid!=self.call_count+1 or cid in self.open:raise TraceRejected('call sequence gap/repeat')\n   self.call_count=cid\n",
  "  if e['edge']=='enter':\n   if cid!=self.call_count+1+e['excluded_calls_before']or cid in self.open:raise TraceRejected('native call sequence gap/repeat')\n   self.call_count+=1\n"),
 ("  if e['edge']=='enter':\n", "  self.full_kinds[kind]['entered'if e['edge']=='enter'else'completed']+=1\n  if e['edge']=='enter':\n"),
 ("  if e['edge']=='enter':\n   if cid!=self.call_count+1+e['excluded_calls_before']or cid in self.open:",
  "  if data['scope']=='unregistered':raise TraceRejected('registered chain/owner INCOMPLETE')\n  if e['edge']=='enter':\n   if cid!=self.call_count+1+e['excluded_calls_before']or cid in self.open:"),
 ("  if data['scope']=='unregistered':raise TraceRejected('registered chain/owner INCOMPLETE')",
  """  if data['scope']=='unregistered':raise TraceRejected('registered chain/owner INCOMPLETE')
  if payload.get('chain_bound')is False:raise TraceRejected('explicit unbound relevant chain INCOMPLETE')
  respawn=payload.get('respawn_source')
  if type(respawn)is dict and respawn.get('chain_bound')is False:raise TraceRejected('explicit unbound respawn source INCOMPLETE')
  if kind=='receive_damage'and(payload.get('inflictor')is None or payload.get('chain_bound')is not True):raise TraceRejected('ReceiveDamage owner/chain INCOMPLETE')"""),
]

def _apply(s,reverse=False):
    for a,b in reversed(DELTAS)if reverse else DELTAS:
        old,new=(b,a)if reverse else(a,b)
        if s.count(old)!=1:raise ValueError('unique exact registered policy fragment: '+old[:80])
        s=s.replace(old,new,1)
    return s

def patch_policy(s):
    if sha(s)!=POLICY_SHA:raise ValueError('exact FULL18 policy required')
    result=_apply(s)
    if reverse_policy(result)!=s:raise ValueError('whole policy inverse')
    return result

def reverse_policy(s):
    result=_apply(s,True)
    if sha(result)!=POLICY_SHA:raise ValueError('whole policy parent hash')
    return result

def patch_schema(s):
    if sha(s)!=SCHEMA_SHA:raise ValueError('exact FULL18 schema required')
    d=json.loads(s);d['$id']='urn:ssam:private:a1:registered-first-state-damage:v1'
    packet=d['$defs']['packet'];packet['properties']['schema']['const']=WIRE
    packet['properties']['measurement_scope']={'const':SCOPE}
    packet['properties']['scope_counters']={'type':'object','properties':{k:{'type':'integer','minimum':0,'maximum':16384}for k in FIELDS},'required':list(FIELDS),'additionalProperties':False}
    packet['required']+=['measurement_scope','scope_counters']
    event=d['$defs']['event']
    for k in('row_sequence','excluded_calls_before','pending_before'):
        event['properties'][k]={'type':'integer','minimum':1 if k=='row_sequence'else 0,'maximum':16384}
        event['required'].append(k)
    return json.dumps(d,indent=2)+'\n'

def reverse_schema(s,parent):
    # Exact canonical output rather than a lossy JSON reverse serialization.
    if sha(parent)!=SCHEMA_SHA or patch_schema(parent)!=s:raise ValueError('whole schema inverse')
    return parent
