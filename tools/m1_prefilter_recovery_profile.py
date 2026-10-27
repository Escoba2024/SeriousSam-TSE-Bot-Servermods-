"""Exact optimized-producer matrix admission; no runtime operations."""
import math

ROOTS={1:('/srv/tse-session-qualification-master-m1-prefilter-one-hour-idle-r3-20261026',3600),
       4:('/srv/tse-session-qualification-master-m1-prefilter-four-hour-idle-r3-20261026',3600),
       8:('/srv/tse-session-qualification-master-m1-prefilter-eight-two-hours-idle-r3-20261026',7200)}


def validated_stages(matrix,candidate):
    if (not isinstance(matrix,dict) or matrix.get('status')!='DURATION_MATRIX_ACCEPTED_PRIVATE_ONLY' or
        matrix.get('m1_complete') is not False or not isinstance(matrix.get('stages'),list) or
        len(matrix['stages'])!=3):raise ValueError('complete private prefilter matrix required')
    found={}
    for row in matrix['stages']:
        if not isinstance(row,dict) or not isinstance(row.get('verdict'),dict):raise ValueError('stage object required')
        v=row['verdict'];b=v.get('bots');seconds=v.get('continuous_full_population_s')
        if type(b) is not int or b not in ROOTS or b in found:raise ValueError('exact unique stages required')
        root,required=ROOTS[b]
        if (row.get('root')!=root or v.get('status')!='DURATION_RECEIPTS_ACCEPTED' or
            type(v.get('required_s')) is not int or v['required_s']!=required or
            type(seconds) not in (float,int) or not math.isfinite(seconds) or seconds<required or
            v.get('dll_sha256')!=candidate or v.get('reasons')!=[] or v.get('m1_complete') is not False):
            raise ValueError('accepted exact candidate/root/duration required')
        found[b]=(root,b,required)
    return [found[b] for b in (1,4,8)]


def bind_and_track(process,owned_factory,active,root,roles):
    """Record every direct child before binding; binding failure permits no signal."""
    active[0]=(process,None,root,roles)
    owned=owned_factory(process)
    active[0]=(process,owned,root,roles)
    return owned


def interrupt_handler(cleaning):
    def interrupted(signum,frame):
        if not cleaning[0]:raise RuntimeError('owned recovery interrupt '+str(signum))
    return interrupted


def require_fresh_recovery(base):
    for name in ('recovery-qualification.json','recovery-HOLD.json'):
        if (base/name).exists():raise RuntimeError('fresh owned recovery required; previous evidence preserved')
