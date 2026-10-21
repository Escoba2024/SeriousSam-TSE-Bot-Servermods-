"""Static guards for the P0 diagnostic / P3 throttle patch candidates.

The patches are proposals, not applied sources. Each test applies them to a
temp copy of the GameMP tree (via `git apply`, which works like patch(1)
outside a repository) and asserts the required markers. This is NOT a compile
or runtime proof; MSBuild + native acceptance gates stay mandatory
(see AGENTS.md and docs/coordination/TECHNICAL_HANDOFF-2026-10-21-cpu-opt.md).
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "poc" / "release" / "gamemp" / "BotDriver.cpp"
PATCH_0008 = ROOT / "poc" / "patch" / "0008-gamemp-botdriver-diagnostics.patch"
PATCH_0009 = ROOT / "poc" / "patch" / "0009-gamemp-bot-ai-throttle.patch"


def _patched_source(patches) -> str:
    """Apply patches in order to a temp copy of the GameMP source tree."""
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        rel = Path("poc") / "release" / "gamemp"
        (tree / rel).mkdir(parents=True)
        shutil.copyfile(SOURCE, tree / rel / "BotDriver.cpp")
        for patch in patches:
            subprocess.run(["git", "apply", str(patch)], cwd=str(tree), check=True)
        return (tree / rel / "BotDriver.cpp").read_text(encoding="latin-1")


class Patch0008DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.source = _patched_source([PATCH_0008])

    def test_patch_applies_to_current_source(self):
        self.assertIn("[BotDiag] init: bot symbols declared", self.source)

    def test_heartbeat_sits_before_every_gate(self):
        start = self.source.index("BOOL BotDriver_HandleTimer")
        block = self.source[start : start + 3000]
        self.assertLess(block.index("if (bot_bDiag) {"), block.index("InterlockedExchange"))

    def test_symbols_declared_and_opt_in(self):
        self.assertIn("static INDEX bot_bDiag = FALSE;", self.source)
        self.assertIn('DeclareSymbol("user INDEX bot_bDiag;"', self.source)
        self.assertIn('DeclareSymbol("user INDEX bot_iDiagEvery;"', self.source)
        self.assertIn('GetINDEX("sam_iMaxFPSActive")', self.source)
        self.assertIn('GetINDEX("sam_iMaxFPSInactive")', self.source)
        self.assertIn('GetINDEX("snd_iFormat")', self.source)

    def test_local_player_mask_reads_local_players(self):
        self.assertIn("lp_pplsPlayerSource!=NULL) iMask|=(1L<<iLP);", self.source)


class Patch0009AiThrottleTests(unittest.TestCase):
    def setUp(self):
        # 0009 is a stacked patch: it applies on top of 0008.
        self.source = _patched_source([PATCH_0008, PATCH_0009])

    def test_throttle_vars_default_to_current_behavior(self):
        self.assertIn("static INDEX bot_iScanInterval = 1;", self.source)
        self.assertIn("static FLOAT bot_fTargetRange  = 0.0f;", self.source)
        self.assertIn("static INDEX bot_iMaxLosRays   = 0;", self.source)
        self.assertIn("static INDEX bot_iObstacleInterval = 1;", self.source)

    def test_cached_target_scan_and_nearest_first_rays_present(self):
        self.assertIn("bFullScan=bot_iScanInterval<=1", self.source)
        self.assertIn("nearest-first", self.source)
        self.assertIn("bot_iObstacleInterval<=1", self.source)

    def test_throttle_symbols_declared(self):
        self.assertIn('DeclareSymbol("user INDEX bot_iScanInterval;"', self.source)
        self.assertIn('DeclareSymbol("user FLOAT bot_fTargetRange;"', self.source)
        self.assertIn('DeclareSymbol("user INDEX bot_iMaxLosRays;"', self.source)
        self.assertIn('DeclareSymbol("user INDEX bot_iObstacleInterval;"', self.source)

    def test_action_pipeline_unchanged(self):
        # The bot still emits exactly one SetAction per local player and tick.
        self.assertIn("ppls->SetAction(pa);", self.source)
        self.assertIn("ctl_ComposeActionPacket(ppls->pls_pcCharacter, pa, FALSE);", self.source)


class RepoStateTests(unittest.TestCase):
    def test_repo_source_is_unpatched(self):
        src = SOURCE.read_text(encoding="latin-1")
        self.assertNotIn("[BotDiag]", src)
        self.assertNotIn("bot_iScanInterval", src)


if __name__ == "__main__":
    unittest.main()
