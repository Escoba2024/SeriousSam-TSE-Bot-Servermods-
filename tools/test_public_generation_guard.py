"""TDD: Public safety guard must not admit P1 A/B on stale Build06 metadata."""
import unittest
from datetime import datetime, timezone, timedelta
from qualify_bot_sessions import validate_public_guard_metadata, assert_exact_public_roster

NOW = datetime(2026, 10, 26, 0, 15, tzinfo=timezone.utc)
GENERATION = 'eight-controlled'
NAMES = ['PublicBot%d' % i for i in range(8)]

def public():
    base = '/srv/tse-experimental-public-20261025/runtime/' + GENERATION
    return {
        'status': 'EXPERIMENTAL_TEST_PASSED',
        'scope': 'PUBLIC_EXPERIMENTAL_AI2_NOT_PRODUCTION_QUALIFIED',
        'expected_names': list(NAMES),
        'bots': 8,
        'processes': {
            'server': {'cwd': base + '/server'},
            'botA': {'cwd': base + '/botA'},
            'botB': {'cwd': base + '/botB'},
        },
    }

def health():
    return {
        'utc': NOW.isoformat(),
        'generation': GENERATION,
        'owned_sync_bad': 0,
        'telemetry_fresh': True,
        'query_fresh': True,
        'processes_verified': True,
        'sync_history_verified': True,
        'status': 'HEALTHY',
    }

class TestPublicGuard(unittest.TestCase):
    def blocked(self, expected, pub=None, hea=None):
        with self.assertRaisesRegex(RuntimeError, expected):
            validate_public_guard_metadata(public() if pub is None else pub, health() if hea is None else hea, now=NOW)

    def test_explicit_fresh_generation_is_eligible_metadata_only(self):
        self.assertEqual(validate_public_guard_metadata(public(), health(), now=NOW), NAMES)

    def test_real_build06_missing_roster_blocks(self):
        p=public()
        del p['expected_names']
        self.blocked('expected_names', p)

    def test_empty_roster_blocks(self):
        p=public()
        p['expected_names']=[]
        self.blocked('expected_names', p)

    def test_duplicate_roster_blocks(self):
        p=public()
        p['expected_names'][4]=p['expected_names'][0]
        self.blocked('expected_names',p)

    def test_stale_health_blocks(self):
        h=health()
        h['utc']=(NOW-timedelta(hours=12)).isoformat()
        self.blocked('stale',hea=h)

    def test_health_missing_generation_blocks(self):
        h=health()
        del h['generation']
        self.blocked('generation',hea=h)

    def test_health_other_generation_blocks(self):
        h=health()
        h['generation']='some-other-run'
        self.blocked('generation',hea=h)

    def test_sync_coverage_unknown_blocks(self):
        h=health()
        h.pop('sync_history_verified')
        self.blocked('sync_history',hea=h)

    def test_healthy_but_sync_error_blocks(self):
        h=health()
        h['owned_sync_bad']=1
        self.blocked('sync',hea=h)

    def test_health_limited_blocks(self):
        h=health()
        h['status']='LIMITED'
        self.blocked('health',hea=h)

    def test_mismatching_public_process_generation_blocks(self):
        p=public()
        p['processes']['botA']['cwd']='/srv/tse-experimental-public-20261025/runtime/eight-foreign/botA'
        self.blocked('generation',p)

    def test_exact_query_roster_only(self):
        self.assertIsNone(assert_exact_public_roster(NAMES,NAMES))

    def test_extraneous_human_blocks(self):
        with self.assertRaisesRegex(RuntimeError,'roster'):
            assert_exact_public_roster(NAMES,NAMES+['Human'])

    def test_missing_bot_blocks(self):
        with self.assertRaisesRegex(RuntimeError,'roster'):
            assert_exact_public_roster(NAMES,NAMES[:7])

    def test_roster_casefold_duplicates_block(self):
        with self.assertRaisesRegex(RuntimeError,'roster'):
            assert_exact_public_roster(NAMES,NAMES[:-1]+[NAMES[0].lower()])

if __name__=='__main__':
    unittest.main()
