#!/usr/bin/env python3
"""Read-only PE32 ABI preflight for original TSE Retail 1.07 and a Bot GameMP.

No libraries beyond stdlib, processes, instrumentation, output files, or binary edits.
PASS_STATIC_PE_LINKAGE is NOT a runtime, struct-layout, CRC or multiplayer PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED = {
    "engine": "B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F",
    "retail_game": "1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208",
    "bot_game": "61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9",
    "entities": "7F595F2A7FC96A978B3467983E8F17C70D827F17A5F4EE887F9C7A1F20B1D350",
}


class PEError(ValueError):
    """Malformed, unsupported, or truncated PE data."""


class PE32:
    def __init__(self, data: bytes):
        self.data = data
        if data[:2] != b"MZ":
            raise PEError("DOS magic missing")
        pe = self.u32(0x3C)
        if self.slice(pe, 4) != b"PE\x00\x00":
            raise PEError("PE signature missing")
        self.machine = self.u16(pe + 4)
        self.section_count = self.u16(pe + 6)
        optional_size = self.u16(pe + 20)
        op = pe + 24
        if self.machine != 0x14C or self.u16(op) != 0x10B:
            raise PEError("expected Intel x86 PE32 (not PE32+/x64)")
        if optional_size < 224:
            raise PEError("optional header too small")
        self.slice(op, optional_size)
        self.image_base = self.u32(op + 28)
        self.header_size = self.u32(op + 60)
        self.sections = []
        for i in range(self.section_count):
            off = op + optional_size + 40 * i
            virtual_size, va, raw_size, raw_ptr = struct.unpack("<IIII", self.slice(off + 8, 16))
            self.sections.append((va, max(virtual_size, raw_size), raw_ptr, raw_size))
        directories = self.u32(op + 92)
        if directories < 2:
            raise PEError("export and import data directories missing")
        self.export_rva, self.export_size = struct.unpack("<II", self.slice(op + 96, 8))
        self.import_rva, _ = struct.unpack("<II", self.slice(op + 104, 8))

    def slice(self, off: int, size: int) -> bytes:
        if off < 0 or size < 0 or off + size > len(self.data):
            raise PEError("PE read outside file")
        return self.data[off:off + size]

    def u16(self, off: int) -> int:
        return struct.unpack("<H", self.slice(off, 2))[0]

    def u32(self, off: int) -> int:
        return struct.unpack("<I", self.slice(off, 4))[0]

    def offset(self, rva: int, size: int = 1) -> int:
        if rva == 0:
            raise PEError("null RVA")
        for va, mapped_size, raw_ptr, raw_size in self.sections:
            delta = rva - va
            if 0 <= delta and delta + size <= min(mapped_size, raw_size):
                self.slice(raw_ptr + delta, size)
                return raw_ptr + delta
        if rva + size <= self.header_size:
            self.slice(rva, size)
            return rva
        raise PEError("RVA points outside mapped file-backed section")

    def string(self, rva: int) -> str:
        off = self.offset(rva)
        end = self.data.find(b"\x00", off, min(off + 4096, len(self.data)))
        if end < 0:
            raise PEError("unterminated PE string")
        return self.data[off:end].decode("ascii", errors="strict")

    def exports(self) -> tuple[dict[str, int], set[int]]:
        if not self.export_rva:
            return {}, set()
        e = self.offset(self.export_rva, 40)
        ordinal_base = self.u32(e + 16)
        count_functions = self.u32(e + 20)
        count_names = self.u32(e + 24)
        if max(count_functions, count_names) > 100000:
            raise PEError("unreasonable export count")
        function_rvas = self.u32(e + 28)
        name_rvas = self.u32(e + 32)
        ordinal_rvas = self.u32(e + 36)
        functions = [self.u32(self.offset(function_rvas + 4*i, 4))
                     for i in range(count_functions)]
        ordinal_set = {ordinal_base+i for i, rva in enumerate(functions) if rva}
        named = {}
        for i in range(count_names):
            name = self.string(self.u32(self.offset(name_rvas + 4*i, 4)))
            index = self.u16(self.offset(ordinal_rvas + 2*i, 2))
            if index >= count_functions:
                raise PEError("export ordinal index out of range")
            named[name] = functions[index]
        return named, ordinal_set

    def imports(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        if not self.import_rva:
            return result
        for descriptor in range(2048):
            d = self.offset(self.import_rva + descriptor*20, 20)
            original_thunk = self.u32(d)
            dll_rva = self.u32(d + 12)
            first_thunk = self.u32(d + 16)
            if not (original_thunk or dll_rva or first_thunk):
                break
            if dll_rva == 0:
                raise PEError("import descriptor lacks library name")
            dll = self.string(dll_rva).casefold()
            values = result.setdefault(dll, set())
            thunk = original_thunk or first_thunk
            for i in range(100000):
                entry = self.u32(self.offset(thunk + 4*i, 4))
                if entry == 0:
                    break
                values.add(f"#{entry & 0xFFFF}" if entry & 0x80000000
                           else self.string(entry + 2))
            else:
                raise PEError("unterminated import thunk table")
        else:
            raise PEError("unterminated import descriptor table")
        return result

    def function_prefix(self, export: str, size: int = 48) -> bytes:
        exports, _ = self.exports()
        if export not in exports:
            raise PEError(f"missing {export} export")
        return self.slice(self.offset(exports[export], size), size)


def unresolved(symbols: set[str], names: dict[str, int], ordinals: set[int]) -> list[str]:
    return sorted(s for s in symbols if
                  (int(s[1:]) not in ordinals if s.startswith("#")
                   else s not in names))


def analyze(data: dict[str, bytes], enforce_known_hashes: bool = True) -> dict:
    images = {key: PE32(value) for key, value in data.items()}
    if set(images) != set(EXPECTED):
        raise PEError("four expected images required")
    engine_names, engine_ordinals = images["engine"].exports()
    entity_names, entity_ordinals = images["entities"].exports()
    game_data = {}
    checks = []
    for key in ("retail_game", "bot_game"):
        image = images[key]
        imports = image.imports()
        engine_used = imports.get("engine.dll", set())
        entities_used = imports.get("entitiesmp.dll", set())
        game_names, _ = image.exports()
        prefix = image.function_prefix("GAME_Create")
        missing_engine = unresolved(engine_used, engine_names, engine_ordinals)
        missing_entities = unresolved(entities_used, entity_names, entity_ordinals)
        game_data[key] = {
            "sha256": hashlib.sha256(data[key]).hexdigest().upper(),
            "bytes": len(data[key]),
            "image_base": f"0x{image.image_base:08X}",
            "game_create_rva": f"0x{game_names['GAME_Create']:08X}",
            "game_create_push_0x2fcc_first_48": b"\x68\xCC\x2F\x00\x00" in prefix,
            "engine_import_count": len(engine_used),
            "entities_import_count": len(entities_used),
            "unresolved_engine_imports": missing_engine,
            "unresolved_entities_imports": missing_entities,
            "runtime_dlls": sorted(imports),
        }
        checks.extend([
            len(engine_used) > 0,
            not missing_engine and not missing_entities,
            game_data[key]["game_create_push_0x2fcc_first_48"],
        ])
    old = images["retail_game"].imports()["engine.dll"]
    new = images["bot_game"].imports()["engine.dll"]
    hashes = {key: hashlib.sha256(value).hexdigest().upper()
              for key, value in data.items()}
    if enforce_known_hashes:
        checks.extend(hashes[k] == expected for k, expected in EXPECTED.items())
    return {
        "status": "PASS_STATIC_PE_LINKAGE" if all(checks) else "FAIL_STATIC_PE_LINKAGE",
        "scope": "PE32/export/import/first-48-byte allocation only; no struct/CRC/runtime conclusion",
        "hashes_match_qualified_set": {k: hashes[k] == v for k, v in EXPECTED.items()},
        "engine_export_count": len(engine_names),
        "entities_export_count": len(entity_names),
        "game": game_data,
        "engine_import_only_in_bot": sorted(new-old),
        "engine_import_only_in_original": sorted(old-new),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in EXPECTED:
        parser.add_argument("--" + key.replace("_", "-"), type=Path, required=True)
    parser.add_argument("--allow-other-hashes", action="store_true",
                        help="For isolated test copies only; results not qualified Retail 1.07")
    args = parser.parse_args()
    try:
        inputs = {key: getattr(args, key).read_bytes() for key in EXPECTED}
        report = analyze(inputs, enforce_known_hashes=not args.allow_other_hashes)
    except (OSError, PEError, UnicodeError, struct.error) as exc:
        print(json.dumps({"status": "ERROR_STATIC_PE", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0 if report["status"] == "PASS_STATIC_PE_LINKAGE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
