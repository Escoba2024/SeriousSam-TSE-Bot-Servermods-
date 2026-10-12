"""Independent summary of preserved native fleet evidence and cleanup."""
import datetime as dt
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
native = root / 'retail'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def field(text, key):
    m = re.search(r'\\' + re.escape(key) + r'\\([^\\]*)', text)
    return m[1] if m else None
def timestamp(text):
    return dt.datetime.fromisoformat(text.replace('Z', '+00:00'))

def assert_hard_exit_log(text):
    joined = re.search(r'^\s*joined\s*$', text, re.M)
    assert joined
    # A display-mode reset also occurs at startup, before the session joins.
    # For the killed session, reject shutdown markers from its joined point on.
    session_log = text[joined.end():]
    assert 'Renderer buffers cleared.' not in session_log
    assert 'CDS: mode reset' not in session_log

def recovery_action_windows(text, after_replacement=False):
    registrations = re.findall(r'^\[BotDriver\] local player (\d+) \(player index (\d+)\) is now bot-driven:', text, re.M)
    slots = {int(slot): int(player) for slot, player in registrations}
    assert set(slots) == set(range(4)) and len(set(slots.values())) == 4
    if after_replacement:
        joins = list(re.finditer(r'^\^oTSE_Fleet_B_4\^r joined\s*$', text, re.M))
        assert len(joins) == 2  # initial B, then its single replacement
        text = text[joins[-1].end():]
    else:
        joined = re.search(r'^\s*joined\s*$', text, re.M)
        assert joined
        text = text[joined.end():]
    samples = {p: [] for p in slots.values()}
    pattern = r'^\[BotSnapshot\] tick=(\d+) player=(\d+) pos=\(([-\d.]+),([-\d.]+),([-\d.]+)\) yaw=([-\d.]+) health=([-\d.]+) buttons=(\d+) (.+)$'
    for m in re.finditer(pattern, text, re.M):
        tick, player = int(m[1]), int(m[2])
        if player in samples:
            assert re.search(r'\\frags_' + str(player) + r'\\-?\d+', m[9])
            samples[player].append((tick, tuple(float(m[i]) for i in (3,4,5)), float(m[6]), int(m[8]) & 1))
    windows = []
    for slot, player in sorted(slots.items()):
        rows = samples[player]
        assert len(rows) >= 1200 and all(a[0] < b[0] for a,b in zip(rows, rows[1:]))
        window = rows[-1200:]
        assert window[-1][0] - window[0][0] == 1199
        positions, yaw = len({r[1] for r in window}), len({r[2] for r in window})
        fire_on = sum(r[3] != 0 for r in window)
        assert positions >= 10 and yaw >= 10 and 0 < fire_on < 1200
        windows.append(dict(localSlot=slot, player=player, samplesAfterJoin=len(rows), windowSamples=1200, firstTick=window[0][0], lastTick=window[-1][0], distinctPositions=positions, distinctYaw=yaw, fireOn=fire_on, fireOff=1200-fire_on))
    return windows
queries = [json.loads(line) for line in (native / 'queries.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
identities = read(native / 'runtime-identities.json')
result = read(native / 'result.json')
diagnostics = read(native / 'diagnostics.json')
preservation = read(root / 'preservation.json')
assert result['passed'] and diagnostics['passed'] and preservation['passed']
assert len(identities) == 8 and len({p['guid'] for p in identities}) == 8 and len({p['name'] for p in identities}) == 8
assert all(p['guidSource'] == 'profile+sidecar' for p in identities)
assert not any(diagnostics[k] for k in ('ownedProcesses', 'udpPorts', 'crashReports', 'matchingCrashEvents', 'cleanupErrors'))
assert diagnostics['applicationEventsRead']
assert not preservation['ownedProcesses'] and not preservation['udpPorts'] and not preservation['cleanupErrors']
assert all(r['restored'] for r in preservation['restored'])
stages = []
maps = []
startup_transitions = []
for q in queries:
    status, players = q['status'], q['players']
    count = int(field(status, 'numplayers'))
    assert field(status, 'gamever') == '1.07' and field(status, 'activemod') == ''
    names = re.findall(r'\\player_\d+\\([^\\]+)', players)
    incomplete_initial_join = q.get('label') == 'eight-bots' and len(names) < count
    assert len(set(names)) == len(names)
    if incomplete_initial_join:
        assert count == 8 and set(names).issubset({p['name'] for p in identities})
        startup_transitions.append(dict(utc=q['utc'], allocatedSlots=count, listedNames=len(names)))
    else:
        assert len(names) == count
    if count in (8, 9) and not incomplete_initial_join:
        assert all(names.count(p['name']) == 1 for p in identities)
        if count == 9:
            assert 'Vanilla_Human_1' in names
    if count == 4:
        assert set(names) == {p['name'] for p in identities if p['name'].startswith('TSE_Fleet_A_')}
    if q.get('label'):
        stages.append(dict(label=q['label'], utc=q['utc'], players=count))
    map_name = field(status, 'mapname')
    if not maps or map_name != maps[-1]['map']:
        maps.append(dict(map=map_name, utc=q['utc'], players=count))
stop_proof = []
if result['lifecycle']:
    expected = dict(zip(('eight-bots','human-join','human-left','human-rejoin','human-left-again','exactly-four-freed','four-bots-restored','final-eight'), (8,9,8,9,8,4,8,8)))
    assert all(any(s['label'] == label and s['players'] == count for s in stages) for label, count in expected.items())
    labels = ('human-leave', 'human-leave-again') if result.get('unexpectedExitRecovery') else ('human-leave', 'human-leave-again', 'four-bots-leave')
    for label in labels:
        stop = read(native / f'{label}-state.json.stopped.json')['results']
        assert len(stop) == 1 and stop[0]['state'] == 'graceful' and stop[0]['exitCode'] == 1
        stop_proof.append(dict(label=label, **stop[0]))
resources = [json.loads(line) for line in (native / 'resources.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
groups = {}
for r in resources:
    groups.setdefault((r['role'], r['pid']), []).append(r)
resource_summary = []
for (role, pid), rows in groups.items():
    seconds = (timestamp(rows[-1]['utc']) - timestamp(rows[0]['utc'])).total_seconds()
    resource_summary.append(dict(role=role, pid=pid, samples=len(rows), sampledSeconds=round(seconds,2), averageHostCpuPercent=round((rows[-1]['cpuSeconds']-rows[0]['cpuSeconds'])/seconds/8*100,2) if seconds else None, peakPrivateMiB=round(max(r['privateBytes'] for r in rows)/2**20,2), peakWorkingSetMiB=round(max(r['workingSet'] for r in rows)/2**20,2)))
telemetry = []
for path in native.glob('*-telemetry.json'):
    t = read(path)
    assert not t['rejectedSnapshotLines']
    telemetry.append(dict(client=path.stem, players=[{key:p[key] for key in ('player','samples','distinctPositions','distinctYaw','fireOnSamples','fireOffSamples')} for p in t['players']], activeMinutes=len(t.get('activeSyncMinutes', []))))
hard_exit = None
if result.get('unexpectedExitRecovery'):
    hard_exit = read(native / 'hard-exit.json')
    initial = read(native / 'fleet-state.json')['processes']
    replacement = read(native / 'restart-state.json')['processes'][0]
    assert hard_exit['passed'] and hard_exit['detectedExit'] and hard_exit['normalShutdown'] is False
    assert hard_exit['oldProcess'] == initial[1] and hard_exit['remainingClient'] == initial[0]
    assert hard_exit['replacement'] == replacement and replacement != initial[1]
    assert isinstance(hard_exit['exitCode'], int)
    times = [timestamp(hard_exit[k]) for k in ('killUtc','detectedUtc','fourSlotsFreedUtc','eightSlotsRestoredUtc')]
    assert all(a <= b for a,b in zip(times,times[1:]))
    old_log = (native / 'four-bots-leave.log').read_text(encoding='utf-8-sig',errors='replace')
    assert_hard_exit_log(old_log)
    identity_key = lambda p: (p['clientDir'],p['slot'],p['name'],p['guid'],p['guidSource'])
    assert {identity_key(p) for p in identities} == {identity_key(p) for p in read(native / 'identities.json')}
    assert len(telemetry) == 2 and all(len(t['players'])==4 and t['activeMinutes'] >= 4 for t in telemetry)
    assert all(p['samples']>=1200 and p['fireOnSamples'] and p['fireOffSamples'] and p['distinctPositions']>1 and p['distinctYaw']>1 for t in telemetry for p in t['players'])
    role_a, role_b = pathlib.Path(initial[0]['clientDir']).name, pathlib.Path(replacement['clientDir']).name
    assert {r['pid'] for r in resources if r['role']==role_a} == {initial[0]['pid']}
    assert {r['pid'] for r in resources if r['role']==role_b} == {replacement['pid']}
    hard_exit['postRelaunchActionWindows'] = {
        role_a: recovery_action_windows((native / f'{role_a}-SeriousSam.log').read_text(encoding='utf-8-sig'), after_replacement=True),
        role_b: recovery_action_windows((native / f'{role_b}-SeriousSam.log').read_text(encoding='utf-8-sig')),
    }
audit = dict(passed=True, scope='Short native scenario; not full Phase-3/hour acceptance. Early join allocation may precede player-list RPC completion; all later steady snapshots require complete eight-name lists.', result=result, stages=stages, startupTransitions=startup_transitions, queries=len(queries), mapTransitions=maps, identities=identities, controlledStops=stop_proof, telemetry=telemetry, resources=resource_summary, restoredFiles=len(preservation['restored']), createdFiles=len(preservation['createdFiles']))
if hard_exit:
    audit['hardExitRecovery'] = hard_exit
    audit['scope'] += ' Hard exit is fault-injected and recovered by the test controller; no permanent supervisor acceptance.'
(root / 'acceptance-audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
print(json.dumps({k:audit[k] for k in ('passed','stages','queries','mapTransitions','telemetry','resources','restoredFiles')}))
