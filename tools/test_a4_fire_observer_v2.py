import copy
import unittest

import a4_fire_observer_v2 as observer


class BoundObserverTests(unittest.TestCase):
    def setUp(self):
        self.mapping = dict(botA=[0, 1, 2, 3], botB=[4, 5, 6, 7], vanilla=[8])
        self.identity = [100, 200]
        self.offsets = dict(server=10, botA=20, botB=30)
        self.players = [dict(slot=i, present=True, entity_id=10+i,
                             entity_pointer=65536+4096*i, world_pointer=131072,
                             render_type=3, health=100, spawned_tick=1.0000001192092896,
                             last_buttons=1, weapons=dict(current=9, owned=259,
                             has_ammo=1, fire_requested=1)) for i in range(9)]
        self.registry = dict(phase=1, players=copy.deepcopy(self.players),
                             actual_slot_mapping=self.mapping,
                             native_fire_epoch=dict(phase=1, server_identity=self.identity,
                                                    log_offsets=self.offsets))
        self.samples = []
        for tick in (1.5, 2., 3.5):
            players = copy.deepcopy(self.players)
            if tick == 1.5:
                for p in players: p['weapons']['owned'] = 3
            raw = dict(game_tick=tick, players=players, process_identity=self.identity,
                       hashes=observer.ORIGINAL_HASHES.copy(), consistency='two_equal_reads_not_atomic')
            self.samples.append(observer.bind_sample(raw, 1, self.identity, self.offsets))
        self.logs = {}
        for role in ('botA', 'botB'):
            lines = ['[CecilLoad] ready=1']
            for local, slot in enumerate(self.mapping[role]):
                entity = self.players[slot]['entity_id']
                prefix = f'local={local} entity={entity} generation=5'
                lines += [f'[CecilSpawn] {prefix} tick=1',
                          f'[CecilWeaponObserve] {prefix} tick=10 native_time=2.000000',
                          f'[CecilState] {prefix} tick=10 alive=1 shots=0',
                          f'[CecilState] {prefix} tick=20 alive=1 shots=2']
            self.logs[role] = '\n'.join(lines)

    def evaluate(self):
        return observer.evidence(self.logs, self.mapping, self.samples,
                                 self.registry, self.identity)

    def test_all_eight_slots_bound(self):
        result = self.evaluate()
        self.assertEqual(len(result), 8)
        for row in result.values():
            self.assertEqual(row['native_fire_with_same_life_source_growth'], 2)
            self.assertEqual(row['actual_useful_inventory_gains'], 1)

    def test_bind_does_not_modify_original_snapshot(self):
        raw = dict(self.samples[0]); raw.pop('observer_epoch')
        before = copy.deepcopy(raw)
        observer.bind_sample(raw, 1, self.identity, self.offsets)
        self.assertEqual(raw, before)

    def test_wrong_process_start_module_consistency_or_phase_rejects(self):
        mutations = [lambda s: s['process_identity'].__setitem__(1, 999),
                     lambda s: s['hashes'].__setitem__('GameMP.dll', '0'*64),
                     lambda s: s.__setitem__('consistency', 'unknown'),
                     lambda s: s['observer_epoch'].__setitem__('phase', 2),
                     lambda s: s['observer_epoch']['log_offsets'].__setitem__('botA', 999)]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                previous = copy.deepcopy(self.samples)
                mutation(self.samples[0])
                with self.assertRaises(ValueError): self.evaluate()
                self.samples = previous

    def test_same_entity_world_spawn_reuse_from_old_epoch_rejects(self):
        self.samples[0]['observer_epoch']['phase'] = 0
        with self.assertRaises(ValueError): self.evaluate()

    def test_registry_mapping_or_server_identity_change_rejects(self):
        self.registry['actual_slot_mapping'] = dict(self.mapping, botA=[1, 0, 2, 3])
        with self.assertRaises(ValueError): self.evaluate()
        self.registry['actual_slot_mapping'] = self.mapping
        self.registry['native_fire_epoch']['server_identity'] = [100, 201]
        with self.assertRaises(ValueError): self.evaluate()

    def test_unbound_sample_cannot_be_silently_skipped(self):
        self.samples[0].pop('observer_epoch')
        with self.assertRaises(ValueError): self.evaluate()

    def test_ambiguous_source_map_epoch_rejects(self):
        self.logs['botA'] += '\n[CecilLoad] ready=1'
        with self.assertRaises(ValueError): self.evaluate()

    def test_only_sparse_fire_gate_is_replaced_and_diagnostics_remain(self):
        result = dict(missing_activity=['botA:0:fire_action_rows', 'botB:3:ready_rows'],
                      qualified=False, functional_pass=False,
                      slots={f'{r}:{i}':dict(fire_action_rows=0) for r in ('botA','botB') for i in range(4)})
        out = observer.apply(result, self.logs, self.mapping, self.samples,
                             self.registry, self.identity)
        self.assertEqual(out['missing_activity'], ['botB:3:ready_rows'])
        self.assertEqual(out['slots']['botA:0']['fire_action_rows'], 0)
        self.assertFalse(out['qualified']); self.assertFalse(out['functional_pass'])

    def test_sampled_ai_fire_cannot_replace_absent_counter_growth(self):
        self.logs['botA'] = self.logs['botA'].replace('shots=2', 'shots=0')
        result = dict(missing_activity=[], slots={f'{r}:{i}':dict(fire_action_rows=9)
                      for r in ('botA','botB') for i in range(4)})
        out = observer.apply(result, self.logs, self.mapping, self.samples,
                             self.registry, self.identity)
        self.assertIn('botA:0:native_bound_fire_actions', out['missing_activity'])
        self.assertNotIn('botB:0:native_bound_fire_actions', out['missing_activity'])


if __name__ == '__main__':
    unittest.main()
