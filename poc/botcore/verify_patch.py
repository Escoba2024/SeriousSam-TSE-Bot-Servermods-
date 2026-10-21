#!/usr/bin/env python3
"""Prove that poc/patch/0008-gamemp-human-bot-ai.patch still applies to the
published BotDriver.cpp and reproduces poc/ai-integration/gamemp/BotDriver.cpp
byte for byte.

Run from anywhere:
    python3 poc/botcore/verify_patch.py

Exit codes: 0 = in sync, 1 = drift or failure.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PATCH = REPO / 'poc/patch/0008-gamemp-human-bot-ai.patch'
SOURCE = REPO / 'poc/release/gamemp/BotDriver.cpp'
RESULT = REPO / 'poc/ai-integration/gamemp/BotDriver.cpp'


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main():
    if not PATCH.exists() or not SOURCE.exists() or not RESULT.exists():
        print('MISSING: patch, published source or integration copy')
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        target = tmp / 'poc/release/gamemp'
        target.mkdir(parents=True)
        shutil.copy2(SOURCE, target / 'BotDriver.cpp')
        for cmd in (['git', 'init', '-q'], ['git', 'add', '-A'],
                    ['git', '-c', 'user.email=a@b.c', '-c', 'user.name=t',
                     'commit', '-qm', 'base']):
            r = run(cmd, tmp)
            if r.returncode != 0:
                print('git failed:', r.stderr)
                return 1
        r = run(['git', 'apply', '--check', str(PATCH)], tmp)
        if r.returncode != 0:
            print('PATCH DOES NOT APPLY:', r.stderr.strip())
            return 1
        r = run(['git', 'apply', str(PATCH)], tmp)
        if r.returncode != 0:
            print('PATCH APPLY FAILED:', r.stderr.strip())
            return 1
        applied = (target / 'BotDriver.cpp').read_bytes()
        shipped = RESULT.read_bytes()
        if applied != shipped:
            print('DRIFT: poc/ai-integration/gamemp/BotDriver.cpp differs from '
                  'published source + patch')
            return 1
    print('PATCH VERIFY PASS: 0008 applies cleanly and matches the integration copy')
    return 0


if __name__ == '__main__':
    sys.exit(main())
