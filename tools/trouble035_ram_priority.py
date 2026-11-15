"""Same-process closed035 RAM selections; no Native files or runtime calls."""
import collections
import hashlib
import json
from decimal import Decimal
from pathlib import Path
USEFUL=0x3df8

def priority_status(batch,driver,goal):
    if driver is None or goal is None:return 'UNKNOWN_NO_SAME_CALL_DRIVER_OR_TARGET'
    k=batch['key'];d=driver['typed'];f=batch['decision']['fields'];i=f['input'];ar=batch['arbitration']
    same=(driver['role'],d['local'],d['tick'],d['actor'],d['gen'][0])==(k[1],k[2],k[5],k[3],k[4])
    if not same or d['gen'][0]!=d['gen'][1] or d['exit_actor']!=d['actor'] or d['life_link']!=1:return 'UNKNOWN_CHANGED_OR_CROSSCALL_IDENTITY'
    bound=batch['binding'];gb=goal['binding'];gf=goal['fields']
    if (bound['status']!='BOUND_SOURCE_LIFE' or gb['status']!='BOUND_SOURCE_LIFE' or
        (bound['local'],bound['native_spawn'])!=(gb['local'],gb['native_spawn'])):return 'UNKNOWN_TARGET_LIFE'
    if not ar or not i[0] or i[5]>=8 or (int(i[1])|int(i[2]))&USEFUL:return 'NOT_OBSERVED_CLOSE_UNARMED_CASE'
    if (f['item'][0]==0 or f['item'][0]!=f['item'][1] or f['goal'][0]!=f['goal'][1] or
        f['attempt'][0]!=f['attempt'][1] or f['deadline'][0]!=f['deadline'][1]):return 'UNKNOWN_NOT_RETAINED_SAME_ATTEMPT'
    weapon=int(gf.get('weapon','0'));mask=1<<(weapon-1) if 1<=weapon<=14 else 0
    if int(gf['entity'])!=f['item'][1] or int(gf.get('kind','-1'))!=0 or not mask&USEFUL:return 'UNKNOWN_USEFUL_TARGET'
    # Exact current Source: ordinary bits15 plus visible close Weapon input
    # cannot retain ownsMovement past the late gate without firstWeaponReady.
    # This is a Source-path proof, not a floor/physical action or pickup ACK.
    if (ar['fields']['refresh']!=[1,0] or d['supply'][:4]!=[1,1,1,1] or
        d['supply'][4:7]!=[15,0,0]):return 'UNKNOWN_NOT_NEW_ORDINARY_PRIORITY_OUTPUT'
    return 'OBSERVED_NEW_CLOSE_FIRST_WEAPON_SOURCE_PRIORITY'

def native_tail(c,batch,driver):
    bound=batch['binding'];g=c['G']
    if bound.get('status')!='BOUND_SOURCE_LIFE':return dict(status='UNKNOWN_NATIVE_LIFE')
    role=batch['key'][1];local=bound['local'];spawn=bound['native_spawn'];start=bound.get('native_interval')
    future=[e for e in g['supplement']['all_extra_events'] if e['role']==role and e['tag']in('CecilGoal','CecilGoalEnd') and e['line']>batch['decision']['line'] and e['binding'].get('local')==local and e['binding'].get('native_spawn')==spawn]
    boundary=min(future,key=lambda e:e['line']) if future else None
    end=c['bind_line'](role,boundary['fields'],boundary['line']) if boundary else None
    # bind_line belongs to the coordinator wrapper, not the base C namespace.
    endtime=end.get('native_interval') if end else None
    rr=[r for r in g['native'][(role,local)] if r['good'] and r['spawn']==spawn]
    out=dict(source_start_interval=start,source_goal_boundary=boundary,boundary_binding=end,
        physical_action_ack=False,pickup_ack=False,clock_conversion=False,
        status='UNKNOWN_NO_WHOLE_GOAL_NATIVE_INTERVAL',gains=[])
    if start is None or endtime is None:return out
    low=Decimal(start['high']);high=Decimal(endtime['low'])
    if high<low:return out
    selected=[r for r in rr if low<=Decimal(str(r['tick']))<=high]
    out.update(status='SUBSEQUENT_SAME_LIFE_OBSERVATIONS_INSIDE_CONSERVATIVE_GOAL_WINDOW',
        observations=[{k:r[k] for k in ('read_serial','tick','health','position','translation','weapons')} for r in selected])
    for old,new in zip(rr,rr[1:]):
        if old['weapons']['owned'] is None or new['weapons']['owned'] is None:continue
        if not low<=Decimal(str(old['tick']))<Decimal(str(new['tick']))<=high:continue
        mask=new['weapons']['owned']&~old['weapons']['owned']&USEFUL
        if mask:out['gains'].append(dict(serials=[old['read_serial'],new['read_serial']],native_ticks=[old['tick'],new['tick']],gained_mask=mask))
    if len(selected)>1:out['endpoint_chord']=sum((a-b)**2 for a,b in zip(selected[0]['position'],selected[-1]['position']))**.5
    return out

def complete(adapter):
    c=adapter.C;g=c['G'];from audit_build030_driver_final import typed
    from trouble034_ram_conclusions import select_native
    dr=[];index={}
    for role in ('botA','botB'):
        for line,text in enumerate(g['logs'][role].splitlines(),1):
            if not text.startswith('[CecilDriverFinalV1]'):continue
            d=typed(c['token'](text));r=dict(role=role,line=line,typed=d)
            key=(role,d['local'],d['tick'],d['actor'],d['gen'][0])
            if key in index:raise ValueError('duplicate same-call Driver')
            index[key]=r;dr.append(r)
    allrows=[];exact=[]
    for b in g['batches']:
        f=b['decision']['fields'];i=f['input']
        if not i[0] or i[5]>=8 or (int(i[1])|int(i[2]))&USEFUL:continue
        k=b['key'];driver=index.get((k[1],k[2],k[5],k[3],k[4]));binding=b['binding']
        goals=[e for e in g['supplement']['all_extra_events'] if e['tag']in('CecilGoal','CecilGoalEnd') and e['role']==k[1] and e['line']<b['decision']['line'] and e['binding'].get('local')==k[2] and e['binding'].get('native_spawn')==binding.get('native_spawn')]
        prior=max(goals,key=lambda e:e['line']) if goals else None
        goal=prior if prior and prior['tag']=='CecilGoal' else None
        row=dict(batch=b,driver=driver,target_goal=goal,status=priority_status(b,driver,goal),native_ack=False)
        if row['status']=='OBSERVED_NEW_CLOSE_FIRST_WEAPON_SOURCE_PRIORITY':
            scope=dict(c);scope['bind_line']=adapter.STATE['scope']['bind_line']
            row['native_after']=native_tail(scope,b,driver);exact.append(row)
        allrows.append(row)
    focuses=[]
    for focus in g['focuses'][:3]:
        l=focus['life'];role=l['role'];local=l['local'];spawn=l['spawn_clock']
        def bound(e):return e['role']==role and e['binding'].get('local')==local and e['binding'].get('native_spawn')==spawn
        rows=[r for r in dr if r['role']==role and r['typed']['local']==local and r['typed']['gen'][0]in l['generations'] and r['typed']['life_link']]
        focuses.append(dict(life=l,native=select_native(g['native'][(role,local)],spawn),
            picker_batches=focus['picker_batches'],source_states=focus['source_life_rows'],
            extra_events=[e for e in g['supplement']['all_extra_events']if bound(e)],
            diagnostic_events=[e for e in g['events']if bound(e)],driver_rows=rows,
            clock_scope='Source life/line binding; endpoint and whole-WPO intervals only. Death Source outside observed Native ending is not interpolated.'))
    counts=dict(picker_batches=len(g['batches']),driver_rows=len(dr),known_close_without_useful=len(allrows),
        samecall_driver=sum(r['driver'] is not None for r in allrows),
        status_counts=dict(collections.Counter(r['status']for r in allrows)),new_source_path_rows=len(exact),
        new_source_actor_lives=len({(r['batch']['key'][1],r['batch']['key'][2],r['batch']['key'][4])for r in exact}),
        supply_active=sum(r['driver']['typed']['post_mode_decoded']['supplyActive']for r in exact),
        safe_reacquire=sum(r['driver']['typed']['safe'][1]==1 for r in exact),
        safe_status=dict(collections.Counter(r['driver']['typed']['safe'][3]for r in exact)),
        nonzero_final_action=sum(any(v!=0 for v in r['driver']['typed']['action'])for r in exact),
        known_goal_native_window=sum(r['native_after']['status'].startswith('SUBSEQUENT')for r in exact),
        later_goal_window_gain_rows=sum(bool(r['native_after']['gains'])for r in exact))
    for name in ('trouble035_ram_priority.py','test_trouble035_ram_priority.py'):
        c['read'](Path(__file__).with_name(name))
    value=dict(status='RAM_ONLY_SOURCE_PRIORITY_AND_NATIVE_TEMPORAL_FOLLOWUP_NOT_ACK',counts=counts,
        all_close_unarmed_batches=allrows,longest_three_no_useful=focuses,
        source_path_argument='Exact035 Header: fresh typed Weapon+same held attempt, close enemy<8, no Useful owned|usable, ordinary active/owns/urgent bits15 with no flags and no flight can pass late closeCombat only via firstWeaponReady. Unlogged internal witnesses are inferred from this exact branch, not individually measured.',
        partial_admission='Only emitted Picker/Driver rows; missing same-call records remain UNKNOWN,1Hz rows are not a complete invocation list',
        causal_pickup_or_physical_ack=False,qualified=False)
    pin=c['save']('new-priority-and-long-lives-ram.json',value)
    receipt=dict(status='COMPLETE_CLOSED035_RAM_FOLLOWUP_NOT_A4_PASS',result_sha256=c['RESULT'],counts=counts,
        input_pins=g['pins'],actual_total_read_bytes=g['read_bytes'],analytic_raw_acquires=1,old_raw_replays=0,
        raw_handles_closed=True,ram_retained=True,output_bytes_before_receipt=g['written'],
        output_pins={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(c['OUT'].iterdir())if p.is_file()})
    final=c['save']('complete035-ram-followup-receipt.json',receipt)
    print('RAM035_FOLLOWUP',json.dumps(dict(counts=counts,focus_pin=pin,receipt=final,output_bytes=g['written'])),flush=True)
    return value
