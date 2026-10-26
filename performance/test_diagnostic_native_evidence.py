"""Synthetic offline fixtures for diagnostic evidence, never native acceptance."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

import diagnostic_native_evidence as e


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ids = {'gamer-%03d' % i for i in range(8)}
        self.roles = self.ids | {'server', 'vanilla'}
        self.config = {'max_log_mib': 1, 'identities': [{'id': i} for i in sorted(self.ids)]}
        self.harness = {name: 'a' * 64 for name in (
            'qualify_bot_sessions.py', 'bot_session_executor.py', 'bot_session_runtime.py',
            'bot_sessions.py', 'qualify_integrated_wine.py')}
        (self.root/'source-sha256.json').write_text(json.dumps(self.harness))
        self.result = {
            'status': 'PASS_LIMITED_SESSION_LIFECYCLE', 'scope': e.SCOPE,
            'dll_sha256': 'd' * 64, 'max_bots': 8, 'peak_playing': 8,
            'original_client': True, 'measured_s': 1500, 'elapsed_s': 1530,
            'all_bots_drained': True, 'new_throttled_periods': 0,
            'cgroup': '/sys/fs/cgroup/tse-sessions-42',
            'utc': datetime.fromtimestamp(1700001540, timezone.utc).isoformat(),
            'telemetry': {i: [{'playing_s': 1500, 'reports': [{
                'verdict': 'ACTIVE_OK', 'exit_code': 0, 'lp_median': 1,
                'tick_hz_median': 20, 'render_skip_total': 1500, 'render_draw_total': 0,
                'config': {'nullrender': '1'}}]}] for i in self.ids},
            'cleanup': [{'role': r, 'errors': []} for r in self.roles],
            'unmounts': [{'path': str(self.root/(prefix+r)), 'exitcode': 0}
                         for r in self.roles for prefix in ('', 'prefix-')],
        }
        self.guard = {'status': 'FINISHED', 'child_exitcode': 0, 'error': None,
                      'public_guard_mode': 'USER_DISABLED', 'public_disabled': True,
                      'samples': [{'at': 1700000000 + i*5, 'available_mib': 1100,
                                   'disk_free_gib': 8.3, 'host_busy_percent': 60} for i in range(310)]}
        for role in self.roles:
            upper = self.root/'layers'/role/'upper'
            upper.mkdir(parents=True)
            (upper/('Dedicated_BotTest.log' if role == 'server' else 'SeriousSam.log')).write_text('benign synthetic log\n')
            if role in self.ids:
                (upper/'Bin').mkdir()
                (upper/'Bin/BotTelemetry.csv').write_text('synthetic raw telemetry\n')
        self.rows = [{'elapsed_s': at, 'active': 8, 'population': 9,
                      'processes': {r: {'start_ticks': n+1, 'pss_mib': 1} for n, r in enumerate(sorted(self.roles))},
                      'decisions': [{'id': i, 'action': 'healthy'} for i in sorted(self.ids)]}
                     for at in range(1501)]
        self.write_rows()

    def write_rows(self):
        (self.root/'samples.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in self.rows))

    def verdict(self):
        return e.validate_probe_evidence(root=self.root, result=self.result, guard=self.guard,
            config=self.config, census={'clean': True}, candidate_sha256='d'*64,
            bound_cgroup='/sys/fs/cgroup/tse-sessions-42', harness_sha256=self.harness)

    def test_positive_is_diagnostic_only_with_all_evidence(self):
        result = self.verdict()
        self.assertEqual(result['status'], 'DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE')
        self.assertFalse(result['m1_complete'])
        self.assertEqual(result['log_inventory']['complete_log_count'], 10)
        self.assertEqual(result['log_inventory']['raw_telemetry_count'], 8)
        self.assertEqual(result['full_population']['longest_contiguous_full_population_s'], 1500)
        self.assertTrue(result['log_inventory']['independent_sync_scan_complete'])
        self.assertNotIn('benign synthetic log', json.dumps(result))

    def test_omitted_log_bound_uses_runner_default_without_mutating_config(self):
        del self.config['max_log_mib']
        path = self.root/'layers/vanilla/upper/SeriousSam.log'
        path.write_bytes(b'x' * (1024 ** 2 + 1))
        verdict = self.verdict()
        self.assertEqual(verdict['status'], 'DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE')
        self.assertFalse(verdict['m1_complete'])
        self.assertEqual(verdict['log_inventory']['complete_log_count'], 10)
        self.assertNotIn('max_log_mib', self.config)
        path.write_bytes(b'x' * (32 * 1024 ** 2) + b'X')
        with self.assertRaisesRegex(RuntimeError, 'COMPLETE_LOG_INVALID'):
            self.verdict()

    def test_explicit_invalid_log_bounds_do_not_use_default(self):
        for value in (None, True, False, 0, -1, 1.0, '32', 129):
            with self.subTest(value=value):
                self.config['max_log_mib'] = value
                with self.assertRaisesRegex(RuntimeError, 'MAX_LOG_CONFIG_INVALID'):
                    self.verdict()

    def test_explicit_producer_upper_log_bound_is_accepted(self):
        self.config['max_log_mib'] = 128
        self.assertEqual(self.verdict()['log_inventory']['complete_log_count'], 10)

    def test_every_required_schema_field_missing_blocks(self):
        original = copy.deepcopy(self.result)
        for key in ['scope','dll_sha256','max_bots','peak_playing','original_client','measured_s',
                    'elapsed_s','all_bots_drained','new_throttled_periods','cgroup']:
            with self.subTest(key=key):
                self.result = copy.deepcopy(original)
                del self.result[key]
                with self.assertRaises(RuntimeError): self.verdict()
        self.result = original

    def test_wrong_candidate_peak_throttling_and_cgroup_block(self):
        for field, value in [('dll_sha256','0'*64),('peak_playing',7),('new_throttled_periods',1),
                             ('cgroup','/sys/fs/cgroup/tse-sessions-43'),('measured_s',1499),
                             ('elapsed_s',float('nan'))]:
            with self.subTest(field=field):
                original = self.result[field]
                self.result[field] = value
                with self.assertRaises(RuntimeError): self.verdict()
                self.result[field] = original

    def test_guard_mode_and_reserve_and_three_cpu_highs_block(self):
        old = copy.deepcopy(self.guard)
        for key, value in [('public_guard_mode','LIVE_PUBLIC'),('public_disabled',False),('child_exitcode',1)]:
            with self.subTest(key=key):
                self.guard = copy.deepcopy(old); self.guard[key] = value
                with self.assertRaises(RuntimeError): self.verdict()
        self.guard = copy.deepcopy(old); self.guard['samples'][3]['available_mib'] = 767
        with self.assertRaises(RuntimeError): self.verdict()
        self.guard = copy.deepcopy(old)
        for i in (3,4,5): self.guard['samples'][i]['host_busy_percent'] = 85
        with self.assertRaises(RuntimeError): self.verdict()
        self.guard = old

    def test_guard_cannot_claim_1500_seconds_from_two_final_samples(self):
        self.guard['samples'] = self.guard['samples'][-2:]
        with self.assertRaisesRegex(RuntimeError, 'GUARD_TIME_COVERAGE'): self.verdict()

    def test_guard_time_must_cover_actual_result_timestamp(self):
        self.result['utc'] = '1970-01-01T00:00:00+00:00'
        with self.assertRaisesRegex(RuntimeError, 'GUARD_TIME_COVERAGE'): self.verdict()

    def test_each_population_process_decision_or_generation_error_breaks_continuity(self):
        original = copy.deepcopy(self.rows)
        for variant in ['population','roles','generation','healthy','missing_decision','pss']:
            with self.subTest(variant=variant):
                self.rows = copy.deepcopy(original)
                row = self.rows[750]
                if variant == 'population': row['population'] = 8
                elif variant == 'roles': del row['processes']['server']
                elif variant == 'generation': row['processes']['server']['start_ticks'] += 1
                elif variant == 'healthy': row['decisions'][0]['action'] = 'joining'
                elif variant == 'missing_decision': row['decisions'].pop()
                elif variant == 'pss': row['processes']['server']['pss_mib'] = 0
                self.write_rows()
                with self.assertRaisesRegex(RuntimeError,'FULL_POPULATION_BELOW'): self.verdict()
        self.rows = original; self.write_rows()

    def test_active_eight_only_is_not_population_proof(self):
        self.rows = [{'elapsed_s': i, 'active': 8} for i in range(1501)]
        self.write_rows()
        with self.assertRaisesRegex(RuntimeError,'FULL_POPULATION_BELOW'): self.verdict()

    def test_nonmonotonic_time_and_long_sample_gap_block(self):
        original = copy.deepcopy(self.rows)
        self.rows[750]['elapsed_s'] = 749; self.write_rows()
        with self.assertRaises(RuntimeError): self.verdict()
        self.rows = original[:749]+original[760:]; self.write_rows()
        with self.assertRaisesRegex(RuntimeError,'FULL_POPULATION_BELOW'): self.verdict()

    def test_each_sync_marker_anywhere_in_complete_log_blocks(self):
        path = self.root/'layers/vanilla/upper/SeriousSam.log'
        for marker in e.MARKERS:
            with self.subTest(marker=marker):
                path.write_text('x'*100000+marker+' late end')
                with self.assertRaisesRegex(RuntimeError,'INDEPENDENT_SYNC_SCAN_NOT_CLEAN'): self.verdict()
        path.write_text('benign\n')

    def test_missing_log_is_not_zero_errors(self):
        path = self.root/'layers/vanilla/upper/SeriousSam.log'
        path.rename(path.with_suffix('.retained'))
        with self.assertRaises(RuntimeError): self.verdict()

    def test_missing_raw_telemetry_is_not_accepted(self):
        path = self.root/'layers'/sorted(self.ids)[0]/'upper/Bin/BotTelemetry.csv'
        path.rename(path.with_suffix('.retained'))
        with self.assertRaisesRegex(RuntimeError, 'RAW_TELEMETRY_MISSING'): self.verdict()

    def test_later_bad_telemetry_report_cannot_hide_behind_one_good_report(self):
        one = self.result['telemetry'][sorted(self.ids)[0]][0]
        report = copy.deepcopy(one['reports'][0]); report['verdict'] = 'INACTIVE'
        one['reports'].append(report)
        with self.assertRaises(RuntimeError): self.verdict()

    def test_wrong_unmount_paths_or_duplicate_cleanup_roles_block(self):
        self.result['unmounts'][0]['path'] = '/different/resource'
        with self.assertRaises(RuntimeError): self.verdict()

    def test_source_receipt_mismatch_blocks(self):
        (self.root/'source-sha256.json').write_text('{"qualify_bot_sessions.py":"wrong"}')
        with self.assertRaisesRegex(RuntimeError,'PRODUCER_SOURCE_RECEIPT'): self.verdict()


if __name__ == '__main__':
    unittest.main()
