"""Pure bounded normal-input pitch feedback; never native input or fire permission.

Observe/act/settled/acknowledge are exact copies of the frozen Colt parent;
only the separate orchestration and conservative input scope are new.
"""
import copy
import math
import hashlib
from pathlib import Path
from a1_passive_xrecord import PassiveRecorder as JournalMethods, private_json
from colt_preparation import (EPS, MAX_SECONDS, MAX_ACTIONS, MAX_OBSERVATIONS,
    ACK_SECONDS, check_window, vector, geometry, levels, live_ready, baseline_equal, same)
from shooter_policy import require, number, valid, key, wrap


class FeedbackScope:
    def __init__(self):
        self.count=0

    def admit(self,role,control,seconds,pixels):
        require(self.count<48,'pitch feedback action bound / scope exhausted')
        require(role=='vanilla' and control=='look_vertical' and type(seconds)in(int,float)
                and seconds==.1 and type(pixels)is int
                and (pixels==12 if self.count==0 else abs(pixels)==1),
                'fixed normal pitch feedback input scope')
        self.count+=1


class FeedbackJournal:
    """Existing in-memory attempt guard, without any recorder/worker or native call."""
    reserve_attempt=JournalMethods.reserve_attempt
    record_emission=JournalMethods.record_emission

    def __init__(self,transport):
        self.transport=transport;self.attempts=[];self.emissions=[];self.failed=False;self.closed=False

    def before_input(self):
        if self.failed or self.closed:raise RuntimeError('sticky pitch journal failure')

    def close(self,evidence):
        if self.closed:return self.final
        self.closed=True;self.transport._passive_xrecord_proxy.observer=None;errors=[];files={}
        for name,value in(('pitch-input-emissions.json',self.emissions),('pitch-input-attempts.json',self.attempts)):
            try:
                path=Path(evidence)/name;private_json(path,value)
                files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
            except BaseException as error:errors.append(name+':'+repr(error))
        self.final=dict(errors=errors,failed=self.failed,no_wire_proof=True,
            attempts=len(self.attempts),emissions=len(self.emissions),files=files,
            attempt_rows=copy.deepcopy(self.attempts),emission_rows=copy.deepcopy(self.emissions))
        return self.final


def journal_complete(report,verdict):
    """Actual normal relative-motion metadata and cleanup, never A1 acceptance."""
    try:
        prep=report['shooter_preparation'];j=report['pitch_journal']
        require(report['status']==prep['status']=='PASS_LIMITED_NATIVE_ACK_PITCH_FEEDBACK_RETURN_ONLY'
                and report['observer_mode']=='pitch-feedback','fixed feedback result')
        require(report['qualified']is False and report['normal_route_or_fire']is False
                and report['diagnostic_only']is True and report['collector_requested']is False,'no qualification or collector')
        require(not report['errors'] and not j['errors'] and j['failed']is False
                and j['no_wire_proof']is True,'sticky journal error')
        require(not any(k in report for k in('collector_arm','collector_cleanup','collector_worker',
                'collector_ipc_timings','passive_xrecord_arm')),'unexpected instrumentation')
        require(report['restoration']['restored']is True and report['post_close_logs']['accepted']is True,'restore/log proof')
        require(set(report['cleanup'])=={'server','vanilla','botA'}
                and all(x['closed']is True for x in report['cleanup'].values()),'normal own role closes')
        require({str(k)for k in report['displays']}=={'154','155'}
                and all(x['closed']is True for x in report['displays'].values()),'normal own display closes')
        require(verdict.reasons==('window_not_passed',),'unmodified generic diagnostic verdict')
        n=prep['actions_acked'];actions=prep['actions'];rows=j['emission_rows'];attempts=j['attempt_rows'];phases=report['input_phase_timings']
        require(type(n)is int and 2<=n<=48 and n==len(actions)==len(rows)==len(attempts)==len(phases)
                and type(j['attempts'])is int and type(j['emissions'])is int and j['attempts']==j['emissions']==n
                and prep['actions_attempted']==n and prep['corrections_acked']==n-1,'exact actual action/call counts')
        transport=None;last_end=None;last_sequence=None
        for i,(event,row,attempt,phase)in enumerate(zip(actions,rows,attempts,phases)):
            pixels=event['pixels'];require(type(pixels)is int and(pixels==12 if i==0 else abs(pixels)==1),'fixed relative pixels')
            require(event['status']=='ACKED' and event['axis_ack']['axis']=='y'
                    and event['axis_ack']['pixels']==pixels,'actual native axis ACK')
            require(phase['actions']=={'vanilla':'look_vertical'} and phase['status']=='PASS'
                    and phase['errors']==[] and phase['requested_seconds']==.1,'actual normal motion phase')
            a,b,c=phase['held_started'],phase['release_started'],phase['finished']
            require(all(number(v)for v in(a,b,c,phase['input_to_release_seconds']))
                    and 0<=a<=b<=c and c-a<=.35 and phase['input_to_release_seconds']==c-a
                    and(last_end is None or last_end<=a),'actual release bound')
            last_end=c;emissions=phase['emissions'];require(len(emissions)==1,'one requested normal motion')
            emission=emissions[0]
            require(emission['role']=='vanilla' and emission['control']=='look_vertical'
                    and emission['pixels']==pixels and emission['axis']=='y'
                    and emission['request_confirmed']is True
                    and all(number(emission[k])for k in('started','finished'))
                    and a<=emission['started']<=emission['finished']<=b,'matching actual input emission')
            require(type(row['index'])is int and row['index']==i
                    and row['function']=='XTestFakeRelativeMotionEvent'
                    and type(row['return_value'])is int and row['return_value']==1 and'error'not in row,'accepted native motion call')
            args=row['arguments']
            require(type(args)is list and len(args)==4 and all(type(x)is int for x in args)
                    and args[0]>0 and args[1:]==[0,pixels,0],'actual relative-motion arguments')
            if transport is None:transport=args[0]
            require(args[0]==transport,'same existing transport')
            begin,end=row['sequence_interval']
            require(type(begin)is int and type(end)is int and 0<begin<end<=0xffffffff
                    and end-begin<=4 and(last_sequence is None or last_sequence<=begin),'unchanged counter bound')
            last_sequence=end
            require(type(attempt['attempt_index'])is int and attempt['attempt_index']==i
                    and attempt['native_invoked']is True and attempt['validation_status']=='ACCEPTED'
                    and attempt['sequence_before']==begin and attempt['sequence_after']==end
                    and attempt['metadata']=={k:v for k,v in row.items()if k!='index'},'actual attempted and accepted call identical')
            start,finish=row['started_monotonic'],row['finished_monotonic']
            require(number(start)and number(finish)
                    and emission['started']<=start<=finish<=emission['finished'],'native call within actual emitted interval')
        return True
    except (KeyError,TypeError,ValueError,IndexError,AttributeError):return False


def run(read_roles,step,clock,sleep,receipt,*,started,runner_deadline):
    receipt.update(status='IN_PROGRESS',qualified=False,a1_pass=False,mouse_gain_fixed=False,
        input_once_proven=False,actual_shot_proven=False,foreign_hit_proven=False,
        first_processed_state_proven=False,actions=[],actions_attempted=0,actions_acked=0,
        corrections_acked=0,role_observations=[],stage='initial',successful_read_sequence_required=True)
    last_clock=started;identities=None;ticks={};last_sequence=None;aim_deadline=None
    require_successful_read_sequence=True
    require(number(started) and started>=0 and number(runner_deadline)
            and started<runner_deadline<=started+90.,'bounded runner deadline required')
    raw_step=step;scope=FeedbackScope()

    def now(reserve=0.):
        nonlocal last_clock
        value=clock()
        require(number(value) and number(last_clock) and value>=last_clock>=started>=0,
                'invalid/backwards shared preparation clock')
        last_clock=value;check_window(started,value)
        require(number(reserve) and reserve>=0,'invalid deadline reserve')
        deadline=min(started+MAX_SECONDS,runner_deadline,
                     aim_deadline if aim_deadline is not None else runner_deadline)
        require(value+reserve<deadline,'pitch feedback deadline / input reserve budget exceeded')
        return value

    def bounded_sleep(seconds):
        now();sleep(seconds);now()

    def checked_step(role,control,seconds,*,before_press,pixels):
        # Recheck after the inherited final fresh-state guard, immediately before input.
        def final_check():
            before_press();now(2.35)
        scope.admit(role,control,seconds,pixels)
        now(2.35)
        output=raw_step(role,control,seconds,before_press=final_check,pixels=pixels)
        # Preserve the returned actual input receipt before any late/timing failure.
        receipt['actions'][-1]['output']=copy.deepcopy(output)
        timing=output.get('input_phase_timing',{}) if isinstance(output,dict) else {}
        a,b=timing.get('held_started'),timing.get('release_started')
        ended=timing.get('finished')
        require(number(a) and number(b) and number(ended) and 0<=a<=b<=ended
                and b-a<=.35 and ended-a<=.35,'normal input through release hold bound exceeded')
        now()
        return output
    step=checked_step

    def observe(phase, *, after_fire=False):
        nonlocal identities,last_sequence
        entry=dict(phase=phase,requested_at=now())
        require(len(receipt['role_observations'])<MAX_OBSERVATIONS,'bounded role observations')
        receipt['role_observations'].append(entry)
        try:
            frame=copy.deepcopy(read_roles());entry['frame']=frame;finished=now()
            a,b=frame.get('monotonic_started'),frame.get('monotonic_finished')
            require(number(a) and number(b) and entry['requested_at']<=a<=b<=finished and finished-a<=.2,
                    'fresh requested paired role frame required')
            processes=[]
            for name in ('server_process_identity','vanilla_process_identity'):
                p=frame.get(name)
                require(type(p)in(list,tuple)and len(p)==2 and all(type(v)is int and v>1 for v in p),
                        'paired process identity missing')
                processes.append(tuple(p))
            require(processes[0]!=processes[1],'two distinct reader processes required')
            keys={}
            for source in ('roles','client_roles'):
                require(set(frame[source])=={'vanilla','botA'},'exact two own roles required')
                for role,row in frame[source].items():
                    if after_fire and role=='botA':
                        require(row.get('present')is True and number(row.get('health'))
                                and number(row.get('spawned_tick'))and row['spawned_tick']>0,'same-life target HP evidence')
                        require(all(type(row.get(k))is int and row[k]>0 for k in
                                    ('entity_id','entity_pointer','world_pointer')),'native target identity')
                        vector(row.get('placement'),6,'target placement')
                        vector(row.get('current_translation_absolute'),3,'target velocity')
                        require(number(row.get('game_tick')),'native target tick')
                    else:valid(row)
                    flags=row.get('rotation_diagnostic',{}).get('player_flags')
                    require(type(flags)is int and 0<=flags<=0xffffffff and flags&1 and not flags&(0x100|0x400),
                            'uninitialized/disconnected/zoom state')
                    require(row['game_tick']>=ticks.get((source,role),row['game_tick']),'native tick reversed')
                    weapon=row.get('weapons')or{};geom=row.get('colt_preparation')or{}
                    objects=(weapon.get('entity_pointer'),weapon.get('entity_id'),
                             geom.get('animator_pointer'),geom.get('animator_id'))
                    require(all(type(v)is int and v>0 for v in objects),'Original weapon/animator generation identity missing')
                    keys[source,role]=(key(row),objects)
                require(frame[source]['vanilla']['slot']!=frame[source]['botA']['slot']
                        and frame[source]['vanilla']['game_tick']==frame[source]['botA']['game_tick'],
                        'two rows from one native snapshot required')
            for role in ('vanilla','botA'):
                x,y=frame['roles'][role],frame['client_roles'][role]
                require(all(x[k]==y[k] for k in ('slot','entity_id','spawned_tick')), 'paired role life identity differs')
            identity=(tuple(processes),keys)
            if identities is None:identities=copy.deepcopy(identity)
            require(identity==identities,'preparation process/life/world identity changed')
            ticks.update({(source,role):row['game_tick'] for source in ('roles','client_roles')
                          for role,row in frame[source].items()})
            marker=frame.get('successful_read_sequence')
            if marker is None:
                require(not require_successful_read_sequence and last_sequence is None,'successful read sequence missing')
            else:
                require(type(marker)is dict and set(marker)=={'index','previous'},'successful read sequence shape')
                i,prev=marker['index'],marker['previous']
                require(type(i)is int and 0<=i<1024,'successful read sequence index')
                if i==0:require(prev is None,'successful read predecessor at zero')
                else:
                    require(type(prev)is dict and set(prev)=={'index','monotonic_started','monotonic_finished'}
                            and prev['index']==i-1 and number(prev['monotonic_started'])
                            and number(prev['monotonic_finished'])
                            and 0<=prev['monotonic_started']<=prev['monotonic_finished']<=a,
                            'successful read predecessor invalid')
                if last_sequence is not None:
                    require(i>last_sequence['index'] and prev['monotonic_started']>=last_sequence['monotonic_started']
                            and prev['monotonic_finished']>=last_sequence['monotonic_finished'],
                            'successful read sequence reversed/reused')
                last_sequence=dict(index=i,monotonic_started=a,monotonic_finished=b)
            entry['status']='OBSERVED';return frame
        except BaseException as error:
            entry.update(status='FAIL',error=repr(error));raise


    def act(role,control,seconds,*,before_press=lambda:None,pixels=None,state_guard=live_ready):
        stage=receipt['stage']
        allowed=(role=='vanilla' and seconds==.1 and
            ((stage=='calibration' and control in ('look_right','look_left','forward') and pixels is None)
             or(stage=='pitch' and control=='look_vertical' and type(pixels)is int and abs(pixels)==12)
             or(stage=='aim' and control in ('look_horizontal','look_vertical') and type(pixels)is int and 1<=abs(pixels)<=12)
             or(stage=='fire' and control=='fire' and pixels is None)))
        require(allowed,'fixed Colt preparation input scope')
        require(len(receipt['actions'])<MAX_ACTIONS,'shared preparation action bound')
        event=dict(role=role,control=control,seconds=seconds,pixels=pixels,stage=stage,
                   status='IN_PROGRESS',requested_at=now(seconds+.25))
        receipt['actions'].append(event);receipt['actions_attempted']=len(receipt['actions']);pressed=False
        try:
            frame=observe(stage+'-before-input');state_guard(frame);now(seconds+.25)
            def final_check():
                nonlocal pressed
                require(not pressed,'one pre-emission callback required');pressed=True
                current=observe(stage+'-pre-emission');state_guard(current)
                event['pre_emission_frame']=copy.deepcopy(current)
                now(seconds+.25);before_press();checked=now(seconds+.25)
                require(checked-current['monotonic_started']<=.2,'final paired state became stale before request')
                event['pre_emission_checked_at']=checked
            kw={'before_press':final_check}
            if pixels is not None:kw['pixels']=pixels
            output=step(role,control,seconds,**kw);event['output']=copy.deepcopy(output);now()
            require(pressed and isinstance(output,dict)and output.get('released')is True,
                    'normal input release/pre-emission receipt missing')
            timing=output.get('input_phase_timing',{});emissions=timing.get('emissions',[])
            require(timing.get('status')=='PASS'and len(emissions)==1,'normal input emission receipt missing/ambiguous')
            e=emissions[0];a,b=e.get('started'),e.get('finished')
            require(e.get('role')==role and e.get('control')==control and e.get('request_confirmed')is True
                    and number(a)and number(b)and event['pre_emission_checked_at']<=a<=b<=now(),
                    'normal request identity/timing invalid')
            expected=(12 if control=='look_right'else-12)if control in('look_right','look_left')else pixels
            require(e.get('pixels')==expected,'normal request pixels differ from pending input')
            if pixels is not None:require(e.get('axis')==('y'if control=='look_vertical'else'x'),'normal request axis mismatch')
            event['after_input_frame']=observe(stage+'-after-input',after_fire=stage=='fire')
            event.update(status='RELEASED_REVIEW_REQUIRED',request_finished=b)
            return output
        except BaseException as error:
            event.update(status='FAIL',error=repr(error));raise


    def settled(phase):
        deadline=now()+ACK_SECONDS;previous=None;held=None
        for unused in range(42):
            frame=observe(phase);live_ready(frame)
            signature=tuple(levels(frame,'x')+levels(frame,'y'))+tuple(
                x for source in('roles','client_roles') for role in('vanilla','botA')
                for x in(*frame[source][role]['placement'],*frame[source][role]['colt_preparation']['viewpoint'],
                          frame[source][role]['colt_preparation']['eyes_y_offset']))
            if previous is None or not all(abs(x-y)<=EPS for x,y in zip(signature,previous)):
                held=(frame['roles']['vanilla']['game_tick'],frame['client_roles']['vanilla']['game_tick'])
            if all(frame[source]['vanilla']['game_tick']-held[i]>=.1 for i,source in enumerate(('roles','client_roles'))):
                require(now()<deadline,'normal geometry settling deadline exceeded');return frame
            previous=signature;require(now()<deadline,'normal geometry settling deadline exceeded');bounded_sleep(.05)
        raise ValueError('bounded geometry settling clock did not advance')


    def acknowledge(before,axis,pixels,event,*,gain=None):
        deadline=event['request_finished']+ACK_SECONDS
        origin=levels(before,axis)[1];last=origin;held=None;previous=None
        other='y'if axis=='x'else'x'
        g0=geometry(before['roles']['vanilla'],before['roles']['botA'])
        physical_field='yaw'if axis=='x'else'pitch'
        for unused in range(42):
            frame=observe('ack-'+event['control']);live_ready(frame,paired_geometry=False)
            values=levels(frame,axis);delta=wrap(values[1]-origin);increment=wrap(values[1]-last);last=values[1]
            require(increment*pixels<=EPS and delta*pixels<=EPS and abs(delta)<=abs(pixels)*.5,
                    'reversed/extra cumulative normal axis response')
            require(all(same(a,b)for a,b in zip(levels(frame,other),levels(before,other))),
                    'uncommanded other-axis cumulative response')
            actual_gain=delta/pixels
            fresh=frame['monotonic_started']>=event['request_finished'] and all(
                frame[source]['vanilla']['game_tick']>before[source]['vanilla']['game_tick'] for source in('roles','client_roles'))
            ready=fresh and -.5<=actual_gain<=-.02 and all(same(v,values[1])for v in values)
            if ready:
                physical=[]
                for source in('roles','client_roles'):
                    current=geometry(frame[source]['vanilla'],frame[source]['botA'])
                    old=geometry(before[source]['vanilla'],before[source]['botA'])
                    raw=wrap(current[physical_field]-old[physical_field]);physical.append(raw)
                    require(same(raw,delta),'Original viewpoint response differs from acknowledged axis')
                    require(math.dist(current['eye'],old['eye'])<=EPS and math.dist(current['target'],old['target'])<=EPS,
                            'Original shooter/target moved during normal aim')
                signature=(*values,*physical)
                if previous is None or not all(same(x,y)for x,y in zip(signature,previous)):
                    held=(frame['roles']['vanilla']['game_tick'],frame['client_roles']['vanilla']['game_tick'])
                if all(frame[source]['vanilla']['game_tick']-held[i]>=.1 for i,source in enumerate(('roles','client_roles'))):
                    require(now()<deadline,'normal axis acknowledgement deadline exceeded')
                    require(gain is None or same(delta,pixels*gain),'normal aim ACK differs from calibrated axis gain')
                    event['axis_ack']=dict(axis=axis,pixels=pixels,delta_deg=delta,gain_deg_per_pixel=actual_gain,
                        physical_delta_deg_raw=physical,frame=copy.deepcopy(frame),exactly_once_proven=False)
                    return frame,actual_gain
                previous=signature
            else:held=previous=None
            require(now()<deadline,'normal axis acknowledgement deadline exceeded');bounded_sleep(.05)
        raise ValueError('bounded axis acknowledgement clock did not advance')


    def pitches(frame):
        return [geometry(frame[source]['vanilla'],frame[source]['botA'])['pitch']
                for source in ('roles','client_roles')]

    def distance(frame,target):
        values=pitches(frame)
        for value in values:
            require(abs((value-target)-wrap(value-target))<=EPS,
                    'unsupported pitch wrap in actual endpoint geometry')
        return max(abs(value-target) for value in values)

    def request(pixels,before):
        now(2.35)
        act('vanilla','look_vertical',.1,pixels=pixels,
            state_guard=lambda frame:baseline_equal(frame,before))
        event=receipt['actions'][-1]
        frame,unused_gain=acknowledge(event['pre_emission_frame'],'y',pixels,event)
        # The inherited ACK uses wrapped deltas for both axes: pitch additionally
        # requires the exact nonwrapped difference to agree, never yaw-normalize pitch.
        for source in ('roles','client_roles'):
            a=geometry(event['pre_emission_frame'][source]['vanilla'],event['pre_emission_frame'][source]['botA'])['pitch']
            b=geometry(frame[source]['vanilla'],frame[source]['botA'])['pitch']
            require(abs((b-a)-event['axis_ack']['delta_deg'])<=EPS, 'unsupported pitch wrap in native ACK')
        event['status']='ACKED';receipt['actions_acked']+=1
        return frame

    try:
        now();before=settled('pitch-feedback-before')
        initial=pitches(before)
        require(same(initial[0],initial[1]),'initial actual peer pitch geometry differs')
        target=initial[0];receipt['target_pitch_deg']=target
        receipt['initial_frame']=copy.deepcopy(before)
        aim_deadline=now()+20.;receipt['active_deadline']=aim_deadline
        receipt['stage']='aim'
        before=request(12,before);error=distance(before,target)
        receipt['detour_frame']=copy.deepcopy(before)
        require(error>.75,'FEEDBACK_NOT_EXERCISED: initial detour already within return boundary')
        while error>.75:
            previous=error;current=pitches(before)[0]
            pixels=-1 if target-current>0 else 1
            receipt.setdefault('feedback_decisions',[]).append(dict(
                frame=copy.deepcopy(before),target_pitch_deg=target,error_deg=error,pixels=pixels))
            before=request(pixels,before);error=distance(before,target)
            receipt['corrections_acked']+=1
            require(previous-error>EPS,'pitch feedback plateau / no strict actual progress')
        final=settled('pitch-feedback-return');error=distance(final,target)
        require(error<=.75 and receipt['corrections_acked']>0,'actual pitch return not reproduced')
        receipt.update(status='PASS_LIMITED_NATIVE_ACK_PITCH_FEEDBACK_RETURN_ONLY',
            return_error_deg=error,final_frame=copy.deepcopy(final),finished=now())
        return receipt
    except BaseException as error:
        receipt.update(status='FAIL',error=repr(error))
        raise
