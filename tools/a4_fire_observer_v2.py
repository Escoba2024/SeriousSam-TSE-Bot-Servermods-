"""Pure prospective A4 fire evidence policy. No processes, input or runtime I/O."""
import copy

import audit_a4_native_fire_observer_v2 as audit


ORIGINAL_HASHES = dict(
    **{'Engine.dll': 'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f',
       'EntitiesMP.dll': '7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350',
       'GameMP.dll': '1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'})


def require(value, message):
    if not value:
        raise ValueError('A4 native fire V2: '+message)


def epoch(phase, server_identity, log_offsets):
    require(type(phase) is int and phase in (0, 1, 2), 'phase')
    require(len(server_identity) == 2 and all(type(n) is int and n > 0 for n in server_identity),
            'server PID/start identity')
    require(all(type(log_offsets.get(r)) is int and log_offsets[r] >= 0
                for r in ('server', 'botA', 'botB')), 'log epoch offsets')
    return dict(phase=phase, server_identity=list(server_identity),
                log_offsets={r:log_offsets[r] for r in ('server', 'botA', 'botB')})


def check_sample(sample, server_identity):
    require(sample.get('process_identity') == list(server_identity), 'sample server identity')
    require(sample.get('hashes') == ORIGINAL_HASHES, 'sample Original module hashes')
    require(sample.get('consistency') == 'two_equal_reads_not_atomic', 'sample consistency')


def bind_sample(sample, phase, server_identity, log_offsets):
    check_sample(sample, server_identity)
    require('observer_epoch' not in sample, 'sample already bound')
    return dict(sample, observer_epoch=epoch(phase, server_identity, log_offsets))


def evidence(logs, mapping, samples, registry, server_identity):
    require(registry.get('actual_slot_mapping') == mapping, 'registry slot mapping')
    binding = registry.get('native_fire_epoch')
    require(isinstance(binding, dict), 'registry observer epoch')
    require(binding == epoch(registry['phase'], server_identity, binding['log_offsets']),
            'registry phase/server identity')
    slots = mapping['botA'] + mapping['botB'] + mapping['vanilla']
    require(len(slots) == 9 and set(slots) == set(range(9)), 'exclusive nine-slot mapping')
    require(len(registry['players']) == 9
            and {r['slot'] for r in registry['players']} == set(range(9)), 'registry roster')
    expected = {r['slot']:r for r in registry['players']}
    for sample in samples:
        check_sample(sample, server_identity)
        require(sample.get('observer_epoch') == binding, 'sample from another phase epoch')
    result = {}
    numbered = list(enumerate(samples, 1))
    for role in ('botA', 'botB'):
        require(logs[role].count('[CecilLoad]') == 1, 'ambiguous source map epoch')
        rows = audit.source_rows(logs[role])
        for local, slot in enumerate(mapping[role]):
            result[f'{role}:{local}'] = audit.slot_evidence(
                rows, numbered, local, slot, expected[slot])
    return copy.deepcopy(result)


def apply(result, logs, mapping, samples, registry, server_identity):
    """Replace only sparse fire gate; preserve every other existing gate/field."""
    proof = evidence(logs, mapping, samples, registry, server_identity)
    missing = [m for m in result['missing_activity'] if not m.endswith(':fire_action_rows')]
    for key, detail in proof.items():
        values = result['slots'][key]
        values['native_fire_v2'] = detail
        if not detail['native_fire_with_same_life_source_growth']:
            missing.append(key+':native_bound_fire_actions')
        if not detail['actual_useful_inventory_gains']:
            missing.append(key+':native_bound_useful_pickup_gains')
    result['missing_activity'] = missing
    result['fire_observer_version'] = 2
    result['native_fire_epoch'] = copy.deepcopy(registry['native_fire_epoch'])
    return result
