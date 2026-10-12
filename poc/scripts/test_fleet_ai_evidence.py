import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('fleet_ai', Path(__file__).with_name('Test-FleetAIEvidence.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    lines = ['[BotDriver] local player 0 (player index 2) is now bot-driven: TSE_Fleet_A_1\n']
    for t in range(1, 81):
        turn, advance, attack = t == 1, 2 <= t <= 41, t == 43
        active = turn or advance
        lines += [
            f'[BotCombat] local=0 tick={t} self=2 alive=1 dm=1 visible=1 target=3 weapon=2 ready={int(attack)} move=1 yawDelta=0 pitchDelta=0\n',
            f'[BotNavigation] local=0 tick={t} alive=1 hold=0 requested=1 front={0.2 if turn else 3} hitType={4 if turn else 0} left=3 right=0.2 active={int(active)} phase={1 if turn else 2 if advance else 0} reason=1 began={int(turn)} finished={int(t == 41)} yaw={t} delta={2.25 if turn else 0} forward={0 if turn else 1} pos=({t/5},0,0)\n',
            f'[BotDriver] bot0 tick={t} pos=({t/5},0,0) heading={t} fire={int(attack)}\n',
            f'[BotSnapshot] tick={t} player=2 pos=({t/5},0,0) yaw={t} health=100 buttons={int(attack)} \\frags_2\\0\n',
        ]
        if attack:
            lines.append(f'[BotCombatWeapon] local=0 tick={t} desired=2 current=2 wanted=2\n')
    return lines


class StreamTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'native.log'
        self.lines = fixture()

    def tearDown(self):
        self.tmp.cleanup()

    def audit(self, minutes=0):
        self.path.write_text(''.join(self.lines), encoding='utf-8')
        return m.audit_stream(self.path, expected_slots=1, min_samples=80, minutes=minutes)

    def test_valid_and_complete_window(self):
        p = self.audit()['players'][0]
        self.assertEqual(p['decisions'], 80)
        self.assertEqual(p['advancesAtLeast2m'], 1)
        self.assertEqual(p['livingAttackTicks'], 1)

    def test_missing_nav_tick(self):
        self.lines = [s for s in self.lines if not s.startswith('[BotNavigation] local=0 tick=20 ')]
        with self.assertRaisesRegex(AssertionError, 'matching'): self.audit()

    def test_missing_replicated_action(self):
        self.lines = [s for s in self.lines if not s.startswith('[BotSnapshot] tick=20 ')]
        with self.assertRaisesRegex(AssertionError, 'matching'): self.audit()

    def test_wrong_self_identity(self):
        self.lines = [s.replace('self=2', 'self=4') for s in self.lines]
        with self.assertRaisesRegex(AssertionError, 'self identity'): self.audit()

    def test_nonfinite_or_unbounded_combat_rotation_rejected(self):
        for invalid in ('nan','4'):
            self.lines=[s.replace('yawDelta=0',f'yawDelta={invalid}') if s.startswith('[BotCombat]') else s for s in fixture()]
            with self.assertRaisesRegex(AssertionError,'combat action bounds'): self.audit()

    def test_fire_during_turn(self):
        self.lines = [s.replace('heading=1 fire=0', 'heading=1 fire=1') for s in self.lines]
        with self.assertRaisesRegex(AssertionError, 'attack while'): self.audit()

    def test_false_wall_recovery(self):
        self.lines = [s.replace('hitType=4', 'hitType=2') for s in self.lines]
        with self.assertRaisesRegex(AssertionError, 'brush'): self.audit()

    def test_stationary_completion(self):
        import re
        self.lines = [re.sub(r'pos=\([^)]*\)', 'pos=(0,0,0)', s) for s in self.lines]
        with self.assertRaisesRegex(AssertionError, 'brush'): self.audit()

    def test_duplicate_frame_rejected(self):
        self.lines.insert(20, self.lines[18])
        with self.assertRaisesRegex(AssertionError, 'duplicate'): self.audit()

    def test_short_data_does_not_prove_hour(self):
        with self.assertRaisesRegex(AssertionError, 'samples'): self.audit(minutes=60)

    def test_only_final_session_is_credited(self):
        self.lines = fixture() + fixture()[:15]
        with self.assertRaisesRegex(AssertionError, 'samples'): self.audit()

    def test_wrong_candidate_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'candidate'):
            m.assert_candidate({'dllSha256': 'old', 'startupSha256': 'config'}, 'new', 'config')

    def test_wrong_startup_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'startup'):
            m.assert_candidate({'dllSha256': 'new', 'startupSha256': 'old'}, 'new', 'config')

    def test_staggered_local_activation_uses_shared_snapshot_clock(self):
        import re
        combined = []
        for clock in range(1, 86):
            source_tick = clock-5 if clock >= 6 else 80
            original = [s.replace(f'tick={source_tick} ', f'tick={clock} ') for s in fixture() if f'tick={source_tick} ' in s]
            if clock == 1:
                combined.append(fixture()[0])
            combined += original
            if clock >= 6:
                if clock == 6:
                    combined.append('[BotDriver] local player 1 (player index 3) is now bot-driven: TSE_Fleet_A_2\n')
                for line in [s for s in fixture() if f'tick={clock-5} ' in s]:
                    line = line.replace('local=0 ', 'local=1 ').replace('bot0 ', 'bot1 ').replace('self=2 ', 'self=3 ').replace('player=2 ', 'player=3 ').replace('frags_2', 'frags_3')
                    if line.startswith('[BotSnapshot]'):
                        line = re.sub(r'tick=\d+', f'tick={clock}', line)
                    combined.append(line)
        self.path.write_text(''.join(combined), encoding='utf-8')
        result = m.audit_stream(self.path, expected_slots=2, min_samples=80)
        self.assertEqual(result['localTickOffsets'], {'0': 0, '1': 5})
        self.assertTrue(all(p['decisions'] == 80 for p in result['players']))

    def test_constant_replicated_position_across_sixty_windows_is_not_movement(self):
        frames = {}
        for line in fixture()[1:]:
            tag, tick, _, fields = m.record(line.strip())
            if tag == 'BotSnapshot':
                fields['pos'] = '(0,0,0)'
            frames.setdefault(tick, {})[tag] = fields
        state = m.PlayerAudit(0, 2, 'TSE_Fleet_A_1')
        for tick in range(1, 72001):
            state.update(tick, frames[(tick-1) % 80+1])
        with self.assertRaisesRegex(AssertionError, 'replicated native movement'):
            state.result(72000)

    def test_replan_inside_same_bounded_attempt_keeps_brush_witness(self):
        self.lines = [s.replace('front=3 hitType=0', 'front=0.2 hitType=2').replace('active=1 phase=2 reason=1 began=0', 'active=1 phase=1 reason=1 began=1').replace('delta=0 forward=1', 'delta=2.25 forward=0') if s.startswith('[BotNavigation] local=0 tick=2 ') else s for s in self.lines]
        self.assertEqual(self.audit()['players'][0]['advancesAtLeast2m'], 1)

    def test_new_stuck_attempt_after_gap_cannot_borrow_old_brush_witness(self):
        self.lines = [s.replace('active=1 phase=2', 'active=0 phase=0') if s.startswith('[BotNavigation] local=0 tick=2 ') else s for s in self.lines]
        self.lines = [s.replace('active=1 phase=2 reason=1 began=0', 'active=1 phase=1 reason=2 began=1').replace('delta=0 forward=1', 'delta=2.25 forward=0') if s.startswith('[BotNavigation] local=0 tick=3 ') else s for s in self.lines]
        with self.assertRaisesRegex(AssertionError, 'brush'):
            self.audit()

    def test_teleport_with_continuous_active_rows_starts_new_attempt(self):
        import re
        changed = []
        for line in self.lines:
            match = re.search(r'tick=(\d+)', line)
            if match and int(match[1]) >= 3:
                tick = int(match[1])
                line = re.sub(r'pos=\([^)]*\)', f'pos=({40+tick/5},0,0)', line)
                if line.startswith('[BotNavigation] local=0 tick=3 '):
                    line = line.replace('front=3 hitType=0', 'front=0.2 hitType=2').replace('active=1 phase=2 reason=1 began=0', 'active=1 phase=1 reason=1 began=1').replace('delta=0 forward=1', 'delta=2.25 forward=0')
            changed.append(line)
        self.lines = changed
        with self.assertRaisesRegex(AssertionError, 'brush'):
            self.audit()


class RuntimeEvidenceTests(unittest.TestCase):
    def test_join_only_smoke_cannot_be_promoted_to_full_ai(self):
        from unittest.mock import patch
        with patch.object(m,'audit_runtime',return_value={'nativeJoinOnly':True}), patch.object(m,'audit_stream') as stream:
            with self.assertRaisesRegex(AssertionError,'join-only smoke'):
                m.audit(Path('unused'),Path('unused.dll'),Path('unused.ini'),60)
            stream.assert_not_called()

    def queries(self):
        return [dict(utc=f'2026-10-11T10:{minute:02d}:00Z', status=r'\gamever\1.07\activemod\\numplayers\8', players=''.join(f'\\player_{i}\\Bot{i}' for i in range(8))) for minute in range(3)]

    def test_native_queries_require_duration_and_real_names(self):
        queries = self.queries()
        self.assertEqual(m.audit_queries(queries, {f'Bot{i}' for i in range(8)}, 120)[1], 120)
        with self.assertRaisesRegex(AssertionError, 'query span'):
            m.audit_queries(queries, {f'Bot{i}' for i in range(8)}, 3600)
        queries[1]['players'] = queries[1]['players'].replace('Bot7', 'Impostor')
        with self.assertRaisesRegex(AssertionError, 'identities'):
            m.audit_queries(queries, {f'Bot{i}' for i in range(8)}, 120)

    def test_query_gap_cannot_be_counted_as_continuous_hour(self):
        queries = self.queries()
        queries[2]['utc'] = '2026-10-11T11:01:00Z'
        with self.assertRaisesRegex(AssertionError, 'query gap'):
            m.audit_queries(queries, {f'Bot{i}' for i in range(8)}, 3600)

    def test_wrong_native_version_or_mod_rejected(self):
        for wrong in (r'\gamever\1.10\activemod\\numplayers\8', r'\gamever\1.07\activemod\Cecil\numplayers\8'):
            queries = self.queries()
            queries[0]['status'] = wrong
            with self.assertRaisesRegex(AssertionError, 'version/mod'):
                m.audit_queries(queries, {f'Bot{i}' for i in range(8)}, 120)

    def resources(self):
        return [dict(utc=f'2026-10-11T10:{minute:02d}:00Z', role=role, pid=pid, cpuSeconds=minute+1, privateBytes=1024*1024, workingSet=2*1024*1024, handles=30, threads=4) for minute in range(3) for pid, role in enumerate(('TSE-BotClient', 'TSE-BotClient2', 'server'), 10)]

    def test_resources_cover_all_processes_and_native_duration(self):
        rows = self.resources()
        stats = m.audit_resources(rows, 120)
        self.assertEqual(len(stats), 3)
        self.assertEqual(stats[0]['peakPrivateMiB'], 1)
        with self.assertRaisesRegex(AssertionError, 'resource duration'):
            m.audit_resources(rows, 3600)
        with self.assertRaisesRegex(AssertionError, 'resource roles'):
            m.audit_resources([r for r in rows if r['role'] != 'server'], 120)

    def test_resource_replacement_and_nonfinite_cpu_rejected(self):
        rows = self.resources()
        rows[-1]['pid'] += 20
        with self.assertRaisesRegex(AssertionError, 'resource process replacement'):
            m.audit_resources(rows, 120)
        rows = self.resources()
        rows[-1]['cpuSeconds'] = float('nan')
        with self.assertRaisesRegex(AssertionError, 'resource value'):
            m.audit_resources(rows, 120)

    def test_resources_need_three_distinct_positive_native_pids(self):
        for invalid in (0, -1, 10):
            rows = self.resources()
            for row in rows:
                if row['role'] == 'server': row['pid'] = invalid
            with self.assertRaisesRegex(AssertionError, 'resource process identities'):
                m.audit_resources(rows, 120)


if __name__ == '__main__': unittest.main()
