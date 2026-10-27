#!/usr/bin/env python3
"""Exact private source-pinned 1/4/8 duration matrix. Never a release gate alone."""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / 'tools'
NATIVE = REPO / 'performance/native/tools'
CONFIG_BASE = Path('/root/ssam-ai-backups/m1-completion-20261026-0155')
BASE = Path('/root/ssam-ai-backups/m1-prefilter-matrix-20261026-idle-r3')
POLICY = BASE / 'policy.json'
STATE = BASE / 'matrix.json'
HOLD = BASE / 'HOLD.json'
RUNTIME_PARENT = Path('/srv')
MANIFEST = Path('/srv/tse-cecil-p1-build-20261025-01/manifest.json')
OFFLINE_MARKER = Path('/root/ssam-ai-backups/shutdown-20261026-0033/public-disabled.json')
CANDIDATE = '7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf'
PRODUCER_NAMES = ('qualify_bot_sessions.py','bot_session_executor.py','bot_session_runtime.py',
                  'bot_sessions.py','qualify_integrated_wine.py')
STAGE_CONTRACT = (
    (1,3600,3720,'one-hour-idle-r3','one-hour-config.json',27170,':160'),
    (4,3600,3840,'four-hour-idle-r3','4-duration-config.json',27174,':161'),
    (8,7200,7680,'eight-two-hours-idle-r3','8-duration-config.json',27178,':162'),
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_object(path):
    with Path(path).open('rb') as stream:
        raw=stream.read(16*1024**2+1)
    if len(raw)>16*1024**2:raise RuntimeError('bounded policy size exceeded')
    obj=json.loads(raw)
    if not isinstance(obj,dict):raise RuntimeError('JSON object required')
    return obj


def stage_contract():
    return [dict(bots=b,required_s=s,duration_s=d,
        root=str(RUNTIME_PARENT/('tse-session-qualification-master-m1-prefilter-'+label+'-20261026')),
        config=str(CONFIG_BASE/name),port=port,display=display)
        for b,s,d,label,name,port,display in STAGE_CONTRACT]


def validate_stage_contract(policy):
    if policy.get('stages')!=stage_contract():
        raise ValueError('exact fresh 1/3600,4/3600,8/7200 private matrix required')


def verify_file_pins(pins):
    if not isinstance(pins,dict) or not pins:raise RuntimeError('nonempty source pin inventory required')
    for name,digest in pins.items():
        try:actual=sha(name)
        except OSError as exc:raise RuntimeError('pinned input missing: '+name) from exc
        if not isinstance(digest,str) or len(digest)!=64 or actual!=digest:
            raise RuntimeError('pinned input drift: '+name)


def expected_source_paths():
    return {str(p) for p in [
        *[NATIVE/n for n in PRODUCER_NAMES],
        *[NATIVE/n for n in ('bot_telemetry.py','redstation_preset.py','gaming_names.py','log_error_prefilter.py')],
        NATIVE.parent/'poc/scripts/Phase1HumanAI.ini',
        *[TOOLS/n for n in ('native_receipt_io.py','native_owned_process.py',
                           'm1_duration_acceptance.py','run_eight_duration_hardened.py')],
        Path(__file__).resolve()]}


def verify_policy(policy, expected_sha):
    if sha(POLICY)!=expected_sha:raise RuntimeError('caller-pinned policy drift')
    validate_stage_contract(policy)
    if policy.get('candidate_sha256')!=CANDIDATE:raise RuntimeError('wrong native candidate')
    if set(policy.get('source_sha256',{}))!=expected_source_paths():
        raise RuntimeError('complete exact source inventory required')
    verify_file_pins(policy['source_sha256'])
    verify_file_pins(policy.get('artifact_sha256'))
    manifest=read_object(MANIFEST)
    if (manifest.get('build_ok') is not True or manifest.get('dll_sha256')!=CANDIDATE or
        sha(manifest['candidate'])!=CANDIDATE):raise RuntimeError('candidate manifest mismatch')
    required_artifacts={str(MANIFEST),str(Path(manifest['candidate'])),str(OFFLINE_MARKER)}|{
        s['config'] for s in policy['stages']}
    if set(policy['artifact_sha256'])!=required_artifacts:raise RuntimeError('exact artifact pins required')
    producer={n:sha(NATIVE/n) for n in PRODUCER_NAMES}
    if policy.get('harness_sha256')!=producer:raise RuntimeError('native producer inventory mismatch')
    for stage in policy['stages']:
        config=read_object(stage['config'])
        if (config.get('enabled') is not True or type(config.get('max_bots')) is not int or
            config['max_bots']!=stage['bots'] or len(config.get('identities',[]))!=stage['bots'] or
            len(config.get('servers',[]))!=1):raise RuntimeError('stage config mismatch')


def build_command(stage):
    return ['/usr/bin/python3','-u',str(NATIVE/'qualify_bot_sessions.py'),
        '--config',stage['config'],'--runtime',stage['root'],'--duration',str(stage['duration_s']),
        '--execute','--cecil-p1','--preset','redstation','--port',str(stage['port']),
        '--display',stage['display'],'--build-manifest',str(MANIFEST),
        '--offline-public-marker',str(OFFLINE_MARKER)]


def require_stage_verdict(verdict, stage, candidate):
    seconds=verdict.get('continuous_full_population_s')
    if (verdict.get('status')!='DURATION_RECEIPTS_ACCEPTED' or
        type(verdict.get('bots')) is not int or verdict['bots']!=stage['bots'] or
        type(verdict.get('required_s')) is not int or verdict['required_s']!=stage['required_s'] or
        type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<stage['required_s'] or
        verdict.get('dll_sha256')!=candidate or verdict.get('reasons')!=[] or
        verdict.get('m1_complete') is not False):raise RuntimeError('native duration gate rejected')


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def save(support,state):
    state['utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    support.atomic_json(STATE,state)


def run_stage(stage,policy,policy_sha,support,reader,acceptance,OwnedProcess,state):
    root=Path(stage['root'])
    if root.exists():raise RuntimeError('refuse runtime adoption or overwrite')
    support.ROOT=root;support.BOTS=stage['bots'];support.DURATION_S=stage['duration_s']
    support.TOOLS=TOOLS
    budget=support.derive_budget(read_object(stage['config']))
    child=owned=None;normal=False;cleaning=False;heartbeat={};handlers={}
    log=BASE/('stage-'+str(stage['bots'])+'.log')
    launched=time.monotonic();last=0
    def interrupted(sig,frame):
        if not cleaning:raise RuntimeError('owned matrix interrupt '+str(sig))
    for sig in (signal.SIGINT,signal.SIGTERM):handlers[sig]=signal.signal(sig,interrupted)
    try:
        verify_policy(policy,policy_sha)
        command=build_command(stage)
        support.atomic_json(BASE/('stage-'+str(stage['bots'])+'-command.json'),
                            dict(argv=command,source_sha256=policy['source_sha256'],m1_complete=False),overwrite=False)
        with log.open('xb') as stream:
            child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,
                                   env=dict(os.environ,PYTHONOPTIMIZE='0'))
        owned=OwnedProcess(child)
        state.update(status='NATIVE_DURATION_RUNNING',active=dict(stage,controller_pid=child.pid,
                     outer_start_ticks=owned.start_ticks,budget=budget));save(support,state)
        while child.poll() is None:
            now=time.monotonic()
            if now-launched>budget['total_s']:raise RuntimeError('bounded lifecycle deadline exceeded')
            if now-last>=15:
                verify_policy(policy,policy_sha)
                heartbeat=support.check_live_heartbeat(reader,launched_mono=launched,
                    now_mono=now,now_epoch=time.time(),budget=budget,previous=heartbeat)
                state['active']['heartbeat']=heartbeat;save(support,state);last=now
            time.sleep(2)
        owned.close()
        result=reader(root/'result.json')
        census=support.wait_for_clean_census(root,result,timeout=budget['cleanup_s'])
        if census.get('clean') is not True:raise RuntimeError('independent native cleanup census not clean')
        if child.returncode!=0:raise RuntimeError('native stage exited nonzero: '+str(result.get('error')))
        verify_policy(policy,policy_sha)
        verdict=acceptance.evaluate_runtime(root,bots=stage['bots'],required_s=stage['required_s'],
                    dll_sha256=policy['candidate_sha256'],harness_sha256=policy['harness_sha256'])
        require_stage_verdict(verdict,stage,policy['candidate_sha256'])
        receipt=dict(root=str(root),verdict=verdict,cleanup_census=census,
            receipt_sha256={n:sha(root/n) for n in ('source-sha256.json','result.json','host-guard.json','samples.jsonl')})
        state['stages'].append(receipt);state.pop('active',None);save(support,state);normal=True
        return receipt
    except BaseException as exc:
        cleaning=True;stop_error=None
        # A producer already in FAIL cleanup must not receive a second parent-death signal.
        if owned is not None and child.poll() is None:
            try:
                try:
                    latest=reader(root/'result.json') if (root/'result.json').exists() else {}
                except (OSError,ValueError,RuntimeError):
                    latest=None
                # Ambiguous receipts may mean cleanup is already underway. Keep
                # bounded supervision; never guess that a second signal is safe.
                if latest is None or latest.get('status')=='FAIL':
                    child.wait(timeout=budget['abort_wait_s'])
                else:support.request_orderly_abort(owned,timeout=budget['abort_wait_s'])
            except BaseException as stop:stop_error=str(stop)
        if owned is not None and child.poll() is not None:owned.close()
        try:
            result=reader(root/'result.json') if (root/'result.json').exists() else {}
            census=support.wait_for_clean_census(root,result,timeout=budget['cleanup_s'])
        except BaseException as ce:census=dict(clean=False,errors=[str(ce)])
        still_live=child is not None and child.poll() is None
        state.update(status='CLEANUP_HOLD' if still_live or stop_error or not census.get('clean') else 'BLOCKED',
                     error=str(exc),cleanup_census=census,no_retry=True,stop_error=stop_error)
        save(support,state)
        if state['status']=='CLEANUP_HOLD':support.atomic_json(HOLD,state,overwrite=False)
        raise
    finally:
        for sig,handler in handlers.items():signal.signal(sig,handler)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--policy-sha256')
    args=parser.parse_args()
    if not args.execute:
        print(json.dumps(dict(status='DRY_RUN_NO_NATIVE_ACTIONS',stages=stage_contract(),m1_complete=False)))
        return
    if os.geteuid()!=0 or os.uname().nodename!='ubuntu-4gb-nbg1-2':raise RuntimeError('authorized host/root required')
    if not args.policy_sha256:raise RuntimeError('explicit policy hash required')
    policy=read_object(POLICY);verify_policy(policy,args.policy_sha256)
    if STATE.exists() or HOLD.exists() or any(Path(s['root']).exists() for s in policy['stages']):
        raise RuntimeError('fresh matrix only; no implicit retries or adoption')
    support=load_module('_prefilter_matrix_support',TOOLS/'run_eight_duration_hardened.py')
    support.TOOLS=TOOLS;reader,acceptance=support.load_pinned_modules()
    OwnedProcess=support.load_owned_process_class()
    state=dict(status='STARTING',m1_complete=False,policy_sha256=args.policy_sha256,stages=[],
               next_gate='CANDIDATE_BOUND_RECOVERY_AND_FINAL_REVIEW')
    with (CONFIG_BASE/'matrix.lock').open('r+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Another invocation may have finished between preflight and flock.
        if STATE.exists() or HOLD.exists() or any(Path(s['root']).exists() for s in policy['stages']):
            raise RuntimeError('fresh matrix only; no implicit retries or adoption')
        verify_policy(policy,args.policy_sha256)
        save(support,state)
        try:
            for stage in policy['stages']:
                run_stage(stage,policy,args.policy_sha256,support,reader,acceptance,OwnedProcess,state)
            verify_policy(policy,args.policy_sha256)
            for stage,receipt in zip(policy['stages'],state['stages']):
                for name,digest in receipt['receipt_sha256'].items():
                    if sha(Path(stage['root'])/name)!=digest:raise RuntimeError('completed stage receipt drift')
                verdict=acceptance.evaluate_runtime(stage['root'],bots=stage['bots'],required_s=stage['required_s'],
                    dll_sha256=policy['candidate_sha256'],harness_sha256=policy['harness_sha256'])
                require_stage_verdict(verdict,stage,policy['candidate_sha256'])
            state.update(status='DURATION_MATRIX_ACCEPTED_PRIVATE_ONLY',m1_complete=False);save(support,state)
        except BaseException as exc:
            if state.get('status') not in ('BLOCKED','CLEANUP_HOLD'):
                state.update(status='BLOCKED',error=str(exc),no_retry=True);save(support,state)
            raise


if __name__=='__main__':main()
