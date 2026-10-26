import tempfile
from pathlib import Path
import unittest
import build_integrated_gamemp as b

class SourceOverlayTests(unittest.TestCase):
    def fixture(self,base):
        source=base/'source';game=base/'game';source.mkdir();game.mkdir()
        for n in ('Game.cpp','Game.vcxproj','BotDriver.cpp','BotDriver.h','bot_human.h'):(source/n).write_text('new '+n)
        (source/'combat2_weapon.h').write_text('header-only composition')
        (source/'SOURCE_MANIFEST.json').write_text('{"source":"synthetic"}')
        (game/'Game.cpp').write_text('old')
        return source,game
    def test_explicit_overlay_copies_all_source_headers_and_pins_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            source,game=self.fixture(Path(d));manifest=b.stage_source_overlay(source,game)
            self.assertEqual((game/'Game.cpp').read_text(),'new Game.cpp')
            self.assertEqual((game/'combat2_weapon.h').read_text(),'header-only composition')
            self.assertEqual(set(manifest),{'Game.cpp','Game.vcxproj','BotDriver.cpp','BotDriver.h','bot_human.h','combat2_weapon.h'})
            self.assertEqual(manifest['Game.cpp'],b.sha(game/'Game.cpp'))
            self.assertFalse((game/'SOURCE_MANIFEST.json').exists())
    def test_incomplete_or_symlink_source_is_rejected_before_any_copy(self):
        for variant in ('missing','symlink'):
            with self.subTest(variant=variant),tempfile.TemporaryDirectory() as d:
                source,game=self.fixture(Path(d))
                if variant=='missing':(source/'bot_human.h').unlink()
                else:
                    p=source/'combat2_weapon.h';p.unlink();p.symlink_to(game/'Game.cpp')
                with self.assertRaises(ValueError):b.stage_source_overlay(source,game)
                self.assertEqual(list(game.iterdir()),[game/'Game.cpp'])
                self.assertEqual((game/'Game.cpp').read_text(),'old')
    def test_missing_directory_or_source_equal_destination_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            source,game=self.fixture(Path(d))
            for p in (Path(d)/'absent',game):
                with self.assertRaises(ValueError):b.stage_source_overlay(p,game)

if __name__=='__main__':unittest.main()
