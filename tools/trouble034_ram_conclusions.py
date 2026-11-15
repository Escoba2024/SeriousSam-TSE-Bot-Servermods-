"""Final small selections from the SAME closed034 reader's retained RAM only.

Reproducer (one Native pass): import audit_trouble034_closed as a; a.main();
import trouble034_ram_conclusions as f; f.complete(a.C).
No case/Native file is opened by this module. Earlier receipts stay checkpoints.
"""
import collections
import hashlib
import json
from pathlib import Path
from decimal import Decimal


def printed_9g_interval(raw):
    """%.9g rounding bin; omitted trailing zeros do not reduce precision.

    Zero prints only for exact zero. At a decade the predecessor uses the
    smaller quantum. Endpoints remain conservative decimal rounding ties.
    """
    value=Decimal(raw)
    if not value.is_finite():raise ValueError('finite printed Source time required')
    if value.is_zero():return value,value
    quantum=Decimal(1).scaleb(value.copy_abs().adjusted()-8)
    low=high=quantum/2
    if value.copy_abs()==Decimal(1).scaleb(value.copy_abs().adjusted()):
        if value>0:low/=10
        else:high/=10
    return value-low,value+high


def same_printed_time(raw, actual):
    lower,upper=printed_9g_interval(raw)
    return lower<=Decimal.from_float(actual)<=upper


def recheck_prior_candidates(value):
    """Only old Superset-bin candidates; never reopens logs/Native streams."""
    old=value['owner_lost_context'];events=[];retained=0;rejected=0
    for event in old['events']:
        prior=event['exact_source_time_driver_rows']
        if not prior:continue
        f=event['event']['fields'];lo,hi=printed_9g_interval(f['time']);checks=[]
        for row in prior:
            actual=row['typed']['safe'][4]
            match=bool(f['event_time_known'] and same_printed_time(f['time'],actual))
            retained+=int(match);rejected+=int(not match)
            checks.append(dict(driver_line=row['line'],actual_source_time=actual,retained=match))
        events.append(dict(role=event['event']['role'],history_line=event['event']['line'],
            printed_source_time=f['time'],new_interval=[str(lo),str(hi)],candidates=checks))
    if retained+rejected!=old['exact_source_time_rows']:raise ValueError('prior candidate denominator differs')
    return dict(status='PRINTED_SOURCE_TIME_BIN_CORRECTION_ONLY_NO_RAW_REPLAY',
        old_candidate_count=old['exact_source_time_rows'],retained=retained,rejected=rejected,
        prior_owner_lost_count=old['total'],events=events,
        noncandidate_scope='Old exponent/2 bins were supersets; only existing candidates rechecked; all prior51 event/Driver brackets remain unchanged',
        exact_clock_or_same_call_identity=False)


def owner_context(c, history):
    # Reuse only the existing strict typed() parser, never its old-case analyze().
    from audit_build030_driver_final import typed
    rows=[];g=c['G']
    for role in ['botA','botB']:
        for line,text in enumerate(g['logs'][role].splitlines(),1):
            if not text.startswith('[CecilDriverFinalV1]'):continue
            e=c['source_event'](role,line,text);d=typed(e['fields'])
            binding=g['bind'](role,dict(local=str(d['local']),entity=str(d['actor']),generation=str(d['gen'][0]),tick=str(d['tick'])),line)
            rows.append(dict(role=role,line=line,typed=d,binding=binding))
    result=[]
    for event in history['typed_rows']:
        if event['fields']['reason']!='owner_lost':continue
        f=event['fields'];same=[r for r in rows if r['role']==event['role'] and r['typed']['actor']==f['entity'] and r['typed']['gen']==[f['generation'],f['generation']] and r['typed']['life_link']==1]
        before=[r for r in same if r['line']<event['line']];after=[r for r in same if r['line']>event['line']]
        a=max(before,key=lambda r:r['line']) if before else None
        b=min(after,key=lambda r:r['line']) if after else None
        # Printed .9g Source time: use its exact decimal rounding interval.
        exact=[r for r in same if f['event_time_known'] and same_printed_time(f['time'],r['typed']['safe'][4])]
        def states(tag):
            ss=[r for r in g['source'][event['role']] if r['tag']==tag and int(r.get('entity',-1))==f['entity'] and int(r.get('generation',-1))==f['generation']]
            pre=[r for r in ss if r['line']<event['line']];post=[r for r in ss if r['line']>event['line']]
            return dict(before=max(pre,key=lambda r:r['line']) if pre else None,after=min(post,key=lambda r:r['line']) if post else None)
        result.append(dict(event=event,driver_before=a,driver_after=b,exact_source_time_driver_rows=exact,
            source_states=states('CecilState'),
            nearest_rows_are_not_same_call_or_causal='Only exact_source_time_driver_rows can witness the same printed Source time; 1Hz omission remains UNKNOWN',
            source_branch='BotCecilSafeMotion !useReacquire clears ItemTransit(owner_lost); Driver passes supplyActive!=FALSE. No physical denial cause inferred.'))
    counts=collections.Counter()
    for x in result:
        for position in ['driver_before','driver_after']:
            d=x[position]
            if d:counts[(position,d['typed']['safe'][1],d['typed']['post_mode_decoded']['supplyActive'])]+=1
    return dict(total=len(result),driver_rows_parsed=len(rows),events=result,
        bracket_lane_counts={str(k):v for k,v in counts.items()},
        exact_source_time_rows=sum(len(x['exact_source_time_driver_rows']) for x in result),
        no_native_clock_interpolation=True)


def select_native(rows, spawn):
    selected=[r for r in rows if r['good'] and r['spawn']==spawn]
    if not selected:
        return dict(status='UNKNOWN_NO_GOOD_SAME_LIFE_OBSERVATIONS', observations=[])
    return dict(status='SPARSE_SAME_LIFE_MEMORY_OBSERVATIONS_NOT_ACTION_ACK',
        health_range=[min(r['health'] for r in selected),max(r['health'] for r in selected)],
        owned_counts=dict(collections.Counter(str(r['weapons']['owned']) for r in selected)),
        current_counts=dict(collections.Counter(str(r['weapons']['current']) for r in selected)),
        observations=[{k:r[k] for k in ['read_serial','tick','spawn','entity','world','health','weapons','position','translation','last_buttons']} for r in selected])


def complete(c):
    g=c['G'];out=c['OUT']
    history=json.loads((out/'transit-history-custody.json').read_bytes())
    chains=json.loads((out/'transit-transition-chains.json').read_bytes())
    # Longest complete no-Useful life plus EVERY observed transit-abort life.
    keys=[(f['life']['role'],f['life']['local'],f['life']['spawn_clock']) for f in g['focuses'][:1]]
    for chain in chains['chains']:
        b=chain['abort']['binding']
        if b.get('status')=='BOUND_SOURCE_LIFE':
            key=(chain['abort']['role'],b['local'],b['native_spawn'])
            if key not in keys:keys.append(key)
    cases=[]
    for role,local,spawn in keys:
        life=next(l for l in g['lives'][(role,local)] if l['spawn_clock']==spawn)
        def bound(e):
            b=e.get('binding',{})
            return e.get('role')==role and b.get('local')==local and b.get('native_spawn')==spawn
        bb=[b for b in g['batches'] if bound(dict(b['decision'],binding=b['binding']))]
        events=[e for e in g['supplement']['all_extra_events'] if bound(e)]
        cases.append(dict(role=role,local=local,life=life,
            native=select_native(g['native'][(role,local)],spawn),
            picker_batches=bb,source_goal_support_events=events,
            history_rows=[r for r in history['typed_rows'] if bound(r)],
            source_states=[r for r in g['source'][role] if r['tag']=='CecilState' and int(r['local'])==local and int(r['generation']) in life['generations']],
            boundaries='Source clocks and client-world pointers stay separate from Native clocks/world; line-bracket WPO intervals only, no tick/20 fusion',
            movement_or_pickup_ack=False))
    source=Path(__file__).resolve();c['read'](source)
    c['read'](source.with_name('test_trouble034_ram_conclusions.py'))
    c['read'](source.with_name('audit_build030_driver_final.py'))
    c['read'](source.parents[1]/'poc/candidates/redstation-supply-20261107/driver_final_decision.h')
    ownership=owner_context(c,history)
    pin=c['save']('functional-focus-ram.json',dict(status='RAM_ONLY_SAME_PASS_FOCUS_NOT_CAUSAL_ACCEPTANCE',cases=cases,owner_lost_context=ownership,qualified=False))
    outputs={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(out.iterdir()) if p.is_file()}
    value=dict(status='COMPLETE_CLOSED034_FUNCTIONAL_AUDIT_WITH_TRANSIT_CUSTODY_ONLY',
        result_sha256=c['RESULT'],original_status_unchanged=g['report']['status'],
        qualified=False,a4_pass=False,gameplay_improvement_proven=False,
        core_receipt_sha256=outputs['complete034-final-receipt.json']['sha256'],
        finalizer_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_pins=g['pins'],input_bytes=g['sizes'],actual_total_read_bytes=g['read_bytes'],
        stream_passes=1,old_raw_replays=0,all_native_raw_handles_closed=True,
        output_limit=8*1024*1024,output_pins=outputs,
        selected_focus_sha256=pin['sha256'],
        prior_checkpoints_preserved=True,
        reproducibility='Same Python process: audit_trouble034_closed.main(); trouble034_ram_conclusions.complete(audit_trouble034_closed.C). Earlier complete034 receipt pins the exact first-stage reader; this finalizer is a separate Source step. Invocation-context failures happened before acquire and are not Native rereads.',
        unknowns=['Exact shot/damage/life kill chains','Unobserved eligibility or physics details','Causal pickup ACK','Route/hazard success from endpoint positions or proposals'])
    result=c['save']('complete034-handoff.json',value)
    print('FINAL034_HANDOFF',json.dumps(dict(receipt=result,output_bytes=g['written'],focus=pin)),flush=True)
    return value
