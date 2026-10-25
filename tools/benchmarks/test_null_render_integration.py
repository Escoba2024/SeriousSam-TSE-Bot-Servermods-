"""Static release guards for the opt-in retail 1.07 null-render candidate.

These are not a substitute for a native Windows/Wine compile and join/CRC test.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'poc/release/gamemp/Game.cpp'
PROFILE = ROOT / 'poc/profiles/HetznerNullRender.ini'

class NullRenderIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text()
        cls.profile = PROFILE.read_text()

    def test_flag_defaults_off_and_exposed_to_script(self):
        self.assertIn('static INDEX bot_bNullRender = FALSE;', self.source)
        self.assertIn('DeclareSymbol("user INDEX bot_bNullRender;", &bot_bNullRender)', self.source)

    def test_opt_in_render_skip_precedes_timer_lock(self):
        start = self.source.index('void CGame::GameRedrawView(')
        block = self.source[start:self.source.index('void CGame::GameMainLoop(', start)]
        self.assertLess(block.index('if (bot_bNullRender && gm_bGameOn'), block.index('CTSingleLock slBotRender'))
        self.assertIn('!_pNetwork->IsServer()', block)
        self.assertIn('_fnmThumb==""', block)
        self.assertRegex(block, r'if \(bot_bNullRender && gm_bGameOn.*\) \{\s*return;\s*\}')

    def test_timer_and_network_loop_unchanged(self):
        self.assertIn('if (BotDriver_HandleTimer(this)) return;', self.source)
        self.assertIn('BotDriver_HandleReconnect(this)', self.source)

    def test_profile_is_opt_in_and_fps_bounded(self):
        self.assertIn('bot_bNullRender=1;', self.profile)
        self.assertIn('sam_iMaxFPSActive=20;', self.profile)
        self.assertIn('sam_iMaxFPSInactive=10;', self.profile)
        self.assertIn('sam_bPauseOnMinimize=0;', self.profile)

if __name__ == '__main__':
    unittest.main()
