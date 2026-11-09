#!/usr/bin/env python3
"""Read-only native Cecil observation. Reports evidence; never installs or restarts."""
import argparse,datetime,hashlib,json,math,os,re,shutil,subprocess,time
from pathlib import Path
from gamespy_query import query

BAD=re.compile(r"SYNCBAD|Too many bad syncs|CRC check failed|Access violation|Fatal Error|\[CecilLoad\] rejected=|\[CecilInvalidAction\]",re.I)
STATE=re.compile(r"\[CecilState\] (.*)")
FIELDS=re.compile(r"(\w+)=([^\s]+)")
GATES={1:3600,4:3600,8:7200}
# CecilState is emitted every 20 native ticks (normally one second).
# This is an observation-coverage limit, not a relaxed gameplay threshold.
MAX_OBSERVATION_GAP_S=5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse_state(line):
    match=STATE.search(line)
    if not match:return None
    values=dict(FIELDS.findall(match[1]))
    for key in ("local","tick","alive","ready","shots","pickups","deaths","respawns","vis","nav","rays","owned","current","wanted","goal_entity"):
        values[key]=int(values[key])
    values["pos"]=tuple(map(float,values["pos"].strip("()").split(",")))
    if len(values["pos"])!=3 or not all(map(math.isfinite,values["pos"])):raise ValueError("invalid position")
    return values
def process_stats(pid):
    root=Path("/proc")/str(pid)
    fields=(root/"stat").read_text().rsplit(") ",1)[1].split()
    rss=int(next(line.split()[1] for line in (root/"status").read_text().splitlines() if line.startswith("VmRSS:")))
    return {"cpu_s":(int(fields[11])+int(fields[12]))/os.sysconf("SC_CLK_TCK"),"rss_kib":rss,"start_ticks":int(fields[19])}
def host_cpu():
    fields=list(map(int,Path("/proc/stat").read_text().splitlines()[0].split()[1:9]))
    return sum(fields),fields[3]+fields[4]
def memory_stats(text):
    fields={line.split(":",1)[0]:int(line.split()[1]) for line in text.splitlines() if ":" in line}
    total,free=fields["SwapTotal"],fields["SwapFree"]
    assert 0<=free<=total and fields["MemAvailable"]>=0,"invalid memory sample"
    return {"available_kib":fields["MemAvailable"],"swap_total_kib":total,"swap_used_kib":total-free}
def summarize(rows):
    if not rows:return {"samples":0}
    first,last=rows[0],rows[-1]
    return {"samples":len(rows),"ticks":last["tick"]-first["tick"],"positions":len({x["pos"] for x in rows}),
            "shots_delta":last["shots"]-first["shots"],"pickups_delta":last["pickups"]-first["pickups"],
            "deaths_delta":last["deaths"]-first["deaths"],"respawns_delta":last["respawns"]-first["respawns"],
            "weapons":sorted({x["current"] for x in rows if x["alive"]}),"max_rays":max(x["rays"] for x in rows)}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runtime",type=Path,required=True);p.add_argument("--unit-prefix",required=True)
    p.add_argument("--port",type=int,required=True);p.add_argument("--bots",type=int,choices=[1,4,8],required=True)
    p.add_argument("--duration",type=int,required=True);p.add_argument("--dll-sha256",required=True)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--gate",action="store_true")
    p.add_argument("--expected-map",help="pin mapname; otherwise pin the first valid query")
    a=p.parse_args()
    if a.duration<60 or (a.gate and a.duration<GATES[a.bots]):p.error("minimum duration not met")
    if not re.fullmatch(r"[a-f0-9]{64}",a.dll_sha256):p.error("invalid DLL hash")
    a.output.mkdir(parents=True,exist_ok=False)
    roles=["botA"]+(["botB"] if a.bots==8 else [])
    pids={role:int(subprocess.check_output(["systemctl","show",a.unit_prefix+"-"+role.lower()+".service","-p","MainPID","--value"],text=True)) for role in ["server"]+roles}
    pinned={};logs={};offsets={};tails={};errors=[]
    for role,pid in pids.items():
        root=a.runtime/role;proc=Path("/proc")/str(pid)
        assert pid>1 and (proc/"cwd").resolve()==root.resolve(),"unexpected process"
        pinned[role]=process_stats(pid)["start_ticks"]
        if role!="server":
            dll=root/"Bin/GameMP.dll";assert sha(dll)==a.dll_sha256
            maps=(proc/"maps").read_text();assert str(dll) in maps and "GameMP.dll (deleted)" not in maps
        logs[role]=root/("Dedicated_BotTest.log" if role=="server" else "SeriousSam.log")
        offsets[role]=logs[role].stat().st_size;tails[role]=""
        if role!="server":
            # Bot logs belong to this process start; historical server errors do not.
            with logs[role].open("rb") as f:initial=f.read(offsets[role]).decode("latin1").split("\n")
            tails[role]=initial.pop()
            errors.extend({"elapsed_s":0.0,"role":role,"line":line} for line in initial if BAD.search(line))
    expected={"Dev-"+str(i) for i in range(1,a.bots+1)}
    expected_slots={"botA:"+str(i) for i in range(min(a.bots,4))}
    if a.bots==8:expected_slots.update("botB:"+str(i) for i in range(4))
    expected_map=a.expected_map
    started=time.monotonic();previous=None;last_save=0;rows={};samples=[];events=[];state_counts={}
    record={"schema_version":1,"status":"RUNNING","utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "bots":a.bots,"required_duration_s":a.duration,"gate":a.gate,"dll_sha256":a.dll_sha256,"pids":pids,"raw_private":True,
            "max_observation_gap_s":MAX_OBSERVATION_GAP_S,"port":a.port,"query_identity":None}
    def save():
        record.update(elapsed_s=time.monotonic()-started,samples=len(samples),errors=errors,
                      slots={k:summarize(v) for k,v in rows.items()})
        temp=a.output/"report.tmp";temp.write_text(json.dumps(record,indent=2)+"\n");temp.replace(a.output/"report.json")
    try:
        with (a.output/"timeseries.jsonl").open("w") as stream:
            while time.monotonic()-started<a.duration:
                now=time.monotonic();elapsed=now-started
                query_error=None
                try:q=query("127.0.0.1",a.port+1,timeout=2,attempts=2)
                except Exception as exc:q={};query_error=exc
                now=time.monotonic();elapsed=now-started
                # Preserve native errors before any population/process/resource failure.
                fresh_lines=[]
                for role,log in logs.items():
                    assert log.stat().st_size>=offsets[role],"log truncated"
                    with log.open("rb") as f:f.seek(offsets[role]);chunk=f.read();offsets[role]=f.tell()
                    parts=(tails[role]+chunk.decode("latin1")).split("\n");tails[role]=parts.pop()
                    for line in parts+[tails[role]]:
                        if BAD.search(line):errors.append({"elapsed_s":elapsed,"role":role,"line":line})
                    fresh_lines.extend((role,line) for line in parts)
                assert not errors,"native log error"
                if query_error is not None:raise query_error
                for role,line in fresh_lines:
                    row=parse_state(line)
                    if row:
                        key=role+":"+str(row["local"]);row["elapsed_s"]=elapsed
                        assert key in expected_slots,"unexpected telemetry slot"
                        assert row["ready"]==1 and row["rays"]<=16,"inactive graph or budget breach"
                        if key in rows:
                            assert row["tick"]>rows[key][-1]["tick"],"bot tick reset"
                            assert elapsed-rows[key][-1]["elapsed_s"]<=MAX_OBSERVATION_GAP_S,"telemetry gap "+key
                        else:assert elapsed<=MAX_OBSERVATION_GAP_S,"late initial telemetry "+key
                        rows.setdefault(key,[]).append(row);stream.write(json.dumps({"slot":key,"state":row})+"\n")
                    elif any(tag in line for tag in ("[CecilGoal", "[CecilPickup]", "[CecilInteraction]", "[CecilGravity]", "[CecilLock]", "[CecilMotionProbe]")):
                        event={"elapsed_s":elapsed,"role":role,"line":line};events.append(event);stream.write(json.dumps({"event":event})+"\n")
                listed=[v for k,v in q.items() if re.fullmatch(r"player_\d+",k)]
                names=set(listed)
                assert expected.issubset(names),"expected bot population missing"
                assert names==expected and len(listed)==a.bots and q.get("numplayers")==str(a.bots),"unexpected player population"
                assert q.get("gamename")=="serioussamse" and q.get("gamever")=="1.07" and q.get("hostport")==str(a.port),"unexpected query identity"
                assert q.get("mapname"),"missing query map"
                if expected_map is None:expected_map=q["mapname"]
                assert q["mapname"]==expected_map,"query map changed"
                record["query_identity"]={k:q[k] for k in ("gamename","gamever","hostport","mapname")}
                if samples:assert elapsed-samples[-1]["elapsed_s"]<=MAX_OBSERVATION_GAP_S,"query sample gap"
                else:assert elapsed<=MAX_OBSERVATION_GAP_S,"late initial query sample"
                for key in expected_slots:
                    last=rows[key][-1]["elapsed_s"] if key in rows else 0
                    assert elapsed-last<=MAX_OBSERVATION_GAP_S,"stale or missing telemetry "+key
                free_disk=shutil.disk_usage("/srv").free
                assert free_disk>=8*2**30,"disk reserve breached"
                proc_stats={r:process_stats(pid) for r,pid in pids.items()}
                assert all(proc_stats[r]["start_ticks"]==pinned[r] for r in pids),"process identity changed"
                total,idle=host_cpu()
                sample={"elapsed_s":elapsed,"players":len(names),"map":q.get("mapname"),"scores":{q[k]:int(q.get("frags_"+k[7:],0)) for k in q if re.fullmatch(r"player_\d+",k)},"processes":proc_stats}
                sample["disk_free_bytes"]=free_disk
                sample["memory"]=memory_stats(Path("/proc/meminfo").read_text())
                if previous:
                    dt=now-previous[0]
                    sample["cpu_percent"]={r:100*(v["cpu_s"]-previous[1][r]["cpu_s"])/dt for r,v in proc_stats.items()}
                    sample["host_percent"]=100*(1-(idle-previous[3])/(total-previous[2]))
                previous=(now,proc_stats,total,idle);samples.append(sample);stream.write(json.dumps({"sample":sample})+"\n")
                if elapsed-last_save>=10:stream.flush();save();last_save=elapsed
                time.sleep(min(1,max(0,a.duration-(time.monotonic()-started))))
        assert len(rows)==a.bots,"per-bot telemetry missing"
        ended=time.monotonic()-started
        assert samples and ended-samples[-1]["elapsed_s"]<=MAX_OBSERVATION_GAP_S,"missing final query coverage"
        for key,values in rows.items():
            assert ended-values[-1]["elapsed_s"]<=MAX_OBSERVATION_GAP_S,"missing final telemetry "+key
            summary=summarize(values)
            assert summary["samples"]>=a.duration*.8 and summary["positions"]>5,"missing sustained movement "+key
            if a.bots>1:assert summary["shots_delta"]>0,"no combat fire "+key
        record["status"]="DURATION_ACTIVITY_SYNC_PASS_BEHAVIOR_REVIEW_REQUIRED"
    except BaseException as exc:
        record.update(status="FAILED",failure=str(exc));raise
    finally:
        save()
        (a.output/"samples.json").write_text(json.dumps(samples)+"\n")
        print(json.dumps(record,indent=2),flush=True)
if __name__=="__main__":main()
