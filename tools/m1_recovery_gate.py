#!/usr/bin/env python3
"""Admission for ONE injected-fault recovery in an owned private M1 test.

This is a native qualification gate, never a public production supervisor.
An unexplained failure, sync warning, human/ownership doubt or pressure HOLDs.
"""
import math
from pathlib import Path
import re


def finite(value):
    return type(value) in (int,float) and math.isfinite(value)


def decide_recovery(sample):
    errors=[]
    def require(condition, reason):
        if not condition: errors.append(reason)
    root=Path(sample.get('runtime','/'))
    require(root.parent==Path('/srv') and bool(re.fullmatch(r'tse-session-qualification-master-m1-server-fault-a-[A-Za-z0-9_-]+',root.name)), 'PRIVATE_OWNED_FAULT_ROOT_REQUIRED')
    require(sample.get('scope')=='ISOLATED_NETNS_RETAIL_WINE','PRIVATE_NAMESPACE_REQUIRED')
    actual=sample.get('candidate_sha256');expected=sample.get('expected_candidate_sha256')
    require(isinstance(expected,str) and bool(re.fullmatch(r'[0-9a-f]{64}',expected)) and actual==expected,'EXACT_CANDIDATE_REQUIRED')
    for flag in ('duration_matrix_accepted','originals_intact','source_intact','config_intact','public_disabled','known_players_only','owned_fault','server_identity_verified','server_absent','cleanup_complete','sync_scan_complete','guard_finished'):
        require(sample.get(flag) is True,'REQUIRED_'+flag.upper())
    require(type(sample.get('sync_bad')) is int and sample['sync_bad']==0,'SYNC_HISTORY_NOT_CLEAN')
    require(sample.get('guard_error') is None and type(sample.get('child_exitcode')) is int and sample['child_exitcode']==1,'UNEXPECTED_GUARD_OR_EXIT')
    require(sample.get('failure')=='query uncertain for more than 15 seconds','UNEXPECTED_NATIVE_FAILURE')
    require(finite(sample.get('available_mib')) and sample['available_mib']>=1068,'RAM_ADMISSION')
    require(finite(sample.get('disk_free_gib')) and sample['disk_free_gib']>=8,'DISK_ADMISSION')
    require(finite(sample.get('host_busy_percent')) and 0<=sample['host_busy_percent']<85,'CPU_ADMISSION')
    require(sample.get('attempts')==[],'ONE_RECOVERY_BUDGET_ONLY')
    fault,finished,now=(sample.get(k) for k in ('fault_at','finished_at','now'))
    require(all(finite(t) for t in (fault,finished,now)) and 0<finished-fault<=600 and 30<=now-finished<=300,'BOUNDED_FAULT_AND_COOLDOWN_REQUIRED')
    return dict(action='HOLD' if errors else 'RESTART_ONE_PRIVATE_GENERATION',reasons=errors,
                m1_complete=False,public_deployment_authorized=False)
