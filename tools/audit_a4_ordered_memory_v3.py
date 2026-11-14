"""Ordered memory observations, not atomic snapshots or weapon-call events.

Only the observation container differs from V2; all source/life/Decimal/counter
and strict oldTick<newTick pickup predicates remain unchanged.
"""
import collections
from decimal import Decimal
from audit_a4_native_fire_observer_v2 import (USEFUL, IDENTITY, stamp, good_player,
                                             native_fire, source_rows)


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
    lives = collections.defaultdict(list)
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
            lives[clock].append((tick, line, row))
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
            alive = [tick for tick, _, row in observations
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
        for tick, line, row in observations:
            good = good_player(row, expected, tick)
            if good and native_fire(row) and len(generations) == 1:
                fire += 1
                if first is None:
                    g = generations[0]
                    before, after = growth[g]
                    first = dict(read_serial=line, game_tick=tick,
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
    return dict(native_fire_flag_observations_with_same_life_source_growth=fire,
                actual_useful_inventory_gains=pickup,
                source_generations_bound=len(joins),
                source_spawn_rows=sum(r['tag'] == 'CecilSpawn' for r in rows),
                rejected_source_time_witnesses=rejected_times,
                contradictory_source_life_generations=sorted(invalid_joins),
                invalid_source_counter_generations=sorted(invalid),
                first_flag_observation_reference=first,
                atomic_snapshot=False, weapon_function_call_proven=False)
