"""DISABLED qualification helpers; no native calls on import or shared globals."""
import hashlib
import json
import copy
import math
from pathlib import Path
import re
import stat
import time
from x11_endpoint import X11Transport,Endpoint
from a1_passive_xrecord import PassiveRecorder as JournalMethods,private_json

KEY_NAMES={'yaw_left':'J','yaw_right':'L','pitch_up':'I','pitch_down':'K'}
BUTTONS={'yaw_left':'Turn Left','yaw_right':'Turn Right','pitch_up':'Look Up','pitch_down':'Look Down'}
CONTROLS=frozenset((*KEY_NAMES,'forward'))
BASELINE_SHA='5d525c46993be88d45941fe14f4638fa001ba9583d1151a27d6df9129d9b9d9b'
NOSMOOTH_SHA='76a947f52a88271133e1f9699da38858c14f293f8fe04700594fa3b85788b6d9'
RELATIVE='vanilla/Controls/Controls0.ctl'
digest=lambda b:hashlib.sha256(b).hexdigest()


def need(ok,why):
 if not ok:raise ValueError('keyboard qualification: '+why)


def prepare_controls(raw):
 need(digest(raw)==NOSMOOTH_SHA,'exact nosmooth profile required')
 assigned=re.findall(rb'(?m)^ Key[12]: ([^\r\n]+)',raw)
 need(not set(k.encode()for k in KEY_NAMES.values())&set(assigned),'look keys already assigned')
 for control,key in KEY_NAMES.items():
  name=b' Name: TTRS '+BUTTONS[control].encode();matches=list(re.finditer(rb'(?m)^'+re.escape(name)+rb'\r?$',raw));need(len(matches)==1,'unique original button')
  start=matches[0].end();end=raw.find(b'\nButton',start);end=len(raw)if end<0 else end
  block=raw[start:end];old=b'None'if control.startswith('yaw')else b'Mouse Button '+(b'4'if control=='pitch_up'else b'5')
  match=list(re.finditer(rb'(?m)^ Key1: ('+re.escape(old)+rb')\r?$',block));need(len(match)==1,'exact original Key1')
  a,b=match[0].span(1);raw=raw[:start+a]+key.encode()+raw[start+b:]
 return raw


def install(transaction,evidence):
 need(transaction.sealed,'sealed transaction required');record=transaction.records.get(RELATIVE)
 need(record is not None and record.get('existed')is True and record.get('sha256')==BASELINE_SHA,'original profile backup absent')
 transaction.quiescent();path=transaction.path(RELATIVE);before=path.read_bytes();st=path.stat();meta=(stat.S_IMODE(st.st_mode),st.st_uid,st.st_gid)
 need(meta==(record['mode'],record['uid'],record['gid']),'profile metadata changed');after=prepare_controls(before)
 evidence=Path(evidence);(evidence/'keyboard-controls-before.ctl').write_bytes(before);(evidence/'keyboard-controls-prepared.ctl').write_bytes(after)
 path.write_bytes(after);st=path.stat();need(path.read_bytes()==after and(stat.S_IMODE(st.st_mode),st.st_uid,st.st_gid)==meta,'profile install changed bytes/metadata');transaction.quiescent()
 return dict(relative_path=RELATIVE,before_sha256=digest(before),prepared_sha256=digest(after),key_names=KEY_NAMES,only_four_key1_tokens_changed=True,effective_key_delivery_proven=False)


class KeyboardTransport(X11Transport):
 def __init__(self,pin,verify_display):
  super().__init__(pin,verify_display)
  try:self.bind_counter_abi();self.bind_keys()
  except BaseException:self.close();raise
 def bind_counter_abi(self):
  # The passive parent's controller_gc() supplied this exact public ABI. This
  # keyboard case has no GC/recorder probe, so declare it without making a call.
  self.x.XNextRequest.argtypes=[self.c.c_void_p];self.x.XNextRequest.restype=self.c.c_ulong
  self.x.XQueryKeymap.restype=self.c.c_int;self.x.XSync.restype=self.c.c_int;self.t.XTestFakeKeyEvent.restype=self.c.c_int
 def bind_keys(self):
  self.guard();old=set(self.keys.values());new={n:int(self.x.XKeysymToKeycode(self.d,ord(k.lower())))for n,k in KEY_NAMES.items()}
  need(all(type(k)is int and 8<=k<=255 for k in new.values())and len(set(new.values()))==4 and not old&set(new.values()),'unavailable/aliased normal keycodes')
  self.keys.update(new);self.guard()
 def look(self,*args,**kwargs):raise ValueError('keyboard case never emits mouse input')
 def event(self,control,down,*,submit=None):
  self.guard();need(control in CONTROLS and type(down)is bool,'fixed keyboard-only control')
  fn=self.t.XTestFakeKeyEvent;args=(self.d,self.keys[control],int(down),0)
  if not down:return self.release_event(args)
  accepted=submit(fn,*args)if down and submit is not None else fn(*args)
  need(bool(accepted),'XTest key event rejected');self.x.XSync(self.d,0)
 def release_event(self,args):
  # A metadata error must never withhold an already-required keyup.  The own
  # release path invokes the original C function exactly once; it is not a retry
  # of a call through the metadata proxy. Down retains the inherited proxy.
  proxy=getattr(self,'_passive_xrecord_proxy',None);observer=getattr(proxy,'observer',None)
  fn=proxy.inner.XTestFakeKeyEvent if proxy is not None else self.t.XTestFakeKeyEvent
  errors=[];attempt=None;row=None;first=None;native_error=None;accepted=None
  release=dict(control=next(c for c in CONTROLS if self.keys[c]==args[1]),keycode=args[1],native_invoked=False,return_value=None,xsync_result=None,neutral_verified=False,bitmap_hex=None,errors=[])
  self._current_release_receipt=release
  def failed(error):
   errors.append(error);release['errors'].append(repr(error)[:1024])
   if observer is not None:observer.failed=True
  if observer is not None:
   if len(observer.release_receipts)<96:observer.release_receipts.append(release)
   else:failed(RuntimeError('bounded keyboard release receipt'))
  if observer is not None:
   try:
    row=dict(function='XTestFakeKeyEvent',arguments=list(args),started_monotonic=time.monotonic(),host_epoch_ms=time.time()*1000,return_value=None)
    attempt=observer.reserve_attempt(row)
    first=int(self.x.XNextRequest(self.d));attempt['sequence_before']=first
   except BaseException as error:
    failed(error)
    if attempt is not None:attempt.update(validation_status='REJECTED',failure_stage='release_metadata_before_native',validation_error=repr(error)[:1024])
  try:
   if attempt is not None:attempt['native_invoked']=True
   release['native_invoked']=True;accepted=fn(*args);release['return_value']=accepted
   if row is not None:row['return_value']=accepted
   need(bool(accepted),'XTest key release rejected')
  except BaseException as error:
   native_error=error;failed(error)
   if row is not None:row['error']=repr(error)
  finally:
   if observer is not None and attempt is not None and first is not None:
    try:
     after=int(self.x.XNextRequest(self.d));attempt['sequence_after']=after
     row.update(sequence_interval=[first,after],finished_monotonic=time.monotonic())
     observer.record_emission(row);attempt['validation_status']='ACCEPTED'
    except BaseException as error:
     failed(error);attempt.update(validation_status='REJECTED',failure_stage='release_metadata_after_native',validation_error=repr(error)[:1024])
   try:
    release['xsync_result']=self.x.XSync(self.d,0);need(type(release['xsync_result'])is int and release['xsync_result']==1,'actual key release XSync failed')
   except BaseException as error:failed(error)
  if errors:
   primary=native_error or errors[0]
   for error in errors:
    if error is not primary:primary.add_note('keyboard release secondary: '+repr(error))
   raise primary
  return accepted
 def held(self,control):
  if control not in CONTROLS:return super().held(control)
  self.guard();bitmap=(self.c.c_char*32)();status=self.x.XQueryKeymap(self.d,bitmap);need(type(status)is int and status==1,'actual XQueryKeymap failed');key=self.keys[control]
  raw=bytes(bitmap);self._last_keymap=dict(control=control,keycode=key,bitmap_hex=raw.hex())
  return bool(raw[key//8]&(1<<(key%8)))


class KeyboardEndpoint(Endpoint):
 def down(self,control,*,submit=None):
  need(control in CONTROLS,'fixed keyboard down');self.verify();self.check_focus()
  self.transport.event(control,True,submit=submit)
  need(self.transport.held(control),'actual pressed key bitmap missing')
  self.record_keymap(control,True)
 def up(self,control):
  need(control in CONTROLS,'fixed keyboard up');self.verify_display()
  try:self.transport.event(control,False)
  except BaseException as error:
   # Inherited action_step calls released() only after a successful up().  On
   # failure perform that same actual bitmap check here, preserving the failure.
   try:self.released(control)
   except BaseException as neutral_error:error.add_note('keyboard release neutrality: '+repr(neutral_error))
   raise
 def released(self,control):
  need(not self.transport.held(control),'actual key release bitmap still held')
  if control in CONTROLS:self.record_keymap(control,False)
 def record_keymap(self,control,down):
  release=getattr(self.transport,'_current_release_receipt',None)
  if not down and release is not None and release['control']==control:
   release.update(neutral_verified=True,bitmap_hex=self.transport._last_keymap['bitmap_hex'])
  proxy=getattr(self.transport,'_passive_xrecord_proxy',None);journal=getattr(proxy,'observer',None)
  if journal is None or not journal.attempts:return
  attempt=journal.attempts[-1];args=attempt['metadata']['arguments']
  if args!=[self.transport.d,self.transport.keys[control],int(down),0]or attempt['native_invoked']is not True:return
  index=attempt['attempt_index']
  if any(p['native_attempt_index']==index for p in journal.keymap_proofs):return
  sample=dict(self.transport._last_keymap,down=down,native_attempt_index=index)
  journal.keymap_proofs.append(sample)
 def neutral(self,controls):
  for control in set(controls)|set(CONTROLS):self.released(control)


class KeyboardJournal:
 reserve_attempt=JournalMethods.reserve_attempt
 record_emission=JournalMethods.record_emission
 def __init__(self,transport):self.transport=transport;self.attempts=[];self.emissions=[];self.keymap_proofs=[];self.release_receipts=[];self.failed=False;self.closed=False
 def before_input(self):need(not self.failed and not self.closed,'sticky keyboard journal failure')
 def close(self,evidence):
  if self.closed:return self.final
  self.closed=True;self.transport._passive_xrecord_proxy.observer=None;errors=[];files={}
  for name,value in(('keyboard-emissions.json',self.emissions),('keyboard-attempts.json',self.attempts),('keyboard-keymaps.json',self.keymap_proofs),('keyboard-releases.json',self.release_receipts)):
   try:
    path=Path(evidence)/name;private_json(path,value);files[name]=digest(path.read_bytes())
   except BaseException as error:errors.append(name+':'+repr(error))
  self.final=dict(errors=errors,attempts=len(self.attempts),emissions=len(self.emissions),failed=self.failed,no_wire_proof=True,files=files,keycodes={c:self.transport.keys[c]for c in CONTROLS},attempt_rows=copy.deepcopy(self.attempts),emission_rows=copy.deepcopy(self.emissions),keymap_proofs=copy.deepcopy(self.keymap_proofs),release_receipts=copy.deepcopy(self.release_receipts))
  return self.final


def keyboard_journal_complete(report,verdict):
 """Validate actual key metadata and cleanup, never confer A1 qualification."""
 try:
  order=('yaw_left','forward','yaw_right','forward','pitch_up','pitch_down')
  status='PASS_LIMITED_ORIGINAL_KEYBOARD_GEOMETRY_ONLY';prep=report['shooter_preparation'];j=report['keyboard_journal']
  need(report['status']==prep['status']==status and report['observer_mode']=='keyboard-qualification','keyboard-only result')
  need(report['qualified']is False and report['normal_route_or_fire']is False and report['diagnostic_only']is True and report['collector_requested']is False,'no gameplay qualification or collector')
  need(not report['errors']and not j['errors']and j['failed']is False and j['no_wire_proof']is True,'sticky input error')
  need(not any(k in report for k in('collector_arm','collector_cleanup','collector_worker','collector_ipc_timings','passive_xrecord_arm')),'unexpected recorder/collector')
  need(report['restoration']['restored']is True and report['post_close_logs']['accepted']is True,'normal restoration and logs')
  need(set(report['cleanup'])=={'server','vanilla','botA'}and all(x['closed']is True for x in report['cleanup'].values()),'all own roles normally closed')
  need({str(k)for k in report['displays']}=={'154','155'}and all(x['closed']is True for x in report['displays'].values()),'own displays normally closed')
  need(verdict.reasons==('window_not_passed',),'unmodified diagnostic-only generic verdict')
  need(all(type(prep[k])is int and prep[k]==6 for k in('actions_admitted','actions_attempted','actions_released','actions_acked','actions_completed')),'six separately acknowledged actions')
  keys=j['keycodes'];need(set(keys)==set(CONTROLS)and all(type(x)is int and 8<=x<=255 for x in keys.values())and len(set(keys.values()))==5,'actual distinct keycodes')
  rows=j['emission_rows'];attempts=j['attempt_rows'];proofs=j['keymap_proofs'];phases=report['input_phase_timings']
  need(type(j['attempts'])is int and type(j['emissions'])is int and j['attempts']==j['emissions']==len(rows)==len(attempts)==len(proofs)==12 and len(phases)==6,'exact twelve native DownUp calls')
  finite=lambda x:type(x)in(int,float)and math.isfinite(x)
  transport=None;last_finished=None;previous_sequence_end=None
  for phase_index,control in enumerate(order):
   p=phases[phase_index];need(p['actions']=={'vanilla':control}and p['status']=='PASS'and p['errors']==[]and p['requested_seconds']==.1,'exact normal key phase')
   a,b,c=p['held_started'],p['release_started'],p['finished'];need(all(finite(v)for v in(a,b,c,p['input_to_release_seconds']))and 0<=a<=b<=c and 0<=c-a<=.35 and p['input_to_release_seconds']==c-a,'unchanged held/release deadline')
   need(last_finished is None or last_finished<=a,'overlapping key phases');last_finished=c
   events=p['emissions'];need(len(events)==1,'one normal pressed event');event=events[0]
   need(event['role']=='vanilla'and event['control']==control and event['request_confirmed']is True and all(finite(event[k])for k in('started','finished'))and a<=event['started']<=event['finished']<=b,'actual press receipt')
   for down in(True,False):
    index=phase_index*2+int(not down);r=rows[index];t=attempts[index];proof=proofs[index];args=r['arguments']
    need(type(r['index'])is int and r['index']==index and r['function']=='XTestFakeKeyEvent'and type(r['return_value'])is int and r['return_value']==1 and'error'not in r,'actual accepted normal key call')
    need(type(args)is list and len(args)==4 and all(type(x)is int for x in args)and args[0]>0 and args[1:]==[keys[control],int(down),0],'actual transport/key/direction')
    if transport is None:transport=args[0]
    need(args[0]==transport,'same actual transport')
    begin,end=r['sequence_interval'];need(type(begin)is int and type(end)is int and 0<begin<end<=0xffffffff and end-begin<=4,'unchanged emission interval guard')
    need(previous_sequence_end is None or previous_sequence_end<=begin,'actual transport counter reversed');previous_sequence_end=end
    need(type(t['attempt_index'])is int and t['attempt_index']==index and t['native_invoked']is True and t['validation_status']=='ACCEPTED'and t['sequence_before']==begin and t['sequence_after']==end and t['metadata']=={k:v for k,v in r.items()if k!='index'},'same actual attempted and accepted call')
    start,finish=r['started_monotonic'],r['finished_monotonic'];low,high=(event['started'],event['finished'])if down else(b,c)
    need(finite(start)and finite(finish)and low<=start<=finish<=high,'native call lies in actual press/release interval')
    need(proof['control']==control and type(proof['keycode'])is int and proof['keycode']==keys[control]and proof['down']is down and type(proof['native_attempt_index'])is int and proof['native_attempt_index']==index,'matching actual bitmap read')
    bits=bytes.fromhex(proof['bitmap_hex']);need(len(bits)==32,'exact key bitmap')
    for name,keycode in keys.items():need(bool(bits[keycode//8]&(1<<(keycode%8)))is(down and name==control),'actual DownUp and other-key neutrality')
  return True
 except (KeyError,TypeError,ValueError,IndexError,AttributeError):return False
