"""Independent audit of failed native JoinGame followed by same-process recovery."""
import datetime as dt
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1]).resolve()
retail = root / 'retail'
def load(name, base=retail):
    return json.loads((base / name).read_text(encoding='utf-8-sig'))
def text(name):
    with (retail / name).open(encoding='utf-8-sig', errors='replace', newline='') as f:
        return f.read()
def rows(name):
    return [json.loads(row) for row in text(name).splitlines() if row.strip()]
def instant(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))

native = load('result.json')
diag = load('diagnostics.json')
preservation = load('preservation.json', root)
fault = load('fault-finished.json')
assert native['passed'] and native['failedJoinRecovery'] and native['mapCycle']
assert native['controlledObserverRejoin'] and native['crcAcceptedCount'] >= 9
assert preservation['passed'] and not preservation['cleanupErrors']
assert preservation['ownedProcesses'] == preservation['udpPorts'] == 0
assert all(v['restored'] for v in preservation['restored'])
assert diag['applicationEventsRead'] and not diag['cleanupErrors']
assert diag['ownedProcesses'] == diag['udpPorts'] == diag['crashReports'] == diag['matchingCrashEvents'] == 0
assert not diag['faultHelperRemaining']
assert fault['passed'] and fault['resumed'] and fault['failedByClient'] == [True, True]
pause = (instant(fault['resumedUtc']) - instant(fault['pausedUtc'])).total_seconds()
assert 0 < pause < 62
identities = load('identities.json')
loaded = load('runtime-identities.json')
key = lambda v: (v['clientDir'], v['slot'], v['name'], v['guid'], v['guidSource'])
assert {key(v) for v in identities} == {key(v) for v in loaded}
assert len(loaded) == len({v['guid'] for v in loaded}) == len({v['name'] for v in loaded}) == 8
assert all(v['guidSource'] == 'profile+sidecar' for v in loaded)
names = {v['name'] for v in loaded}
queries = rows('queries.jsonl')
maps = []
for map_name in ('Fortress', 'Little Trouble', "We Got Skulls'n'Bones Too"):
    complete = []
    for q in queries:
        m = re.search(r'\\mapname\\([^\\]+)', q['status'])
        players = re.findall(r'\\player_\d+\\([^\\]+)\\', q['players'])
        if m and m[1] == map_name and re.search(r'\\numplayers\\8\\', q['status']) and len(players) == 8 and set(players) == names:
            assert re.search(r'\\gamever\\1\.07\\', q['status']) and re.search(r'\\activemod\\\\', q['status'])
            complete.append(q)
    assert len(complete) >= 3, map_name
    span = (instant(complete[-1]['utc']) - instant(complete[0]['utc'])).total_seconds()
    assert span >= 10
    maps.append(dict(map=map_name, completeSamples=len(complete), sampleSpanSeconds=round(span, 3)))

states = load('fleet-state.json')['processes']
assert states == load('recovery-retained-processes.json')['processes']
resources = rows('resources.jsonl')
clients = []
server_text = text('TSE-Server-Dedicated_BotTest.log')
levels = list(re.finditer(r"^\s*level: '([^']+)'", server_text, re.M))
assert len(levels) == 3
for i, map_stem in enumerate(('Fortress', 'DM_LittleTrouble', 'WeGotSkullsNBonesToo')):
    assert levels[i][1].endswith('\\'+map_stem+'.wld')
    block = server_text[levels[i].start():levels[i+1].start() if i+1<len(levels) else len(server_text)]
    assert block.count('CRC check OK') >= 3
    assert all(name+'^r joined' in block for name in names)
assert not re.search(r'sync lost|wrong crc|access.violation|Timeout while waiting|Client: Timeout receiving UDP port',server_text,re.I)
for client_index, state in enumerate(states):
    role = pathlib.Path(state['clientDir']).name
    samples = [r for r in resources if r['role'] == role]
    assert len(samples) > 5 and {r['pid'] for r in samples} == {state['pid']}
    log = text(role + '-SeriousSam.log')
    attempts = list(re.finditer(r'^\[BotReconnect\] attempt address=([^\r\n]+)\r?$', log, re.M))
    pending, allowed, pending_address = [], [], None
    for index, attempt in enumerate(attempts):
        end = attempts[index+1].start() if index+1 < len(attempts) else len(log)
        block = log[attempt.start():end]
        results = list(re.finditer(r'^\[BotReconnect\] result=(failed|joined)\r?$', block, re.M))
        assert len(results) == 1
        result = results[0]
        before, after = block[:result.start()], block[result.end():]
        if pending:
            assert pending_address == attempt[1]
        if result[1] == 'failed':
            errors = list(re.finditer(r'^Cannot join game:\r?\n(?P<error>Timeout while waiting for reply|Client: Timeout receiving UDP port)\r?$', before, re.M))
            assert len(errors) == 1
            assert not re.search(r'^\s*joined\s*$|^Disconnected:', after, re.M)
            pending.append(attempt.start() + errors[0].start('error'))
            pending_address = attempt[1]
        else:
            assert re.search(r'^\s*joined\s*$', before, re.M)
            assert not re.search(r'^Disconnected:|^Cannot join game:', before, re.M)
            allowed.extend(pending)
            pending = []
            pending_address = None
    assert not pending and allowed
    assert min(allowed) >= fault['logOffsets'][client_index]
    unexpected = [m.group() for m in re.finditer(r'sync lost|out of sync|bad sync|wrong crc|access.violation|Timeout while waiting|Client: Timeout receiving UDP port', log, re.I) if m.start() not in allowed]
    assert not unexpected, unexpected
    gate = load('recovery-' + role + '.json')
    assert gate['failedJoins'] == len(allowed) and gate['successfulRetries'] == 2
    sessions = re.split(r'^[ \t]*joined[ \t]*\r?$', log, flags=re.M)[1:]
    assert len(sessions) == 3
    windows = []
    for session_index, session in enumerate(sessions, 1):
        session = session.split('Disconnected:', 1)[0]
        for slot in range(4):
            records = re.findall(r'\[BotDriver\] bot' + str(slot) + r' tick=(\d+) pos=\(([^)]+)\) heading=([-\d.]+) fire=([01])', session)
            assert len(records) >= 10
            ticks = [int(r[0]) for r in records]
            assert all(a < b for a,b in zip(ticks,ticks[1:]))
            assert len({r[1] for r in records}) > 1 and len({r[2] for r in records}) > 1
            assert {r[3] for r in records} == {'0','1'}
            windows.append(dict(session=session_index, slot=slot, samples=len(records), firstTick=ticks[0], lastTick=ticks[-1]))
    clients.append(dict(role=role,pid=state['pid'],failedJoins=len(allowed),successfulRetries=2,sameProcessAcrossMaps=True,actionWindows=windows))
observer = load('observer-map-sessions.json')
assert len(observer) == len({v['pid'] for v in observer}) == 3
for session in observer:
    log = text(session['log'])
    assert re.search(r'^\s*joined\s*$', log, re.M)
    assert not re.search(r'sync lost|wrong crc|Timeout while waiting|Client: Timeout receiving UDP port', log, re.I)
    if 'state' in session:
        stops = load(session['state'])['results']
        assert len(stops) == 1 and stops[0]['state'] == 'graceful'
audit = dict(passed=True,scope='Short native failed-join recovery gate; three maps and controlled fresh vanilla observer sessions. No hour or permanent supervisor acceptance.',dllSha256=native['dllSha256'],elapsedSeconds=native['elapsedSeconds'],pauseSeconds=round(pause,3),crcAcceptedCount=native['crcAcceptedCount'],maps=maps,clients=clients,restoredFiles=len(preservation['restored']),observerSessions=observer)
(root/'acceptance-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k != 'clients'},indent=2))
