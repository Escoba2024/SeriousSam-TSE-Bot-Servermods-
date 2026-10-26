#!/usr/bin/env python3
"""Fail-closed duration receipt checks; never a full M1/release authorization.

The native producer and its immutable source inventory must be verified by the
caller. Synthetic fixtures test these rules but establish no native acceptance.
"""
import json
import math
import os
from datetime import datetime
from pathlib import Path
import re
from native_receipt_io import read_receipt


def _number(value):
    return type(value) in (int,float) and math.isfinite(value)


def evaluate_stage(result, guard, samples, *, bots, required_s, dll_sha256):
    errors=[]
    def require(value, reason):
        if not value: errors.append(reason)
    require(bots in (1,4,8) and type(bots) is int, 'INVALID_BOT_GATE')
    require(_number(required_s) and required_s >= (7200 if bots==8 else 3600), 'INSUFFICIENT_REQUIRED_DURATION')
    require(result.get('status')=='PASS_LIMITED_SESSION_LIFECYCLE' and result.get('scope')=='ISOLATED_NETNS_RETAIL_WINE', 'NATIVE_RESULT_NOT_SUCCESSFUL')
    require(result.get('dll_sha256')==dll_sha256 and bool(re.fullmatch('[0-9a-f]{64}',str(dll_sha256))), 'CANDIDATE_MISMATCH')
    require(result.get('max_bots')==bots and result.get('peak_playing')==bots and result.get('original_client') is True, 'NATIVE_POPULATION_OR_CONTROL_MISSING')
    require(result.get('all_bots_drained') is True and result.get('new_throttled_periods')==0, 'DRAIN_OR_THROTTLE_FAILURE')
    require(result.get('sync_scan_complete') is True and type(result.get('sync_bad')) is int and result['sync_bad']==0, 'SYNC_SCAN_NOT_VERIFIED_CLEAN')
    require(guard.get('status')=='FINISHED' and guard.get('child_exitcode')==0, 'HOST_GUARD_NOT_FINISHED')
    checks=guard.get('samples',[])
    try:
        end=datetime.fromisoformat(result['utc'].replace('Z','+00:00')).timestamp()
        elapsed=result['elapsed_s']
        times=[row['at'] for row in checks]
        require(_number(elapsed) and elapsed>=required_s and all(_number(t) for t in times) and len(times)>1 and
                all(0<b-a<=15 for a,b in zip(times,times[1:])) and
                times[0]<=end-elapsed+5 and end-5<=times[-1]<=end+15, 'HOST_GUARD_TIME_COVERAGE_MISSING')
    except (KeyError,ValueError,TypeError,AttributeError,IndexError):
        require(False,'HOST_GUARD_TIME_COVERAGE_MISSING')
    require(bool(checks) and all(_number(s.get('available_mib')) and s['available_mib']>=768 and _number(s.get('disk_free_gib')) and s['disk_free_gib']>=8 for s in checks), 'HOST_RESERVE_NOT_PROVEN')
    telemetry=result.get('telemetry',{})
    bot_roles=set(telemetry) if isinstance(telemetry,dict) else set()
    roles=bot_roles|{'server','vanilla'}
    require(len(bot_roles)==bots and all(re.fullmatch(r'gamer-[0-9]{3}',role) for role in bot_roles),'BOT_ROLE_SET_INVALID')
    root=Path(result.get('runtime_root','/'))
    require(root.parent==Path('/srv') and root.name.startswith('tse-session-qualification-master-m1-'),'RUNTIME_ROOT_UNBOUND')
    cleanup=result.get('cleanup',[]);unmounts=result.get('unmounts',[])
    require(len(cleanup)==len(roles) and {row.get('role') for row in cleanup}==roles and
            all('errors' in row and row['errors']==[] for row in cleanup), 'PROCESS_CLEANUP_FAILED')
    mounts={str(root/(prefix+role)) for role in roles for prefix in ('','prefix-')}
    require(len(unmounts)==len(mounts) and {row.get('path') for row in unmounts}==mounts and
            all(row.get('exitcode')==0 for row in unmounts), 'MOUNT_CLEANUP_FAILED')
    require(result.get('cleanup_observed_complete') is True,'FINAL_NATIVE_RESOURCE_CENSUS_NOT_CLEAN')
    valid_telemetry=isinstance(telemetry,dict) and len(telemetry)==bots
    if valid_telemetry:
        for windows in telemetry.values():
            if not isinstance(windows,list) or not windows:valid_telemetry=False;break
            total=0
            for window in windows:
                seconds=window.get('playing_s');reports=window.get('reports',[])
                if not _number(seconds) or seconds<0 or not reports:valid_telemetry=False;break
                total+=seconds
                if not all(r.get('verdict')=='ACTIVE_OK' and r.get('exit_code')==0 and _number(r.get('tick_hz_median')) and 18<=r['tick_hz_median']<=22 for r in reports):valid_telemetry=False
            if total<required_s:valid_telemetry=False
    require(valid_telemetry,'INSUFFICIENT_NATIVE_TELEMETRY')
    previous=None;start=None;generation=None;longest=0
    for row in samples:
        now=row.get('elapsed_s')
        if not _number(now) or now<0 or not _number(result.get('elapsed_s')) or now>result['elapsed_s'] or (previous is not None and now<=previous):
            errors.append('NONMONOTONIC_OR_INVALID_SAMPLES');break
        processes=row.get('processes',{})
        valid=(row.get('active')==bots and row.get('population')==bots+1 and len(processes)==bots+2 and
               set(processes)==roles and all(isinstance(v,dict) and type(v.get('start_ticks')) is int and v['start_ticks']>0 and _number(v.get('pss_mib')) and v['pss_mib']>0 for v in processes.values()))
        current=tuple(sorted((k,v.get('start_ticks')) for k,v in processes.items() if isinstance(v,dict)))
        decisions=row.get('decisions',[])
        valid=valid and len(decisions)==bots and {d.get('id') for d in decisions}==bot_roles and all(d.get('action')=='healthy' for d in decisions)
        if not valid:
            start=None;generation=None
        elif start is None or generation!=current or (previous is not None and now-previous>5):
            start=now;generation=current
        else:
            longest=max(longest,now-start)
        previous=now
    require(longest>=required_s,'FULL_POPULATION_CONTINUOUS_DURATION_NOT_MET')
    return dict(status='REJECTED' if errors else 'DURATION_RECEIPTS_ACCEPTED',
                bots=bots,required_s=required_s,continuous_full_population_s=round(longest,3),
                dll_sha256=dll_sha256,reasons=sorted(set(errors)),m1_complete=False,
                scope='SOURCE_PINNED_NATIVE_RECEIPT_VALIDATION_REQUIRED_NOT_RELEASE_AUTHORIZATION')


def evaluate_runtime(root, *, bots, required_s, dll_sha256, harness_sha256):
    root=Path(root)
    if root.parent!=Path('/srv') or not root.name.startswith('tse-session-qualification-master-m1-'):
        raise ValueError('M1_PRIVATE_NATIVE_ROOT_REQUIRED')
    inventory=read_receipt(root/'source-sha256.json')
    if not harness_sha256 or inventory!=harness_sha256:raise ValueError('NATIVE_PRODUCER_SOURCE_DRIFT')
    result=read_receipt(root/'result.json')
    guard=read_receipt(root/'host-guard.json')
    result['runtime_root']=str(root)
    cgroup=Path(result.get('cgroup','/'))
    if cgroup.parent!=Path('/sys/fs/cgroup') or not re.fullmatch(r'tse-sessions-[0-9]+',cgroup.name):
        raise ValueError('NATIVE_CGROUP_UNBOUND')
    expected_roles={'server','vanilla'}|set(result.get('telemetry',{}))
    expected_mounts={str(root/(prefix+role)) for role in expected_roles for prefix in ('','prefix-')}
    mounted={line.split()[4] for line in Path('/proc/self/mountinfo').read_text().splitlines()}
    empty=cgroup.exists() and not (cgroup/'cgroup.procs').read_text().strip()
    # Read-only independent final census; never infer cleanup from a count.
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            cwd=Path(os.readlink(proc/'cwd'))
            state=(proc/'stat').read_text().rsplit(') ',1)[1].split()[0]
            if state!='Z' and cwd.is_relative_to(root):empty=False
        except (OSError,ValueError):pass
    result['cleanup_observed_complete']=empty and not (mounted&expected_mounts)

    samples=[json.loads(s) for s in (root/'samples.jsonl').read_text().splitlines()]
    expected=['server','vanilla']+sorted(result.get('telemetry',{}))
    paths=[root/'layers'/role/'upper'/('Dedicated_BotTest.log' if role=='server' else 'SeriousSam.log') for role in expected]
    # No missing log may be interpreted as zero SYNCBAD.
    result['sync_scan_complete']=len(expected)==bots+2 and all(p.is_file() and p.stat().st_size>0 for p in paths)
    result['sync_bad']=sum(len(re.findall(r'SYNCBAD|Too many bad syncs|CRC check failed',p.read_text(errors='replace'))) for p in paths if p.is_file())
    return evaluate_stage(result,guard,samples,bots=bots,required_s=required_s,dll_sha256=dll_sha256)
