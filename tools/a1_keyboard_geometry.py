"""Pure bounded key qualification. Callbacks supply real evidence at runtime."""
import copy
import math
import colt_preparation as CP
from shooter_policy import require,number,valid,key,wrap

ORDER=('yaw_left','forward','yaw_right','forward','pitch_up','pitch_down')
EPS=CP.EPS


class KeyboardScope:
 def __init__(self):self.count=0;self.failed=False
 def admit(self,role,control,seconds):
  try:
   require(not self.failed and self.count<len(ORDER)and role=='vanilla'and type(seconds)in(int,float)and seconds==.1 and control==ORDER[self.count],'fixed keyboard qualification order')
   self.count+=1
  except BaseException:self.failed=True;raise


def run(read_frame,step,clock,sleep,receipt,*,started):
 receipt.update(status='IN_PROGRESS',qualified=False,a1_pass=False,mouse_gain_fixed=False,input_once_proven=False,actual_shot_proven=False,foreign_hit_proven=False,first_processed_state_proven=False,observations=[],actions=[],yaw=[],pitch=[],actions_admitted=0,actions_attempted=0,actions_released=0,actions_acked=0,actions_completed=0)
 scope=KeyboardScope();identities={};ticks={};previous_index=-1;last_clock=started
 def now():
  nonlocal last_clock
  value=clock();require(number(value)and value>=last_clock,'invalid/reversed keyboard clock');CP.check_window(started,value);last_clock=value;return value
 def same(a,b):return abs(wrap(a-b))<=EPS
 def observe(phase):
  nonlocal previous_index
  entry=dict(phase=phase,requested_at=now());receipt['observations'].append(entry);require(len(receipt['observations'])<=CP.MAX_OBSERVATIONS,'bounded keyboard observations')
  try:
   f=copy.deepcopy(read_frame());entry['frame']=f;finished=now();a,b=f['monotonic_started'],f['monotonic_finished']
   require(number(a)and number(b)and 0<=a<=b<=finished and finished-a<=.2,'fresh paired keyboard state required')
   seq=f['successful_read_sequence'];index=seq['index'];require(type(index)is int and index>previous_index,'successful paired read sequence must advance')
   if index>0:
    prev=seq['previous'];require(type(prev['index'])is int and prev['index']==index-1 and number(prev['monotonic_finished'])and prev['monotonic_finished']<=a,'actual prior successful pair required')
   previous_index=index
   for source,pid_key in(('roles','server_process_identity'),('client_roles','vanilla_process_identity')):
    pid=f[pid_key];require(type(pid)is list and len(pid)==2 and all(type(x)is int and x>1 for x in pid),'real process generation required')
    require(set(f[source])=={'vanilla','botA'},'two actual role rows required')
    for role,row in f[source].items():
     valid(row);ident=(tuple(pid),key(row));which=(source,role)
     if which not in identities:identities[which]=ident
     require(identities[which]==ident,'keyboard process/entity/world/life changed');require(row['game_tick']>=ticks.get(which,row['game_tick']),'native clock reversed');ticks[which]=row['game_tick']
    r=f[source]['vanilla']['rotation_diagnostic'];flags=r['player_flags']
    require(type(flags)is int and flags&1 and not flags&0x500 and all(number(r[k])for k in('last_action_yaw_deg','local_action_yaw_deg','relative_view_yaw_deg')),'uninitialized/disconnected/zoom state')
   require(f['server_process_identity']!=f['vanilla_process_identity'],'distinct actual peers required')
   require(f['roles']['vanilla']['slot']==f['client_roles']['vanilla']['slot'],'same actual Original slot')
   return f
  except BaseException as error:entry['error']=repr(error);raise
 def values(f,axis):return CP.levels(f,axis)
 def stable(phase,expected=None,not_before=None):
  deadline=now()+2;previous=None;held=None
  for unused in range(42):
   f=observe(phase);v=values(f,'x')
   if expected is not None:require(all(same(x,expected)for x in v),'uncommanded cumulative yaw after acknowledgement')
   signature=(f['roles']['vanilla']['placement'][3],*v)
   quiet=((not_before is None or f['monotonic_started']>=not_before)and math.dist(f['roles']['vanilla']['current_translation_absolute'],[0,0,0])<=.2 and bool(f['roles']['vanilla'].get('support_pointer'))and all(abs(wrap(f[source]['vanilla']['rotation_diagnostic']['relative_view_yaw_deg']))<=EPS for source in('roles','client_roles'))and all(same(x,v[1])for x in v))
   if quiet:
    if previous is None or not all(same(x,y)for x,y in zip(signature,previous)):held=tuple(f[source]['vanilla']['game_tick']for source in('roles','client_roles'))
    if held is not None and all(f[source]['vanilla']['game_tick']-held[i]>=.1 for i,source in enumerate(('roles','client_roles'))):
     require(now()<deadline,'keyboard settling deadline');CP.live_ready(f);return f
    previous=signature
   else:held=previous=None
   require(now()<deadline,'keyboard motion did not settle');sleep(.05)
  raise ValueError('bounded keyboard settling failed')
 def act(control,before):
  scope.admit('vanilla',control,.1);event=dict(control=control,status='IN_PROGRESS',requested_at=now());receipt['actions'].append(event)
  receipt['actions_admitted']+=1
  def guard():
   f=observe('pre-emission-'+control);event['before']=f
   if control=='forward':
    require(all(same(a,b)for a,b in zip(values(f,'x'),values(before,'x')))and same(f['roles']['vanilla']['placement'][3],before['roles']['vanilla']['placement'][3])and all(same(f[source]['vanilla']['rotation_diagnostic']['relative_view_yaw_deg'],before[source]['vanilla']['rotation_diagnostic']['relative_view_yaw_deg'])for source in('roles','client_roles')),'input baseline drift before forward')
   else:CP.baseline_equal(f,before)
   return f
  try:
   receipt['actions_attempted']+=1
   output=step('vanilla',control,.1,before_press=guard);event['output']=copy.deepcopy(output)
   require(output.get('released')is True,'actual normal release required');timing=output['input_phase_timing'];emissions=timing['emissions'];require(timing['status']=='PASS'and len(emissions)==1,'normal emitted request required')
   e=emissions[0];a,b=e['started'],e['finished'];require(e['role']=='vanilla'and e['control']==control and e['request_confirmed']is True and number(a)and number(b)and event['requested_at']<=a<=b<=now(),'normal key request identity/timing')
   require('before'in event,'final pre-emission guard not executed');require(number(timing['finished'])and timing['finished']>=b,'real release timestamp required')
   receipt['actions_released']+=1
   event.update(status='RELEASED_REVIEW_REQUIRED',request_finished=b,release_finished=timing['finished']);return event
  except BaseException as error:event.update(status='FAIL',error=repr(error));raise
 def ack(event,axis,sign):
  before=event['before'];origin=values(before,axis)[1];last=origin;deadline=event['request_finished']+2;previous=None;held=None;other='y'if axis=='x'else'x'
  for unused in range(42):
   f=observe('ack-'+event['control']);CP.live_ready(f,paired_geometry=False);v=values(f,axis);delta=wrap(v[1]-origin);increment=wrap(v[1]-last);last=v[1]
   require(increment*sign>=-EPS and delta*sign>=-EPS,'reversed keyboard cumulative response')
   require(all(same(a,b)for a,b in zip(values(f,other),values(before,other))),'uncommanded other axis')
   for source in('roles','client_roles'):
    require(math.dist(f[source]['vanilla']['placement'][:3],before[source]['vanilla']['placement'][:3])<=EPS and math.dist(f[source]['botA']['placement'][:3],before[source]['botA']['placement'][:3])<=EPS,'uncommanded translation during look')
   fresh=f['monotonic_started']>=event['request_finished']and all(f[source]['vanilla']['game_tick']>before[source]['vanilla']['game_tick']for source in('roles','client_roles'))
   ready=fresh and delta*sign>EPS and all(same(x,v[1])for x in v)
   if ready:
    if axis=='y':
     for source in('roles','client_roles'):
      old=CP.geometry(before[source]['vanilla'],before[source]['botA']);new=CP.geometry(f[source]['vanilla'],f[source]['botA'])
      require(same(wrap(new['pitch']-old['pitch']),delta)and math.dist(new['eye'],old['eye'])<=EPS and math.dist(new['target'],old['target'])<=EPS,'Original pitch geometry disagrees')
    if previous is None or not all(same(x,y)for x,y in zip(v,previous)):held=tuple(f[source]['vanilla']['game_tick']for source in('roles','client_roles'))
    if held is not None and all(f[source]['vanilla']['game_tick']-held[i]>=.1 for i,source in enumerate(('roles','client_roles'))):
     require(now()<deadline,'normal key ACK deadline');receipt['actions_acked']+=1;event.update(status='ACKED',ack_frame=f,action_delta_deg=delta);return f
    previous=v
   else:previous=held=None
   require(now()<deadline,'normal key ACK not observed');sleep(.05)
  raise ValueError('bounded keyboard ACK failed')
 try:
  initial=stable('keyboard-before');before=initial
  for control,sign in(('yaw_left',1),('yaw_right',-1)):
   origin=copy.deepcopy(before);event=act(control,before);acked=ack(event,'x',sign)
   check=observe('before-forward-'+control);expected=values(acked,'x')[1];require(all(same(v,expected)for v in values(check,'x')),'uncommanded cumulative yaw before forward')
   forward=act('forward',acked);after=stable('settling-'+control,expected,forward['release_finished'])
   raw=wrap(after['roles']['vanilla']['placement'][3]-origin['roles']['vanilla']['placement'][3]);result=dict(control=control,before=origin,after=after,body_delta_yaw_deg=raw,action_delta_deg=event['action_delta_deg']);receipt['yaw'].append(result)
   require(same(raw,event['action_delta_deg']),'body yaw disagrees with acknowledged key angle');receipt['actions_acked']+=1;forward.update(status='ACKED',ack_frame=after);before=after
  yaw_return=abs(wrap(before['roles']['vanilla']['placement'][3]-initial['roles']['vanilla']['placement'][3]));receipt['yaw_return_error_deg']=yaw_return;require(yaw_return<=.75,'opposite keyboard yaw did not return')
  pitch_start=copy.deepcopy(before)
  for control,sign in(('pitch_up',1),('pitch_down',-1)):
   event=act(control,before);before=ack(event,'y',sign);receipt['pitch'].append(copy.deepcopy(event))
  error=abs(wrap(CP.geometry(before['roles']['vanilla'],before['roles']['botA'])['pitch']-CP.geometry(pitch_start['roles']['vanilla'],pitch_start['roles']['botA'])['pitch']));receipt['pitch_return_error_deg']=error
  require(error<=.75,'opposite keyboard pitch did not return');require(scope.count==6,'exact six keyboard actions');CP.live_ready(before)
  receipt.update(status='PASS_LIMITED_ORIGINAL_KEYBOARD_GEOMETRY_ONLY',actions_completed=receipt['actions_acked'],elapsed_seconds=now()-started);return receipt
 except BaseException as error:receipt.update(status='FAIL',error=repr(error),actions_completed=receipt['actions_acked']);raise
