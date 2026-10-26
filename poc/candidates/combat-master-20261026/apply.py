#!/usr/bin/env python3
"""Compose pinned PR57 + selected PR66 modules into a NEW unqualified directory.

Default: engine-free botcore/tests. --gamemp: reuse PR57's pinned source applier
then overlay the same headers and native opt-in shell wiring. Never deploys.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PR57 = '6b84c5d283664bc9e968bb4961abf2dd48731c5b'
PR66 = '48e110a7aa7b818cf7bab5979f6aae629932a2dc'
PR62 = 'd5fcd066c28764a6ba7fb6808364304f3ccd74e7'
RESEARCH = 'poc/research/behavior-improvements/'
CANDIDATE = 'poc/candidates/integrated-human-cpu-20261021/'

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def read(commit, path):
    return git('show', commit + ':' + path)

def files_at(commit, prefix):
    return git('ls-tree', '--name-only', commit, prefix).decode().splitlines()

def extract(text, start, end):
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError('pinned module extraction mismatch')
    return text.split(start, 1)[1].split(end, 1)[0]

def modules():
    text = read(PR66, RESEARCH + 'combat2_tactics.h').decode()
    # Only style, strafe, coherent range. Do not import ChooseTarget2,
    # PlanRespawn, profile retuning, cover, search or tolerance-widening code.
    style = 'struct CombatStyle {' + extract(text, 'struct CombatStyle {', '/* F-7 target prioritisation').rsplit('/* ------------------------------------------------------------------ */', 1)[0]
    strafe = 'class StrafeController {' + extract(text, 'class StrafeController {', '// While strafing fast,')
    desired = 'inline double DesiredRange2(' + extract(text, 'inline double DesiredRange2(', '}  // namespace combat2')
    return ('// Selected unchanged PR66 functions; provenance in SOURCE_MANIFEST.json.\n'
            '#ifndef SSAM_COMBAT2_SELECTED_H\n#define SSAM_COMBAT2_SELECTED_H\n'
            '#include "combat2_weapon.h"\nnamespace combat2 {\n'
            'inline double Clamp(double v,double lo,double hi) { return v<lo?lo:(v>hi?hi:v); }\n'
            + style + strafe + desired + '\n}\n#endif\n').encode()

def patch(target, name):
    subprocess.run(['patch', '--batch', '--fuzz=0', '-p0', '-i', str(HERE / name)],
                   cwd=target, check=True, stdout=subprocess.DEVNULL)

def materialize(output, gamemp=False):
    output = Path(output).absolute()
    # lexists also rejects dangling symlinks. Check again before final rename.
    if output.exists() or output.is_symlink():
        raise ValueError('target already exists; refusing overwrite')
    if not output.parent.is_dir():
        raise ValueError('output parent must already exist')
    source_hashes = {}
    def source(commit, path):
        data = read(commit, path)
        source_hashes[commit + ':' + path] = hashlib.sha256(data).hexdigest()
        return data
    with tempfile.TemporaryDirectory(prefix='.combat-compose-', dir=output.parent) as tmp:
        stage = Path(tmp)
        target = stage / 'result'
        if gamemp:
            # PR57's actual applier verifies the qualified release input pins.
            seed = stage / 'seed'
            names = files_at(PR57, 'poc/release/gamemp/')
            names += [CANDIDATE + n for n in ('apply.py', 'Game.cpp', 'BotDriver.cpp', 'BotTelemetry.h')]
            names += ['poc/botcore/' + n for n in ('bot_profile.h', 'bot_perception.h', 'bot_aim.h', 'bot_loadout.h', 'bot_human.h', 'bot_route.h')]
            for name in names:
                dest = seed / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(source(PR57, name))
            subprocess.run(['python3', str(seed / CANDIDATE / 'apply.py'), str(target)],
                           check=True, stdout=subprocess.DEVNULL)
        else:
            target.mkdir()
            for name in files_at(PR57, 'poc/botcore/'):
                if name.endswith(('.h', '.cpp', '.py')) or Path(name).name == 'Makefile':
                    (target / Path(name).name).write_bytes(source(PR57, name))
        (target / 'combat2_weapon.h').write_bytes(source(PR66, RESEARCH + 'combat2_weapon.h'))
        source(PR66, RESEARCH + 'combat2_tactics.h')
        (target / 'combat2_selected.h').write_bytes(modules())
        shutil.copy2(HERE / 'combat_master_support.h', target)
        patch(target, 'combat.patch')
        if gamemp:
            patch(target, 'driver.patch')
        manifest = {'qualified': False, 'native_build': 'NOT_TESTED', 'retail': 'NOT_TESTED',
                    'source_pins': {'pr57': PR57, 'pr66': PR66, 'qa_pr62': PR62},
                    'mode': 'gamemp' if gamemp else 'botcore', 'inputs_sha256': source_hashes,
                    'local_inputs_sha256': {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()
                        for n in ('combat.patch', 'driver.patch', 'combat_master_support.h')},
                    'output_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(target.iterdir()) if p.is_file()}}
        (target / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
        if output.exists() or output.is_symlink():
            raise ValueError('target appeared during composition; refusing overwrite')
        target.rename(output)
    return output

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gamemp', action='store_true')
    p.add_argument('output', type=Path)
    args = p.parse_args()
    try:
        out = materialize(args.output, args.gamemp)
    except (ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc)) from exc
    print('UNQUALIFIED composed source:', out)
if __name__ == '__main__':
    main()
