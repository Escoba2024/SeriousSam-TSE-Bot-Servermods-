"""Independent read-only audit of the three-map, two-process retail evidence."""
import collections
import datetime as dt
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1]).resolve()
retail = root / "retail"
def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def rows(name):
    return [json.loads(line) for line in retail.joinpath(name).read_text(encoding="utf-8-sig").splitlines() if line.strip()]
def instant(text):
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))

native = read_json(retail / "result.json")
preservation = read_json(root / "preservation.json")
diag = read_json(retail / "diagnostics.json")
assert native["passed"] and native["mapCycle"] and native["controlledObserverRejoin"]
assert preservation["passed"] and not preservation["cleanupErrors"]
assert preservation["ownedProcesses"] == preservation["udpPorts"] == 0
assert all(item["restored"] for item in preservation["restored"])
assert not diag["cleanupErrors"] and diag["applicationEventsRead"]
assert diag["crashReports"] == diag["matchingCrashEvents"] == 0
identities = read_json(retail / "identities.json")
loaded = read_json(retail / "runtime-identities.json")
key = lambda v: (v["clientDir"], v["slot"], v["name"], v["guid"], v["guidSource"])
assert {key(v) for v in identities} == {key(v) for v in loaded}
assert len(loaded) == len({v["guid"] for v in loaded}) == len({v["name"] for v in loaded}) == 8
assert all(v["guidSource"] == "profile+sidecar" for v in loaded)
names = {v["name"] for v in loaded}
queries = rows("queries.jsonl")
maps = []
for name in ("Fortress", "Little Trouble", "We Got Skulls'n'Bones Too"):
    complete = []
    for q in queries:
        map_field = re.search(r"\\mapname\\([^\\]+)", q["status"])
        if map_field and map_field[1] == name and re.search(r"\\numplayers\\8\\", q["status"]):
            players = re.findall(r"\\player_\d+\\([^\\]+)\\", q["players"])
            if len(players) == 8 and set(players) == names:
                complete.append(q)
    assert len(complete) >= 3, name
    span = (instant(complete[-1]["utc"]) - instant(complete[0]["utc"])).total_seconds()
    assert span >= 10, name
    maps.append({"map": name, "completeSamples": len(complete), "sampleSpanSeconds": round(span, 3)})

states = read_json(retail / "fleet-state.json")["processes"]
resources = rows("resources.jsonl")
clients = []
for state in states:
    role = pathlib.Path(state["clientDir"]).name
    samples = [r for r in resources if r["role"] == role]
    assert samples and {r["pid"] for r in samples} == {state["pid"]}
    text = retail.joinpath(role + "-SeriousSam.log").read_text(encoding="utf-8-sig", errors="replace")
    sessions = re.split(r"(?m)^[ \t]*joined[ \t]*\r?$", text)[1:]
    assert len(sessions) == 3
    assert text.count("[BotReconnect] result=joined") == 2
    assert "[BotReconnect] result=failed" not in text
    windows = []
    for index, session in enumerate(sessions, 1):
        session = session.split("Disconnected:", 1)[0]
        for slot in range(4):
            records = re.findall(r"\[BotDriver\] bot" + str(slot) + r" tick=(\d+) pos=\(([^)]+)\) heading=([-\d.]+) fire=([01])", session)
            assert len(records) >= 10
            ticks = [int(r[0]) for r in records]
            assert all(a < b for a, b in zip(ticks, ticks[1:]))
            assert len({r[1] for r in records}) > 1 and len({r[2] for r in records}) > 1
            assert {r[3] for r in records} == {"0", "1"}
            windows.append({"session": index, "localSlot": slot, "samples": len(records), "firstTick": ticks[0], "lastTick": ticks[-1], "positions": len({r[1] for r in records})})
    clients.append({"role": role, "pid": state["pid"], "sameProcessAcrossMaps": True, "automaticSuccessfulRejoins": 2, "actionWindows": windows})

assert len(clients) == 2
observer = read_json(retail / "observer-map-sessions.json")
assert len(observer) == 3 and len({s["pid"] for s in observer}) == 3
for session in observer:
    text = retail.joinpath(session["log"]).read_text(encoding="utf-8-sig", errors="replace")
    assert re.search(r"(?m)^[ \t]*joined[ \t]*\r?$", text)
    if "state" in session:
        stops = read_json(retail / session["state"])["results"]
        assert len(stops) == 1 and stops[0]["state"] == "graceful"

audit = {"passed": True, "scope": "Three-map short run; automatic successful bot rejoins, controlled vanilla observer processes; no native failed-bot-join recovery or hour acceptance.", "dllSha256": native["dllSha256"], "elapsedSeconds": native["elapsedSeconds"], "crcAcceptedCount": native["crcAcceptedCount"], "maps": maps, "clients": clients, "observerSessions": observer, "restoredFiles": len(preservation["restored"]), "queryRetryErrors": rows("query-retries.jsonl") if retail.joinpath("query-retries.jsonl").exists() else []}
root.joinpath("acceptance-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: audit[k] for k in ("passed", "scope", "dllSha256", "elapsedSeconds", "crcAcceptedCount", "maps", "restoredFiles")}, indent=2))
