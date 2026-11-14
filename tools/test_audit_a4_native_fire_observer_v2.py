import copy
import unittest

import audit_a4_native_fire_observer_v2 as audit


class NativeFireReviewTests(unittest.TestCase):
    def setUp(self):
        self.expected = dict(entity_id=7, entity_pointer=65536, world_pointer=131072)
        self.row = dict(self.expected, slot=0, present=True, render_type=3, health=100,
                        spawned_tick=1.0000001192092896, last_buttons=1,
                        weapons=dict(current=9, owned=259, has_ammo=1, fire_requested=1))
        old = dict(self.row, weapons=dict(self.row['weapons'], owned=3, current=1))
        self.snapshots = [(1, dict(game_tick=1.5, players=[old])),
                          (2, dict(game_tick=2.0, players=[self.row])),
                          (3, dict(game_tick=3.5, players=[copy.deepcopy(self.row)]))]
        self.text = '''[CecilSpawn] local=0 tick=1 entity=7 generation=5
[CecilWeaponObserve] local=0 tick=1 entity=7 generation=5 native_time=1.000000
[CecilState] local=0 tick=10 entity=7 generation=5 alive=1 shots=0
[CecilWeaponObserve] local=0 tick=10 entity=7 generation=5 native_time=2.000000
[CecilState] local=0 tick=20 entity=7 generation=5 alive=1 shots=2
'''

    def result(self):
        return audit.slot_evidence(audit.source_rows(self.text), self.snapshots,
                                   0, 0, self.expected)

    def test_interior_witness_binds_life_without_widening_spawn_boundary(self):
        self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 2)
        self.assertEqual(self.result()['actual_useful_inventory_gains'], 1)

    def test_entire_printf_range_must_be_inside_exact_server_bounds(self):
        self.text = self.text.replace('native_time=2.000000', 'native_time=1.000000')
        self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)

    def test_native_action_requires_real_fire_bit_current_owned_ammo_and_request(self):
        for change in ('last_buttons', 'current', 'owned', 'has_ammo', 'fire_requested'):
            with self.subTest(change=change):
                saved = copy.deepcopy(self.snapshots)
                for _, snap in self.snapshots:
                    for row in snap['players']:
                        if change == 'last_buttons': row[change] = 0
                        else: row['weapons'][change] = 0
                self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)
                self.snapshots = saved

    def test_wrong_entity_world_or_pointer_cannot_contribute(self):
        for key in audit.IDENTITY:
            with self.subTest(key=key):
                saved = copy.deepcopy(self.snapshots)
                for _, snap in self.snapshots: snap['players'][0][key] += 4
                self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)
                self.snapshots = saved

    def test_counter_without_growth_or_reset_is_insufficient(self):
        for replacement in ('shots=0', 'shots=-1'):
            with self.subTest(replacement=replacement):
                text = self.text
                self.text = self.text.replace('shots=2', replacement)
                self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)
                self.text = text

    def test_counter_cannot_cross_generation(self):
        self.text = self.text.replace('tick=20 entity=7 generation=5',
                                      'tick=20 entity=7 generation=6')
        self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)

    def test_initial_owned_inventory_is_not_a_pickup(self):
        self.snapshots = self.snapshots[1:]
        self.assertEqual(self.result()['actual_useful_inventory_gains'], 0)

    def test_dead_rows_are_not_fire_or_pickup(self):
        for _, snap in self.snapshots: snap['players'][0]['health'] = 0
        self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)
        self.assertEqual(self.result()['actual_useful_inventory_gains'], 0)

    def test_source_generation_with_interior_witnesses_in_two_lives_is_invalid(self):
        late = dict(self.row, spawned_tick=4.0)
        self.snapshots.append((4, dict(game_tick=5.0, players=[late])))
        self.text += '[CecilWeaponObserve] local=0 tick=30 entity=7 generation=5 native_time=4.500000\n'
        self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)

    def test_counter_tick_reversal_is_invalid(self):
        self.text = self.text.replace('tick=20 entity=7 generation=5 alive',
                                      'tick=9 entity=7 generation=5 alive')
        self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)

    def test_possession_gain_across_spawn_is_not_a_pickup(self):
        for _, snap in self.snapshots[1:]: snap['players'][0]['spawned_tick'] = 1.75
        self.assertEqual(self.result()['actual_useful_inventory_gains'], 0)

    def test_upper_printf_boundary_is_not_rounded_outwards(self):
        self.text = self.text.replace('native_time=2.000000', 'native_time=3.500000')
        self.assertEqual(self.result()['native_fire_with_same_life_source_growth'], 0)

    def test_missing_previous_inventory_is_not_zero_owned_or_pickup(self):
        self.snapshots[0][1]['players'][0]['weapons'] = None
        self.assertEqual(self.result()['actual_useful_inventory_gains'], 0)


if __name__ == '__main__':
    unittest.main()
