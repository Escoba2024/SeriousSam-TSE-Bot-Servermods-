"""Source-only initial paired geometry admission; no reader or runtime mutation.

A PENDING discard is neither a valid snapshot nor evidence of a transient cause.
Server/client ticks and pointers remain distinct observation domains.
"""
import hashlib
import math
import re

PARENT_SHA = 'babb8de66565a6966fac8d8378df84d626b3360ba63828ee2c4e834e4fc979fb'
IMPORT_BEFORE = 'import first_state_inputfree_method as MW'
IMPORT_AFTER = IMPORT_BEFORE + '\nimport first_state_initial_geometry_patch as IGR'
BEFORE = "  except ValueError as error:\n   if str(error).startswith('mouse input profile'):"
AFTER = "  except ValueError as error:\n   if not rotation_samples and isinstance(error,EvidenceError):\n    pending=IGR.classify_initial_null(str(error),attempt,mapping,entity_ids,records['server']['identity'],vanilla_inventory.identity,records['vanilla']['identity'])\n    if pending is not None:\n     attempt.update(raw_read_status=attempt['status'],status='PENDING_INITIAL_GEOMETRY',initial_geometry_pending=pending)\n     report['initial_geometry_pending_reads']=report.get('initial_geometry_pending_reads',0)+1\n     sample_stream.write(json.dumps({'monotonic':now,'discarded':str(error),'pending_initial_geometry':pending})+'\\n');sample_stream.flush();last_sample=now;return\n   if str(error).startswith('mouse input profile'):"
_PATTERN = re.compile(r'invalid animator pointer animator=0x([0-9a-f]{8}) slot=([0-9]+) entity=0x([0-9a-f]{8}) entity_id=([0-9]+) world=0x([0-9a-f]{8}) snapshot_tick=([-+0-9.eE]+)')


def _identity(value):
    return (isinstance(value, (tuple, list)) and len(value) == 2
            and all(type(x) is int and x > 1 for x in value))


def _pointer(value):
    return type(value) is int and 0x10000 <= value <= 0xffffffff and value % 4 == 0


def classify_initial_null(message, receipt, mapping, entity_ids, server_identity,
                          client_reader_identity, client_identity):
    """Return bounded evidence details for one exact pre-first-pair discard, else None.

    Caller additionally requires EvidenceError and no earlier successful pair.
    Client reader's unchanged pre-snapshot _guard owns client process/module
    verification; this function does not read the process or bless the failed
    snapshot. The successful server receipt binds the mapped stable entity IDs.
    """
    try:
        match = _PATTERN.fullmatch(message)
        if match is None:
            return None
        animator, slot, entity, entity_id, world, tick = match.groups()
        animator, slot, entity, entity_id, world = (int(animator, 16), int(slot),
                                                    int(entity, 16), int(entity_id), int(world, 16))
        tick = float(tick)
        canonical = ('invalid animator pointer animator=0x%08x slot=%d entity=0x%08x entity_id=%d '
                     'world=0x%08x snapshot_tick=%.17g' %
                     (animator, slot, entity, entity_id, world, tick))
        if (message != canonical or animator != 0 or not _pointer(entity) or not _pointer(world)
                or not math.isfinite(tick) or tick < 0 or not 0 < entity_id <= 0xffffffff):
            return None
        if (not _identity(server_identity) or not _identity(client_reader_identity)
                or not _identity(client_identity) or tuple(client_reader_identity) != tuple(client_identity)):
            return None
        if (type(receipt) is not dict or receipt.get('status') != 'FAIL'
                or receipt.get('error') != 'EvidenceError(%r)' % message
                or 'vanilla_snapshot' in receipt or 'pair' in receipt):
            return None
        s = receipt['server_snapshot']
        if type(s) is not dict or not _identity(s.get('process_identity')) or tuple(s['process_identity']) != tuple(server_identity):
            return None
        server_tick = s['game_tick']
        if type(server_tick) not in (int, float) or not math.isfinite(server_tick) or server_tick < 0:
            return None
        if (type(mapping) is not dict or set(mapping) != {'vanilla', 'botA'}
                or any(type(x) is not int or not 0 <= x < 16 for x in mapping.values())
                or len(set(mapping.values())) != 2 or type(entity_ids) is not dict
                or set(entity_ids) != set(mapping.values())
                or any(type(x) is not int or not 0 < x <= 0xffffffff for x in entity_ids.values())
                or slot not in mapping.values() or entity_ids[slot] != entity_id):
            return None
        players = s['players']
        if type(players) is not list or len(players) != 4:
            return None
        rows = {}
        all_slots = set()
        for row in players:
            if (type(row) is not dict or type(row.get('slot')) is not int
                    or not 0 <= row['slot'] < 16 or row['slot'] in all_slots
                    or type(row.get('present')) is not bool):
                return None
            all_slots.add(row['slot'])
            if row['present']:
                if (row['slot'] not in entity_ids or type(row.get('entity_id')) is not int
                        or row['entity_id'] != entity_ids[row['slot']]):
                    return None
                rows[row['slot']] = row
        if set(rows) != set(mapping.values()):
            return None
        return {'reason': 'BOUND_CLIENT_NULL_ANIMATOR_BEFORE_FIRST_VALID_PAIR',
                'slot': slot, 'entity_id': entity_id, 'client_entity_pointer': entity,
                'client_world_pointer': world, 'client_snapshot_tick': tick,
                'server_snapshot_tick': server_tick, 'server_process_identity': list(server_identity),
                'client_process_identity': list(client_identity), 'animator_pointer': 0,
                'snapshot_accepted': False, 'null_state_cause': 'UNKNOWN'}
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def transform(source):
    if hashlib.sha256(source.encode()).hexdigest() != PARENT_SHA:
        raise ValueError('exact QJS10 V3 disabled parent required')
    if source.count(IMPORT_BEFORE) != 1 or source.count(BEFORE) != 1:
        raise ValueError('unique initial geometry insertion anchors required')
    result = source.replace(IMPORT_BEFORE, IMPORT_AFTER, 1).replace(BEFORE, AFTER, 1)
    if reverse(result) != source:
        raise ValueError('whole Runner inverse failed')
    return result


def reverse(source):
    if source.count(IMPORT_AFTER) != 1 or source.count(AFTER) != 1:
        raise ValueError('unique initial geometry reverse anchors required')
    result = source.replace(AFTER, BEFORE, 1).replace(IMPORT_AFTER, IMPORT_BEFORE, 1)
    if hashlib.sha256(result.encode()).hexdigest() != PARENT_SHA:
        raise ValueError('whole Runner inverse parent mismatch')
    return result
