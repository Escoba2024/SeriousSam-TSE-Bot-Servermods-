"""ONE normal Original W pulse; server motion is not an exact ActionACK.

Pure rules import no native libraries. Runtime ports are bound explicitly in the
separate disabled builder. Old calibration/respawn sources are never mutated.
"""
import copy
import math
try:from . import a1_original_respawn_policy as P
except ImportError:import a1_original_respawn_policy as P

CONDITION='ORIGINAL_FORWARD_TRANSLATION_V1'
EPS=.001  # unchanged RD/CP numeric observation consistency, not a route margin
MAX_READS=16
OWNERSHIP_BYTES=24*1024**2
DISK_MINIMUM=8*1024**3+216*1024**2
MEMORY_MINIMUM=(1536+128)*1024**2


def need(ok,why):P.need(ok,'forward: '+why)
def vector(v,n):
    need(type(v)in(list,tuple)and len(v)==n and all(P.number(x)for x in v),'finite native vector')
    return list(v)


class Frames:
    def __init__(self):self.rows=[];self.ticks={};self.keys={};self.index=-1
    def accept(self,entry,now):
        need(len(self.rows)<MAX_READS,'16 fresh role-read bound')
        n,f=entry['native'],entry['context'];P.bound_frame(f,now,self.rows[0]['context']if self.rows else None)
        need(n['server_process_identity']==f['identity']['server']and n['vanilla_process_identity']==f['identity']['vanilla'],'actual peer identities')
        need(n['monotonic_started']==f['started']and n['monotonic_finished']<=f['finished'],'actual read envelope')
        seq=n['successful_read_sequence']['index'];need(type(seq)is int and seq>self.index,'advancing real successful pair')
        for label,row in [('server',n['roles']['vanilla']),('replica',n['original_replica'])]:
            a=f['actors']['vanilla']
            need(row['present']is True and type(row['slot'])is int and row['slot']==0,'actual Original slot0')
            need(type(row['entity_id'])is int and row['entity_id']==a['id']and row['spawned_tick']==a['spawn_clock']and row['health']==a['health']and row['last_buttons']==a['buttons_now'],'same actor state')
            if label=='server':need(row['entity_pointer']==int(a['pointer'],16)and row['world_pointer']==int(a['world'],16),'actual server actor/world')
            else:need(row['process_identity']==f['identity']['vanilla'],'replica process')
            key=(row['slot'],row['entity_id'],row['entity_pointer'],row['world_pointer'],row['spawned_tick'])
            need(key==self.keys.get(label,key),'peer Actor/World/Life changed')
            tick=row['game_tick'];need(P.number(tick)and tick>=0 and tick>=self.ticks.get(label,tick),'native clock reversed')
            vector(row['placement'],6);vector(row['current_translation_absolute'],3)
            need(a['health']>0 and a['entity_flags']&8 and a['may_respawn']==0 and not a['buttons_now']&1,'live neutral Original')
            need(type(row['support_pointer'])is int and row['support_pointer']>=0,'actual support scalar')
            self.keys[label]=key;self.ticks[label]=tick
        self.index=seq;out=copy.deepcopy(entry);self.rows.append(out);return out
    def admit(self,first,before,now,deadline):
        need(P.number(now)and P.number(deadline)and deadline-now>=2.35,'2.35s reserve')
        for label in ('server','replica'):
            a=self.row(first,label);b=self.row(before,label)
            need(b['game_tick']>a['game_tick'],'progressive baseline native tick')
            need(b['support_pointer']>0 and math.dist(b['current_translation_absolute'],[0,0,0])<=.2,'supported stationary baseline')
            need(math.dist(a['placement'][:3],b['placement'][:3])<=EPS,'baseline position drift')
            need(abs(b['rotation_diagnostic']['relative_view_yaw_deg'])<=EPS,'neutral body-relative view')
        return before
    @staticmethod
    def row(entry,label):return entry['native']['roles']['vanilla']if label=='server'else entry['native']['original_replica']
    def outcome(self,before,after,*,request_finished,release_finished,now,deadline):
        need(all(P.number(x)for x in(request_finished,release_finished,now,deadline))and request_finished<=release_finished<=now and now<deadline<=request_finished+2.,'ACK deadline')
        if after['context']['started']<release_finished:return None
        deltas={}
        for label in('server','replica'):
            a,b=self.row(before,label),self.row(after,label)
            if b['game_tick']<=a['game_tick']:return None
            d=[y-x for x,y in zip(a['placement'][:3],b['placement'][:3])];deltas[label]=d
            # Vertical settling alone never qualifies horizontal movement.
            if math.hypot(d[0],d[2])<=EPS:return None
        if sum(deltas['server'][i]*deltas['replica'][i]for i in(0,2))<=0:return None
        return dict(status='SERVER_OBSERVED_TRANSLATION_ONLY',server_displacement=deltas['server'],original_replica_displacement=deltas['replica'],
          server_current_translation=list(self.row(after,'server')['current_translation_absolute']),original_current_translation=list(self.row(after,'replica')['current_translation_absolute']),
          exact_action_ack_proven=False,direction_calibrated=False,input_once_proven=False,clock_domains_fused=False)


# Exact parent body derivations; transformations proved by the builder/tests.
finite=P.number

def forward_pulse(endpoint,*,clock,sleep,before_press,observe,deadline,receipt):
    """Exactly one requested .1s pulse; actual hold/flush/release may FAIL.

    Port has the existing Endpoint verify/focus/neutral/down/up/released API.
    Up and neutrality are independent cleanup attempts, including partial Down.
    """
    receipt.update(status='IN_PROGRESS',requested_seconds=.1,exact_action_ack_proven=False,
                   preparation_started=None,started=None,held_seconds=None,
                   input_to_release_seconds=None,held_observations=0,errors=[])
    last=None;start=None;touched=False;primary=None
    def now():
        nonlocal last
        value=clock();need(finite(value)and(last is None or value>=last),'monotonic input clock')
        last=value;return value
    def bound(label):
        value=now();need(value<deadline,label+' deadline')
        if start is not None:need(value-start<=.35,label+' host overrun')
        return value
    try:
        receipt['preparation_started']=now()
        need(finite(deadline)and deadline-last>=2.35,'2.35s input reserve')
        endpoint.verify();endpoint.check_focus();endpoint.neutral({'fire','forward','backward','left','right','knife','colt'})
        def submit(fn,*args):
            nonlocal start
            before_press()
            value=now();need(deadline-value>=2.35,'final 2.35s input reserve')
            start=value;receipt['started']=value
            try:return fn(*args)
            finally:
                try:receipt['down_finished']=now()
                except BaseException as error:receipt['errors'].append('Down clock: '+repr(error))
        touched=True;endpoint.down('forward',submit=submit)
        need(start is not None,'actual normal transport must invoke submit')
        for unused in range(102):
            value=bound('held')
            if value-start>=.1:break
            endpoint.verify();endpoint.check_focus();value=bound('held guards')
            if value-start>=.1:break
            receipt['held_observations']+=1;observe();value=bound('held observation')
            if value-start>=.1:break
            sleep(min(.02,.1-(value-start)))
        else:raise ValueError('input clock failed to advance')
    except BaseException as error:primary=error;receipt['errors'].append(repr(error))
    finally:
        try:
            receipt['release_started']=now()
            if start is not None:receipt['held_seconds']=last-start
        except BaseException as error:
            receipt['errors'].append('release start: '+repr(error))
            if primary is None:primary=error
        if touched:
            for label,callback in [('Up',lambda:endpoint.up('forward')),('neutrality',lambda:endpoint.released('forward'))]:
                try:callback()
                except BaseException as error:
                    receipt['errors'].append(label+': '+repr(error))
                    if primary is None:primary=error
        try:
            receipt['finished']=now();need(last<deadline,'release deadline')
            if start is not None:
                receipt['input_to_release_seconds']=last-start
                need(last-start<=.35,'input through release host overrun')
        except BaseException as error:
            receipt['errors'].append('release finish: '+repr(error))
            if primary is None:primary=error
        receipt['status']='FAIL'if primary is not None or receipt['errors']else'RELEASED_TRANSPORT_ONLY'
    if primary is not None:raise primary
    need(not receipt['errors'],'sticky input metadata errors')
    return receipt


def make_transport_class(normal_transport):
    """Existing normal XTest W Key path, journaled with independent XSync.

    No different device/API/mapping or additional input. `normal_transport` is
    the inherited X11Transport in production; tests use a C-call-shaped port.
    """
    class ForwardTransport(normal_transport):
        def __init__(self,*args,journal,**kwargs):
            super().__init__(*args,**kwargs);self.journal=journal
        def event(self,control,down,*,submit=None):
            need(control=='forward'and type(down)is bool,'only original normal W')
            self.guard();primary=None;result=None
            native=self.t.XTestFakeKeyEvent
            def fn(*args):return self.journal.invoke(native,down,*args)
            args=(self.d,self.keys['forward'],int(down),0)
            try:result=submit(fn,*args)if down and submit is not None else fn(*args)
            except BaseException as error:primary=error
            finally:
                try:self.x.XSync(self.d,0)
                except BaseException as error:
                    self.journal.failed=True
                    if primary is None:primary=error
                    elif hasattr(primary,'add_note'):primary.add_note('release/input XSync failure: '+repr(error))
            if primary is not None:raise primary
            return result
    return ForwardTransport



def ownership_reads(rp,evidence,clock,deadline):
    """Keep actual old O_EXCL capture/accounting; stricter new attempt bound."""
    class Reads(rp.OwnershipReads):
        def read(self,capture):
            try:
                need(len(self.attempts)<MAX_READS,'16 ownership attempts including initial')
                need(self.payload_bytes+rp.OWNERSHIP_RECEIPT_LIMIT<=OWNERSHIP_BYTES,'24MiB ownership reserve')
                return super().read(capture)
            except BaseException:
                self.failed=True;self.receipt['failed']=True;raise
    result=Reads(evidence,clock,deadline)
    result.receipt.update(maximum_reads_including_initial=MAX_READS,new_condition_payload_limit=OWNERSHIP_BYTES)
    return result


def bind(legacy,rp):
    """No worker/trace path: reuse ordinary control class and passive Context."""
    from types import SimpleNamespace
    class ForwardWindow(legacy.MethodWindow):
        def __init__(self,*,read_roles,endpoint,journal,context_factory=rp.readiness_context,**kwargs):
            super().__init__(**kwargs)
            self.read_roles=read_roles;self.endpoint=endpoint;self.journal=journal;self.context_factory=context_factory
            self.frames=Frames()
            self.record.update(measurement_scope=CONDITION,condition=CONDITION,read_attempts=[{'index':0,'status':'INITIAL_CONTEXT_CUSTODY_ONLY','native':self.frame}],forward_program={},outcome=None,
              exact_action_ack_proven=False,direction_calibrated=False,damage_proven=False,first_valid_state_damage_proven=False)
        def checked_now(self):
            value=self.now();need(value<self.parent_started+85,'85s absolute deadline');return value
        def sample(self):
            need(len(self.record['read_attempts'])<MAX_READS,'16 role-read attempts including initial')
            row={'index':len(self.record['read_attempts']),'status':'IN_PROGRESS'};self.record['read_attempts'].append(row)
            try:
                self.checked_now()
                self.periodic();native=self.read_roles()
                row['native']=native
                context=self.context.input_frame(native);row['context']=context
                rp.bind_replica(native,context)
                result=self.frames.accept(row,self.checked_now());row['status']='OBSERVED';return result
            except BaseException as error:row.update(status='FAIL',error=repr(error));raise
        def run(self):
            need(self.mode=='control','forward control only; trace forbidden')
            need(not self.used,'one forward program, no retry');self.used=True;legacy.no_trace_imports()
            self.record['phase']='STARTING';self.context=self.context_factory(self)
            self.record['original_regions_before']=self.context.require_original_regions()
            need(len(self.record['original_regions_before'])==38,'38 actual Original regions')
            initial=self.sample();before=self.sample();deadline=self.parent_started+85
            self.frames.admit(initial,before,self.checked_now(),deadline)
            def prepress():
                nonlocal before
                current=self.sample();self.frames.admit(before,current,self.checked_now(),deadline);before=current
                self.record['before_press']=copy.deepcopy(current)
            self.record['phase']='INPUT'
            try:
                forward_pulse(self.endpoint,clock=self.checked_now,sleep=self.sleep,before_press=prepress,
                  observe=self.sample,deadline=deadline,receipt=self.record['forward_program'])
                program=self.record['forward_program'];end=program['down_finished']+2.
                for unused in range(MAX_READS):
                    need(self.checked_now()<end,'2s ACK deadline before read')
                    after=self.sample()
                    outcome=self.frames.outcome(before,after,request_finished=program['down_finished'],release_finished=program['finished'],now=self.checked_now(),deadline=min(end,deadline))
                    if outcome is not None:
                        self.record.update(outcome=outcome,after_input=copy.deepcopy(after),observation_complete=True,phase='OBSERVED')
                        return
                    self.sleep(.05)
                raise ValueError('forward observation budget exhausted')
            finally:
                self.record['keymap_proofs']=copy.deepcopy(getattr(self.journal,'keymaps',[]))
                self.record['native_attempts']=copy.deepcopy(self.journal.attempts)
                self.record['input_emissions']=sum(x.get('native_invoked')is True for x in self.journal.attempts)
                self.save()
        def finish_before_roles(self):
            need(not self.closed,'control close exactly once');self.closed=True
            try:
                legacy.no_trace_imports()
                if self.context is not None:
                    self.record['original_regions_after']=self.context.require_original_regions()
                    need(self.record['original_regions_before']==self.record['original_regions_after'],'Original bytes changed')
                self.record['before_roles_cleanup_complete']=True
            finally:
                if self.context is not None:self.context.close()
                self.record['keymap_proofs']=copy.deepcopy(getattr(self.journal,'keymaps',[]))
                self.record['native_attempts']=copy.deepcopy(self.journal.attempts)
                self.record['input_emissions']=sum(x.get('native_invoked')is True for x in self.journal.attempts)
                try:legacy.private_json(self.evidence/'forward-native-attempts.json',self.record['native_attempts'])
                finally:self.save()
    def candidate_status(report,window):
        if window is None:return 'FAIL'
        r=window.record
        if report.get('status')!='CLEANUP_PENDING'or report.get('errors')or not report.get('units_closed_verified'):return 'FAIL'
        if set(report.get('cleanup',{}))!=set(legacy.ROLES)or not all(x.get('closed')is True for x in report['cleanup'].values()):return 'FAIL'
        if report.get('restoration',{}).get('restored')is not True or report.get('post_close_logs',{}).get('accepted')is not True:return 'FAIL'
        if window.mode!='control'or window.proxy is not None or r.get('worker_created')is not False:return 'FAIL'
        if not all(r.get(k)is True for k in('observation_complete','before_roles_cleanup_complete','after_roles_cleanup_complete')):return 'FAIL'
        if not r.get('outcome')or r['outcome'].get('status')!='SERVER_OBSERVED_TRANSLATION_ONLY':return 'FAIL'
        attempts=window.journal.attempts
        if window.journal.failed or len(attempts)!=2 or[x.get('down')for x in attempts]!=[True,False]or any(x.get('native_invoked')is not True or x.get('accepted')is not True or x.get('return')!=1 for x in attempts):return 'FAIL'
        if r.get('forward_program',{}).get('status')!='RELEASED_TRANSPORT_ONLY':return 'FAIL'
        proofs=r.get('keymap_proofs',[])
        if not proofs or sum(p.get('down')is True for p in proofs)!=1 or proofs[-1].get('down')is not False or any(p.get('accepted')is not True for p in proofs):return 'FAIL'
        before=r.get('original_regions_before',{});after=r.get('original_regions_after',{})
        if len(before)!=38 or before!=after:return 'FAIL'
        return 'PASS_LIMITED_NORMAL_ORIGINAL_FORWARD_SERVER_TRANSLATION_ONLY'
    return SimpleNamespace(MethodWindow=ForwardWindow,candidate_status=candidate_status)


def publish_attempts(report,window):
    attempts=[]if window is None else window.journal.attempts
    report['native_input_attempts']=copy.deepcopy(attempts)
    report['input_emissions']=sum(x.get('native_invoked')is True for x in attempts)
    report['normal_route_or_fire']=any(x.get('native_invoked')is True and x.get('down')is True for x in attempts)
    report['completed_input_program']=bool(window and window.record.get('outcome')and not window.journal.failed)


def make_endpoint_class(normal_endpoint):
    class ForwardEndpoint(normal_endpoint):
        def keymap(self,down):
            t=self.transport;j=t.journal
            if not hasattr(j,'keymaps'):j.keymaps=[]
            need(len(j.keymaps)<32,'bounded actual keymap proofs')
            row={'down':down,'bitmap_hex':None,'keycode':t.keys['forward'],'accepted':False};j.keymaps.append(row)
            try:
                t.guard();bitmap=(t.c.c_char*32)()
                need(t.x.XQueryKeymap(t.d,bitmap)==1,'actual XQueryKeymap return')
                value=bytes(bitmap);row['bitmap_hex']=value.hex();expected=bytearray(32)
                if down:expected[row['keycode']//8]|=1<<(row['keycode']%8)
                need(value==bytes(expected),'exact W-only/neutral keyboard bitmap');row['accepted']=True
            except BaseException as error:row['error']=repr(error);j.failed=True;raise
        def down(self,c,*,submit=None):
            need(c=='forward','only one normal W control')
            result=super().down(c,submit=submit);self.keymap(True);return result
        def up(self,c):
            need(c=='forward','only normal W release');return super().up(c)
        def released(self,c):
            result=super().released(c)
            if c=='forward':self.keymap(False)
            return result
    return ForwardEndpoint


def volume_budget(sample,ram_mode,ram_free=None):
    need(ram_mode is False and ram_free is None,'persistent evidence only, no RAM condition')
    for k in('disk_free_bytes','mem_available_bytes'):need(type(sample.get(k))is int,'actual typed volume counters')
    need(sample['disk_free_bytes']>=DISK_MINIMUM,'8GiB +216MiB persistent reserve')
    need(sample['mem_available_bytes']>=MEMORY_MINIMUM,'1.5GiB +128MiB memory reserve')
    return dict(mode='persistent_forward_only',minimum_disk_bytes=DISK_MINIMUM,minimum_memory_bytes=MEMORY_MINIMUM,
      ownership_bytes=OWNERSHIP_BYTES,raw_journal_bytes=64*1024**2,case_bytes=64*1024**2,safety_bytes=64*1024**2)


def select_case_base(base,ram_base):
    import os
    from pathlib import Path
    need(ram_base is None,'RAM option forbidden in forward condition')
    p=Path('/proc/meminfo').resolve(strict=True)
    with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:b=f.read(65537)
    need(len(b)<=65536,'bounded MemAvailable')
    lines=[line.split()for line in b.decode('ascii').splitlines()if line.startswith('MemAvailable:')]
    need(len(lines)==1 and len(lines[0])==3 and lines[0][2]=='kB'and lines[0][1].isdigit(),'actual MemAvailable shape')
    disk=os.statvfs(base)
    return Path(base),volume_budget(dict(disk_free_bytes=disk.f_bavail*disk.f_frsize,mem_available_bytes=int(lines[0][1])*1024),False)


class JournalBudget:
    def __init__(self):self.used=0
    def reserve(self,data):
        need(type(data)is str,'journal text')
        size=len(data.encode('utf8'));need(self.used+size<=64*1024**2,'64MiB raw journal cap')
        self.used+=size


def open_journal(path,budget):
    import os
    class Stream:
        def __init__(self):self.stream=os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')
        def write(self,data):budget.reserve(data);return self.stream.write(data)
        def flush(self):return self.stream.flush()
        def close(self):return self.stream.close()
    return Stream()


def save_report(path,report):
    import json
    data=json.dumps(report,indent=2,allow_nan=False)
    need(len(data.encode('utf8'))<=64*1024**2,'64MiB result cap')
    path.write_text(data)


def require_case_budget(evidence):
    import os,stat
    total=0;count=0
    for directory,dirs,files in os.walk(evidence,followlinks=False):
        for name in dirs:need(not os.path.islink(os.path.join(directory,name)),'no evidence directory aliases')
        for name in files:
            info=os.lstat(os.path.join(directory,name));need(stat.S_ISREG(info.st_mode),'regular own evidence')
            count+=1;total+=info.st_size;need(count<=4096 and total<=(24+64+64)*1024**2,'152MiB total case cap')
    return {'files':count,'bytes_before_final_status':total,'limit_bytes':152*1024**2}
