#!/usr/bin/env python3
"""Materialize the combined unqualified overlay without changing release files."""
import hashlib
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
RELEASE=ROOT/"poc/release/gamemp"
PINS={
"Game.cpp":"01dfa59857df4953d3a89096cd8049b9ba022f81e388c0dfc52b4826909474b6",
"BotDriver.cpp":"b5d3290391b2504cce96529155b4072361fed0319a80ad1695707e36a9165c64",
"BotDriver.h":"82c8282d1426177031cdaa3f140fd084c2ddcf51cb74bfd694e49af90e8d0a3d"}
def main():
    if len(sys.argv)!=2:
        raise SystemExit("usage: apply.py NEW_TARGET_DIRECTORY")
    target=Path(sys.argv[1]).resolve()
    if target.exists():
        raise SystemExit("target already exists; refusing overwrite")
    for name,digest in PINS.items():
        if hashlib.sha256((RELEASE/name).read_bytes()).hexdigest()!=digest:
            raise SystemExit("release provenance mismatch: "+name)
    shutil.copytree(RELEASE,target)
    for name in ("Game.cpp","BotDriver.cpp","BotTelemetry.h"):
        shutil.copy2(HERE/name,target/name)
    for name in ("bot_profile.h","bot_perception.h","bot_aim.h","bot_loadout.h","bot_human.h"):
        shutil.copy2(ROOT/"poc/botcore"/name,target/name)
    print("UNQUALIFIED candidate source:",target)
if __name__=="__main__": main()
