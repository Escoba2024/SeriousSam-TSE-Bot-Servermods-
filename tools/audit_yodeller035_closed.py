"""One exact closed Yodeller035 audit; no runtime interfaces."""
import ast,hashlib,json,os,collections,re
from pathlib import Path
CASE=Path('/srv/tse-milestone-a-evidence-20261111/nav20-035-yodeller-v3-root-yodeller-20261115-211726')
PACKAGE=Path('/srv/tse-nav20-035-yodeller600-diag0-root-v3-frozen-20261115')
OUT=Path('/srv/tse-yodeller035-closed-audit-evidence-20261115')
E=Path('/srv/tse-cecil-rollout-evidence-20261114')
BUILD=Path('/srv/tse-milestone-a-build-035-20261115')
RESULT='ba0da223d3188da74f0df3775821739dffdfce2399b8931df8f5c5c8afe2c2b8'
RUNNER='28a18d3a368a064e454e0907d44315f3f91913536b2ae69338c744d7aabb5642'
MANIFEST='47432877967beeaa040f371c0d06db9fed9394752cba76cced5126bfaf2d1ef6'
BUILD_MANIFEST='942b4922d1b36b64e96ed998661d2ce23b9ce04508210639bf65425c5c98aa7b'
DLL='e76395a7cb9fc4ea436cc09e9d86b0774f64b8b8df100fa722f4790afe19cae5'
HEADER='a2cf922bdd05058e50b633282a4ebb21be6f25ef01e1482c5dd56b710a8c88d9'
DRIVER='1c081af07169c96b3158307135d0c2b495ea91ce6e957a690a90363d90e914ff'
HOST=E/'navigation035-yodeller-v3-host/receipt.json'
RESTORE=E/'navigation035-yodeller-v3-root-restore.json'
HOST_SHA='01e6234b364ee49f55b9d57aa3e73ef3d050f5ba68f3b388f20afd582e8196a6'
RESTORE_SHA='12612424cb1ab5442db2b1306d18e5bf3286ab22fc150359909cd7679bf74138'
BASE=Path(__file__).with_name('audit_hole031_closed.py')
BASE_SHA='475ddc0a9ea17020873e6733964b3d93abdb8c3a8005e6871fe338db466e0f0e'
C=None
STATE={}
def small(path,cap=2*2**20):
 with os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:data=f.read(cap+1)
 if len(data)>cap:raise ValueError('small input cap')
 return data

def validate_metadata(m):
    r=m['result'];f=m['manifest'];restore=m['restore'];host=m['host'];b=m['build']
    if (r['status']!='PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY' or r['errors'] or
        r['controller_sha256']!=RUNNER or r['candidate_sha256']!=DLL or r['map_key']!='yodeller' or
        r['diagnostics_enabled'] is not False or r['functional_pass'] is not False or r['qualified'] is not False or
        set(r['cleanup'])!={'server','botA','botB','vanilla'} or not all(v['closed'] is True for v in r['cleanup'].values())):
        raise ValueError('exact035 closed result')
    if (restore['status']!='PASS_RESTORE' or restore['result_sha256']!=RESULT or
        restore['case_result']!=str(CASE/'result.json') or restore['counts']!={'files':640,'absences':0,'closed_logs':4} or
        restore['parent_returncode']!=0 or restore['closed_log_scope_complete'] is not True or
        set(restore['started_roles'])!={'server','botA','botB','vanilla'}):raise ValueError('exact035 Root restore')
    if (host['status']!='PASS_HOST_OBSERVATION_ONLY' or host['child_exit_code']!=0 or host['child_reaped'] is not True or
        host['errors'] or host['signals_sent']!=0 or host['automatic_retries']!=0):raise ValueError('exact035 host observation')
    c=f['comparison'];mc=f['map_case']
    if (c['order']!=['035'] or c['map']!='yodeller' or c['seconds']!=600 or c['diagnostics']!=0 or
        c['observer_fps']!=20 or c['hard_difficulty']!=2 or mc['bot_count']!=8 or mc['bot_tier']!=3 or
        any(o['automatic_retry'] is not False or o['automatic_sequence'] is not False for o in (c,mc)) or
        f['candidate']['build_manifest_sha256']!=BUILD_MANIFEST or f['candidate']['dll_sha256']!=DLL or
        b['dll_sha256']!=DLL or b['build_ok'] is not True or b['qualified'] is not False):raise ValueError('exact035 condition/build')
    return True

PAIRS=[
 ('One bounded closed Hole031 audit','One bounded closed Yodeller035 audit'),
 ('/srv/tse-milestone-a-evidence-20261111/nav20-031-hole-root-hole-20261115-141204',str(CASE)),
 ('/srv/tse-nav20-031-hole600-diag1-root-frozen-20261115',str(PACKAGE)),
 ('/srv/tse-hole031-closed-audit-evidence-20261115',str(OUT)),
 ('7e581f512eaf9717221d18eeb9b5091e11ed72d83b8960d282858c3bc00262a4',RESULT),
 ("map='hole'","map='yodeller'"),
 ('/srv/tse-cecil-rollout-evidence-20261114/navigation031-hole-host/receipt.json',str(HOST)),
 ('/srv/tse-cecil-rollout-evidence-20261114/navigation031-hole-root-restore.json',str(RESTORE)),
 ('OUTPUT=5*1024*1024','OUTPUT=8*1024*1024'),
 ('5MiB output/8GiB+64MiB reserve','8MiB output/8GiB+64MiB reserve'),
 ('COMPLETE_CANONICAL_HOLE031_CLOSED_AUDIT_ONLY','COMPLETE_CANONICAL_YODELLER035_CLOSED_AUDIT_ONLY')]
def digest(raw):return hashlib.sha256(raw).hexdigest()
def adapt(raw,reverse=False):
 if not reverse and digest(raw)!=BASE_SHA:raise ValueError('exact existing reader Source')
 s=raw.decode()
 for a,b in(reversed(PAIRS)if reverse else PAIRS):
  if reverse:a,b=b,a
  if s.count(a)!=1:raise ValueError('unique reader anchor')
  s=s.replace(a,b,1)
 out=s.encode();ast.parse(out)
 if reverse and digest(out)!=BASE_SHA:raise ValueError('whole reader inverse')
 return out

def preflight():
 names=['inventory.jsonl','session-health.jsonl','read-attempts.jsonl']+[r+'-closed.log'for r in ('server','botA','botB','vanilla')]
 sizes={n:(CASE/n).stat().st_size for n in names};logs=[v for n,v in sizes.items()if n.endswith('-closed.log')]
 if max(sizes.values())>64*2**20 or sum(sizes.values())>128*2**20 or max(logs)>16*2**20 or sum(logs)>32*2**20:raise ValueError('input stat cap')
 paths={'result':CASE/'result.json','manifest':CASE/'source-manifest.json','restore':RESTORE,'host':HOST,'build':BUILD/'manifest.json'}
 raw={p:small(p)for p in paths.values()};meta={k:json.loads(raw[p])for k,p in paths.items()}
 validate_metadata(meta)
 pins={paths['result']:RESULT,paths['manifest']:MANIFEST,RESTORE:RESTORE_SHA,HOST:HOST_SHA,paths['build']:BUILD_MANIFEST,CASE/'controller-source.py':RUNNER,PACKAGE/'source-manifest.json':MANIFEST,BUILD/'Sources/Game/BotSupplyNative.h':HEADER,BUILD/'Sources/Game/BotDriver.cpp':DRIVER}
 for p,h in pins.items():
  if p not in raw:raw[p]=small(p)
  if digest(raw[p])!=h:raise ValueError('exact Source/metadata pin '+str(p))
 st=os.statvfs(OUT.parent);free=st.f_bavail*st.f_frsize
 if OUT.exists()or free<2**33+2**26+8*2**20:raise ValueError('fresh output/fixed reserve')
 return dict(sizes=sizes,raw_bytes=sum(sizes.values()),output_cap=8*2**20,free_bytes=free,pins={str(p):digest(v)for p,v in raw.items()}),raw

def namespace(cache):
 raw=small(BASE);changed=adapt(raw)
 if adapt(changed,True)!=raw:raise ValueError('inverse')
 scope={'__name__':'closed_yodeller035_reader','__file__':str(Path(__file__).resolve())}
 exec(compile(changed,str(BASE)+'[Yodeller035 exact]', 'exec'),scope)
 for p,data in {**cache,BASE:raw}.items():scope['account'](p,data);scope['G']['cache'][str(p)]=data
 STATE.update(parent_reader_sha256=digest(raw),adapted_reader_sha256=digest(changed),whole_inverse=True)
 return scope

def private_kill_custody():
 from yodeller035_kill_tokens import parse_kills
 g=C['G'];names=collections.defaultdict(set)
 for row in g['queries']:
  for k,v in row['query'].items():
   if re.fullmatch(r'player_[0-8]',k):names[v].add(int(k.split('_')[1]))
 events=parse_kills(g['logs']['server'],names)
 tokens=sorted({t for e in events for t in e['tokens']})
 value=dict(scope='ORIGINAL_SERVER_ONLY_EXACT_TOKENS_PRIVATE_NO_NORMALIZATION',query_name_slots={k:sorted(v)for k,v in names.items()},events=events,unique_tokens=[dict(token=t,latin1_hex=t.encode('latin1').hex(),exact_query_slots=sorted(names.get(t,set())),caret_codes=re.findall(r'\^.',t),nonascii=any(ord(c)>127 for c in t),trailing_space=bool(t and t[-1].isspace()))for t in tokens],counts=dict(collections.Counter(e['kind']for e in events)),killer_joined=sum(e['killer_slot']is not None for e in events if len(e['tokens'])==2),victim_joined=sum(e['victim_slot']is not None for e in events),total=len(events),native_damage_life_chain='UNKNOWN')
 C['save']('private-server-kill-tokens.json',value);g['kill_tokens']=value
 return value

def ram_context():
 g=C['G'];all_lives=[l for ll in g['lives'].values()for l in ll];ranking=[];special=[]
 for l in all_lives:
  if l['first_alive_observed_tick']is None:continue
  end=l['first_useful_observed_tick']if l['first_useful_observed_tick']is not None else l['last_alive_observed_tick']
  no_useful=end-l['first_alive_observed_tick']
  rr=[r for r in g['native'][(l['role'],l['local'])]if r['good']and r['spawn']==l['spawn_clock']]
  ranking.append(dict(life=l,no_useful_prefix_observed_seconds=no_useful,prefix_ends_with='first_useful_observation'if l['first_useful_observed_tick']is not None else l['ending'],owned_counts=dict(collections.Counter(str(r['weapons']['owned'])for r in rr)),current_counts=dict(collections.Counter(str(r['weapons']['current'])for r in rr)),health_range=[min(r['health']for r in rr),max(r['health']for r in rr)]if rr else None,native_fire_by_current=dict(collections.Counter(str(r['weapons']['current'])for r in rr if r['native_ranged_fire']))))
 ranking.sort(key=lambda x:x['no_useful_prefix_observed_seconds'],reverse=True)
 for x in ranking[:5]:
  l=x['life'];role=l['role'];gens=l['generations'];ss=[r for r in g['source'][role]if int(r['local'])==l['local']and int(r.get('generation',0))in gens]
  x['source_state_rows']=[r for r in ss if r['tag']=='CecilState']
  x['source_goal_events']=[e for e in g['supplement']['all_extra_events']if e['role']==role and e['binding'].get('local')==l['local']and e['binding'].get('native_spawn')==l['spawn_clock']]
  x['source_state_motion_count']=sum(any(float(r.get(k,0))!=0 for k in ('move','strafe','up'))for r in x['source_state_rows'])
 special=[e for e in g['events']if e['tag'].startswith(('CecilFlight','CecilBouncer','CecilTele','CecilJump'))or e['tag']in ('CecilGroundReplan','CecilImportantOriginRecovery','CecilHopCheckpoint')]
 value=dict(scope='ALL_NATIVE_LIVES_PREFIX_GAPS_AND_SOURCE_CONTEXT_NO_CLOCK_FUSION',all_life_count=len(all_lives),longest_prefix_gaps=ranking[:10],specialty_observed_rows=special,specialty_marker_counts=dict(collections.Counter(e['tag']for e in special)),diagnostics0=True,missing_diagnostic_reason='UNKNOWN_NOT_DISABLED_BEHAVIOR',shot_damage_ack=False,continuous_route_or_trigger_ack=False)
 C['save']('functional-ram-context.json',value);g['ram_context']=value
 return value

def finalize():
 g=C['G'];sources=['audit_yodeller035_closed.py','yodeller035_kill_tokens.py','test_yodeller035_closed_reader.py','test_yodeller035_kill_tokens.py']
 for name in sources:C['read'](Path(__file__).with_name(name))
 artifacts={}
 for p in sorted(OUT.iterdir()):
  if p.is_file():
   raw=small(p,8*2**20);artifacts[p.name]=dict(bytes=len(raw),sha256=digest(raw))
 receipt=dict(status='COMPLETE_YODELLER035_CLOSED_FUNCTIONAL_OBSERVATION_ONLY',qualified=False,a4_pass=False,original_status_unchanged=g['report']['status'],case=str(CASE),result_sha256=RESULT,stat_admission=STATE['admission'],reader_inverse=STATE,source_input_pins=g['pins'],actual_input_bytes=g['sizes'],actual_total_read_bytes=g['read_bytes'],output_bytes_before_receipt=g['written'],output_pins=artifacts,analytic_raw_passes=1,old_raw_replays=0,all_native_raw_handles_closed=True,source_native_clocks_separate=True,diag0_gaps_unknown=True)
 pin=C['save']('final-yodeller035-receipt.json',receipt)
 print('YODELLER035_FINAL',json.dumps(dict(pin=pin,lives=g['summary']['observed_lives'],gains=g['summary']['useful_gain_events'],longest_gap=g['ram_context']['longest_prefix_gaps'][0]['no_useful_prefix_observed_seconds'],server_kills=g['kill_tokens']['counts'],name_joins=[g['kill_tokens']['killer_joined'],g['kill_tokens']['victim_joined']],output_bytes=g['written'],input_bytes=g['read_bytes'])),flush=True)
 return receipt

def main():
 global C
 admission,cache=preflight();STATE['admission']=admission;C=namespace(cache)
 print('ADMITTED_YODELLER035',json.dumps(admission),flush=True)
 C['acquire']();C['derive']();C['outputs']();C['G']['supplement']=C['supplement']();C['behavior_hazards']();private_kill_custody();ram_context();finalize()
if __name__=='__main__':main()
