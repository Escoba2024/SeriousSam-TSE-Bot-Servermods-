"""One bounded closed-case replay. No process, Original, Nav, display or Frida access."""
import argparse
import ast
import collections
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import types
sys.dont_write_bytecode = True

E = Path('/srv/tse-cecil-rollout-evidence-20261114')
BASE = Path('/srv/tse-milestone-a-evidence-20261111')
CASES = {'control': BASE/'a1-first-state-qjs10-v4-root-control-20261115-122450',
         'trace': BASE/'a1-first-state-qjs10-v4-root-trace-20261115-122632'}
F = Path('/srv/tse-a1-first-state-qjs10-v4-root-frozen-20261115')
A = F/'method-api'
RESULTS = {'control': '37bd808529c48af397e6669d6e5e5bfebe0d43377f6bbe00e1650689f7a70263',
           'trace': '07b37e6363834959cea04dfb6b513768bcc8b7a6a4b82abb3b1cf6daa95db77c'}
MANIFEST = 'eac23cc167d0569d576bc620f5e176401faa8db86496966044086adbf62c92e9'
PINS = {}
TOTAL_BYTES = 0


def read(path, limit=8*1024*1024):
    global TOTAL_BYTES
    path = Path(path).resolve(strict=True)
    with os.fdopen(os.open(path, os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW), 'rb') as stream:
        before = os.fstat(stream.fileno())
        assert before.st_size <= limit, 'bounded file size: '+str(path)
        data = stream.read(limit+1)
        after = os.fstat(stream.fileno())
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    assert len(data) <= limit
    TOTAL_BYTES += len(data)
    assert TOTAL_BYTES <= 64*1024*1024, 'total closed-read bound'
    digest = hashlib.sha256(data).hexdigest()
    assert str(path) not in PINS or PINS[str(path)] == digest, 'source changed during audit'
    PINS[str(path)] = digest
    return data


def load(path): return json.loads(read(path))


def pure_module(name, path, expected, injected=None):
    source = read(path)
    assert hashlib.sha256(source).hexdigest() == expected
    tree = ast.parse(source)
    if injected:
        # Only data-loading assignments are omitted; every policy function/class is unchanged.
        tree.body = [n for n in tree.body if not (isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id in injected for t in n.targets))]
    module = types.ModuleType(name)
    module.__dict__.update(__file__=str(path), **(injected or {}))
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    return module


def cpu_audit(arm, result, module):
    path = E/f'first-state-qjs10-v4-{arm}-cpu-private.jsonl'
    rows = [json.loads(x) for x in read(path).splitlines()]
    last = rows.pop()
    assert last['ended'] and last['coverage_complete_to_reap'] and last['controller_returncode']==0
    assert last['samples']==len(rows) and last['bound_case']==str(CASES[arm])
    expected = {e['role']:tuple(e['identity']) for e in result['events'] if e['event']=='launched'}
    parent_owner=load(E/f'first-state-qjs10-v4-{arm}-owner.json')
    assert parent_owner['manifest_sha256']==MANIFEST and parent_owner['automatic_retry']is False
    cfg = load(CASES['trace']/'first-state-worker-config.json') if arm=='trace' else None
    if cfg:
        expected['controller']=(cfg['parent']['pid'],cfg['parent']['start_ticks'])
        owner=load(CASES[arm]/'worker-owner.json');expected['worker']=(owner['pid'],owner['start_ticks'])
    domains = collections.defaultdict(lambda: {'valid_samples':0,'unknown_samples':0,'valid_intervals':0,'unknown_intervals':0,'cpu_seconds':0.,'max_core_equivalent_upper':None})
    epochs=set(); bindings=0; samples_unknown=0; previous=None; tick_hz=set(); identities={}
    for row in rows:
        bindings += len(row['binding_errors']); assert not row['binding_errors']
        assert row['known_case'] in (None,str(CASES[arm]))
        s=row['sample']; epochs.add(s['epoch']);tick_hz.add(s['clock_hz'])
        assert type(s['clock_hz'])is int and s['clock_hz']>0
        assert all(type(s[k])in(int,float)and math.isfinite(s[k])for k in ('started','finished'))
        assert s['started']<=s['finished'];samples_unknown += s['status']=='UNKNOWN'
        for name,v in s['processes'].items():
            dom=domains['process:'+name];dom['valid_samples' if v['status']=='VALID' else 'unknown_samples']+=1
            pair=tuple(v['identity']);assert all(type(x)is int and x>0 for x in pair)
            assert name not in identities or identities[name]==pair
            identities[name]=pair
            if name in expected:assert pair==expected[name]
            elif name!='controller':raise AssertionError('unexpected own process domain')
            if v['status']=='VALID':
                assert len(v['raw'])==2
                first,last_raw=(module._proc(text,*pair)for text in v['raw'])
                if name=='controller':assert all(int(text.rsplit(') ',1)[1].split()[1])==parent_owner['pid']for text in v['raw'])
                assert all(b>=a for a,b in zip(first,last_raw))
                assert last_raw==(v['utime_ticks'],v['stime_ticks']) and sum(last_raw)==v['counter']
        for name,v in s['cgroups'].items():
            dom=domains['cgroup:'+name];dom['valid_samples' if v['status']=='VALID' else 'unknown_samples']+=1
            if v['status']=='VALID':
                identity=v['identity'];assert identity==v['identity_before']==v['identity_after']
                assert identity[0]=='/sys/fs/cgroup/system.slice/ssam-a1-first-state-qjs10-v4-root-20261115-'+arm+'-'+name+'.service'
                assert type(identity[1])is int and 0<=identity[1]<2**64
                assert type(identity[2])is int and 0<identity[2]<2**64
                assert len(v['raw'])==1
                usages=[int(x.split()[1])for x in v['raw'][0].splitlines()if x.startswith('usage_usec ')]
                assert usages==[v['counter']] and 0<=v['counter']<2**64
        if previous is not None:
            d=module.delta(previous,s);assert d==row['delta']
            for kind in ('processes','cgroups'):
                for name,v in d[kind].items():
                    dom=domains[('process:'if kind=='processes'else'cgroup:')+name]
                    dom['valid_intervals'if v['status']=='VALID'else'unknown_intervals']+=1
                    if v['status']=='VALID':
                        dom['cpu_seconds']+=v['cpu_seconds']
                        dom['max_core_equivalent_upper']=max(dom['max_core_equivalent_upper']or 0,v['core_equivalent_range'][1])
        previous=s
    assert len(epochs)==len(tick_hz)==1
    return dict(samples=len(rows),binding_errors=bindings,samples_with_unknown_domains=samples_unknown,
                ended_and_covered_to_controller_reap=True,domains=dict(domains),
                no_cross_domain_sum=True,not_host_percent=True,
                source_sha256=PINS[str(path.resolve())],first_started=rows[0]['sample']['started'],
                last_finished=rows[-1]['sample']['finished'],controller_identity_stable=True)


def audit(output):
    manifest=load(F/'source-manifest.json');assert PINS[str((F/'source-manifest.json').resolve())]==MANIFEST
    results={}
    for arm,case in CASES.items():
        r=load(case/'result.json');assert PINS[str((case/'result.json').resolve())]==RESULTS[arm]
        assert load(case/'source-manifest.json')==manifest
        assert read(case/'controller-source.py')==read(F/'run_dual.py')
        assert not r['errors'] and r['input_emissions']==0 and not r['input_receipts']
        assert not r.get('initial_geometry_pending_reads',0)
        assert r['units_closed_verified'] and r['restoration']['restored'] and not r['restoration']['errors']
        assert set(r['cleanup'])=={'server','vanilla','botA'} and all(v['closed']for v in r['cleanup'].values())
        proof=load(E/f'first-state-qjs10-v4-{arm}-root-restore.json')
        assert proof['status']=='PASS_RESTORE' and proof['result_sha256']==RESULTS[arm]
        assert proof['parent_returncode']==0 and proof['closed_log_scope_complete']
        results[arm]=r
    C=CASES['trace'];r=results['trace'];method=r['first_state_method'];o=method['observer_cleanup'];identity=o['identity']
    assert r['status']=='PASS_LIMITED_FIRST_STATE_METHOD_OBSERVED_CALLBACKS_ONLY'
    assert results['control']['status']=='PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY'
    assert not results['control']['first_state_method']['worker_created']
    protocol=A/'first_state_autodrain_protocol.py';policy=A/'vendor/observer/observer_policy.py'
    schema=A/'vendor/observer/event-schema.json';bindings=A/'vendor/observer/bindings/original-bindings.json'
    for p in [schema,bindings]:assert hashlib.sha256(read(p)).hexdigest()==manifest['runtime_dependencies'][str(p)]
    P=pure_module('v4_closed_protocol',protocol,manifest['runtime_dependencies'][str(protocol)])
    V=pure_module('v4_closed_policy',policy,manifest['runtime_dependencies'][str(policy)],
                  {'SCHEMA':load(schema),'BINDINGS':load(bindings)})
    trace=V.TraceValidator(identity);journal=read(C/'observer-rpc.jsonl')
    rows=[P.strict_json(x)for x in journal.splitlines()];drains=[x for x in rows if x['operation']=='worker-drain']
    assert [x['serial']for x in drains]==list(range(1,len(drains)+1))
    assert collections.Counter(x['operation']for x in rows)=={'worker-arm':1,'worker-drain':199,'worker-stop':1,'worker-status':1,'worker-finishstop':1}
    wires=[];caps=[];serial=1;stop=None;final=None;prior_finish=None;prior_start=None;archive_end=0
    timings=r['method_worker']['timings'];files=sorted(C.glob('worker-wire-*.bin'))
    assert len(files)==len(timings)==53
    for i,path in enumerate(files,1):
        data=read(path);meta=load(path.with_suffix('.json'));assert meta=={'length':len(data),'complete':True,'sha256':hashlib.sha256(data).hexdigest()}
        b=P.decode_batch(data,request_id=i,expected_serial=serial);reply=b['reply'];t=timings[i-1]
        assert t['id']==i and t['method']==reply['method']
        assert reply['ok']is True and reply['failed']is False and t['ok']is True
        assert t['started']<=t['finished']<t['deadline']
        for key,value in [('stop_serial',b['stop_serial']),('final_serial',b['final_serial'])]:
            previous=stop if key=='stop_serial'else final
            assert previous is None or previous==value
            if key=='stop_serial':stop=value
            else:final=value
        for cap in b['captures']:
            assert cap['serial']==serial
            original=journal[cap['archive_offset']:cap['archive_offset']+cap['archive_length']]
            assert original==cap['raw'] and hashlib.sha256(original).hexdigest()==cap['sha256']
            packet=P.strict_json(original);assert packet==drains[serial-1]['raw']
            assert cap['archive_offset']>=archive_end;archive_end=cap['archive_offset']+cap['archive_length']
            assert cap['started']<=cap['finished'] and cap['finished']-cap['started']<=.1
            if prior_finish is not None:assert cap['started']>=prior_finish and cap['started']-prior_start<=.1
            prior_finish,prior_start=cap['finished'],cap['started']
            V.validate_packet(packet,identity);trace.consume(packet)
            recorded=o['packet_receipts'][serial-1]
            assert all(recorded[k]==cap[k]for k in cap if k!='raw')
            assert recorded['attempted']and recorded['accepted']and recorded['event_count']==len(packet['events'])
            caps.append({k:v for k,v in cap.items()if k!='raw'}|{'events':len(packet['events']),'cumulative_events':len(trace.events),'enabled':packet['enabled'],'stop_reason':packet['stop_reason']})
            serial+=1
        wires.append(dict(id=i,method=reply['method'],capture_count=len(b['captures']),stop_serial=stop,final_serial=final,bytes=len(data),sha256=meta['sha256'],ipc_seconds=t['finished']-t['started'],ipc_budget=t['deadline']-t['started']))
    assert stop==o['stop_serial']==198 and final==o['final_serial']==199 and serial==200
    assert len(caps)==len(drains)==len(o['packet_receipts'])==o['validated_packets']==199
    assert o['coverage_complete']and not o['errors']
    assert all(x['enabled']and x['stop_reason']is None for x in caps[:stop])
    assert o['cutoff_sequence']==caps[stop-1]['cumulative_events']==2870
    assert caps[-1]['cumulative_events']==2870
    replay_finish=trace.finish(o['external_restore'])
    expected=V.expected_restore_regions(identity)
    assert len(expected)==38 and expected==method['original_regions_before']==o['external_restore']['regions']
    assert all(x['attempted']and x['succeeded']for x in o['cleanup'])
    assert all(x['finished']<=method['absolute_observer_deadline']for x in caps)
    assert method['observation_started']<method['observation_deadline']<=method['admission_cutoff_requested']<=method['cutoff_validation_finished']<=method['absolute_observer_deadline']
    assert o['external_restore']['script_unloaded']and o['external_restore']['session_detached']
    assert r['method_worker']['reaped']and r['method_worker']['returncode']==-15 and not r['method_worker']['sticky_failure']
    runtime=load(C/'observer-runtime-identity.json')
    assert runtime=={'requested_runtime':'qjs','identity':{'runtime':'QJS','pid':identity['pid'],'arch':'ia32','pointer_size':4}}
    last=drains[-1]['raw'];assert not last['errors']and last['terminal_record']is None
    assert last['counters']['getter_calls']==1 and last['counters']['getter_non_main']==0
    assert last['tls_binding']==o['tls_binding']and last['tls_binding']['thread_id']==identity['pid']
    assert last['armed_ms']<=last['tls_binding']['bound_ms']<last['armed_ms']+last['bounds']['binding_ms']
    legacy=[]
    for i,path in enumerate(sorted(C.glob('legacy-rpc-*.json')),1):
        v=load(path)
        for k in ['before_identity','after_identity']:
            if k in v:assert v[k]==identity
        assert not v.get('errors')and not v.get('failures')and not v.get('error')
        legacy.append(dict(index=i,operation=v['operation'],sha256=PINS[str(path.resolve())],status=v.get('status'),succeeded=v.get('succeeded')))
    assert len(legacy)==58
    ticks=[e for e in trace.events[:o['cutoff_sequence']]if e['kind']=='process_game_tick'and e['data']['scope']=='context']
    enter={e['call_id']for e in ticks if e['edge']=='enter'};leave={e['call_id']for e in ticks if e['edge']=='leave'}
    assert enter==leave and len(enter)==205 and o['main_tick_pair_before_cutoff']
    cpu_pins=load(E/'first-state-qjs10-v4-observer-pins.json')
    for path,pin in cpu_pins.items():assert hashlib.sha256(read(path)).hexdigest()==pin
    cpu_path=Path('/srv/tse-cecil-rollout-a-b-20261114/tools/owned_cpu_domains.py')
    CPU=pure_module('v4_closed_cpu',cpu_path,cpu_pins[str(cpu_path)])
    cpu={arm:cpu_audit(arm,value,CPU)for arm,value in results.items()}
    events=collections.Counter(e['kind']+':'+e['edge']for e in trace.events)
    scopes=collections.Counter(e['kind']+':'+e['data']['scope']for e in trace.events)
    value=dict(status='PASS_CLOSED_QJS10_V4_BOUNDED_OBSERVER_TRANSPORT_ONLY',scope='CLOSED_WIRE_DRAIN_RPC_RUNTIME_CPU_AND_EXTERNAL_RESTORE_REPLAY_ONLY',
               utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),qualified=False,first_state_damage_qualified=False,
               result_sha256=RESULTS,manifest_sha256=MANIFEST,wire=wires,capture_receipts=caps,legacy_rpc=legacy,
               raw_journal_operations=dict(collections.Counter(x['operation']for x in rows)),
               stop_serial=stop,final_serial=final,all_raw_captures_1_through_F_accepted=True,
               cutoff_sequence=o['cutoff_sequence'],events_after_cutoff=0,events=dict(events),scopes=dict(scopes),
               counters=last['counters'],bounds=last['bounds'],observed_kinds=method['observed_callback_kinds'],
               getter_tls=dict(callbacks=1,non_main_callbacks=0,binding_delay_js_ms=last['tls_binding']['bound_ms']-last['armed_ms'],
                               raw_tls_binding=o['tls_binding'],not_extra_GetTLS_invocation_claim=True),
               runtime_identity=runtime,replayed_validator_finish=replay_finish,
               final_original_regions=dict(count=38,before_and_after_equal=True,identity_unchanged=True,script_unloaded=True,session_detached=True),
               observer_timing={k:method[k]for k in ['absolute_observer_deadline','observation_started','observation_deadline','admission_cutoff_requested','cutoff_validation_finished','observation_finished','observed_seconds']},
               worker_reap=dict(returncode=-15,sticky_failure=False,reaped=True,description='OwnWorker SIGTERM is intentional inherited roles-closed reap; no observer/IPC exception recorded; no claim that signal exit is normal exit0'),
               cpu=cpu,host={arm:value['host_budget']for arm,value in results.items()},
               initial_pending_observed=False,inputs=0,
               missing_natural_ai_custody=['Both actual actors are Original clients, not a natural Bot-AI shooter; no role/one-local Bot generation/hash qualification transfers.',
                 'Zero Initialize/SetConnected/Unconnected/Death/EEnd or ReceiveDamage observed; pre-arm joins left-censored, first valid post-respawn state unobserved.',
                 'Zero FireColt/PrepareBullet/FireOneBullet/LaunchBullet/InflictDirectDamage: bullet ownership/ray hit/normal-fatal damage chains absent.',
                 'CastRay is recorded unregistered context; 410 enter/leave pairs are not a registered shooter bullet path or hit proof.',
                 'A separate two-actor Bot-shooter/Original-victim condition needs exact registry/role/hash/life binding and actual callbacks; Bot-victim class remains separate.' ],
               limitations=['Four observed hook kinds only; zero counters do not qualify the other14 ABIs.','No host/CPU improvement causality; startup aggregate gap means host budget_pass_claim remains false.','CPU cgroup/process domains overlap and are not summed; UNKNOWN domains/intervals retained.','Capture raw is first Python JSON encoding of Frida result; IPC wire is separate exact archived framing, not Frida native transport bytes.','No clock fusion of JS wall, host monotonic and native game ticks.','Initial zero-PENDING branch was never exercised in either arm and has no native qualification.'],
               input_sha256=PINS.copy(),reader_sha256=hashlib.sha256(read(__file__)).hexdigest(),total_read_bytes=TOTAL_BYTES)
    data=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode();assert len(data)<2*1024*1024
    output=Path(output);output.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with os.fdopen(os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
    print(json.dumps(dict(output=str(output),sha256=hashlib.sha256(data).hexdigest(),status=value['status'],wires=len(wires),drains=len(caps),events=len(trace.events),calls=trace.call_count,cpu_samples={a:v['samples']for a,v in cpu.items()},bytes=len(data))))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();audit(args.output)
