#!/usr/bin/env python3
"""Integration overlay contracts; no gameplay claims."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
CAND=ROOT/"poc/candidates/integrated-human-cpu-20261021"
class IntegrationTests(unittest.TestCase):
    def test_materializer_preserves_release_and_refuses_overwrite(self):
        release=ROOT/"poc/release/gamemp"
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in release.iterdir() if p.is_file()}
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"gamemp"
            proc=subprocess.run(["python3",str(CAND/"apply.py"),str(target)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            for name in ("Game.cpp","BotDriver.cpp","BotTelemetry.h"):
                self.assertEqual((target/name).read_bytes(),(CAND/name).read_bytes())
            for name in ("bot_profile.h","bot_perception.h","bot_aim.h","bot_loadout.h","bot_human.h","bot_route.h"):
                self.assertTrue((target/name).is_file(),name+" absent from materialized build")
                self.assertEqual((target/name).read_bytes(),(ROOT/"poc/botcore"/name).read_bytes())
            for name in before:
                if name not in ("Game.cpp","BotDriver.cpp"):
                    self.assertEqual((target/name).read_bytes(),(release/name).read_bytes())
            again=subprocess.run(["python3",str(CAND/"apply.py"),str(target)],capture_output=True)
            self.assertNotEqual(again.returncode,0)
        self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in release.iterdir() if p.is_file()})
    def test_flags_and_all_runtime_paths_coexist(self):
        text=(CAND/"BotDriver.cpp").read_text()
        self.assertFalse("<<<<<<<" in text,"unresolved source conflict")
        for symbol in ("bot_bHumanAI","bot_bDiag","bot_iScanInterval","bot_fTargetRange","bot_iMaxLosRays","bot_iObstacleInterval","bot_iTelemetry"):
            self.assertIn('DeclareSymbol("user ',text)
            self.assertIn("&"+symbol,text)
        for marker in ("human.Step(","BotTelemetry_Tick(","BotTelemetry_Action(iLP)","ppls->SetAction(pa)","BotCombatVisible(player,cached)"):
            self.assertIn(marker,text)
        self.assertEqual(text.count("const BOOL bFullScan="),1)
        human=text[text.index("if (bot_bHumanAI) {",text.index("if (automatic) {")):]
        human=human[:human.index("} else if (player!=NULL && deathmatch")]
        self.assertNotIn("bFullScan",human)
        self.assertIn("human.PlanLosQueries",human)
    def test_render_bypass_keeps_native_timer(self):
        game=(CAND/"Game.cpp").read_text()
        self.assertLess(game.index("if (bot_bNullRender"),game.index("CTSingleLock slBotRender"))
        self.assertIn("BotDriver_HandleTimer",game)
        self.assertIn("bot_bHumanAI      = FALSE",(CAND/"BotDriver.cpp").read_text())
if __name__=="__main__": unittest.main()
