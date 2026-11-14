"""Read CLOSED files for OFFLINE_DESIGN_CHECK only; never requalify a run.

Historical group labels are retrospective provenance in this check, not proof
that a prospective contract existed during that run. Sources remain read-only.
"""
import argparse
import hashlib
import json
from pathlib import Path

import a4_canonical_native_groups as groups
import a4_fire_observer_v2 as core


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check(root):
    root = Path(root)
    names = ('inventory.jsonl', 'registry.json', 'result.json', 'botA-closed.log', 'botB-closed.log',
             'a4_fire_observer_v2.py', 'audit_a4_native_fire_observer_v2.py')
    before = {name:sha(root/name) for name in names}
    tools = Path(__file__).resolve().parent
    for name in ('a4_fire_observer_v2.py', 'audit_a4_native_fire_observer_v2.py'):
        if before[name] != sha(tools/name):
            raise ValueError('historical V2 bytes differ')
    registry = json.loads((root/'registry.json').read_text())
    mapping = registry['actual_slot_mapping']
    epoch = registry['native_fire_epoch']
    identity = epoch['server_identity']
    contract = groups.declare(mapping, identity, epoch['log_offsets'])
    if epoch != contract['observer_epoch']:
        raise ValueError('historical epoch differs')
    registry['native_group_contract'] = contract
    samples = []
    paused = 0
    with (root/'inventory.jsonl').open() as stream:
        for text in stream:
            envelope = json.loads(text)
            if 'elapsed' not in envelope:
                if envelope.get('phase') != 'paused_smoke':
                    raise ValueError('unknown raw phase')
                paused += 1
                continue
            sample = envelope['snapshot']
            if sample.get('observer_epoch') != epoch:
                raise ValueError('historical sample epoch differs')
            del sample['observer_epoch']  # Parsed copy only; no archived writes.
            samples.append(groups.bind_sample(sample, envelope['group'], contract))
    result = dict(missing_activity=[], slots={f'{r}:{i}':dict(fire_action_rows=0)
                 for r in ('botA','botB') for i in range(4)}, qualified=False, functional_pass=False)
    logs = {r:(root/(r+'-closed.log')).read_text(errors='replace') for r in ('botA','botB')}
    observed = groups.apply(result, logs, mapping, samples, registry, identity, contract)
    after = {name:sha(root/name) for name in names}
    if after != before:
        raise ValueError('closed source files changed during check')
    return dict(scope='OFFLINE_DESIGN_CHECK_NOT_NATIVE_QUALIFICATION', historical_status='FAIL',
        qualified=False, functional_pass=False, source_hashes=before, sources_unchanged=after == before,
        paused_smoke_samples_excluded_from_gameplay_evidence=paused,
        retrospective_group_labels=True, prospective_contract_existed_during_historical_run=False,
        observation=observed['native_group_observation'],
        missing_native_evidence=observed['missing_activity'],
        slots={key:dict(native_fire_with_same_life_source_growth=value['native_fire_v2']['native_fire_with_same_life_source_growth'],
                        actual_useful_inventory_gains=value['native_fire_v2']['actual_useful_inventory_gains'])
               for key,value in observed['slots'].items()})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--closed-window', type=Path, required=True)
    parser.add_argument('--new-output', type=Path, required=True)
    args = parser.parse_args()
    result = check(args.closed_window)
    with args.new_output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
