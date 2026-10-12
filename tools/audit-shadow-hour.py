"""Independent raw-data gate for one uninterrupted 2x4 fleet hour.

Run audit-shadow-fleet.py first; this audit strengthens its short-scenario
checks without changing the runner of an already active native test.
"""
import collections
import datetime as dt
import io
import json
import pathlib
import re
import sys

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def timestamp(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))

def field(text, key):
    m = re.search(r'\\' + re.escape(key) + r'\\([^\\]*)', text)
    assert m, key
    return m[1]

def raw_minutes(path, replacement_boundary=False, expected_players=4, require_shutdown=True, first_hour=False, replicated_players=None, prefix_characters=None):
    slots = {}
    buffers = {} if replicated_players is None else {p: collections.deque(maxlen=75000) for p in range(replicated_players)}
    last_ticks = {}
    total = collections.Counter()
    boundary_seen = False
    b4_joins = 0
    local_joins = 0
    last_snapshot_line = 0
    last_renderer_line = 0
    last_cds_line = 0
    capture_tail = 0
    snapshot = re.compile(r'^\[BotSnapshot\] tick=(\d+) player=(\d+) pos=\(([-\d.]+),([-\d.]+),([-\d.]+)\) yaw=([-\d.]+) health=([-\d.]+) buttons=(\d+) (.+)$')
    stream = path.open(encoding='utf-8-sig', errors='strict', newline='')
    if prefix_characters is not None:
        with stream:
            prefix = stream.read(prefix_characters)
        assert len(prefix)==prefix_characters and not re.search('[\U00010000-\U0010ffff]', prefix)
        # A concurrent read can end inside an append. This edge is not a
        # complete captured native line; do not repair it or count its snapshot.
        complete_end=prefix.rfind('\n')+1
        capture_tail=len(prefix)-complete_end
        prefix=prefix[:complete_end]
        stream = io.StringIO(prefix)
    with stream:
        for line_number, line in enumerate(stream, 1):
            if '[BotSnapshot]' in line:
                last_snapshot_line = line_number
            if 'Renderer buffers cleared.' in line:
                last_renderer_line = line_number
            if 'CDS: mode reset' in line:
                last_cds_line = line_number
            local = re.match(r'^\[BotDriver\] local player (\d+) \(player index (\d+)\) is now bot-driven:', line)
            if local:
                slot, player = int(local[1]), int(local[2])
                assert slot not in slots or slots[slot] == player
                slots[slot] = player
                buffers.setdefault(player, collections.deque(maxlen=75000))
            if re.fullmatch(r'\s*joined\s*', line):
                local_joins += 1
                if not replacement_boundary:
                    boundary_seen = True
            if re.fullmatch(r'\^oTSE_Fleet_B_4\^r joined\s*', line):
                b4_joins += 1
                if replacement_boundary and b4_joins == 2:
                    boundary_seen = True
            if not boundary_seen or '[BotSnapshot]' not in line:
                continue
            m = snapshot.match(line.rstrip('\r\n'))
            assert m, f'Malformed snapshot: {path}'
            tick, player = int(m[1]), int(m[2])
            if player not in buffers:
                continue
            assert re.search(r'\\frags_' + str(player) + r'\\-?\d+(?:\s|$)', m[9])
            assert tick > last_ticks.get(player, -1), f'Tick restart/duplicate: {path}, {player}'
            last_ticks[player] = tick
            total[player] += 1
            if not first_hour or len(buffers[player])<75000:
                buffers[player].append((tick, tuple(float(m[i]) for i in (3,4,5)), float(m[6]), int(m[8]) & 1))
    assert boundary_seen and set(slots) == set(range(expected_players)) and len(set(slots.values())) == expected_players
    assert local_joins == 1 and (not replacement_boundary or b4_joins == 2)
    if require_shutdown:
        assert last_snapshot_line < last_renderer_line < last_cds_line
    summaries = []
    windows = []
    shared_start = None
    if first_hour and replicated_players is not None:
        assert all(buffers[p] for p in range(replicated_players))
        shared_start = max(buffers[p][0][0] for p in range(replicated_players))+1200
    selected_players = sorted(slots.items()) if replicated_players is None else [(p % expected_players, p) for p in range(replicated_players)]
    for slot, player in selected_players:
        rows = list(buffers[player])
        assert total[player] >= 72000 and rows
        start = shared_start if shared_start is not None else (rows[0][0]+1200 if first_hour else rows[-1][0] - 72000 + 1)
        assert rows[0][0] <= start
        assert rows[-1][0]>=start+72000-1
        cursor = 0
        while rows[cursor][0] < start:
            cursor += 1
        for minute in range(60):
            begin, end = start + minute*1200, start + (minute+1)*1200
            part = []
            while cursor < len(rows) and rows[cursor][0] < end:
                assert rows[cursor][0] >= begin
                part.append(rows[cursor])
                cursor += 1
            positions, yaw = len({r[1] for r in part}), len({r[2] for r in part})
            fire_on = sum(r[3] != 0 for r in part)
            assert len(part) >= 1190 and positions >= 10 and yaw >= 10 and 0 < fire_on < len(part)
            windows.append(dict(localSlot=slot, player=player, minute=minute+1, samples=len(part), positions=positions, yaw=yaw, fireOn=fire_on, fireOff=len(part)-fire_on))
        summaries.append(dict(localSlot=slot, player=player, snapshotsAfterJoin=total[player], firstHourTick=start, lastHourTick=start+72000-1))
    return dict(players=summaries, minuteWindows=windows, windowSelection='post-join native minutes 2 through 61' if first_hour else 'last 72000 native ticks', replicatedPlayers=replicated_players, capturedPrefixCharacters=prefix_characters, incompleteCaptureTailCharacters=capture_tail, finalShutdownAfterActions=last_snapshot_line < last_renderer_line < last_cds_line)

def audit(root):
    native = root / 'retail'
    common = read(root / 'acceptance-audit.json')
    result = read(native / 'result.json')
    assert common['passed'] and result['passed'] and result['lifecycle']
    assert not result['mapCycle'] and not result.get('unexpectedExitRecovery')
    assert result['syncMinutes'] == 60 and result['steadySeconds'] >= 3600
    assert result['dllSha256'] == '24053920C63E02F9883056331B246BEF2D08D645FFCCE2C74ED7EDC9B35B9ACF'
    expected_stages = dict(zip(('eight-bots','human-join','human-left','human-rejoin','human-left-again','exactly-four-freed','four-bots-restored','final-eight'), (8,9,8,9,8,4,8,8)))
    for label, count in expected_stages.items():
        assert any(s['label']==label and s['players']==count for s in common['stages'])
    start = timestamp(next(s['utc'] for s in common['stages'] if s['label']=='four-bots-restored'))
    identities = read(native / 'runtime-identities.json')
    expected_names = {p['name'] for p in identities}
    assert len(expected_names) == 8 and len({p['guid'] for p in identities}) == 8
    queries = [json.loads(line) for line in (native / 'queries.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    steady = [q for q in queries if timestamp(q['utc']) >= start]
    span = (timestamp(steady[-1]['utc']) - start).total_seconds()
    assert span >= 3600
    assert all(0 < (timestamp(b['utc'])-timestamp(a['utc'])).total_seconds() <= 60 for a,b in zip(steady, steady[1:]))
    for q in steady:
        assert field(q['status'], 'numplayers') == '8' and field(q['status'], 'gamever') == '1.07' and field(q['status'], 'activemod') == ''
        names = re.findall(r'\\player_\d+\\([^\\]+)', q['players'])
        assert len(names) == 8 and set(names) == expected_names
    initial = read(native / 'fleet-state.json')['processes']
    replacement = read(native / 'restart-state.json')['processes']
    assert len(initial)==2 and len(replacement)==1
    live = [initial[0], replacement[0]]
    assert all(p['localPlayers']==4 for p in live) and live[1] != initial[1]
    final_stops = [read(native / 'fleet-state.json.stopped.json'), read(native / 'restart-state.json.stopped.json')]
    for process, stop in zip(live, final_stops):
        matching = [r for r in stop['results'] if r['pid']==process['pid'] and r['exe']==process['exe']]
        assert len(matching)==1 and matching[0]['state']=='graceful' and matching[0]['exitCode']==1
        assert timestamp(stop['stoppedUtc']) >= timestamp(steady[-1]['utc'])
    assert len(common['telemetry']) == 2 and all(len(t['players'])==4 and t['activeMinutes']==240 for t in common['telemetry'])
    resources = [json.loads(line) for line in (native / 'resources.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    for role, expected_pid in [(pathlib.Path(p['clientDir']).name, p['pid']) for p in live] + [('server', None)]:
        rows = [r for r in resources if r['role']==role]
        assert rows and len({r['pid'] for r in rows}) == 1
        if expected_pid is not None:
            assert {r['pid'] for r in rows} == {expected_pid}
        assert 0 <= (timestamp(rows[0]['utc'])-start).total_seconds() <= 60
        assert (timestamp(rows[-1]['utc'])-timestamp(rows[0]['utc'])).total_seconds() >= 3600
        assert all(0 < (timestamp(b['utc'])-timestamp(a['utc'])).total_seconds() <= 60 for a,b in zip(rows,rows[1:]))
    raw = {pathlib.Path(p['clientDir']).name: raw_minutes(native / (pathlib.Path(p['clientDir']).name+'-SeriousSam.log'), replacement_boundary=(i==0)) for i,p in enumerate(live)}
    assert sum(len(v['minuteWindows']) for v in raw.values()) == 480
    frame_gate = read(native / 'gate-TSE-BotClient.json')
    frame_lag = (timestamp(frame_gate['utc'])-timestamp(steady[-1]['utc'])).total_seconds()
    assert 0<=frame_lag<=60 and frame_gate['joinedMarker'] and not frame_gate['failureMarker']
    frame_raw = raw_minutes(native / 'TSE-BotClient-SeriousSam.log', replacement_boundary=True, require_shutdown=False, first_hour=True, replicated_players=8, prefix_characters=frame_gate['characters'])
    assert len(frame_raw['minuteWindows'])==480
    configuration = read(root.parent / 'effective-server-config.json')
    assert configuration['logicalProcessors'] == 8
    assert re.search(r'(?m)^\s*ded_bRestartWhenEmpty\s*=\s*0\s*;', configuration['serverInit'])
    assert configuration['dllSha256'] == result['dllSha256']
    hour = dict(passed=True, scope='Local 2x4 vanilla fleet hour with controlled human/lifecycle checks; early captured replicated native tick hour, snapshots have no individual UTC timestamps; no AI, permanent supervisor or external server-browser acceptance.', dllSha256=result['dllSha256'], elapsedSeconds=result['elapsedSeconds'], steadySeconds=result['steadySeconds'], completeEightNameQuerySpanSeconds=span, completeEightNameQueries=len(steady), activeBotMinuteWindows=480, raw=raw, replicatedFrameRaw=frame_raw, framePrefixCapturedUtc=frame_gate['utc'], frameCaptureAfterFinalQuerySeconds=frame_lag, liveAtCleanup=live, finalStops=final_stops, crcAcceptedCount=result['crcAcceptedCount'], restoredFiles=common['restoredFiles'])
    (root / 'hour-acceptance-audit.json').write_text(json.dumps(hour, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in hour.items() if k not in ('raw','replicatedFrameRaw','finalStops')}))
    return hour

if __name__ == '__main__':
    audit(pathlib.Path(sys.argv[1]))
