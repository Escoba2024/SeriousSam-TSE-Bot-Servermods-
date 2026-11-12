"""Read/copy retained role logs only after caller-attested normal closure.

No process inspection, launch, signalling or runtime mutation. This is a log
completion gate, not a gameplay/stability/release qualification.
"""
import hashlib
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Mapping, Sequence
@dataclass(frozen=True)
class ClosedLogEvidence:
    accepted: bool
    reasons: tuple[str, ...]
    logs: dict

def scan_log_errors(data: bytes, *, after: int = 0) -> dict:
    """Return existing error classes, optionally only matches ending after a byte boundary.

    Scan the complete bytes so a marker or disconnect message split across the
    boundary cannot disappear. Multiple matches on one partial line are checked;
    event summaries retain line numbers, never player names or raw log text.
    """
    if not isinstance(data, bytes) or type(after) is not int or not 0 <= after <= len(data):
        raise ValueError('log bytes/boundary')
    patterns={
        'bad_sync':re.compile(rb'\bSYNCBAD\b',re.I),
        'sync_disconnect':re.compile(rb'Too many bad syncs|Disconnected:.*(?:sync|CRC)|ordered to disconnect.*sync',re.I),
        'crc_failure':re.compile(rb'CRC check failed',re.I),
        'crash':re.compile(rb'Access violation|Fatal Error|Unhandled (?:exception|page fault)|Segmentation fault|SIGSEGV|assertion failed|stack overflow',re.I),
        'invalid_action':re.compile(rb'\[CecilInvalidAction\]',re.I),
        'join_failure':re.compile(rb'Cannot join game:',re.I),
    }
    events={kind:[] for kind in patterns}
    offset=0
    for number,line in enumerate(data.splitlines(keepends=True),1):
        for kind,pattern in patterns.items():
            if any(offset+match.end()>after for match in pattern.finditer(line)):
                events[kind].append(number)
        offset+=len(line)
    return events

def archive_closed_role_logs(*,role_roots:Mapping,source_logs:Mapping,archive_logs:Mapping,cleanup:Mapping,expected_roles:Sequence[str],max_log_bytes:int=64*1024*1024)->ClosedLogEvidence:
    """Archive once, then inspect exactly those bytes; never read a live role log.

    ``cleanup[role]['closed'] is True`` is a caller attestation that its verified
    normal-close operation AND own-helper exit checks completed. This function
    cannot establish process ownership or closure. Roots must be role-named
    directories; each source must resolve directly inside its corresponding
    root. Outputs must be fresh, distinct files and may not alias any source.
    Missing roles, wrong paths, empty/changing logs or any IO failure reject the
    evidence. Other closed roles are still retained when one role fails.
    """
    reasons=[];logs={}
    if (not isinstance(expected_roles,(list,tuple)) or not expected_roles or
        any(not isinstance(r,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',r) for r in expected_roles) or
        len(set(expected_roles))!=len(expected_roles)):
        return ClosedLogEvidence(False,('expected_roles_invalid',),{})
    roles=set(expected_roles)
    for name,values in [('role_roots',role_roots),('source_logs',source_logs),('archive_logs',archive_logs),('cleanup',cleanup)]:
        if not isinstance(values,Mapping) or set(values)!=roles:reasons.append('roles_mismatch:'+name)
    if type(max_log_bytes) is not int or max_log_bytes<1:reasons.append('max_log_bytes_invalid')
    if reasons:return ClosedLogEvidence(False,tuple(reasons),{})
    try:
        sources={r:Path(source_logs[r]) for r in expected_roles}
        roots={r:Path(role_roots[r]) for r in expected_roles}
        archives={r:Path(archive_logs[r]) for r in expected_roles}
        source_targets={p.resolve(strict=False) for p in sources.values()}
        archive_targets=[p.resolve(strict=False) for p in archives.values()]
        if len(set(archive_targets))!=len(archive_targets) or source_targets.intersection(archive_targets):
            return ClosedLogEvidence(False,('archive_path_alias',),{})
    except (OSError,ValueError,TypeError,RuntimeError) as error:
        return ClosedLogEvidence(False,('invalid_paths:'+type(error).__name__,),{})
    def signature(s):return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    seen_sources=set()
    for role in expected_roles:
        closed=cleanup[role]
        if not isinstance(closed,Mapping) or closed.get('closed') is not True:
            reasons.append('not_normally_closed:'+role);continue
        source,root,dest=sources[role],roots[role],archives[role]
        try:
            resolved_root=root.resolve(strict=True);resolved_source=source.resolve(strict=True)
            if resolved_root.name!=role or not resolved_root.is_dir() or resolved_source.parent!=resolved_root:
                reasons.append('wrong_role_log:'+role);continue
            before=source.stat()
            if not stat.S_ISREG(before.st_mode):reasons.append('not_regular_log:'+role);continue
            if before.st_size>max_log_bytes:reasons.append('log_too_large:'+role);continue
            source_identity=(before.st_dev,before.st_ino)
            if source_identity in seen_sources:reasons.append('duplicate_role_log:'+role);continue
            seen_sources.add(source_identity)
            with source.open('rb') as stream:
                opened=os.fstat(stream.fileno())
                data=stream.read(max_log_bytes+1)
                finished=os.fstat(stream.fileno())
            if signature(before)!=signature(opened) or signature(opened)!=signature(finished):
                reasons.append('source_changed:'+role);continue
            after=source.stat()
            if signature(before)!=signature(after) or len(data)!=before.st_size:
                reasons.append('source_changed:'+role);continue
            if not data.strip():reasons.append('empty_log:'+role);continue
        except (OSError,ValueError,RuntimeError) as error:
            reasons.append('source_failed:'+role+':'+type(error).__name__);continue
        try:
            # Exclusive create prevents a stale previous receipt being treated
            # as this run, and prevents silent replacement of existing files.
            with dest.open('xb') as stream:
                if stream.write(data)!=len(data):raise OSError('short archive write')
            archived=dest.read_bytes()
            if archived!=data:raise OSError('archive verification mismatch')
        except (OSError,ValueError,RuntimeError) as error:
            reasons.append('archive_failed:'+role+':'+type(error).__name__);continue
        events=scan_log_errors(archived)
        logs[role]={'sha256':hashlib.sha256(archived).hexdigest(),'bytes':len(archived),'events':events,
                    'scope':'RETAINED_LOG_AFTER_CALLER_ATTESTED_NORMAL_CLOSE'}
        if any(events.values()):reasons.append('log_events:'+role)
    return ClosedLogEvidence(not reasons,tuple(reasons),logs)
