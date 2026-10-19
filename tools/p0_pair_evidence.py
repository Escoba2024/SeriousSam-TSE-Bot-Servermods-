"""Validate archived P0-PAIR metadata, never native sync or capture authenticity.

Stdlib-only, read-only, POSIX descriptor-relative file access. See
p0_pair_evidence.md for schema, independent pin trust and completeness limits.
"""
import argparse
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import stat


ENGINE = 'B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F'
VANILLA = '1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208'
BOT = '61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9'
JSON_LIMIT = 1024 * 1024
DUMP_LIMIT = 8 * 1024 * 1024
SERIES_LIMIT = 32 * 1024 * 1024  # per role
HASH = re.compile(r'[0-9a-fA-F]{64}')
TICK = re.compile(r'[0-9]+(?:\.[0-9]+)?')
CRC = re.compile(r'0x[0-9a-fA-F]{8}')
ROLES = ('server', 'client')
MANIFEST_KEYS = {'schema_version', 'retail_version', 'client_kind', 'run_id',
                 'mapepoch', 'map_sha256', 'modules', 'snapshots'}
PIN_KEYS = {'schema_version', 'retail_version', 'client_kind', 'modules'}
SNAPSHOT_KEYS = {'role', 'run_id', 'mapepoch', 'path', 'sha256', 'size',
                 'encoding', 'level', 'sequence', 'tick', 'crc', 'complete',
                 'truncated', 'dropped_records', 'writer_closed'}


class Invalid(ValueError):
    """Only fixed, public reason codes may enter this exception."""


def need(condition, code):
    if not condition:
        raise Invalid(code)


def shape(value, keys):
    need(type(value) is dict and value.keys() == keys, 'INVALID_SCHEMA')


def digest(value):
    need(type(value) is str and HASH.fullmatch(value) is not None, 'INVALID_HASH')
    return value.upper()


def identifier(value):
    need(type(value) is str and 0 < len(value) <= 128
         and value.strip() == value and all(c.isprintable() for c in value),
         'INVALID_IDENTIFIER')


def decimal_tick(value):
    need(type(value) is str and len(value) <= 128 and TICK.fullmatch(value),
         'INVALID_TICK')
    return Decimal(value)


def relative_parts(value):
    need(type(value) is str and 0 < len(value) <= 4096
         and not any(c in value for c in ('\\', ':', '\x00')),
         'UNSAFE_PATH')
    parts = value.split('/')
    need(all(p not in ('', '.', '..') for p in parts), 'UNSAFE_PATH')
    return parts


class Archive:
    """Read a bounded regular file without following any path-component link.

    Directory handles anchor resolution even if a parent directory is renamed.
    This requires POSIX O_NOFOLLOW/dir_fd; unsupported hosts fail closed.
    """
    def __init__(self, root):
        self.fd = None
        need(os.name == 'posix' and os.open in os.supports_dir_fd
             and hasattr(os, 'O_NOFOLLOW') and hasattr(os, 'O_DIRECTORY'),
             'UNSUPPORTED_SAFE_FILE_ACCESS')
        path = Path(root).absolute()
        need('..' not in path.parts, 'UNSAFE_PATH')
        current = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for part in path.parts[1:]:
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                  dir_fd=current)
                os.close(current)
                current = next_fd
            self.fd = current
        except BaseException:
            os.close(current)
            raise

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        os.close(self.fd)

    def read(self, name, limit):
        parts = relative_parts(name)
        current = os.dup(self.fd)
        try:
            for part in parts[:-1]:
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                  dir_fd=current)
                os.close(current)
                current = next_fd
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                         dir_fd=current)
            try:
                before = os.fstat(fd)
                need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1,
                     'NOT_SINGLE_REGULAR_FILE')
                need(0 < before.st_size <= limit, 'FILE_SIZE_LIMIT')
                chunks = []
                total = 0
                while True:
                    data = os.read(fd, min(65536, limit + 1 - total))
                    if not data:
                        break
                    chunks.append(data)
                    total += len(data)
                    need(total <= limit, 'FILE_SIZE_LIMIT')
                after = os.fstat(fd)
                fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
                need(all(getattr(before, k) == getattr(after, k) for k in fields)
                     and total == before.st_size, 'FILE_CHANGED_DURING_READ')
                return b''.join(chunks)
            finally:
                os.close(fd)
        finally:
            os.close(current)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'DUPLICATE_JSON_KEY')
        result[key] = value
    return result


def reject_constant(unused):
    raise Invalid('INVALID_JSON')


def load_json(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def modules(value, kind):
    shape(value, set(ROLES))
    result = {}
    for role, exe in (('server', 'DedicatedServer.exe'), ('client', 'SeriousSam.exe')):
        shape(value[role], {exe, 'Engine.dll', 'EntitiesMP.dll', 'GameMP.dll'})
        result[role] = {name: digest(pin) for name, pin in value[role].items()}
        need(result[role]['Engine.dll'] == ENGINE, 'UNQUALIFIED_ENGINE_PIN')
        expected = BOT if role == 'client' and kind == 'bot61dc' else VANILLA
        need(result[role]['GameMP.dll'] == expected, 'UNQUALIFIED_GAMEMP_PIN')
    return result


def parse_dump(raw, encoding):
    need(encoding in ('utf-8', 'utf-8-sig', 'cp1252'), 'UNSUPPORTED_ENCODING')
    text = raw.decode(encoding, errors='strict')
    need(text.endswith('\n') and '\x00' not in text, 'INCOMPLETE_DUMP')
    patterns = {
        'CRC': re.compile(r'\s*CRC:\s*(0x[0-9A-Fa-f]{8})\s*'),
        'Level': re.compile(r'\s*Level:\s*([0-9]+)\s*'),
        'Sequence': re.compile(r'\s*Sequence:\s*([0-9]+)\s*'),
        'Tick': re.compile(r'\s*Tick:\s*([0-9]+(?:\.[0-9]+)?)\s*'),
    }
    headers = {}
    last_header = -1
    lines = text.splitlines()
    for i, line in enumerate(lines):
        prefix = re.match(r'\s*(CRC|Level|Sequence|Tick)\s*:', line)
        if prefix:
            key = prefix[1]
            match = patterns[key].fullmatch(line)
            need(match is not None and key not in headers, 'INVALID_DUMP_HEADERS')
            headers[key] = match[1]
            last_header = i
    need(headers.keys() == patterns.keys(), 'INVALID_DUMP_HEADERS')
    need(any(line.strip() and not re.fullmatch(r'[_= -]{6,}', line.strip())
             for line in lines[last_header + 1:]), 'INCOMPLETE_DUMP')
    return (int(headers['Level']), int(headers['Sequence']),
            decimal_tick(headers['Tick'])), headers['CRC'].upper()


def check_manifest(archive, manifest_name, pins_name, pins_sha256):
    # Validate independent trust anchor before parsing pin claims.
    expected_hash = digest(pins_sha256)
    pin_raw = archive.read(pins_name, JSON_LIMIT)
    need(hashlib.sha256(pin_raw).hexdigest().upper() == expected_hash,
         'PIN_FILE_HASH_MISMATCH')
    pins = load_json(pin_raw)
    shape(pins, PIN_KEYS)
    manifest = load_json(archive.read(manifest_name, JSON_LIMIT))
    shape(manifest, MANIFEST_KEYS)
    for obj in (pins, manifest):
        need(type(obj['schema_version']) is int and obj['schema_version'] == 1
             and obj['retail_version'] == '1.07'
             and obj['client_kind'] in ('vanilla', 'bot61dc'), 'INVALID_SCHEMA')
    need(manifest['client_kind'] == pins['client_kind'], 'PIN_MODE_MISMATCH')
    trusted_modules = modules(pins['modules'], pins['client_kind'])
    need(modules(manifest['modules'], manifest['client_kind']) == trusted_modules,
         'MODULE_PIN_MISMATCH')
    for name in ('run_id', 'mapepoch'):
        identifier(manifest[name])
    digest(manifest['map_sha256'])
    records = manifest['snapshots']
    need(type(records) is list and 2 <= len(records) <= 256, 'INVALID_SNAPSHOT_COUNT')
    captured = {role: {} for role in ROLES}
    paths = set()
    sizes = {role: 0 for role in ROLES}
    for entry in records:
        shape(entry, SNAPSHOT_KEYS)
        role = entry['role']
        need(type(role) is str and role in ROLES, 'INVALID_ROLE')
        need(entry['run_id'] == manifest['run_id']
             and entry['mapepoch'] == manifest['mapepoch'], 'RUN_EPOCH_MISMATCH')
        need(entry['complete'] is True and entry['truncated'] is False
             and entry['writer_closed'] is True
             and type(entry['dropped_records']) is int and entry['dropped_records'] == 0,
             'INCOMPLETE_CAPTURE')
        need(type(entry['level']) is int and entry['level'] >= 0
             and type(entry['sequence']) is int and entry['sequence'] >= 0,
             'INVALID_DUMP_IDENTITY')
        identity = (entry['level'], entry['sequence'], decimal_tick(entry['tick']))
        need(type(entry['crc']) is str and CRC.fullmatch(entry['crc']), 'INVALID_CRC')
        relative_parts(entry['path'])
        need(entry['path'] not in paths, 'DUPLICATE_SNAPSHOT_PATH')
        paths.add(entry['path'])
        need(identity not in captured[role], 'DUPLICATE_SNAPSHOT_IDENTITY')
        need(type(entry['size']) is int and 0 < entry['size'] <= DUMP_LIMIT,
             'FILE_SIZE_LIMIT')
        sizes[role] += entry['size']
        need(sizes[role] <= SERIES_LIMIT and len(captured[role]) < 128,
             'SERIES_SIZE_LIMIT')
        expected_digest = digest(entry['sha256'])
        need(type(entry['encoding']) is str, 'UNSUPPORTED_ENCODING')
        raw = archive.read(entry['path'], DUMP_LIMIT)
        need(len(raw) == entry['size'], 'SNAPSHOT_SIZE_MISMATCH')
        need(hashlib.sha256(raw).hexdigest().upper() == expected_digest,
             'SNAPSHOT_HASH_MISMATCH')
        raw_identity, raw_crc = parse_dump(raw, entry['encoding'])
        need(identity == raw_identity and entry['crc'].upper() == raw_crc,
             'RAW_METADATA_MISMATCH')
        captured[role][identity] = raw_crc
    need(captured['server'].keys() == captured['client'].keys(), 'UNPAIRED_SNAPSHOTS')
    # A manifest covers one map epoch/level; no merging levels to hide transitions.
    need(len({key[0] for key in captured['server']}) == 1, 'MULTIPLE_LEVELS')
    return {'status': 'VALIDATED_CAPTURE_METADATA',
            'paired_snapshots': len(captured['server']),
            'crc_differing_pairs': sum(captured['server'][key] != captured['client'][key]
                                       for key in captured['server'])}


def base_report():
    return {'native_sync': 'NOT_ASSESSED',
            'first_divergent_tick': 'NOT_DETERMINED',
            'capture_authenticity': 'NOT_ASSESSED',
            'continuous_tick_coverage': 'NOT_ASSESSED'}


def validate(root, manifest, pins, pins_sha256):
    """Return only public codes/counts; never propagate private input errors."""
    result = base_report()
    try:
        with Archive(root) as archive:
            result.update(check_manifest(archive, manifest, pins, pins_sha256))
    except Invalid as exc:
        result.update(status='INVALID_EVIDENCE_MANIFEST', reason=str(exc))
    except (OSError, ValueError, TypeError, RecursionError, OverflowError):
        result.update(status='INVALID_EVIDENCE_MANIFEST', reason='INVALID_INPUT_OR_ARCHIVE')
    return result


class PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, unused):
        raise Invalid('INVALID_ARGUMENTS')


def main(argv=None):
    parser = PrivateArgumentParser(description=__doc__)
    for name in ('root', 'manifest', 'pins', 'pins-sha256'):
        parser.add_argument('--' + name, required=True)
    try:
        args = parser.parse_args(argv)
        report = validate(args.root, args.manifest, args.pins, args.pins_sha256)
    except Invalid:
        report = dict(base_report(), status='INVALID_EVIDENCE_MANIFEST',
                      reason='INVALID_ARGUMENTS')
    print(json.dumps(report, sort_keys=True))
    return 0 if report['status'] == 'VALIDATED_CAPTURE_METADATA' else 2


if __name__ == '__main__':
    raise SystemExit(main())
