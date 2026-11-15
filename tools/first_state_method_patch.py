"""Exact, reversible source-only changes to the private two-actor observer.

Contains no Original machine bytes. The immutable binding table is composed
only inside a private disabled package. No function/field/TLS rule is replaced.
"""
import hashlib

PARENT_BODY_SHA256='38275a9f15d9f867bccbefb1f523352c74aad78c8c5ff559da1b1589894fde71'
OLD_STOP="""function stop(why){
 enabled=false;if(reason===null)reason=String(why);
 for(const [name,h]of Array.from(hooks.entries())){
  try{h.detach();hooks.delete(name);}catch(e){counters.detach_failures++;addError('detach',String(e),null,{hook:name});}
 }
 return {stopped:hooks.size===0,stop_reason:reason};
}"""
NEW_STOP="""let listenerCallbacks=0,getterCallbacks=0;
function tracked(callback,getter=false){
 return function(...args){
  if(getter)getterCallbacks++;else listenerCallbacks++;
  try{return callback.apply(this,args);}
  finally{if(getter)getterCallbacks--;else listenerCallbacks--;}
 };
}
function stop(why){
 enabled=false;if(reason===null)reason=String(why);
 return {stopped:hooks.size===0,stop_reason:reason};
}
function status(){
 const inFlight=counters.order_calls-counters.completed_calls;
 return {enabled,stop_reason:reason,in_flight:inFlight,callbacks:listenerCallbacks,
  getter_callbacks:getterCallbacks,active_calls:stack.length,active_damage:activeDamage.length,
  idle:!enabled&&inFlight===0&&stack.length===0&&activeDamage.length===0&&listenerCallbacks===0&&getterCallbacks===0,
  detached:hooks.size===0};
}
function finishstop(){
 if(!status().idle)return {stopped:false,stop_reason:reason};
 for(const [name,h]of Array.from(hooks.entries())){
  try{h.detach();hooks.delete(name);}catch(e){counters.detach_failures++;addError('detach',String(e),null,{hook:name});}
 }
 return {stopped:hooks.size===0,stop_reason:reason};
}"""
# Exact old→new clauses. Reversing every clause must recover the full pinned
# parent body, which also protects all unmentioned I1/I2 guards and event fields.
CHANGES=[
 (OLD_STOP,NEW_STOP),
 ('function bounded(){','function bounded(continuation=false){'),
 (' return enabled;\n}\nfunction tick()'," return enabled||(continuation&&reason==='host requested'&&counters.faults===0&&counters.dropped===0&&counters.aborted_leaves===0);\n}\nfunction tick()"),
 ('if(!bounded()||counters.events_attempted>cfg.max_events',"if(!bounded(edge==='leave')||counters.events_attempted>cfg.max_events"),
 ('  onEnter(){\n   this.frame=null;', '  onEnter:tracked(function(){\n   this.frame=null;'),
 ('  },\n  onLeave(retval){','  }),\n  onLeave:tracked(function(retval){'),
 ('    if(!enabled){counters.aborted_leaves++;return;}\n    if(!bounded()){', '    if(!bounded(true)){'),
 ('  }\n });\n hooks.set(name,h);','  })\n });\n hooks.set(name,h);'),
 ("hooks.set('getter_binding',Interceptor.attach(mods['Engine.dll'].add(g.rva+G.tls.binding_instruction_offset),{\n    onEnter(){", "hooks.set('getter_binding',Interceptor.attach(mods['Engine.dll'].add(g.rva+G.tls.binding_instruction_offset),tracked(function(){"),
 ('    }\n   }));\n   enabled=true;', '    },true)));\n   enabled=true;'),
 (" stop(){return stop('host requested');}", " stop(){return stop('host requested');},\n status(){return status();},\n finishstop(){return finishstop();}"),
]


def _replace_once(text,old,new):
    if text.count(old)!=1:raise ValueError('observer patch anchor differs')
    return text.replace(old,new,1)


def patch_body(text):
    if hashlib.sha256(text.encode()).hexdigest()!=PARENT_BODY_SHA256:raise ValueError('observer parent body pin differs')
    for old,new in CHANGES:text=_replace_once(text,old,new)
    return text


def reverse_body(text):
    for old,new in reversed(CHANGES):text=_replace_once(text,new,old)
    if hashlib.sha256(text.encode()).hexdigest()!=PARENT_BODY_SHA256:raise ValueError('observer inverse body pin differs')
    return text
