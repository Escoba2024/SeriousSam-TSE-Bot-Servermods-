"""Exact035 coordinator/finalizer derivation; no Raw opens until main()."""
import ast
import hashlib
import json
import os
from pathlib import Path

BASE=Path(__file__).with_name('audit_trouble034_closed.py')
BASE_SHA='ad942928daaca4226bda5b08b01d52825dccaae9a395712ff772856d01300e77'
FINAL=Path(__file__).with_name('trouble034_ram_conclusions.py')
FINAL_SHA='4c31b7f4b154af34a67c789b7f12e4124da8cd26586a0283f07817e1b676739e'
CASE=Path('/srv/tse-milestone-a-evidence-20261111/nav20-035-trouble-root-trouble-20261115-200004')
PACKAGE=Path('/srv/tse-nav20-035-trouble300-diag1-root-frozen-20261115')
OUT=Path('/srv/tse-trouble035-closed-audit-evidence-20261115')
E=Path('/srv/tse-cecil-rollout-evidence-20261114')
BUILD=Path('/srv/tse-milestone-a-build-035-20261115')
RESULT='7da99dace3e09fcd8ea843ed053f6cd0e7642265d85b318af10fb8259826fe9b'
RUNNER='da427193b4e554092b4fef297206e8dcaecad6f507d1b774b5f8f7d59e67654f'
MANIFEST='07497e5f4f469a34d44d04e9f0543a7834f778a323c1512a46ee8828558222e7'
BUILD_MANIFEST='942b4922d1b36b64e96ed998661d2ce23b9ce04508210639bf65425c5c98aa7b'
DLL='e76395a7cb9fc4ea436cc09e9d86b0774f64b8b8df100fa722f4790afe19cae5'
HEADER='a2cf922bdd05058e50b633282a4ebb21be6f25ef01e1482c5dd56b710a8c88d9'
DRIVER='1c081af07169c96b3158307135d0c2b495ea91ce6e957a690a90363d90e914ff'
HOST_SHA='f70127dc83f17edfb75c28db05e043f1327310af06e22072a17e16594625a2bf'
RESTORE_SHA='8c742566bdc45b2df1af19066edab3a652e5c318cc67e45712022a23766ab2e5'
COORDINATOR_PAIRS=[('034','035',15),
 ('bb91a86973a2241ef0eddaf541c3f3160c73ec380811236534068dbf92a458e5',RESULT,1),
 ('183149','200004',1),
 ('652bb66d266d2e52bf961a3b6141112a7fe8abce4c8501032e2c1e3c3e0264dd',HEADER,1)]
FINALIZER_PAIRS=[('034','035',12),('test_trouble035_ram_conclusions.py','test_trouble034_ram_conclusions.py',1)]
C=None
STATE={}

def digest(raw):return hashlib.sha256(raw).hexdigest()

def transform(raw,pairs,parent_sha,reverse=False):
    if not reverse and digest(raw)!=parent_sha:raise ValueError('exact parent full Source required')
    text=raw.decode()
    for a,b,n in (reversed(pairs) if reverse else pairs):
        if reverse:a,b=b,a
        if text.count(a)!=n:raise ValueError('exact Source anchor multiplicity')
        text=text.replace(a,b)
    result=text.encode();ast.parse(result)
    if reverse and digest(result)!=parent_sha:raise ValueError('whole Source inverse differs')
    return result

def adapt(raw,reverse=False):return transform(raw,COORDINATOR_PAIRS,BASE_SHA,reverse)
def adapt_finalizer(raw,reverse=False):return transform(raw,FINALIZER_PAIRS,FINAL_SHA,reverse)

def small_read(path,cap=2*1024*1024):
    with os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb') as f:raw=f.read(cap+1)
    if len(raw)>cap:raise ValueError('bounded small Source/metadata input')
    return raw

def validate_metadata(m):
    r=m['result'];f=m['manifest'];restore=m['restore'];host=m['host'];b=m['build']
    if (r['status']!='PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY' or r['errors'] or
        r['controller_sha256']!=RUNNER or r['candidate_sha256']!=DLL or r['map_key']!='trouble' or
        r['diagnostics_enabled'] is not True or r['functional_pass'] is not False or r['qualified'] is not False or
        set(r['cleanup'])!={'server','botA','botB','vanilla'} or not all(v['closed'] is True for v in r['cleanup'].values())):
        raise ValueError('exact035 closed result')
    if (restore['status']!='PASS_RESTORE' or restore['result_sha256']!=RESULT or
        restore['case_result']!=str(CASE/'result.json') or restore['counts']!={'files':640,'absences':0,'closed_logs':4} or
        restore['parent_returncode']!=0 or restore['closed_log_scope_complete'] is not True or
        set(restore['started_roles'])!={'server','botA','botB','vanilla'}):raise ValueError('exact035 Root restore')
    if (host['status']!='PASS_HOST_OBSERVATION_ONLY' or host['child_exit_code']!=0 or host['child_reaped'] is not True or
        host['errors'] or host['signals_sent']!=0 or host['automatic_retries']!=0):raise ValueError('exact035 host observation')
    c=f['comparison'];mc=f['map_case']
    if (c['order']!=['035'] or c['map']!='trouble' or c['seconds']!=300 or c['diagnostics']!=1 or
        c['observer_fps']!=20 or c['hard_difficulty']!=2 or mc['bot_count']!=8 or mc['bot_tier']!=3 or
        any(o['automatic_retry'] is not False or o['automatic_sequence'] is not False for o in (c,mc)) or
        f['candidate']['build_manifest_sha256']!=BUILD_MANIFEST or f['candidate']['dll_sha256']!=DLL or
        b['dll_sha256']!=DLL or b['build_ok'] is not True or b['qualified'] is not False):raise ValueError('exact035 condition/build')
    return True

def output_guard(free_bytes,exists=False):
    if exists or free_bytes<2**33+2**26+8*2**20:raise ValueError('fresh output/8GiB+64MiB+8MiB reserve')

def preflight():
    """Only stat and small metadata/Source reads; no heavy stream or log opens."""
    names=['inventory.jsonl','read-attempts.jsonl','session-health.jsonl']+[r+'-closed.log' for r in ('server','botA','botB','vanilla')]
    sizes={n:(CASE/n).stat().st_size for n in names}
    logs=[v for n,v in sizes.items() if n.endswith('-closed.log')]
    if max(sizes.values())>64*2**20 or sum(sizes.values())>128*2**20 or max(logs)>16*2**20 or sum(logs)>32*2**20:raise ValueError('prospective Raw stat admission')
    paths={'result':CASE/'result.json','manifest':CASE/'source-manifest.json','restore':E/'navigation035-trouble-root-restore.json','host':E/'navigation035-trouble-host/receipt.json','build':BUILD/'manifest.json'}
    raw={p:small_read(p) for p in paths.values()};objects={k:json.loads(raw[p]) for k,p in paths.items()}
    for p,sha in [(paths['result'],RESULT),(paths['manifest'],MANIFEST),(paths['restore'],RESTORE_SHA),(paths['host'],HOST_SHA),(paths['build'],BUILD_MANIFEST),(CASE/'controller-source.py',RUNNER),(PACKAGE/'source-manifest.json',MANIFEST),(BUILD/'Sources/Game/BotSupplyNative.h',HEADER),(BUILD/'Sources/Game/BotDriver.cpp',DRIVER)]:
        if p not in raw:raw[p]=small_read(p)
        if digest(raw[p])!=sha:raise ValueError('exact035 metadata/Source pin: '+str(p))
    validate_metadata(objects)
    st=os.statvfs(OUT.parent);free=st.f_bavail*st.f_frsize;output_guard(free,OUT.exists())
    return dict(status='PREFLIGHT_SOURCE_METADATA_STAT_ONLY_NO_RAW',sizes=sizes,total_raw_bytes=sum(sizes.values()),metadata_bytes=sum(map(len,raw.values())),free_bytes=free,output=str(OUT),pins={str(p):digest(v) for p,v in raw.items()}),raw

def coordinator_scope():
    raw=small_read(BASE);changed=adapt(raw)
    if adapt(changed,True)!=raw:raise ValueError('coordinator inverse')
    scope={'__file__':str(Path(__file__).resolve()),'__name__':'closed035_coordinator'}
    exec(compile(changed,str(BASE)+'[exact035]','exec'),scope)
    STATE.update(coordinator_parent=digest(raw),coordinator_executed=digest(changed))
    return scope

def main():
    global C
    admission,cache=preflight();scope=coordinator_scope();original=scope['namespace'];parent_raw=small_read(BASE)
    def seeded():
        c=original()
        for p,raw in cache.items():
            c['account'](p,raw);c['G']['cache'][str(p)]=raw
        c['account'](BASE,parent_raw);c['G']['cache'][str(BASE)]=parent_raw
        return c
    scope['namespace']=seeded
    print('PREFLIGHT035',json.dumps(admission),flush=True)
    scope['main']();C=scope['C'];STATE.update(preflight=admission,scope=scope)

def complete():
    if C is None:raise ValueError('same-process main required; no second acquire')
    raw=small_read(FINAL);changed=adapt_finalizer(raw)
    if adapt_finalizer(changed,True)!=raw:raise ValueError('corrected finalizer inverse')
    scope={'__file__':str(FINAL.resolve()),'__name__':'closed035_ram_finalizer'}
    exec(compile(changed,str(FINAL)+'[exact035]','exec'),scope)
    value=scope['complete'](C)
    proof={k:v for k,v in STATE.items() if k!='scope'}
    proof.update(status='COMPLETE_CLOSED035_ADAPTER_AND_FINALIZER_NOT_A4_PASS',finalizer_parent=digest(raw),finalizer_executed=digest(changed),adapter_sha256=digest(small_read(Path(__file__))),old_raw_replays=0,analytic_raw_acquires=1,source_and_native_clocks_separate=True,proposal_is_not_movement_or_pickup=True,output_bytes_before_receipt=C['G']['written'])
    pin=C['save']('complete035-source-adapter-receipt.json',proof)
    print('ADAPTER035_COMPLETE',json.dumps(dict(receipt=pin,output_bytes=C['G']['written'])),flush=True)
    return value

if __name__=='__main__':main();complete()
