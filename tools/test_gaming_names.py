"""Portable safety/identity contracts; no native rendering claim."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GamingNames(unittest.TestCase):
    def setUp(self):
        path = ROOT / 'tools/gaming_names.py'
        self.assertTrue(path.exists(), 'name validator and fleet allocator not implemented')
        spec = importlib.util.spec_from_file_location('gaming_names', path)
        self.g = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.g)

    def test_original_decoder_supported_cases_and_flash_rejection(self):
        for raw, visible in [('PlainName', 'PlainName'), ('^cFF0000ReaPer^r', 'ReaPer'),
                             ('^bRaven^B^r', 'Raven'), ('^iRaven^I^r', 'Raven'),
                             ('^b^iNeCrO^I^B^r', 'NeCrO'),
                             ('^cFFFFFFxX_^cFF0000RaVeN^r', 'xX_RaVeN')]:
            self.assertEqual(self.g.validate_native(raw), visible)
        for raw in ['^f3NIGHT^F^r', '^f3^c00FF00NIGHT^F^r', '^f0X^F^r']:
            with self.assertRaises(ValueError):
                self.g.validate_native(raw)

    def test_untrusted_name_cannot_become_config_command(self):
        for raw in ['N;Quit()', 'N"', 'N\\player_0', 'N\nX', 'N\rX', 'N\x00X',
                    'N`id`', 'N$(id)', 'N//', 'N\tX', 'Né', ' N', 'N ', '',
                    '^xN^r', '^c123N^r', '^c123456^r', '^bN', '^bN^r',
                    '^BN^r', 'N^rX', 'A'*23, '^c123456'+'A'*22+'^b^B^r']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.g.validate_native(raw)
        self.assertEqual(self.g.validate_native('[EU] Nyro-7'), '[EU] Nyro-7')
        self.assertEqual(self.g.validate_native('^c123456'+'A'*22+'^r'), 'A'*22)

    def test_collision_after_native_format_removal_and_casefold(self):
        for names in [['Raven', 'rAvEn'], ['Raven', '^bRAVEN^B^r'],
                      ['^c123456Raven^r', '^iRaven^I^r']]:
            with self.assertRaises(ValueError):
                self.g.validate_pool(names)

    def test_bundle_preserves_208_and_adds_exactly_250(self):
        data = ROOT / 'poc/scripts'
        baseline = json.loads((data/'GamingNicknames.baseline.json').read_text())
        merged = json.loads((data/'GamingNicknames.json').read_text())
        additions = json.loads((data/'GamingNicknames.additions.json').read_text())
        self.assertEqual(len(baseline), 208)
        self.assertEqual(len(additions), 250)
        self.assertEqual(len(merged), 458)
        self.assertEqual(merged[:208], baseline)
        self.assertEqual(merged[208:], [a['nickname'] for a in additions])
        self.g.validate_pool(merged)
        self.g.validate_pool([a['native_name'] for a in additions] + baseline)
        self.assertEqual(len({a['name_id'] for a in additions}), 250)
        self.assertTrue(any(a['native_name']==a['nickname'] for a in additions))
        for code in ('^c', '^b', '^i'):
            self.assertTrue(any(code in a['native_name'] for a in additions))
        self.assertFalse(any('^f' in a['native_name'] for a in additions))
        self.g.verify_bundle(data)

    def test_allocate_globally_avoids_active_names_and_retains_ids(self):
        catalog = self.g.make_catalog(['Raven', 'Birch', 'Kestrel', 'Moth'])
        ids = ['public-1:botA:0', 'public-2:botB:3']
        allocated = self.g.allocate(catalog, ids, occupied_names=['^bRAVEN^B^r'])
        self.assertEqual(set(allocated), set(ids))
        self.assertEqual(len({x['nickname'].lower() for x in allocated.values()}), 2)
        self.assertNotIn('raven', {x['nickname'].lower() for x in allocated.values()})
        self.assertEqual(allocated, self.g.allocate(catalog, list(reversed(ids)), occupied_names=['RAVEN']))
        extended = self.g.allocate(catalog, ids+['dev:botA:0'], occupied_names=['Raven'], existing=allocated)
        self.assertEqual({k:extended[k] for k in ids}, allocated)
        for k, row in extended.items():
            self.assertEqual(row['bot_id'], k)
            self.assertNotEqual(row['bot_id'], row['name_id'])
        with self.assertRaises(ValueError):
            self.g.allocate(catalog, ids, occupied_names=['Raven','Birch','Kestrel','Moth'])
        with self.assertRaises(ValueError):
            self.g.allocate(catalog, [ids[0], ids[0]])
        with self.assertRaises(ValueError):
            self.g.allocate(catalog, ['x;Quit()'])
        with self.assertRaises(ValueError):
            self.g.allocate(catalog, ids, occupied_names=[next(iter(allocated.values()))['nickname']], existing=allocated)

    def test_external_occupied_display_names_are_not_new_name_candidates(self):
        catalog=self.g.make_catalog(['Raven','Birch'])
        got=self.g.allocate(catalog,['dev:0'],occupied_names=['RAVEN ', 'A'*40, 'Joueuré', 'Name;Quit()'])
        self.assertEqual(got['dev:0']['nickname'],'Birch')
        with self.assertRaises(ValueError):
            self.g.allocate(catalog,['dev:0'],occupied_names=['^f3Raven^F^r'])

    def test_bundle_regenerates_and_tampering_is_rejected(self):
        source = ROOT/'poc/scripts'
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)
            for name in ('GamingNicknames.baseline.json','GamingNicknames.additions.source.json'):
                (target/name).write_bytes((source/name).read_bytes())
            self.g.generate_bundle(target)
            for name in ('GamingNicknames.json','GamingNicknames.additions.json','GamingNicknames.metadata.json'):
                self.assertEqual((source/name).read_bytes(), (target/name).read_bytes())
            pool=json.loads((target/'GamingNicknames.json').read_text())
            pool[-1]='InjectedAlias'
            (target/'GamingNicknames.json').write_text(json.dumps(pool))
            with self.assertRaises(ValueError):
                self.g.verify_bundle(target)

    def test_cli_emits_proposal_and_rejects_bad_request_without_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            request=Path(tmp)/'request.json'
            request.write_text(json.dumps(dict(bot_ids=['dev:0','public:0'],occupied_names=['Avaro'])))
            command=[sys.executable,'-B',str(ROOT/'tools/gaming_names.py'),'--request',str(request)]
            run=subprocess.run(command,text=True,capture_output=True)
            self.assertEqual(run.returncode,0,run.stderr)
            result=json.loads(run.stdout)
            self.assertEqual(set(result),{'dev:0','public:0'})
            self.assertNotIn('Avaro',[r['nickname'] for r in result.values()])
            request.write_text(json.dumps(dict(bot_ids=['dev:0','dev:0'])))
            run=subprocess.run(command,text=True,capture_output=True)
            self.assertNotEqual(run.returncode,0)
            self.assertEqual(run.stdout,'')


if __name__ == '__main__':
    unittest.main()
