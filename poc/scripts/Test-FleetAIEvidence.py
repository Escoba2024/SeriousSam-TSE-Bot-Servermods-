"""Bounded-memory audit of native AI decisions, replicated actions and fleet life cycle."""
import argparse
import datetime as dt
import hashlib
import json
import math
import re
from pathlib import Path

REGISTER = re.compile(r'^\[BotDriver\] local player (\d+) \(player index (\d+)\) is now bot-driven: (.+)$')
DRIVER = re.compile(r'^\[BotDriver\] bot(\d+) tick=(\d+) .* fire=(\d+)$')
FIELDS = re.compile(r'(\w+)=([^\s]+)')


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def assert_candidate(result, digest, startup_digest):
    require(result['dllSha256'] == digest, 'evidence does not use the exact candidate')
    require(result['startupSha256'] == startup_digest, 'evidence does not use the exact startup')


def record(line):
    for tag in ('BotNavigation', 'BotCombat', 'BotCombatWeapon', 'BotSnapshot'):
        if line.startswith('[' + tag + '] '):
            v = dict(FIELDS.findall(line))
            return tag, int(v['tick']), int(v['player'] if tag == 'BotSnapshot' else v['local']), v
    match = DRIVER.match(line)
    if match:
        return 'BotDriver', int(match[2]), int(match[1]), {'fire': match[3]}
    return None


def position(v):
    p = tuple(map(float, v['pos'].strip('()').split(',')))
    require(len(p) == 3 and all(math.isfinite(n) for n in p), 'nonfinite native position')
    return p


def assert_combat_bounds(c):
    yaw,pitch,move=(float(c[key]) for key in ('yawDelta','pitchDelta','move'))
    require(all(math.isfinite(v) for v in (yaw,pitch,move)) and abs(yaw)<=2.251 and abs(pitch)<=2.251 and 0<=move<=1,'native combat action bounds')


class PlayerAudit:
    def __init__(self, slot, player, name):
        self.slot, self.player, self.name = slot, player, name
        self.count = self.brush_turns = self.successes = self.attacks = self.age = self.max_age = 0
        self.advance_ticks = 0
        self.brush = False
        self.advance_start = None
        self.previous_position = None
        self.windows = []
        self.total_positions = set()
        self.reset_window()

    def reset_window(self):
        self.window_samples = self.on = self.dead = self.targets = self.holds = 0
        self.positions, self.yaws = set(), set()
        self.first_tick = None

    def update(self, tick, frame):
        n, c, d, s = (frame[k] for k in ('BotNavigation', 'BotCombat', 'BotDriver', 'BotSnapshot'))
        require(int(c['self']) == self.player, 'combat self identity does not match native registration')
        assert_combat_bounds(c)
        active, phase, alive = (int(n[k]) for k in ('active', 'phase', 'alive'))
        began, finished = int(n['began']), int(n['finished'])
        require(alive == int(c['alive']), 'combat/navigation life state differs')
        delta, forward = float(n['delta']), float(n['forward'])
        distances = [float(n[k]) for k in ('front', 'left', 'right')]
        p = position(n)
        # ObstacleRecovery resets internally on a horizontal jump over eight
        # metres, even if it begins another recovery in that same Update call.
        if self.previous_position is not None and math.hypot(p[0]-self.previous_position[0], p[2]-self.previous_position[2]) > 8:
            self.brush = False
            self.age = self.advance_ticks = 0
            self.advance_start = None
        self.previous_position = p
        require(all(math.isfinite(v) for v in (delta, forward, *distances)), 'nonfinite navigation evidence')
        require(abs(delta) <= 2.251 and 0 <= forward <= 1 and all(0 <= v <= 3 for v in distances), 'native action/ray bounds')
        require(not active or (alive and not int(n['hold']) and phase in (1, 2)), 'dead/held or invalid navigation remains active')
        if not active and not finished:
            self.brush = False
        if active and phase == 1:
            require(forward == 0, 'turn recovery also advances')
        if began:
            self.advance_start = None
            if int(n['reason']) == 1 and int(n['hitType']) == 4 and distances[0] < 1.2:
                require(active and phase == 1 and forward == 0 and delta != 0, 'brush obstruction did not turn in place')
                if max(distances[1:]) >= 1.2 and distances[1] != distances[2]:
                    require((delta > 0) == (distances[1] > distances[2]), 'turn away from freer side')
                self.brush_turns += 1
                self.brush = True
        self.age = self.age + 1 if active or finished else 0
        self.max_age = max(self.max_age, self.age)
        require(self.age <= 240, 'recovery exceeded overall attempt budget')
        if active and phase == 2:
            self.advance_ticks += 1
            require(self.advance_ticks <= 40, 'advance exceeded phase budget')
            if self.advance_start is None:
                self.advance_start = p
            if finished and self.brush and math.hypot(p[0]-self.advance_start[0], p[2]-self.advance_start[2]) >= 2:
                self.successes += 1
        else:
            self.advance_start = None
            self.advance_ticks = 0
        if finished:
            self.age = self.advance_ticks = 0
            self.brush = False
            self.advance_start = None
        if int(d['fire']) and alive:
            require(not active and int(c['ready']), 'attack while recovering or without combat readiness')
            w = frame.get('BotCombatWeapon')
            require(w is not None and int(w['desired']) == int(w['current']) == int(w['wanted']) == int(c['weapon']), 'attack without acknowledged native weapon')
            self.attacks += 1
        self.count += 1
        self.window_samples += 1
        if self.first_tick is None:
            self.first_tick = tick
        native_position = position(s)
        self.positions.add(native_position)
        if len(self.total_positions) < 11:
            self.total_positions.add(native_position)
        yaw, health = float(s['yaw']), float(s['health'])
        require(math.isfinite(yaw) and math.isfinite(health), 'nonfinite replicated native state')
        self.yaws.add(yaw)
        self.on += bool(int(s['buttons']) & 1)
        self.dead += health <= 0
        self.targets += int(c['target']) >= 0
        self.holds += bool(int(n['hold']))
        if self.window_samples == 1200:
            self.finish_window(tick)

    def finish_window(self, tick):
        self.windows.append(dict(firstTick=self.first_tick, lastTick=tick, samples=self.window_samples,
            distinctPositions=len(self.positions), distinctYaw=len(self.yaws), fireOn=self.on,
            fireOff=self.window_samples-self.on, deadSamples=self.dead, targetSamples=self.targets,
            holdSamples=self.holds))
        self.reset_window()

    def result(self, last_tick):
        if self.window_samples:
            self.finish_window(last_tick)
        require(self.brush_turns and self.successes, f'no actual brush turn/completed progress local {self.slot}')
        require(self.attacks, f'no living combat attacks local {self.slot}')
        require(len(self.total_positions) > 10, 'no replicated native movement')
        require(sum(w['fireOn'] for w in self.windows) and sum(w['fireOff'] for w in self.windows), 'missing replicated native fire press/release')
        return dict(localSlot=self.slot, player=self.player, name=self.name, decisions=self.count,
            brushTurns=self.brush_turns, advancesAtLeast2m=self.successes, maxAttemptTicks=self.max_age,
            livingAttackTicks=self.attacks, replicatedDistinctPositionsAtLeast=len(self.total_positions), windows=self.windows)


def audit_stream(path, expected_slots=4, min_samples=600, minutes=0):
    # First pass locates the final native source session and its complete endpoint.
    # A replaced process must earn its own window; earlier activity is never added.
    start_offset, slots, lasts, offsets, clock = 0, {}, {}, {}, None
    with path.open('rb') as stream:
        while True:
            offset = stream.tell()
            raw = stream.readline()
            if not raw:
                break
            line = raw.decode('utf-8', errors='replace').strip()
            require(not re.search(r'bad sync|sync lost|out of sync|wrong crc|Timeout while waiting', line, re.I), 'native synchronization/runtime error')
            match = REGISTER.match(line)
            if match:
                slot, player = int(match[1]), int(match[2])
                if slot == 0:
                    start_offset, slots, lasts, offsets, clock = offset, {}, {}, {0: 0}, None
                require(slot not in slots, 'duplicate native source registration')
                slots[slot] = (player, match[3])
            r = record(line)
            if r:
                tag, tick, index, _ = r
                if tag == 'BotNavigation':
                    if index == 0:
                        clock = tick
                    elif index not in offsets:
                        require(clock is not None, 'missing primary snapshot clock for local activation')
                        offsets[index] = clock-tick
                lasts[(tag, index)] = tick
    require(set(slots) == set(range(expected_slots)) and len({v[0] for v in slots.values()}) == expected_slots, 'distinct complete native local registrations')
    require(set(offsets) == set(slots) and all(v >= 0 for v in offsets.values()), 'invalid local activation clock offsets')
    endpoints = []
    for slot, (player, _) in slots.items():
        for tag, index in (('BotNavigation', slot), ('BotCombat', slot), ('BotDriver', slot), ('BotSnapshot', player)):
            require((tag, index) in lasts, 'missing matching native decision/action endpoint')
            endpoints.append(lasts[(tag, index)] + (offsets[slot] if tag != 'BotSnapshot' else 0))
    last_tick = min(endpoints)
    require(max(endpoints)-last_tick <= 2, 'incomplete native trailing decisions exceed shutdown allowance')
    sample_count = minutes*1200 if minutes else last_tick-max(offsets.values())
    require(last_tick-max(offsets.values()) >= sample_count >= min_samples, 'insufficient native samples for requested window')
    first_tick = last_tick-sample_count+1
    states = {s: PlayerAudit(s, p, name) for s, (p, name) in slots.items()}
    players = {p: s for s, (p, _) in slots.items()}
    frames, next_tick = {}, first_tick

    def flush(end):
        nonlocal next_tick
        while next_tick <= end:
            frame = frames.pop(next_tick, {})
            for slot, state in states.items():
                v = frame.get(slot, {})
                require(all(k in v for k in ('BotNavigation', 'BotCombat', 'BotDriver', 'BotSnapshot')), f'missing matching native decision/action tick {next_tick} local {slot}')
                state.update(next_tick, v)
            next_tick += 1

    with path.open('rb') as stream:
        stream.seek(start_offset)
        for raw in stream:
            r = record(raw.decode('utf-8', errors='replace').strip())
            if r is None:
                continue
            tag, tick, index, fields = r
            if tag != 'BotSnapshot' and index in offsets:
                tick += offsets[index]
            if not first_tick <= tick <= last_tick:
                continue
            slot = players.get(index) if tag == 'BotSnapshot' else index
            if slot not in states:
                continue
            if tick >= next_tick+3:
                flush(tick-3)
            require(tick >= next_tick, 'out-of-order native tick')
            v = frames.setdefault(tick, {}).setdefault(slot, {})
            require(tag not in v, f'duplicate {tag} native row tick {tick} local {slot}')
            v[tag] = fields
    flush(last_tick)
    result = [s.result(last_tick) for s in states.values()]
    if minutes:
        require(all(len(p['windows']) == minutes and all(w['samples'] == 1200 for w in p['windows']) for p in result), 'incomplete native minute windows')
    return dict(client=path.name, firstTick=first_tick, lastTick=last_tick,
        localTickOffsets={str(s): v for s,v in offsets.items()},
        trailingIncompleteTicks=max(endpoints)-last_tick, players=result)


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def timestamp(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))


def query_fields(text):
    require(isinstance(text, str), 'malformed native query framing')
    pairs = list(re.finditer(r'\\([^\\]+)\\([^\\]*)', text))
    require(''.join(match[0] for match in pairs) == text, 'malformed native query framing')
    fields = {}
    for match in pairs:
        key, value = match.groups()
        require(key not in fields, 'duplicate query field')
        fields[key] = value
    require(fields.get('final') == '', 'missing or invalid native query completion marker')
    return fields


def audit_queries(queries, expected_names, minimum_seconds):
    stages, steady = [], []
    for q in queries:
        status, players = query_fields(q['status']), query_fields(q['players'])
        require(status.get('gamever') == '1.07' and status.get('activemod') == '', 'wrong native version/mod')
        count = int(status['numplayers'])
        rows = []
        for key, name in players.items():
            match = re.fullmatch(r'player_(\d+)', key)
            if match:
                rows.append((int(match[1]), name))
        require(all(0 <= index < 16 and name for index, name in rows) and
                len({index for index, _ in rows}) == len(rows), 'invalid or duplicate native player index')
        names = [name for _, name in rows]
        require(len(set(names)) == len(names), 'duplicate native player names')
        startup_transition = q.get('label') == 'eight-bots' and len(names) < count
        require(startup_transition or len(names) == count, 'incomplete native player list')
        if count in (8, 9) and not startup_transition:
            require(expected_names <= set(names) and (count != 9 or 'Vanilla_Human_1' in names), 'wrong native fleet/human identities')
        if count == 4:
            require(set(names) == {n for n in expected_names if n.startswith('TSE_Fleet_A_')}, 'wrong four freed native slots')
        if q.get('label'):
            stages.append(dict(label=q['label'], players=count, utc=q['utc']))
        else:
            require(count == 8 and set(names) == expected_names, 'steady fleet lost native players')
            steady.append(q)
    require(len(steady) >= 2, 'missing steady native queries')
    query_span = (timestamp(steady[-1]['utc'])-timestamp(steady[0]['utc'])).total_seconds()
    require(query_span >= minimum_seconds, 'insufficient continuous native query span')
    gaps = [(timestamp(b['utc'])-timestamp(a['utc'])).total_seconds() for a, b in zip(steady, steady[1:])]
    require(all(0 < gap <= 60 for gap in gaps), 'native steady query gap or reversed timestamp')
    return stages, query_span


def audit_resources(rows, minimum_seconds):
    roles = ('TSE-BotClient', 'TSE-BotClient2', 'server')
    require({row['role'] for row in rows} == set(roles), 'incomplete native resource roles')
    pids = {row['pid'] for row in rows}
    require(all(type(pid) is int and pid > 0 for pid in pids), 'invalid native resource process identities')
    stats = []
    for role in roles:
        samples = [row for row in rows if row['role'] == role]
        require(len(samples) >= 2 and len({row['pid'] for row in samples}) == 1, 'native resource process replacement or missing samples')
        for row in samples:
            require(all(math.isfinite(row[key]) and row[key] >= 0 for key in ('cpuSeconds', 'privateBytes', 'workingSet', 'handles', 'threads')) and row['privateBytes'] > 0 and row['workingSet'] > 0, 'invalid native resource value')
        times = [timestamp(row['utc']) for row in samples]
        seconds = (times[-1]-times[0]).total_seconds()
        require(seconds >= minimum_seconds, 'insufficient native resource duration')
        require(all(0 < (b-a).total_seconds() <= 60 for a, b in zip(times, times[1:])), 'native resource gap or reversed timestamp')
        require(all(b['cpuSeconds'] >= a['cpuSeconds'] for a, b in zip(samples, samples[1:])), 'native resource CPU time reversed')
        stats.append(dict(role=role, pid=samples[0]['pid'], samples=len(samples), seconds=seconds,
            averageCpuOneCorePercent=round(100*(samples[-1]['cpuSeconds']-samples[0]['cpuSeconds'])/seconds, 3),
            peakPrivateMiB=round(max(row['privateBytes'] for row in samples)/1048576, 3),
            peakWorkingSetMiB=round(max(row['workingSet'] for row in samples)/1048576, 3),
            peakHandles=max(row['handles'] for row in samples), peakThreads=max(row['threads'] for row in samples)))
    require(len(pids) == 3, 'invalid native resource process identities')
    return stats


def audit_runtime(root, dll, startup, minutes=0):
    native = root/'retail'
    result, diagnostics, preservation = (read(p) for p in (native/'result.json', native/'diagnostics.json', root/'preservation.json'))
    digest, startup_digest = (hashlib.sha256(p.read_bytes()).hexdigest().upper() for p in (dll, startup))
    assert_candidate(result, digest, startup_digest)
    require(all(v['passed'] for v in (result, diagnostics, preservation)), 'native fleet/preservation gate')
    require(result['crcAcceptedCount'] >= 3 and result['steadySeconds'] >= (minutes*60 if minutes else 120), 'native duration/CRC gate')
    require(diagnostics['applicationEventsRead'] and not any(diagnostics[k] for k in ('ownedProcesses', 'udpPorts', 'matchingCrashEvents', 'crashReports', 'cleanupErrors')), 'runtime cleanup/crash gate')
    require(not any(preservation[k] for k in ('ownedProcesses', 'udpPorts', 'cleanupErrors')) and all(v['restored'] for v in preservation['restored']), 'original runtime preservation gate')
    identities = read(native/'runtime-identities.json')
    require(len(identities) == len({p['guid'] for p in identities}) == len({p['name'] for p in identities}) == 8 and all(p['guidSource'] == 'profile+sidecar' for p in identities), 'distinct native profiles/GUIDs')
    expected_names = {p['name'] for p in identities}
    queries = [json.loads(line) for line in (native/'queries.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    stages, query_span = audit_queries(queries, expected_names, minutes*60 if minutes else 100)
    resources = audit_resources([json.loads(line) for line in (native/'resources.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()], minutes*60 if minutes else 100)
    if result['lifecycle']:
        expected = dict(zip(('eight-bots', 'human-join', 'human-left', 'human-rejoin', 'human-left-again', 'exactly-four-freed', 'four-bots-restored', 'final-eight'), (8, 9, 8, 9, 8, 4, 8, 8)))
        require(all(any(s['label'] == label and s['players'] == count for s in stages) for label, count in expected.items()), 'incomplete native fleet life cycle')
        for label in ('human-leave', 'human-leave-again', 'four-bots-leave'):
            stops = read(native/f'{label}-state.json.stopped.json')['results']
            require(len(stops) == 1 and stops[0]['state'] == 'graceful' and stops[0]['exitCode'] == 1, 'native controlled stop failed')
    observer = (native/'TSE-Observer-SeriousSam.log').read_text(encoding='utf-8-sig', errors='replace')
    kills = [line for line in observer.splitlines() if 'TSE_Fleet_' in line and 'poured lead into' in line]
    require(kills, 'missing independent vanilla observer combat witness')
    return dict(passed=True, dllSha256=digest, startupSha256=startup_digest,
        steadySeconds=result['steadySeconds'], nativeQuerySeconds=query_span, crcAcceptedCount=result['crcAcceptedCount'],
        nativeJoinOnly=bool(result.get('nativeJoinOnly')), lifecycle=bool(result['lifecycle']), stages=stages,
        identities=identities, observerCombatKills=len(kills), resources=resources, restoredFiles=len(preservation['restored']),
        scope='Native transport/lifecycle/resources/preservation only; AI decision/action continuity requires the separate complete stream audit.')


def audit(root, dll, startup, minutes=0):
    result = audit_runtime(root, dll, startup, minutes)
    require(not result['nativeJoinOnly'], 'join-only smoke cannot qualify native decision/action continuity')
    require(result['lifecycle'], 'full fleet AI release requires the native lifecycle')
    clients = [audit_stream(root/'retail'/f'{name}-SeriousSam.log', minutes=minutes) for name in ('TSE-BotClient', 'TSE-BotClient2')]
    require({p['name'] for c in clients for p in c['players']} == {p['name'] for p in result['identities']}, 'decision logs do not match eight native identities')
    result.update(completeMinutesPerBot=minutes, completeMinuteWindows=8*minutes, clients=clients,
        scope='Stock Fortress local deathmatch, 2x4 bot clients. Native decision/action continuity; AI no-target pauses are reported per window. No global routes, item collection, cliff safety, coop, internet or 24/7 qualification.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--dll', type=Path, required=True)
    parser.add_argument('--startup', type=Path, required=True)
    parser.add_argument('--minutes', type=int, default=0)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.minutes >= 0, 'negative minutes')
    result = audit(args.root, args.dll, args.startup, args.minutes)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('NATIVE FLEET AI PASS:', args.output)
