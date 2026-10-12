"""Summarize existing retail evidence; acceptance remains the native PS gates."""
import datetime as dt
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
count = int(sys.argv[2])
output = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else root
output.mkdir(parents=True, exist_ok=True)
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def lines(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8-sig').splitlines() if s.strip()] if path.exists() else []
def field(text, key):
    match = re.search(r'\\' + re.escape(key) + r'\\([^\\]*)', text)
    return match[1] if match else None
def time(text):
    return dt.datetime.fromisoformat(text.replace('Z', '+00:00'))
def write(name, value):
    (output / name).write_text(json.dumps(value, indent=2), encoding='utf-8')

queries = lines(root / 'queries.jsonl')
first = next(i for i, q in enumerate(queries) if field(q['\\status\\'], 'numplayers') == str(count))
steady = queries[first:]
identities = read(root / f'identities-{count}.json')
invalid = []
for q in steady:
    status, players = q['\\status\\'], q['\\players\\']
    if field(status, 'numplayers') != str(count) or field(status, 'gamever') != '1.07' or field(status, 'activemod') != '' or any(players.count('\\' + p['name'] + '\\') != 1 for p in identities):
        invalid.append(q['utc'])
identity_pass = len(identities) == count and len({p['name'] for p in identities}) == count and len({p['guid'] for p in identities}) == count and not invalid
write('identity-network-audit.json', dict(identities=identities, playerQueriesChecked=len(steady), invalidQueries=invalid, passed=identity_pass))
resources = lines(root / 'resources.jsonl')
groups = {}
for r in resources:
    groups.setdefault(r['pid'], []).append(r)
summary = []
for pid, rows in groups.items():
    first_row, last_row = rows[0], rows[-1]
    seconds = (time(last_row['utc']) - time(first_row['utc'])).total_seconds()
    summary.append(dict(role=pathlib.PureWindowsPath(first_row['exe']).parts[-3], pid=pid, samples=len(rows), sampledSeconds=round(seconds, 2), averageHostCpuPercent=round((last_row['cpuSeconds'] - first_row['cpuSeconds']) / seconds / 8 * 100, 2) if seconds else None, peakPrivateMiB=round(max(r['privateBytes'] for r in rows) / 2**20, 2), lastPrivateMiB=round(last_row['privateBytes'] / 2**20, 2), peakWorkingSetMiB=round(max(r['workingSet'] for r in rows) / 2**20, 2)))
network = dict(allQueries=len(queries), steadyQueries=len(steady), firstFullUtc=steady[0]['utc'], invalidSteadyQueries=len(invalid), queryErrors=len(lines(root / 'query-errors.jsonl')))
write('resource-network-summary.json', dict(network=network, resources=summary))
telemetry = read(root / f'native-{count}-Soak' / 'telemetry.json')
players = [{k: p[k] for k in ('player', 'samples', 'firstTick', 'lastTick', 'distinctPositions', 'distinctYaw', 'fireOnSamples', 'fireOffSamples')} for p in telemetry['players']]
minute_keys = [k for k, v in telemetry.items() if isinstance(v, list) and v and isinstance(v[0], dict) and 'minute' in v[0]]
minutes = telemetry[minute_keys[0]] if minute_keys else []
write('telemetry-summary.json', dict(players=players, minuteWindows=len(minutes), minimumSamples=min((m['samples'] for m in minutes), default=0), minimumPositions=min((m['positions'] for m in minutes), default=0), minimumYaw=min((m['yaw'] for m in minutes), default=0), rejectedSnapshotLines=telemetry.get('rejectedSnapshotLines')))
assert identity_pass and not network['queryErrors'], 'Identity/network audit failed'
print(json.dumps(dict(network=network, resources=summary, players=players, minuteWindows=len(minutes))))
