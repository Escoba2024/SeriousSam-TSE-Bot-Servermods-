#!/usr/bin/env python3
"""Pin a manually selected, running 2x4 retail generation for read-only monitoring.

No discovery, process control, runtime edits or public identity data are emitted.
The private receipt is not a native acceptance; regenerate only after reviewing a
new generation. Output creation is exclusive to preserve prior evidence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build_receipt(result_file):
    result_file = Path(result_file).resolve(strict=True)
    raw = result_file.read_bytes()
    result = json.loads(raw)
    receipt = {'version': 1, 'resultHash': sha(raw), 'roles': {}}
    guids, names = set(), set()
    for role in ('server', 'botA', 'botB'):
        recorded = result['processes'][role]
        cwd = result_file.parent / role
        assert str(cwd) == recorded['cwd'], 'runtime CWD mismatch'
        pid = recorded['pid']
        proc = Path('/proc') / str(pid)
        start = int((proc / 'stat').read_text().rsplit(') ', 1)[1].split()[19])
        assert start == recorded['start_ticks'] and (proc / 'cwd').resolve() == cwd, 'process identity mismatch'
        pin = dict(recorded, uid=proc.stat().st_uid, cgroup=(proc / 'cgroup').read_text().strip(), binaryHashes={})
        exe = 'DedicatedServer.exe' if role == 'server' else 'SeriousSam.exe'
        assert ('Bin/' + exe) in (proc / 'cmdline').read_text(), 'wrong executable'
        for name in (exe, 'Engine.dll', 'EntitiesMP.dll', 'GameMP.dll'):
            pin['binaryHashes'][name] = sha((cwd / 'Bin' / name).read_bytes())
        if role != 'server':
            pin['profiles'] = []
            for slot in range(4):
                p = cwd / 'Players' / f'Player{slot}.plr'
                b, guid = p.read_bytes(), Path(str(p) + '.guid').read_bytes()
                assert b[:4] == b'PLC4' and len(guid) == 16 and b.count(guid) == 1, 'profile/GUID mismatch'
                size = struct.unpack_from('<I', b, 4)[0]
                assert 0 < size <= 64 and len(b) >= size + 8, 'invalid profile string'
                name = b[8:8+size].decode('ascii')
                name = re.sub(r'\^c[0-9a-fA-F]{6}|\^[a-zA-Z]', '', name)
                assert name and name not in names and guid not in guids, 'ambiguous roster identity'
                names.add(name); guids.add(guid)
                pin['profiles'].append(dict(slot=slot, name=name, profileHash=sha(b), guidHash=sha(guid)))
            # Four local participants confirmed by live telemetry, not profile existence alone.
            rows = (cwd / 'Bin/BotTelemetry.csv').read_bytes()[-65536:].splitlines()
            complete = [x for x in rows if re.match(rb'^\d+,', x)]
            assert complete and int(complete[-1].split(b',')[6]) == 4, 'unexpected active local roster'
        receipt['roles'][role] = pin
    assert result_file.read_bytes() == raw, 'result changed during receipt capture'
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    receipt = build_receipt(args.result)
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print('Private runtime receipt created; validate through verifyRuntime before use.')
