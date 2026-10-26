#!/usr/bin/env python3
"""Bounded instrumentation of the pinned Retail 1.07 server SYNC handler.

Private research only. Frida changes code memory temporarily; no game-state
writes, no packet injection, no sync-kick changes and no public-server support.
Handler entry counts CANNOT prove CRC correspondence, causes or stable gameplay.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import time

ENGINE_SHA256 = "b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f"
HANDLER_RVA = 0x000E2D10  # Ghidra: 0x601a2d10 - original image base 0x600c0000.
LEVEL_RVA = 0x000E34B2    # objdump IA32: 3b c8 (cmp ecx, eax)
CRC_RVA = 0x000E34CA      # objdump IA32: 3b d0 (cmp edx, eax)
ALLOWED_RVAS = frozenset((HANDLER_RVA, LEVEL_RVA, CRC_RVA))
EXPECTED_SCOPE = "ISOLATED_NETNS_RETAIL_WINE"
EXPECTED_CGROUP = re.compile(r"^/sys/fs/cgroup/tse-sessions-[0-9]+$")
EXPECTED_NETNS = re.compile(r"^net:\[[0-9]+\]$")


class ProbeBlocked(RuntimeError):
    """A safety invariant was not established; never start instrumentation."""


def validate_binding(runtime, report, proc, host_netns, engine_sha):
    """Require exact source/namespace/process-generation match before attaching."""
    root = Path(runtime)
    if (root.parent != Path("/srv") or
            not root.name.startswith("tse-session-qualification-master-") or
            not root.name.replace("-", "").replace("_", "").isalnum()):
        raise ProbeBlocked("PRIVATE_ROOT")
    if not isinstance(report, dict) or (report.get("status") != "MEASURING" or
            report.get("scope") != EXPECTED_SCOPE or
            not EXPECTED_CGROUP.fullmatch(str(report.get("cgroup", "")))):
        raise ProbeBlocked("ACTIVE_PRIVATE_MEASURING_REQUIRED")
    ns = report.get("network_namespace")
    if (not isinstance(ns, str) or not EXPECTED_NETNS.fullmatch(ns) or
            proc.get("netns") != ns or host_netns == ns):
        raise ProbeBlocked("PRIVATE_NETNS")
    if (proc.get("comm") != "DedicatedServer" or proc.get("uid") != 65534 or
            proc.get("cwd") != str(root / "server") or
            type(proc.get("pid")) is not int or proc["pid"] < 2):
        raise ProbeBlocked("OWNED_SERVER")
    if type(proc.get("start_ticks")) is not int or proc["start_ticks"] <= 0:
        raise ProbeBlocked("PROCESS_EPOCH")
    if proc.get("cgroup") != "0::" + report["cgroup"].removeprefix("/sys/fs/cgroup"):
        raise ProbeBlocked("PROCESS_CGROUP")
    if engine_sha != ENGINE_SHA256:
        raise ProbeBlocked("ENGINE_HASH")
    return True


def summarize_observation(count, elapsed_s, detached):
    if type(count) is not int or count < 0 or not detached:
        status = "PROBE_FAILED"
    elif count:
        status = "HANDLER_REACHED_ONLY"
    else:
        status = "NO_HANDLER_REACHABILITY_PROVEN"
    return {
        "status": status, "observed_handler_entries": count if type(count) is int and count >= 0 else None,
        "duration_s": round(elapsed_s, 3),
        "native_crc_causation": "NOT_ESTABLISHED",
        "applied_action_capture": "NOT_IMPLEMENTED",
        "server_client_state_pairing": "NOT_IMPLEMENTED",
        "release_qualification": "NOT_ESTABLISHED",
        "instrumentation": "FRIDA_INTERCEPTOR_ATTACH_MODIFIES_CODE_MEMORY_TEMPORARILY",
    }


def summarize_server_operands(rows):
    """Aggregate only the exact native server operands; never claim pairing."""
    crc = level = bad_crc = bad_level = 0
    for row in rows:
        if not isinstance(row, dict) or row.get("event") not in ("level_operands", "crc_operands"):
            raise ProbeBlocked("OPERAND_EVENT_INVALID")
        lhs, rhs = row.get("lhs"), row.get("rhs")
        if (type(lhs) is not int or type(rhs) is not int or
                not 0 <= lhs <= 0xffffffff or not 0 <= rhs <= 0xffffffff or
                type(row.get("tag")) is not int or not 1 <= row["tag"] <= 128):
            raise ProbeBlocked("OPERAND_VALUES_INVALID")
        if row["event"] == "level_operands":
            level += 1
            bad_level += (lhs != rhs)
        else:
            crc += 1
            bad_crc += (lhs != rhs)
    return {
        "status": "SERVER_OPERANDS_ONLY" if crc else "NO_CRC_OPERANDS_CAPTURED",
        "server_level_comparisons": level, "server_level_mismatches": bad_level,
        "server_crc_comparisons": crc, "server_crc_mismatches": bad_crc,
        "native_crc_causation": "NOT_ESTABLISHED",
        "release_qualification": "NOT_ESTABLISHED",
        "server_client_state_pairing": "NOT_IMPLEMENTED",
    }


def read_process_record(pid):
    path = Path("/proc") / str(pid)
    # Procfs reads must be immediately rechecked before and during attach.
    raw = (path / "stat").read_text().rsplit(") ", 1)[1].split()
    name = (path / "comm").read_text().strip()
    status = (path / "status").read_text()
    uidmatch = re.search(r"^Uid:\s+(\d+)", status, re.M)
    if not uidmatch:
        raise ProbeBlocked("PROCESS_UID_MISSING")
    return {
        "pid": pid, "comm": name, "start_ticks": int(raw[19]),
        "uid": int(uidmatch[1]), "cwd": os.path.realpath(path / "cwd"),
        "netns": os.readlink(path / "ns/net"),
        "cgroup": (path / "cgroup").read_text().strip(),
    }


def find_pinned_engine_entry(maps_text, engine_path, rva=HANDLER_RVA):
    """Derive an exact executable PE RVA from /proc/maps, not Frida Linux modules."""
    if rva not in ALLOWED_RVAS:
        raise ProbeBlocked("ENGINE_MAPPING_UNAPPROVED_RVA")
    roots = set()
    segments = []
    identities = set()
    for line in maps_text.splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6 or fields[5] != str(engine_path):
            continue
        try:
            lo, hi = (int(v, 16) for v in fields[0].split("-", 1))
            offset = int(fields[2], 16)
        except (ValueError, TypeError):
            raise ProbeBlocked("ENGINE_MAPPING_MALFORMED") from None
        if offset == 0 and "x" in fields[1]:
            roots.add(lo)
        identities.add((fields[3], fields[4]))
        segments.append((lo, hi, "x" in fields[1], offset))
    if len(roots) != 1:
        raise ProbeBlocked("ENGINE_MAPPING_BASE_NOT_UNIQUE")
    base = next(iter(roots))
    # Wine can map noncontiguous PE sections. Never assume file offsets are
    # equivalent to PE RVAs beyond the unique offset-zero image mapping.
    if len(identities) != 1:
        raise ProbeBlocked("ENGINE_MAPPING_INODE_CONFLICT")
    entry = base + rva
    if not any(lo <= entry < hi and executable for lo, hi, executable, _off in segments):
        raise ProbeBlocked("ENGINE_MAPPING_TARGET_NOT_EXECUTABLE")
    return entry


def inspect_runtime(root, pid):
    if not root.is_dir() or root.is_symlink():
        raise ProbeBlocked("PRIVATE_ROOT")
    report = json.loads((root / "result.json").read_text())
    proc = read_process_record(pid)
    engine = root / "server/Bin/Engine.dll"
    # Authenticates bytes on the private layer, not memory's complete integrity.
    expected_sha = hashlib.sha256(engine.read_bytes()).hexdigest()
    validate_binding(root, report, proc, os.readlink("/proc/1/ns/net"), expected_sha)
    entry = find_pinned_engine_entry((Path("/proc") / str(pid) / "maps").read_text(),
                                     str(engine))
    return proc, expected_sha, entry


# JS is a passive count-only instrumentation, not a CRC or packet producer.
FRIDA_JS = r"""
if (Process.arch !== 'ia32' || Process.pointerSize !== 4)
  throw new Error('expected Retail x86 engine');
// Linux Frida module enumeration omits Wine PE files. The host preflight
// resolves this address from an exact hash-pinned /proc/<pid>/maps RVA.
const entry = ptr('HANDLER_ADDRESS');
let hits = 0;
Interceptor.attach(entry, {onEnter(_args) { hits++; }});
rpc.exports = { snapshot() { return hits; } };
send({event:'hook_ready', architecture:Process.arch});
"""


# SECURITY: Interior CMP hooks at known Retail opcodes caused a reproducible
# isolated server crash (Wine page fault at 0x601a2d57). No CMP interception
# code is shipped here. Offline operand aggregates alone cannot prove CRC pairs.


def run(root, pid, seconds, comparisons=False):
    if comparisons:
        # MUST block before inspecting/attaching to any native process.
        raise ProbeBlocked("COMPARISON_HOOK_DISABLED_AFTER_CRASH")
    if not 5 <= seconds <= 90:
        raise ProbeBlocked("DURATION_LIMIT")
    proc, source_sha, entry = inspect_runtime(root, pid)
    import frida  # Only after exclusive native process, netns and SHA checks.
    start = time.monotonic()
    session = None
    script = None
    detached = False
    ready = False
    errors = []
    count = 0
    result_path = root / "private-sync-handler-probe-v2.json"
    if result_path.exists():
        raise ProbeBlocked("EVIDENCE_ALREADY_EXISTS")
    try:
        assert_entry = find_pinned_engine_entry((Path("/proc") / str(pid) / "maps").read_text(),
                                                str(root / "server/Bin/Engine.dll"))
        if assert_entry != entry:
            raise ProbeBlocked("ENGINE_MAPPING_CHANGED_BEFORE_ATTACH")
        if read_process_record(pid) != proc:
            raise ProbeBlocked("PROCESS_EPOCH_CHANGED_BEFORE_ATTACH")
        session = frida.attach(pid)
        js = FRIDA_JS.replace("HANDLER_ADDRESS", f"0x{entry:08x}")
        script = session.create_script(js)

        def on_message(message, _raw):
            nonlocal ready
            if message.get("type") == "error":
                errors.append("FRIDA_HANDLER_ERROR")
            elif (message.get("type") == "send" and
                  message.get("payload", {}).get("event") == "hook_ready"):
                ready = True

        script.on("message", on_message)
        script.load()
        for _ in range(int(seconds * 2)):
            time.sleep(0.5)
            if read_process_record(pid) != proc:
                raise ProbeBlocked("PROCESS_EPOCH_CHANGED_DURING_PROBE")
            if errors:
                raise ProbeBlocked("FRIDA_HANDLER_ERROR")
            count = int(script.exports_sync.snapshot())
    except Exception as error:
        errors.append(type(error).__name__)
    finally:
        if script is not None:
            try:
                count = int(script.exports_sync.snapshot())
            except Exception:
                pass
            try:
                script.unload()
            except Exception:
                errors.append("UNLOAD_FAILED")
        if session is not None:
            try:
                session.detach()
                detached = True
            except Exception:
                errors.append("DETACH_FAILED")
        elapsed = time.monotonic() - start
        summary = summarize_observation(count, elapsed, detached and ready and not errors)
        summary.update(engine_sha256=source_sha, handler_rva="000e2d10",
                       errors=errors, probe_version="ssam-private-handler/2",
                       engine_mapping="HASH_PINNED_EXACT_PROCFS_MAPPING",
                       source_runtime="ORIGINAL_RETAIL_107_HASH_PINNED")
        result_path.write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    return summary


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--runtime", required=True, type=Path)
    a.add_argument("--pid", required=True, type=int)
    a.add_argument("--duration", required=True, type=int)
    a.add_argument("--comparisons", action="store_true",
                   help="disabled after native crash; comparison hooking is refused")
    opt = a.parse_args()
    result = run(opt.runtime.resolve(), opt.pid, opt.duration, comparisons=opt.comparisons)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "HANDLER_REACHED_ONLY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
