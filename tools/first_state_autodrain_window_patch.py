"""Exact reversible monitor-parent retarget for the disabled batch method API."""
import hashlib
from pathlib import Path

PARENT = Path('/srv/tse-a1-first-state-method-monitor-disabled-20261115')
HELPER_SHA = '62b368a3118998a0c95808c4052c91f7a94cc6df647fa652af5eb429ad386dbb'
RUNNER_SHA = '171ec899b243309cf6fbd05efb4bbf528d3f6a7ea58081a38609d9d9a271b171'


def require(value, message):
    if not value: raise ValueError(message)


def sha(text): return hashlib.sha256(text.encode()).hexdigest()


def parent(name, digest):
    source = (PARENT/name).read_text(); require(sha(source) == digest, 'immutable parent source changed')
    return source


def replace(source, old, new):
    require(source.count(old) == 1, 'exact one intended source delta')
    return source.replace(old, new, 1)


NEW_IMPORT_GUARD = '''    forbidden=('first_state_method_transport','original_damage_worker','a1_input_worker',
        'a1_passive_xrecord_worker','a1_xres_attribution_worker','native_first_state',
        'observer_session','first_state_autodrain_worker','first_state_autodrain_protocol',
        'first_state_autodrain_session','frozen_first_state_native','source_loader',
        'a1_frozen_observer_policy')
    require(not any('frida'in n.split('.')or n.rsplit('.',1)[-1]in forbidden for n in sys.modules),'control must not import Frida/worker')'''

NEW_LOADER = '''def load_trace_api(root):
    root=Path(root).resolve(strict=True)
    sys.path.insert(0,str(root))
    names=('native_first_state','first_state_autodrain_worker','first_state_autodrain_session')
    indirect=('first_state_method_transport','original_damage_worker','first_state_autodrain_protocol','observer_session','source_loader')
    for name in names+indirect:require(not any(n.rsplit('.',1)[-1]==name for n in sys.modules),'unexpected previous method module:'+name)
    modules=tuple(importlib.import_module(name)for name in names)
    for name in names+indirect[:3]:require(Path(sys.modules[name].__file__).resolve()==root/(name+'.py'),'method module path differs:'+name)
    return modules
'''

NEW_TRACE_PREDICATE = '''    result=r.get('observer_cleanup',{})
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
    r['observed_callback_kinds']=list(result.get('observed_callback_kinds_before_cutoff',[]))
    return 'PASS_LIMITED_FIRST_STATE_METHOD_OBSERVED_CALLBACKS_ONLY'
'''


def helper_pairs():
    original = parent('first_state_inputfree_method.py', HELPER_SHA)
    guard = original.split('def no_trace_imports():\n', 1)[1].split('\n\n\ndef load_trace_api', 1)[0]
    loader = original[original.index('def load_trace_api('):original.index('\n\ndef private_json(')]
    predicate = original[original.index("    result=r.get('observer_cleanup',{})", original.index('def candidate_status')):]
    return (
        (guard, NEW_IMPORT_GUARD),
        (loader, NEW_LOADER.rstrip()),
        ('transport.WireArchive(self.evidence)', 'transport.legacy.WireArchive(self.evidence)'),
        ('self.ports=transport.LegacyWorkerPorts(self.context,self.evidence,self.proxy)',
         'self.ports=session.BatchPorts(self.context,self.evidence,self.proxy)'),
        ("        if self.observer is not None:self.observer.mark_cutoff()\n",
         "        if self.observer is not None:\n            requested=self.now();self.record['admission_cutoff_requested']=requested\n            self.observer.mark_cutoff()\n            self.record['cutoff_validation_finished']=self.now()\n            self.record['minimum_admission_target_elapsed']=requested-began\n"),
        ("require(self.record['observer_cleanup']['status']=='OBSERVER_TRANSPORT_COMPLETE_ONLY','strict observer cleanup/validator failed')",
         "require(self.record['observer_cleanup']['status']=='AUTODRAIN_OBSERVER_TRANSPORT_COMPLETE_ONLY','strict batch observer cleanup/validator failed')"),
        (predicate, NEW_TRACE_PREDICATE),
    )


def patch_helper(source):
    require(sha(source) == HELPER_SHA, 'requested helper parent changed')
    for old, new in helper_pairs(): source = replace(source, old, new)
    return source


def reverse_helper(source):
    for old, new in reversed(helper_pairs()): source = replace(source, new, old)
    require(sha(source) == HELPER_SHA, 'whole helper inverse differs')
    return source


def runner_pairs():
    return (("PREFIX='ssam-a1-first-state-method-monitor-disabled-20261115'",
             "PREFIX='ssam-a1-first-state-autodrain-disabled-20261115'"),
            ("E=BASE/('a1-first-state-method-monitor-disabled-'+arm+'-'",
             "E=BASE/('a1-first-state-autodrain-disabled-'+arm+'-'"))


def patch_runner(source):
    require(sha(source) == RUNNER_SHA, 'requested runner parent changed')
    for old, new in runner_pairs(): source = replace(source, old, new)
    return source


def reverse_runner(source):
    for old, new in reversed(runner_pairs()): source = replace(source, new, old)
    require(sha(source) == RUNNER_SHA, 'whole runner inverse differs')
    return source
