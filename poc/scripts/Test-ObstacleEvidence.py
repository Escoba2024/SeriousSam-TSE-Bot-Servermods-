"""Require native wall recovery, action bounds, combat coexistence and restoration."""
import argparse
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path

_spec = importlib.util.spec_from_file_location('combat_evidence', Path(__file__).with_name('Test-AutoCombatEvidence.py'))
_combat = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_combat)
require, rows = _combat.require, _combat.rows

def audit_rows(nav, combat, driver, locals_expected=(0, 1), min_samples=600):
    records = []
    for local in locals_expected:
        sequence = sorted((tick, v) for (slot, tick), v in nav.items() if slot == local)
        require(len(sequence) >= min_samples, f'missing navigation decisions local {local}')
        brush_turns, attacks, finishes, age, max_age = 0, 0, [], 0, 0
        advance_start, brush_attempt, previous_tick, advance_ticks = None, False, None, 0
        for tick, v in sequence:
            require(previous_tick is None or tick == previous_tick+1, 'missing native navigation ticks')
            require((local, tick) in combat and (local, tick) in driver, 'missing matching combat/driver evidence')
            previous_tick = tick
            active, phase, alive = int(v['active']), int(v['phase']), int(v['alive'])
            began, finished = int(v['began']), int(v['finished'])
            delta, forward = float(v['delta']), float(v['forward'])
            distances = [float(v[k]) for k in ('front', 'left', 'right')]
            pos = tuple(map(float, v['pos'].strip('()').split(',')))
            require(len(pos) == 3 and all(math.isfinite(n) for n in (*pos, delta, forward, *distances)), 'nonfinite navigation evidence')
            require(abs(delta) <= 2.251 and 0 <= forward <= 1 and all(0 <= n <= 3 for n in distances), 'native action/ray bounds')
            require(not active or (alive and not int(v['hold'])), 'dead/held navigation remains active')
            if not active and not finished:
                brush_attempt = False
            if active and phase == 1:
                require(forward == 0, 'turn recovery also advances')
            if began:
                advance_start = None
                if int(v['reason']) == 1 and int(v['hitType']) == 4 and distances[0] < 1.2:
                    require(active and phase == 1 and forward == 0 and delta != 0, 'brush obstruction did not turn in place')
                    if max(distances[1:]) >= 1.2 and distances[1] != distances[2]:
                        require((delta > 0) == (distances[1] > distances[2]), 'turn away from freer side')
                    brush_turns += 1
                    brush_attempt = True
            age = age + 1 if active or finished else 0
            max_age = max(max_age, age)
            require(age <= 240, 'recovery exceeded overall attempt budget')
            if active and phase == 2:
                advance_ticks += 1
                require(advance_ticks <= 40, 'advance exceeded phase budget')
                if advance_start is None:
                    advance_start = (tick, pos)
                if finished:
                    distance = math.hypot(pos[0]-advance_start[1][0], pos[2]-advance_start[1][2])
                    finishes.append(dict(firstTick=advance_start[0], lastTick=tick,
                                         planarMetres=round(distance, 3), brushAttempt=brush_attempt))
                    advance_start = None
            else:
                advance_start = None
                advance_ticks = 0
            if finished:
                age = 0
                brush_attempt = False
                advance_ticks = 0
            if driver.get((local, tick)) and alive:
                require(not active and int(combat[(local, tick)]['ready']), 'attack while recovering or without combat readiness')
                attacks += 1
        successes = [v for v in finishes if v['planarMetres'] >= 2 and v['brushAttempt']]
        require(brush_turns and successes, f'no actual brush turn/completed progress local {local}')
        require(attacks, f'no combat attacks alongside navigation local {local}')
        records.append(dict(local=local, decisions=len(sequence), brushTurns=brush_turns,
                            completedAdvances=finishes, advancesAtLeast2m=len(successes),
                            maxAttemptTicks=max_age, livingAttackTicks=attacks))
    return records

def audit(root, dll):
    native = root / 'native-2-Combat'
    read = lambda path: json.loads(path.read_text(encoding='utf-8-sig'))
    result, diagnostics = read(native/'result.json'), read(root/'diagnostics.json')
    identities, telemetry = read(root/'identities-2.json'), read(native/'telemetry.json')
    digest = hashlib.sha256(dll.read_bytes()).hexdigest().upper()
    require(result['sha256'] == digest, 'evidence does not use current candidate')
    require(len(identities) == 2 and len({p['guid'] for p in identities}) == 2 and len({p['name'] for p in identities}) == 2, 'distinct native profiles/GUIDs')
    for field in ('loaded', 'alive', 'serverAlive', 'crcAccepted', 'clientCurrentlyJoined', 'observerCurrentlyJoined', 'observerAlive', 'observerSawBotJoin'):
        require(result[field], f'native join/CRC gate: {field}')
    require(result['crcAcceptedCount'] >= 2 and result['elapsedSeconds'] >= 120, 'native duration/CRC')
    require(diagnostics['passed'] and diagnostics['applicationEventsRead'] and all(f['restored'] for f in diagnostics['restored']), 'restoration failed')
    require(not any(diagnostics[k] for k in ('ownedProcesses', 'udpPorts', 'matchingCrashEvents', 'crashReports', 'cleanupErrors')), 'runtime cleanup/crash gate')
    require(not telemetry['rejectedSnapshotLines'], 'corrupt snapshot evidence')
    text = (native/'SeriousSam.log').read_text(encoding='utf-8', errors='replace')
    observer = (native/'observer-SeriousSam.log').read_text(encoding='utf-8', errors='replace')
    nav, combat = rows(text, 'BotNavigation'), rows(text, 'BotCombat')
    driver = {(int(m[1]), int(m[2])): int(m[3]) for m in re.finditer(r'\[BotDriver\] bot(\d+) tick=(\d+) [^\n]* fire=(\d+)', text)}
    records = audit_rows(nav, combat, driver)
    kills = [line for line in observer.splitlines() if 'TSE_Bot_PoC_' in line and 'poured lead into' in line]
    require(kills, 'no independent vanilla observer combat witness')
    for local in (0, 1):
        p = next(p for p in telemetry['players'] if p['player'] == local+1)
        require(p['samples'] >= 600 and p['fireOnSamples'] and p['fireOffSamples'], 'missing replicated native actions')
    return dict(passed=True, sha256=digest, nativeSeconds=result['elapsedSeconds'],
                crcAcceptedCount=result['crcAcceptedCount'], players=records, identities=identities,
                observerKills=kills, restoredFiles=len(diagnostics['restored']),
                scope='Bounded reactive recovery on stock Fortress deathmatch; 2 local bots and vanilla observer; no global route, floor/drop safety, coop or hour qualification')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--dll', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.root, args.dll)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('OBSTACLE EVIDENCE PASS:', args.output)
