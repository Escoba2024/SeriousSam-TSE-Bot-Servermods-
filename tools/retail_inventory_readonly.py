"""Passive Retail 1.07 inventory sampling. Never writes/pauses a target process.

Only the two original Engine/Entities hashes below define supported layouts.
Global slots must come from the trial's join log, not assumed local-player order.
Two equal read passes reduce torn observations; they do not make an atomic snapshot.
"""
import argparse
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import time

ENGINE_SHA = 'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f'
ENTITIES_SHA = '7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350'
FIXTURE = Path('/srv/tse-arena-isolated-20261111')


class EvidenceError(ValueError):
    """Invalid identity, unsupported image, or inconsistent observation."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def unpack(fmt, data, offset=0):
    return struct.unpack_from('<' + fmt, data, offset)


def snapshot(read, engine_base, slots):
    require(len(slots) == 4 and all(type(s) is int and 0 <= s < 16 for s in slots)
            and len(set(slots)) == 4, 'four distinct global slots required')
    observed = []

    def take(address, size):
        require(0x10000 <= address <= 0xffffffff - size and 0 < size <= 65536, 'bad read bounds')
        data = read(address, size)
        require(len(data) == size, 'short read')
        observed.append((address, size, data))
        return data

    def u(address):
        return unpack('I', take(address, 4))[0]

    def finite(value):
        require(math.isfinite(value), 'nonfinite state')
        return value

    network = u(engine_base + 0x20d6a4)
    session = u(network + 0x20)
    table = u(session + 4)
    tick = finite(unpack('f', take(session + 0x4c, 4))[0])
    players = []
    for slot in slots:
        active, entity = unpack('II', take(table + 136 * slot, 8))
        if not active or not entity:
            players.append({'slot': slot, 'present': False})
            continue
        header = take(entity + 0x10, 0x28)
        flags, entity_id = unpack('I', header)[0], unpack('I', header, 12)[0]
        require(not flags & 4, 'deleted player')
        placement = tuple(finite(x) for x in unpack('6f', header, 16))
        world = u(entity + 0x8c)
        health = finite(unpack('f', take(entity + 0xcc, 4))[0])
        buttons, armor = unpack('If', take(entity + 0x36c, 8))
        finite(armor)
        weapon = u(entity + 0x384)
        spawn = finite(unpack('f', take(entity + 0xc14, 4))[0])
        row = dict(slot=slot, present=True, entity_id=entity_id, entity_pointer=entity,
                   world_pointer=world, health=health, armor=armor, placement=placement,
                   spawned_tick=spawn, last_buttons=buttons, weapons=None)
        if weapon:
            weapon_header = take(weapon + 0x10, 16)
            wflags, wid = unpack('I', weapon_header)[0], unpack('I', weapon_header, 12)[0]
            wworld = u(weapon + 0x8c)
            fields = take(weapon + 0xdc, 0x3c)
            capacity, array, used, step = unpack('iIii', fields)
            owner, fire, ammo, current, wanted, previous, owned, change, reload, mirror, anim = unpack('Iiiiiiiiiii', fields, 16)
            require(not wflags & 4 and owner == entity and world >= 0x10000 and world == wworld,
                    'weapon owner/world/deletion mismatch')
            require(0 <= used <= 16 and used <= capacity <= 4096, 'invalid weapon stack size')
            require(0 <= current <= 14 and 0 <= wanted <= 14 and 0 <= previous <= 14,
                    'invalid weapon enum')
            require(0 <= owned <= 0x3fff, 'invalid inventory mask')
            stack = list(unpack(str(used) + 'i', take(array, used * 4))) if used else []
            row['weapons'] = dict(entity_pointer=weapon, entity_id=wid, current=current,
                                  wanted=wanted, previous=previous, owned=owned,
                                  useful_owned=owned & 0x3df8, fire_requested=fire,
                                  has_ammo=ammo, change=change, reload=reload,
                                  mirror_fire=mirror, animation=anim, state_stack=stack)
        players.append(row)
    # An external observer cannot take the game's mutex. Discard any read that
    # changes during this bounded second pass, including same-tick entity reuse.
    for address, size, before in observed:
        require(read(address, size) == before, 'state changed during read')
    require(read(session + 0x4c, 4) == struct.pack('<f', tick), 'tick changed during read')
    return dict(game_tick=tick, players=players,
                all_selected_present=all(p['present'] for p in players))


def process_identity(text):
    try:
        pid = int(text.split(' (', 1)[0])
        fields = text.rsplit(') ', 1)[1].split()
        start = int(fields[19])
    except (ValueError, IndexError) as exc:
        raise EvidenceError('invalid proc stat') from exc
    require(pid > 1 and start > 0, 'invalid process identity')
    return pid, start


def require_identity(text, expected):
    require(len(expected) == 2 and all(type(x) is int and x > 1 for x in expected), 'identity pin required')
    require(process_identity(text) == tuple(expected), 'process identity changed')


def module_base(maps, path, inode, device):
    rows = [line.split(maxsplit=5) for line in maps.splitlines()]
    matched = [row for row in rows if len(row) == 6 and row[5] == str(path)]
    require(bool(matched), 'module mapping missing/deleted')
    require(all(int(row[4]) == inode and tuple(int(x, 16) for x in row[3].split(':')) == device
                for row in matched), 'module inode/device mismatch')
    starts = [int(row[0].split('-')[0], 16) for row in matched if int(row[2], 16) == 0]
    require(len(starts) == 1, 'module base absent/ambiguous')
    return starts[0]


@dataclass(frozen=True)
class FilePin:
    path: Path
    signature: tuple
    sha256: str


def signature(path):
    st = path.stat()
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


def pin_file(path, expected_sha):
    path = Path(path)
    require(not path.is_symlink(), 'symlink module rejected')
    before = signature(path)
    require(re.fullmatch('[0-9a-f]{64}', expected_sha) is not None, 'invalid expected hash')
    require(hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha, 'module hash mismatch')
    require(signature(path) == before, 'module changed during hashing')
    return FilePin(path, before, expected_sha)


def check_file(pin):
    require(not pin.path.is_symlink() and signature(pin.path) == pin.signature, 'pinned module replaced/changed')


def check_read_range(maps, address, size):
    require(type(address) is int and type(size) is int and 0x10000 <= address
            and 0 < size <= 65536 and address + size <= 0x100000000, 'bad read bounds')
    for lower, upper in readable_ranges(maps):
        if lower <= address and address + size <= upper:
            return
    raise EvidenceError('read outside readable mapping')


@lru_cache(maxsize=4)
def readable_ranges(maps):
    return tuple(tuple(int(x, 16) for x in row[0].split('-'))
                 for row in (line.split() for line in maps.splitlines())
                 if row[1].startswith('r'))


# Relocation-free instructions in the two original, hash-pinned modules.
FINGERPRINTS = (
    ('Engine.dll', 0x17020, 'd981cc000000c3'),             # GetHealth +cc
    ('Engine.dll', 0x16e10, '8b818c000000c3'),             # GetWorld +8c
    ('Engine.dll', 0xdc8d0, '8b4120d9404cc3'),             # session +20, game tick +4c
    ('Engine.dll', 0x103037, '8b86e4000000'),              # Call state stack used +e4
    ('EntitiesMP.dll', 0xe6b90, '8b8184030000c3'),        # GetPlayerWeapons +384
    ('EntitiesMP.dll', 0x10c5d4, '858604010000'),          # owned inventory +104
    ('EntitiesMP.dll', 0xed52a, 'd8ae70030000'),           # armor +370
    ('EntitiesMP.dll', 0xed46c, 'd8a6140c0000'),           # spawned tick +c14
)


class InventoryReader:
    """Bounded observation of one explicitly pinned process in our arena fixture.

    Caller supplies the recorded start ticks, not a freshly discovered substitute.
    The private proc-root injection exists for filesystem fixture tests only.
    """
    def __init__(self, pid, start_ticks, root, game_sha, *, _proc_root=Path('/proc')):
        self.fd = None
        self.root = Path(root).resolve(strict=True)
        require(self.root.parent == FIXTURE.resolve(strict=True)
                and self.root.name in ('botA', 'botB', 'server', 'vanilla'), 'outside own arena fixture')
        self.identity = (pid, start_ticks)
        self.proc = Path(_proc_root) / str(pid)
        require_identity((self.proc / 'stat').read_text(), self.identity)
        require((self.proc / 'cwd').resolve(strict=True) == self.root, 'process cwd mismatch')
        self.pins = {}
        for name, digest in [('Engine.dll', ENGINE_SHA), ('EntitiesMP.dll', ENTITIES_SHA), ('GameMP.dll', game_sha)]:
            path = self.root / 'Bin' / name
            require(path.resolve(strict=True) == path, 'module path alias rejected')
            self.pins[name] = pin_file(path, digest)
        self.bases = None
        self.maps = self._guard()
        try:
            self.fd = os.open(self.proc / 'mem', os.O_RDONLY | os.O_CLOEXEC)
            self.maps = self._guard()
            self.bytes_read = 0
            self._fingerprints()
        except BaseException:
            self.close()
            raise

    def _guard(self):
        require_identity((self.proc / 'stat').read_text(), self.identity)
        require((self.proc / 'cwd').resolve(strict=True) == self.root, 'process cwd changed')
        maps = (self.proc / 'maps').read_text()
        bases = {}
        for name, pin in self.pins.items():
            check_file(pin)
            dev, inode = pin.signature[:2]
            bases[name] = module_base(maps, pin.path, inode, (os.major(dev), os.minor(dev)))
        require(self.bases is None or self.bases == bases, 'module mapping base changed')
        self.bases = bases
        return maps

    def _read(self, address, size):
        require(self.fd is not None, 'reader closed')
        check_read_range(self.maps, address, size)
        value = os.pread(self.fd, size, address)
        require(len(value) == size, 'short process read')
        self.bytes_read += size
        return value

    def _fingerprints(self):
        for name, offset, expected in FINGERPRINTS:
            expected = bytes.fromhex(expected)
            require(self._read(self.bases[name] + offset, len(expected)) == expected,
                    'loaded Retail instructions differ: ' + name)

    def sample(self, slots):
        started = time.perf_counter()
        self.maps = self._guard()
        self.bytes_read = 0
        self._fingerprints()
        result = snapshot(self._read, self.bases['Engine.dll'], slots)
        self._guard()
        result.update(process_identity=list(self.identity),
                      hashes={name: pin.sha256 for name, pin in self.pins.items()},
                      consistency='two_equal_reads_not_atomic',
                      bytes_read=self.bytes_read, elapsed_seconds=time.perf_counter() - started)
        return result

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pid', required=True, type=int)
    parser.add_argument('--start-ticks', required=True, type=int)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--game-sha256', required=True)
    parser.add_argument('--slots', required=True, help='exactly four global indices from the join log, comma-separated')
    args = parser.parse_args()
    try:
        slots = tuple(int(x) for x in args.slots.split(','))
        with InventoryReader(args.pid, args.start_ticks, args.root, args.game_sha256) as reader:
            print(json.dumps(reader.sample(slots), allow_nan=False))
    except (EvidenceError, OSError, ValueError, struct.error) as exc:
        print(json.dumps({'status': 'INVALID_OBSERVATION', 'reason': str(exc)}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
