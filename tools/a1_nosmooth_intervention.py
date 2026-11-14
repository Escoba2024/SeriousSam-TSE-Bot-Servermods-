"""Sealed isolated-profile intervention and one passive pre-calibration gate.

No process or input implementation. The caller owns the exclusive arena lock,
the already sealed FileTransaction and all normal startup/cleanup operations.
"""
import hashlib
import json
import stat
import time

import a1_controls_diagnostic as controls

RELATIVE = 'vanilla/Controls/Controls0.ctl'
BASELINE_SHA = '5d525c46993be88d45941fe14f4638fa001ba9583d1151a27d6df9129d9b9d9b'
PREPARED_SHA = '76a947f52a88271133e1f9699da38858c14f293f8fe04700594fa3b85788b6d9'


def require(ok, why):
    if not ok:
        raise ValueError('Original nosmooth controls: '+why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def install(transaction, evidence):
    require(transaction.sealed, 'transaction must already be sealed')
    record = transaction.records.get(RELATIVE)
    require(record is not None and record.get('existed') is True
            and record.get('sha256') == BASELINE_SHA, 'exact original Controls0 absent from transaction')
    transaction.quiescent()
    path = transaction.path(RELATIVE)
    before = path.read_bytes()
    st = path.stat()
    metadata = (stat.S_IMODE(st.st_mode), st.st_uid, st.st_gid)
    require(digest(before) == BASELINE_SHA, 'profile changed since sealed backup')
    require(metadata == (record['mode'], record['uid'], record['gid']), 'profile metadata changed')
    after = controls.disable_global_smoothing(before)
    require(digest(after) == PREPARED_SHA, 'prepared profile pin differs')
    (evidence/'controls-profile-before.ctl').write_bytes(before)
    (evidence/'controls-profile-prepared.ctl').write_bytes(after)
    path.write_bytes(after)
    st = path.stat()
    require(path.read_bytes() == after
            and (stat.S_IMODE(st.st_mode), st.st_uid, st.st_gid) == metadata,
            'installed profile bytes/metadata differ')
    transaction.quiescent()
    return dict(relative_path=RELATIVE, baseline_sha256=BASELINE_SHA,
                prepared_sha256=PREPARED_SHA, effective_runtime_observed=False,
                only_global_controls_smoothing_changed=True)


def require_effective(observation):
    require(isinstance(observation, dict), 'effective observation absent')
    for field in ('local_slot', 'profile', 'global_smooth'):
        require(type(observation.get(field)) is int and observation[field] == 0,
                'effective '+field+' differs from required zero')
    axes = observation.get('axes')
    require(isinstance(axes, dict) and set(axes) == {'x', 'y'}, 'effective mouse axes absent')
    for axis in ('x','y'):
        for flag in ('smooth','effective_smooth'):
            require(type(axes[axis].get(flag)) is int and axes[axis][flag] == 0,
                    'effective '+axis+' '+flag+' differs from required zero')


def run_after_verified_controls(reader, report, journal, save, calibrate, *,
                                sample=controls.sample, clock=time.monotonic):
    require(report.get('status') != 'FAIL', 'failed run cannot be retried')
    record = dict(status='IN_PROGRESS', monotonic_started=clock(),
                  native_abi_qualified=False, input_cause_proven=False)
    report.setdefault('controls_input_profile', {})['effective'] = record
    created = False
    def persist():
        nonlocal created
        if created:
            journal.write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
        else:
            with journal.open('x') as stream:
                json.dump(record, stream, indent=2, allow_nan=False)
                stream.write('\n')
            created = True
    try:
        record['sample'] = sample(reader, local_slot=0)
        require_effective(record['sample'])
        record.update(status='OBSERVED', monotonic_finished=clock())
        persist()
        save()
    except BaseException as error:
        record.update(status='FAIL', error=repr(error), monotonic_finished=clock())
        if hasattr(error, 'raw_reads'):
            record['raw_reads'] = error.raw_reads
        report['status'] = 'FAIL'
        for label, fn in [('controls-journal', persist), ('result-journal', save)]:
            try:
                fn()
            except BaseException as write_error:
                report.setdefault('errors', []).append(label+':'+repr(write_error))
        raise
    return calibrate()
