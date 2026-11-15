"""Bounded CLOSED new registered-scope audit, no runtime/fixture/API actions."""
import argparse,ast,collections,hashlib,json,math,os,sys,types
from pathlib import Path
BASE=Path('/srv/tse-milestone-a-evidence-20261111')
E=Path('/srv/tse-cecil-rollout-evidence-20261114')
F=Path('/srv/tse-a1-registered-first-state-damage-v1-v2-root-frozen-20261115')
D=Path('/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115')
A=F/'method-api'
CASES={'control':BASE/'a1-registered-damage-v1-v2-root-control-20261115-150725',
       'trace':BASE/'a1-registered-damage-v1-v2-root-trace-20261115-150838'}
MANIFEST='1e9a4c115669ca87c24761fb2ce71f46d0d3953447c0576c2f097887428c92d8'
TRACE_RESULT='05c17acbd4854cd00631d54d4d47c1cf9d5f9cd7762ff22632862fc81a53cc1d'
SCOPE='REGISTERED_FIRST_STATE_DAMAGE_V1'
CACHE={};PINS={};TOTAL_BYTES=0;STATE={}

def require(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path,limit=8*1024*1024):
    global TOTAL_BYTES
    path=Path(path).resolve(strict=True);key=str(path)
    if key in CACHE:return CACHE[key]
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:
        a=os.fstat(f.fileno());require(a.st_size<=limit,'single-file read bound')
        b=f.read(limit+1);z=os.fstat(f.fileno())
    require(len(b)<=limit and(a.st_dev,a.st_ino,a.st_size,a.st_atime_ns,a.st_mtime_ns)==
      (z.st_dev,z.st_ino,z.st_size,z.st_atime_ns,z.st_mtime_ns),'stable no-atime source')
    TOTAL_BYTES+=len(b);require(TOTAL_BYTES<=32*1024*1024,'total read bound')
    CACHE[key]=b;PINS[key]=sha(b);return b
def load(p):return json.loads(read(p))
def pure(name,path,pin,injected=None):
    source=read(path);require(sha(source)==pin,'pinned pure module')
    tree=ast.parse(source)
    if injected:tree.body=[n for n in tree.body if not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in injected for t in n.targets))]
    m=types.ModuleType(name);m.__dict__.update(__file__=str(path),**(injected or{}));exec(compile(tree,str(path),'exec'),m.__dict__);return m

def scope_summary(caps,S,final):
    require(type(S)is int and type(final)is int and 0<=S<=final==len(caps),'exact S/F')
    rows=[];last=None;positive=None
    for i,cap in enumerate(caps,1):
        require(type(cap['serial'])is int and cap['serial']==i,'capture1..F')
        p=cap['packet'];require(p['measurement_scope']==SCOPE,'new explicit scope')
        s=p['scope_counters'];c=p['counters'];rows.extend(p['events'])
        require([e['row_sequence']for e in rows]==list(range(1,len(rows)+1)),'full row sequence')
        require(s['rows_attempted']==c['events_enqueued']==c['events_drained']==len(rows),'row denominator')
        require(s['native_edges']==c['events_attempted']==len(rows)+2*s['completed_excluded']+s['pending'],'native/excluded denominator')
        require(s['entered_excluded']==s['completed_excluded']and s['incomplete_closed']==0,'closed exclusion proof')
        if i==S:positive=dict(s)
        last=p
    require(last is not None,'nonempty final')
    positive=positive or dict.fromkeys(last['scope_counters'],0)
    return {'raw_full_rows':len(rows),'positive_full_rows':positive['rows_attempted'],
      'tail_full_rows':len(rows)-positive['rows_attempted'],'native_edges_final':last['scope_counters']['native_edges'],
      'excluded_calls_final':last['scope_counters']['completed_excluded'],'positive_at_S':positive,
      'final_at_F':last['scope_counters'],'native_sequence_has_real_exclusion_gaps':[e['sequence']for e in rows]!=list(range(1,len(rows)+1))}

def cpu_reader():
    # Reuse only the qualified closed-reader function. Exact prefix/returncode retarget.
    path=Path(__file__).with_name('audit_natural_ai030_v2_closed.py');source=read(path).decode()
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)and n.name=='cpu_audit')
    old=ast.get_source_segment(source,node)
    pairs=[('natural-ai030-v2','registered-damage-v1-v2'),('(0 if arm==\'control\'else 1)','0')]
    new=old
    for a,b in pairs:new=new.replace(a,b)
    # The returncode replacement is not globally reversible (literal 0 is common).
    # Compare the exact single changed assertion and then reverse the prefix.
    inverse=new.replace("ending['controller_returncode']==0","ending['controller_returncode']==(0 if arm=='control'else 1)")
    inverse=inverse.replace('registered-damage-v1-v2','natural-ai030-v2')
    require(inverse==old,'whole qualified CPU function inverse')
    env=dict(E=E,CASES=CASES,MANIFEST=MANIFEST,read=read,load=load,collections=collections,math=math,json=json)
    exec(compile(new,str(path)+'::retarget_cpu_only','exec'),env)
    return env['cpu_audit'],{'parent_function_sha256':sha(old.encode()),'retarget_function_sha256':sha(new.encode()),'edits':pairs}

def source_inverses():
    root=Path(__file__).parent
    def module(name,injected=None):
        p=root/(name+'.py');return pure('closed_'+name,p,sha(read(p)),injected)
    patch=module('first_state_registered_damage_patch')
    policy=module('first_state_registered_damage_policy')
    builder=module('prepare_first_state_registered_damage',{'P':patch,'V':policy})
    builder.read=read
    proof={}
    for rel in builder.CHANGED:
        child=read(D/rel);parent=read(builder.PARENT/rel)
        require(builder.reverse_source(rel,child)==parent,'fresh whole scope source inverse')
        proof[rel]={'child_sha256':sha(child),'parent_sha256':sha(parent),'whole_inverse':True}
    return proof

def audit(output):
    free=os.statvfs('/srv').f_bavail*os.statvfs('/srv').f_frsize
    require(free>=8*1024**3+64*1024**2+5*1024**2,'disk floor reserve and output')
    manifest=load(F/'source-manifest.json');require(sha(read(F/'source-manifest.json'))==MANIFEST,'exact Root manifest')
    results={};ownership={};restore={};result_pins={}
    for arm,case in CASES.items():
        r=load(case/'result.json');results[arm]=r;result_pins[arm]=sha(read(case/'result.json'))
        require(result_pins[arm]==TRACE_RESULT if arm=='trace'else result_pins[arm].startswith('f215d516'),'actual result pin')
        require(load(case/'source-manifest.json')==manifest and read(case/'controller-source.py')==read(F/'run_dual.py'),'actual executed source')
        require(r['input_emissions']==0 and not r['input_receipts']and r['units_closed_verified'],'inputfree own roles')
        require(r['restoration']['restored']and not r['restoration']['errors']and all(q['closed']for q in r['cleanup'].values()),'closed restore')
        proof=load(E/f'registered-damage-v1-v2-{arm}-root-restore.json');restore[arm]=proof
        require(proof['status']=='PASS_RESTORE'and proof['result_sha256']==result_pins[arm]and proof['parent_returncode']==0,'independent Root restore')
        require(proof['counts']=={'files':664,'absences':9,'closed_logs':3},'full Root restore count')
        ownership[arm]=load(case/'natural-ai-ownership.json')
    STATE['results']=results
    require(results['control']['status']=='PASS_LIMITED_UNINSTRUMENTED_NATURAL_AI030_ORIGINAL_VICTIM_ONLY','limited control label')
    r=results['trace'];method=r['first_state_method'];o=method['observer_cleanup'];identity=o['identity'];C=CASES['trace']
    require(r['status']=='PASS_LIMITED_REGISTERED_FIRST_STATE_DAMAGE_METHOD_CALLBACKS_ONLY','new limited method label')
    require(not results['control']['first_state_method']['worker_created']and results['control']['method_worker']is None,'control no worker')
    schema=load(A/'vendor/observer/event-schema.json');bindings=load(A/'vendor/observer/bindings/original-bindings.json')
    V=pure('closed_registered_policy',A/'vendor/observer/observer_policy.py',manifest['runtime_dependencies'][str(A/'vendor/observer/observer_policy.py')],{'SCHEMA':schema,'BINDINGS':bindings})
    P=pure('closed_registered_protocol',A/'first_state_autodrain_protocol.py',manifest['runtime_dependencies'][str(A/'first_state_autodrain_protocol.py')])
    N=pure('closed_registered_ownership',F/'first_state_natural_ai.py',manifest['runtime_dependencies'][str(F/'first_state_natural_ai.py')])
    cfg=load(C/'first-state-worker-config.json');require(cfg['expected_identity']==identity,'server identity config')
    require(N.roles_from_receipt(cfg['frame'],cfg['roles'],cfg['pins'])=={'vanilla':'vanilla','botA':'bot'},'actual Source-owned AI role')
    custody={}
    for arm,q in ownership.items():
        result=results[arm];case=CASES[arm];require(q['mapping']==result['actual_slot_mapping']=={'vanilla':0,'botA':1},'real population mapping')
        require(q['log_epoch']==result['natural_ai_staging']['log_epoch']and q['log_epoch']['cleared_before_launch'],'fresh Source log epoch')
        N.validate_gms(bytes.fromhex(q['gms_hex']));require(q['staged']==result['natural_ai_staging']['staged']and q['staged']['dll_sha256']==N.BOT_GAME,'actual030 staging')
        raw=read(case/'botA-closed.log');text=q['log_text'].encode('latin1');prefixes=[text,text.replace(b'\n',b'\r\n')]
        matches=[p for p in prefixes if raw.startswith(p)and sha(p)==q['raw_log_sha256']];require(len(matches)==1,'Source byteexact prefix')
        registry=load(case/'join-registry.json');require(registry['mapping']==q['mapping'],'Source/session registry')
        queries=[json.loads(x)for x in read(case/'join-queries.jsonl').splitlines()]
        populations=collections.Counter(int(x['query']['numplayers'])for x in queries if x.get('query')and'numplayers'in x['query'])
        require(set(populations)<=set((0,1,2))and 1 in populations and 2 in populations,'exclusive0→1→2 admission')
        inventory=[json.loads(x)for x in read(case/'inventory.jsonl').splitlines()]
        custody[arm]={'source_prefix_sha256':q['raw_log_sha256'],'prefix_bytes':len(matches[0]),'population_counts':dict(populations),
          'mapping':q['mapping'],'entity_ids':q['entity_ids'],'gms_sha256':sha(bytes.fromhex(q['gms_hex'])),
          'inventory_samples':inventory,'control_no_independent_bot_modulemap_archive_claim':arm=='control'}
    trace=V.TraceValidator(identity);journal=read(C/'observer-rpc.jsonl');journalrows=[P.strict_json(x)for x in journal.splitlines()]
    drains=[q for q in journalrows if q['operation']=='worker-drain'];require([q['serial']for q in drains]==list(range(1,len(drains)+1)),'all indexed Raw captures')
    caps=[];wire_summary=[];serial=1;S=None;final=None;last_start=None;last_finish=None;archive_end=0
    timings=r['method_worker']['timings'];files=sorted(C.glob('worker-wire-*.bin'));require(len(files)==len(timings),'all IPC replies')
    for index,path in enumerate(files,1):
        wire=read(path);meta=load(path.with_suffix('.json'));require(meta=={'complete':True,'length':len(wire),'sha256':sha(wire)},'whole wire hash')
        batch=P.decode_batch(wire,request_id=index,expected_serial=serial);reply=batch['reply'];t=timings[index-1]
        require(t['id']==index and t['method']==reply['method']and t['started']<=t['finished']<t['deadline'],'actual IPC time bound')
        if S is not None:require(batch['stop_serial']==S,'S immutable')
        if final is not None:require(batch['final_serial']==final,'F immutable')
        S,final=batch['stop_serial'],batch['final_serial']
        for c in batch['captures']:
            require(c['serial']==serial,'capture1..F');raw=journal[c['archive_offset']:c['archive_offset']+c['archive_length']]
            require(raw==c['raw']and sha(raw)==c['sha256']and c['archive_offset']>=archive_end,'Raw beforeparse exact offsets/hash')
            archive_end=c['archive_offset']+c['archive_length'];packet=P.strict_json(raw);require(packet==drains[serial-1]['raw'],'same original packet')
            require(c['started']<=c['finished']and c['finished']-c['started']<=.1,'drain duration')
            if last_start is not None:require(c['started']>=last_finish and c['started']-last_start<=.1,'drain service bounds')
            last_start,last_finish=c['started'],c['finished'];record=o['packet_receipts'][serial-1]
            require(record['attempted']and all(record[k]==v for k,v in c.items()if k!='raw'),'capture custody metadata')
            V.validate_packet(packet,identity);trace.consume(packet);require(record['accepted'],'all newly accepted')
            caps.append({k:v for k,v in c.items()if k!='raw'}|{'packet':packet,'accepted':True});serial+=1
        wire_summary.append({'id':index,'method':reply['method'],'ok':reply.get('ok'),'failed':reply.get('failed'),'error':reply.get('error'),
          'captures':len(batch['captures']),'S':S,'F':final,'started':t['started'],'finished':t['finished'],'deadline':t['deadline'],'timing_ok':t.get('ok')})
    require(S==o['stop_serial']and final==o['final_serial']and serial==final+1,'same recorded S/F')
    require(len(caps)==len(drains)==len(o['packet_receipts'])==o['validated_packets']and o['coverage_complete'],'complete new coverage')
    STATE.update(caps=caps,events=trace.events,identity=identity,cfg=cfg,policy=V)
    totals=scope_summary(caps,S,final);events=trace.events;last=caps[-1]['packet'];native_kinds=last['counters']['by_kind']
    require(len(native_kinds)==18,'all18 actual kind denominators')
    expected=V.expected_restore_regions(identity);external=o['external_restore']
    require(len(expected)==38 and expected==method['original_regions_before']==external['regions'],'actual38Original byte regions')
    require(external['before_identity']==external['after_identity']==identity and external['script_unloaded']and external['session_detached'],'full independent Original cleanup')
    finish=trace.finish(external);require(finish['status']=='OBSERVER_TRANSPORT_COMPLETE_ONLY','new strict finish')
    runtime=load(C/'observer-runtime-identity.json');require(runtime=={'requested_runtime':'qjs','identity':{'runtime':'QJS','pid':identity['pid'],'arch':'ia32','pointer_size':4}},'actual cold QJS/ia32/4 server identity')
    require(last['tls_binding']['thread_id']==identity['pid']and last['counters']['getter_non_main']==0,'TLS actual main binding')
    require(all(q['finished']<=method['absolute_observer_deadline']for q in caps),'unchanged observer deadline')
    kinds={};life={};calls={};damage=[]
    for kind,counter in native_kinds.items():
        full=collections.Counter(e['edge']for e in events if e['kind']==kind)
        kinds[kind]={'native':counter,'full_rows':dict(full),'excluded_completed_calls':counter['completed']-full['leave']}
        require(counter['entered']-full['enter']==counter['completed']-full['leave']and(kind in('cast_ray','continue_cast')or counter['entered']==full['enter']),'perkind excluded denominator')
    for e in events:
        calls.setdefault(e['call_id'],{})[e['edge']]=e
        s=e['player']
        if s:
            key=(s['role'],s['id'],s['generation'],s['init_call_id'],s['spawn_clock'])
            q=life.setdefault(key,{'role':s['role'],'generation':s['generation'],'init_call_id':s['init_call_id'],'spawn_clock':s['spawn_clock'],
              'rows':0,'first_native_sequence':e['sequence'],'last_native_sequence':e['sequence'],'kinds':collections.Counter(),'anchors':[],
              'health_min':s['health'],'health_max':s['health'],'first_tick_ordinal':e['tick']['ordinal'],'last_tick_ordinal':e['tick']['ordinal']})
            q['rows']+=1;q['last_native_sequence']=e['sequence'];q['kinds'][e['kind']+':'+e['edge']]+=1
            q['last_tick_ordinal']=e['tick']['ordinal'];q['health_min']=min(q['health_min'],s['health']);q['health_max']=max(q['health_max'],s['health'])
            if s['valid_anchor']is not None and s['valid_anchor']not in q['anchors']:q['anchors'].append(s['valid_anchor'])
    for cid,pair in calls.items():
        require(set(pair)=={'enter','leave'},'real full retained Enter/Leave')
        if pair['enter']['kind']=='receive_damage':
            a,b=pair['enter'],pair['leave'];owner=a['data']['payload']['inflictor']
            damage.append({'call_id':cid,'victim_role':a['player']['role'],'inflictor_role':owner['role']if owner else None,
              'before':a,'after':b,'health_delta':b['player']['health']-a['player']['health'],
              'fatal':a['player']['health']>0>=b['player']['health'],'actual_first_state_claim':False})
    cpu_pins=load(E/'registered-damage-v1-v2-observer-pins.json')
    for p,h in cpu_pins.items():require(sha(read(p))==h,'actual CPU observer source')
    cpu_path=Path('/srv/tse-cecil-rollout-a-b-20261114/tools/owned_cpu_domains.py')
    CPU=pure('closed_registered_cpu',cpu_path,cpu_pins[str(cpu_path)])
    cpu_fn,cpu_derivation=cpu_reader();cpu={arm:cpu_fn(arm,result,CPU,cfg if arm=='trace'else None)for arm,result in results.items()}
    reader_attempts={};host_outer={}
    for arm,case in CASES.items():
        attempts=[json.loads(x)for x in read(case/'rotation-read-attempts.jsonl').splitlines()]
        reader_attempts[arm]={'rows':len(attempts),'top_level_keys':sorted(set().union(*(set(x)for x in attempts))),
          'statuses':dict(collections.Counter(str(x.get('status',x.get('accepted','UNSPECIFIED')))for x in attempts)),
          'error_rows':[x for x in attempts if any(k in x for k in('error','exception','reason'))]}
        directory=E/f'registered-damage-v1-v2-{arm}-host'
        host_outer[arm]={'receipt':load(directory/'receipt.json'),'samples':[json.loads(x)for x in read(directory/'host-samples.jsonl').splitlines()]}
    source_proof=load(Path('/srv/tse-registered-first-state-damage-evidence-20261115/final-source-proof-v3.json'))
    peer=load(E/'registered-damage-v1-v2-root-peer-review.json')
    require(peer['status']=='PASS_SCOPE'and peer['manifest_sha256']==MANIFEST and peer['other_files_byte_equal']==132,'exact Root application proof')
    for p,h in source_proof['whole_source_inverses'].items():require(sha(read(D/p))==h['child_sha256'],'actual D-v3 Source proof child')
    for rel in('method-api/vendor/observer/observer_policy.py','method-api/vendor/observer/event-schema.json','method-api/observer_body.js'):
        require(read(F/rel)==read(D/rel),'new contract source unchanged by Root')
    receipt={'status':'CLOSED_REGISTERED_DAMAGE_V1_V2_METHOD_AUDIT_ONLY','qualified':False,'first_state_damage_qualified':False,
      'result_sha256':result_pins,'manifest_sha256':MANIFEST,'runtime_identity':runtime,'registry_identity':identity,
      'wire_replies':wire_summary,'capture_totals':totals,'stop_serial':S,'final_serial':final,
      'capture_receipts':[{k:v for k,v in q.items()if k!='packet'}|{'rows':len(q['packet']['events']),
        'counters':q['packet']['counters'],'scope_counters':q['packet']['scope_counters'],'enabled':q['packet']['enabled'],
        'stop_reason':q['packet']['stop_reason']}for q in caps],
      'actual_kinds':kinds,'actual_retained_roles':dict(collections.Counter((e['player']['role']if e['player']else'context')+':'+e['kind']+':'+e['edge']for e in events)),
      'lives':list(life.values()),'actual_damage_intervals':damage,
      'init_call_ids':[cid for cid,p in calls.items()if p['enter']['kind']=='initialize_player'],
      'native_game_ticks':[(p['enter']['tick'],p['leave']['tick'])for p in calls.values()if p['enter']['kind']=='process_game_tick'],
      'final_packet':{k:v for k,v in last.items()if k!='events'},'strict_finish':finish,
      'original38_regions':external,'cleanup_errors':o['errors'],'cleanup_steps':o['cleanup'],'worker_reap':r['method_worker'],
      'rpc_operations':dict(collections.Counter(x['operation']for x in journalrows)),
      'ownership':ownership,'custody':custody,'reader_attempts':reader_attempts,'cpu':cpu,'cpu_reader_derivation':cpu_derivation,
      'host_inner':{a:r['host_budget']for a,r in results.items()},'host_outer':host_outer,'root_restore':restore,
      'source_application_peer':peer,'author_source_proof_sha256':sha(read(Path('/srv/tse-registered-first-state-damage-evidence-20261115/final-source-proof-v3.json'))),
      'source_template_independently_reviewed_by_author':False,'fresh_seven_source_inverses':source_inverses(),'input_emissions':0,
      'limits':['New method coverage only; absence never proves first-state/normal/fatal damage.',
        'No clock fusion between JS wall, host monotonic or native game tick.',
        'Excluded worldcasts have counters and source-limited ancestry proof, no retained per-cast payload/target claim.',
        'CPU process and cgroup domains remain distinct; no general budget/ABI/A1 claim.'],
      'input_sha256':PINS.copy(),'total_distinct_file_read_bytes':TOTAL_BYTES,'reader_sha256':sha(read(__file__))}
    raw=(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+'\n').encode();require(len(raw)<=5*1024*1024,'bounded output')
    output=Path(output)
    with os.fdopen(os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    STATE['receipt']=receipt
    print(json.dumps({'output':str(output),'sha256':sha(raw),'bytes':len(raw),'read_bytes':TOTAL_BYTES,'wires':len(files),'captures':len(caps),'S':S,'F':final,'totals':totals,'damage_intervals':len(damage),'init_calls':len(receipt['init_call_ids'])},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);audit(p.parse_args().output)
