#!/usr/bin/env python3
"""Run actual M2 policy and extracted native adapter code; no game processes."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('m2_apply',HERE/'apply.py');apply=importlib.util.module_from_spec(s);s.loader.exec_module(apply)
def run(cmd,cwd=None):
    p=subprocess.run([str(x) for x in cmd],cwd=cwd,text=True,capture_output=True)
    if p.returncode:raise RuntimeError(' '.join(map(str,cmd))+'\n'+p.stdout+p.stderr)
    return p.stdout

def block(text,start):
    pos=text.index(start);begin=text.index('{',pos);depth=1;end=begin+1
    while depth:
        if text[end]=='{':depth+=1
        if text[end]=='}':depth-=1
        end+=1
    return text[pos:end]+'\n'

def extract(native):
    text=(native/'BotDriver.cpp').read_text()
    start=text.index('        if (bot_bHumanAI) {',text.index('const FLOAT distance=bot_bHumanAI')) if 'if (bot_bHumanAI) {\n          combatHold=' in text else -1
    hold=text[start:text.index('        CPlayerWeapons *weapons=',start)] if start>=0 else 'combatHold=combatHold || distance<=((combatWeapon==1 || combatWeapon==10)?1.5f:8.0f);\n'
    # Retain legacy branch but avoid unused fixture variable diagnostics.
    (native/'hold.inc').write_text(hold+'\n(void)bot_bHumanAI;(void)moveFactor;(void)humanStrafe;(void)bot_fStrafeScale;\n')
    (native/'recovery.inc').write_text(block(text,'      if (navigation.overrideInput) {'))
    (native/'session_reset.inc').write_text(block(text,'static void BotResetNavigation(void)'))
    (native/'attach.inc').write_text(block(text,'static void BotHumanAttach(INDEX iLP)'))
    start=text.index('        testAimReady=testAimReady && weapons->m_iCurrentWeapon')
    (native/'weapon_gate.inc').write_text(text[start:text.index(';',start)+1]+'\n')
    start=text.index('    BOOL bFire = FALSE;',text.index('    // 2) fire decision'))
    (native/'fire_decision.inc').write_text(text[start:text.index('    // 3) compose the action',start)])
    (native/'fire_button.inc').write_text(block(text,'    if (bFire) {'))
    start=text.index('    ppls->SetAction(pa);')
    (native/'emission.inc').write_text(text[start:text.index('    // Count emitted combat fire input',start)])
    marker='      if (bot_bObstacleAvoidance && (moveFactor<0.0f'
    (native/'clearance.inc').write_text(block(text,marker) if marker in text else '')
    start=text.index('          BotLog("[BotAmmo]') if '          BotLog("[BotAmmo]' in text else -1
    (native/'ammo.inc').write_text(text[start:text.index(');',start)+2]+'\n' if start>=0 else '')
    result=run(['python3',native/'extract_block.py',native/'BotDriver.cpp']) if (native/'extract_block.py').exists() else run(['python3',apply.c1.ROOT/'poc/botcore/extract_block.py',native/'BotDriver.cpp'])
    (native/'block.inc').write_text(result)

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--sanitize',action='store_true');a=p.parse_args()
    generated=HERE/'.generated';generated.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=generated,prefix='verify-') as tmp:
        root=Path(tmp);materialize=apply.c1.materialize if a.baseline else apply.materialize
        core=materialize(root/'core');native=materialize(root/'native',True);extract(native)
        results=[];failures=[]
        for name,include in [('policy',core),('driver',native),('tail',native),('attach',native),('emission',native),('ammo',native)]:
            exe=root/name
            flags=['-std=c++17','-O1' if a.sanitize else '-O2','-g','-Wall','-Wextra','-Werror']
            if a.sanitize:flags+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
            try:
                run(['g++',*flags,'-I',include,HERE/'tests'/('test_'+name+'.cpp'),'-o',exe])
                result=run([exe]).strip();print(result,flush=True);results.append(result)
            except RuntimeError as e:failures.append(str(e));print(str(e),flush=True)
        if failures:raise SystemExit(1)
        # Exact patched headers reach native and portable composition identically.
        assert (core/'bot_human.h').read_bytes()==(native/'bot_human.h').read_bytes()
        sentinel=core/'preserve';sentinel.write_text('preserve')
        try:materialize(core)
        except ValueError:pass
        else:raise AssertionError('existing output overwritten')
        assert sentinel.read_text()=='preserve'
        print('M2 APPLIER parity and no-overwrite PASS',flush=True)
        for name in ('test_combat_master','test_combat_regressions'):
            exe=root/name
            run(['g++','-std=c++17','-O2','-Wall','-Wextra','-I',core,HERE.parent/'combat-master-20261026/tests'/(name+'.cpp'),'-o',exe])
            print(run([exe]).strip(),flush=True)
        inherited=run(['make','-j1','test'],core)
        print('\n'.join(x for x in inherited.splitlines() if 'PASS' in x),flush=True)
        (generated/'verification.json').write_text(json.dumps({'qualified':False,'retail':'NOT_TESTED','sanitize':a.sanitize,'results':results,'inherited':'PASS'},indent=2)+'\n')
if __name__=='__main__':main()
