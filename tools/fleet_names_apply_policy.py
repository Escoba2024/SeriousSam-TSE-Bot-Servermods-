"""Pure name-only fleet validation and rollback ordering. No runtime authority."""
from collections import Counter
import re
from gaming_names import validate_native, name_id, normalize_occupied

INSTANCES = ('redstation', 'yodeller', 'skulls', 'trouble', 'hole', 'development')
LEGACY_TOKEN = re.compile(r'\^c[0-9a-fA-F]{6}|\^f[0-9]|\^[biBIF]|\^r')
ATTACH = re.compile(r'^\[BotDriver\] local player ([0-3]) \(player index (\d+)\) is now bot-driven: (.*)$')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def assignments(rows):
    require(isinstance(rows, list) and len(rows) == 48, 'exactly 48 assignments')
    expected = {(i, r, n) for i in INSTANCES for r in ('botA', 'botB') for n in range(4)}
    seen, names, ids = set(), set(), set()
    for row in rows:
        key = row['instance'], row['role'], row['local']
        require(type(key[2]) is int and key in expected and key not in seen, 'physical slot identity')
        ordinal = key[2] + (4 if key[1] == 'botB' else 0)
        require(row['bot_id'] == f'{key[0]}.bot.{ordinal:03d}', 'stable bot ID')
        visible = validate_native(row['native_name'])
        require(row['nickname'] == visible and row['name_id'] == name_id(visible), 'name identity')
        require(visible.casefold() not in names and row['bot_id'] not in ids, 'duplicate assignment')
        seen.add(key); names.add(visible.casefold()); ids.add(row['bot_id'])
    return names


def legacy_display(value):
    """Old spellings are identity exclusion data, never newly emitted names."""
    require(isinstance(value, str), 'name text required')
    plain = LEGACY_TOKEN.sub('', value)
    require('^' not in plain, 'unresolved legacy spelling/identity')
    return plain.strip().casefold()


def attach_rows(text):
    rows = {}
    for line in text.splitlines():
        match = ATTACH.fullmatch(line)
        if match:
            local, index, native = int(match[1]), int(match[2]), match[3]
            value = dict(local=local, index=index, native=native)
            require(local not in rows or rows[local] == value, 'ambiguous local attachment epoch')
            rows[local] = value
    require(set(rows) == set(range(4)), 'four actual attached locals required')
    require(len({r['index'] for r in rows.values()}) == 4, 'duplicate actual player index')
    return [rows[i] for i in range(4)]


def fleet(rows, observations, *, applied=False):
    """Validate fresh caller-owned snapshots. Extra players are allowed unchanged.

Each observation has query_names as a LIST (multiplicity matters) and eight
locals from current-process logs plus unchanged PLC GUIDs. No query count alone
establishes ownership. Transport/process freshness belongs to the backend.
"""
    proposed = assignments(rows)
    require(set(observations) == set(INSTANCES), 'all six fresh fleet observations')
    by_slot = {(r['instance'], r['role'], r['local']): r for r in rows}
    unknown = {}
    for instance in INSTANCES:
        ob = observations[instance]
        require(isinstance(ob['query_names'], list), 'preserve query multiplicity')
        locals_ = ob['locals']
        require(len(locals_) == 8, 'eight actual own locals per server')
        slots, indices, guids = set(), set(), set()
        own = []
        for local in locals_:
            key = instance, local['role'], local['local']
            require(key in by_slot and key not in slots, 'actual local identity conflict')
            require(type(local['index']) is int and 0 <= local['index'] < 16 and local['index'] not in indices, 'actual global slot conflict')
            guid = local['guid']
            require(isinstance(guid, str) and re.fullmatch('[0-9a-f]{32}', guid) and int(guid, 16) and guid not in guids, 'own GUID conflict')
            require(local['native'] == local['profile_native'], 'running versus disk name mismatch')
            if applied:
                require(local['native'] == by_slot[key]['native_name'], 'actual local did not load assigned name')
            own.append(legacy_display(local['native']))
            slots.add(key); indices.add(local['index']); guids.add(guid)
        require(len(set(own)) == 8, 'own visible identity collision')
        query = Counter(legacy_display(n) for n in ob['query_names'])
        for name in own:
            require(query[name] == 1, 'own name absent or ambiguous in query')
            del query[name]
        require(not (set(query) & proposed), 'foreign name collides with proposed fleet')
        unknown[instance] = sum(query.values())
    return dict(own_count=48, unknown_counts=unknown, unknown_removed=False,
                independent_external_query_proven=False, dll_qualified=False)


def name_only_paths(paths, roots):
    expected = {f'{roots[i]}/{r}/Players/Player{n}.plr'
                for i in INSTANCES for r in ('botA', 'botB') for n in range(4)}
    red = roots['redstation']
    expected.update((red+'/launch-botA.sh', red+'/launch-botB.sh', red+'/roster100.json'))
    require(set(paths) == expected and len(paths) == 51, 'exact name-only 51 path boundary')
    return expected


class RollbackIncomplete(RuntimeError):
    """Both operation errors survive even when their journal cannot be written."""
    def __init__(self, apply_error, recovery_error, journal_errors):
        self.apply_error = apply_error
        self.recovery_error = recovery_error
        self.journal_errors = tuple(journal_errors)
        super().__init__(f'apply failed: {apply_error!r}; rollback incomplete: '
                         f'{recovery_error!r}; journal errors: {self.journal_errors!r}')


def rollback(backend):
    """Every mutation requires a durable phase intent, including explicit recovery."""
    for state, method in (
        ('rollback_close_own_clients', 'rollback_close'),
        ('rollback_restore_with_rotation_bypassed', 'rollback_restore'),
        ('rollback_start_exact_old_names', 'rollback_start'),
        ('rollback_verify_old_names', 'rollback_verify'),
        ('rollback_restore_original_launch_policy', 'rollback_launch_policy'),
    ):
        backend.event(state)
        getattr(backend, method)()
    backend.event('rolled_back')


def transaction(backend):
    """Run guarded IO; report failures without replacing the original exception.

A failure before the first close intent must not close healthy clients. Once
mutation might have begun, a transient failure-report write must not prevent
rollback. A failed rollback intent stops before that mutation; no undurable
recovery success is claimed. Explicit recovery uses the same rollback function.
"""
    backend.event('preflight')
    backend.preflight()
    backend.event('backup_before_close')
    backend.backup_before_close()
    mutation_started = False
    try:
        backend.event('close_own_clients')
        mutation_started = True
        backend.close_own_clients()
        backend.event('backup_after_close')
        backend.backup_after_close()
        backend.event('apply_51')
        backend.apply_names()
        backend.event('start_own_clients')
        backend.start_own_clients()
        backend.event('verify_all_48')
        result = backend.verify_applied()
        backend.event('applied_names_only', result=result)
        return result
    except BaseException as error:
        journal_errors = []
        try:
            backend.event('apply_failed', error=repr(error))
        except BaseException as reporting:
            journal_errors.append(repr(reporting))
        if mutation_started:
            try:
                rollback(backend)
            except BaseException as recovery:
                try:
                    backend.event('rollback_incomplete', apply_error=repr(error),
                                  recovery_error=repr(recovery), journal_errors=journal_errors)
                except BaseException as reporting:
                    journal_errors.append(repr(reporting))
                raise RollbackIncomplete(error, recovery, journal_errors) from recovery
        for reporting in journal_errors:
            error.add_note('Failure-report journal write failed: '+reporting)
        raise
