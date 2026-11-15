"""Disabled-runner helper for an input-free two-Original method comparison.

Control imports only standard library. Trace imports the pinned private method
API lazily; all actual Frida operations remain in its FreshExec worker.
"""
import importlib
import json
import math
import os
from pathlib import Path
import sys
import time

ROLES=('server','vanilla','botA')
ACTIVE_SECONDS=10
INNER_SECONDS=85
OUTER_SECONDS=90


def require(condition,message):
    if not condition:raise RuntimeError(message)


def no_trace_imports():
    require(not any(n=='frida'or n.startswith('frida.')or n in('first_state_method_transport','original_damage_worker','a1_input_worker','a1_passive_xrecord_worker','a1_xres_attribution_worker')for n in sys.modules),'control must not import Frida/worker')


def load_trace_api(root):
    root=Path(root).resolve(strict=True)
    sys.path.insert(0,str(root))
    names=('native_first_state','first_state_method_transport','observer_session')
    for name in names:require(name not in sys.modules,'unexpected previous method module:'+name)
    modules=tuple(importlib.import_module(name)for name in names)
    for name,module in zip(names,modules):require(Path(module.__file__).resolve()==root/(name+'.py'),'method module path differs:'+name)
    return modules


def private_json(path,value):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w')as stream:json.dump(value,stream,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())


def worker_config(window,identity,deadline):
    roles={}
    for role in ROLES:
        window.own_identity(role)
        record=window.records[role]
        roles[role]={'identity':list(record['identity']),'unit':window.unit(role),
                     'net_namespace_inode':(Path('/proc')/str(record['identity'][0])/'ns/net').stat().st_ino}
    lock=(window.arena/'runtime.lock').stat()
    return {'controller_root':str(window.api_root),'arena':str(window.arena),'evidence':str(window.evidence),
            'parent':{'pid':os.getpid(),'start_ticks':int((Path('/proc/self/stat')).read_text().rsplit(') ',1)[1].split()[19]),'lock_file':[lock.st_dev,lock.st_ino]},
            'roles':roles,'frame':window.frame,'pins':window.pins,'expected_identity':identity,'observer_deadline':deadline}


class MethodWindow:
    def __init__(self,*,mode,api_root,arena,evidence,parent_started,frame,records,pins,own_identity,unit,periodic,save,record,clock=time.monotonic,sleep=time.sleep):
        if mode not in('control','trace'):raise ValueError('one declared control|trace arm')
        self.mode=mode;self.api_root=Path(api_root);self.arena=Path(arena);self.evidence=Path(evidence)
        self.parent_started=parent_started;self.frame=frame;self.records=records;self.pins=pins;self.own_identity=own_identity;self.unit=unit
        self.periodic=periodic;self.save=save;self.record=record;self.clock=clock;self.sleep=sleep
        self.context=None;self.proxy=None;self.ports=None;self.observer=None;self.last_clock=-float('inf');self.used=False;self.closed=False;self.reaped=False
        self.record.update(mode=mode,qualified=False,native_qualified=False,first_processed_state_proven=False,input_emissions=0,worker_created=False,observed_callback_kinds=[])
    def now(self):
        value=self.clock();require(type(value)in(int,float)and math.isfinite(value)and value>=self.last_clock,'method monotonic clock')
        self.last_clock=value;return value
    def run(self):
        require(not self.used,'one method arm; no retry');self.used=True
        require(set(self.records)==set(ROLES),'exact three own Original roles')
        require(self.now()+ACTIVE_SECONDS<=self.parent_started+INNER_SECONDS,'remaining parent budget cannot contain10s')
        self.record['phase']='STARTING';self.save()
        if self.mode=='control':
            no_trace_imports();deadline=self.parent_started+INNER_SECONDS
        else:
            nat,transport,session=load_trace_api(self.api_root)
            def guard():
                for role in ROLES:self.own_identity(role)
            self.context=nat.NativeContext(self.frame,self.records,self.pins,guard,self.evidence)
            self.record['original_regions_before']=self.context.require_original_regions()
            arm_now=self.now();deadline=min(self.parent_started+INNER_SECONDS,arm_now+15)
            cfg={**self.context.expected,'max_records':64,'max_damage_calls':1024,'max_order_calls':8192,'max_events':16384,'ttl_ms':15000,'binding_ms':2000,'binding_calls':256}
            require(self.now()+ACTIVE_SECONDS<=deadline,'context costs exhausted immutable observation budget; no worker/arm')
            private_json(self.evidence/'first-state-worker-config.json',worker_config(self,self.context.expected,deadline))
            self.proxy=transport.WorkerProxy.start(self.evidence/'first-state-worker-config.json',transport.WireArchive(self.evidence))
            self.record['worker_created']=True
            self.ports=transport.LegacyWorkerPorts(self.context,self.evidence,self.proxy)
            self.observer=session.ObserverSession(self.context.expected,cfg,self.ports,deadline=deadline)
            require(self.now()+ACTIVE_SECONDS<=deadline,'worker setup exhausted immutable observation budget; no arm')
            self.observer.start()
            binding_deadline=min(deadline,self.now()+2)
            for unused in range(101):
                require(self.now()<binding_deadline,'unchanged2s TLS binding deadline')
                packet=self.observer.poll()
                if packet['tls_bound']:break
                self.sleep(min(.02,max(0,binding_deadline-self.now())))
            else:raise RuntimeError('bounded TLS binding attempts exhausted')
            self.record.update(observer_config=cfg,absolute_observer_deadline=deadline)
        began=self.now();require(began+ACTIVE_SECONDS<=deadline,'remaining observer budget cannot contain10s')
        self.record.update(phase='OBSERVING',observation_started=began,observation_deadline=began+ACTIVE_SECONDS);self.save()
        for unused in range(502):
            current=self.now();require(current<=deadline and current<=self.parent_started+INNER_SECONDS,'method observation deadline')
            if current-began>=ACTIVE_SECONDS:break
            self.periodic()  # unchanged owned host/query/paired inventory guards
            if self.observer is not None:self.observer.poll()
            remaining=began+ACTIVE_SECONDS-self.now()
            if remaining>0:self.sleep(min(.02,remaining))
        else:raise RuntimeError('method observation clock failed to advance')
        if self.observer is not None:self.observer.mark_cutoff()
        else:no_trace_imports()
        ended=self.now();require(ended<=deadline and ended<=self.parent_started+INNER_SECONDS,'observation finished outside immutable deadline')
        self.record.update(phase='OBSERVED',observation_finished=ended,observed_seconds=ended-began,observation_complete=True);self.save()
    def finish_before_roles(self):
        require(not self.closed,'method close exactly once');self.closed=True
        try:
            if self.observer is not None:
                self.record['observer_cleanup']=self.observer.finish()
                require(self.record['observer_cleanup']['status']=='OBSERVER_TRANSPORT_COMPLETE_ONLY','strict observer cleanup/validator failed')
            elif self.mode=='control':no_trace_imports()
            self.record['before_roles_cleanup_complete']=True
        finally:
            if self.context is not None:self.context.close()
            self.save()
        return self.record
    def finish_after_roles_closed(self,*,roles_closed):
        require(roles_closed is True,'all three own roles/units must be normally closed before reap')
        require(self.closed,'observer cleanup must precede normal role cleanup/reap')
        if self.proxy is not None:self.record['worker_reap']=self.proxy.finish_after_roles_closed(roles_closed=True)
        self.reaped=True;self.record['after_roles_cleanup_complete']=True;self.save()
        return self.record.get('worker_reap')


def candidate_status(report,window):
    """Own evidence predicate; generic trial acceptance cannot repair this FAIL."""
    if window is None:return 'FAIL'
    r=window.record
    if report.get('status')!='CLEANUP_PENDING'or report.get('errors')or not report.get('units_closed_verified'):return 'FAIL'
    cleanup=report.get('cleanup',{})
    if set(cleanup)!=set(ROLES)or not all(x.get('closed')is True for x in cleanup.values()):return 'FAIL'
    if report.get('restoration',{}).get('restored')is not True or report.get('post_close_logs',{}).get('accepted')is not True:return 'FAIL'
    if not r.get('observation_complete')or r.get('observed_seconds',0)<10 or r.get('input_emissions')!=0 or not r.get('before_roles_cleanup_complete')or not r.get('after_roles_cleanup_complete'):return 'FAIL'
    if window.mode=='control':
        if r.get('worker_created')or window.proxy is not None:return 'FAIL'
        return 'PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY'
    result=r.get('observer_cleanup',{})
    if result.get('status')!='OBSERVER_TRANSPORT_COMPLETE_ONLY'or result.get('errors'):return 'FAIL'
    ext=result.get('external_restore',{})
    if len(ext.get('regions',{}))!=38 or ext.get('script_unloaded')is not True or ext.get('session_detached')is not True or ext.get('prior_errors'):return 'FAIL'
    packets=result.get('packets',[])
    if not packets or not packets[-1].get('tls_binding'):return 'FAIL'
    if packets[-1]['tls_binding'].get('thread_id')!=packets[-1].get('identity',{}).get('pid'):return 'FAIL'
    events=[e for p in packets for e in p.get('events',[])]
    pid=packets[-1]['identity']['pid']
    ticks=[e for e in events if e.get('kind')=='process_game_tick'and e.get('thread_id')==pid and e.get('data',{}).get('scope')=='context']
    enters={e['call_id']for e in ticks if e.get('edge')=='enter'}
    leaves={e['call_id']for e in ticks if e.get('edge')=='leave'}
    if not enters.intersection(leaves)or r.get('worker_reap',{}).get('reaped')is not True:return 'FAIL'
    r['observed_callback_kinds']=sorted({e['kind']for e in events})
    return 'PASS_LIMITED_FIRST_STATE_METHOD_OBSERVED_CALLBACKS_ONLY'
