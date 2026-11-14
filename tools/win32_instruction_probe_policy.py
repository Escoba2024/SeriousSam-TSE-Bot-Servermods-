"""Verdict for own IA32 method evidence; never qualifies Retail or gameplay."""
import re

MODES=('baseline','historical-object','function-probe')
CLEANUP=('native_frames_returned','script_idle','hooks_detached',
         'original_bytes_verified','script_unloaded','session_detached',
         'process_ended','worker_reaped')


def verdict(mode,report):
    if mode not in MODES:raise ValueError('one fixed method mode required')
    out=dict(status='FAIL_METHOD_EVIDENCE',abi_preserved=False,retail_qualified=False)
    native=report.get('native')or{};cleanup=report.get('cleanup')or{}
    if (native.get('phase')!='WAIT_CLEANUP' or report.get('process_returncode')!=0
        or any(cleanup.get(k)is not True for k in CLEANUP)or cleanup.get('errors')!=[]
        or report.get('callback_records')!=(0 if mode=='baseline'else 2)
        or report.get('callback_faults')!=0 or report.get('callback_dropped')!=0):return out
    if not all(isinstance(native.get(k),str)and re.fullmatch('[0-9a-f]{8}',native[k])
               for k in ('saved_edi','argument_result')):return out
    rows=report.get('callback_rows')
    if mode=='baseline':
        if rows!=[]:return out
    else:
        if (not isinstance(rows,list)or len(rows)!=2
            or any(not isinstance(r,dict)for r in rows)
            or [r.get('site')for r in rows]!=['saved','arguments']
            or any(type(r.get('thread'))is not int or r['thread']<=0 for r in rows)
            or rows[0]['thread']!=rows[1]['thread']
            or any(type(r.get('stack_top'))is not int or not 0<=r['stack_top']<=0xffffffff for r in rows)
            or any(not isinstance(r.get('raw_edi'),str)or not re.fullmatch('0x[0-9a-f]{1,8}',r['raw_edi'])for r in rows)
            or rows[0]['raw_edi']!='0x12345678'):return out
        # Frida17.26.2 writes its return-trap slot AFTER invoking onEnter.
        # Both modes must therefore observe the original entry stack values.
        if [r['stack_top']for r in rows]!=[0x12345678,0x11223344]:return out
    same=native['saved_edi']=='12345678'and native['argument_result']=='10203040'
    if mode=='historical-object':
        out['status']='CONTROL_NOT_REPRODUCED'if same else'EXPECTED_CONTROL_VIOLATION_OBSERVED'
    else:
        out.update(status='PASS_METHOD_ONLY'if same else'FAIL_NATIVE_PRESERVATION',abi_preserved=same)
    return out
