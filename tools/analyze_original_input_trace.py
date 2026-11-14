"""Offline accounting for the proposed A1 trace. No process access or native pass.

The caller must retain the full ordered raw trace separately. This compact input
is a reviewed projection of a completed window, not proof that a collector ran.
Exact comparisons classify the synthetic examples; no gameplay gate uses them.
"""
import math


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('numeric observation required')
    if not math.isfinite(value):
        raise ValueError('nonfinite observation')
    return value


def analyze(trace):
    try:
        if (trace['complete'] is not True or trace['dropped'] != 0
                or trace['pins_verified'] is not True):
            raise ValueError('incomplete or unverified trace')
        request = trace['request']
        if request['axis'] != 'x' or request['confirmed'] is not True:
            raise ValueError('one confirmed horizontal request required')
        pixels = number(request['pixels'])
        gain = number(trace['calibrated_gain'])
        if pixels == 0 or gain >= 0:
            raise ValueError('nonzero request and signed yaw gain required')
        inputs = trace['inputs']; actions = trace['actions']
        if not 0 < len(inputs) <= 512 or not 0 < len(actions) <= 512:
            raise ValueError('empty or unbounded window')
        by_id = {}; counts = {}; active_counts = {}
        for row in inputs:
            key = row['id']
            if type(key) is not int or key < 0 or key in by_id:
                raise ValueError('invalid or duplicate input ID')
            if (row['cursor_ok'] is not True or row['recenter_ok'] is not True
                    or type(row['prescan']) is not bool
                    or type(row['thread']) is not int):
                raise ValueError('invalid input observation')
            number(row['raw_dx']); number(row['engine_x'])
            by_id[key] = row; counts[key] = 0; active_counts[key] = 0
        delta = 0
        for action in actions:
            row = by_id.get(action['input_id'])
            if (row is None or action['thread'] != row['thread']
                    or type(action['prescan']) is not bool
                    or action['prescan'] != row['prescan']):
                raise ValueError('unbound or incompatible action')
            counts[row['id']] += 1
            change = (number(action['local_yaw_after'])
                      - number(action['local_yaw_before']))
            delta += change
            if change != 0:
                active_counts[row['id']] += 1
        if any(counts[key] == 0 and (row['raw_dx'] != 0 or row['engine_x'] != 0)
               for key, row in by_id.items()):
            raise ValueError('unconsumed nonzero input: window cannot attribute full delta')
        if delta != number(trace['settled_local_delta']):
            raise ValueError('action accounting does not match settled delta')
        raw = sum(row['raw_dx'] for row in inputs)
        engine = sum(row['engine_x'] for row in inputs)
        reused = sorted(key for key, count in active_counts.items()
                        if count > 1 and by_id[key]['engine_x'] != 0)
        # The sign inversion is original CreateAction yaw (axis 4 -> fchs).
        expected = pixels * gain
        raw_matches = delta == raw * gain
        engine_matches = delta == -engine
        shape = 'unresolved_combination'
        if not reused and delta == expected and raw == pixels and engine_matches:
            shape = 'ordinary'
        elif reused and raw == pixels and engine == -expected:
            shape = 'reused_input_observation'
        elif not reused and raw_matches and engine_matches and raw != pixels:
            shape = ('larger_raw_displacement' if sum(r['raw_dx'] != 0 for r in inputs) == 1
                     else 'repeated_raw_displacement')
        elif not reused and raw == pixels and delta != expected:
            if engine_matches:
                shape = 'engine_transform_difference'
            elif engine == -expected:
                shape = 'action_transform_difference'
        return {'scope': 'OFFLINE_TRACE_ACCOUNTING_ONLY',
                'native_qualified': False, 'cause_proven': False,
                'requested_pixels': pixels, 'raw_dx_total': raw,
                'engine_x_total': engine, 'local_yaw_delta_total': delta,
                'input_count': len(inputs), 'action_count': len(actions),
                'reused_input_ids': reused, 'shape': shape}
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError('malformed trace') from exc
