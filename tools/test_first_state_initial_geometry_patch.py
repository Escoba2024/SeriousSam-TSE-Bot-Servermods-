"""Pure fixtures execute the actual nested parent Runner functions; never Native."""
import ast
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import textwrap
import types
import unittest

try:
    from tools import first_state_initial_geometry_patch as patch
except ImportError:
    try:
        import first_state_initial_geometry_patch as patch
    except ImportError:
        patch = None

PARENT = Path('/srv/tse-a1-first-state-qjs10-v3-disabled-20261115/run_dual.py')
PARENT_SHA = 'babb8de66565a6966fac8d8378df84d626b3360ba63828ee2c4e834e4fc979fb'

def read(path):
    with os.fdopen(os.open(path.resolve(strict=True), os.O_RDONLY | os.O_NOATIME | os.O_NOFOLLOW), 'r') as stream:
        return stream.read()

SOURCE = read(PARENT)
assert hashlib.sha256(SOURCE.encode()).hexdigest() == PARENT_SHA

class EvidenceError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise EvidenceError(message)

class Clock:
    def __init__(self): self.now = 0.0
    def monotonic(self): return self.now
    perf_counter = monotonic
    def sleep(self, seconds): self.now += seconds

MAPPING = {'vanilla': 0, 'botA': 1}
IDS = {0: 101, 1: 102}
RECORDS = {'server': {'identity': (100, 200)}, 'vanilla': {'identity': (300, 400)}}

def server():
    return {'game_tick': 7.80001163482666, 'process_identity': [100, 200],
            'players': [{'slot': slot, 'present': True, 'entity_id': IDS[slot],
                         'entity_pointer': 0x20000 + slot * 256, 'world_pointer': 0x30000}
                        for slot in (0, 1)] + [{'slot': slot, 'present': False} for slot in (2, 3)]}

def null_message(**changes):
    v = dict(animator=0, slot=1, entity=0x0370c308, entity_id=102, world=0x00b24cac,
             tick=7.7500114440917969)
    v.update(changes)
    return ('invalid animator pointer animator=0x%08x slot=%d entity=0x%08x entity_id=%d '
            'world=0x%08x snapshot_tick=%.17g' %
            (v['animator'], v['slot'], v['entity'], v['entity_id'], v['world'], v['tick']))

class Reader:
    rotation_diagnostics = True
    colt_preparation = True
    mouse_input_profile = False
    def __init__(self, clock, identity, outcomes=None, duration=.001):
        self.clock, self.identity = clock, identity
        self.outcomes = list(outcomes or [])
        self.calls = 0
        self.duration = duration
    def sample(self, slots):
        self.calls += 1
        self.clock.now += self.duration
        out = self.outcomes.pop(0) if self.outcomes else server()
        if isinstance(out, BaseException): raise out
        out = copy.deepcopy(out)
        out['process_identity'] = list(self.identity)
        return out

class Fixture:
    def __init__(self, source, outcomes=None, duration=.001):
        self.clock = Clock()
        self.report = {}
        self.samples, self.pairs = [], []
        self.attempts, self.pair_stream, self.sample_stream = io.StringIO(), io.StringIO(), io.StringIO()
        self.inventory = Reader(self.clock, (100, 200))
        self.client = Reader(self.clock, (300, 400), outcomes, duration)
        tree = ast.parse(source)
        names = ('read_rotation_pair', 'sample', 'native_rotation_pair')
        funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in names}
        lines = source.splitlines()
        def get(name):
            n = funcs[name]
            return textwrap.dedent('\n'.join(lines[n.lineno-1:n.end_lineno]))
        ns = dict(time=self.clock, math=math, json=json, EvidenceError=EvidenceError,
                  S=types.SimpleNamespace(require=require), inventory=self.inventory,
                  vanilla_inventory=self.client, slots=(0, 1, 2, 3), mapping=copy.deepcopy(MAPPING),
                  entity_ids=copy.deepcopy(IDS), records=copy.deepcopy(RECORDS), report=self.report,
                  samples=self.samples, rotation_samples=self.pairs, rotation_attempt_stream=self.attempts,
                  rotation_stream=self.pair_stream, sample_stream=self.sample_stream, started=0.,
                  IGR=patch)
        exec(compile(get('read_rotation_pair'), '<actual-read-rotation-pair>', 'exec'), ns)
        binder = 'def bind(last_sample=-100., last_good_sample=-100.):\n'
        binder += textwrap.indent(get('sample'), ' ') + '\n'
        binder += textwrap.indent(get('native_rotation_pair'), ' ') + '\n'
        binder += ' return sample, native_rotation_pair\n'
        ns['periodic'] = lambda: self.sample(force=True)
        exec(compile(binder, '<actual-nested-sample-and-acquisition>', 'exec'), ns)
        self.sample, self.acquire = ns['bind']()
        self.ns = ns
    def rows(self): return [json.loads(row) for row in self.attempts.getvalue().splitlines()]

def transformed():
    return SOURCE if patch is None else patch.transform(SOURCE)

class ActualRunnerTests(unittest.TestCase):
    def test_initial_zero_then_valid_uses_original_loop(self):
        f = Fixture(transformed(), [EvidenceError(null_message())])
        result, error = None, None
        try: result = f.acquire()
        except BaseException as exc: error = exc
        self.assertIsNone(error, 'initial bound zero must be PENDING, not fatal: %r' % error)
        self.assertIs(result, f.pairs[0])
        self.assertEqual((f.client.calls, f.inventory.calls), (2, 2))
        self.assertEqual(len(f.samples), 1)
        self.assertEqual(f.report['initial_geometry_pending_reads'], 1)
        self.assertEqual(f.rows()[0]['status'], 'PENDING_INITIAL_GEOMETRY')
        self.assertEqual(f.rows()[0].get('raw_read_status'), 'FAIL')
        self.assertIn('server_snapshot', f.rows()[0])
        self.assertNotIn('vanilla_snapshot', f.rows()[0])
        self.assertEqual(f.rows()[1]['status'], 'OBSERVED')

    def test_old_parent_zero_fails_with_receipt(self):
        f = Fixture(SOURCE, [EvidenceError(null_message())])
        with self.assertRaisesRegex(EvidenceError, 'animator=0x00000000'): f.acquire()
        self.assertEqual(f.rows()[0]['status'], 'FAIL')
        self.assertEqual(f.client.calls, 1)

    def test_persistent_zero_attempt_bound_unchanged(self):
        f = Fixture(transformed(), [EvidenceError(null_message()) for _ in range(9)])
        with self.assertRaisesRegex(AssertionError, 'bounded diagnostic pair acquisition attempts'): f.acquire()
        self.assertEqual(f.client.calls, 8)
        self.assertEqual(len(f.rows()), 8)
        self.assertFalse(f.pairs)

    def test_persistent_zero_time_bound_unchanged(self):
        f = Fixture(transformed(), [EvidenceError(null_message()) for _ in range(9)], duration=.11)
        with self.assertRaisesRegex(AssertionError, 'diagnostic pair acquisition deadline exceeded'): f.acquire()
        self.assertLess(f.client.calls, 8)
        self.assertFalse(f.pairs)

    def test_zero_after_valid_pair_is_fatal(self):
        f = Fixture(transformed(), [server(), EvidenceError(null_message())])
        f.acquire()
        with self.assertRaisesRegex(EvidenceError, 'animator=0x00000000'): f.acquire()
        self.assertEqual(len(f.pairs), 1)
        self.assertNotIn('initial_geometry_pending_reads', f.report)
        self.assertEqual(f.rows()[-1]['status'], 'FAIL')

    def test_other_errors_and_invalid_bindings_remain_fatal(self):
        for message in [null_message(animator=1), null_message(animator=0x10001),
                        null_message(slot=2), null_message(entity_id=999), null_message(entity=1),
                        null_message(world=0), null_message(tick=float('nan')),
                        'animator owner/world/deletion mismatch', 'module hash mismatch']:
            with self.subTest(message=message):
                f = Fixture(transformed(), [EvidenceError(message)])
                with self.assertRaises(EvidenceError): f.acquire()
                self.assertEqual(f.client.calls, 1)
                self.assertEqual(f.rows()[0]['status'], 'FAIL')
        for mutate in [lambda f: f.ns['records']['server'].update(identity=(999, 200)),
                       lambda f: f.ns['records']['vanilla'].update(identity=(999, 400)),
                       lambda f: f.ns['entity_ids'].update({0:999})]:
            f = Fixture(transformed(), [EvidenceError(null_message())]); mutate(f)
            with self.assertRaises(EvidenceError): f.acquire()
            self.assertEqual(f.client.calls, 1)

    def test_existing_consistency_retry_and_valid_frame_unchanged(self):
        f = Fixture(transformed(), [EvidenceError('state changed during read'), server()])
        f.acquire()
        self.assertEqual(f.report['discarded_reads'], 1)
        self.assertNotIn('initial_geometry_pending_reads', f.report)
        self.assertEqual(f.rows()[0]['status'], 'FAIL')
        self.assertEqual(f.rows()[1]['status'], 'OBSERVED')

    def test_non_evidence_error_is_fatal(self):
        f = Fixture(transformed(), [ValueError(null_message())])
        with self.assertRaises(ValueError): f.acquire()
        self.assertEqual(f.client.calls, 1)

    def test_missing_server_receipt_and_server_failure_are_fatal(self):
        f = Fixture(transformed(), [server()])
        f.inventory.outcomes = [EvidenceError(null_message())]
        with self.assertRaises(EvidenceError): f.acquire()
        self.assertEqual(f.client.calls, 0)
        self.assertNotIn('server_snapshot', f.rows()[0])
        self.assertEqual(f.rows()[0]['status'], 'FAIL')

    def test_pure_classifier_strict_receipt_roster_and_pin_types(self):
        good = {'status': 'FAIL', 'error': repr(EvidenceError(null_message())),
                'server_snapshot': server()}
        args = [null_message(), good, MAPPING, IDS, (100, 200), (300, 400), (300, 400)]
        self.assertIsNotNone(patch.classify_initial_null(*args))
        mutations = [
            lambda a: a[1].pop('server_snapshot'),
            lambda a: a[1].update(status='OBSERVED'),
            lambda a: a[1].update(error='different failure'),
            lambda a: a[1].update(vanilla_snapshot={}),
            lambda a: a[1].update(pair={}),
            lambda a: a[1]['server_snapshot'].update(process_identity=[True, 200]),
            lambda a: a[1]['server_snapshot'].update(process_identity=[100, 201]),
            lambda a: a[1]['server_snapshot'].update(game_tick=float('nan')),
            lambda a: a[1]['server_snapshot']['players'][0].update(entity_id=999),
            lambda a: a[1]['server_snapshot']['players'][0].update(entity_id=True),
            lambda a: a[1]['server_snapshot']['players'][1].update(slot=0),
            lambda a: a[1]['server_snapshot']['players'][2].update(present=True, entity_id=999),
            lambda a: a[1]['server_snapshot']['players'][0].update(present=1),
            lambda a: a[2].update(vanilla=True),
            lambda a: a[3].update({0:True}),
            lambda a: a.__setitem__(4, (True, 200)),
            lambda a: a.__setitem__(5, (300, 401)),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                values = copy.deepcopy(args); mutate(values)
                self.assertIsNone(patch.classify_initial_null(*values))

    def test_method_constructor_not_entered_before_valid_frame(self):
        source = transformed()
        call = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                    and n.func.value.id == 'MW' and n.func.attr == 'MethodWindow')
        expr = compile(ast.Expression(call), '<actual-method-constructor-call>', 'eval')
        for persistent in [False, True]:
            f = Fixture(source, [EvidenceError(null_message())] * (9 if persistent else 1))
            entered = []
            ns = dict(MW=types.SimpleNamespace(MethodWindow=lambda **kw: entered.append(kw)),
                      arm='control', DRAFT=Path('/not-a-real-runtime'), R=None, E=None,
                      parent_started=0., native_roles=f.acquire, records=RECORDS, pins={},
                      own_identity=None, unit=None, method_periodic=None, save=None, report={})
            if persistent:
                with self.assertRaises(AssertionError): eval(expr, ns)
                self.assertEqual(entered, [])
            else:
                eval(expr, ns)
                self.assertEqual(len(entered), 1)
                self.assertIs(entered[0]['frame'], f.pairs[0])

    def test_whole_inverse_and_guarded_function_bodies(self):
        self.assertIsNotNone(patch)
        new = patch.transform(SOURCE)
        self.assertEqual(patch.reverse(new), SOURCE)
        def body(source, name):
            node = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef) and n.name == name)
            return ast.dump(node, include_attributes=False)
        for name in ['read_rotation_pair', 'native_rotation_pair', 'native_roles', 'method_periodic']:
            self.assertEqual(body(SOURCE, name), body(new, name))
        self.assertEqual(new.count('frame=native_roles(),records=records'), 1)
        for mutation in [SOURCE.replace('deadline=time.monotonic()+.2', 'deadline=time.monotonic()+.3'),
                         SOURCE.replace('rotation_read_attempts', 'different_attempts', 1)]:
            with self.assertRaises(ValueError): patch.transform(mutation)
        with self.assertRaises(ValueError): patch.reverse(new.replace("'PENDING_INITIAL_GEOMETRY'", "'NOT_PENDING'", 1))

if __name__ == '__main__': unittest.main()
