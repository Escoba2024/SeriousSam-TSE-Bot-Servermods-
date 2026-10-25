#!/usr/bin/env python3
"""Gemeinsame Formate und Parser fuer die TSE-Sync-Forensics-Werkzeuge.

Dieses Modul enthaltet:
  * die dokumentarischen Log-Syntax-Konstanten (Server-Log, Client-Log,
    BotTelemetry.csv, Sync-Dump-Textformat),
  * tolerante Parser fuer SYNCBAD / SYNCOK / SYNCLATE / SYNCEARLY /
    Disconnect-Ereignisse,
  * Feld-Kategorisierung fuer Sync-Dump-Unterschiede und
  * eine strict-fail-closed Fehlerbehandlung (nie erfinde viene Divergenz).

Die Werkzeuge in diesem Verzeichnis lesen nur lokal vorhandene Logs und
schreiben ausschließlich JSON-Belege. Sie starten keine Prozesse und
verandern keine Spieldateien.

Hinweis: Die Log-Syntax entstammt den im Projekt dokumentierten Befunden
(docs/reports/2026-10-17-retail107-sync-check-investigation.md,
tools/analyze_sync_log.py, poc/candidates/p0-nullrender-20261022/).
Rohlogs selbst sind privat und werden nicht in diesem Modul gelesen.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Dokumentierte Server-Log-Syntax (tolerant parsebar)
# ---------------------------------------------------------------------------

SYNCBAD_RE = re.compile(
    r"SYNCBAD:\s*Client\s+'([^']+)',\s*Sequence\s+(\d+)\s+Tick\s+([\d.]+)\s*-\s*bad\s+(\d+)"
)
SYNCOK_RE = re.compile(
    r"SYNCOK:\s*Client\s+'([^']+)',\s*Tick\s+([\d.]+)"
)
SYNCLATE_RE = re.compile(
    r"SYNCLATE:\s*Client\s+'([^']+)',\s*Tick\s+([\d.]+)"
)
SYNCEARLY_RE = re.compile(
    r"SYNCEARLY:\s*Client\s+'([^']+)',\s*Tick\s+([\d.]+)"
)
KICK_RE = re.compile(
    r"Client\s+'([^']+)'\s+ordered to disconnect:\s*Too many bad syncs"
)
CLIENT_DISCONNECT_RE = re.compile(
    r"Disconnected:\s*Too many bad syncs"
)
CONNECTED_RE = re.compile(
    r"Client\s+'([^']+)'\s+connected"
)
LEFT_RE = re.compile(
    r"Client\s+'([^']+)'\s+left"
)
MAP_RE = re.compile(
    r"^Level\s+(.+?)\s+started", re.IGNORECASE
)

# ---------------------------------------------------------------------------
# Client-Log-Syntax (tolerant)
# ---------------------------------------------------------------------------

BOTDRIVER_TICK_RE = re.compile(
    r"\[BotDriver\]\s*bot(\d+)\s+tick=(\d+)"
)
BOTP0_NOTE_RE = re.compile(
    r"\[BotP0\]\s*(.+)"
)

# ---------------------------------------------------------------------------
# Sync-Dump-Textformat (nach dem statisch belegten Retail-1.07-Dump-Pfad)
# ---------------------------------------------------------------------------

DUMP_CRC_RE = re.compile(r"^\s*CRC:\s*0x([0-9A-Fa-f]+)\s*$")
DUMP_FIELD_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
DUMP_HEADER_RE = re.compile(
    r"^\s*(Level|Sequence|Tick)\s*[:=]\s*(.+?)\s*$", re.IGNORECASE
)

# Feldkategorien (abgeleitet aus der 1.10-Referenz; fuer Retail-1.07 als
# PROPOSED gekennzeichnet, da die exakte Feldabdeckung nicht ABI-verifiziert).
FIELD_CATEGORY_RULES: List[Tuple[str, Tuple[str, ...]]] = [
    ("session", ("sequence", "level", "pause", "session", "sp_", "gm_")),
    ("player_action", ("action", "pa_", "buttons", "fire", "weapon_select")),
    ("player_entity", ("entity", "player_state", "health", "position", "placement",
                       "rotation", "velocity", "armor", "ammo")),
]

KNOWN_DUMP_FIELDS = {
    "CRC", "Level", "Sequence", "Tick", "Pause", "SessionTime",
    "PlayerActions", "PlayerEntitys", "sc_iLevel", "sc_ulCRC",
}


def classify_field(name: str) -> str:
    """Klassifiziert einen Dump-Feldnamen in eine Scope-Gruppe.

    Unbekannte Felder werden als 'unknown' ausgewiesen - niemals erfunden.
    """
    low = name.lower()
    for category, needles in FIELD_CATEGORY_RULES:
        if any(n in low for n in needles):
            return category
    return "unknown"


# ---------------------------------------------------------------------------
# Datenklassen
# ---------------------------------------------------------------------------

@dataclass
class SyncEvent:
    """Ein einzelnes Server- oder Client-Sync-Ereignis."""
    line_no: int
    kind: str                     # SYNCBAD | SYNCOK | SYNCLATE | SYNCEARLY |
                                  # KICK | CLIENT_DISCONNECT | JOIN | LEAVE | MAP
    client: Optional[str] = None
    sequence: Optional[int] = None
    tick: Optional[float] = None
    count: Optional[int] = None   # bad-Counter bei SYNCBAD
    raw: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "line": self.line_no,
            "kind": self.kind,
            "client": self.client,
            "sequence": self.sequence,
            "tick": self.tick,
            "count": self.count,
        }


@dataclass
class DumpRecord:
    """Ein geparstes Sync-Dump-Snapshot."""
    path: str
    header: Dict[str, str] = field(default_factory=dict)
    crc: Optional[int] = None
    fields: Dict[str, str] = field(default_factory=dict)
    line_count: int = 0
    parse_errors: List[str] = field(default_factory=list)
    raw_lines: List[str] = field(default_factory=list)

    @property
    def aligned_key(self) -> Optional[Tuple[str, int, float]]:
        """Alignment-Schlüssel: (Level, Sequence, Tick)."""
        level = self.header.get("Level")
        try:
            seq = int(self.header.get("Sequence", "-1"))
        except (TypeError, ValueError):
            seq = -1
        try:
            tick = float(self.header.get("Tick", "-1"))
        except (TypeError, ValueError):
            tick = -1.0
        if level is None or seq < 0 or tick < 0:
            return None
        return (level, seq, tick)


def parse_server_log_events(text: str) -> List[SyncEvent]:
    """Parset Server-Log-Zeilen in SyncEvent-Listen (tolerant, fail-closed).

    Unparsebare Zeilen werden ignoriert; falsche Tick-Werte werden als
    letzter Ausweg als None genommen, aber als 'malformed' erkennbar.
    """
    events: List[SyncEvent] = []
    for num, line in enumerate(text.splitlines(), 1):
        m = SYNCBAD_RE.search(line)
        if m:
            client, seq, tick, count = m.groups()
            events.append(SyncEvent(num, "SYNCBAD", client, int(seq), float(tick),
                                    int(count), line.strip()[:200]))
            continue
        m = SYNCOK_RE.search(line)
        if m:
            events.append(SyncEvent(num, "SYNCOK", m.group(1), None, float(m.group(2)),
                                    None, line.strip()[:200]))
            continue
        m = SYNCLATE_RE.search(line)
        if m:
            events.append(SyncEvent(num, "SYNCLATE", m.group(1), None, float(m.group(2)),
                                    None, line.strip()[:200]))
            continue
        m = SYNCEARLY_RE.search(line)
        if m:
            events.append(SyncEvent(num, "SYNCEARLY", m.group(1), None, float(m.group(2)),
                                    None, line.strip()[:200]))
            continue
        m = KICK_RE.search(line)
        if m:
            events.append(SyncEvent(num, "KICK", m.group(1), None, None, None,
                                    line.strip()[:200]))
            continue
        if CLIENT_DISCONNECT_RE.search(line):
            events.append(SyncEvent(num, "CLIENT_DISCONNECT", None, None, None, None,
                                    line.strip()[:200]))
            continue
        m = CONNECTED_RE.search(line)
        if m:
            events.append(SyncEvent(num, "JOIN", m.group(1), None, None, None,
                                    line.strip()[:200]))
            continue
        m = LEFT_RE.search(line)
        if m:
            events.append(SyncEvent(num, "LEAVE", m.group(1), None, None, None,
                                    line.strip()[:200]))
            continue
        m = MAP_RE.search(line)
        if m:
            events.append(SyncEvent(num, "MAP", None, None, None, None,
                                    line.strip()[:200]))
    return events


def parse_client_log_events(text: str) -> List[SyncEvent]:
    """Parset Client-Log-Ereignisse (Disconnect + BotDriver-Ticks)."""
    events: List[SyncEvent] = []
    for num, line in enumerate(text.splitlines(), 1):
        if CLIENT_DISCONNECT_RE.search(line):
            events.append(SyncEvent(num, "CLIENT_DISCONNECT", None, None, None, None,
                                    line.strip()[:200]))
            continue
        m = BOTDRIVER_TICK_RE.search(line)
        if m:
            events.append(SyncEvent(num, "BOT_TICK", None, None, float(m.group(2)), None,
                                    line.strip()[:200]))
            continue
        m = BOTP0_NOTE_RE.search(line)
        if m:
            events.append(SyncEvent(num, "BOT_NOTE", None, None, None, None,
                                    line.strip()[:200]))
    return events


def parse_dump_text(path: str, text: str) -> DumpRecord:
    """Parset einen Sync-Dump-Text (CRC + Header + Felder)."""
    rec = DumpRecord(path=path)
    for line in text.splitlines():
        rec.line_count += 1
        rec.raw_lines.append(line)
        m = DUMP_CRC_RE.match(line)
        if m:
            rec.crc = int(m.group(1), 16)
            continue
        m = DUMP_HEADER_RE.match(line)
        if m:
            rec.header[m.group(1).capitalize()] = m.group(2).strip()
            continue
        m = DUMP_FIELD_RE.match(line)
        if m:
            rec.fields[m.group(1)] = m.group(2)
            continue
        if line.strip():
            rec.parse_errors.append(
                "unparsed line %d: %.80s" % (rec.line_count, line.strip())
            )
    return rec


# ---------------------------------------------------------------------------
# Universelle Bewertung (fail-closed)
# ---------------------------------------------------------------------------

EVIDENCE_NOTE = (
    "Log- und Dump-Analyse allein beweist keine Runtime-Stabilität. "
    "Erst der isolierte native Test mit echten aligned Dumps kann den "
    "ersten divergenten Tick belegen."
)
