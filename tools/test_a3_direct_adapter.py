"""Focused private-package source/adapter checks; no process or native access."""
import collections
import ast
import copy
import importlib.util
import math
import os
from pathlib import Path
import sys
import textwrap
import unittest

PACKAGE=os.environ.get('TSE_A3_DIRECT_PACKAGE')


@unittest.skipUnless(PACKAGE,'explicit disabled private package required')
class DirectAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(PACKAGE)
        sys.path.insert(0,str(cls.root))
        spec=importlib.util.spec_from_file_location('direct_adapter_tests',cls.root/'a3_direct_controller_policy.py')
        cls.pol=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.pol)
        spec=importlib.util.spec_from_file_location('direct_original_damage_tests',cls.root/'a3_damage_policy.py')
        cls.damage=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.damage)

    @classmethod
    def tearDownClass(cls):
        sys.path.remove(str(cls.root))

    def test_actual_pinned_configs_and_dll_identical_except_tier_in_all_windows(self):
        for lower in (1,2):
            for swap in (0,1):
                a,b=[self.pol.cohort(role,lower,swap,0)for role in ('botA','botB')]
                self.assertEqual(a['game_sha256'],self.pol.CANDIDATE_SHA)
                self.assertEqual(a['game_sha256'],b['game_sha256'])
                self.assertTrue(a['candidate'] and b['candidate'])
                self.assertEqual(a['config_base_sha256'],b['config_base_sha256'])
                self.assertEqual(self.pol.direct.without_tier(a['config']),
                                 self.pol.inherited.load_source('candidate'))
                self.assertEqual((a['tier'],b['tier']),(lower,lower+1)if swap==0 else(lower+1,lower))

    def registry(self,lower=1,swap=0):
        cohorts={r:self.pol.cohort(r,lower,swap,0)for r in ('botA','botB')}
        mapping=dict(botA=[0,2,4,6],botB=[1,3,5,7],vanilla=[8])
        rows={s:dict(entity_id=100+s,entity_pointer=65536+s*4096)for s in range(9)}
        return self.pol.build_direct_registry(self.damage,rows,mapping,cohorts)

    def test_actual_original_builder_preserves_all_nine_slots_pointers_and_labels(self):
        for lower in (1,2):
            for swap in (0,1):
                out=self.registry(lower,swap);self.assertEqual(len(out),9)
                for s in range(8):
                    role='botA'if s%2==0 else'botB'
                    self.assertEqual(out[100+s]['slot'],s)
                    self.assertEqual(out[100+s]['pointer'],hex(65536+s*4096))
                    self.assertEqual(out[100+s]['cohort'],self.pol.direct.NAMES[self.pol.direct.tiers(lower,swap)[role]])
                self.assertEqual(out[108]['cohort'],'vanilla')

    def test_real_profile_rows_required_for_all_locals_and_actual_tier(self):
        cohorts={r:self.pol.cohort(r,2,1,0)for r in ('botA','botB')}
        logs={r:'\n'.join(f"[BotHuman] local={i} profile={c['tier_name']} tier={c['tier']} persona=duelist seed=123 model=arena-v1"for i in range(4))for r,c in cohorts.items()}
        out=self.pol.check_actual_tiers(logs,cohorts)
        self.assertEqual(out['botA'][0]['profile'],'DEMON')
        for bad in [logs['botA'].replace('tier=3','tier=2'),logs['botA'].replace('profile=DEMON','profile=STARK'),
                    '\n'.join(logs['botA'].splitlines()[:3])]:
            changed=copy.deepcopy(logs);changed['botA']=bad
            with self.assertRaises(ValueError):self.pol.check_actual_tiers(changed,cohorts)

    def test_hard_template_changes_only_difficulty_and_rejects_other_rule_drift(self):
        source='\n'.join(['gam_iStartDifficulty=3;','gam_iFragLimit=0;','gam_iTimeLimit=0;',
            'gam_bInfiniteAmmo=1;','gam_iBlood=3;','gam_bGibs=0;','gam_tmSpawnInvulnerability=(FLOAT)0;'])+'\n'
        self.assertEqual(self.pol.hard_server_template(source),source.replace('Difficulty=3','Difficulty=2'))
        self.assertEqual(self.pol.hard_server_template(source.replace('Difficulty=3','Difficulty=2')),
                         source.replace('Difficulty=3','Difficulty=2'))
        for bad in [source.replace('TimeLimit=0','TimeLimit=2'),source.replace('Difficulty=3','Difficulty=1'),
                    source+'gam_iStartDifficulty=3;\n',source.replace('gam_bGibs=0;','')]:
            with self.assertRaises(ValueError):self.pol.hard_server_template(bad)

    def test_hard_checks_reuse_existing_reads_and_remain_inside_restore_scope(self):
        import json
        manifest=json.loads((self.root/'source-manifest.json').read_text())
        parent=Path(manifest['direct_tiers']['parent_source'])
        old=(parent/'run-a3-damage018.py').read_text()
        new=(self.root/'run-a3-direct020.py').read_text()
        def selected_calls(source):
            return sorted(ast.dump(node,include_attributes=False)for node in ast.walk(ast.parse(source))
                if isinstance(node,ast.Call)and isinstance(node.func,ast.Attribute)and
                isinstance(node.func.value,ast.Name)and
                (node.func.value.id,node.func.attr)in{('probe','read'),('inventory','sample'),('B','query'),('time','sleep')})
        self.assertEqual(selected_calls(old),selected_calls(new))
        self.assertEqual(new.count('hard_rules.validate_session(snapshot)'),2)
        self.assertEqual(new.count('hard_rules.validate_query(q)'),1)
        self.assertLess(new.index('transaction.seal()'),new.index('policy.hard_server_template('))
        self.assertLess(new.index('policy.hard_server_template('),new.index("launch('server')"))

    def test_native_hard_rules_reject_serious_and_wrong_query_from_existing_samples(self):
        import struct
        hard=self.pol.local('stability_hard_rules')
        raw=bytearray(156)
        for key,(fmt,offset)in hard.FIELDS.items():struct.pack_into(fmt,raw,offset,hard.EXPECTED[key])
        self.assertEqual(hard.validate_session(dict(session156_hex=raw.hex())),hard.EXPECTED)
        struct.pack_into('<i',raw,0x1c,3)
        with self.assertRaises(ValueError):hard.validate_session(dict(session156_hex=raw.hex()))
        hard.validate_query(dict(difficulty='Hard'))
        with self.assertRaises(ValueError):hard.validate_query(dict(difficulty='Serious'))

    def record(self,seq,src,dst,hp_before=100,hp_after=50,armor_before=10,armor_after=5):
        registry=self.registry()
        state=lambda health,armor:dict(health=health,armor=armor,spawn_clock=1.,current_tick=2.)
        return dict(sequence=seq,total_sequence=seq,thread_id=17,tls_bound_at_entry=True,nested=False,
                    player_id=dst,player_pointer=registry[dst]['pointer'],inflictor_known_player=src,
                    entered_ms=10.,left_ms=11.,damage_type=1,requested_damage=50.,
                    before=state(hp_before,armor_before),after=state(hp_after,armor_after))

    def run_actual_closed_damage_loop(self,records):
        source=(self.root/'analyze-direct020.py').read_text()
        start=source.index(' counts=collections.Counter(')
        end=source.index(" expected=load(P/'damage-attribution.json')",start)
        code=textwrap.dedent(source[start:end])
        state=dict(collections=collections,math=math,records=records,registry=self.registry(),
                   f=dict(tls_binding=dict(thread_id=17),gameplay_window_start_ms=0.,gameplay_window_end_ms=100.))
        exec(compile(code,'actual-closed-damage-loop','exec'),state)
        return state

    def test_actual_both_direction_damage_armor_overkill_and_kills(self):
        records=[self.record(1,100,101,100,-20),self.record(2,101,100,100,70)]
        out=self.run_actual_closed_damage_loop(records)
        low=out['matrix']['MITTEL -> STARK'];high=out['matrix']['STARK -> MITTEL']
        self.assertEqual((low['hp_loss_raw'],low['hp_loss_capped_at_pre_hit_health'],low['lethal_calls']),(120,100,1))
        self.assertEqual((high['hp_loss_raw'],high['armor_loss_raw'],high['lethal_calls']),(30,5,0))
        self.assertEqual(out['lethal'],collections.Counter({(0,1):1}))
        inherited=self.damage.summarize(records,self.registry(),0.,100.)
        self.assertEqual(inherited['known_foreign']['MITTEL']['hp_loss_raw'],120)
        self.assertEqual(inherited['known_foreign']['STARK']['hp_loss_raw'],30)

    def test_actual_partition_keeps_self_unknown_corpse_vanilla_and_outside_separate(self):
        records=[self.record(1,100,100),self.record(2,None,100),self.record(3,100,101,0,-10),
                 self.record(4,108,100),self.record(5,100,101)]
        records[-1]['left_ms']=101.
        out=self.run_actual_closed_damage_loop(records)
        self.assertEqual(dict(out['counts']),dict(known_foreign=1,corpse=1,self=1,unattributed=1,outside_or_crossing=1))
        self.assertEqual(set(out['matrix']),{'vanilla -> MITTEL'})

    def test_actual_damage_loop_rejects_sequence_gap_tls_mismatch_and_wrong_pointer(self):
        for key,value in [('sequence',2),('thread_id',18),('player_pointer','0x0'),('nested',True)]:
            r=self.record(1,100,101);r[key]=value
            with self.assertRaises(AssertionError):self.run_actual_closed_damage_loop([r])


if __name__=='__main__':unittest.main()
