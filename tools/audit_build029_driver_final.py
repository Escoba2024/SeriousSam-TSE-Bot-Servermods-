"""Read only closed029 Skulls receipts; no native/process/network interfaces.

Requires the four retained qualified026→027→029 reader outputs. Does not
replace their complete V3/attempt/life validation. Every Final row is retained;
only whole decimal native-clock witnesses bind a row into observed life time.
"""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import argparse
import hashlib
import json
import math
import os
import re

RESULT = '9800b41c91373b8b89056ad96694f8ffcbcbc612bac189ebc0938f0670a63064'
DLL = 'a043de1e0fc647d2805c20ea01e9f52eada3fdaa0b55caad8be6df5302ded971'
SOURCE_PINS = {
    'BotDriver.cpp': '7af47d87aaaf4c51ebaca6f65d628cfec3c2544419be07e39b65e52b370eb386',
    'driver_final_decision.h': '5286aaca6d3ea407a8f2f91b50e571522368a9a8595c27798cee573df2eac9bb',
    'BotSupplyNative.h': '72cea9c22d1a781bac8e1b733f63c22368f4cee8e0f3c3677067e571af8040bd',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def interval(text):
    value = Decimal(text)
    assert value.is_finite()
    precision = len(text.split('.')[1]) if '.' in text else 0
    half = Decimal(1).scaleb(-precision) / 2
    return value - half, value + half


def vector(text, count, integers=0):
    assert text.startswith('(') and text.endswith(')'), text
    parts = text[1:-1].split(',')
    assert len(parts) == count, (count, text)
    values = [int(x) if i < integers else float(x) for i, x in enumerate(parts)]
    assert all(math.isfinite(x) for x in values)
    return values


def mode(bits):
    return {name: bool(bits & (1 << i)) for i, name in enumerate((
        'automatic', 'humanMode', 'deathmatch', 'targetVisible', 'supplyActive',
        'combatHold', 'aimReady', 'humanFire', 'bFire', 'cecilUseControl'))}


def typed(row):
    fields = {'local', 'tick', 'actor', 'gen', 'exit_actor', 'baseline_map_pin',
              'map_known', 'life_link', 'pre_supply', 'supply', 'wp', 'post_mode',
              'arb', 'weapon', 'safe', 'submitted', 'action', 'rot', 'view', 'buttons'}
    assert fields == set(row), (fields ^ set(row))
    scalar = ('local', 'tick', 'actor', 'exit_actor', 'baseline_map_pin',
              'map_known', 'life_link', 'post_mode', 'submitted', 'buttons')
    out = {name: int(row[name]) for name in scalar}
    for name, count, ints in (('gen', 2, 2), ('pre_supply', 2, 2),
                             ('supply', 13, 8), ('wp', 2, 2), ('arb', 6, 0),
                             ('weapon', 11, 11), ('safe', 13, 4),
                             ('action', 3, 0), ('rot', 3, 0), ('view', 3, 0)):
        out[name] = vector(row[name], count, ints)
    assert 0 <= out['local'] < 4 and out['tick'] % 20 == 0
    assert out['map_known'] == 0 and out['submitted'] == 1
    assert out['life_link'] == int(out['actor'] != 0 and out['actor'] == out['exit_actor']
                                   and out['gen'][0] == out['gen'][1])
    for group, indices in (('supply', range(4)), ('wp', range(2)),
                           ('weapon', (0, 1, 5)), ('safe', range(3))):
        assert all(out[group][i] in (0, 1) for i in indices)
    out['pre_mode'] = mode(out['pre_supply'][0])
    out['post_mode_decoded'] = mode(out['post_mode'])
    names = ('active', 'ownsMovement', 'itemGoal', 'urgent', 'followGoal',
             'useControl', 'flightGoal', 'activeFlight')
    out['proposal_bits'] = {name: bool(out['supply'][4] & (1 << i))
                            for i, name in enumerate(names)}
    return out


def analyze(case, output, root):
    assert sha(case / 'result.json') == RESULT
    report = json.loads((case / 'result.json').read_text())
    complete = json.loads((output / 'complete-receipt.json').read_text())
    decisions = json.loads((output / 'decision-receipt.json').read_text())
    summary = json.loads((output / 'life-summary.json').read_text())
    for name, digest in summary['input_sha256'].items():
        assert sha(case / name) == digest
    assert report['candidate_sha256'] == DLL and not report['errors']
    assert complete['all_own_lives_uniquely_source_bound'] is True
    source = root / 'poc/candidates/redstation-supply-20261107'
    for name, digest in SOURCE_PINS.items():
        assert sha(source / name) == digest, name
    lives = {(x['role'], x['local'], x['generation']): x for x in complete['lives']}
    spawned = {(x['role'], x['local'], x['generation']): x
               for x in complete['source_native_bindings']}
    all_rows = []; seen = set(); raw_tags = Counter(); all_supply = []
    for role in ('botA', 'botB'):
        for line, text in enumerate((case / (role + '-closed.log')).read_text().splitlines(), 1):
            if not text.startswith('[Cecil'): continue
            tag = text.split(']', 1)[0][1:]; raw_tags[tag] += 1
            values = dict(re.findall(r'(\w+)=([^\s]+)', text))
            if tag in ('CecilSupplyDiagCandidate', 'CecilSupplyDiagSelection'):
                all_supply.append(dict(role=role, line=line, tag=tag, fields=values, text=text))
            if tag != 'CecilDriverFinalV1': continue
            assert len(text.encode()) + 2 <= 2048
            d = typed(values)
            token = (role, d['local'], d['tick'], d['actor'], d['gen'][0])
            assert token not in seen, ('duplicate invocation', token)
            seen.add(token)
            item = dict(role=role, line=line, text=text, typed=d,
                        invocation_token=list(token), actual_current_map='UNKNOWN',
                        native_clock_binding='UNKNOWN', same_call_supply_rows=[])
            key = (role, d['local'], d['gen'][0]); spawn = spawned.get(key)
            life = lives.get(key)
            if spawn is None:
                item['life_binding'] = 'UNKNOWN_NO_MATCHING_SOURCE_SPAWN'
            elif int(spawn['spawn']['entity']) != d['actor']:
                item['life_binding'] = 'UNKNOWN_ACTOR_DIFFERS_FROM_SOURCE_SPAWN'
            elif not d['life_link']:
                item['life_binding'] = 'UNKNOWN_ENTRY_EXIT_ACTOR_OR_GENERATION_CHANGED'
            elif life is None:
                item['life_binding'] = 'SOURCE_ONLY_NO_NATIVE_LIFE_WITNESS'
            else:
                assert life['entity'] == d['actor'] and spawn['match_count'] == 1
                assert life['source_spawn']['line'] < line
                item['life_binding'] = 'EXACT_COHORT_LOCAL_ACTOR_ENTRY_EXIT_GENERATION'
                item.update(slot=life['slot'], generation=life['generation'],
                            spawn_clock=life['spawn_clock'])
                witnesses = [x for x in life['source_life_rows']
                             if x['tag'] in ('CecilWeaponObserve', 'CecilPlayerObserve')
                             and x.get('tick') == str(d['tick'])
                             and x.get('entity') == str(d['actor'])
                             and x.get('generation') == str(d['gen'][0])
                             and Decimal(x.get('native_time', '0')) > 0
                             and (x['tag'] != 'CecilWeaponObserve' or x.get('valid') == '1')]
                valid = [x for x in witnesses
                         if Decimal.from_float(life['spawn_clock']) <= interval(x['native_time'])[0]
                         and interval(x['native_time'])[1] <= Decimal.from_float(life['last_alive_observed_tick'])]
                item['native_clock_witnesses'] = witnesses
                if valid:
                    item['native_clock_binding'] = 'WHOLE_DECIMAL_INTERVAL_INSIDE_OBSERVED_LIFE'
                    item['accepted_native_clock_witnesses'] = valid
                # These are unique per-local/tick invocation fields from the
                # production single BotSupplyTick call. Entity here is ITEM.
                # Generation-changing calls above deliberately do not link.
                item['same_call_supply_rows'] = [x for x in all_supply
                    if x['role'] == role and x['fields'].get('local') == str(d['local'])
                    and x['fields'].get('tick') == str(d['tick'])
                    and x['fields'].get('generation') == str(d['gen'][0])]
            all_rows.append(item)
    # Full denominator independent of outcome. All source-only/tail/changed-life
    # records stay in the receipt; they never gain an interpolated native clock.
    count = Counter(x['life_binding'] for x in all_rows)
    clock_count = Counter(x['native_clock_binding'] for x in all_rows)
    contention_counts = {}
    for tag in ('CecilSupplyDiagCandidate', 'CecilSupplyDiagSelection'):
        rows = [x for x in all_supply if x['tag'] == tag]
        contention_counts[tag] = dict(rows=len(rows),
            contested=sum(x['fields'].get('contested') == '1' for x in rows),
            owner_valid=sum(x['fields'].get('owner_valid') == '1' for x in rows))
        for row in rows:
            v = row['fields']
            if v.get('owner_valid') != '1': continue  # Unknown, not proof of no owner.
            assert v['contested'] == '1' and float(v['owner_cost']) + 1 < float(v['claim_cost'])
            if tag == 'CecilSupplyDiagSelection':
                assert v['prefer_uncontested'] == '1' and v['chosen'] == v['owner_item']
                assert 0 <= float(v['observed_common']) - float(v['owner_seen_common']) <= .250001
                assert 0 <= float(v['owner_local_time']) - float(v['owner_progress_local']) < 5
                assert float(v['owner_local_time']) < float(v['owner_deadline_local'])
    never = sorted((x for x in complete['lives'] if x['first_useful_observed_tick'] is None),
                   key=lambda x: x['observed_alive_span_seconds'], reverse=True)
    exact = decisions['exact_position_zero_translation']
    still = sorted((x for x in complete['lives']
                    if exact.get(str((x['slot'], x['spawn_clock']))) is not None),
                   key=lambda x: exact[str((x['slot'], x['spawn_clock']))]['span_seconds'], reverse=True)
    focus = []
    for kind, selected in (('LONGEST_NEVER_USEFUL', never[:3]), ('EXACT_STILLNESS', still[:3])):
        for life in selected:
            rows = [r for r in all_rows if r.get('slot') == life['slot']
                    and r.get('spawn_clock') == life['spawn_clock']]
            focus.append(dict(kind=kind, role=life['role'], local=life['local'], slot=life['slot'],
                generation=life['generation'], spawn_clock=life['spawn_clock'],
                observed_alive_span_seconds=life['observed_alive_span_seconds'],
                ending=life['ending'], left_censored=life['left_censored'],
                exact_stillness=exact.get(str((life['slot'], life['spawn_clock']))),
                max_stationary=life['max_stationary'],
                source_chain=life['source_chain'], final_rows=rows,
                supply_source_rows=[r for r in all_supply if r['role'] == life['role']
                    and r['fields'].get('local') == str(life['local'])
                    and r['fields'].get('generation') == str(life['generation'])]))
    result = dict(schema='ssam.closed029.driver-final-audit.v1', qualified=False, a4_pass=False,
        evidence=str(case), result_sha256=RESULT, source_pins=SOURCE_PINS,
        reader_sha256=sha(__file__), parent_receipts={name: sha(output / name) for name in
            ('reader-adaptation.json', 'life-summary.json', 'complete-receipt.json',
             'decision-receipt.json', 'final-receipt.json')},
        driver_final_count=len(all_rows), life_binding_counts=dict(count),
        contention_receipt_counts=contention_counts,
        native_clock_binding_counts=dict(clock_count), all_rows=all_rows,
        source_tag_denominators=dict(raw_tags), all_supply_candidate_selection=all_supply,
        focus=focus, limits=[
            'Submitted SetAction argument is not a native ACK, actual movement, shot, hit or damage.',
            'Actual current map is unknown for every DriverFinalV1 row; baseline pin is not a live map read.',
            'Only exact cohort/local/tick/actor and unchanged entry/exit generation identify an invocation.',
            'Missing/throttled final rows and native clocks are not interpolated.',
            'Candidate entity is an item; owner receipt is qualified current selection context, not pickup attribution.',
            'Same-life source context without a wholly contained same-tick native clock is not timed into an episode.',
            'Single600s diagnostic window cannot establish comparative performance or all-map acceptance.'])
    path = output / 'driver-final-receipt-v2.json'
    data = (json.dumps(result, allow_nan=False, separators=(',', ':')) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(),
                      'bytes': len(data), 'driver_final_count': len(all_rows),
                      'life_binding_counts': dict(count), 'native_clock_binding_counts': dict(clock_count)}))
    for x in focus:
        print('FOCUS', x['kind'], x['role'], x['local'], x['generation'], x['spawn_clock'],
              x['observed_alive_span_seconds'], len(x['final_rows']),
              None if x['exact_stillness'] is None else x['exact_stillness']['span_seconds'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    analyze(args.case, args.output, Path(__file__).resolve().parents[1])
