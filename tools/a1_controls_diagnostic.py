"""Opt-in, read-only Original 1.07 controls observations; no input/process launch.

Layouts are statically bound to the original DLLs. Native ABI validation remains
required. A two-pass observation is not atomic and cannot prove input causality.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import struct
import sys

GAME_SHA = '1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'
ENGINE_SHA = 'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f'
BINDINGS = Path(__file__).with_name('a1_controls_original_bindings.json')


def disable_global_smoothing(data):
    """Produce an isolated .ctl variant; caller owns backup and installation."""
    matches = list(re.finditer(rb'(?m)^[ \t]*(GlobalSmoothAxes|GlobalDontSmoothAxes)[ \t]*\r?$', data))
    if len(matches) != 1:
        raise ValueError('exactly one global smoothing directive required')
    a, b = matches[0].span(1)
    return data[:a] + b'GlobalDontSmoothAxes' + data[b:]


class ObservationError(ValueError):
    def __init__(self, message, raw_reads=()):
        super().__init__(message)
        self.raw_reads = list(raw_reads)


def snapshot(read, game_base, engine_base, *, local_slot):
    """Decode one explicit local slot after caller verifies loaded Original guards."""
    raw = []
    def require(ok, message):
        if not ok:
            raise ObservationError(message, raw)

    require(type(local_slot) is int and 0 <= local_slot < 4, 'invalid local slot')
    require(all(type(x) is int and 0x10000 <= x < 0xff000000 for x in (game_base, engine_base)),
            'invalid module bases')
    def take(address, size):
        require(0x10000 <= address <= 0xffffffff-size and 0 < size <= 0x160, 'bad read bounds')
        value = read(address, size)
        raw.append(dict(address=address, size=size, raw_hex=value.hex()))
        require(len(value)==size, 'short controls read')
        return value
    def pointer(address):
        value = struct.unpack('<I', take(address, 4))[0]
        require(0x10000 <= value < 0xff000000 and value % 4 == 0, 'invalid controls pointer')
        return value
    def boolean(value):
        require(value in (0, 1), 'invalid controls flag')
        return value

    game = pointer(game_base+0x2fba4)
    inp = pointer(engine_base+0x1f178c)
    local = game+0xfa0+local_slot*0x80c
    profile, source = struct.unpack('<iI', take(local, 8))
    require(0 <= profile < 8 and 0x10000 <= source < 0xff000000 and source % 4 == 0,
            'invalid active local controls profile/source')
    controls = game+0x2d4+profile*0x160
    smooth = boolean(struct.unpack('<i', take(controls+0x15c, 4))[0])
    axes = {}
    for name, index, expected_binding in [('x', 4, 1), ('y', 3, 2)]:
        values = struct.unpack('<iffiiifff', take(controls+0x10+index*36, 36))
        bound, sensitivity, deadzone, invert, relative, axis_smooth, influence, previous, absolute = values
        require(bound == expected_binding, 'unexpected original mouse axis binding')
        boolean(invert); boolean(relative); boolean(axis_smooth)
        engine = struct.unpack('<f', take(inp+0x10+bound*20, 4))[0]
        require(all(math.isfinite(v) for v in (sensitivity, deadzone, influence, previous, absolute, engine)),
                'nonfinite control axis')
        axes[name] = dict(binding=bound, sensitivity=sensitivity, deadzone=deadzone,
                          invert=invert, relative=relative, smooth=axis_smooth,
                          effective_smooth=int(bool(smooth or axis_smooth)), influence=influence,
                          previous_reading=previous, absolute_reading=absolute, engine_reading=engine)
    first = list(raw)
    for entry in first:
        second = read(entry['address'], entry['size'])
        raw.append(dict(address=entry['address'], size=entry['size'], raw_hex=second.hex(), phase='second'))
        require(second.hex() == entry['raw_hex'], 'controls state changed during read')
    return dict(local_slot=local_slot, profile=profile, source_pointer=source,
                controls_address=controls, global_smooth=smooth, axes=axes,
                consistency='two_equal_reads_not_atomic', raw_reads=raw,
                native_abi_qualified=False, input_cause_proven=False)


def verify_guards(read, bases, bindings):
    for guard in bindings['guards']:
        base = bases[guard['module']]
        expected = bytearray.fromhex(guard['hex'])
        for offset in guard['highlow_offsets']:
            value = struct.unpack_from('<I', expected, offset)[0]
            struct.pack_into('<I', expected, offset, (value+base-guard['preferred_base']) & 0xffffffff)
        if read(base+guard['rva'], len(expected)) != bytes(expected):
            raise ObservationError('loaded Original controls guard differs: '+guard['label'])


def sample(reader, *, local_slot):
    bindings = json.loads(BINDINGS.read_text())
    for name, sha in bindings['original_sha256'].items():
        if reader.pins[name].sha256 != sha:
            raise ObservationError('unsupported controls module: '+name)
    reader.maps = reader._guard()
    verify_guards(reader._read, reader.bases, bindings)
    result = snapshot(reader._read, reader.bases['GameMP.dll'], reader.bases['Engine.dll'], local_slot=local_slot)
    reader._guard()
    result['process_identity'] = list(reader.identity)
    result['hashes'] = bindings['original_sha256']
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    prepare = sub.add_parser('prepare-controls', help='write a new isolated profile; never overwrite')
    prepare.add_argument('--source', type=Path, required=True)
    prepare.add_argument('--output', type=Path, required=True)
    live = sub.add_parser('sample', help='one passive observation of an already owned arena process')
    live.add_argument('--reader-package', type=Path, required=True)
    live.add_argument('--pid', type=int, required=True)
    live.add_argument('--start-ticks', type=int, required=True)
    live.add_argument('--root', type=Path, required=True)
    live.add_argument('--local-slot', type=int, required=True)
    args = p.parse_args()
    try:
        if args.action == 'prepare-controls':
            original = args.source.read_bytes()
            output = disable_global_smoothing(original)
            with args.output.open('xb') as f:
                f.write(output)
            print(json.dumps(dict(source_sha256=hashlib.sha256(original).hexdigest(),
                                  output_sha256=hashlib.sha256(output).hexdigest(), installed=False)))
            return 0
        reader_path = args.reader_package/'tools/retail_inventory_readonly.py'
        binding = json.loads(BINDINGS.read_text())
        if hashlib.sha256(reader_path.read_bytes()).hexdigest() != binding['reader_source_sha256']:
            raise ObservationError('private base reader source pin differs')
        spec = importlib.util.spec_from_file_location('original_a1_controls_base_reader', reader_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        with module.InventoryReader(args.pid, args.start_ticks, args.root, GAME_SHA) as reader:
            print(json.dumps(sample(reader, local_slot=args.local_slot), allow_nan=False))
        return 0
    except (ValueError, OSError, struct.error) as error:
        print(json.dumps(dict(status='INVALID_OBSERVATION', reason=str(error),
                              raw_reads=getattr(error, 'raw_reads', []))))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
