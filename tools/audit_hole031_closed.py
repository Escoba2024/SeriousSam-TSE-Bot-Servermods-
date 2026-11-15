"""One bounded closed Hole031 audit; no process/Native/controller interfaces."""
import ast,collections,copy,hashlib,importlib.util,json,math,os,re,sys
from pathlib import Path
from decimal import Decimal
sys.dont_write_bytecode=True
import navigation_life_summary as life
import picker_custody_audit as picker
from audit_reset031_picker_closed import binding_prefix,geometry
CASE=Path('/srv/tse-milestone-a-evidence-20261111/nav20-031-hole-root-hole-20261115-141204')
PACKAGE=Path('/srv/tse-nav20-031-hole600-diag1-root-frozen-20261115')
OUT=Path('/srv/tse-hole031-closed-audit-evidence-20261115')
RESULT='7e581f512eaf9717221d18eeb9b5091e11ed72d83b8960d282858c3bc00262a4'
LIMIT=128*1024*1024;OUTPUT=5*1024*1024
G={'pins':{},'sizes':{},'cache':{},'read_bytes':0,'written':0}
EVENTS={'CecilReacquireDecision','CecilGroundReplan','CecilImportantOriginRecovery','CecilHopCheckpoint','CecilSupplyDiagUnavailable','CecilSupplyDiagTerminal','CecilPickup','CecilSupplyGoal','CecilSupplyGoalEnd','CecilSupplyDiagCandidate','CecilSupplyDiagSelection'}

def opened(path):return os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')
def account(path,raw):
 G['read_bytes']+=len(raw)
 if G['read_bytes']>LIMIT:raise ValueError('128MiB actual aggregate read cap')
 G['pins'][str(path)]=hashlib.sha256(raw).hexdigest();G['sizes'][str(path)]=len(raw)
def read(path,cap=2*1024*1024):
 key=str(path)
 if key in G['cache']:return G['cache'][key]
 with opened(path)as f:raw=f.read(cap+1)
 if len(raw)>cap:raise ValueError('per-stream/small input cap')
 account(path,raw);G['cache'][key]=raw;return raw

def load(path):return json.loads(read(path))
def rows(path):
 total=0;h=hashlib.sha256()
 with opened(path)as f:
  for raw in f:
   total+=len(raw)
   if total>64*1024*1024 or len(raw)>262144:raise ValueError('64MiB stream/line cap')
   G['read_bytes']+=len(raw)
   if G['read_bytes']>LIMIT:raise ValueError('128MiB actual total read cap')
   h.update(raw);yield json.loads(raw)
 G['pins'][str(path)]=h.hexdigest();G['sizes'][str(path)]=total

def save(name,value):
 wire=(json.dumps(value,allow_nan=False,sort_keys=True,separators=(',',':'))+'\n').encode()
 st=os.statvfs(OUT.parent)
 if G['written']+len(wire)>OUTPUT or st.f_bavail*st.f_frsize<2**33+2**26+len(wire):raise ValueError('5MiB output/8GiB+64MiB reserve')
 with os.fdopen(os.open(OUT/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(wire);f.flush();os.fsync(f.fileno())
 G['written']+=len(wire)
 return dict(bytes=len(wire),sha256=hashlib.sha256(wire).hexdigest())

EXTRA_EVENTS={'CecilGoal','CecilGoalEnd','CecilGoalBudget','CecilReacquireSupport','CecilMotionProbe'}

def event_tag(tag):return tag in EVENTS or tag in EXTRA_EVENTS or tag.startswith(('CecilFlight','CecilBouncer','CecilTele','CecilJump'))

def token(line):
 return dict(re.findall(r'(\w+)=([^\s]+)',line))
def source_event(role,line,text):
 tag=text.partition(']')[0][1:];return dict(role=role,line=line,tag=tag,fields=token(text))

def acquire():
 if OUT.exists():raise ValueError('fresh output required')
 # Stat only beforehand; the three heavy streams plus final logs justify128MiB,
 # not a transferred historical64MiB aggregate admission.
 names=['inventory.jsonl','read-attempts.jsonl','session-health.jsonl']+[r+'-closed.log'for r in ['server','botA','botB','vanilla']]
 sizes={n:(CASE/n).stat().st_size for n in names}
 if any(n>64*1024*1024 for n in sizes.values())or sum(sizes.values())>LIMIT:raise ValueError('stat input budget')
 G['prescan_sizes']=sizes
 report=load(CASE/'result.json');manifest=load(CASE/'source-manifest.json');registry=load(CASE/'registry.json');controller=read(CASE/'controller-source.py')
 if (G['pins'][str(CASE/'result.json')]!=RESULT or report['status']!='PASS_LIMITED_REACQUIRE_DIAGNOSTIC_OBSERVATION_ONLY' or report['errors'] or not all(r['closed']for r in report['cleanup'].values())):raise ValueError('exact closed technical result')
 if hashlib.sha256(controller).hexdigest()!=report['controller_sha256']:raise ValueError('executed controller differs')
 for name in ['a4_ordered_memory_v3.py','audit_a4_ordered_memory_v3.py','a4_canonical_native_groups.py','audit_a4_native_fire_observer_v2.py','a4_fire_observer_v2.py','adapter_policy.py','reset_policy.py']:
  if hashlib.sha256(read(PACKAGE/name)).hexdigest()!=manifest['draft_source_sha256'][name]:raise ValueError('unchanged archived helper pin')
 if hashlib.sha256(read(Path(__file__).with_name('navigation_life_summary.py'))).hexdigest()!='6f4a2f150368ddddefb530afa2b40ba210a3d648dc6b323fe41430bbb4b9b65c':raise ValueError('unchanged life helper')
 raw=list(rows(CASE/'inventory.jsonl'));samples=life.unpack_rows(raw);del raw
 G.update(report=report,manifest=manifest,registry=registry,samples=samples)
 attempts=list(rows(CASE/'read-attempts.jsonl'));G['attempts']=attempts
 mapping=report['actual_slot_mapping'];identity=registry['native_fire_epoch']['server_identity'];contract=report['native_group_contract']
 G['summary']=life.validated_summary(samples,registry,mapping,identity,contract,attempts)
 print('VALIDATED_LIFE',json.dumps({k:v for k,v in G['summary'].items()if k!='lives'}),flush=True)
 logs={r:read(CASE/(r+'-closed.log'),64*1024*1024).decode('latin1')for r in ['server','botA','botB','vanilla']};G['logs']=logs
 health={'rows':0,'spawn_values':collections.defaultdict(set),'session_hashes':set()}
 for row in rows(CASE/'session-health.jsonl'):
  health['rows']+=1
  for role,v in row['roles'].items():health['spawn_values'][role].add(v['spawn_value']);health['session_hashes'].add(v['session156_sha256'])
 health['spawn_values']={k:sorted(v)for k,v in health['spawn_values'].items()};health['session_hashes']=sorted(health['session_hashes']);G['health']=health
 G['queries']=load(CASE/'queries.json');G['resources']=load(CASE/'resource-usage.json');G['active']=load(CASE/'active-evidence.json')
 print('ACQUIRED_ONCE',G['read_bytes'],flush=True)

def derive():
 report=G['report'];registry=G['registry'];mapping=report['actual_slot_mapping'];samples=G['samples'];logs=G['logs'];summary=G['summary']
 import a4_ordered_memory_v3 as ordered
 from audit_a4_native_fire_observer_v2 import source_rows,good_player,stamp,native_fire
 canonical=[s for s in samples if s['memory_observation']['phase']=='gameplay'and s['native_group_provenance']['name']in report['native_group_contract']['fixed_sources'].values()]
 own=set(mapping['botA']+mapping['botB']);expected={r['slot']:r for r in registry['players']if r['slot']in own}
 source={r:source_rows(logs[r])for r in ['botA','botB']}
 bindings,prefixsha=binding_prefix(ordered.audit,read(PACKAGE/'audit_a4_ordered_memory_v3.py').decode())
 native={};bound={};events=[];typed=[];tags={};driver={};spawns={};lives={};slots=[]
 for role in ['botA','botB']:
  tags[role]=collections.Counter();driver[role]={}
  for n,text in enumerate(logs[role].splitlines(),1):
   if not text.startswith('[')or']'not in text:continue
   tag=text.partition(']')[0][1:];tags[role][tag]+=1
   p=picker.parse(text)
   if p is not None:p.update(role=role,phase=0,line=n);typed.append(p)
   if event_tag(tag)and tag not in EXTRA_EVENTS:events.append(source_event(role,n,text))
   if tag=='CecilDriverFinalV1':
    f=token(text);driver[role][(int(f['local']),int(f['tick']),int(f['actor']),int(f['gen'][1:-1].split(',')[0]))]=n
  for local,slot in enumerate(mapping[role]):
   key=(role,local);ref=expected[slot]
   j=bindings(source[role],[(s['memory_observation']['read_serial'],s)for s in canonical],local,slot,ref);bound[key]=j
   ss=[r for r in source[role]if int(r['local'])==local and int(r.get('entity',0))==ref['entity_id']];spawns[key]=[r for r in ss if r['tag']=='CecilSpawn']
   ll=[copy.deepcopy(l)for l in summary['lives']if l['slot']==slot];lives[key]=ll
   rr=[]
   for s in canonical:
    for p in s['players']:
     if p['slot']!=slot:continue
     clock=p.get('spawned_tick',0);l=next((l for l in ll if l['spawn_clock']==clock),None)
     good=good_player(p,ref,s['game_tick'])and l is not None and(l['first_dead_observed_tick']is None or s['game_tick']<l['first_dead_observed_tick'])
     w=p.get('weapons')or{}
     rr.append(dict(read_serial=s['memory_observation']['read_serial'],tick=s['game_tick'],spawn=clock,entity=p['entity_id'],world=p['world_pointer'],good=good,health=p.get('health'),position=p.get('placement',[])[:3],translation=p.get('current_translation_absolute'),last_buttons=p.get('last_buttons'),physics_flags=p.get('physics_flags'),weapons={k:w.get(k)for k in ['owned','current','wanted','has_ammo','fire_requested']},native_ranged_fire=bool(good and native_fire(p))))
   native[key]=rr
   for l in ll:
    l['geometry']=geometry(rr,l)
    observations=[r for r in rr if r['good']and r['spawn']==l['spawn_clock']]
    l['role']=role;l['local']=local
    l['generations']=[g for g,clock in j['joins'].items()if clock==l['spawn_clock']]
    l['y_range']=[min(r['position'][1]for r in observations),max(r['position'][1]for r in observations)]if observations else None
    l['native_ranged_fire_samples']=sum(r['native_ranged_fire']for r in observations)
   evidence=ordered.audit.slot_evidence(source[role],[(s['memory_observation']['read_serial'],s)for s in canonical],local,slot,ref)
   slots.append(dict(role=role,local=local,slot=slot,lives=len(ll),useful_possession_lives=sum(l['first_useful_observed_tick']is not None for l in ll),useful_gains=sum(l['useful_gain_events']for l in ll),bound_native_fire=evidence,max_stationary_1m=max((l['geometry']['stationary_1m_span']for l in ll),default=0),max_exact_nulltranslation=max((l['geometry']['exact_position_zero_translation_span']for l in ll),default=0),position_chords=sum(l['geometry']['observed_position_chords']for l in ll),y_range=[min(r['position'][1]for r in rr if r['good']),max(r['position'][1]for r in rr if r['good'])],source_state_counts=dict(collections.Counter(r.get('liquid','UNKNOWN')for r in ss if r['tag']=='CecilState'and r.get('alive')=='1')),source_life_bindings={str(g):clock for g,clock in j['joins'].items()},invalid_generations=j['invalid']))
 G.update(native=native,bound=bound,source=source,lives=lives,slots=slots,source_spawns=spawns)
 def bind(role,f,line):
  # entity is PLAYER only on event families without a local; item diagnostic
  # entity fields must never be used to identify a player.
  if 'local'in f:local=int(f['local'])
  else:
   local=next((local for local,slot in enumerate(mapping[role])if expected[slot]['entity_id']==int(f.get('entity',0))),None)
  if local not in range(4):return dict(status='UNKNOWN_LOCAL_OR_ACTOR')
  key=(role,local);slot=mapping[role][local]
  before=[r for r in spawns[key]if r['line']<=line]
  spawn=max(before,key=lambda r:r['line'])if before else None
  gen=int(f['generation'])if 'generation'in f else(int(spawn['generation'])if spawn else None)
  if spawn is None or gen!=int(spawn['generation'])or int(spawn['entity'])!=expected[slot]['entity_id']:return dict(status='UNKNOWN_SOURCE_SPAWN_CONTEXT',local=local,slot=slot,generation=gen)
  clock=bound[key]['joins'].get(gen);matches=[l for l in lives[key]if l['spawn_clock']==clock]
  out=dict(status='BOUND_SOURCE_LIFE'if len(matches)==1 else'UNKNOWN_NATIVE_LIFE',local=local,slot=slot,generation=gen,source_spawn_line=spawn['line'],native_spawn=clock)
  if len(matches)!=1:return out
  l=matches[0];out['native_interval']=None
  if 'native_time'in f and f.get('native_time_valid','1')=='1':
   value=Decimal(f['native_time']);digits=len(f['native_time'].split('.')[1])if'.'in f['native_time']else 0;half=Decimal(1).scaleb(-digits)/2;lo,hi=value-half,value+half
   if l['last_alive_observed_tick']is not None and stamp(clock)<=lo<=hi<=stamp(l['last_alive_observed_tick']):out['native_interval']=dict(low=str(lo),high=str(hi),kind='OWN_EVENT_EXACT_PRINT_ROUNDING')
  elif 'tick'in f:
   tick=int(f['tick']);wpo=[r for r in source[role]if int(r['local'])==local and int(r.get('generation',0))==gen and r['tag']=='CecilWeaponObserve']
   a=[r for r in wpo if int(r['tick'])<=tick];z=[r for r in wpo if int(r['tick'])>=tick]
   if a and z:
    a=max(a,key=lambda r:int(r['tick']));z=min(z,key=lambda r:int(r['tick']));lo=Decimal(a['native_time'])-Decimal('.0000005');hi=Decimal(z['native_time'])+Decimal('.0000005')
    if l['last_alive_observed_tick']is not None and stamp(clock)<=lo<=hi<=stamp(l['last_alive_observed_tick']):out['native_interval']=dict(low=str(lo),high=str(hi),kind='WHOLE_WPO_INTERVAL',wpo_lines=[a['line'],z['line']])
  return out
 for e in events:e['binding']=bind(e['role'],e['fields'],e['line'])
 batches=picker.assemble(typed)
 for b in batches:
  role=b['key'][1];d=b['decision'];b['binding']=bind(role,d['fields'],d['line']);t=(b['key'][2],b['key'][5],b['key'][3],b['key'][4])
  if t in driver[role]and b['arbitration']is None:raise ValueError('known admitted DriverFinal missing Arbitration')
 G.update(events=events,batches=batches,tags=tags,prefix_sha=prefixsha,bind=bind)
 return bind

def outputs():
 ls=[l for ll in G['lives'].values()for l in ll]
 never=sorted((l for l in ls if l['first_alive_observed_tick']is not None and l['first_useful_observed_tick']is None),key=lambda l:l['observed_alive_span_seconds'],reverse=True)
 stationary=sorted(ls,key=lambda l:l['geometry']['stationary_1m_span'],reverse=True)
 focuses=[]
 for l in never[:5]:
  role=l['role'];local=l['local'];gens=l['generations'];rr=[r for r in G['native'][(role,local)]if r['spawn']==l['spawn_clock']and r['good']]
  bb=[b for b in G['batches']if b['key'][1:3]==[role,local]and b['binding'].get('native_spawn')==l['spawn_clock']]
  ee=[e for e in G['events']if e['role']==role and e['binding'].get('local')==local and e['binding'].get('native_spawn')==l['spawn_clock']]
  focuses.append(dict(life=l,alive_samples=len(rr),owned_counts=dict(collections.Counter(str(r['weapons']['owned'])for r in rr)),current_counts=dict(collections.Counter(str(r['weapons']['current'])for r in rr)),picker_batches=[dict(key=b['key'],decision=b['decision'],origin=b['origin'],attempts=b['attempts'],arbitration=b['arbitration'],binding=b['binding'])for b in bb],source_events=ee,source_life_rows=[r for r in G['source'][role]if int(r['local'])==local and int(r.get('generation',0))in gens],first_last_native=[rr[0],rr[-1]]if rr else[]))
 closed={r:dict(sha256=G['pins'][str(CASE/(r+'-closed.log'))],bytes=G['sizes'][str(CASE/(r+'-closed.log'))],syncbad=len(re.findall('SYNCBAD',text)),bad_disconnect=len(re.findall('Too many bad syncs',text)),crash_markers=len(re.findall(r'Segmentation fault|Unhandled exception|Fatal error',text,re.I)))for r,text in G['logs'].items()}
 compact=[dict(key=b['key'],lines=[b['decision']['line'],b['origin']['line']]+[a['line']for a in b['attempts']]+([b['arbitration']['line']]if b['arbitration']else[]),binding=b['binding'],reason=b['decision']['fields']['reason'],attempt_ends=[a['fields']['end']for a in b['attempts']],arbitration_taken=b['arbitration']['fields']['taken']if b['arbitration']else None)for b in G['batches']]
 reacquire=[e for e in G['events']if e['tag']=='CecilReacquireDecision']
 G['focuses']=focuses
 report=dict(status='CLOSED_FUNCTIONAL_OBSERVATION_AUDIT_ONLY_NOT_A4_QUALIFICATION',original_status_unchanged=G['report']['status'],result_sha256=RESULT,qualified=False,a4_pass=False,map='hole',life_summary=G['summary'],slots=G['slots'],source_tag_counts={r:dict(c)for r,c in G['tags'].items()},picker_counts=dict(rows=dict(collections.Counter(r['tag']for b in G['batches']for r in [b['decision'],b['origin']]+b['attempts']+([b['arbitration']]if b['arbitration']else[]))),batches=len(G['batches']),binding=dict(collections.Counter(b['binding']['status']for b in G['batches'])),reasons=dict(collections.Counter(b['decision']['fields']['reason']for b in G['batches'])),attempt_ends=dict(collections.Counter(a['fields']['end']for b in G['batches']for a in b['attempts']))),reacquire_counts=dict(total=len(reacquire),reasons=dict(collections.Counter(e['fields']['reason']for e in reacquire)),binding=dict(collections.Counter(e['binding']['status']for e in reacquire))),all_reacquire=reacquire,other_recovery_events=[e for e in G['events']if e['tag']in ['CecilGroundReplan','CecilImportantOriginRecovery','CecilHopCheckpoint']or e['tag'].startswith(('CecilFlight','CecilBouncer','CecilTele','CecilJump'))],longest_no_useful=never[:10],longest_stationary=stationary[:10],closed_logs=closed,session_health=G['health'],resources=G['resources'],binding_prefix_ast_sha256=G['prefix_sha'],hazard_teleporter_lava_jumppad_acceptance='UNKNOWN; no per-transition causal physics/trigger witness created by endpoint movement or proposals',damage_hit_ack='UNKNOWN; native ranged fire flags and kills do not prove shot/damage chains')
 OUT.mkdir(mode=0o700)
 files={};files['summary.json']=save('summary.json',report);files['all-lives.json']=save('all-lives.json',ls);files['all-picker-batch-bindings.json']=save('all-picker-batch-bindings.json',compact);files['long-no-useful-focus.json']=save('long-no-useful-focus.json',focuses)
 receipt=dict(status='COMPLETE_BOUNDED_CLOSED_AUDIT_NO_GAMEPLAY_QUALIFICATION',result_sha256=RESULT,reader_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),prescan_sizes=G['prescan_sizes'],input_pins=G['pins'],input_bytes=G['sizes'],actual_total_read_bytes=G['read_bytes'],read_limit=LIMIT,output_limit=OUTPUT,written_before_receipt=G['written'],files=files,qualified=False,a4_pass=False,continuous_physics_proven=False)
 files['final-receipt.json']=save('final-receipt.json',receipt)
 print('FINAL',json.dumps({'files':files,'lives':len(ls),'max_no_useful':never[0]['observed_alive_span_seconds']if never else None,'slots':G['slots'],'reacquire':report['reacquire_counts'],'picker':report['picker_counts'],'output_bytes':G['written'],'read_bytes':G['read_bytes']},allow_nan=False),flush=True)

def supplement():
 # This final small file adds actual Goal/GoalEnd and support custody. Earlier
 # checkpoints remain unchanged; no Native stream is opened again.
 extra=[]
 for role in ['botA','botB']:
  for n,text in enumerate(G['logs'][role].splitlines(),1):
   tag=text.partition(']')[0][1:]
   if tag in EXTRA_EVENTS:
    e=source_event(role,n,text);e['binding']=G['bind'](role,e['fields'],n);extra.append(e)
 focuses=[]
 for f in G['focuses'][:2]:
  l=f['life'];role=l['role'];local=l['local'];bb=f['picker_batches']
  e=[e for e in extra if e['role']==role and e['binding'].get('local')==local and e['binding'].get('native_spawn')==l['spawn_clock']]
  focuses.append(dict(role=role,local=local,life=l,all_goal_support_events=e,picker_counts=dict(reasons=dict(collections.Counter(b['decision']['fields']['reason']for b in bb)),gates={str(k):v for k,v in collections.Counter(tuple(b['decision']['fields']['gates'])for b in bb).items()},attempts=dict(collections.Counter(a['fields']['end']for b in bb for a in b['attempts'])),arbitration_taken=sum(bool(b['arbitration']and b['arbitration']['fields']['taken'])for b in bb)),source_end_reasons=dict(collections.Counter(e['fields'].get('reason','UNKNOWN')for e in e if e['tag']=='CecilGoalEnd'))))
 query_frags=[]
 for row in G['queries']:
  q=row['query']
  # Query values are net scoreboard observations, not authoritative kill events.
  frags={k:v for k,v in q.items()if k.startswith('frags_')}
  if frags:query_frags.append(dict(elapsed=row['elapsed'],frags=frags))
 value=dict(status='FINAL_SOURCE_EVENT_CUSTODY_ADDENDUM_NO_RAW_REPLAY',all_extra_events=extra,focus=focuses,query_net_frags_first_last=[query_frags[0],query_frags[-1]]if query_frags else[],actual_kill_event_attribution='See final behavior-hazards.json for actual unclocked kill/death console records; life/damage chains remain UNKNOWN',reacquire_native_time_bound=sum(e['binding'].get('native_interval')is not None for e in G['events']if e['tag']=='CecilReacquireDecision'),input_pins=G['pins'],input_bytes=G['sizes'],actual_total_read_bytes=G['read_bytes'],reader_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),prior_checkpoints_preserved=True,qualified=False)
 result=save('source-custody-addendum.json',value)
 print('SUPPLEMENT',json.dumps(result),flush=True)
 return value


def behavior_hazards():
 outer=load(Path('/srv/tse-cecil-rollout-evidence-20261114/navigation031-hole-host/receipt.json'))
 restore=load(Path('/srv/tse-cecil-rollout-evidence-20261114/navigation031-hole-root-restore.json'))
 if restore['result_sha256']!=RESULT or restore['status']!='PASS_RESTORE':raise ValueError('Root restore receipt context differs')
 player_source=Path('/srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es');read(player_source)
 patterns={'telefrag':r'^(.+) telefragged (.+)$','knife':r'^(.+) cut (.+) into pieces$','lead':r'^(.+) poured lead into (.+)$','blast':r'^(.+) blew (.+) away$','cannon':r'^(.+) smashed (.+) with a cannon$','nuke':r'^(.+) nuked (.+)$','generic':r'^(.+) killed (.+)$','drowned':r'^(.+) drowned$','burning':r'^(.+) burst into flames$','spike':r'^(.+) fell into a spike-hole$','freezing':r'^(.+) has frozen$','acid':r'^(.+) dissolved$','selfblast':r'^(.+) blew himself away$','suicide':r'^(.+) has committed suicide$','abyss':r'^(.+) went over the edge$','brush':r'^(.+) was squashed$','impact':r'^(.+) swashed$','heat':r'^(.+) stood in the sun for too long$','unknown_other':r'^(.+) passed away$','missing':r'^(.+) is missing in action$','pierced':r'^(.+) was pierced$','enemy_telefrag':r'^(.+) was telefragged$'}
 names=collections.defaultdict(set)
 for row in G['queries']:
  for k,v in row['query'].items():
   if re.fullmatch(r'player_[0-8]',k):names[v].add(int(k.split('_')[1]))
 def ownslot(name):
  slots=names.get(name,set());return next(iter(slots))if len(slots)==1 else None
 deaths={}
 for role,text in G['logs'].items():
  events=[]
  for line,t in enumerate(text.splitlines(),1):
   matches=[(k,re.fullmatch(p,t))for k,p in patterns.items()];matches=[(k,m)for k,m in matches if m]
   # Generic blast also matches himself; prefer the distinct explicit self case.
   if len(matches)>1 and any(k=='selfblast'for k,m in matches):matches=[(k,m)for k,m in matches if k=='selfblast']
   if len(matches)>1:raise ValueError('ambiguous death template')
   if not matches:continue
   k,m=matches[0];groups=m.groups();events.append(dict(line=line,kind=k,killer_slot=ownslot(groups[0])if len(groups)==2 else None,victim_slot=ownslot(groups[-1]),native_time='UNKNOWN',native_life='UNKNOWN'))
  deaths[role]=dict(rows=events,counts=dict(collections.Counter(e['kind']for e in events)),name_to_slot_unknown=sum(e['victim_slot']is None for e in events))
 own_kills=[e for e in deaths['server']['rows']if e['killer_slot']in set(G['report']['actual_slot_mapping']['botA']+G['report']['actual_slot_mapping']['botB'])]
 focus=[]
 for f in G['focuses'][:2]:
  l=f['life'];rr=[r for r in G['native'][(l['role'],l['local'])]if r['good']and r['spawn']==l['spawn_clock']];ss=[r for r in f['source_life_rows']if r['tag']=='CecilState']
  focus.append(dict(role=l['role'],local=l['local'],slot=l['slot'],spawn=l['spawn_clock'],native_current_counts=dict(collections.Counter(str(r['weapons']['current'])for r in rr)),native_fire_by_current=dict(collections.Counter(str(r['weapons']['current'])for r in rr if(r['last_buttons']or 0)&1)),source_states=len(ss),source_current_fire_visible={str(k):v for k,v in collections.Counter((r['current'],r['fire'],r['vis'])for r in ss).items()},source_nonzero_motion_states=sum(any(float(r.get(k,0))!=0 for k in ['move','strafe','up'])for r in ss),picker_arbitration_taken=sum(bool(b['arbitration']and b['arbitration']['fields']['taken'])for b in f['picker_batches']),picker_batch_count=len(f['picker_batches']),native_position_chords=l['geometry']['observed_position_chords'],continuous_far_colt_fire='NOT_PROVEN; source fire intentions and sparse native Coltflags are not shot/range ACKs'))
 flights=[e for e in G['events']if e['tag']=='CecilFlightFinish']
 value=dict(status='FINAL_CLOSED_BEHAVIOR_HAZARD_RESOURCE_CONTEXT_ONLY',qualified=False,focus=focus,death_template_source_sha256=G['pins'][str(player_source)],death_templates=deaths,server_player_kill_template_total=sum(deaths['server']['counts'].get(k,0)for k in ['telefrag','knife','lead','blast','cannon','nuke','generic']),server_own_killer_slot_counts=dict(collections.Counter(str(e['killer_slot'])for e in own_kills)),death_scope='Whole closed original server log only; peer copies never summed. Exact names only link to declared own query slots; no clocks/life/damage chains inferred.',flight_counts={str(k):v for k,v in collections.Counter((e['fields'].get('action'),e['fields'].get('reason'))for e in flights).items()},all_flight_events=flights,root_outer_host_receipt={k:v for k,v in outer.items()if k!='samples'},root_restore_receipt=restore,source_state_enum='Raw numeric state values; not a proof of liquid/lava or a successful navigation trigger',teleporter_scope='Telefrag kill messages do not establish a navigated teleport transition',damage_ack=False)
 save('behavior-hazards.json',value);G['behavior']=value
 # Corrected complete custody file uses the final source hash and final inputs.
 final=dict(G['supplement'],input_pins=G['pins'],input_bytes=G['sizes'],actual_total_read_bytes=G['read_bytes'],reader_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 save('source-custody-final.json',final)
 canonical=['summary.json','all-lives.json','all-picker-batch-bindings.json','long-no-useful-focus.json','source-custody-final.json','behavior-hazards.json']
 output_pins={}
 for name in canonical:
  with opened(OUT/name)as f:raw=f.read(OUTPUT+1)
  if len(raw)>OUTPUT:raise ValueError('output verification bound')
  output_pins[name]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
 receipt=dict(status='COMPLETE_CANONICAL_HOLE031_CLOSED_AUDIT_ONLY',qualified=False,a4_pass=False,result_sha256=RESULT,reader_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),input_pins=G['pins'],input_bytes=G['sizes'],actual_total_read_bytes=G['read_bytes'],stream_passes=1,canonical_outputs=output_pins,noncanonical_checkpoints=['final-receipt.json','source-custody-addendum.json'],checkpoint_note='Earlier author metadata/source-selection checkpoints retained; canonical source custody is source-custody-final.json. Sourceevent coverage correction used only retained RAM; no new Native log/inventory reads.',prescan_sizes=G['prescan_sizes'],input_cap=LIMIT,output_cap=OUTPUT,written_before_receipt=G['written'])
 pin=save('complete-final-receipt.json',receipt);print('COMPLETE',json.dumps(dict(pin=pin,output_bytes=G['written'],read_bytes=G['read_bytes'],kill_counts=value['death_templates']['server']['counts'],own_killer_counts=value['server_own_killer_slot_counts'],unknown_names=value['death_templates']['server']['name_to_slot_unknown'])),flush=True)

def main():acquire();derive();outputs();G['supplement']=supplement();behavior_hazards()
if __name__=='__main__':main()
