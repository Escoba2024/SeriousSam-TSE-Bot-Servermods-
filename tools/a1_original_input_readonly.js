'use strict';
// Disabled until arm RPC. Main holds its existing exclusive fixture lease.
// Original instruction observers only; no call replacement or game-data writes.
let used=false, enabled=false, cfg=null, guards=null, engine=null, game=null;
let input=null, gameObject=null, controls=null, source=null, player=null, world=null;
let armedMs=0, expiresMs=0, lastMs=0, stoppedMs=null, reason='', sequence=0, calls=0;
let faults=0, dropped=0, inFlight=0, records=[], handles=[], detachErrors=[];
let timer=null;
let inputThread=null;
let ready=false, completedSequences=0, warmupSkipped=0;
const activeInputs=new Map(), activeActions=new Map(), latestInput=new Map();
function need(ok, message) { if (!ok) throw Error(message); }
function finite(value) { need(Number.isFinite(value),'nonfinite observation'); return value; }
function pointer(value) {
  need(typeof value==='string' && /^0x[0-9a-f]{1,8}$/i.test(value),'pointer syntax');
  const n=Number(value); need(n>=0x10000 && n<=0xfffff000 && n%4===0,'pointer bounds');
  return ptr(value);
}
function same(a,b,label) { need(a.equals(b),label); }
function bool(value) { need(value===0 || value===1,'invalid boolean'); return !!value; }
function bytes(base, mod, guard) {
  const a=Uint8Array.from(guard.hex.match(/../g).map(x=>parseInt(x,16)));
  need(a.length===guard.length,'guard length');
  const delta=base.toUInt32()-mod.preferred_base;
  for (const off of guard.highlow_offsets) {
    need(Number.isInteger(off) && off>=0 && off+4<=a.length,'relocation bounds');
    let n=a[off]+a[off+1]*256+a[off+2]*65536+a[off+3]*16777216+delta;
    need(n>=0 && n<=0xffffffff,'relocation overflow');
    for(let i=0;i<4;i++) { a[off+i]=n%256; n=Math.floor(n/256); }
  }
  return a;
}
function original() {
  if(!guards) return false;
  return guards.guards.every(g=>{
    const b=g.module==='Engine.dll'?engine:game;
    const expected=bytes(b,guards.modules[g.module],g);
    const actual=new Uint8Array(b.add(g.rva).readByteArray(expected.length));
    return expected.length===actual.length && expected.every((v,i)=>v===actual[i]);
  });
}
function detachIdle() {
  if(stoppedMs===null || inFlight!==0) return false;
  for(let i=handles.length-1;i>=0;i--) {
    if(!handles[i]) continue;
    try { handles[i].detach(); handles[i]=null; }
    catch(e) { faults++; if(detachErrors.length<16) detachErrors.push(String(e).slice(0,512)); }
  }
  Interceptor.flush();
  return handles.every(h=>h===null);
}
function stop(why) {
  if(stoppedMs===null) { stoppedMs=Date.now(); reason=why; }
  enabled=false;
  if(timer!==null) { clearTimeout(timer); timer=null; }
  // A stop never removes an admitted entry/leave pair in flight. The host
  // drains this short quiescence phase before unloading or detaching session.
  return detachIdle();
}
function fault(error) { faults++; stop('unproven: '+String(error)); }
function running() {
  if(!enabled) return false;
  const now=Date.now();
  if(now<lastMs || now>=expiresMs) { stop('TTL/clock'); return false; }
  lastMs=now;
  return true;
}
function emit(record) {
  if(records.length>=cfg.max_records) { dropped++; stop('unproven: queue overflow'); return; }
  record.sequence=++sequence; record.epoch_ms=Date.now(); records.push(record);
}
function axis(index,binding) {
  const p=controls.add(0x10+index*36);
  need(p.readS32()===binding,'axis binding');
  need(p.add(0x0c).readS32()===0 && p.add(0x10).readS32()===1 &&
       p.add(0x14).readS32()===0,'axis invert/relative/smoothing');
  const row={sensitivity:finite(p.add(4).readFloat()),deadzone:finite(p.add(8).readFloat()),
    influence:finite(p.add(0x18).readFloat()),previous:finite(p.add(0x1c).readFloat()),
    absolute:finite(p.add(0x20).readFloat())};
  need(row.sensitivity===50 && row.deadzone===0 && row.influence===1,'axis transform changed');
  return row;
}
function lifetime() {
  same(engine.add(0x1f178c).readPointer(),input,'input global changed');
  same(game.add(0x2fba4).readPointer(),gameObject,'game global changed');
  need(gameObject.add(0xfa0).readS32()===0,'local profile changed');
  same(gameObject.add(0xfa4).readPointer(),source,'local source changed');
  same(controls,gameObject.add(0x2d4),'controls pointer changed');
  need(controls.add(0x15c).readS32()===0,'global controls smoothing changed');
  need(player.add(0x1c).readU32()===cfg.player_id && player.add(4).readU32()===3 &&
       !(player.add(0x10).readU32()&4),'player identity/deletion/render changed');
  same(player.add(0x8c).readPointer(),world,'world changed');
  need(finite(player.add(0xc14).readFloat())===cfg.spawn_clock &&
       finite(player.add(0xcc).readFloat())>0,'life changed');
  const profile={acceleration:engine.add(0x1e7f48).readS32(),
    sensitivity:finite(engine.add(0x1e7f4c).readFloat()),
    prescan:engine.add(0x1e7f5c).readS32(),
    precision:engine.add(0x20d760).readS32(),filter:engine.add(0x20d768).readS32(),
    x:axis(4,1),y:axis(3,2)};
  need(profile.acceleration===0 && profile.sensitivity===.25 && profile.prescan===0,
       'effective input profile changed');
  return profile;
}
// Passive observations of the Original post-GetInput guards. These values
// can change before the native caller evaluates them; no branch is claimed.
function timerGuard(rawEDI,phase) {
  const g=guards.timer_gate;
  need(g && g.schema==='original107-timer-guard-observation-v2','timer guard metadata');
  need(phase==='entry' || phase==='return','guard callback phase');
  // EDI context is diagnostic only. Never dereference it or assume it identifies
  // the caller. lifetime() above already checks the independently bound Game.
  const observedGame=gameObject;
  const network=engine.add(g.network_pointer_rva).readPointer();
  const global=engine.add(g.network_guard_rva).readS32();
  let session=null, pauseWord=null, localWord=null;
  if(network.toUInt32()!==0) {
    pointer(network.toString());
    const observedSession=network.add(g.network_session_offset).readPointer();
    if(observedSession.toUInt32()!==0) {
      pointer(observedSession.toString()); session=observedSession;
      pauseWord=session.add(g.session_pause_offset).readS32();
    }
    localWord=network.add(g.network_local_pause_offset).readS32();
  }
  const fallback=network.toUInt32()===0 || global!==0;
  const paused=fallback?1:pauseWord, local=fallback?1:localWord;
  const vtable=controls.readPointer();pointer(vtable.toString());
  const target=vtable.add(g.controls_action_slot_offset).readPointer();
  const gameOn=observedGame.add(g.game_on_offset).readS32();
  return {observed_ms:Date.now(),callback_phase:phase,raw_edi:rawEDI.toString(),
    raw_edi_matches_bound_game:rawEDI.equals(gameObject),observed_game:observedGame.toString(),
    game_binding:'ARM_GLOBAL_LIFETIME_VERIFIED',caller_game_binding_proven:false,game_on:gameOn,
    menu_on:observedGame.add(g.game_menu_offset).readS32(),
    input_enabled:input.add(g.input_enabled_offset).readS32(),
    local_source:observedGame.add(0xfa4).readPointer().toString(),
    network:network.toString(),network_global_guard:global,
    session:session===null?null:session.toString(),session_pause_word:pauseWord,
    local_pause_word:localWord,derived_is_paused:paused,derived_local_pause:local,
    controls_vtable:vtable.toString(),virtual_action_target:target.toString(),
    expected_vtable_matches:vtable.equals(game.add(g.controls_vtable_rva)),
    expected_action_target_matches:target.equals(game.add(guards.sites.action.rva)),
    derived_create_action_gate_open:gameOn!==0 && paused===0 && local===0,
    actual_branch_proven:false};
}
function entry(thread) {
  if(!running()) return false;
  need(Number.isInteger(thread)&&thread>0,'invalid input thread');
  if(inputThread!==null) need(thread===inputThread,'observed timer thread changed');
  need(calls<cfg.max_calls,'call bound'); calls++; lifetime(); return true;
}
function currentInput(thread) {
  const row=activeInputs.get(thread);
  if(row) return row;
  if(!enabled) return null;
  need(!ready,'unbound internal input site after readiness');
  need(++warmupSkipped<=16,'warmup bound');
  return null;
}
rpc.exports={
  arm(c,g) {
    need(!used && Process.arch==='ia32' && Process.pointerSize===4,'single ia32 arm');
    need(c && c.pid===Process.id,'PID mismatch');
    need(Number.isInteger(c.max_records)&&c.max_records>0&&c.max_records<=256,'queue bound');
    need(Number.isInteger(c.max_calls)&&c.max_calls>0&&c.max_calls<=4096,'call bound');
    need(Number.isInteger(c.ttl_ms)&&c.ttl_ms>0&&c.ttl_ms<=90000,'TTL bound');
    need(g && g.timer_gate && g.timer_gate.schema==='original107-timer-guard-observation-v2','timer guard metadata required');
    guards=g; cfg=JSON.parse(JSON.stringify(c));
    engine=pointer(c.engine_base); game=pointer(c.game_base);
    need(engine.toUInt32()%4096===0&&game.toUInt32()%4096===0,'module base alignment');
    input=pointer(c.input); gameObject=pointer(c.game); controls=pointer(c.controls);
    source=pointer(c.source); player=pointer(c.player); world=pointer(c.world);
    need(Number.isInteger(c.player_id)&&c.player_id>0&&Number.isFinite(c.spawn_clock)&&c.spawn_clock>0,'player registry');
    need(original(),'full Original input/action fingerprint'); lifetime();
    used=true; armedMs=Date.now(); lastMs=armedMs; expiresMs=armedMs+c.ttl_ms; enabled=true;
    try {
      handles.push(Interceptor.attach(engine.add(guards.sites.input.rva),{
        onEnter() { this.row=null; try {
          if(!entry(this.threadId)) return;
          need(!activeInputs.has(this.threadId),'nested GetInput');
          same(this.context.ecx,input,'GetInput this differs');
          const sp=pointer(this.context.esp.toString());
          same(sp.readPointer(),game.add(guards.callers.input_return_rva),'non-timer GetInput caller');
          const prescan=bool(sp.add(4).readS32()); need(!prescan,'unexpected prescan call');
          if(inputThread===null) inputThread=this.threadId;
          const row={kind:'input',id:calls,thread:this.threadId,prescan,entry_sp:sp.toString(),
            caller:sp.readPointer().toString(),entered_ms:Date.now(),profile:lifetime(),
            timer_guard_entry:timerGuard(this.context.edi,'entry'),timer_guard_return:null,cursor:null,recenter:null};
          this.row=row; activeInputs.set(this.threadId,row); inFlight++;
        } catch(e) { fault(e); } },
        onLeave() { const row=this.row; if(!row) return; try {
          lifetime();
          need(row.cursor && row.cursor.ok,'missing cursor result');
          need(row.recenter && row.recenter.ok,'missing/failed recenter');
          row.timer_guard_return=timerGuard(this.context.edi,'return');
          row.engine_x=finite(input.add(0x24).readFloat());
          row.engine_y=finite(input.add(0x38).readFloat()); row.left_ms=Date.now();
          latestInput.set(this.threadId,row.id); emit(row);
        } catch(e) { fault(e); } finally { activeInputs.delete(this.threadId); inFlight--; this.row=null;
          if(stoppedMs!==null&&inFlight===0)setImmediate(detachIdle); } }
      }));
      // After the Original GetCursorPos call: test eax,eax (2 bytes), je (6).
      handles.push(Interceptor.attach(engine.add(guards.sites.cursor_return.rva),{onEnter() { if(!activeInputs.has(this.threadId)&&!running()) return; try {
        const row=currentInput(this.threadId); if(!row)return; need(!row.cursor,'duplicate cursor result');
        const bp=pointer(this.context.ebp.toString());
        same(bp,ptr(row.entry_sp).sub(4),'GetInput frame differs');
        const ok=this.context.eax.toUInt32()!==0; need(ok,'GetCursorPos failed');
        const x=bp.sub(0x20).readS32(),y=bp.sub(0x1c).readS32();
        const cx=input.add(0x17a4).readS32(),cy=input.add(0x17a8).readS32();
        row.cursor={ok,x,y,center_x:cx,center_y:cy,raw_dx:x-cx,raw_dy:y-cy,epoch_ms:Date.now()};
      } catch(e) { fault(e); } }}));
      // At the Original six-byte indirect call; no USER32 export hook.
      handles.push(Interceptor.attach(engine.add(guards.sites.recenter_call.rva),{onEnter() { if(!activeInputs.has(this.threadId)&&!running()) return; try {
        const row=currentInput(this.threadId); if(!row)return; need(!row.recenter,'duplicate recenter');
        const sp=pointer(this.context.esp.toString());
        row.recenter={needed:true,x:sp.readS32(),y:sp.add(4).readS32(),ok:false,entered_ms:Date.now()};
      } catch(e) { fault(e); } }}));
      // Recenter returns here, or zero-displacement path branches here.
      handles.push(Interceptor.attach(engine.add(guards.sites.recenter_return.rva),{onEnter() { if(!activeInputs.has(this.threadId)&&!running()) return; try {
        const row=currentInput(this.threadId); if(!row)return; need(row.cursor,'recenter before cursor');
        if(row.recenter) {
          row.recenter.ok=this.context.eax.toUInt32()!==0;
          row.recenter.left_ms=Date.now(); need(row.recenter.ok,'SetCursorPos failed');
          need(row.recenter.x===row.cursor.center_x&&row.recenter.y===row.cursor.center_y,'recenter target changed');
        } else {
          need(row.cursor.raw_dx===0&&row.cursor.raw_dy===0,'nonzero displacement without recenter');
          row.recenter={needed:false,ok:true};
        }
      } catch(e) { fault(e); } }}));
      handles.push(Interceptor.attach(game.add(guards.sites.action.rva),{
        onEnter() { this.row=null; try {
          if(!running()) return;
          if(latestInput.get(this.threadId)===undefined && !ready) {
            need(++warmupSkipped<=16,'warmup action bound'); return;
          }
          if(!entry(this.threadId)) return;
          need(!activeActions.has(this.threadId)&&!activeInputs.has(this.threadId),'nested/overlapping action');
          same(this.context.ecx,controls,'CreateAction controls differs');
          const sp=pointer(this.context.esp.toString());
          same(sp.readPointer(),game.add(guards.callers.action_return_rva),'non-timer CreateAction caller');
          same(sp.add(4).readPointer(),gameObject.add(0x114),'CreateAction character differs');
          need(inputThread!==null&&this.threadId===inputThread,'action without observed timer thread');
          const action=pointer(sp.add(8).readPointer().toString());
          const prescan=bool(sp.add(12).readS32()); need(!prescan,'unexpected prescan action');
          const inputId=latestInput.get(this.threadId); need(inputId!==undefined,'action without completed input');
          const row={kind:'action',id:calls,input_id:inputId,thread:this.threadId,prescan,
            character:sp.add(4).readPointer().toString(),caller:sp.readPointer().toString(),
            entity_local_accumulator_before:finite(player.add(0xcc4).readFloat()),
            entity_received_yaw_before:finite(player.add(0xca0).readFloat()),
            entity_viewpoint_yaw_before:finite(player.add(0x344).readFloat()),
            entered_ms:Date.now(),profile:lifetime(),raw_action_yaw:null,action_pointer:action.toString()};
          this.row=row; this.action=action; activeActions.set(this.threadId,row); inFlight++;
        } catch(e) { fault(e); } },
        onLeave() { const row=this.row; if(!row) return; try {
          lifetime(); need(row.raw_action_yaw!==null,'missing pre-compose action');
          row.entity_local_accumulator_after=finite(player.add(0xcc4).readFloat());
          row.entity_received_yaw_after=finite(player.add(0xca0).readFloat());
          row.entity_viewpoint_yaw_after=finite(player.add(0x344).readFloat());
          row.action_yaw=finite(this.action.add(0x0c).readFloat());
          need(row.action_yaw===row.entity_local_accumulator_after,'action/own accumulator differ');
          row.left_ms=Date.now(); emit(row); completedSequences++; if(enabled) ready=true;
        } catch(e) { fault(e); } finally { activeActions.delete(this.threadId); inFlight--; this.row=null;
          if(stoppedMs!==null&&inFlight===0)setImmediate(detachIdle); } }
      }));
      // Original CreateAction has finished axis/button assignment and is about
      // to call ctl_ComposeActionPacket; EDI remains the bound action argument.
      handles.push(Interceptor.attach(game.add(guards.sites.compose_call.rva),{onEnter() {
        if(!activeActions.has(this.threadId)) return;
        try {
          const row=activeActions.get(this.threadId);
          need(row.raw_action_yaw===null,'duplicate compose call');
          same(this.context.edi,ptr(row.action_pointer),'compose action argument differs');
          row.raw_action_yaw=finite(this.context.edi.add(0x0c).readFloat());
          row.raw_view_yaw=finite(this.context.edi.add(0x18).readFloat());
          row.compose_entered_ms=Date.now();
        } catch(e) { fault(e); }
      }}));
      Interceptor.flush();
      timer=setTimeout(()=>stop('TTL/clock'),cfg.ttl_ms);
    } catch(e) { fault(e); throw e; }
    return {armed:true,armed_ms:armedMs,expires_ms:expiresMs,listener_count:handles.length};
  },
  drain() {
    if(enabled) running();
    if(stoppedMs!==null) detachIdle();
    let restored=false;
    try { restored=used && handles.every(h=>h===null) && original(); }
    catch(e) { fault(e); }
    const packet={records,calls,faults,dropped,in_flight:inFlight,enabled,stop_reason:reason,
      detach_errors:detachErrors.slice(),armed_ms:armedMs,expires_ms:expiresMs,
      stopped_ms:stoppedMs,observed_ms:Date.now(),restored,
      input_thread:inputThread,ready,completed_sequences:completedSequences,warmup_skipped:warmupSkipped,
      game_state_writes:0,native_qualified:false}; records=[]; return packet;
  },
  stop() { stop('host requested'); return {stopped:handles.every(h=>h===null),in_flight:inFlight}; }
};
