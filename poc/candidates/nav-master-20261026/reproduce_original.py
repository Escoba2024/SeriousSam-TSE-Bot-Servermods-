#!/usr/bin/env python3
"""Prove the eight regression assertions fail on the original pinned sources."""
import subprocess
import prepare

try:
    prepare.prepare(False)
    output=prepare.HERE/'.build/original_regressions'
    subprocess.run(['g++','-std=c++17','-O0','-Wall','-Wextra','-Werror',
        '-DNAV_ITEM_BRIDGE_REQUIRE_UPSTREAM',
        '-I'+str(prepare.DEST/'poc/research/nav-item-bridge/include'),
        str(prepare.HERE/'tests/test_regressions.cpp'),'-o',str(output)],check=True)
    result=subprocess.run([str(output)],capture_output=True,text=True)
    print(result.stdout,end='')
    if result.returncode!=1 or 'C2 regressions: 8 failures' not in result.stdout:
        raise RuntimeError('original source did not reproduce exactly eight known failures')
    print('EXPECTED_RED: all eight original assertions reproduced')
finally:
    prepare.prepare(True)
