"""Read archived A4 evidence only. Never requalifies a run or accesses a process.

The proposed V2 fire predicate is stricter than a sampled AI fire intention.
This file reports native-action/life/counter evidence for independent review;
it is deliberately not imported by any native controller.
"""
import argparse
import collections
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re


USEFUL = 0x3df8
IDENTITY = ('entity_id', 'entity_pointer', 'world_pointer')


def stamp(value):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError('invalid observed clock')
    return Decimal.from_float(float(value))


def good_player(row, expected, tick):
    clock = row.get('spawned_tick', 0)
    return (row.get('present') is True and row.get('render_type') == 3
            and row.get('health', 0) > 0 and clock > 0 and tick >= clock
            and all(row.get(k) == expected[k] for k in IDENTITY))


def native_fire(row):
    w = row.get('weapons') or {}
    current = w.get('current', 0)
    if type(current) is not int or not 1 <= current <= 14:
        return False
    bit = 1 << (current - 1)
    return bool(bit & USEFUL and w.get('owned', 0) & bit
                and w.get('has_ammo') == 1 and w.get('fire_requested') == 1
                and row.get('last_buttons', 0) & 1)


def source_rows(text):
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        tag = line.split(']', 1)[0][1:]
        if not line.startswith('[') or tag not in (
                'CecilState', 'CecilSpawn', 'CecilWeaponObserve'):
            continue
        values = dict(re.findall(r'(\w+)=([^\s]+)', line))
        values.update(tag=tag, line=number)
        rows.append(values)
    return rows


def slot_evidence(rows, snapshots, local, slot, expected):
    rows = [r for r in rows if int(r['local']) == local
            and int(r.get('entity', 0)) == expected['entity_id']]
    native_times = {}
    for r in rows:
        if r['tag'] != 'CecilWeaponObserve':
            continue
        tick = int(r['tick'])
        value = Decimal(r['native_time'])
        if tick in native_times and native_times[tick] != value:
            raise ValueError('conflicting source time at same actual source tick')
        native_times[tick] = value
    lives = collections.defaultdict(dict)
    for line, snapshot in snapshots:
        tick = snapshot['game_tick']
        stamp(tick)
        for row in snapshot['players']:
            if row['slot'] != slot or any(row.get(k) != expected[k] for k in IDENTITY):
                continue
            clock = row.get('spawned_tick', 0)
            if clock <= 0:
                continue
            stamp(clock)
            previous = lives[clock].get(tick)
            if previous is not None and previous[1] != row:
                raise ValueError('conflicting duplicate inventory sample')
            lives[clock][tick] = (line, row)
    joins, invalid_joins, rejected_times = {}, set(), 0
    for r in rows:
        if r['tag'] != 'CecilWeaponObserve':
            continue
        native = native_times[int(r['tick'])]
        # %f has six printed fractional digits: its WHOLE possible rounding
        # interval must be inside the unmodified exact server-float interval.
        # Boundary witnesses are discarded, never granted a larger lifetime.
        low, high = native - Decimal('.0000005'), native + Decimal('.0000005')
        matches = []
        for clock, observations in lives.items():
            alive = [tick for tick, (_, row) in observations.items()
                     if good_player(row, expected, tick)]
            if alive and stamp(clock) <= low and high <= stamp(max(alive)):
                matches.append(clock)
        generation = int(r['generation'])
        if len(matches) == 1:
            if generation in joins and joins[generation] != matches[0]:
                invalid_joins.add(generation)
            joins[generation] = matches[0]
        else:
            rejected_times += 1
            if len(matches) > 1:
                invalid_joins.add(generation)
    inverse = collections.Counter(joins.values())
    joins = {g: clock for g, clock in joins.items()
             if inverse[clock] == 1 and g not in invalid_joins}
    growth, previous, invalid = {}, {}, set()
    for r in rows:
        if r['tag'] != 'CecilState':
            continue
        generation = int(r['generation'])
        count = int(r['shots'])
        if generation in previous:
            old = previous[generation]
            if int(r['tick']) <= int(old['tick']) or count < int(old['shots']):
                invalid.add(generation)
            if (r.get('alive') == old.get('alive') == '1'
                    and count > int(old['shots'])):
                growth[generation] = (old, r)
        previous[generation] = r
    growth = {g: pair for g, pair in growth.items() if g not in invalid}
    fire, pickup, first = 0, 0, None
    for clock, observations in lives.items():
        generations = [g for g, sc in joins.items() if sc == clock and g in growth]
        previous = None
        for tick, (line, row) in sorted(observations.items()):
            good = good_player(row, expected, tick)
            if good and native_fire(row) and len(generations) == 1:
                fire += 1
                if first is None:
                    g = generations[0]
                    before, after = growth[g]
                    first = dict(inventory_line=line, game_tick=tick,
                                 source_generation=g,
                                 source_counter_lines=[before['line'], after['line']],
                                 source_counter_ticks=[int(before['tick']), int(after['tick'])],
                                 source_counter_values=[int(before['shots']), int(after['shots'])])
            w = row.get('weapons') or {}
            if good and previous is not None:
                old_tick, old = previous
                old_w = old.get('weapons') or {}
                if (old_tick < tick and good_player(old, expected, old_tick)
                        and isinstance(old.get('weapons'), dict)
                        and type(old_w.get('owned')) is int
                        and isinstance(row.get('weapons'), dict)
                        and type(w.get('owned')) is int
                        and w.get('owned', 0) & ~old_w.get('owned', 0) & USEFUL):
                    pickup += 1
            previous = (tick, row)
    return dict(native_fire_with_same_life_source_growth=fire,
                actual_useful_inventory_gains=pickup,
                source_generations_bound=len(joins),
                source_spawn_rows=sum(r['tag'] == 'CecilSpawn' for r in rows),
                rejected_source_time_witnesses=rejected_times,
                contradictory_source_life_generations=sorted(invalid_joins),
                invalid_source_counter_generations=sorted(invalid),
                first_fire_reference=first)


def audit(root):
    root = Path(root)
    pins = {}

    def read(name):
        data = (root / name).read_bytes()
        pins[name] = hashlib.sha256(data).hexdigest()
        return data

    result = json.loads(read('result.json'))
    snapshots = collections.defaultdict(list)
    for line, raw in enumerate(read('inventory.jsonl').splitlines(), 1):
        entry = json.loads(raw)
        if type(entry.get('phase')) is int:
            snapshots[entry['phase']].append((line, entry['snapshot']))
    slots, old_missing = {}, {}
    for phase in range(3):
        prefix = f'phase-{phase}-redstation/'
        registry = json.loads(read(prefix + 'registry.json'))
        if registry['phase'] != phase:
            raise ValueError('phase registry mismatch')
        mapping = registry['actual_slot_mapping']
        claimed = mapping['botA'] + mapping['botB']
        if len(claimed) != 8 or len(set(claimed)) != 8:
            raise ValueError('ambiguous local/global slot assignment')
        expected = {row['slot']: row for row in registry['players']}
        old_missing[str(phase)] = json.loads(read(prefix + 'active-evidence.json'))['missing_activity']
        for role in ('botA', 'botB'):
            # Archived phase files have ALREADY been cut at log_byte_start_offsets.
            text = read(prefix + role + '.log').decode('latin1')
            if text.count('[CecilLoad]') != 1:
                raise ValueError('phase source map epoch ambiguous')
            rows = source_rows(text)
            for local, slot in enumerate(mapping[role]):
                slots[f'{phase}:{role}:{local}'] = slot_evidence(
                    rows, snapshots[phase], local, slot, expected[slot])
    return dict(scope='ARCHIVED_OBSERVER_V2_REVIEW_ONLY', native_qualified=False,
                original_run_status=result['status'], original_missing_activity=old_missing,
                runtime_or_criteria_changed=False, slots=slots, input_sha256=pins)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.evidence), indent=2, allow_nan=False))
