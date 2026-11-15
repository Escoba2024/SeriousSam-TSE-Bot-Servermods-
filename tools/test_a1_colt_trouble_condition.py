"""Pure new condition checks; no native/process/display or fake runtime PASS."""
import copy
import importlib.util
from pathlib import Path
import unittest


def condition():
    p=Path(__file__).with_name('a1_colt_trouble_condition.py')
    if not p.exists():return None
    s=importlib.util.spec_from_file_location('trouble_condition',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def frame(hp=100.):
    from test_a1_original_respawn_policy import frame as actual_shape
    f=actual_shape();a=f['actors']['vanilla'];a.update(health=hp,entity_flags=8 if hp>0 else 0,may_respawn=0 if hp>0 else 2)
    return f


def native(f):
    result={'server_process_identity':f['identity']['server'],'vanilla_process_identity':f['identity']['vanilla'],
            'monotonic_started':f['started'],'monotonic_finished':f['finished'],'roles':{}}
    for role,a in f['actors'].items():
        result['roles'][role]={'present':True,'slot':0 if role=='vanilla'else 1,'entity_id':a['id'],
         'entity_pointer':int(a['pointer'],16),'world_pointer':int(a['world'],16),'spawned_tick':a['spawn_clock'],
         'health':a['health'],'last_buttons':a['buttons_now'],'placement':[1.,2.,3.,4.,5.,6.],'game_tick':5.}
    result['original_replica']=dict(result['roles']['vanilla'],process_identity=f['identity']['vanilla'],game_tick=4.95)
    return result


class ConditionTests(unittest.TestCase):
    def setUp(self):
        self.m=condition();self.assertIsNotNone(self.m,'new explicit LittleTrouble condition absent')

    def test_existing_placements_only_and_separate_clock_domains(self):
        f=frame();n=native(f);old=copy.deepcopy((n,f));v=self.m.role_geometry(n,f)
        self.assertEqual((n,f),old)
        self.assertEqual(v['server_actors']['vanilla']['placement'],[1.,2.,3.,4.,5.,6.])
        self.assertEqual(v['original_replica']['game_tick'],4.95)
        self.assertEqual(v['server_actors']['vanilla']['game_tick'],5.)
        self.assertFalse(v['los_proven']);self.assertFalse(v['spawn_marker_proven'])

    def test_geometry_cannot_be_wrong_actor_life_process_missing_or_nonfinite(self):
        f=frame();n=native(f)
        changes=[lambda x:x['roles']['botA'].update(entity_id=99),
                 lambda x:x['roles']['vanilla'].update(spawned_tick=99.),
                 lambda x:x.update(server_process_identity=[99,100]),
                 lambda x:x['original_replica'].update(process_identity=[99,100]),
                 lambda x:x['roles']['vanilla'].pop('placement'),
                 lambda x:x['roles']['vanilla'].update(placement=[0.,0.,float('nan'),0.,0.,0.])]
        for change in changes:
            with self.subTest(change=change):
                bad=copy.deepcopy(n);change(bad)
                with self.assertRaises(ValueError):self.m.role_geometry(bad,f)

    def test_original_process_pointers_are_not_equated_to_server_addresses(self):
        f=frame();n=native(f)
        n['original_replica'].update(entity_pointer=0x90000,world_pointer=0xa0000)
        v=self.m.role_geometry(n,f)
        self.assertNotEqual(v['original_replica']['entity_pointer'],v['server_actors']['vanilla']['entity_pointer'])
        self.assertFalse(v['clock_domains_fused'])

    def test_bool_alias_is_not_an_actual_health_or_spawn_float(self):
        f=frame(1.);f['actors']['vanilla']['spawn_clock']=1.
        for field in('health','spawned_tick'):
            n=native(f);n['roles']['vanilla'][field]=True
            with self.subTest(field=field),self.assertRaises(ValueError):self.m.role_geometry(n,f)

    def test_observed_hp_drop_and_dead_ready_same_life_not_damage_owner_proof(self):
        a,b,c=frame(),frame(90.),frame(0.)
        v=self.m.require_hp_drop(a,[{'frame':a},{'frame':b},{'frame':c}])
        self.assertTrue(v['hp_drop_observed']);self.assertEqual(v['first_drop']['actors']['vanilla']['health'],90.)
        self.assertFalse(v['damage_owner_proven']);self.assertFalse(v['los_proven'])
        # A single sampled100→dead change is retained honestly; it does not invent an intermediate live hit.
        v=self.m.require_hp_drop(a,[{'frame':a},{'frame':c}]);self.assertFalse(v['intermediate_positive_drop_observed'])

    def test_no_drop_incomplete_reads_changed_actor_or_no_death_remain_fatal(self):
        first=frame();dead=frame(0.);bad=copy.deepcopy(dead);bad['actors']['vanilla']['spawn_clock']+=1
        for rows in([{'frame':first}], [{'error':'read failed'}], [{'frame':bad}], [{'frame':frame(90.)}]):
            with self.subTest(rows=rows),self.assertRaises(ValueError):self.m.require_hp_drop(first,rows)
        self.assertEqual(self.m.OWNERSHIP_PAYLOAD_LIMIT,64*1024**2)
        self.assertEqual(self.m.MAX_ROLE_READS,1024)


if __name__=='__main__':unittest.main()
