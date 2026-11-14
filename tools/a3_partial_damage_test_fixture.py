"""Synthetic closed-file fixture, never native or game qualification."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct

PARENT=Path('/srv/tse-a3-instruction-probe-root-frozen-20261114')


def make_window(root):
 p=Path(root)/'fixture';p.mkdir()
 sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
 for n in('a3_direct_controller_policy.py','a3_direct_tiers.py','controller_policy.py','stability_hard_rules.py','candidate.ini','public.ini','initial-reference.json','source-manifest.json','original_damage_worker.py','original_damage_collector.py'):shutil.copy2(PARENT/n,p/n)
 shutil.copy2(PARENT/'run-a3-direct020.py',p/'controller-source.py')
 spec=importlib.util.spec_from_file_location('synthetic_partial_policy',p/'a3_direct_controller_policy.py');pol=importlib.util.module_from_spec(spec);spec.loader.exec_module(pol)
 mapping=dict(botA=[0,1,2,3],botB=[4,5,6,7],vanilla=[8]);cohorts={role:pol.cohort(role,1,0,0)for role in('botA','botB')}
 logs={}
 for role in('botA','botB'):
  lines=[]
  for local,slot in enumerate(mapping[role]):
   lines.extend([f'local player {local} (player index {slot}) is now bot-driven:',f"[BotHuman] local={local} profile={cohorts[role]['tier_name']} tier={cohorts[role]['tier']} persona=duelist seed=123 model=arena-v1",f'[CecilSpawn] local={local} entity={100+slot} generation=6 tick=5 respawns=1'])
  if role=='botB':lines+=['[CecilDeath] local=0 entity=104 generation=6 tick=20 deaths=1','[CecilSpawn] local=0 entity=104 generation=7 tick=30 respawns=2']
  logs[role]='\n'.join(lines)+'\n';(p/(role+'-cohort.ini')).write_text(cohorts[role]['config'])
 logs.update(server='Synthetic0 killed Synthetic4\n',vanilla='');closed={}
 for role,text in logs.items():
  (p/(role+'.log')).write_text(text);f=p/(role+'-closed.log');f.write_text(text);closed[role]=dict(bytes=f.stat().st_size,sha256=sha(f))
 identities={role:[17+i,100+i]for i,role in enumerate(('server','botA','botB','vanilla'))};reference=json.loads((p/'initial-reference.json').read_text())
 players=[dict(slot=s,entity_id=100+s,entity_pointer=65536+s*4096,present=True,spawned_tick=.25,health=100.,armor=0,render_type=3,support_pointer=0,last_buttons=0,current_translation_absolute=[0,0,0],physics_flags=0x40000284,placement=reference[str(s)]['placement'],weapons=dict(owned=3,current=2,wanted=2))for s in range(9)]
 snapshot=dict(process_identity=identities['server'],game_tick=.25,players=players,hashes={'Engine.dll':'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f','EntitiesMP.dll':'7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350','GameMP.dll':'1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'})
 initial=pol.InitialObservations();initial.add(snapshot,.01);initial.finish()
 for n,v in [('first-spawn-observations.json',initial.raw_first),('neutral-spawn-observations.json',initial.players),('pending-phase-errors.json',{})]:(p/n).write_text(json.dumps(v))
 first=json.dumps(dict(elapsed=.01,snapshot=snapshot));snapshot=json.loads(json.dumps(snapshot));snapshot['game_tick']=1.;snapshot['players'][4]['health']=-25.
 (p/'inventory.jsonl').write_text(first+'\n'+json.dumps(dict(elapsed=.9,snapshot=snapshot))+'\n')
 registry={100+s:dict(slot=s,pointer=hex(65536+s*4096),cohort='MITTEL'if s<4 else'STARK'if s<8 else'vanilla')for s in range(9)};(p/'damage-cohort-registry.json').write_text(json.dumps(registry))
 damage=dict(sequence=1,total_sequence=1,thread_id=17,tls_bound_at_entry=True,nested=False,player_id=104,player_pointer=registry[104]['pointer'],inflictor_known_player=100,damage_type=1,entered_ms=10.,left_ms=11.,before=dict(health=100.,armor=0.,spawn_clock=.25,current_tick=1.),after=dict(health=-25.,armor=0.,spawn_clock=.25,current_tick=1.))
 (p/'frida-damage.jsonl').write_text(json.dumps(dict(records=[damage]))+'\n');(p/'damage-attribution.json').write_text(json.dumps(dict(known_foreign=dict(MITTEL=dict(calls=1,hp_loss_raw=125.,hp_loss_capped_at_pre_hit_health=100.,lethal_calls=1)))))
 hard=pol.local('stability_hard_rules');raw=bytearray(156)
 for key,(fmt,offset)in hard.FIELDS.items():struct.pack_into(fmt,raw,offset,hard.EXPECTED[key])
 health=dict(session156_hex=raw.hex());barrier={role:health for role in identities};(p/'session-health.jsonl').write_text(json.dumps(dict(elapsed=.01,roles=barrier))+'\n')
 query=dict(numplayers='9',difficulty='Hard')
 for s in range(9):query['player_'+str(s)]='Synthetic'+str(s);query['frags_'+str(s)]='0'
 (p/'queries.json').write_text(json.dumps([dict(elapsed=.01,query=query)]));(p/'host-resources.json').write_text(json.dumps(dict(samples=[dict(violations=[])],summary={})))
 f=dict(faults=0,dropped=0,in_flight=0,unknown_victim_calls=0,non_main_calls=0,detach_errors=[],detached=True,original_getter_restored=True,original_damage_restored=True,coverage=dict(entire_gameplay_window_covered=True),records_received=1,matched_calls=1,total_calls=1,tls_binding=dict(thread_id=17),gameplay_window_start_ms=0.,gameplay_window_end_ms=120000.,same_spawn_tick_health_decrease_count=0,world_crc32='ff3776e0',cecil_path_hash='5af1a276',version='17.26.2',hook_source_sha256=sha(PARENT/'frozen-v2/damage_readonly.js'),host_source_sha256=sha(PARENT/'frozen-v2/host_binding.py'),guard_source_sha256=sha(PARENT/'frozen-v2/controller_guard.py'))
 result=dict(finished_utc='synthetic',post_close_logs=dict(accepted=True,logs=closed),errors=[],final_evidence_reasons=[],cleanup={role:dict(closed=True,identity=i)for role,i in identities.items()},events=[dict(event='launched',details=dict(role=role,identity=i))for role,i in identities.items()],actual_slot_mapping=mapping,cohort_policy={role:{k:v for k,v in c.items()if k!='config'}for role,c in cohorts.items()},actual_role_profiles=pol.check_actual_tiers(logs,cohorts),pair_lower_tier=1,direct_pair=[1,2],role_tiers=dict(botA=1,botB=2),swap_cohorts=False,diagnostics_enabled=False,restoration=dict(restored=True,errors=[]),barrier_before_release=barrier,frida_damage=f,controller_usage_start=dict(user_seconds=0.,system_seconds=0.),controller_usage_end=dict(user_seconds=.1,system_seconds=0.,max_rss_kib=1),clock_ticks=100,page_bytes=4096,usage_start={role:dict(cpu_ticks=0,rss_pages=1)for role in identities},usage_end={role:dict(cpu_ticks=1,rss_pages=1)for role in identities},observed_seconds=120.,status='SYNTHETIC_OFFLINE_FIXTURE',inventory={},controller_sha256=sha(p/'controller-source.py'))
 (p/'result.json').write_text(json.dumps(result));return p
