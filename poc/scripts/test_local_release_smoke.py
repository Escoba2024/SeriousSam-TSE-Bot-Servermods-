import importlib.util
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('production_smoke', Path(__file__).with_name('Test-LocalReleaseSmoke.py'))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    lines=['[BotDriver] local player 0 (player index 2) is now bot-driven: TSE_Fleet_A_1\n']
    for tick in range(20, 261, 20):
        lines.extend((f'[BotCombat] local=0 tick={tick} self=2 alive=1 dm=1 visible=1 target=3 weapon=2 ready=1 move=1 yawDelta=2.25 pitchDelta=0\n',
            f'[BotNavigation] local=0 tick={tick} alive=1 hold=0 front=3 hitType=0 left=3 right=3 active=0 phase=0 delta=0 forward=1 pos=({tick/20},0,0)\n',
            f'[BotDriver] bot0 tick={tick} pos=({tick/20},0,0) heading=0 fire=0\n'))
    return lines


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'native.log'
        self.lines=fixture()

    def tearDown(self): self.tmp.cleanup()

    def audit(self):
        self.path.write_text(''.join(self.lines),encoding='utf-8')
        return m.audit_sparse_stream(self.path,expected_slots=1,min_samples=12)

    def test_valid_sparse_production_evidence(self):
        self.assertEqual(self.audit()[0]['completeSamples'],13)

    def test_production_must_exclude_local_targets(self):
        self.lines=[line.replace('target=3','target=2') for line in self.lines]
        with self.assertRaisesRegex(AssertionError,'local target'): self.audit()

    def test_missing_submitted_action_rejected(self):
        self.lines=[line for line in self.lines if not line.startswith('[BotDriver] bot0 tick=60 ')]
        with self.assertRaisesRegex(AssertionError,'matching sparse'): self.audit()

    def test_sparse_log_cannot_claim_movement_from_yaw_alone(self):
        import re
        self.lines=[re.sub(r'pos=\([^)]*\)','pos=(0,0,0)',line) for line in self.lines]
        with self.assertRaisesRegex(AssertionError,'native movement'): self.audit()

    def test_sparse_illegal_turn_forward_rejected(self):
        self.lines=[line.replace('active=0 phase=0','active=1 phase=1') if line.startswith('[BotNavigation] local=0 tick=40 ') else line for line in self.lines]
        with self.assertRaisesRegex(AssertionError,'turn also advances'): self.audit()

    def test_sparse_illegal_combat_rotation_rejected(self):
        self.lines=[line.replace('yawDelta=2.25','yawDelta=nan') for line in self.lines]
        with self.assertRaisesRegex(AssertionError,'combat action bounds'): self.audit()

    def test_off_period_target_change_is_also_checked(self):
        for bad in ('target=2','target=3 weapon=2 ready=1 move=1 yawDelta=nan pitchDelta=0'):
            self.lines=fixture()
            extra='[BotCombat] local=0 tick=21 self=2 alive=1 dm=1 visible=1 '+bad+'\n'
            self.lines.insert(4,extra)
            with self.assertRaises(AssertionError): self.audit()

    def test_off_period_navigation_is_also_checked(self):
        self.lines.insert(4,'[BotNavigation] local=0 tick=21 alive=1 hold=0 front=3 hitType=0 left=3 right=3 active=1 phase=1 delta=0 forward=1 pos=(1,0,0)\n')
        with self.assertRaisesRegex(AssertionError,'turn also advances'): self.audit()

    def test_partial_shutdown_row_does_not_hide_invalid_values(self):
        self.lines.append('[BotCombat] local=0 tick=280 self=2 alive=1 dm=1 visible=1 target=3 weapon=2 ready=1 move=1 yawDelta=nan pitchDelta=0\n')
        with self.assertRaisesRegex(AssertionError,'combat action bounds'): self.audit()

    def test_only_exact_canonical_production_startup_is_accepted(self):
        startup=Path(self.tmp.name)/'startup.ini'
        original=Path(m.__file__).with_name('LocalBotRelease.ini').read_bytes()
        startup.write_bytes(original)
        m.assert_production_startup(startup)
        startup.write_bytes(original.replace(b'bot_iLogEvery = 20',b'bot_iLogEvery = 1'))
        with self.assertRaisesRegex(AssertionError,'canonical production startup'):
            m.assert_production_startup(startup)


if __name__=='__main__': unittest.main()
