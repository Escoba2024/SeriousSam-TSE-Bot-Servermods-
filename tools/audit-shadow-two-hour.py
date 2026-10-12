"""Separate two-local-player hour; legacy native runner uses hard teardown."""
import datetime as dt
import importlib.util
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

def json_lines(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]

def resource_coverage(resources, steady):
    query_start, query_end = timestamp(steady[0]['utc']), timestamp(steady[-1]['utc'])
    starts, ends, summaries = [query_start], [query_end], []
    for role in ('TSE-BotClient','TSE-Observer','TSE-Server'):
        rows=[r for r in resources if pathlib.PureWindowsPath(r['exe']).parts[-3]==role]
        assert rows and len({r['pid'] for r in rows})==1
        start, end = timestamp(rows[0]['utc']), timestamp(rows[-1]['utc'])
        seconds=(end-start).total_seconds()
        assert seconds>=3600 and all(0 < (timestamp(b['utc'])-timestamp(a['utc'])).total_seconds()<=60 for a,b in zip(rows,rows[1:]))
        assert start <= query_start + dt.timedelta(seconds=60) and end >= query_end - dt.timedelta(seconds=60)
        starts.append(start)
        ends.append(end)
        summaries.append(dict(role=role,pid=rows[0]['pid'],sampledSeconds=seconds,peakPrivateMiB=max(r['privateBytes'] for r in rows)/2**20))
    overlap=(min(ends)-max(starts)).total_seconds()
    assert overlap>=3600, 'Resources and full-player queries do not share one complete hour'
    return summaries, overlap

def audit(root):
    native = root / 'native-2-Soak'
    diagnostics = read(root / 'diagnostics.json')
    result = read(native / 'result.json')
    telemetry = read(native / 'telemetry.json')
    identities = read(root / 'identities-2.json')
    assert diagnostics['passed'] and diagnostics['counts']==[2] and diagnostics['syncMinutes']==60
    assert diagnostics['applicationEventsRead'] and not any(diagnostics[k] for k in ('cleanupErrors','ownedProcesses','udpPorts','matchingCrashEvents','crashReports'))
    assert diagnostics['restored'] and all(item['restored'] for item in diagnostics['restored'])
    for flag in ('loaded','alive','serverAlive','crcAccepted','clientCurrentlyJoined','observerCurrentlyJoined','observerAlive'):
        assert result[flag], flag
    assert result['elapsedSeconds'] >= 3600
    assert result['sha256']=='24053920C63E02F9883056331B246BEF2D08D645FFCCE2C74ED7EDC9B35B9ACF'
    assert len(identities)==2 and len({p['guid'] for p in identities})==2 and all(p['guidSource']=='profile+sidecar' for p in identities)
    names = {p['name'] for p in identities}
    assert len(names)==2
    queries = json_lines(root / 'queries.jsonl')
    def complete(q):
        players = re.findall(r'\\player_\d+\\([^\\]+)', q['\\players\\'])
        return field(q['\\status\\'],'numplayers')=='2' and len(players)==2 and set(players)==names
    first = next(i for i,q in enumerate(queries) if complete(q))
    steady = queries[first:]
    assert all(complete(q) and field(q['\\status\\'],'gamever')=='1.07' and field(q['\\status\\'],'activemod')=='' for q in steady)
    span = (timestamp(steady[-1]['utc'])-timestamp(steady[0]['utc'])).total_seconds()
    assert span >= 3600
    assert all(0 < (timestamp(b['utc'])-timestamp(a['utc'])).total_seconds() <= 60 for a,b in zip(steady,steady[1:]))
    error_file = root / 'query-errors.jsonl'
    assert not error_file.exists() or not error_file.read_text(encoding='utf-8-sig').strip()
    assert len(telemetry['players'])==2 and not telemetry['rejectedSnapshotLines']
    windows = telemetry['activeSyncMinutes']
    assert len(windows)==120 and {(w['player'],w['minute']) for w in windows}=={(p,m) for p in (0,1) for m in range(1,61)}
    assert all(w['samples']>=1190 and w['positions']>=10 and w['yaw']>=10 and w['fireOn'] and w['fireOff'] for w in windows)
    resources = json_lines(root / 'resources.jsonl')
    resource_summary, resource_overlap = resource_coverage(resources, steady)
    spec=importlib.util.spec_from_file_location('fleet_hour',pathlib.Path(__file__).with_name('audit-shadow-hour.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raw=module.raw_minutes(native/'SeriousSam.log',expected_players=2,require_shutdown=False)
    assert len(raw['minuteWindows'])==120
    record=dict(passed=True,scope='Separate one-process two-local-bot60m gate, vanilla observer; native legacy runner uses hard teardown, no graceful shutdown assertion.',dllSha256=result['sha256'],elapsedSeconds=result['elapsedSeconds'],completeTwoNameQuerySpanSeconds=span,completeTwoNameQueries=len(steady),sharedResourceQuerySeconds=resource_overlap,activeBotMinuteWindows=120,raw=raw,resources=resource_summary,restoredFiles=len(diagnostics['restored']),crcAcceptedCount=result['crcAcceptedCount'])
    (root/'hour-acceptance-audit.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k!='raw'}))
    return record

if __name__=='__main__':
    audit(pathlib.Path(sys.argv[1]))
