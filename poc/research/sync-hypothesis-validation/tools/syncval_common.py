#!/usr/bin/env python3
"""Shared primitives for the sync-hypothesis-validation toolchain.

Scope note
----------
This package is the *hypothesis validation* layer. It does not replace the
log/dump forensic tools under ``poc/research/sync-forensics`` (PR #58); it
consumes their results and adds falsifiable offline models plus an
evidence contract for native runs.

Hard rules implemented here
---------------------------
* Read-only: no process is started, no game file is written, no DLL touched.
* Fail-closed: missing or contradictory data yields ``INCOMPLETE`` /
  ``UNMEASURABLE`` / ``CONFLICT``, never a stability claim.
* No native claim from offline output: every payload carries
  ``evidence_class`` and ``stability_claim`` fields that consumers must
  preserve. Offline model output is never ``native``.

Only documented, already published facts are encoded here:
  * server log lines ``SYNCBAD`` / ``SYNCOK`` / ``SYNCLATE`` / ``SYNCEARLY``
    and the kick text ``Too many bad syncs``
    (docs/reports/2026-10-17-retail107-sync-check-investigation.md),
  * the fixed BotTelemetry CSV layout published in
    poc/candidates/integrated-human-cpu-20261021/BotTelemetry.h,
  * the 20 Hz game tick (``CTimer::TickQuantum = 1/20 s``).
"""

from __future__ import annotations

import json
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SCHEMA = "syncval/1"
EVIDENCE_NOTE = (
    "Offline model or log analysis only. This is not a native Retail-1.07 "
    "acceptance and it does not confirm a root cause."
)

# Evidence classes, ordered from weakest to strongest for *native* claims.
# Only the three runtime classes may ever back a NATIVE_SUPPORTED verdict.
EVIDENCE_CLASSES = (
    "simulation",   # generated fixture, no game involved
    "model",        # offline numeric/behavioural model
    "log",          # log file of a real run (no instrumentation control)
    "telemetry",    # instrumentation CSV of a real run
    "native",       # controlled native evidence bundle (hashes, config, dumps)
)
NATIVE_OK = {"log", "telemetry", "native"}

# Exit codes shared by all tools (documented in README.md).
EXIT_OK = 0
EXIT_USAGE = 2
EXIT_INCOMPLETE = 4
EXIT_INVALID = 5
EXIT_CONFLICT = 6
EXIT_DIVERGENCE = 3

TICK_QUANTUM_S = 1.0 / 20.0


class SyncValError(ValueError):
    """Malformed input that must not be interpreted."""


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def base_payload(tool: str, evidence_class: str) -> Dict[str, object]:
    """Common envelope: every tool output is self-describing."""
    if evidence_class not in EVIDENCE_CLASSES:
        raise SyncValError("unknown evidence class: %r" % (evidence_class,))
    return {
        "schema": SCHEMA,
        "tool": tool,
        "evidence_class": evidence_class,
        "stability_claim": "NONE",
        "evidence_note": EVIDENCE_NOTE,
    }


def observation(obs_id: str, value: object, evidence_class: str,
                source: str) -> Dict[str, object]:
    """A single machine-readable observation for the verdict engine."""
    if evidence_class not in EVIDENCE_CLASSES:
        raise SyncValError("unknown evidence class: %r" % (evidence_class,))
    return {
        "id": obs_id,
        "value": value,
        "evidence_class": evidence_class,
        "source": source,
    }


def collect_observations(payload: object) -> List[Dict[str, object]]:
    """Pull the ``observations`` arrays out of one or more tool payloads."""
    found: List[Dict[str, object]] = []

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            entries = node.get("observations")
            if isinstance(entries, list):
                for entry in entries:
                    if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                        found.append(entry)
            for key, value in node.items():
                if key != "observations":
                    _walk(value)
        elif isinstance(node, list):
            for value in node:
                _walk(value)

    _walk(payload)
    return found


def emit(payload: Dict[str, object], out: Optional[str] = None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if out:
        Path(out).write_text(text + "\n", encoding="utf-8")
    print(text)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SyncValError(message)


def read_json(path: str) -> object:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SyncValError("file not found: %s" % path)
    except json.JSONDecodeError as exc:
        raise SyncValError("invalid JSON in %s: %s" % (path, exc))


# ---------------------------------------------------------------------------
# float32 emulation
# ---------------------------------------------------------------------------

def f32(value: float) -> float:
    """Round a Python float to IEEE-754 binary32 and return it as double."""
    return struct.unpack("<f", struct.pack("<f", value))[0]


def f32_bits(value: float) -> int:
    """Raw binary32 bit pattern of a value (after rounding)."""
    return struct.unpack("<I", struct.pack("<f", f32(value)))[0]


def bits_hex(value: float) -> str:
    return "0x%08X" % f32_bits(value)


def f32_vec(vals: Sequence[float]) -> List[float]:
    return [f32(v) for v in vals]


# ---------------------------------------------------------------------------
# BotTelemetry.csv (fixed layout, see BotTelemetry.h)
# ---------------------------------------------------------------------------

TELEMETRY_REQUIRED_COLUMNS = ("t_ms", "ticks", "actions", "lp", "gameon", "enabled")


@dataclass
class Telemetry:
    path: str
    columns: List[str] = field(default_factory=list)
    headers: List[str] = field(default_factory=list)
    rows: List[Dict[str, str]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def numeric(self, row: Dict[str, str], name: str, default: float = 0.0) -> float:
        return _to_float(row.get(name), default)


def _to_float(raw: Optional[str], default: float = 0.0) -> float:
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def parse_bot_telemetry(path: str) -> Telemetry:
    """Parse the published BotTelemetry.csv layout.

    The ``#columns`` manifest line is authoritative: a file without it, or
    with rows that do not match it, is rejected instead of guessed.
    """
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    tel = Telemetry(path=path)
    rows: List[Dict[str, str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            tel.headers.append(stripped)
            if stripped.startswith("#columns,"):
                tel.columns = [c.strip() for c in stripped[len("#columns,"):].split(",")]
            continue
        if not tel.columns:
            tel.errors.append("data row before #columns manifest: %.60s" % stripped)
            continue
        cells = [c.strip() for c in stripped.split(",")]
        if len(cells) != len(tel.columns):
            tel.errors.append(
                "row cell count %d != column count %d: %.60s"
                % (len(cells), len(tel.columns), stripped)
            )
            continue
        rows.append(dict(zip(tel.columns, cells)))
    tel.rows = rows
    if not tel.columns:
        tel.errors.append("missing #columns manifest line")
    for name in TELEMETRY_REQUIRED_COLUMNS:
        if name not in tel.columns:
            tel.errors.append("missing required column: %s" % name)
    return tel


# ---------------------------------------------------------------------------
# Minimal server-log sync parser (fallback only)
# ---------------------------------------------------------------------------

SYNCBAD_RE = re.compile(
    r"SYNCBAD:\s*Client\s+'([^']+)',\s*Sequence\s+(\d+)\s+Tick\s+([\d.]+)\s*-\s*bad\s+(\d+)"
)
SYNCOK_RE = re.compile(r"SYNCOK:\s*Client\s+'([^']+)',\s*Tick\s+([\d.]+)")
SYNCLATE_RE = re.compile(r"SYNCLATE:\s*Client\s+'([^']+)',\s*Tick\s+([\d.]+)")
SYNCEARLY_RE = re.compile(r"SYNCEARLY:\s*Client\s+'([^']+)',\s*Tick\s+([\d.]+)")
KICK_RE = re.compile(r"Client\s+'([^']+)'\s+ordered to disconnect:\s*Too many bad syncs")
CLIENT_DISCONNECT_RE = re.compile(r"Disconnected:\s*Too many bad syncs")


@dataclass
class SyncLine:
    line_no: int
    kind: str
    client: Optional[str] = None
    sequence: Optional[int] = None
    tick: Optional[float] = None
    counter: Optional[int] = None
    raw: str = ""


def parse_server_sync(log_text: str) -> List[SyncLine]:
    """Extract only SYNC* / kick lines. Deliberately minimal.

    This exists so the cadence and coverage probes can correlate their own
    timelines with sync events without importing the forensic package. For
    full log forensics use ``poc/research/sync-forensics`` (PR #58).
    """
    events: List[SyncLine] = []
    for num, line in enumerate(log_text.splitlines(), 1):
        m = SYNCBAD_RE.search(line)
        if m:
            events.append(SyncLine(num, "SYNCBAD", m.group(1), int(m.group(2)),
                                   float(m.group(3)), int(m.group(4)),
                                   line.strip()[:200]))
            continue
        m = SYNCOK_RE.search(line)
        if m:
            events.append(SyncLine(num, "SYNCOK", m.group(1), None,
                                   float(m.group(2)), None, line.strip()[:200]))
            continue
        m = SYNCLATE_RE.search(line)
        if m:
            events.append(SyncLine(num, "SYNCLATE", m.group(1), None,
                                   float(m.group(2)), None, line.strip()[:200]))
            continue
        m = SYNCEARLY_RE.search(line)
        if m:
            events.append(SyncLine(num, "SYNCEARLY", m.group(1), None,
                                   float(m.group(2)), None, line.strip()[:200]))
            continue
        m = KICK_RE.search(line)
        if m:
            events.append(SyncLine(num, "KICK", m.group(1), None, None, None,
                                   line.strip()[:200]))
            continue
        if CLIENT_DISCONNECT_RE.search(line):
            events.append(SyncLine(num, "CLIENT_DISCONNECT", None, None, None,
                                   None, line.strip()[:200]))
    return events


def first_bad_tick(events: Iterable[SyncLine]) -> Optional[float]:
    for event in events:
        if event.kind == "SYNCBAD" and event.tick is not None:
            return event.tick
    return None


# ---------------------------------------------------------------------------
# Action traces and CPlayerAction layout hypotheses
# ---------------------------------------------------------------------------

@dataclass
class ActionTrace:
    path: str
    source: Optional[str] = None
    samples: Dict[Tuple[int, int], bytes] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def ticks(self) -> List[int]:
        return sorted({tick for tick, _ in self.samples})


def parse_action_trace(path: str) -> ActionTrace:
    """Parse the syncval action-trace format.

    ::

        #syncval-action-trace,rev=1
        #source,synthetic
        #tick,slot,bytes_hex
        137,0,000000000000000000000000...

    ``bytes_hex`` is the raw byte image of one composed ``CPlayerAction``.
    The probe never needs to know the 1.07 field semantics to answer "do the
    bytes the checksum covers differ?" - field names only enrich the report.
    """
    trace = ActionTrace(path=path)
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    for num, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if stripped.startswith("#source,"):
                trace.source = stripped[len("#source,"):].strip()
            continue
        cells = [c.strip() for c in stripped.split(",")]
        if len(cells) != 3:
            trace.errors.append("line %d: expected tick,slot,bytes_hex" % num)
            continue
        try:
            tick = int(cells[0])
            slot = int(cells[1])
        except ValueError:
            trace.errors.append("line %d: non-integer tick/slot" % num)
            continue
        raw = cells[2]
        if len(raw) % 2 != 0:
            trace.errors.append("line %d: odd hex length" % num)
            continue
        try:
            blob = bytes.fromhex(raw)
        except ValueError:
            trace.errors.append("line %d: invalid hex payload" % num)
            continue
        key = (tick, slot)
        if key in trace.samples:
            trace.errors.append("line %d: duplicate sample for tick=%d slot=%d"
                                % (num, tick, slot))
            continue
        trace.samples[key] = blob
    return trace


@dataclass
class FieldSpan:
    name: str
    offset: int
    size: int


@dataclass
class Layout:
    """A *hypothesis* about the CPlayerAction byte layout and checksum scope."""

    status: str
    source: str
    struct_size: int
    fields: List[FieldSpan]
    checksum_calls: List[Tuple[int, int]]   # (offset, length)
    errors: List[str] = field(default_factory=list)

    def covered_bytes(self) -> List[int]:
        covered: List[int] = []
        for offset, length in self.checksum_calls:
            covered.extend(range(offset, offset + length))
        return sorted(set(covered))

    def coverage_of(self, span: FieldSpan) -> str:
        covered = set(self.covered_bytes())
        inside = sum(1 for i in range(span.offset, span.offset + span.size)
                     if i in covered)
        if inside == 0:
            return "OUTSIDE"
        if inside == span.size:
            return "INSIDE"
        return "PARTIAL"

    def field_at(self, index: int) -> List[str]:
        return [f.name for f in self.fields
                if f.offset <= index < f.offset + f.size]

    def validate(self) -> None:
        for span in self.fields:
            if span.offset < 0 or span.size <= 0:
                self.errors.append("field %s has invalid offset/size" % span.name)
            if self.struct_size and span.offset + span.size > self.struct_size:
                self.errors.append("field %s exceeds struct_size" % span.name)
        for offset, length in self.checksum_calls:
            if offset < 0 or length <= 0:
                self.errors.append("invalid checksum call offset/length")
            if self.struct_size and offset + length > self.struct_size:
                self.errors.append("checksum call exceeds struct_size")


def parse_layout(obj: object, path: str = "<inline>") -> Layout:
    require(isinstance(obj, dict), "layout must be a JSON object")
    fields_obj = obj.get("fields", [])
    require(isinstance(fields_obj, list), "layout.fields must be a list")
    fields: List[FieldSpan] = []
    for entry in fields_obj:
        require(isinstance(entry, dict), "layout field must be an object")
        name = entry.get("name")
        offset = entry.get("offset")
        size = entry.get("size")
        require(isinstance(name, str) and name, "layout field needs a name")
        require(isinstance(offset, int) and offset >= 0,
                "layout field %s needs an integer offset" % name)
        require(isinstance(size, int) and size > 0,
                "layout field %s needs a positive size" % name)
        fields.append(FieldSpan(name, offset, size))
    calls_obj = obj.get("checksum_calls", [])
    require(isinstance(calls_obj, list) and calls_obj,
            "layout.checksum_calls must be a non-empty list")
    calls: List[Tuple[int, int]] = []
    for entry in calls_obj:
        require(isinstance(entry, dict), "checksum call must be an object")
        offset = entry.get("offset")
        length = entry.get("length")
        require(isinstance(offset, int) and offset >= 0,
                "checksum call needs an integer offset")
        require(isinstance(length, int) and length > 0,
                "checksum call needs a positive length")
        calls.append((offset, length))
    layout = Layout(
        status=str(obj.get("status", "UNVERIFIED")),
        source=str(obj.get("source", path)),
        struct_size=int(obj.get("struct_size", 0) or 0),
        fields=fields,
        checksum_calls=calls,
    )
    layout.validate()
    return layout


def differing_bytes(left: bytes, right: bytes) -> List[int]:
    """Byte indices whose values differ; length mismatch is an error."""
    if len(left) != len(right):
        raise SyncValError("byte images differ in length: %d vs %d"
                           % (len(left), len(right)))
    return [i for i, (a, b) in enumerate(zip(left, right)) if a != b]


# ---------------------------------------------------------------------------
# Deterministic pseudo randomness for fixtures
# ---------------------------------------------------------------------------

class Lcg:
    """Deterministic 31-bit LCG; identical on every platform."""

    def __init__(self, seed: int = 20261025) -> None:
        self.state = seed & 0x7FFFFFFF

    def next_int(self) -> int:
        self.state = (self.state * 1103515245 + 12345) & 0x7FFFFFFF
        return self.state

    def unit(self) -> float:
        return self.next_int() / float(0x7FFFFFFF)

    def between(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.unit()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main_guard(function) -> None:
    """Uniform CLI error handling: SyncValError -> exit 2 with a message."""
    try:
        code = function()
    except SyncValError as exc:
        print("error: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_USAGE)
    raise SystemExit(code)
