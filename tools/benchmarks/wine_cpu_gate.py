"""Fail-closed evidence gates for isolated Retail 1.07 Wine benchmarks."""
import os
from pathlib import Path
import re
import tempfile

def write_runtime_config(path, text, uid, gid):
    """Atomically publish a private script owned by the actual Wine runtime user."""
    path=Path(path)
    fd,name=tempfile.mkstemp(prefix=path.name+".",dir=path.parent)
    try:
        with os.fdopen(fd,"w") as stream:
            os.fchmod(stream.fileno(),0o600)
            os.fchown(stream.fileno(),uid,gid)
            stream.write(text)
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)

def action_evidence(text, elapsed, slots=4):
    """Measure tick deltas from boundary snapshots; caller supplies wall duration."""
    if elapsed<=0:raise ValueError("invalid duration")
    if re.search(r"Cannot load script|Permission denied|[Uu]nknown symbol",text):
        raise ValueError("script load failed")
    if re.search(r"SYNCBAD|Too many bad syncs|CRC check failed",text,re.I):
        raise ValueError("sync/CRC failure")
    rates=[]; moved=[]
    for slot in range(slots):
        rows=re.findall(r"\[BotDriver\] bot"+str(slot)+r" tick=(\d+) pos=\(([^)]+)\)",text)
        if len(rows)<2:raise ValueError("missing slot evidence: "+str(slot))
        ticks=[int(row[0]) for row in rows]
        if any(b<a for a,b in zip(ticks,ticks[1:])):raise ValueError("slot reset during sample")
        rate=(ticks[-1]-ticks[0])/elapsed
        if not 19<=rate<=21:raise ValueError("action rate outside 20Hz tolerance: "+str(rate))
        motion=len(set(row[1] for row in rows))>1
        if not motion:raise ValueError("no motion for slot "+str(slot))
        rates.append(round(rate,3));moved.append(motion)
    return {"rates_hz":rates,"moved":moved}

def check_throttling(before,after):
    """Historic throttling is irrelevant; any new throttled period rejects a run."""
    if after.get("nr_throttled",0)>before.get("nr_throttled",0):
        raise ValueError("cgroup throttled during measurement")
