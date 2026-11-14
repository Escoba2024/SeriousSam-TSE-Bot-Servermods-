"""Versioned lifecycle-only patch of the private frozen Originaldamage hook.

No Retail fingerprint bytes are distributed here. The exact original private
source is required; all source outside the explicit changes is preserved.
"""
import hashlib

ORIGINAL_SHA='767a013ae896aa507d536e16f34ee3ed9bcc73121b41970ea329478f59381787'

STOP_RULES='''let listenerCallbacks=0,getterCallbacks=0;
function tracked(callback,getter=false){return function(...args){
 listenerCallbacks++;if(getter)getterCallbacks++;
 try{return callback.apply(this,args);}finally{if(getter)getterCallbacks--;listenerCallbacks--;}
};}
function stop(why){
 if(stoppedMs===null){stoppedMs=Date.now();reason=why;}enabled=false;
 // Admission only. Already admitted native ReceiveDamage pairs retain their
 // onLeave observer under the unchanged TTL/identity/body limits.
}
function stopStatus(){return {admission_closed:!enabled,in_flight:inFlight,
 active_records:active.length,listener_callbacks:listenerCallbacks,getter_callbacks:getterCallbacks,
 idle:inFlight===0&&active.length===0&&listenerCallbacks===0&&getterCallbacks===0,
 getter_bound:!!tls,getter_hook_present:!!getterHook,damage_hook_present:!!damageHook};}
function finishStop(){
 const state=stopStatus();need(state.admission_closed&&state.idle,'passive callbacks not idle');
 // Historical successful getter binding has already restored its hook. A
 // partial-arm/failed-bind handle is detached here only after the same idle
 // proof; its earlier fault cannot be erased by cleanup.
 for(const [site,detach] of [['getter',detachGetter],['damage',detachDamage]]){
  try{detach();}catch(e){faults=Math.min(1024,faults+1);if(detachErrors.length<64)detachErrors.push({site,error:String(e).slice(0,512)});}
 }
 return {stopped:!getterHook&&!damageHook,idle:true,detach_errors:detachErrors.slice()};
}
function continuationAllowed(){
 const now=Date.now();if(now>=expiresMs){stop('TTL');return false;}
 if(!tls&&now>=bindingExpiresMs){stop('unproven: getter binding timeout');return false;}
 return faults===0&&(enabled||reason==='host requested');
}
'''


def patch(source):
    if hashlib.sha256(source.encode()).hexdigest()!=ORIGINAL_SHA:
        raise ValueError('exact original private damage hook required')
    start=source.index('function stop(why){');end=source.index('function fault(e)',start)
    source=source[:start]+STOP_RULES+source[end:]
    changes={
        'onEnter(){this.record=null;this.counted=false;':'onEnter:tracked(function(){this.record=null;this.counted=false;',
        '    }catch(e){fault(e);}},\n    onLeave(){':'    }catch(e){fault(e);}}),\n    onLeave:tracked(function(){',
        'if(!enabled||!bounded())return;r.after=snapshot':'if(!continuationAllowed())return;r.after=snapshot',
        "if(total>=cfg.max_calls)stop('damage call bound');}}\n   });":"if(total>=cfg.max_calls)stop('damage call bound');}})\n   });",
        'onEnter(){if(!enabled||tls)return;try{':'onEnter:tracked(function(){if(!enabled||tls)return;try{',
        '   }catch(e){fault(e);}}});':'   }catch(e){fault(e);}},true)});',
        'first_processed_state_proven:false,native_qualified:false};records=[];return out;':'first_processed_state_proven:false,native_qualified:false,...stopStatus()};records=[];return out;',
        " stop(){stop('host requested');return {stopped:!getterHook&&!damageHook,detach_errors:detachErrors.slice()};}":" disarm(){stop('host requested');return stopStatus();},\n status(){return stopStatus();},\n finishstop(){return finishStop();}",
    }
    for old,new in changes.items():
        if source.count(old)!=1:raise ValueError('unrecognized original lifecycle region')
        source=source.replace(old,new)
    return source
