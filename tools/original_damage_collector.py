"""Disabled Originaldamage observer, used exclusively inside a fresh worker.

Potentially blocking Frida operations deliberately stay out of the role-owning
parent. close_passive is separately testable without Frida or process access.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import time

RUNTIME_REVIEWED=False
FRIDA_PACKAGE=Path('/srv/tse-frida-probe-20261111/lib/python3.12/site-packages')
READER_SOURCE=Path('/srv/tse-milestone-a-20261111/tools/retail_inventory_readonly.py')


def close_passive(script,session,pin_host,verify_original,check_messages,*,
                  clock=time.monotonic,sleep=time.sleep,idle_seconds=1.):
    """Admission → admitted callbacks idle → hook detach → bytes → unload.

    RPC calls can themselves block. Only a worker calls this function; the
    parent has its independent two-second close/normal-role-cleanup deadline.
    """
    out=dict(closed=False,detached=False,original_bytes_verified=False,
             cleanup_errors=[],packets=[],idle_verified=False)
    def attempt(label,fn):
        try:return True,fn()
        except BaseException as error:
            out['cleanup_errors'].append(label+': '+repr(error));return False,None
    def rpc(name):
        pin_host();return getattr(script.exports_sync,name)()
    attempt('messages before close',check_messages)
    ok,packet=attempt('pre-disarm drain',lambda:rpc('drain'))
    if ok:out['packets'].append(packet)
    attempt('admission disarm',lambda:rpc('disarm'))
    deadline=clock()+idle_seconds
    while clock()<deadline:
        ok,state=attempt('passive idle status',lambda:rpc('status'))
        if not ok:break
        out['last_idle_status']=state
        if (state.get('admission_closed')is True and state.get('idle')is True and
            all(type(state.get(k))is int and state[k]==0 for k in
                ('in_flight','active_records','listener_callbacks','getter_callbacks'))):
            out['idle_verified']=True;break
        sleep(.01)
    if not out['idle_verified']:
        out['cleanup_errors'].append('passive callback idle not proven before worker close deadline')
        return out
    ok,stopped=attempt('idle hook detach',lambda:rpc('finishstop'))
    out['stop_result']=stopped
    if not(ok and stopped.get('stopped')is True and stopped.get('idle')is True and stopped.get('detach_errors')==[]):
        out['cleanup_errors'].append('idle hook detach not proven');return out
    ok,packet=attempt('post-detach drain',lambda:rpc('drain'))
    if ok:out['packets'].append(packet)
    ok,verified=attempt('full Original bytes before unload',lambda:(pin_host(),verify_original())[1])
    out['original_bytes_verified']=ok and verified is True
    if not out['original_bytes_verified']:
        out['cleanup_errors'].append('full Original bytes not proven; unload refused');return out
    # Message/journal failure stays sticky, but cannot skip a now-safe detach.
    unloaded,_=attempt('script unload',lambda:(pin_host(),script.unload())[1])
    detached,_=attempt('session detach',lambda:(pin_host(),session.detach())[1])
    out['detached']=detached;out['closed']=unloaded and detached
    attempt('messages after close',check_messages)
    return out


def local(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


class Collector:
    def __init__(self,config,ownership_gate):
        if not RUNTIME_REVIEWED:raise RuntimeError('disabled damage collector: Root freeze required')
        self.config=config;self.root=Path(config['controller_root']).resolve(strict=True)
        self.registry=json.loads(Path(config['registry_file']).read_text());self.reg=self.registry['host']
        self.owner=ownership_gate;self.owner();self.reader=None;self.script=None;self.session=None
        self.arm_requested=False;self.closed=False;self.close_result=None;self.failed=False;self.journal_errors=[];self.original_receipts=[]
        self.report={};self.frozen=self.root/'frozen-v2'
        self.guard=local('damage_worker_message_guard',self.frozen/'controller_guard.py')
        self.messages=self.guard.MessageGuard(self.report)
        self.host=local('damage_worker_host_binding',self.frozen/'host_binding.py')
        sys.modules['host_binding']=self.host
        self.damage_host=local('damage_worker_damage_host',self.frozen/'damage_host.py')
        self.guards=json.loads((self.frozen/'original_guards.json').read_text())
        self.policy=local('damage_worker_original_policy',self.root/'damage_policy.py')
        manifest=json.loads((self.root/'source-manifest.json').read_text())
        if str(READER_SOURCE)not in manifest['runtime_dependencies']:raise RuntimeError('Original reader outside pinned manifest')
        sys.path.insert(0,str(READER_SOURCE.parent))
        from retail_inventory_readonly import InventoryReader
        import retail_inventory_readonly
        if Path(retail_inventory_readonly.__file__).resolve()!=READER_SOURCE:raise RuntimeError('Original reader import path')
        self.reader=InventoryReader(self.reg['pid'],self.reg['start_ticks'],self.reg['cwd'],self.reg['game_sha256'])
        self.pin_host();self.verify_original('reader-initialization')

    def journal(self,event,**fields):
        try:
            path=Path(self.config['evidence'])/'damage-worker-journal.jsonl'
            with path.open('a')as stream:stream.write(json.dumps(dict(event=event,epoch_ms=time.time()*1000,**fields),allow_nan=False)+'\n')
            path.chmod(0o600)
        except BaseException as error:
            self.failed=True;self.journal_errors.append(repr(error))

    def pin_host(self):
        self.owner();self.damage_host.validate_damage_host(self.reg)
        if (Path('/proc')/str(self.reg['pid'])/'ns/net').stat().st_ino!=self.registry['net_namespace_inode']:
            raise RuntimeError('Original server net namespace changed')

    def verify_original(self,phase='before-unload'):
        self.pin_host()
        receipt=dict(phase=phase,pid=self.reg['pid'],start_ticks=self.reg['start_ticks'],bodies=[])
        for mod,name,key in [('engine','Engine.dll','current_tick'),('entities','EntitiesMP.dll','receive_damage')]:
            module=self.guards[mod];guard=module[key];base=self.reg['modules'][name]['base']
            expected=self.policy.rebased(guard,module['preferred_base'],base,module['image_size'])
            observed=self.reader._read(base+guard['rva'],len(expected))
            receipt['bodies'].append(dict(module=name,rva=guard['rva'],bytes=len(expected),
                expected_sha256=hashlib.sha256(expected).hexdigest(),observed_sha256=hashlib.sha256(observed).hexdigest(),equal=observed==expected))
        receipt['all_equal']=all(row['equal']for row in receipt['bodies'])
        self.original_receipts.append(receipt);self.journal('full-original-body-compare',receipt=receipt)
        if not receipt['all_equal']:raise RuntimeError('full Original body mismatch')
        return True

    def check(self):
        self.pin_host();self.messages.check()
        if self.failed:raise RuntimeError('sticky damage worker journal/operation error')

    def arm(self):
        if self.arm_requested or self.session is not None:raise RuntimeError('one damage arm per worker')
        self.check();self.verify_original('before-attach');self.journal('pre-attach-original-bodies-verified')
        if self.failed:raise RuntimeError('journal failed before attach')
        sys.path.insert(0,str(FRIDA_PACKAGE));import frida
        if (Path(frida.__file__).resolve()!=FRIDA_PACKAGE/'frida/__init__.py' or
            Path(frida._frida.__file__).resolve()!=FRIDA_PACKAGE/'frida/_frida.abi3.so' or frida.__version__!='17.26.2'):
            raise RuntimeError('pinned Frida import/version mismatch')
        self.pin_host();self.session=frida.get_local_device().attach(self.reg['pid']);self.pin_host()
        self.script=self.session.create_script((self.frozen/'damage_readonly.js').read_text())
        self.script.on('message',self.messages.on_message)
        self.pin_host();self.script.load();self.check()
        self.arm_requested=True;self.pin_host();packet=self.script.exports_sync.arm(self.registry['arm']);self.check()
        self.journal('armed',armed=packet.get('armed'),frida_version=frida.__version__)
        if self.failed:raise RuntimeError('journal failed after arm')
        return dict(arm_result=packet,frida_version=frida.__version__,pre_attach_original_bytes_verified=True,
                    message_report=self.report)

    def drain(self):
        self.check()
        if not self.arm_requested:raise RuntimeError('damage worker not armed')
        packet=self.script.exports_sync.drain();self.check();return packet

    def close(self):
        if self.close_result is not None:return self.close_result
        if self.script is not None and self.arm_requested:
            result=close_passive(self.script,self.session,self.pin_host,self.verify_original,self.messages.check)
        else:
            # The reviewed hook has no load-time instrumentation. Before the
            # first arm request no admitted callback exists, even on load error.
            result=dict(closed=False,detached=False,original_bytes_verified=False,
                        idle_verified=False,packets=[],cleanup_errors=[])
            try:
                result['original_bytes_verified']=self.verify_original()
                if self.script is not None:self.pin_host();self.script.unload()
                if self.session is not None:self.pin_host();self.session.detach();result['detached']=True
                result['closed']=True
            except BaseException as error:result['cleanup_errors'].append('unarmed cleanup:'+repr(error))
        self.journal('close',closed=result['closed'],idle_verified=result['idle_verified'],
                     original_bytes_verified=result['original_bytes_verified'],detached=result['detached'])
        result['cleanup_errors'].extend('journal: '+e for e in self.journal_errors)
        result['message_report']=self.report
        result['original_body_receipts']=self.original_receipts
        if self.reader is not None:
            try:self.reader.close()
            except BaseException as error:result['cleanup_errors'].append('Original reader close:'+repr(error))
        self.closed=result['closed'];self.close_result=result;return result
