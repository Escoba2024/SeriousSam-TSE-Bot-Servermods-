"""Normal Original Fire-release primitives for a separate disabled condition.

No runtime action or trace import on import. All clocks/ports are explicit;
there is no default fake port and no input-to-hit inference.
"""
import ast
import copy
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import struct
import stat
import time
from types import SimpleNamespace


def need(ok,message):
    if not ok:raise ValueError('Original respawn method: '+message)


def finite(value):return type(value)in(int,float)and math.isfinite(value)


# Same maximum already enforced by unchanged NAI.private_json. Aggregate
# reservation is deliberately conservative: two old maxima, never unbounded.
OWNERSHIP_RECEIPT_LIMIT=1536*1024
OWNERSHIP_TOTAL_LIMIT=2*OWNERSHIP_RECEIPT_LIMIT


class OwnershipReads:
    """Fresh custody for initial frame and every subsequent roles read.

    No role/proof cache. Callback performs the unchanged actual capture. The
    whole callback and fsync stay inside the existing absolute parent deadline.
    """
    def __init__(self,evidence,clock,deadline):
        need(finite(deadline),'ownership absolute deadline')
        self.evidence=Path(evidence);self.clock=clock;self.deadline=deadline
        self.attempts=[];self.payload_bytes=0;self.failed=False;self.created=False
        self.receipt={'schema':'ORIGINAL_RESPAWN030_FRESH_ROLE_READS_V1',
          'maximum_reads_including_initial':1024,'single_receipt_limit':OWNERSHIP_RECEIPT_LIMIT,
          'aggregate_payload_limit':OWNERSHIP_TOTAL_LIMIT,'absolute_deadline':deadline,
          'attempts':self.attempts,'payload_bytes':0,'failed':False}

    def read(self,capture):
        row=None;primary=None;result=None;path=None;start=None
        try:
            need(not self.failed,'sticky ownership read failure')
            need(len(self.attempts)<1024,'1024 ownership reads including initial')
            need(self.payload_bytes+OWNERSHIP_RECEIPT_LIMIT<=OWNERSHIP_TOTAL_LIMIT,'ownership receipt payload budget')
            start=self.clock();need(finite(start)and start<self.deadline,'ownership read deadline before capture')
            serial=len(self.attempts)+1
            row={'serial':serial,'started':start,'finished':None,'status':'IN_PROGRESS',
                 'receipt':f'respawn-role-reads/{serial:04d}/natural-ai-ownership.json',
                 'capture_invoked':False,'payload_bytes':None,'custody_errors':[]}
            self.attempts.append(row)
            base=self.evidence/'respawn-role-reads'
            if not self.created:base.mkdir(mode=0o700);self.created=True
            directory=base/f'{serial:04d}';directory.mkdir(mode=0o700)
            path=directory/'natural-ai-ownership.json'
            before=self.clock();need(finite(before)and start<=before<self.deadline,'ownership read deadline before callback')
            row['capture_invoked']=True;result=capture(directory)
        except BaseException as error:primary=error
        finally:
            if row is not None and row['capture_invoked']:
                try:
                    # No extra game/source read. Only account the known, newly
                    # created receipt, including when actual validation failed.
                    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as stream:
                        info=os.fstat(stream.fileno())
                        self.payload_bytes+=info.st_size;row['payload_bytes']=info.st_size
                        need(stat.S_ISREG(info.st_mode)and stat.S_IMODE(info.st_mode)==0o600,'private ownership receipt type/mode')
                        need(0<info.st_size<=OWNERSHIP_RECEIPT_LIMIT,'bounded actual ownership receipt')
                        need(self.payload_bytes<=OWNERSHIP_TOTAL_LIMIT,'aggregate ownership receipt payload')
                except BaseException as error:
                    row['custody_errors'].append(repr(error)[:256])
                    if primary is None:primary=error
            if row is not None:
                try:
                    end=self.clock();row['finished']=end if finite(end)else None
                    need(finite(end)and start<=end<self.deadline,'ownership read deadline after capture')
                except BaseException as error:
                    row['custody_errors'].append(repr(error)[:256])
                    if primary is None:primary=error
                row['status']='PASS'if primary is None else'FAIL'
                if primary is not None:row['error']=repr(primary)[:256]
            if primary is not None:self.failed=True
            self.receipt.update(payload_bytes=self.payload_bytes,failed=self.failed)
        if primary is not None:raise primary
        return result


class FireJournal:
    """Bounded metadata before every attempted actual native Down/Up call.

    No file I/O in the input path. Sticky errors block presses, never the required
    release; the inherited fixed program has only two actual native calls.
    """
    def __init__(self,clock):
        self.clock=clock;self.attempts=[];self.failed=False

    def invoke(self,fn,down,*args):
        need(type(down)is bool,'exact Down/Up')
        need(len(self.attempts)<96,'96 native-attempt bound before call')
        need(not down or not self.failed,'sticky journal blocks a new press')
        row={'index':len(self.attempts)+1,'down':down,'reserved':True,'native_invoked':False,
             'started':None,'finished':None,'return':None,'errors':[]}
        self.attempts.append(row);primary=None;result=None
        try:
            try:
                value=self.clock();row['start_clock_raw']=repr(value)
                need(finite(value),'native start clock');row['started']=value
            except BaseException as error:
                row['errors'].append('before native: '+repr(error));self.failed=True
                if down:raise
            row['native_invoked']=True
            try:result=fn(*args);row['return']=int(result)
            except BaseException as error:
                primary=error;row['native_error']=repr(error);raise
            need(result==1,'native XTest return')
        except BaseException as error:
            primary=error;self.failed=True
        finally:
            try:
                value=self.clock();row['finish_clock_raw']=repr(value)
                need(finite(value),'native finish clock');row['finished']=value
                if row['started']is not None:need(row['finished']>=row['started'],'native backwards clock')
            except BaseException as error:
                row['errors'].append('after native: '+repr(error));self.failed=True
                if primary is None:primary=error
        if row['errors']and primary is None:primary=ValueError('; '.join(row['errors']))
        row['accepted']=primary is None
        if primary is not None:raise primary
        return result


def fire_pulse(endpoint,*,clock,sleep,before_press,observe,deadline,receipt):
    """Exactly one requested .1s pulse; actual hold/flush/release may FAIL.

    Port has the existing Endpoint verify/focus/neutral/down/up/released API.
    Up and neutrality are independent cleanup attempts, including partial Down.
    """
    receipt.update(status='IN_PROGRESS',requested_seconds=.1,native_respawn_proven=False,
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
        touched=True;endpoint.down('fire',submit=submit)
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
            for label,callback in [('Up',lambda:endpoint.up('fire')),('neutrality',lambda:endpoint.released('fire'))]:
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
    """Existing normal XTest Button1 path, journaled with independent XSync.

    No different device/API/mapping or additional input. `normal_transport` is
    the inherited X11Transport in production; tests use a C-call-shaped port.
    """
    class FireTransport(normal_transport):
        def __init__(self,*args,journal,**kwargs):
            super().__init__(*args,**kwargs);self.journal=journal
        def event(self,control,down,*,submit=None):
            need(control=='fire'and type(down)is bool,'only original normal Fire')
            self.guard();primary=None;result=None
            native=self.t.XTestFakeButtonEvent
            def fn(*args):return self.journal.invoke(native,down,*args)
            args=(self.d,1,int(down),0)
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
    return FireTransport


def pinned_read(path,pin,maximum=512*1024):
    path=Path(path).resolve(strict=True)
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:
        before=os.fstat(f.fileno());data=f.read(maximum+1);after=os.fstat(f.fileno())
    need(len(data)<=maximum and hashlib.sha256(data).hexdigest()==pin,'pinned source bytes')
    need((before.st_dev,before.st_ino,before.st_size,before.st_atime_ns,before.st_mtime_ns)==
         (after.st_dev,after.st_ino,after.st_size,after.st_atime_ns,after.st_mtime_ns),'stable no-atime Source')
    return data


def context_sources(root):
    """Exact existing passive Context AST, without importing trace-only modules.

    Parent manifest is already entry-pinned by main. This verifies each actual
    copied source against its current nested dependency value, not a fallback.
    """
    root=Path(root).resolve(strict=True)
    mp=root/'source-manifest.json'
    with os.fdopen(os.open(mp,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:
        manifest=json.loads(f.read(512*1024+1))
    pins=manifest['runtime_dependencies']
    def read(rel):
        p=(root/rel).resolve(strict=True);return pinned_read(p,pins[str(p)])
    source=read('native_first_state.py').decode()
    policy_source=read('vendor/observer/observer_policy.py').decode()
    bindings=json.loads(read('vendor/observer/bindings/original-bindings.json'))
    schema=json.loads(read('vendor/observer/event-schema.json'))
    tree=ast.parse(policy_source)
    tree.body=[n for n in tree.body if not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in('SCHEMA','BINDINGS')for t in n.targets))]
    policy_env={'__file__':str(root/'vendor/observer/observer_policy.py'),'SCHEMA':schema,'BINDINGS':bindings}
    exec(compile(tree,str(root/'vendor/observer/observer_policy.py'),'exec'),policy_env)
    names=['NativeBindingError','require','sha','canonical','assert_identity','build_identity','NativeContext']
    original=ast.parse(source)
    nodes=[next(n for n in original.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name==name)for name in names]
    extracted=ast.Module(body=nodes,type_ignores=[])
    env={'Path':Path,'copy':copy,'hashlib':hashlib,'json':json,'math':math,'os':os,'struct':struct,'time':time,
         'observer_policy':lambda:__import__('types').SimpleNamespace(**policy_env)}
    exec(compile(extracted,str(root/'native_first_state.py')+'::exact_passive_AST','exec'),env)
    return {'functions':names,'whole_ast_equal':all(ast.dump(n)==ast.dump(next(x for x in ast.parse(source).body if isinstance(x,(ast.FunctionDef,ast.ClassDef))and x.name==n.name))for n in nodes),
      'regions':sum(len(m['guards'])for m in bindings['modules'].values()),'namespace':env,
      'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'ast_sha256':hashlib.sha256(ast.dump(extracted).encode()).hexdigest()}


def readiness_context(window):
    proof=context_sources(window.api_root)
    nai=importlib.import_module('first_state_natural_ai')
    need(Path(nai.__file__).resolve()==window.api_root.parent/'first_state_natural_ai.py','exact new condition ownership module')
    proof['namespace']['NAI']=nai
    window.record['passive_context_provenance']={k:v for k,v in proof.items()if k!='namespace'}
    def guard():
        for role in('server','vanilla','botA'):window.own_identity(role)
    return proof['namespace']['NativeContext'](window.frame,window.records,window.pins,guard,window.evidence)


def bind_replica(native,frame):
    """Exact existing paired Original read, not a server-only input ACK.

    Pointer/World addresses are process-local and deliberately not equated.
    No clock conversion or interpolation; a replication disagreement is fatal.
    """
    v=native.get('original_replica');s=native.get('roles',{}).get('vanilla');a=frame['actors']['vanilla']
    need(type(v)is dict and type(s)is dict,'actual paired Original replica required')
    need(v.get('present')is True and type(v.get('slot'))is int and v['slot']==0
         and type(s.get('slot'))is int and s['slot']==0,'exact Original global slot0')
    need(v.get('process_identity')==native.get('vanilla_process_identity')==frame['identity']['vanilla'],'Original replica PID/start')
    for field,expected in [('entity_id',a['id']),('spawned_tick',a['spawn_clock']),
                           ('health',a['health']),('last_buttons',a['buttons_now'])]:
        value=v.get(field)
        need(type(value)in(int,float)and finite(value)and value==expected and s.get(field)==expected,
             'Original/server replica '+field)
    return v


def make_window_class(legacy):
    """Reuse exact old 10s/15s/TLS/worker/cleanup loop, never its old PASS label."""
    try:from . import a1_original_respawn_policy as policy
    except ImportError:import a1_original_respawn_policy as policy

    class RespawnWindow(legacy.MethodWindow):
        def __init__(self,*,read_roles,endpoint,journal,context_factory=readiness_context,**kwargs):
            original_periodic=kwargs['periodic']
            super().__init__(**kwargs)
            self.original_periodic=original_periodic;self.periodic=self._periodic
            self.read_roles=read_roles;self.endpoint=endpoint;self.journal=journal
            self.context_factory=context_factory;self.prep_context=None;self.dead_pin=None
            self.preparation_used=False;self.pulse_used=False;self.down_seen=False;self.row_floor=0
            self.record.update(condition=policy.CONDITION,first_valid_state_damage_proven=False,
                               first_processed_state_proven=False,readiness_reads=[],fire_program={})

        def _context(self):return self.context if self.context is not None else self.prep_context

        def _sample(self):
            need(len(self.record['readiness_reads'])<1024,'readiness read budget')
            row={'attempt':len(self.record['readiness_reads'])+1}
            self.record['readiness_reads'].append(row)
            try:
                native=self.read_roles();frame=self._context().input_frame(native)
                row['frame']=copy.deepcopy(frame);row['original_replica']=copy.deepcopy(native.get('original_replica'))
                policy.bound_frame(frame,self.now())
                bind_replica(native,frame)
                return frame
            except BaseException as error:row['error']=repr(error);raise

        def _prepare(self):
            need(not self.preparation_used,'one preparation, no retry');self.preparation_used=True
            self.prep_context=self.context_factory(self)
            self.record['original_regions_before_preparation']=self.prep_context.require_original_regions()
            first=self._sample();need(first['actors']['vanilla']['health']>0 and first['actors']['vanilla']['entity_flags']&8,'actual initial live Original before legal death')
            for unused in range(1024):
                need(self.now()+10<=self.parent_started+85,'preparation consumes immutable parent budget')
                self.original_periodic();frame=self._sample()
                policy.bound_frame(frame,self.now(),first)
                a=frame['actors']['vanilla'];need(a['may_respawn']in(0,1,2)and not a['buttons_now']&1,'unexpected pre-arm readiness/input')
                if a['health']<=0 and a['may_respawn']==2:
                    self.dead_pin=policy.dead_ready(frame,now=self.now(),deadline=self.parent_started+85,expected=first)
                    self.frame=self.read_roles()
                    self.record['pre_arm_death']={'initial':first,'dead_ready':copy.deepcopy(self.dead_pin),
                        'damage_chain_before_arm_left_censored':True,'no_game_state_writes':True}
                    return
                self.sleep(.1)
            raise ValueError('bounded preparation did not reach real DEAD_READY')

        def _before_press(self):
            if self.observer is not None:self.observer.poll();self.row_floor=len(self.observer.core.trace.events)
            frame=self._sample()
            policy.dead_ready(frame,now=self.now(),deadline=self.input_deadline,expected=self.dead_pin)
            self.record['fire_program']['before_press']=copy.deepcopy(frame)

        def _observe_input(self):
            self.original_periodic()
            if self.observer is not None:self.observer.poll()
            frame=self._sample();policy.bound_frame(frame,self.now(),self.dead_pin)
            if frame['actors']['vanilla']['buttons_now']&1:self.down_seen=True

        def _ack(self):
            deadline=min(self.input_deadline,self.now()+2.)
            for unused in range(202):
                need(self.now()<deadline,'2s server Release/respawn ACK timeout')
                self.original_periodic()
                if self.observer is not None:self.observer.poll()
                f=self._sample();v=f['actors']['vanilla'];old=self.dead_pin['actors']['vanilla']
                need(self.now()<deadline,'late server ACK read crossed deadline')
                need(f['identity']==self.dead_pin['identity']and policy.actor_key(f['actors']['botA'])==policy.actor_key(self.dead_pin['actors']['botA']),'ACK domain/shooter life drift')
                need(policy.actor_key(v)[:3]==policy.actor_key(old)[:3],'ACK actor/world replacement')
                if v['health']>0 and v['entity_flags']&8 and not v['buttons_now']&1 and v['spawn_clock']>old['spawn_clock']:
                    need(self.down_seen,'actual server Down was not observed')
                    self.record['fire_program'].update(server_down_observed=True,server_release_respawn_observed=True,
                                                      after_release=copy.deepcopy(f),ack_finished=self.now())
                    return
                self.sleep(min(.01,max(0,deadline-self.now())))
            raise ValueError('bounded ACK observations exhausted')

        def _periodic(self):
            self.original_periodic()
            if self.record.get('phase')!='OBSERVING'or self.pulse_used:return
            self.pulse_used=True
            self.input_deadline=min(self.record['observation_deadline'],self.record.get('absolute_observer_deadline',self.parent_started+85),self.parent_started+85)
            try:
                fire_pulse(self.endpoint,clock=self.now,sleep=self.sleep,before_press=self._before_press,
                           observe=self._observe_input,deadline=self.input_deadline,receipt=self.record['fire_program'])
                self._ack()
            finally:
                self.record['native_attempts']=copy.deepcopy(self.journal.attempts)
                self.record['input_emissions']=sum(x['native_invoked']for x in self.journal.attempts)
                self.save()

        def run(self):
            self._prepare()
            if self.mode=='trace':self.prep_context.close();self.prep_context=None
            super().run()
            need(self.record['input_emissions']==2 and not self.journal.failed,'exact successful Down/Up metadata')

        def finish_before_roles(self):
            primary=None;result=None
            try:
                result=super().finish_before_roles()
                if self.mode=='trace'and self.record.get('observation_complete'):
                    self.record['examples']=policy.complete_chain(self.observer.core.trace.events,
                        cutoff=self.observer.cutoff_sequence,dead_pin=self.dead_pin,row_floor=self.row_floor)
            except BaseException as error:
                primary=error;self.record['condition_error']=repr(error)
            finally:
                if self.prep_context is not None:
                    try:self.record['original_regions_after_control']=self.prep_context.require_original_regions()
                    except BaseException as error:
                        self.record['control_region_error']=repr(error)
                        if primary is None:primary=error
                    finally:self.prep_context.close();self.prep_context=None
                self.record['native_attempts']=copy.deepcopy(self.journal.attempts)
                self.record['input_emissions']=sum(x['native_invoked']for x in self.journal.attempts)
                try:legacy.private_json(self.evidence/'respawn-native-attempts.json',self.record['native_attempts'])
                except BaseException as error:
                    self.record['native_attempt_archive_error']=repr(error)
                    if primary is None:primary=error
                self.save()
            if primary is not None:raise primary
            return result
    return RespawnWindow


def candidate_status(report,window):
    """New condition; inherited completion/cleanup guards are all retained."""
    if window is None:return 'FAIL'
    r=window.record
    if report.get('status')!='CLEANUP_PENDING'or report.get('errors')or not report.get('units_closed_verified'):return 'FAIL'
    cleanup=report.get('cleanup',{})
    if set(cleanup)!={'server','vanilla','botA'}or not all(x.get('closed')is True for x in cleanup.values()):return 'FAIL'
    if report.get('restoration',{}).get('restored')is not True or report.get('post_close_logs',{}).get('accepted')is not True:return 'FAIL'
    if not r.get('observation_complete')or r.get('observed_seconds',0)<10 or r.get('input_emissions')!=2 or not r.get('before_roles_cleanup_complete')or not r.get('after_roles_cleanup_complete'):return 'FAIL'
    if r.get('condition')!='NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_COLT_V1'or r.get('condition_error')or r.get('native_attempt_archive_error'):return 'FAIL'
    attempts=r.get('native_attempts',[])
    if len(attempts)!=2 or[entry.get('down')for entry in attempts]!=[True,False]or any(entry.get('accepted')is not True or entry.get('native_invoked')is not True or entry.get('return')!=1 for entry in attempts):return 'FAIL'
    program=r.get('fire_program',{})
    if program.get('status')!='RELEASED_TRANSPORT_ONLY'or program.get('server_down_observed')is not True or program.get('server_release_respawn_observed')is not True:return 'FAIL'
    if window.mode=='control':
        if r.get('worker_created')or window.proxy is not None:return 'FAIL'
        before=r.get('original_regions_before_preparation',{});after=r.get('original_regions_after_control',{})
        if len(before)!=38 or before!=after:return 'FAIL'
        return 'PASS_LIMITED_NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_CONTROL_ONLY'
    result=r.get('observer_cleanup',{})
    if result.get('schema')!='a1.first-state.autodrain-session.v1':return 'FAIL'
    if any(result.get(k)is not False for k in('qualified','native_qualified','first_processed_state_proven')):return 'FAIL'
    if result.get('status')!='AUTODRAIN_OBSERVER_TRANSPORT_COMPLETE_ONLY'or result.get('errors')!=[]:return 'FAIL'
    if result.get('coverage_complete')is not True:return 'FAIL'
    S=result.get('stop_serial');F=result.get('final_serial')
    if type(S)is not int or type(F)is not int or not 1<=S<=F<=1024:return 'FAIL'
    rows=result.get('packet_receipts',[])
    if len(rows)!=F or type(result.get('validated_packets'))is not int or result['validated_packets']!=F:return 'FAIL'
    if any(type(row.get('serial'))is not int or row['serial']!=i or row.get('accepted')is not True for i,row in enumerate(rows,1)):return 'FAIL'
    ext=result.get('external_restore',{})
    if len(ext.get('regions',{}))!=38 or ext.get('script_unloaded')is not True or ext.get('session_detached')is not True or ext.get('prior_errors')!=[]:return 'FAIL'
    tls=result.get('tls_binding');identity=result.get('identity',{})
    if type(identity.get('pid'))is not int or identity['pid']<=0 or type(tls)is not dict or type(tls.get('thread_id'))is not int or tls['thread_id']!=identity['pid']:return 'FAIL'
    if type(result.get('cutoff_sequence'))is not int or result['cutoff_sequence']<=0:return 'FAIL'
    if result.get('main_tick_pair_before_cutoff')is not True or r.get('worker_reap',{}).get('reaped')is not True:return 'FAIL'
    examples=r.get('examples',{})
    if examples.get('status')!='LIMITED_BOUND_ORIGINAL_RESPAWN_COLT_EXAMPLES_ONLY'or examples.get('first_valid_state_damage_proven')is not False:return 'FAIL'
    r['observed_callback_kinds']=list(result.get('observed_callback_kinds_before_cutoff',[]))
    return 'PASS_LIMITED_NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_BOUND_EXAMPLES_ONLY'


def bind(legacy):
    return SimpleNamespace(MethodWindow=make_window_class(legacy),candidate_status=candidate_status)


def publish_attempts(report,window):
    attempts=[]if window is None else window.journal.attempts
    report['native_input_attempts']=copy.deepcopy(attempts)
    report['input_emissions']=sum(x.get('native_invoked')is True for x in attempts)
    report['normal_route_or_fire']=any(x.get('native_invoked')is True and x.get('down')is True for x in attempts)
    program={}if window is None else window.record.get('fire_program',{})
    report['completed_input_program']=(program.get('status')=='RELEASED_TRANSPORT_ONLY'
        and program.get('server_down_observed')is True and program.get('server_release_respawn_observed')is True)

