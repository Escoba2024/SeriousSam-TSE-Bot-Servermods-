"""Exact reversible NEW measurement contract. Old FULL18 artifacts are untouched."""
import hashlib

SCOPE='REGISTERED_FIRST_STATE_DAMAGE_V1'
BODY_SHA='99607a2b7e61eb317971f9c5f0719b709f942c9eb6b53a98989e054e20e18507'
COMPILED_SHA='d8056397dddd02c27af5e13f15cbb54cbd5c1ffc2c83c342865ddc17a3f77732'

SCOPE_JS="""const measurementScope='REGISTERED_FIRST_STATE_DAMAGE_V1';
const scopeCounters={entered_full:0,completed_full:0,entered_excluded:0,completed_excluded:0,pending:0,native_edges:0,rows_attempted:0,incomplete_closed:0};
function scopeEnter(f){
 let pending=false,registeredAncestor=false;
 for(let p=f.parent;p;p=p.parent){
  if(p.scopePending)pending=true;
  if(p.kind==='launch_bullet'||WEAPON_KINDS.has(p.kind))registeredAncestor=true;
 }
 const candidate=f.thread===Process.id&&(f.kind==='cast_ray'||f.kind==='continue_cast')&&!registeredAncestor;
 need(!(pending&&!candidate),'relevant callback under pending worldcast ancestor');
 f.scopePending=candidate;
 if(candidate)scopeCounters.pending++;else scopeCounters.entered_full++;
}
"""

DELTAS=[
 ("const SCHEMA = 'a1.first-state.observer.v2';","const SCHEMA = 'a1.registered-first-state-damage.observer.v1';"),
 ('function emit(frame,edge,player,payload){',SCOPE_JS+'function emit(frame,edge,player,payload){'),
]
DELTAS=DELTAS+[
 (' frame.partial=row;', """ scopeCounters.native_edges=counters.events_attempted;
 if(!frame.scopePending){row.row_sequence=++scopeCounters.rows_attempted;row.excluded_calls_before=scopeCounters.entered_excluded;row.pending_before=scopeCounters.pending;}
 frame.partial=row;"""),
 (' queue.push(row);counters.events_enqueued++;return true;',""" if(frame.scopePending){
  frame.partial=null;
  if(edge==='leave'){frame.scopeFinalized=true;scopeCounters.pending--;scopeCounters.entered_excluded++;scopeCounters.completed_excluded++;}
  return true;
 }
 if(edge==='leave')scopeCounters.completed_full++;
 queue.push(row);counters.events_enqueued++;return true;"""),
 ('    stack.push(f);f.pushed=true;','    scopeEnter(f);\n    stack.push(f);f.pushed=true;'),
 ('    counters.completed_calls++;counters.by_kind[name].completed++;',
  '    if(f.scopePending&&!f.scopeFinalized){scopeCounters.pending--;scopeCounters.incomplete_closed++;}\n    counters.completed_calls++;counters.by_kind[name].completed++;'),
 ("     emit(f,'enter',null,{});return;","     scopeEnter(f);emit(f,'enter',null,{});return;"),
 ('  return {schema:SCHEMA,identity:clone(identity),events,counters:clone(counters),',
  '  return {schema:SCHEMA,measurement_scope:measurementScope,scope_counters:clone(scopeCounters),identity:clone(identity),events,counters:clone(counters),'),
]

def sha(text):return hashlib.sha256(text.encode()).hexdigest()

def _apply(text,reverse=False):
    for a,b in reversed(DELTAS)if reverse else DELTAS:
        old,new=(b,a)if reverse else(a,b)
        if text.count(old)!=1:raise ValueError('unique exact registered-scope fragment required: '+old[:90])
        text=text.replace(old,new,1)
    return text

def patch_body(text):
    if sha(text)!=BODY_SHA:raise ValueError('exact disabled FULL18 body required')
    result=_apply(text)
    if reverse_body(result)!=text:raise ValueError('whole body inverse')
    return result

def reverse_body(text):
    result=_apply(text,True)
    if sha(result)!=BODY_SHA:raise ValueError('whole body parent hash')
    return result

def patch_compiled(text):
    if sha(text)!=COMPILED_SHA:raise ValueError('exact disabled FULL18 compiled required')
    return _apply(text)

def reverse_compiled(text):
    result=_apply(text,True)
    if sha(result)!=COMPILED_SHA:raise ValueError('whole compiled parent hash')
    return result
