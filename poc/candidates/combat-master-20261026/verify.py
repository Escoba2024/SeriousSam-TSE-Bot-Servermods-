#!/usr/bin/env python3
"""Sequential portable integration/regression checks; creates no game processes."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('combat_apply', HERE / 'apply.py')
apply = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apply)

def run(command, cwd=None):
    result = subprocess.run([str(c) for c in command], cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(' '.join(map(str, command)) + '\n' + result.stdout + result.stderr)
    return result.stdout

def compile_cpp(source, include, output):
    run(['c++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-I', include, source, '-o', output])

def main():
    generated = HERE / '.generated'
    generated.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='verify-', dir=generated) as tmp:
        base = Path(tmp)
        candidate = apply.materialize(base / 'candidate')
        pristine = base / 'pristine'
        pristine.mkdir()
        for p in apply.files_at(apply.PR57, 'poc/botcore/'):
            if p.endswith('.h'):
                (pristine / Path(p).name).write_bytes(apply.read(apply.PR57, p))
        # Real seeded command-stream comparison: all5 tiers x6 personas x2 P1 modes.
        traces = []
        for name, headers in [('pristine', pristine), ('candidate', candidate)]:
            exe = base / ('trace-' + name)
            compile_cpp(HERE / 'tests/trace.cpp', headers, exe)
            traces.append(run([exe]).encode())
        assert traces[0] == traces[1], 'default-off commands diverged from pristine PR57'
        assert traces[0].count(b'\n') == 21600
        print('DEFAULT OFF: 21600 commands byte-identical to pinned PR57')
        exe = base / 'test-master'
        compile_cpp(HERE / 'tests/test_combat_master.cpp', candidate, exe)
        master = run([exe]).strip()
        print(master)
        regressions_exe = base / 'test-regressions'
        compile_cpp(HERE / 'tests/test_combat_regressions.cpp', candidate, regressions_exe)
        regressions = run([regressions_exe]).strip()
        print(regressions)
        inherited = run(['make', '-j1', 'test'], candidate)
        print('\n'.join(l for l in inherited.splitlines() if 'PASS' in l))
        native = apply.materialize(base / 'gamemp', gamemp=True)
        # Execute the real tail reset branch omitted by the older block smoke.
        reset = re.search(r'    } else \{([^{}]*)\}\n\n    // Obstacle recovery can replace',
                          (native / 'BotDriver.cpp').read_text())
        assert reset, 'native recovery reset branch not found'
        (native / 'driver_reset.inc').write_text(reset.group(1))
        reset_exe = base / 'test-recovery-reset'
        compile_cpp(HERE / 'tests/test_recovery_reset.cpp', native, reset_exe)
        reset_result = run([reset_exe]).strip()
        print(reset_result)

        for name in ('bot_human.h', 'combat_master_support.h', 'combat2_selected.h', 'combat2_weapon.h'):
            assert (candidate / name).read_bytes() == (native / name).read_bytes(), name
        # Existing-directory and symlink outputs must be untouched.
        sentinel = candidate / 'sentinel'
        sentinel.write_text('preserve')
        for target in (candidate, base / 'link'):
            if target.name == 'link':
                target.symlink_to(base / 'absent')
            try:
                apply.materialize(target)
            except ValueError:
                pass
            else:
                raise AssertionError('existing target overwritten')
        assert sentinel.read_text() == 'preserve'
        # Compile/run the real driver block with its one new config global.
        smoke_source = candidate / 'test_botdriver_block.cpp'
        text = smoke_source.read_text().replace('static FLOAT bot_fStrafeScale=0.5f;',
                'static FLOAT bot_fStrafeScale=0.5f;\nstatic FLOAT bot_fCombatObservationAge=0.0f;')
        smoke_source.write_text(text)
        smoke = run(['make', '-j1', 'smoke', 'BOTDRIVER=' + str(native / 'BotDriver.cpp')], candidate)
        print(smoke.strip())
        print('APPLIER: both modes, input/output manifests, refusal to overwrite PASS')
        summary = {'retail': 'NOT_TESTED', 'native_build': 'NOT_TESTED',
                   'default_off_commands': 21600,
                   'default_off_trace_sha256': hashlib.sha256(traces[0]).hexdigest(),
                   'integration': master, 'combat_regressions': regressions, 'pr57_inherited_suite': 'PASS',
                   'driver_block_smoke': 'PASS', 'native_recovery_reset_branch': reset_result, 'applier': 'PASS',
                   'pins': {'pr57': apply.PR57, 'pr66': apply.PR66, 'qa_pr62': apply.PR62}}
        (generated / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
if __name__ == '__main__':
    main()
