"""Full analyzer on synthetic closed files, not native/gameplay qualification."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile
import unittest

PACKAGE=os.environ.get('TSE_A3_DIRECT_PACKAGE')


@unittest.skipUnless(PACKAGE,'explicit disabled private package required')
class ClosedAnalyzerFixtureTests(unittest.TestCase):
    def test_actual_closed_analyzer_both_tiers_and_native_hard_rejection(self):
        source=Path(PACKAGE)
        spec=importlib.util.spec_from_file_location('direct_complete_fixture',source/'analyze-direct020.py')
        analyzer=importlib.util.module_from_spec(spec);spec.loader.exec_module(analyzer)
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary);window=base/'fixture';window.mkdir()
            analyzer.BASE=base;analyzer.OUT=base
            for name in ('a3_direct_controller_policy.py','a3_direct_tiers.py','controller_policy.py',
                         'stability_hard_rules.py','candidate.ini','public.ini','initial-reference.json','source-manifest.json'):
                shutil.copy2(source/name,window/name)
            for name in ('original_damage_worker.py','original_damage_collector.py'):
                if (source/name).is_file():shutil.copy2(source/name,window/name)
            shutil.copy2(source/'run-a3-direct020.py',window/'controller-source.py')
            spec=importlib.util.spec_from_file_location('direct_fixture_policy',window/'a3_direct_controller_policy.py')
            pol=importlib.util.module_from_spec(spec);spec.loader.exec_module(pol)
            mapping=dict(botA=[0,1,2,3],botB=[4,5,6,7],vanilla=[8])
            cohorts={r:pol.cohort(r,1,0,0)for r in ('botA','botB')}
            logs={}
            for role in ('botA','botB'):
                c=cohorts[role];lines=[]
                for local,slot in enumerate(mapping[role]):
                    lines.extend([f'local player {local} (player index {slot}) is now bot-driven:',
                        f"[BotHuman] local={local} profile={c['tier_name']} tier={c['tier']} persona=duelist seed=123 model=arena-v1",
                        f'[CecilSpawn] local={local} entity={100+slot} generation=1 tick=5 owned=3'])
                logs[role]='\n'.join(lines)+'\n'
                (window/(role+'-cohort.ini')).write_text(c['config'])
            logs.update(server='',vanilla='')
            sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
            closed={}
            for role,text in logs.items():
                (window/(role+'.log')).write_text(text)
                file=window/(role+'-closed.log');file.write_text(text)
                closed[role]=dict(bytes=file.stat().st_size,sha256=sha(file))
            identities={role:[17+i,100+i]for i,role in enumerate(('server','botA','botB','vanilla'))}
            reference=json.loads((window/'initial-reference.json').read_text())
            players=[dict(slot=s,entity_id=100+s,entity_pointer=65536+s*4096,present=True,
                spawned_tick=.25,health=100,armor=0,render_type=3,support_pointer=0,last_buttons=0,
                current_translation_absolute=[0,0,0],physics_flags=0x40000284,
                placement=reference[str(s)]['placement'],weapons=dict(owned=3,current=2,wanted=2))for s in range(9)]
            snapshot=dict(process_identity=identities['server'],game_tick=.25,players=players,
                hashes={'Engine.dll':'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f',
                        'EntitiesMP.dll':'7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350',
                        'GameMP.dll':'1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'})
            initial=pol.InitialObservations();initial.add(snapshot,.01);initial.finish()
            for name,value in [('first-spawn-observations.json',initial.raw_first),
                               ('neutral-spawn-observations.json',initial.players),('pending-phase-errors.json',{})]:
                (window/name).write_text(json.dumps(value))
            (window/'inventory.jsonl').write_text(json.dumps(dict(elapsed=.01,snapshot=snapshot))+'\n')
            registry={100+s:dict(slot=s,pointer=hex(65536+s*4096),cohort='MITTEL'if s<4 else'STARK'if s<8 else'vanilla')for s in range(9)}
            (window/'damage-cohort-registry.json').write_text(json.dumps(registry))
            (window/'damage-attribution.json').write_text(json.dumps(dict(known_foreign={})))
            (window/'frida-damage.jsonl').write_text('')
            raw=bytearray(156);hard=pol.local('stability_hard_rules')
            for key,(fmt,offset)in hard.FIELDS.items():struct.pack_into(fmt,raw,offset,hard.EXPECTED[key])
            health=dict(session156_hex=raw.hex());barrier={r:health for r in identities}
            (window/'session-health.jsonl').write_text(json.dumps(dict(elapsed=.01,roles=barrier))+'\n')
            query=dict(numplayers='9',difficulty='Hard')
            for s in range(9):query['player_'+str(s)]='Synthetic'+str(s);query['frags_'+str(s)]='0'
            (window/'queries.json').write_text(json.dumps([dict(elapsed=.01,query=query)]))
            (window/'host-resources.json').write_text(json.dumps(dict(samples=[dict(violations=[])],summary={})))
            f=dict(faults=0,dropped=0,in_flight=0,unknown_victim_calls=0,non_main_calls=0,detach_errors=[],
                detached=True,original_getter_restored=True,original_damage_restored=True,
                coverage=dict(entire_gameplay_window_covered=True),records_received=0,matched_calls=0,total_calls=0,
                tls_binding=dict(thread_id=17),gameplay_window_start_ms=0.,gameplay_window_end_ms=100.,
                same_spawn_tick_health_decrease_count=0,world_crc32='ff3776e0',cecil_path_hash='5af1a276')
            f.update(version='17.26.2',hook_source_sha256=sha(source/'frozen-v2/damage_readonly.js'),
                     host_source_sha256=sha(source/'frozen-v2/host_binding.py'),guard_source_sha256=sha(source/'frozen-v2/controller_guard.py'))
            report=dict(finished_utc='synthetic',post_close_logs=dict(accepted=True,logs=closed),errors=[],final_evidence_reasons=[],
                cleanup={r:dict(closed=True,identity=i)for r,i in identities.items()},
                events=[dict(event='launched',details=dict(role=r,identity=i))for r,i in identities.items()],
                actual_slot_mapping=mapping,cohort_policy={r:{k:v for k,v in c.items()if k!='config'}for r,c in cohorts.items()},
                actual_role_profiles=pol.check_actual_tiers(logs,cohorts),pair_lower_tier=1,direct_pair=[1,2],role_tiers=dict(botA=1,botB=2),
                swap_cohorts=False,diagnostics_enabled=False,restoration=dict(restored=True,errors=[]),barrier_before_release=barrier,
                frida_damage=f,controller_usage_start=dict(user_seconds=0.,system_seconds=0.),
                controller_usage_end=dict(user_seconds=.1,system_seconds=0.,max_rss_kib=1),clock_ticks=100,page_bytes=4096,
                usage_start={r:dict(cpu_ticks=0,rss_pages=1)for r in identities},usage_end={r:dict(cpu_ticks=1,rss_pages=1)for r in identities},
                observed_seconds=120.,status='SYNTHETIC_OFFLINE_FIXTURE',inventory={})
            (window/'result.json').write_text(json.dumps(report))
            with contextlib.redirect_stdout(io.StringIO()):out=analyzer.analyze('fixture')
            self.assertEqual(set(out['cohorts']),{'MITTEL','STARK','vanilla'})
            self.assertEqual(out['cohorts']['MITTEL']['lives'],4);self.assertEqual(out['cohorts']['STARK']['lives'],4)
            self.assertEqual(len(out['lives']),9)
            self.assertTrue(out['native_hard_rules_verified'])
            self.assertFalse(out['qualified']);self.assertFalse(out['a3_accepted']);self.assertFalse(out['tier_strength_accepted'])
            query['difficulty']='Serious';(window/'queries.json').write_text(json.dumps([dict(elapsed=.01,query=query)]))
            with self.assertRaises(ValueError):analyzer.analyze('fixture')


if __name__=='__main__':unittest.main()
