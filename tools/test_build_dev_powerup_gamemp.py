# SPDX-License-Identifier: GPL-2.0-only
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import build_dev_powerup_gamemp as builder

class OverlayTests(unittest.TestCase):
    def test_hook_is_only_in_newgame(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=builder.stage_server_overlay(Path(tmp)/'overlay')
            text=(p/'Game.cpp').read_text()
            call=text.index('DevFilterPowerups(dem_bPlay);')
            self.assertLess(text.index('BOOL CGame::NewGame('),call)
            self.assertLess(call,text.index('BOOL CGame::JoinGame('))
            self.assertEqual(text.count('DevFilterPowerups(dem_bPlay);'),1)

    def test_rejects_newgame_anchor_drift_before_patching_join(self):
        original=builder.builder.materialize_candidate_overlay
        def drift(target):
            original(target)
            p=Path(target)/'Game.cpp';text=p.read_bytes()
            text=text.replace(b'  // setup players from given indices\r\n  SetupLocalPlayers();',b'  // changed NewGame formatting\r\n  SetupLocalPlayers();',1)
            p.write_bytes(text)
        with tempfile.TemporaryDirectory() as tmp,patch.object(builder.builder,'materialize_candidate_overlay',side_effect=drift):
            with self.assertRaisesRegex(ValueError,'NewGame'):
                builder.stage_server_overlay(Path(tmp)/'overlay')
if __name__=='__main__':unittest.main()
