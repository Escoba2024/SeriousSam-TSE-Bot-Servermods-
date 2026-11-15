"""Bounded CLOSED NaturalAI030-V2 audit; no runtime, process or API access."""
import argparse,ast,collections,hashlib,json,math,os,sys,types
from pathlib import Path
sys.dont_write_bytecode=True
BASE=Path('/srv/tse-milestone-a-evidence-20261111')
E=Path('/srv/tse-cecil-rollout-evidence-20261114')
F=Path('/srv/tse-a1-natural-ai030-two-actor-status-v2-root-frozen-20261115')
A=F/'method-api'
CASES={'control':BASE/'a1-natural-ai030-v2-root-control-20261115-134842','trace':BASE/'a1-natural-ai030-v2-root-trace-20261115-135001'}
MANIFEST='882b578a17af082332d7aecfbcf541ac3ca0f8e1aea4772e2027172039d3ff6b'
RESULTS={'control':'1f69abbc7e18d908dfdfe811dc32dc7457987c8ebac14c4feb567d2a12a67a6a','trace':'6a1c82996277870b4c33a45287a3b7578bbbf99dad6b3cf27a24335e4da4e0ba'}
PINS={};TOTAL_BYTES=0

def read(path,limit=8*1024*1024):
    global TOTAL_BYTES
    path=Path(path).resolve(strict=True)
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as stream:
        before=os.fstat(stream.fileno());assert before.st_size<=limit
        value=stream.read(limit+1);after=os.fstat(stream.fileno())
    assert len(value)<=limit and(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_atime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_atime_ns)
    TOTAL_BYTES+=len(value);assert TOTAL_BYTES<=64*1024*1024
    pin=hashlib.sha256(value).hexdigest();assert str(path)not in PINS or PINS[str(path)]==pin
    PINS[str(path)]=pin;return value
def load(path):return json.loads(read(path))
def pure_module(name,path,pin,injected=None):
    source=read(path);assert hashlib.sha256(source).hexdigest()==pin
    tree=ast.parse(source)
    if injected:tree.body=[n for n in tree.body if not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in injected for t in n.targets))]
    m=types.ModuleType(name);m.__dict__.update(__file__=str(path),**(injected or{}));exec(compile(tree,str(path),'exec'),m.__dict__);return m

def capture_summary(captures):
    """Diagnostic denominator only; never repairs strict validator acceptance."""
    events=[];terminal=[];first=None;accepted=0;failed=0
    for expected,cap in enumerate(captures,1):
        if type(cap['serial'])is not int or cap['serial']!=expected:raise ValueError('capture serial not exact1..F')
        packet=cap['packet'];rows=packet['events'];events.extend(rows)
        if cap['accepted']:accepted+=len(rows)
        else:failed+=len(rows)
        if packet.get('terminal_record')is not None:terminal.append(packet['terminal_record'])
        dropped=packet.get('counters',{}).get('dropped',0)
        if first is None and(dropped or packet.get('errors')or packet.get('terminal_record')is not None or packet.get('stop_reason')not in(None,'host requested')):
            first={'serial':cap['serial'],'stop_reason':packet.get('stop_reason'),'dropped':dropped,'terminal_record':packet.get('terminal_record')}
    return dict(events=events,terminal_records=terminal,first_sticky=first,accepted_events=accepted,failed_packet_events=failed)

def cpu_audit(arm,result,module,cfg):
    path=E/f'natural-ai030-v2-{arm}-cpu-private.jsonl';rows=[json.loads(x)for x in read(path).splitlines()];ending=rows.pop()
    assert ending['ended']and ending['coverage_complete_to_reap']and ending['controller_returncode']==(0 if arm=='control'else 1)
    assert ending['samples']==len(rows)and ending['bound_case']==str(CASES[arm])
    owner=load(E/f'natural-ai030-v2-{arm}-owner.json');assert owner['manifest_sha256']==MANIFEST and owner['automatic_retry']is False
    expected={e['role']:tuple(e['identity'])for e in result['events']if e['event']=='launched'}
    if cfg:
        expected['controller']=(cfg['parent']['pid'],cfg['parent']['start_ticks']);w=load(CASES[arm]/'worker-owner.json');expected['worker']=(w['pid'],w['start_ticks'])
    domains=collections.defaultdict(lambda:dict(valid_samples=0,unknown_samples=0,valid_intervals=0,unknown_intervals=0,cpu_seconds=0.,max_core_equivalent_upper=None))
    identities={};epochs=set();hz=set();previous=None;binding_errors=0
    for row in rows:
        binding_errors+=len(row['binding_errors']);assert not row['binding_errors']and row['known_case']in(None,str(CASES[arm]))
        sample=row['sample'];epochs.add(sample['epoch']);hz.add(sample['clock_hz']);assert type(sample['clock_hz'])is int and sample['clock_hz']>0
        assert all(type(sample[k])in(int,float)and math.isfinite(sample[k])for k in('started','finished'))and sample['started']<=sample['finished']
        for name,value in sample['processes'].items():
            domain=domains['process:'+name];domain['valid_samples'if value['status']=='VALID'else'unknown_samples']+=1
            pair=tuple(value['identity']);assert all(type(x)is int and x>0 for x in pair)
            assert name not in identities or identities[name]==pair;identities[name]=pair
            if name in expected:assert pair==expected[name]
            else:assert name=='controller'
            if value['status']=='VALID':
                assert len(value['raw'])==2
                first,last=(module._proc(text,*pair)for text in value['raw']);assert all(b>=a for a,b in zip(first,last))
                assert last==(value['utime_ticks'],value['stime_ticks'])and sum(last)==value['counter']
                if name=='controller':assert all(int(text.rsplit(') ',1)[1].split()[1])==owner['pid']for text in value['raw'])
        for name,value in sample['cgroups'].items():
            domain=domains['cgroup:'+name];domain['valid_samples'if value['status']=='VALID'else'unknown_samples']+=1
            if value['status']=='VALID':
                ident=value['identity'];assert ident==value['identity_before']==value['identity_after']
                assert ident[0]=='/sys/fs/cgroup/system.slice/ssam-a1-natural-ai030-v2-root-20261115-'+arm+'-'+name+'.service'
                assert type(ident[1])is int and 0<=ident[1]<2**64 and type(ident[2])is int and 0<ident[2]<2**64
                assert len(value['raw'])==1
                assert [int(x.split()[1])for x in value['raw'][0].splitlines()if x.startswith('usage_usec ')]==[value['counter']]
        if previous is not None:
            delta=module.delta(previous,sample);assert delta==row['delta']
            for kind in('processes','cgroups'):
                for name,value in delta[kind].items():
                    domain=domains[('process:'if kind=='processes'else'cgroup:')+name];domain['valid_intervals'if value['status']=='VALID'else'unknown_intervals']+=1
                    if value['status']=='VALID':
                        domain['cpu_seconds']+=value['cpu_seconds'];domain['max_core_equivalent_upper']=max(domain['max_core_equivalent_upper']or 0,value['core_equivalent_range'][1])
        previous=sample
    assert len(epochs)==len(hz)==1
    return dict(samples=len(rows),binding_errors=binding_errors,domains=dict(domains),covered_to_controller_reap=True,no_cross_domain_sum=True,not_host_percent=True)

def audit(output):
    assert os.statvfs('/srv').f_bavail*os.statvfs('/srv').f_frsize>=8*1024**3+64*1024**2
    manifest=load(F/'source-manifest.json');assert PINS[str((F/'source-manifest.json').resolve())]==MANIFEST
    results={};ownership={};restore={}
    for arm,case in CASES.items():
        r=load(case/'result.json');assert PINS[str((case/'result.json').resolve())]==RESULTS[arm]
        assert load(case/'source-manifest.json')==manifest and read(case/'controller-source.py')==read(F/'run_dual.py')
        assert r['input_emissions']==0 and not r['input_receipts']and r['units_closed_verified']and r['restoration']['restored']
        assert not r['restoration']['errors']and set(r['cleanup'])=={'server','vanilla','botA'}and all(x['closed']for x in r['cleanup'].values())
        proof=load(E/f'natural-ai030-v2-{arm}-root-restore.json');assert proof['status']=='PASS_RESTORE'and proof['result_sha256']==RESULTS[arm]
        assert proof['parent_returncode']==(0 if arm=='control'else 1)and proof['counts']=={'files':664,'absences':9,'closed_logs':3}
        restore[arm]=proof;results[arm]=r;ownership[arm]=load(case/'natural-ai-ownership.json')
    r=results['trace'];method=r['first_state_method'];o=method['observer_cleanup'];identity=o['identity'];C=CASES['trace']
    assert r['status']=='FAIL'and results['control']['status']=='PASS_LIMITED_UNINSTRUMENTED_NATURAL_AI030_ORIGINAL_VICTIM_ONLY'
    assert not results['control']['first_state_method']['worker_created']and results['control']['method_worker']is None
    protocol=A/'first_state_autodrain_protocol.py';policy=A/'vendor/observer/observer_policy.py'
    schema=A/'vendor/observer/event-schema.json';bindings=A/'vendor/observer/bindings/original-bindings.json'
    P=pure_module('closed_natural_ai_protocol',protocol,manifest['runtime_dependencies'][str(protocol)])
    V=pure_module('closed_natural_ai_policy',policy,manifest['runtime_dependencies'][str(policy)],{'SCHEMA':load(schema),'BINDINGS':load(bindings)})
    N=pure_module('closed_natural_ai_ownership',F/'first_state_natural_ai.py',manifest['runtime_dependencies'][str(F/'first_state_natural_ai.py')])
    cfg=load(C/'first-state-worker-config.json');assert cfg['expected_identity']==identity
    assert cfg['frame']['natural_ai_ownership']==ownership['trace']
    assert N.roles_from_receipt(cfg['frame'],cfg['roles'],cfg['pins'])=={'vanilla':'vanilla','botA':'bot'}
    assert {p['role']for p in identity['players']}=={'vanilla','bot'}and len(identity['players'])==2
    for arm,proof in ownership.items():
        assert proof['mapping']==results[arm]['actual_slot_mapping']=={'vanilla':0,'botA':1}
        assert proof['log_epoch']==results[arm]['natural_ai_staging']['log_epoch']and proof['log_epoch']['cleared_before_launch']is True
        N.validate_gms(bytes.fromhex(proof['gms_hex']))
        assert proof['staged']==results[arm]['natural_ai_staging']['staged']and proof['staged']['dll_sha256']==N.BOT_GAME
        log=read(CASES[arm]/'botA-closed.log').decode('latin1').replace('\r\n','\n');assert log.startswith(proof['log_text'])
        assert [p['entity_id']for p in cfg['frame']['roles'].values()]if arm=='trace'else True
    trace=V.TraceValidator(identity);journal=read(C/'observer-rpc.jsonl');rows=[P.strict_json(line)for line in journal.splitlines()]
    drains=[x for x in rows if x['operation']=='worker-drain'];assert [x['serial']for x in drains]==list(range(1,len(drains)+1))
    caps=[];wires=[];serial=1;S=None;Fserial=None;last_finish=None;last_start=None;archive_end=0
    files=sorted(C.glob('worker-wire-*.bin'));timings=r['method_worker']['timings'];assert len(files)==len(timings)
    for index,path in enumerate(files,1):
        wire=read(path);meta=load(path.with_suffix('.json'));assert meta=={'length':len(wire),'complete':True,'sha256':hashlib.sha256(wire).hexdigest()}
        batch=P.decode_batch(wire,request_id=index,expected_serial=serial);reply=batch['reply'];t=timings[index-1]
        assert t['id']==index and t['method']==reply['method']and t['started']<=t['finished']<t['deadline']
        if S is not None:assert batch['stop_serial']==S
        if Fserial is not None:assert batch['final_serial']==Fserial
        S=batch['stop_serial'];Fserial=batch['final_serial']
        for cap in batch['captures']:
            assert cap['serial']==serial
            raw=journal[cap['archive_offset']:cap['archive_offset']+cap['archive_length']]
            assert raw==cap['raw']and hashlib.sha256(raw).hexdigest()==cap['sha256']and cap['archive_offset']>=archive_end
            archive_end=cap['archive_offset']+cap['archive_length'];packet=P.strict_json(raw);assert packet==drains[serial-1]['raw']
            assert cap['started']<=cap['finished']and cap['finished']-cap['started']<=.1
            if last_finish is not None:assert cap['started']>=last_finish and cap['started']-last_start<=.1
            last_finish,last_start=cap['finished'],cap['started']
            recorded=o['packet_receipts'][serial-1];assert recorded['attempted']and all(recorded[k]==v for k,v in cap.items()if k!='raw')
            schema_error=None
            try:V.validate_packet(packet,identity)
            except Exception as error:schema_error=repr(error)
            error=None
            try:trace.consume(packet);accepted=True
            except Exception as exc:error=repr(exc);accepted=False
            assert accepted==recorded['accepted']
            if not accepted:assert error==recorded['error']
            caps.append({k:v for k,v in cap.items()if k!='raw'}|dict(packet=packet,accepted=accepted,schema_error=schema_error,error=error))
            serial+=1
        wires.append(dict(id=index,method=reply['method'],ok=reply.get('ok'),failed=reply.get('failed'),error=reply.get('error'),captures=len(batch['captures']),stop_serial=S,final_serial=Fserial,ipc_seconds=t['finished']-t['started'],budget=t['deadline']-t['started'],timing_ok=t.get('ok')))
    assert S==o['stop_serial']and Fserial==o['final_serial']and serial==Fserial+1
    assert len(caps)==len(drains)==len(o['packet_receipts'])and sum(c['accepted']for c in caps)==o['validated_packets']
    assert not o['coverage_complete']
    summary=capture_summary(caps);events=summary.pop('events');terminal=summary.pop('terminal_records')
    assert [e['sequence']for e in events]==list(range(1,len(events)+1))
    first=summary['first_sticky'];failure=caps[first['serial']-1];prior=caps[first['serial']-2]
    calls={e['call_id']:e for e in events if e['edge']=='enter'}
    tick_counts=collections.Counter(e['tick']['ordinal']for e in events if e.get('tick'))
    target=first['terminal_record'];parent_chain=[];call=target['call_id'];seen=set()
    while call is not None:
        assert call not in seen;seen.add(call);entry=calls.get(call)
        if entry is None:parent_chain.append({'call_id':call,'entry_missing':True});break
        parent_chain.append(entry);call=entry['parent_call_id']
    critical_tick=[e for e in events if e.get('tick',{}).get('ordinal')==target['tick']['ordinal']]
    around=dict(first_sticky=first,prior_capture={k:v for k,v in prior.items()if k not in('packet',)},
        failed_capture={k:v for k,v in failure.items()if k not in('packet',)},
        start_to_start_seconds=failure['started']-prior['started'],service_gap_seconds=failure['started']-prior['finished'],
        failed_drain_seconds=failure['finished']-failure['started'],
        prior_counter=prior['packet']['counters'],failed_counter=failure['packet']['counters'],
        terminal_parent_chain=parent_chain,critical_tick_events=critical_tick,
        max_raw_events_per_native_tick=max(tick_counts.values()),raw_events_by_native_tick=dict(tick_counts))
    external=o['external_restore'];expected=V.expected_restore_regions(identity)
    assert len(expected)==38 and expected==method['original_regions_before']==external['regions']
    assert external['before_identity']==external['after_identity']==identity
    assert external['script_unloaded']and external['session_detached']
    try:trace.finish(external);finish_error=None
    except Exception as error:finish_error=repr(error)
    assert finish_error is not None
    runtime=load(C/'observer-runtime-identity.json');assert runtime=={'requested_runtime':'qjs','identity':{'runtime':'QJS','pid':identity['pid'],'arch':'ia32','pointer_size':4}}
    last=caps[-1]['packet'];assert last['tls_binding']['thread_id']==identity['pid']and last['counters']['getter_non_main']==0
    assert all(x['finished']<=method['absolute_observer_deadline']for x in caps)
    legacy=[]
    for path in sorted(C.glob('legacy-rpc-*.json')):
        value=load(path)
        for key in('before_identity','after_identity'):
            if key in value:assert value[key]==identity
        legacy.append({k:v for k,v in value.items()if k in('operation','status','succeeded','error','errors','failures')}|{'file':path.name,'sha256':PINS[str(path.resolve())]})
    cpu_pins=load(E/'natural-ai030-v2-observer-pins.json')
    for path,pin in cpu_pins.items():assert hashlib.sha256(read(path)).hexdigest()==pin
    cpu_path=Path('/srv/tse-cecil-rollout-a-b-20261114/tools/owned_cpu_domains.py')
    CPU=pure_module('natural_ai_closed_cpu',cpu_path,cpu_pins[str(cpu_path)])
    cpu={arm:cpu_audit(arm,value,CPU,cfg if arm=='trace'else None)for arm,value in results.items()}
    kinds=last['counters']['by_kind'];assert len(kinds)==18
    value=dict(status='CLOSED_AUDIT_TRACE_FAIL_QUEUE_COVERAGE_RETAINED',qualified=False,first_state_damage_qualified=False,
        result_sha256=RESULTS,manifest_sha256=MANIFEST,wire=wires,capture_summary=summary,
        captures=[{k:v for k,v in c.items()if k!='packet'}|{'events':len(c['packet']['events']),'counters':c['packet']['counters'],'stop_reason':c['packet']['stop_reason']}for c in caps],
        raw_operations=dict(collections.Counter(x['operation']for x in rows)),stop_serial=S,final_serial=Fserial,
        accepted_prefix_events=len(trace.events),raw_enqueued_events=len(events),terminal_record_count=len(terminal),
        actual_event_counts=dict(collections.Counter(e['kind']+':'+e['edge']for e in events)),
        actual_scopes=dict(collections.Counter(e['kind']+':'+e['data']['scope']for e in events)),
        kind_counters=kinds,first_sticky_detail=around,non_order_events=[e for e in events if e['kind']not in('process_game_tick','apply_action','post_moving','cast_ray')],
        final_packet={k:v for k,v in last.items()if k!='events'},original38_regions={'before_and_after_bytes_equal':True,'identity_equal':True,'script_unloaded':True,'session_detached':True,'regions':external['regions']},
        final_validator_error=finish_error,cleanup_errors=o['errors'],cleanup_steps=o['cleanup'],legacy_rpc=legacy,
        worker_reap=r['method_worker'],runtime_identity=runtime,ownership=ownership,trace_full_ownership_policy_replayed=True,
        control_ownership_scope='Fresh Source/GMS/staging/slot identity; no independent archived full bot-module mapping receipt found',
        input_emissions=0,initial_pending_observed={a:result.get('initial_geometry_pending_reads',0)for a,result in results.items()},
        host={a:result['host_budget']for a,result in results.items()},cpu=cpu,root_restore=restore,
        limits=['Fail/drop/aborted leaves and all tails retained; no validator/queue/limit change','Raw failed-packet events are diagnostic, never accepted first-state proof','No fusion of JS wall, host monotonic and native game clocks','Unregistered casts/damage are not registered Colt/bullet ownership or victim damage proof','Control has no trace worker; its limitedPASS does not repair traceFAIL','Host startup gaps mean no general resource-budget pass'],
        input_sha256=PINS.copy(),total_read_bytes=TOTAL_BYTES,reader_sha256=hashlib.sha256(read(__file__)).hexdigest())
    data=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode();assert len(data)<5*1024*1024
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with os.fdopen(os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
    print(json.dumps(dict(output=str(output),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),read_bytes=TOTAL_BYTES,wires=len(wires),drains=len(caps),first_sticky=first['serial'],events=len(events),accepted_prefix_events=len(trace.events),cpu_samples={a:v['samples']for a,v in cpu.items()})))

def supplement(source,output):
    """Small custody/inventory followup; never rereads the observer journal/wire."""
    r=load(source);details={}
    for arm,case in CASES.items():
        q=r['ownership'][arm];registry=load(case/'join-registry.json')
        assert registry['mapping']==q['mapping']
        inventory=[json.loads(line)for line in read(case/'inventory.jsonl').splitlines()]
        snapshots=[]
        for row in inventory:
            sample=row['snapshot'];players=[p for p in sample['players']if p.get('present')]
            assert {p['slot']:p['entity_id']for p in players}=={int(k):v for k,v in q['entity_ids'].items()}
            snapshots.append({'game_tick':sample['game_tick'],'process_identity':sample['process_identity'],
                'consistency':sample['consistency'],'players':[{k:p[k]for k in('slot','entity_id','health','armor','spawned_tick','last_buttons','weapons')}for p in players]})
        raw=read(case/'botA-closed.log');normalized=q['log_text'].encode('latin1')
        candidates=[normalized,normalized.replace(b'\n',b'\r\n')]
        matches=[x for x in candidates if raw.startswith(x)and hashlib.sha256(x).hexdigest()==q['raw_log_sha256']]
        assert len(matches)==1,'exact archived fresh Source prefix hash/bytes'
        queryrows=[json.loads(x)for x in read(case/'join-queries.jsonl').splitlines()]
        populations=[int(x['query']['numplayers'])for x in queryrows if x.get('query')and'numplayers'in x['query']]
        assert set(populations)<=set((0,1,2))and 1 in populations and 2 in populations
        details[arm]={'source_prefix_raw_sha256':q['raw_log_sha256'],'source_prefix_bytes':len(matches[0]),
            'closed_log_prefix_byteexact':True,'gms_sha256':hashlib.sha256(bytes.fromhex(q['gms_hex'])).hexdigest(),
            'mapping':q['mapping'],'actor_ids':q['entity_ids'],'join_population_counts':dict(collections.Counter(populations)),
            'initial_inventory_samples':snapshots,'no_during_observer_inventory_samples_claim':True}
    kinds=r['kind_counters'];a=r['first_sticky_detail'];critical=a['critical_tick_events']
    actual_result=load(CASES['trace']/'result.json');assert PINS[str((CASES['trace']/'result.json').resolve())]==RESULTS['trace']
    values={int(k):v for k,v in a['raw_events_by_native_tick'].items()};tick=a['first_sticky']['terminal_record']['tick']['ordinal']
    a3=Path('/srv/tse-a3-direct020-hard-controller-20261114/frozen-v2/damage_readonly.js');a3source=read(a3).decode()
    assert 'inflictor_known_player'in a3source and 'first_processed_state_proven:false'in a3source
    value={'status':'SMALL_CUSTODY_AND_DENOMINATOR_SUPPLEMENT_NOT_NEW_NATIVE_PASS','full_receipt_sha256':PINS[str(Path(source).resolve())],
        'source_and_inventory':details,'first_sticky':a['first_sticky'],
        'complete_ticks_before_failure':len([k for k in values if k<tick]),
        'raw_event_counts_per_complete_tick':dict(collections.Counter(v for k,v in values.items()if k<tick)),
        'failed_tick_raw_events':len(critical),'failed_tick_kind_edges':dict(collections.Counter(e['kind']+':'+e['edge']for e in critical)),
        'failed_tick_js_wall_span_ms':max(e['wall_ms']for e in critical)-min(e['wall_ms']for e in critical),
        'failed_tick_true_total_censored':True,'terminal_is_65th_attempt_in_failed_tick':True,
        'first_sticky_host_elapsed_from_observation_start':a['failed_capture']['started']-actual_result['first_state_method']['observation_started'],
        'other_weapon_identity_proven':False,'colt_chain_observed':any(kinds[k]['entered']for k in('fire_colt','prepare_bullet','fire_one_bullet','launch_bullet'))>0,
        'registered_receive_damage_calls':kinds['receive_damage']['entered'],'initialize_calls':kinds['initialize_player']['entered'],
        'a3_comparison':{'path':str(a3),'sha256':hashlib.sha256(a3source.encode()).hexdigest(),
            'scope':'Historical original ReceiveDamage payload/source comparison only; no ABI/method qualification transfer',
            'facts':['Registered victim before/after state and inflictor_known_player field exist','No first processed state proof','No guaranteed Bullet owner/Initialize custody from that smaller collector']},
        'single_next_recommendation':{'new_condition_required':True,'name':'Registered first-state and damage-chain observer contract',
            'preserve':['Existing native identity/life/init/TLS/byte/queue/TTL/drop guards','All registered actor Init/connection/death/first-valid GameTick/ReceiveDamage facts','Registered Colt weapon/Bullet-owner/Cast descendants and explicit unknown-owner outcomes'],
            'narrow_only':'Do not enqueue a full world CastRay row when no registered Colt/Bullet ancestry exists; retain exact excluded-call counters under a NEW denominator contract',
            'must_not_claim':['Cannot convert this FULL18 queueFAIL to PASS','No normal/fatal/first-state success until actual relevant complete chains exist','Unknown other-weapon ownership remains INCOMPLETE','A3 ReceiveDamage alone does not prove Initialize or Bullet ownership'],
            'precondition':'Root must review the exact new relevant-chain completeness contract/source classification and its adversarial tests before any implementation/native'},
        'input_sha256':PINS.copy(),'source_reads_this_supplement':TOTAL_BYTES,'no_full_wire_or_raw_journal_replay':True}
    data=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode();assert len(data)<512*1024
    with os.fdopen(os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(output=str(output),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),read_bytes=TOTAL_BYTES)))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--supplement')
    args=parser.parse_args();supplement(args.supplement,args.output)if args.supplement else audit(args.output)
