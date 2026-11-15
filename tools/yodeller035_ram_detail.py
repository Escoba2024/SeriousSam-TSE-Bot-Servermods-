"""Small retained-RAM supplement; never opens Native streams."""
import collections,math,re

def stationary_witness(rows):
    anchor=None;prior=None;best=None
    for r in rows:
        gap=r['tick']-prior['tick']if prior else 0
        if anchor is None or not 0<gap<=.5 or math.dist(anchor['position'],r['position'])>1:anchor=r
        elif best is None or r['tick']-anchor['tick']>best['seconds']:
            best=dict(seconds=r['tick']-anchor['tick'],first=anchor,last=r)
        prior=r
    return best

def complete(C):
    g=C['G'];station=[];extra=[]
    all_lives=[l for ll in g['lives'].values()for l in ll]
    for l in sorted(all_lives,key=lambda l:l['geometry']['stationary_1m_span'],reverse=True)[:3]:
        rr=[r for r in g['native'][(l['role'],l['local'])]if r['good']and r['spawn']==l['spawn_clock']]
        witness=stationary_witness(rr)
        if witness and witness['seconds']!=l['geometry']['stationary_1m_span']:raise ValueError('same inherited geometry result required')
        station.append(dict(life=l,witness=witness,source_states=[r for r in g['source'][l['role']]if r['tag']=='CecilState'and int(r['local'])==l['local']and int(r.get('generation',0))in l['generations']],source_time_is_not_native_time=True))
    tags={'CecilAirRecovery','CecilInteraction','CecilGoalBudget','CecilReacquireSupport','CecilGravity'}
    for role,text in g['logs'].items():
        if role not in ('botA','botB'):continue
        for line,t in enumerate(text.splitlines(),1):
            tag=t.partition(']')[0][1:]
            if tag in tags:
                event=C['source_event'](role,line,t);f=event['fields']
                event['binding']=g['bind'](role,f,line)if 'local'in f or tag=='CecilAirRecovery'and 'entity'in f else dict(status='UNKNOWN_NO_DECLARED_LOCAL_OR_PLAYER_ACTOR')
                extra.append(event)
    names=g['kill_tokens']['query_name_slots'];tokens=g['kill_tokens']['unique_tokens']
    relation=[]
    for entry in tokens:
        matches=[dict(query_name=name,slots=slots)for name,slots in names.items()if entry['token']=='^o'+name+'^r']
        relation.append(dict(raw_token=entry['token'],exact_decorated_query_matches=matches))
    v=dict(status='CLOSED_RETAINED_RAM_DETAIL_ONLY',stationary=station,additional_source_context=extra,additional_marker_counts=dict(collections.Counter(e['tag']for e in extra)),kill_token_relation=relation,all_tokens_have_one_unique_query_decoration_match=all(len(x['exact_decorated_query_matches'])==1 and len(x['exact_decorated_query_matches'][0]['slots'])==1 for x in relation),decoration_scope='Observed exact case correspondence only; no general stripping, no authoritative kill-slot reassignment. Retail implementation of decoration has not been proved here.',strict_killer_joins=g['kill_tokens']['killer_joined'],strict_victim_joins=g['kill_tokens']['victim_joined'],diag0=True,no_new_raw_reads=True)
    C['save']('ram-context-detail-v2.json',v);g['detail']=v
    return v
