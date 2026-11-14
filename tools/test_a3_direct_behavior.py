"""Synthetic closed-file fixtures only; never imports Frida or starts a game."""
import importlib.util
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest


PACKAGE=os.environ.get('TSE_A3_DIRECT_PACKAGE')


@unittest.skipUnless(PACKAGE,'explicit disabled private package required')
class BothBehaviorTests(unittest.TestCase):
    def test_actual_two_role_parser_keeps_different_commands_and_tiers(self):
        path=Path(PACKAGE)/'behavior-direct020.py'
        spec=importlib.util.spec_from_file_location('direct_behavior_offline',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);window=root/'fixture';window.mkdir()
            module.BASE=root;module.D=root
            report=dict(finished_utc='synthetic',cleanup={r:dict(closed=True)for r in ('server','botA','botB','vanilla')},errors=[],
                candidate_tier=1,cohort_policy=dict(botA=dict(candidate=True,tier=1),botB=dict(candidate=True,tier=2)),
                actual_slot_mapping=dict(botA=[0,1,2,3],botB=[4,5,6,7],vanilla=[8]))
            (window/'result.json').write_text(json.dumps(report))
            for role,tier,error,fire,shots in [('botA',1,2,0,4),('botB',2,.5,1,7)]:
                name='MITTEL'if tier==1 else'STARK'
                lines=[f'[BotHuman] local=0 profile={name} tier={tier} persona=duelist seed=123 model=arena-v1']
                for tick,counter in [(20,0),(40,shots)]:
                    lines += [f'[CecilState] local=0 tick={tick} alive=1 owned=67 current=7 fire={fire} shots={counter} liquid=0',
                              f'[BotHuman] local=0 tick={tick} vis=1 weapon=7 err={error} fire={fire} switches=0 overshoots=0']
                (window/(role+'.log')).write_text('\n'.join(lines))
            records=[]
            for tick in (1.,1.25):
                players=[dict(slot=slot,entity_id=100+slot,spawned_tick=.25,present=True,health=100,
                              placement=[tick,0,0],weapons=dict(owned=67,current=7,fire_requested=fire))
                         for slot,fire in [(0,0),(4,1)]]
                records.append(dict(elapsed=tick,snapshot=dict(game_tick=tick,players=players)))
            (window/'inventory.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in records))
            with contextlib.redirect_stdout(io.StringIO()):
                out=module.inspect('fixture')
            self.assertEqual(set(out),{'botA','botB'})
            self.assertEqual(out['botA']['tier'],1);self.assertEqual(out['botB']['tier'],2)
            self.assertEqual(out['botA']['per_local'][0]['fire_action_counter_delta'],4)
            self.assertEqual(out['botB']['per_local'][0]['fire_action_counter_delta'],7)
            self.assertEqual(out['botA']['per_local'][0]['human_fire_rows'],0)
            self.assertEqual(out['botB']['per_local'][0]['human_fire_rows'],2)
            self.assertEqual(out['botA']['per_local'][0]['visible_error_median'],2)
            self.assertEqual(out['botB']['per_local'][0]['visible_error_median'],.5)
            self.assertTrue((root/'fixture-botA-behavior.json').is_file())
            self.assertTrue((root/'fixture-botB-behavior.json').is_file())


if __name__=='__main__':unittest.main()
