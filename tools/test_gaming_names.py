import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
import gaming_names as g


class GamingNames(unittest.TestCase):
    def test_pool_and_weighted_persistent_assignments(self):
        pool = json.loads((Path(__file__).parents[1]/'poc/scripts/GamingNicknames.json').read_text())
        names = g.assign(pool, 160, seed=107, advanced_styles=False)
        self.assertEqual(len(names), 160)
        self.assertEqual(len({n['nickname'].casefold() for n in names}), 160)
        self.assertEqual(names, g.assign(pool, 160, seed=107, advanced_styles=False))
        self.assertGreater(len({n['native_name'] for n in names if '^c' in n['native_name']}), 40)
        for n in names:
            self.assertEqual(g.validate_native(n['native_name']), n['nickname'])
            self.assertNotRegex(n['nickname'], r'(?i)^(?:BOT[_-]?|\[BOT\])')
            self.assertLessEqual(len(n['native_name'].encode('ascii')), 32)
            self.assertLessEqual(len(n['nickname']), 22)
            self.assertNotRegex(n['native_name'], r'\^[bif]')

    def test_full_codes_and_effect_reset(self):
        self.assertEqual(g.validate_native('^b^i^cFF00FFNeCrO^I^B^r'), 'NeCrO')
        with self.assertRaises(ValueError):g.validate_native('^f3^c00FF00N1GHT^F^r')
        self.assertEqual(g.validate_native('^f3^c00FF00N1GHT^F^r',flash_probe=True), 'N1GHT')
        advanced=g.assign(['Raven','Nightjar','ReaPer'],3,seed=107,advanced_styles=True)
        self.assertTrue(all('^f' not in n['native_name'] for n in advanced))
        for n in ['^c123Foo', '^fXName^r', '^xName^r', '^oName^r', '^bName',
                  'Name;Quit()', 'Name\\player_0\\Fake', 'N\nX', '^c123456^r',
                  'A'*23, '^b'+'A'*22+'^B^c123456^r', ' Name', 'N^rX']:
            with self.subTest(n=n), self.assertRaises(ValueError): g.validate_native(n)

    def test_formats_fit_without_truncating_tokens(self):
        rng = random.Random(1)
        short=g.decorate('RAZE',rng,'multi')
        self.assertEqual(short.count('^c'),3)
        self.assertEqual(g.validate_native(short),'RAZE')
        for style in g.STYLES:
            for name in ['ReaPer', 'xX_RaVeN_Xx', 'TwentyTwoLetterNameXYZ']:
                n = g.decorate(name, rng, style)
                self.assertEqual(g.validate_native(n), name)

    def test_visible_collisions_and_prefixes_are_rejected(self):
        for pool in [['Raven','raven'], ['BOT_Raven'], ['[BOT]Raven'], ['BOT-Raven'], ['BOTRaven']]:
            with self.assertRaises(ValueError): g.assign(pool, 1, seed=1)

    def test_cli_generates_disabled_reusable_config_and_refuses_overwrite(self):
        from bot_sessions import validate_config
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'pool.json'
            cmd=[sys.executable,g.__file__,'--seed','107','--count','150','--output',str(target)]
            run=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            c=validate_config(json.loads(target.read_text()))
            self.assertFalse(c['enabled']);self.assertFalse(c['colors_enabled'])
            self.assertEqual(len(c['identities']),150)
            original=target.read_bytes()
            self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertEqual(target.read_bytes(),original)


if __name__ == '__main__': unittest.main()
