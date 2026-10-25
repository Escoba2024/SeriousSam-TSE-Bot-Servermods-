"""Fail-closed acceptance: fixture PASS is not a native release certificate."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).parent
SCRIPT = HERE / 'redstation_gate.py'
STATUS = dict(gamename='serioussamse', gamever='1.07', hostname='ssam.ai | Red Station | Human Bots',
              mapname='Red Station', gametype='Fragmatch', maxplayers='16', difficulty='Hard',
              infiniteammo='1', final='')
RULES = dict(difficulty='Hard', infiniteammo='1', final='')

class RedStationGateTests(unittest.TestCase):
    def check(self, status=None, rules=None):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            for name, value in [('status', STATUS if status is None else status),
                                ('rules', RULES if rules is None else rules)]:
                (base / (name+'.json')).write_text(json.dumps(value), encoding='utf8')
            proc = subprocess.run([sys.executable, str(SCRIPT), '--status-json', str(base/'status.json'),
                                   '--rules-json', str(base/'rules.json')], text=True, capture_output=True)
        return proc

    def test_valid_fixture_not_classified_as_live_release(self):
        res=self.check()
        self.assertEqual(res.returncode,0,res.stderr)
        report=json.loads(res.stdout)
        self.assertEqual(report['verdict'],'SIMULATED_CONFIG_PASS')
        self.assertEqual(report['evidence_class'],'SYNTHETIC_FIXTURE')
        self.assertFalse(report['release_qualified'])

    def test_infinite_ammo_discrepancy_blocks(self):
        res=self.check(status={**STATUS,'infiniteammo':'0'},rules={**RULES,'infiniteammo':'0'})
        self.assertEqual(res.returncode,8,res.stderr)
        self.assertIn('infiniteammo',res.stdout)

    def test_incomplete_or_missing_final_blocks(self):
        for field in ('status','rules'):
            with self.subTest(field=field):
                status,rules=dict(STATUS),dict(RULES)
                (status if field=='status' else rules).pop('final')
                self.assertEqual(self.check(status,rules).returncode,8)

    def test_disagreeing_rules_blocks(self):
        res=self.check(rules={**RULES,'infiniteammo':'0'})
        self.assertEqual(res.returncode,8)
        self.assertIn('inconsistent',res.stdout)

    def test_wrong_map_or_version_blocks(self):
        for key,value in [('mapname','Yodeller'),('gamever','1.10'),('hostname','OldServer')]:
            with self.subTest(key=key):
                self.assertEqual(self.check(status={**STATUS,key:value}).returncode,8)

if __name__=='__main__':unittest.main()
