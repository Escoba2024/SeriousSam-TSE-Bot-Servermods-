"""Prospective fixed provenance wrapper; no process, input or runtime I/O.

All raw envelopes are checked before selecting the two predeclared groups.
The historical V2 core receives one identical subset for fire AND pickups.
"""
import copy
import hashlib
import json

import a4_fire_observer_v2 as core


def require(value, message):
    if not value:
        raise ValueError('A4 canonical native groups: '+message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def declare(mapping, server_identity, log_offsets):
    """Declare exactly once after physical mapping, before releasing gameplay."""
    require(isinstance(mapping, dict) and set(mapping) == {'botA', 'botB', 'vanilla'},
            'physical roles')
    require(all(isinstance(mapping[r], list) and len(mapping[r]) == n
                for r, n in (('botA', 4), ('botB', 4), ('vanilla', 1))), 'role sizes')
    slots = mapping['botA']+mapping['botB']+mapping['vanilla']
    require(all(type(s) is int for s in slots) and sorted(slots) == list(range(9)),
            'exclusive nine-slot mapping')
    return dict(schema='a4-fixed-native-groups-v1',
                actual_slot_mapping=copy.deepcopy(mapping),
                observer_epoch=core.epoch(0, server_identity, log_offsets),
                groups=dict(botA_actual=list(mapping['botA']),
                            botB_actual=list(mapping['botB']),
                            vanilla_plus_overlap=list(mapping['vanilla']+mapping['botA'][:3])),
                fixed_sources=dict(botA='botA_actual', botB='botB_actual'))


def checked_contract(contract):
    require(isinstance(contract, dict), 'missing contract')
    epoch = contract.get('observer_epoch') or {}
    expected = declare(contract.get('actual_slot_mapping'),
                       epoch.get('server_identity', []), epoch.get('log_offsets', {}))
    require(contract == expected, 'contract altered')
    return expected


def bind_sample(sample, group, contract):
    """Bind the actual existing read name/slot request; never infer from outcomes."""
    checked_contract(contract)
    require(group in contract['groups'], 'unknown read group')
    require('native_group_provenance' not in sample, 'sample already group-bound')
    epoch = contract['observer_epoch']
    bound = copy.deepcopy(core.bind_sample(sample, 0, epoch['server_identity'],
                                          epoch['log_offsets']))
    bound['native_group_provenance'] = dict(name=group,
        read_slots=list(contract['groups'][group]), contract_sha256=digest(contract))
    return bound


def validate_all(samples, registry, mapping, server_identity, contract):
    """Validate every envelope, including excluded overlap, before any selection."""
    checked_contract(contract)
    require(contract['actual_slot_mapping'] == mapping, 'contract physical mapping')
    epoch = contract['observer_epoch']
    require(epoch['server_identity'] == list(server_identity), 'contract process identity')
    require(registry.get('native_group_contract') == contract, 'registry group contract')
    require(registry.get('actual_slot_mapping') == mapping, 'registry physical mapping')
    require(registry.get('phase') == 0 and registry.get('native_fire_epoch') == epoch,
            'registry phase/epoch')
    roster = registry.get('players')
    require(isinstance(roster, list) and len(roster) == 9
            and sorted(p.get('slot', -1) for p in roster) == list(range(9)), 'registry roster')
    expected = {p['slot']: p for p in roster}
    identities = core.audit.IDENTITY
    require(all(all(type(p.get(k)) is int and p[k] > 0 for k in identities)
                for p in roster), 'registry identities')
    require(len({p['world_pointer'] for p in roster}) == 1
            and len({p['entity_id'] for p in roster}) == 9
            and len({p['entity_pointer'] for p in roster}) == 9, 'registry identity exclusivity')
    counts = dict.fromkeys(contract['groups'], 0)
    stamp = digest(contract)
    for sample in samples:
        core.check_sample(sample, server_identity)
        require(sample.get('observer_epoch') == epoch, 'sample phase/epoch')
        core.audit.stamp(sample.get('game_tick'))
        provenance = sample.get('native_group_provenance')
        require(isinstance(provenance, dict), 'missing sample provenance')
        name = provenance.get('name')
        require(name in counts, 'unknown sample group')
        slots = contract['groups'][name]
        require(provenance == dict(name=name, read_slots=slots, contract_sha256=stamp),
                'sample provenance differs')
        players = sample.get('players')
        require(isinstance(players, list) and [p.get('slot') for p in players] == slots,
                'actual read slots differ')
        require(sample.get('all_selected_present') is True
                and all(p.get('present') is True for p in players), 'missing read player')
        require(all(all(p.get(k) == expected[p['slot']][k] for k in identities)
                    for p in players), 'sample physical identity/world differs')
        for player in players:
            clock = player.get('spawned_tick', 0)
            if not clock <= 0:
                core.audit.stamp(clock)  # Identical V2 finite-clock rule; no new lifetime/EPS.
        counts[name] += 1
    require(all(counts.values()), 'missing expected read group')
    return counts


def apply(result, logs, mapping, samples, registry, server_identity, contract):
    counts = validate_all(samples, registry, mapping, server_identity, contract)
    canonical_names = set(contract['fixed_sources'].values())
    selected = [s for s in samples if s['native_group_provenance']['name'] in canonical_names]
    # No separate pickup stream, outcome selection, fallback, or altered V2 core.
    out = core.apply(result, logs, mapping, selected, registry, server_identity)
    out['native_group_observation'] = dict(schema='a4-fixed-native-groups-v1',
        contract_sha256=digest(contract), fixed_sources=copy.deepcopy(contract['fixed_sources']),
        raw_samples=len(samples), canonical_samples=len(selected), raw_group_samples=counts,
        canonical_group_samples={name:counts[name] for name in contract['fixed_sources'].values()},
        overlap_scope='raw and existing activity gates; excluded from V2 fire and pickup evidence')
    return out
