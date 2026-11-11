#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build a separate default-off server candidate; installs nothing.

Uses the existing pinned Retail-107 builder. Does not change Cecil048 source
or artifacts: only the generated server overlay receives this hook.
"""
import argparse
from pathlib import Path
import shutil
import build_supply_gamemp as builder
ROOT=Path(__file__).resolve().parents[1]

def stage_server_overlay(target):
    target=Path(target)
    builder.materialize_candidate_overlay(target)
    feature=ROOT/'poc/candidates/dev-powerup-filter-20261111'
    for name in ('DevPowerupPolicy.h','DevPowerupFilter.h'):
        shutil.copy2(feature/name,target/name)
    game=target/'Game.cpp'
    text=game.read_bytes()
    patches=[
      (b'#include "BotTelemetry.h"',b'#include "BotTelemetry.h"\r\n#include "DevPowerupFilter.h"'),
      (b'  _pShell->DeclareSymbol("persistent user INDEX gam_iBlood;',b'  _pShell->DeclareSymbol("user INDEX dev_bRemoveDamageAndInvisibility;", &dev_bRemoveDamageAndInvisibility);\r\n  _pShell->DeclareSymbol("persistent user INDEX gam_iBlood;'),
      (b'  // setup players from given indices\r\n  SetupLocalPlayers();',b'  DevFilterPowerups(dem_bPlay);\r\n\r\n  // setup players from given indices\r\n  SetupLocalPlayers();')]
    for old,new in patches:
        # SetupLocalPlayers also occurs in join/load: inject only first (NewGame).
        count=text.count(old)
        if count<1 or (old!=patches[2][0] and count!=1):
            raise ValueError('server overlay anchor mismatch: '+repr(old))
        text=text.replace(old,new,1)
    game.write_bytes(text)
    return target

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('sdk','toolchain','prefix','output','overlay'):
        p.add_argument('--'+name,required=True,type=Path)
    args=p.parse_args()
    args.source_overlay=stage_server_overlay(args.overlay)
    builder.build(args)
if __name__=='__main__': main()
