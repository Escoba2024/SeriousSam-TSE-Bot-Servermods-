#!/usr/bin/env python3
"""
session_hybrid_lab.py - Serious Sam TSE 1.07 Session-Hybrid-Lab (Architecture C1)

Offline, deterministischer Prototyp fur hybride Bot-Sessions:

  * stabile Botidentitaeten (UUIDv5-GUIDs, Profil, Spiel-Seed, Nickname) –
    Identitat uberlebt Crash, Cooldown und Rejoin
  * Session-Lifecycle: OFFLINE -> WAITING -> JOINING -> PLAYING -> LEAVING ->
    COOLDOWN, getrennt geplanter Abgang vs. Crash
  * Human-Slot-Reserve und Mindestpopulation (min_bots)
  * Ghost-Zustande und Server-Neustart-Recovery (verifizierte Abwesenheit
    vor Slot-Wiederverwendung, Epochen-Schutz gegen Doppelstart)
  * zufallige und geordnete Join/Leave-Traces
  * Hybrid-Scheduler C1 (ROSTER_RESTART): Sessions werden auf shared
    4-Spieler-Retail-Clients gepackt; Mitgliedschaftsanderungen werden in
    Batch-Fenstern gebunden und durch Client-Neustart mit neuem Roster
    umgesetzt. Keine neue Engine-Fahigkeit erforderlich (E1/E2 Dynamic-Slot
    bleibt unverifiziert und wird nicht beansprucht).

Designregeln:
* Nur offline: kein Wine, keine Retail-Binary, kein Netzwerk, keine echten
  Prozesse. Deterministisch (ge Seeder PRNG, virtuelle Uhr, wiederholbare
  Traces).
* Keine Zeile ist ein Live-Benchmark und keine Kapazitatsfreigabe.
* Evidenzklassen: [T] = zitierte Hetzner-/PR-Messung,
  [O] = offline getestet (Fixture, dieser Sandbox), [A] = Entwurf,
  [N] = noch nicht gepruft.

Aufbau auf (schreibgeschutzte Referenz, nicht geandert):
  * PR #47: tools/bot_sessions.py (Identitaeten, Lifecycle, Epochen, min_bots)
  * PR #56: poc/research/ram-efficiency/slotplan.py (ROSTER_RESTART-Scheduler)
            poc/research/ram-efficiency/resource_model.py (A/B/C/D RAM-Modell)
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import sqlite3
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Evidence classes (dokumentiert in docs/research/session-hybrid-lab/)
# ---------------------------------------------------------------------------
T = "[T]"  # technisch nachgewiesen (zitierte Hetzner-/PR-Messung)
O = "[O]"  # offline getestet (Fixture, dieser Sandbox)
A = "[A]"  # Architekturvorschlag (Entwurf, kein Laufzeitnachweis)
N = "[N]"  # noch nicht gepruft

VISIBLE_CAP = 24  # eigene konservative Policy-Kappe, kein gemessenes Retail-Maximum
DEFAULT_BANDS = [[0.1, 300, 1199], [0.8, 1200, 5400], [0.1, 5401, 10800]]  # Sekunden
ACTIVE = ("JOINING", "PLAYING", "LEAVING")

ROSTER_RESTART = "ROSTER_RESTART"  # C1: nur erwiesene Primitive (Start/Stopp-Roster)
DYNAMIC_SLOT = "DYNAMIC_SLOT"      # C2: benotigt E1/E2, NICHT verifiziert - Planung nur

JOIN = "JOIN"
LEAVE = "LEAVE"

GHOST_VERIFY_AGE_S = 60.0  # ein Ghost muss mind. so lange ungekannt sein

# Defaults (enabled=False bewusst ausserhalb produktiver Flucht nach vorn)
DEFAULT_CONFIG = {
    "pool_id": "session-hybrid-lab-v1",
    "seed": 20261025,
    "enabled": False,
    "colors_enabled": False,
    "accelerated": False,
    "max_bots": 8,
    "min_bots": 0,
    "reserved_human_slots": 2,
    "maxplayers": 16,
    "join_interval_s": 60.0,
    "leave_interval_s": 15.0,
    "startup_delay_s": [10, 180],
    "pause_s": [900, 7200],
    "session_bands": DEFAULT_BANDS,
    "servers": ["alpha-one", "alpha-two"],
    "connect_delay_s": 8.0,      # modellierter Client-Start/Connect (ohne Wine)
    "client_start_s": 8.0,       # modellierter Viererclient-Start (ohne Wine)
    "batch_window_s": 20.0,
    "idle_stop_s": 30.0,
    "slots_per_client": 4,
    "max_clients": 4,
    "identities": [
        {"id": "player-01", "nickname": "Bot01", "profile": 0,
         "regular_weight": 3}
    ],
}


# ---------------------------------------------------------------------------
# Datenmodelle
# ---------------------------------------------------------------------------
@dataclass
class Identity:
    ident: str
    nickname: str
    profile: int
    regular_weight: float
    color: Optional[str]
    guid: str
    gameplay_seed: int

    def as_dict(self) -> dict:
        return {
            "id": self.ident,
            "nickname": self.nickname,
            "profile": self.profile,
            "regular_weight": self.regular_weight,
            "color": self.color,
            "guid": self.guid,
            "gameplay_seed": self.gameplay_seed,
        }


@dataclass
class SessionRecord:
    ident: str
    server: str
    status: str = "OFFLINE"
    epoch: int = 0
    until: float = 0.0
    reason: str = ""
    last_event: str = ""
    client: Optional[int] = None
    slot: Optional[int] = None
    joins: int = 0
    leaves: int = 0
    crashes: int = 0
    disconnects: int = 0
    total_playing_s: float = 0.0
    _playing_since: Optional[float] = None

    def as_dict(self) -> dict:
        return {
            "id": self.ident,
            "server": self.server,
            "status": self.status,
            "epoch": self.epoch,
            "until": self.until,
            "reason": self.reason,
            "last_event": self.last_event,
            "client": self.client,
            "slot": self.slot,
            "joins": self.joins,
            "leaves": self.leaves,
            "crashes": self.crashes,
            "disconnects": self.disconnects,
            "total_playing_s": round(self.total_playing_s, 3),
        }


@dataclass
class Client:
    index: int
    slots: dict = field(default_factory=dict)  # slot -> ident
    running: bool = False
    empty_since: Optional[float] = None
    starts: int = 0
    restarts: int = 0


@dataclass
class SchedulerMetrics:
    peak_clients: int = 0
    client_starts: int = 0
    client_stops: int = 0
    client_restarts: int = 0
    joins_served: int = 0
    leaves_served: int = 0
    transient_peak_extra_clients: int = 0  # kurzzeitige +1 pro Restart-Fenster
    join_wait_s: list = field(default_factory=list)
    interrupted_bot_ticks: int = 0  # Co-Residenten unterbrochen (ROSTER_RESTART)
    timeline: list = field(default_factory=list)  # (t, running_clients)

    def snapshot(self, t: float, running: int) -> None:
        self.peak_clients = max(self.peak_clients, running)
        self.timeline.append((round(t, 3), running))

    def as_dict(self) -> dict:
        waits = sorted(self.join_wait_s)
        return {
            "peak_clients": self.peak_clients,
            "client_starts": self.client_starts,
            "client_stops": self.client_stops,
            "client_restarts": self.client_restarts,
            "joins_served": self.joins_served,
            "leaves_served": self.leaves_served,
            "join_wait_max_s": round(waits[-1], 3) if waits else 0.0,
            "join_wait_mean_s": round(sum(waits) / len(waits), 3) if waits else 0.0,
            "transient_peak_extra_clients": self.transient_peak_extra_clients,
            "co_resident_interruptions": self.interrupted_bot_ticks,
        }


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------
def clean_name(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("nickname must be text")
    value = re.sub(r"\^c[0-9a-fA-F]{6}|\^r", "", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9 ._\\[\\]-]", "", value)
    value = " ".join(value.split())[:VISIBLE_CAP].strip()
    if not value or not any(c.isalnum() for c in value):
        raise ValueError("empty visible nickname")
    return value


def make_guid(pool_id: str, seed: int, ident: str) -> str:
    """Stabiler UUIDv5-GUID: identisch bei Crash, Cooldown, Rejoin [O-A]."""
    data = pool_id + "/" + str(seed) + "/" + ident
    return uuid.uuid5(uuid.NAMESPACE_URL, data).hex


def make_gameplay_seed(seed: int, pool_id: str, ident: str, epoch: int) -> int:
    data = json.dumps([seed, pool_id, "gameplay", ident, epoch])
    return int.from_bytes(hashlib.sha256(data.encode()).digest()[:4], "big") % 2147483647 or 1


_VALID_KEYS = set(DEFAULT_CONFIG.keys())


def validate_config(config: dict) -> dict:
    if not isinstance(config, dict) or set(config) - _VALID_KEYS:
        raise ValueError("configuration must be an object with known keys")
    c = dict(DEFAULT_CONFIG)
    c.update(config)
    for key in ("enabled", "colors_enabled", "accelerated"):
        if type(c[key]) is not bool:
            raise ValueError(key + " must be boolean")
    if not isinstance(c.get("pool_id"), str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", c["pool_id"]):
        raise ValueError("pool_id required")
    if type(c.get("seed")) is not int or not 0 <= c.get("seed") < 2**63:
        raise ValueError("integer seed required")
    for key, low, high in (("max_bots", 0, 16), ("reserved_human_slots", 1, 16), ("min_bots", 0, 16)):
        if type(c[key]) is not int or not low <= c[key] <= high:
            raise ValueError("invalid " + key)
    if c["min_bots"] > c["max_bots"]:
        raise ValueError("min_bots may not exceed max_bots")
    for key in ("join_interval_s", "leave_interval_s"):
        if not (type(c[key]) in (int, float)) or c[key] < 1:
            raise ValueError("invalid " + key)
    for key, low in (("startup_delay_s", 0), ("pause_s", 1)):
        v = c[key]
        if (not isinstance(v, list) or len(v) != 2
                or any(type(x) is not int or x < low for x in v) or v[1] < v[0]):
            raise ValueError("invalid " + key)
    if type(c["connect_delay_s"]) not in (int, float) or c["connect_delay_s"] < 0:
        raise ValueError("invalid connect_delay_s")
    if type(c["client_start_s"]) not in (int, float) or c["client_start_s"] < 0:
        raise ValueError("invalid client_start_s")
    if type(c["batch_window_s"]) not in (int, float) or c["batch_window_s"] < 1:
        raise ValueError("invalid batch_window_s")
    if type(c["idle_stop_s"]) not in (int, float) or c["idle_stop_s"] < 1:
        raise ValueError("invalid idle_stop_s")
    if type(c["slots_per_client"]) is not int or not 1 <= c["slots_per_client"] <= 4:
        raise ValueError("slots_per_client must be 1..4 (Retail 4 lokale Spieler)")
    if type(c["max_clients"]) is not int or c["max_clients"] < 1:
        raise ValueError("invalid max_clients")
    bands = c["session_bands"]
    if not isinstance(bands, list) or not bands:
        raise ValueError("session_bands required")
    for band in bands:
        if (not isinstance(band, list) or len(band) != 3
                or not (type(band[0]) in (int, float)) or band[0] <= 0
                or any(type(x) is not int or x < 1 for x in band[1:])
                or band[2] < band[1]):
            raise ValueError("invalid session band")
    servers = c.get("servers")
    if (not isinstance(servers, list) or not servers
            or any(not isinstance(s, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", s) for s in servers)
            or len(set(servers)) != len(servers)):
        raise ValueError("unique server IDs required")
    pool = c.get("identities")
    if not isinstance(pool, list) or not pool or len(pool) > 1024:
        raise ValueError("identity pool required (1..1024)")
    ids, names = set(), set()
    for raw in pool:
        i = dict(raw)
        ident = i.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z0-9_-]{1,40}", ident) or ident in ids:
            raise ValueError("invalid or duplicate identity ID")
        i["nickname"] = clean_name(i.get("nickname"))
        key = i["nickname"].casefold()
        if key in names:
            raise ValueError("duplicate visible nickname")
        if type(i.get("profile")) is not int or not 0 <= i["profile"] < 8:
            raise ValueError("existing roster profile 0..7 required")
        i.setdefault("regular_weight", 1)
        if not (type(i["regular_weight"]) in (int, float)) or i["regular_weight"] <= 0 or i["regular_weight"] > 10:
            raise ValueError("invalid regular_weight")
        color = i.get("color")
        if color is not None and (not isinstance(color, str)
                                  or not re.fullmatch(r"[0-9A-Fa-f]{6}", color)):
            raise ValueError("invalid RGB color")
        if color:
            i["color"] = color.upper()
        ids.add(ident)
        names.add(key)
    c["identities"] = pool
    return c


# ---------------------------------------------------------------------------
# Session-Politik (gehegt auf PR #47: Identitaeten, Lifecycle, Epochen, min_bots)
# ---------------------------------------------------------------------------
class SessionPolicy:
    """Erzeugt idempotente Join/Leave-Absichten; startet selbst keine Spiele.

    Alle Controller teilen sich eine lokale SQLite-Datenbank. Absichten sind
    transaktional reserviert (JOINING/LEAVING) und epoche-geschuetzt.
    """

    def __init__(self, database: str, config: dict):
        self.config = validate_config(config)
        self.db = sqlite3.connect(database, timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        try:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS identity (
                    id TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS session (
                    id TEXT PRIMARY KEY REFERENCES identity(id), server TEXT NOT NULL,
                    status TEXT NOT NULL, until REAL NOT NULL DEFAULT 0,
                    epoch INTEGER NOT NULL DEFAULT 0, reason TEXT NOT NULL DEFAULT '',
                    last_event TEXT NOT NULL DEFAULT '');
                CREATE TABLE IF NOT EXISTS control (
                    server TEXT PRIMARY KEY, enabled INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS event (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT, epoch INTEGER,
                    event TEXT, reason TEXT, at REAL);
            """)
            with self._transaction():
                fingerprint = json.dumps({
                    k: self.config[k]
                    for k in ("pool_id", "seed", "identities", "max_bots", "min_bots",
                              "reserved_human_slots")
                }, sort_keys=True)
                previous = self._meta("pool", None)
                if previous is not None and previous != fingerprint:
                    raise ValueError("persisted identity pool differs; explicit migration required")
                self._put_meta("pool", fingerprint)
                for s in self.config["servers"]:
                    self.db.execute("INSERT OR IGNORE INTO control VALUES (?,1)", (s,))
                for i in self.config["identities"]:
                    ident = i["id"]
                    data = dict(i,
                                guid=make_guid(self.config["pool_id"], self.config["seed"], ident),
                                gameplay_seed=make_gameplay_seed(
                                    self.config["seed"], self.config["pool_id"], ident, 0))
                    self.db.execute("INSERT OR IGNORE INTO identity VALUES (?,?)",
                                    (ident, json.dumps(data, sort_keys=True)))
                    server = max(self.config["servers"],
                                 key=lambda s: random.Random(
                                     int.from_bytes(
                                         hashlib.sha256(
                                             json.dumps([self.config["seed"], self.config["pool_id"],
                                                         "server", s, ident]).encode()).digest()[:8],
                                         "big")
                                 ).random())
                    self.db.execute("INSERT OR IGNORE INTO session (id,server,status) "
                                    "VALUES (?,?,'OFFLINE')", (ident, server))
        except BaseException:
            self.db.close()
            raise

    def close(self) -> None:
        self.db.close()

    def _transaction(self):
        return _Txn(self.db)

    def _meta(self, key, default=0):
        r = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return json.loads(r[0]) if r else default

    def _put_meta(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO meta VALUES (?,?)",
                        (key, json.dumps(value)))

    def _seed(self, purpose: str, ident: str, epoch: int) -> int:
        data = json.dumps([self.config["seed"], self.config["pool_id"], purpose, ident, epoch])
        return int.from_bytes(hashlib.sha256(data.encode()).digest()[:8], "big")

    def _rng(self, purpose: str, ident: str, epoch: int) -> random.Random:
        return random.Random(self._seed(purpose, ident, epoch))

    def identities(self) -> list[Identity]:
        out = []
        for r in self.db.execute("SELECT data FROM identity ORDER BY id"):
            d = json.loads(r[0])
            out.append(Identity(d["id"], d["nickname"], d["profile"],
                                d.get("regular_weight", 1), d.get("color"),
                                d["guid"], d["gameplay_seed"]))
        return out

    def states(self) -> dict[str, dict]:
        return {r["id"]: dict(r) for r in
                self.db.execute("SELECT * FROM session ORDER BY id")}

    def clock(self, now: float) -> None:
        if not isinstance(now, (int, float)) or not math.isfinite(now):
            raise ValueError("invalid clock")
        last = self._meta("last_time", None)
        if last is not None and now < last:
            raise ValueError("backwards clock rejected")
        self._put_meta("last_time", now)

    def set_enabled(self, server: str, enabled: bool, now: float) -> None:
        if server not in self.config["servers"] or type(enabled) is not bool:
            raise ValueError("known server and boolean enabled required")
        with self._transaction():
            self.clock(now)
            self.db.execute("UPDATE control SET enabled=? WHERE server=?", (int(enabled), server))

    def _snapshot_ok(self, snapshot: Optional[dict], now: float):
        """Liefert (capacity, humans) oder None bei unbekannter Population."""
        if not isinstance(snapshot, dict):
            return None
        at, maximum, names = (snapshot.get(k) for k in
                              ("observed_at", "maxplayers", "human_names"))
        if (not isinstance(at, (int, float)) or not 0 <= now - at <= 15
                or type(maximum) is not int or not 1 <= maximum <= 16
                or not isinstance(names, list) or len(names) > maximum):
            return None
        try:
            keys = [clean_name(n).casefold() for n in names]
        except ValueError:
            return None
        if len(set(keys)) != len(keys):
            return None
        humans = set(keys)
        capacity = max(0, min(self.config["max_bots"],
                              maximum - self.config["reserved_human_slots"] - len(humans)))
        return capacity, humans

    def plan(self, server: str, snapshot: Optional[dict], now: float) -> list[dict]:
        """Idempotente Absichten fuer einen Server (transaktional, epoche-geschuetzt)."""
        if server not in self.config["servers"]:
            raise ValueError("unknown server")
        with self._transaction():
            self.clock(now)
            enabled = (self.config["enabled"]
                       and bool(self.db.execute(
                           "SELECT enabled FROM control WHERE server=?", (server,)).fetchone()[0]))
            all_rows = self.states()
            identities = {i.ident: i for i in self.identities()}
            rows = [r for r in all_rows.values() if r["server"] == server]
            for r in rows:
                if r["status"] == "COOLDOWN" and now >= r["until"]:
                    r["status"] = "OFFLINE"
                if not enabled and r["status"] in ("OFFLINE", "WAITING"):
                    r["status"] = "OFFLINE"
                elif enabled and r["status"] == "OFFLINE":
                    r["status"] = "WAITING"
                    r["until"] = now + self._rng("startup", r["id"], r["epoch"]).randint(
                        *self.config["startup_delay_s"])
                self.db.execute("UPDATE session SET status=?,until=? WHERE id=?",
                                (r["status"], r["until"], r["id"]))
            active = [r for r in rows if r["status"] in ACTIVE]
            observed = self._snapshot_ok(snapshot, now)
            capacity, humans = (0, set()) if observed is None else observed
            due = [r for r in active
                   if (not enabled
                       or (observed is not None and (len(active) > capacity
                                                     or identities[r["id"]].nickname.casefold() in humans))
                       or (r["status"] == "PLAYING" and now >= r["until"]
                           and sum(a["status"] == "PLAYING" for a in active)
                           > self.config["min_bots"]))
                   and r["status"] != "LEAVING"]
            actions: list[dict] = []
            if due and not any(r["status"] == "LEAVING" for r in all_rows.values()) \
                    and now >= self._meta("leave_at", 0):
                row = min(due, key=lambda r: (r["until"], r["id"]))
                reason = ("admin" if not enabled else
                          ("human_capacity" if observed is not None
                           and (len(active) > capacity
                                or identities[row["id"]].nickname.casefold() in humans)
                           else "planned"))
                actions.append(self._intent(row, "leave", reason, now))
                self._put_meta("leave_at", now + self.config["leave_interval_s"])
            if (not enabled or observed is None or len(active) >= capacity
                    or any(r["status"] == "JOINING" for r in all_rows.values())
                    or now < self._meta("join_at", 0)):
                return actions
            ready = [r for r in rows
                     if r["status"] == "WAITING" and now >= r["until"]
                     and identities[r["id"]].nickname.casefold() not in humans]
            if ready:
                seq = self._meta("join_sequence", 0)
                row = self._rng("selection", server, seq).choices(
                    ready,
                    weights=[identities[r["id"]].regular_weight for r in ready])[0]
                actions.append(self._intent(row, "join", "scheduled", now))
                delay = self._rng("join_gap", server, seq).triangular(
                    self.config["join_interval_s"],
                    self.config["join_interval_s"] * 3,
                    self.config["join_interval_s"])
                self._put_meta("join_at", now + delay)
                self._put_meta("join_sequence", seq + 1)
            return actions

    def _intent(self, row: dict, action: str, reason: str, now: float) -> dict:
        epoch = row["epoch"] + int(action == "join")
        status = "JOINING" if action == "join" else "LEAVING"
        self.db.execute(
            "UPDATE session SET status=?,epoch=?,reason=?,last_event=? WHERE id=?",
            (status, epoch, reason, action + "_requested", row["id"]))
        self.db.execute(
            "INSERT INTO event (id,epoch,event,reason,at) VALUES (?,?,?,?,?)",
            (row["id"], epoch, action + "_requested", reason, now))
        ident_row = self.db.execute(
            "SELECT data FROM identity WHERE id=?", (row["id"],)).fetchone()[0]
        identity = json.loads(ident_row)
        return dict(action=action, identity_id=row["id"], server=row["server"],
                    epoch=epoch, reason=reason, identity=identity)

    def record(self, ident: str, epoch: int, event: str, now: float) -> bool:
        """Bestaetigter externer Lebenszyklus-Event (joined/left/crashed/disconnected)."""
        if type(epoch) is not int or epoch < 1:
            raise ValueError("positive integer session epoch required")
        if event not in ("joined", "left", "crashed", "disconnected"):
            raise ValueError("unknown lifecycle event")
        with self._transaction():
            self.clock(now)
            row = self.db.execute("SELECT * FROM session WHERE id=?", (ident,)).fetchone()
            if row is None or row["epoch"] != epoch:
                return False
            expected = {"joined": ("JOINING",), "left": ("LEAVING",),
                        "crashed": ACTIVE, "disconnected": ACTIVE}[event]
            if row["status"] not in expected:
                return False
            if event == "joined":
                rng = self._rng("duration", ident, epoch)
                band = rng.choices(self.config["session_bands"],
                                   weights=[b[0] for b in self.config["session_bands"]])[0]
                status, until, reason = "PLAYING", now + rng.randint(band[1], band[2]), ""
            else:
                status = "COOLDOWN"
                until = now + self._rng("pause", ident, epoch).randint(*self.config["pause_s"])
                reason = row["reason"] if event == "left" and row["status"] == "LEAVING" else event
            self.db.execute(
                "UPDATE session SET status=?,until=?,reason=?,last_event=? WHERE id=?",
                (status, until, reason, event, ident))
            self.db.execute(
                "INSERT INTO event (id,epoch,event,reason,at) VALUES (?,?,?,?,?)",
                (ident, epoch, event, reason, now))
            return True


class _Txn:
    """Minimaler BEGIN IMMEDIATE-Wrapper um sqlite3-isolation_level=None."""

    def __init__(self, db):
        self.db = db

    def __enter__(self):
        self.db.execute("BEGIN IMMEDIATE")
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.db.execute("COMMIT")
        else:
            self.db.execute("ROLLBACK")
        return False


# ---------------------------------------------------------------------------
# Hybrid-Scheduler C1: ROSTER_RESTART auf 4-Slot-Clients
# ---------------------------------------------------------------------------
class HybridScheduler:
    """Unabhaengige Bot-Sessions multiplexen auf shared 4-Slot-Clients.

    ROSTER_RESTART (C1): Mitgliedschaftsanderungen sammeln sich im
    batch_window_s; der betroffene Client startet mit neuem Roster neu.
    Benutzt ausschliesslich bereits qualifizierte Primitive
    (Client-Start mit festem Roster, Stopp, persistente Identitaet/Reconnect).

    DYNAMIC_SLOT (C2): setzt E1/E2 voraus (mid-session AddPlayer /
    Spielerquelle-Entfernung auf bestehender Verbindung), das auf Retail 1.07
    nicht verifiziert ist – dieser Modus ist reine Planung und wird hier nicht
    als Fahigkeit behauptet.
    """

    def __init__(self, mode: str = ROSTER_RESTART, slots_per_client: int = 4,
                 max_clients: int = 4, idle_stop_s: float = 30.0,
                 batch_window_s: float = 20.0, client_start_s: float = 8.0):
        if mode not in (ROSTER_RESTART, DYNAMIC_SLOT):
            raise ValueError("unknown mode: %r" % mode)
        self.mode = mode
        self.slots_per_client = slots_per_client
        self.max_clients = max_clients
        self.idle_stop_s = idle_stop_s
        self.batch_window_s = batch_window_s
        self.client_start_s = client_start_s
        self.clients = [Client(i) for i in range(max_clients)]
        self.metrics = SchedulerMetrics()
        self.pending: list = []  # (join_time, ident)
        self.location: dict = {}  # ident -> (client_index, slot)
        self.batch: list = []  # ROSTER_RESTART: gepufferte Absichten
        self.batch_deadline: Optional[float] = None
        self.transient_extra_now: int = 0

    def _running(self) -> int:
        return sum(1 for c in self.clients if c.running)

    def _start(self, client: Client) -> None:
        client.running = True
        client.empty_since = None
        client.starts += 1
        self.metrics.client_starts += 1

    def _stop(self, client: Client) -> None:
        client.running = False
        client.empty_since = None

    def _free_slot(self, client: Client) -> Optional[int]:
        for s in range(self.slots_per_client):
            if s not in client.slots:
                return s
        return None

    def _place(self, t_event: float, t_now: float, ident: str) -> bool:
        """Platziere einen Bot auf dem dichtesten laufenden Client mit freiem Slot."""
        candidates = [c for c in self.clients if c.running
                      and self._free_slot(c) is not None]
        candidates.sort(key=lambda c: -len(c.slots))
        if not candidates:
            stopped = [c for c in self.clients if not c.running]
            if not stopped:
                return False  # Kapazitat erschopft -> Join wartet in der Warteschlange
            client = stopped[0]
            self._start(client)
            candidates = [client]
        client = candidates[0]
        slot = self._free_slot(client)
        client.slots[slot] = ident
        client.empty_since = None
        self.location[ident] = (client.index, slot)
        self.metrics.joins_served += 1
        self.metrics.join_wait_s.append(max(0.0, t_now - t_event))
        return True

    def _remove(self, ident: str) -> None:
        loc = self.location.pop(ident, None)
        if loc is None:
            return
        client = self.clients[loc[0]]
        client.slots.pop(loc[1], None)
        self.metrics.leaves_served += 1
        if not client.slots and client.running:
            client.empty_since = None  # wird im Reap-Schritt initialisiert

    def _reap_idle(self, t: float) -> None:
        for client in self.clients:
            if (client.running and not client.slots
                    and client.empty_since is not None
                    and t - client.empty_since >= self.idle_stop_s):
                self._stop(client)

    def _drain_pending(self, t: float) -> None:
        remaining = []
        for t_event, ident in self.pending:
            if not self._place(t_event, t, ident):
                remaining.append((t_event, ident))
        self.pending = remaining

    def add_intent(self, intent: dict, t_now: float) -> None:
        """Eine Session-Politik-Absicht in den Scheduler einspeisen."""
        event = {"time": t_now, "ident": intent["identity_id"],
                 "action": intent["action"], "reason": intent["reason"],
                 "epoch": intent["epoch"]}
        if self.mode == DYNAMIC_SLOT:
            if event["action"] == JOIN:
                if not self._place(t_now, t_now, event["ident"]):
                    self.pending.append((t_now, event["ident"]))
            else:
                self._remove(event["ident"])
        else:
            self.batch.append(event)
            if self.batch_deadline is None:
                self.batch_deadline = t_now + self.batch_window_s

    def _flush_batch(self, t: float) -> list:
        """Wende die gesammelte Charge an; betroffene Clients starten neu."""
        joins = [e for e in self.batch if e["action"] == JOIN]
        leaves = [e for e in self.batch if e["action"] == LEAVE]
        self.batch = []
        self.batch_deadline = None
        touched: set = set()
        restart_events: list = []
        for ev in leaves:
            loc = self.location.get(ev["ident"])
            if loc is not None:
                touched.add(loc[0])
            self._remove(ev["ident"])
        for ev in joins:
            before = {c.index: dict(c.slots) for c in self.clients}
            if self._place(ev["time"], t, ev["ident"]):
                cidx = self.location[ev["ident"]][0]
                if before.get(cidx):
                    touched.add(cidx)
            else:
                self.pending.append((ev["time"], ev["ident"]))
        # Transienter +1-Client pro Restart-Fenster (stop vor start konservativ)
        self.transient_extra_now = max(self.transient_extra_now, len(touched))
        for cidx in sorted(touched):
            client = self.clients[cidx]
            if client.running:
                client.restarts += 1
                self.metrics.client_restarts += 1
                self.metrics.interrupted_bot_ticks += len(client.slots)
                restart_events.append({
                    "client": cidx, "time": t, "slots": len(client.slots),
                    "idents": list(client.slots.values())})
        self.metrics.snapshot(t, self._running())
        return restart_events

    def step(self, t: float) -> dict:
        """Ein Simulationsschritt zur Zeit t; liefert Restart-Events."""
        if (self.mode == ROSTER_RESTART and self.batch_deadline is not None
                and t >= self.batch_deadline):
            self._flush_batch(t)
        self._reap_idle(t)
        self._drain_pending(t)
        for client in self.clients:
            if client.running and not client.slots and client.empty_since is None:
                client.empty_since = t
        self.metrics.snapshot(t, self._running())
        running = self._running()
        peak_total = running + self.transient_extra_now
        self.metrics.transient_peak_extra_clients = max(
            self.metrics.transient_peak_extra_clients, peak_total - running)
        return {"t": t, "running_clients": running,
                "transient_extra": self.transient_extra_now,
                "peak_clients": self.metrics.peak_clients}

    def flush_final(self, t: float) -> list:
        if self.mode == ROSTER_RESTART and self.batch:
            return self._flush_batch(self.batch_deadline or t)
        return []

    def summary(self) -> dict:
        out = self.metrics.as_dict()
        out["mode"] = self.mode
        out["slots_per_client"] = self.slots_per_client
        out["max_clients"] = self.max_clients
        out["estimated_peak_ram_mib_rss_basis"] = round(
            50.2 + (self.metrics.peak_clients + self.metrics.transient_peak_extra_clients) * 184.2, 1)
        out["ram_basis_note"] = ("DERIVED: 50.2 MiB Server + 184.2 MiB je Client "
                                 "(RSS, geteilte Seiten mehrfach gezahlt; PSS noch offen [N])")
        return out


# ---------------------------------------------------------------------------
# Ghost- / Recovery-Modell
# ---------------------------------------------------------------------------
@dataclass
class GhostRecord:
    ident: str
    epoch: int
    first_seen: float
    last_seen: float
    verified_absent: bool = False
    acknowledged: bool = False


class GhostRecovery:
    """Modelliert Ghost-Slots und Recovery nach Crash / Server-Neustart.

    Ein Ghost liegt vor, wenn die Server-Query einen Slot belegt meldet, aber
    kein zugeordneter laufender Client-Prozess mehr existiert. Die Identitaet
    darf erst nach 'verified_absence' (Query-Abwesenheit bestaetigt) wieder
    verwendet werden; Epochen schuetzen vor Doppelstart.
    """

    def __init__(self, verify_age_s: float = GHOST_VERIFY_AGE_S):
        self.verify_age_s = verify_age_s
        self.ghosts: dict = {}

    def observe(self, ident: str, epoch: int, t: float,
                query_has_player: bool, process_alive: bool) -> str:
        """Rueckgabe: 'healthy' | 'ghost' | 'cleared' | 'quarantine'."""
        g = self.ghosts.get(ident)
        if query_has_player and not process_alive:
            if g is None:
                self.ghosts[ident] = GhostRecord(ident, epoch, t, t)
            else:
                g.last_seen = t
            if g is not None and g.verified_absent:
                g.verified_absent = False
                g.acknowledged = False
            return "ghost"
        if query_has_player and process_alive:
            if g is not None and g.epoch == epoch and g.verified_absent:
                g.acknowledged = True
                return "cleared"
            if g is not None:
                del self.ghosts[ident]
            return "healthy"
        # kein Spieler in der Query
        if (g is not None and g.epoch == epoch
                and t - g.last_seen >= self.verify_age_s):
            g.verified_absent = True
            return "cleared" if g.acknowledged else "quarantine"
        return "healthy"

    def claim_reuse(self, ident: str, epoch: int, t: float) -> bool:
        """Slot darf wiederverwendet werden, nur wenn Ghost geklaert/abwesend.

        'verified_absent' heisst, die Query hat den Slot lange genug nicht
        mehr gemeldet. 'acknowledged' markiert den Sonderfall, dass der
        Prozess zurueckkam (geisterhafte Slot-Belegung geklaert).
        """
        g = self.ghosts.get(ident)
        if g is None or g.epoch != epoch:
            return True
        return bool(g.verified_absent)


# ---------------------------------------------------------------------------
# Simulations-Runner (komponiert Policy + Scheduler + Ghost-Recovery)
# ---------------------------------------------------------------------------
@dataclass
class SimResult:
    config: dict
    mode: str
    sessions: dict
    scheduler: SchedulerMetrics
    ghost_events: list
    timeline: list
    provenance: dict


class SimRunner:
    """Fuehrt einen Join/Leave-Trace durch Policy und Scheduler.

    Virtuelle Uhr, deterministisch. Jeder Bot behält seine Identitaet
    (GUID, Profil, Seed) ueber Crash, Cooldown und Rejoin hinweg.
    """

    def __init__(self, config: dict, mode: str = ROSTER_RESTART,
                 database: str = ":memory:", seed_offset: int = 0):
        self.config = validate_config(config)
        self.mode = mode
        self.database = database
        self.policy = SessionPolicy(database, self.config)
        self.scheduler = HybridScheduler(
            mode=mode,
            slots_per_client=self.config["slots_per_client"],
            max_clients=self.config["max_clients"],
            idle_stop_s=self.config["idle_stop_s"],
            batch_window_s=self.config["batch_window_s"],
            client_start_s=self.config["client_start_s"])
        self.ghosts = GhostRecovery()
        self.sessions: dict = {
            i.ident: SessionRecord(i.ident, self._assign_server(i.ident))
            for i in self.policy.identities()}
        self._identities = {i.ident: i for i in self.policy.identities()}
        self.now = 0.0
        self.ghost_events: list = []
        self.timeline: list = []
        self._placed_at: dict = {}  # ident -> Zeit der Scheduler-Platzierung
        self.rng_trace = random.Random(self.config["seed"] + 1000003 + seed_offset)

    def _assign_server(self, ident: str) -> str:
        servers = self.config["servers"]
        h = int.from_bytes(hashlib.sha256(
            json.dumps([self.config["seed"], self.config["pool_id"], ident]).encode()).digest()[:4], "big")
        return servers[h % len(servers)]

    def run_trace(self, events: list, end_time: Optional[float] = None) -> SimResult:
        """events: Liste von {t, ident, action}; actions JOIN|LEAVE|CRASH|RESTART_SERVER|REJOIN.

        Virtuelle Uhr. Jeder Simulationsschritt: Scheduler-Flush/Platzierung,
        Platzierungs-Sync in die Session-Status (mit Connect-Verzoegerung),
        Ghost-Beobachtung, dann Trace-Ereignisse zu dieser Zeit.
        """
        evts = sorted(events, key=lambda e: (e["t"], 0 if e["action"] != "JOIN" else 1))
        t_end = end_time or (max((e["t"] for e in evts), default=0.0) + 300.0)
        cursor = 0
        while self.now <= t_end:
            next_t = t_end
            if cursor < len(evts):
                next_t = min(next_t, evts[cursor]["t"])
            self.now = next_t
            self.scheduler.step(self.now)
            self._sync_placements(self.now)
            for ident, sess in self.sessions.items():
                alive = (sess.client is not None
                         and self.scheduler.clients[sess.client].running)
                query_has = sess.status == "PLAYING"
                verdict = self.ghosts.observe(ident, sess.epoch, self.now,
                                              query_has, alive)
                if verdict == "ghost":
                    self.ghost_events.append({
                        "t": self.now, "ident": ident, "epoch": sess.epoch,
                        "verdict": "ghost"})
                elif verdict == "cleared":
                    self.ghost_events.append({
                        "t": self.now, "ident": ident, "epoch": sess.epoch,
                        "verdict": "ghost_cleared"})
            while cursor < len(evts) and evts[cursor]["t"] <= self.now:
                self._apply_event(evts[cursor])
                cursor += 1
            if cursor >= len(evts):
                break
        self.scheduler.flush_final(self.now)
        final_t = self.now + self.config["idle_stop_s"] + 1.0
        self.scheduler.step(final_t)
        self._sync_placements(final_t + self.config["connect_delay_s"])
        return self._result()

    def _sync_placements(self, now: float) -> None:
        """Schreibt Scheduler-Platzierungen in die Session-Records zurueck.

        JOINING -> PLAYING nach modellierter Connect-Verzoegerung
        (client_start_s). LEAVING -> COOLDOWN sobald der Slot im Scheduler
        freigegeben ist (modellierte Query-Abwesenheit bestaetigt).
        """
        for ident, sess in self.sessions.items():
            placed = ident in self.scheduler.location
            if sess.status == "JOINING" and placed:
                # Erstmalig gesehene Platzierung gilt als connect_delay
                # her (Flush vor dem Sync); uebere Place-Zeit gesetzt.
                if ident not in self._placed_at:
                    self._placed_at[ident] = now - self.config["connect_delay_s"]
                if now >= self._placed_at[ident] + self.config["connect_delay_s"]:
                    cidx, slot = self.scheduler.location[ident]
                    sess.status = "PLAYING"
                    sess.client = cidx
                    sess.slot = slot
                    sess._playing_since = now
                    sess.last_event = "joined"
                    self.timeline.append({
                        "t": now, "ident": ident, "action": "JOINED",
                        "epoch": sess.epoch, "client": cidx, "slot": slot})
            elif sess.status == "LEAVING" and not placed:
                if sess.status == "PLAYING":
                    sess.total_playing_s += max(0.0, now - (sess._playing_since or now))
                sess.status = "COOLDOWN"
                sess.leaves += 1
                sess.last_event = "left"
                self.timeline.append({
                    "t": now, "ident": ident, "action": "LEFT",
                    "epoch": sess.epoch})

    def _apply_event(self, ev: dict) -> None:
        action = ev["action"]
        ident = ev["ident"]
        t = self.now
        if action == "RESTART_SERVER":
            for s in self.sessions.values():
                if s.status == "PLAYING":
                    if s._playing_since is not None:
                        s.total_playing_s += max(0.0, t - s._playing_since)
                    s.status = "COOLDOWN"
                    s.disconnects += 1
                    s.last_event = "server_restart_disconnect"
                    self.scheduler._remove(s.ident)
                    self.ghost_events.append({
                        "t": t, "ident": s.ident, "epoch": s.epoch,
                        "verdict": "server_restart_ghost"})
            self.timeline.append({"t": t, "action": "SERVER_RESTART",
                                  "clients_stopped": self.scheduler.metrics.client_starts})
            return
        sess = self.sessions[ident]
        ident_obj = self._identities[ident]
        if action == JOIN:
            intent = dict(action=JOIN, identity_id=ident, server=sess.server,
                          epoch=sess.epoch + 1, reason="trace",
                          identity=ident_obj.as_dict())
            self.scheduler.add_intent(intent, t)
            sess.status = "JOINING"
            sess.epoch += 1
            sess.client = None
            sess.slot = None
            sess.joins += 1
            sess.last_event = "join_requested"
            self.timeline.append({
                "t": t, "ident": ident, "action": "JOIN_REQUESTED",
                "epoch": sess.epoch, "client": None})
        elif action == LEAVE:
            intent = dict(action=LEAVE, identity_id=ident, server=sess.server,
                          epoch=sess.epoch, reason="trace",
                          identity=ident_obj.as_dict())
            self.scheduler.add_intent(intent, t)
            if sess.status == "PLAYING":
                sess.total_playing_s += max(0.0, t - (sess._playing_since or t))
            sess.status = "LEAVING"
            sess.reason = "planned"
            sess.last_event = "leave_requested"
            self.timeline.append({
                "t": t, "ident": ident, "action": "LEAVE_REQUESTED",
                "epoch": sess.epoch})
        elif action == "CRASH":
            if sess.status in ACTIVE:
                if sess.status == "PLAYING":
                    sess.total_playing_s += max(0.0, t - (sess._playing_since or t))
                sess.status = "COOLDOWN"
                sess.crashes += 1
                sess.last_event = "crashed"
                self.timeline.append({
                    "t": t, "ident": ident, "action": "CRASH",
                    "epoch": sess.epoch})
                self.scheduler._remove(ident)
        elif action == "REJOIN":
            if sess.status in ("COOLDOWN", "OFFLINE", "LEAVING") and \
                    self.ghosts.claim_reuse(ident, sess.epoch, t):
                intent = dict(action=JOIN, identity_id=ident, server=sess.server,
                              epoch=sess.epoch + 1, reason="rejoin",
                              identity=ident_obj.as_dict())
                self.scheduler.add_intent(intent, t)
                sess.status = "JOINING"
                sess.epoch += 1
                sess.client = None
                sess.slot = None
                sess.joins += 1
                sess.last_event = "rejoin_requested"

    def _result(self) -> SimResult:
        return SimResult(
            config=self.config, mode=self.mode,
            sessions=self.sessions, scheduler=self.scheduler,
            ghost_events=self.ghost_events, timeline=self.timeline,
            provenance={
                "generated_by": "session_hybrid_lab.SimRunner",
                "schema": "offline-fixture",
                "wine_used": False,
                "retail_binary_used": False,
                "evidence": O,
            })

    # -- Komfort-Trace-Generatoren ------------------------------------------
    def random_trace(self, duration_s: float, join_rate_per_hour: float,
                     bots: Optional[list] = None) -> list:
        """Zufalliger Join/Leave-Trace (Poisson-Joins, Band-Sessiondauern).

        Reine Simulation [O]; keinerlei Retail-Messung.
        """
        bots = bots or [i.ident for i in self._identities.values()]
        events: list = []
        t = 0.0
        active_bots = {}
        while t < duration_s:
            gap = self.rng_trace.expovariate(join_rate_per_hour / 3600.0)
            t += gap
            if t >= duration_s:
                break
            idle = [b for b in bots if b not in active_bots]
            if not idle:
                continue
            ident = self.rng_trace.choice(idle)
            band = self.rng_trace.choices(
                self.config["session_bands"],
                weights=[b[0] for b in self.config["session_bands"]])[0]
            end = t + self.rng_trace.randint(band[1], band[2])
            events.append({"t": round(t, 3), "ident": ident, "action": JOIN})
            events.append({"t": round(min(end, duration_s), 3), "ident": ident, "action": LEAVE})
            active_bots[ident] = end
        events.sort(key=lambda e: e["t"])
        return events

    def ordered_join_trace(self, bots: list, interval_s: float = 60.0,
                           start_at: float = 0.0) -> list:
        """Geordnete Joins (z. B. 4 Bots in einer Clientgruppe, 8 in zwei)."""
        return [{"t": round(start_at + i * interval_s, 3),
                 "ident": b, "action": JOIN} for i, b in enumerate(bots)]

    def crash_cooldown_rejoin_trace(self, ident: str, join_at: float = 10.0,
                                    crash_at: float = 40.0, rejoin_at: float = 200.0
                                    ) -> list:
        """Crash + Cooldown + Rejoin mit stabiler Identitaet."""
        return [
            {"t": join_at, "ident": ident, "action": JOIN},
            {"t": crash_at, "ident": ident, "action": "CRASH"},
            {"t": rejoin_at, "ident": ident, "action": "REJOIN"},
        ]

    def server_restart_trace(self, bots: list, join_interval: float = 30.0,
                             restart_at: float = 300.0, rejoin_delay: float = 60.0
                             ) -> list:
        """Alle Bots joinen, Server-Neustart (trennt alle PLAYING), dann Rejoin
        mit stabiler Identitaet. RESTART_SERVER entkoppelt die Sessions; keine
        eigenen LEAVE-Events noetig."""
        events = self.ordered_join_trace(bots, join_interval)
        events.append({"t": restart_at, "ident": "__server__", "action": "RESTART_SERVER"})
        for i, b in enumerate(bots):
            events.append({"t": restart_at + rejoin_delay + i * 10.0, "ident": b,
                           "action": "REJOIN"})
        events.sort(key=lambda e: e["t"])
        return events

    def save_ledger(self, path: str | Path, result: SimResult) -> None:
        """Reproduzierbares Protokoll aller Sessions und Ereignisse (JSON)."""
        payload = {
            "config": result.config,
            "mode": result.mode,
            "provenance": result.provenance,
            "scheduler": result.scheduler.as_dict(),
            "sessions": {k: v.as_dict() for k, v in result.sessions.items()},
            "ghost_events": result.ghost_events,
            "timeline": result.timeline,
        }
        Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_arg_parser():
    import argparse
    p = argparse.ArgumentParser(
        description="Session-Hybrid-Lab: hybride Bot-Sessions auf Viererclients (offline).")
    p.add_argument("trace", nargs="?", help="Trace-Datei (JSON-Liste von {t,ident,action})")
    p.add_argument("--mode", choices=(ROSTER_RESTART, DYNAMIC_SLOT), default=ROSTER_RESTART)
    p.add_argument("--bots", type=int, default=8,
                   help="Anzahl Bots fuer generierten Ordered-Join-Trace")
    p.add_argument("--interval", type=float, default=60.0,
                   help="Sekunden zwischen geordneten Joins")
    p.add_argument("--duration", type=float, default=1800.0,
                   help="Simulationsdauer fuer Zufalls-Trace")
    p.add_argument("--random", action="store_true",
                   help="zufalliger Join/Leave-Trace statt geordneter Joins")
    p.add_argument("--seed", type=int, default=20261025)
    p.add_argument("--max-bots", type=int, default=8)
    p.add_argument("--min-bots", type=int, default=0)
    p.add_argument("--reserved-human-slots", type=int, default=2)
    p.add_argument("--max-clients", type=int, default=4)
    p.add_argument("--batch-window", type=float, default=20.0)
    p.add_argument("--out", default="-", help="Ausgabe-Datei (JSON) oder '-' für stdout")
    p.add_argument("--ledger", default=None, help="Detailliertes Sitzungsprotokoll (JSON)")
    return p


def main(argv=None) -> int:
    args = _build_arg_parser().parse_args(argv)
    config = dict(DEFAULT_CONFIG)
    config.update(seed=args.seed, max_bots=args.max_bots, min_bots=args.min_bots,
                  reserved_human_slots=args.reserved_human_slots,
                  max_clients=args.max_clients,
                  batch_window_s=args.batch_window,
                  pool_id="session-hybrid-lab-v1",
                  identities=[
                      {"id": f"player-{i:02d}", "nickname": f"Bot{i:02d}",
                       "profile": i % 8, "regular_weight": 3 if i < 4 else 1}
                      for i in range(1, 33)])
    runner = SimRunner(config, mode=args.mode, seed_offset=args.seed)
    if args.trace:
        events = json.loads(Path(args.trace).read_text(encoding="utf-8"))
    elif args.random:
        events = runner.random_trace(args.duration,
                                     join_rate_per_hour=(args.max_bots * 6.0))
    else:
        events = runner.ordered_join_trace(
            [f"player-{i:02d}" for i in range(1, args.bots + 1)],
            interval_s=args.interval)
    result = runner.run_trace(events)
    out = {
        "config": {k: v for k, v in result.config.items() if k != "identities"},
        "mode": result.mode,
        "provenance": result.provenance,
        "scheduler": result.scheduler.summary(),
        "summary": {
            "bots_requested": args.bots if not args.trace else None,
            "sessions": {k: v.as_dict() for k, v in result.sessions.items()},
            "ghost_events": result.ghost_events,
        },
    }
    text = json.dumps(out, indent=2, sort_keys=True)
    if args.out == "-":
        print(text)
    else:
        Path(args.out).write_text(text, encoding="utf-8")
    if args.ledger:
        runner.save_ledger(args.ledger, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
