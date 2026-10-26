#!/usr/bin/env python3
"""Persistent, engine-free session policy. Emits intents; never starts or stops games.

All controllers must share one local SQLite database. The unqualified runtime
adapter must reconcile an intent by identity/epoch before acknowledging it.
"""
from contextlib import contextmanager
import hashlib
import json
import math
import random
import re
import sqlite3
import unicodedata
import uuid
from gaming_names import VISIBLE_CAP as NATIVE_VISIBLE_CAP, validate_native

# Keep query normalization at its previous bound: shortening a human name to
# the owned 22-character cap could invent a collision. Bot admission below uses
# the shared native cap and rejects excess input instead of truncating it.
VISIBLE_CAP = 24
DEFAULT_BANDS = [[0.15, 300, 900], [0.55, 900, 2700], [0.25, 2700, 5400], [0.05, 5400, 9000]]
ACTIVE = ("JOINING", "PLAYING", "LEAVING")
DECORATION = re.compile(r'\^c[0-9a-fA-F]{6}|\^f[0-9]|\^[biIBFr]')


def clean_name(value):
    if not isinstance(value, str):
        raise ValueError("nickname must be text")
    # Candidate decoration grammar; colors remain gated until native verification.
    value = DECORATION.sub('', value)
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[^A-Za-z0-9 ._\[\]-]", "", value)
    value = " ".join(value.split())[:VISIBLE_CAP].strip()
    if not value or not any(c.isalnum() for c in value):
        raise ValueError("empty visible nickname")
    return value


def number(value, minimum=0):
    return type(value) in (int, float) and math.isfinite(value) and value >= minimum


def validate_config(config):
    allowed = {"enabled", "colors_enabled", "accelerated", "max_bots", "pool_id", "seed",
               "reserved_human_slots", "join_interval_s", "leave_interval_s",
               "startup_delay_s", "pause_s", "session_bands", "servers", "identities", "min_bots",
               "debug_logging", "log_every_ticks", "max_log_mib", "low_memory_rendering", "exploratory_search", "strafe_scale"}
    if not isinstance(config, dict) or set(config) - allowed:
        raise ValueError("configuration must be an object with known keys")
    c = dict(config)
    c.setdefault("enabled", False)
    c.setdefault("colors_enabled", False)
    c.setdefault("accelerated", False)
    c.setdefault("max_bots", 8)
    c.setdefault("min_bots", 0)
    c.setdefault('debug_logging', False)
    c.setdefault('log_every_ticks', 20)
    c.setdefault('max_log_mib', 32)
    c.setdefault('low_memory_rendering', False)
    c.setdefault('exploratory_search', False)
    c.setdefault('strafe_scale', 0.0)
    if not number(c['strafe_scale']) or c['strafe_scale']>1:
        raise ValueError('strafe_scale must be a finite number in 0..1')
    c.setdefault("reserved_human_slots", 2)
    c.setdefault("join_interval_s", 60)
    c.setdefault("leave_interval_s", 15)
    c.setdefault("startup_delay_s", [10, 180])
    c.setdefault("pause_s", [900, 7200])
    c.setdefault("session_bands", DEFAULT_BANDS)
    for key in ("enabled", "colors_enabled", "accelerated", "debug_logging", "low_memory_rendering", "exploratory_search"):
        if type(c[key]) is not bool:
            raise ValueError(key + " must be boolean")
    for key,high in [('log_every_ticks',1200),('max_log_mib',128)]:
        if type(c[key]) is not int or not 1<=c[key]<=high:raise ValueError('invalid '+key)
    if not isinstance(c.get("pool_id"), str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", c["pool_id"]):
        raise ValueError("pool_id required")
    if type(c.get("seed")) is not int or not 0 <= c["seed"] < 2**63:
        raise ValueError("integer seed required")
    for key, low, high in (("max_bots", 0, 16), ("reserved_human_slots", 1, 16)):
        if type(c[key]) is not int or not low <= c[key] <= high:
            raise ValueError("invalid " + key)
    if type(c['min_bots']) is not int or not 0 <= c['min_bots'] <= c['max_bots']:
        raise ValueError('invalid min_bots')
    for key in ("join_interval_s", "leave_interval_s"):
        if not number(c[key], 1):
            raise ValueError("invalid " + key)
    for key, low in (("startup_delay_s", 0), ("pause_s", 1)):
        v = c[key]
        if not isinstance(v, list) or len(v) != 2 or any(type(x) is not int or x < low for x in v) or v[1] < v[0]:
            raise ValueError("invalid " + key)
    bands = c["session_bands"]
    if not isinstance(bands, list) or not bands:
        raise ValueError("session_bands required")
    for band in bands:
        if not isinstance(band, list) or len(band) != 3 or not number(band[0], 0.000001) or band[0] > 1000000 or any(type(x) is not int or x < 1 for x in band[1:]) or band[2] < band[1]:
            raise ValueError("invalid session band")
    if not c["accelerated"] and (c["pause_s"][0] < 900 or min(x[1] for x in bands) < 300):
        raise ValueError("short test timings require accelerated=true")
    servers = c.get("servers")
    if not isinstance(servers, list) or not servers or any(not isinstance(s, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", s) for s in servers) or len(set(servers)) != len(servers):
        raise ValueError("unique server IDs required")
    pool = c.get("identities")
    if not isinstance(pool, list) or not pool or len(pool) > 1024:
        raise ValueError("identity pool required (1..1024)")
    ids, names, normalized = set(), set(), []
    for raw in pool:
        i = dict(raw)
        ident = i.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[a-z0-9_-]{1,40}", ident) or ident in ids:
            raise ValueError("invalid or duplicate identity ID")
        i["nickname"] = clean_name(i.get("nickname"))
        if len(i['nickname']) > NATIVE_VISIBLE_CAP:
            raise ValueError('native nickname exceeds 22-visible-character policy cap')
        if 'native_name' in i and validate_native(i['native_name']) != i['nickname']:
            raise ValueError('native name must match the stable visible identity')
        if 'session_bands' in i or 'pause_s' in i:
            # Reuse the global validation contract, including the accelerated gate.
            timing = dict(c, identities=[dict(id='timing', nickname='Timing', profile=0)])
            for field in ('session_bands', 'pause_s'):
                if field in i: timing[field] = i[field]
            validate_config(timing)
        if 'active_hours_utc' in i:
            hours = i['active_hours_utc']
            if (not isinstance(hours, list) or not hours or
                    any(type(h) is not int or not 0 <= h <= 23 for h in hours) or
                    len(hours) != len(set(hours))):
                raise ValueError('active_hours_utc must contain unique UTC hours 0..23')
        key = i["nickname"].casefold()
        if key in names:
            raise ValueError("duplicate visible nickname")
        if type(i.get("profile")) is not int or not 0 <= i["profile"] < 8:
            raise ValueError("existing roster profile 0..7 required")
        i.setdefault("regular_weight", 1)
        if not number(i["regular_weight"], 0.01) or i["regular_weight"] > 10:
            raise ValueError("invalid regular_weight")
        color = i.get("color")
        if color is not None and (not isinstance(color, str) or not re.fullmatch(r"[0-9A-Fa-f]{6}", color)):
            raise ValueError("invalid RGB color")
        if color:
            i["color"] = color.upper()
            if c['colors_enabled'] and len(i['nickname'])+10>32:
                raise ValueError('decorated native name exceeds qualified 32-byte policy cap')
        ids.add(ident); names.add(key); normalized.append(i)
    c["identities"] = normalized
    return c


class Planner:
    def __init__(self, database, config):
        self.config = validate_config(config)
        self.db = sqlite3.connect(database, timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        try:
            self.db.executescript("""
                CREATE TABLE IF NOT EXISTS identity (id TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS session (
                    id TEXT PRIMARY KEY REFERENCES identity(id), server TEXT NOT NULL,
                    status TEXT NOT NULL, until REAL NOT NULL DEFAULT 0,
                    epoch INTEGER NOT NULL DEFAULT 0, reason TEXT NOT NULL DEFAULT '',
                    last_event TEXT NOT NULL DEFAULT '');
                CREATE TABLE IF NOT EXISTS control (server TEXT PRIMARY KEY, enabled INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS event (
                    sequence INTEGER PRIMARY KEY, id TEXT, epoch INTEGER, event TEXT,
                    reason TEXT, at REAL);
            """)
            with self.transaction():
                fingerprint = json.dumps({k: self.config[k] for k in ("pool_id", "seed", "identities")}, sort_keys=True)
                previous = self.meta("pool", None)
                if previous is not None and previous != fingerprint:
                    raise ValueError("persisted identity pool differs; explicit migration required")
                self.put_meta("pool", fingerprint)
                if any(r["server"] not in self.config["servers"] for r in self.db.execute("SELECT server FROM session")):
                    raise ValueError("persisted server assignment missing from configuration")
                for i in self.config["identities"]:
                    ident = i["id"]
                    data = dict(i, guid=uuid.uuid5(uuid.NAMESPACE_URL, self.config["pool_id"] + "/" + str(self.config["seed"]) + "/" + ident).hex,
                                gameplay_seed=self.seed("gameplay", ident, 0) % 2147483647 or 1)
                    self.db.execute("INSERT OR IGNORE INTO identity VALUES (?,?)", (ident, json.dumps(data, sort_keys=True)))
                    server = max(self.config["servers"], key=lambda s: self.seed("server/" + s, ident, 0))
                    self.db.execute("INSERT OR IGNORE INTO session (id,server,status) VALUES (?,?,'OFFLINE')", (ident, server))
                for s in self.config["servers"]:
                    self.db.execute("INSERT OR IGNORE INTO control VALUES (?,1)", (s,))
        except BaseException:
            self.db.close()
            raise

    def close(self):
        self.db.close()

    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def meta(self, key, default=0):
        r = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return json.loads(r[0]) if r else default

    def put_meta(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO meta VALUES (?,?)", (key, json.dumps(value)))

    def seed(self, purpose, ident, epoch):
        data = json.dumps([self.config["seed"], self.config["pool_id"], purpose, ident, epoch])
        return int.from_bytes(hashlib.sha256(data.encode()).digest()[:8], "big")

    def rng(self, purpose, ident, epoch):
        return random.Random(self.seed(purpose, ident, epoch))

    def identities(self):
        return [json.loads(r[0]) for r in self.db.execute("SELECT data FROM identity ORDER BY id")]

    def states(self):
        return {r["id"]: dict(r) for r in self.db.execute("SELECT * FROM session ORDER BY id")}

    def clock(self, now):
        if not number(now) or now < self.meta("last_time"):
            raise ValueError("invalid or backwards clock")
        self.put_meta("last_time", now)

    def set_enabled(self, server, enabled, now):
        if server not in self.config["servers"] or type(enabled) is not bool:
            raise ValueError("known server and boolean enabled required")
        with self.transaction():
            self.clock(now)
            self.db.execute("UPDATE control SET enabled=? WHERE server=?", (int(enabled), server))

    def snapshot(self, snapshot, now):
        if not isinstance(snapshot, dict):
            return None
        at, maximum, names = (snapshot.get(k) for k in ("observed_at", "maxplayers", "human_names"))
        if not number(at) or not 0 <= now - at <= 15 or type(maximum) is not int or not 1 <= maximum <= 16 or not isinstance(names, list) or len(names) > maximum:
            return None
        try:
            # Raw human markup outside the earlier color qualification still
            # holds admission. clean_name separately prevents visible aliases.
            if any(not isinstance(n, str) or "^" in re.sub(r"\^c[0-9a-fA-F]{6}|\^r", "", n) for n in names):
                return None
            keys = [clean_name(n).casefold() for n in names]
        except ValueError:
            return None
        return (maximum, keys) if len(set(keys)) == len(keys) else None

    def intent(self, row, action, reason, now):
        epoch = row["epoch"] + int(action == "join")
        status = "JOINING" if action == "join" else "LEAVING"
        self.db.execute("UPDATE session SET status=?,epoch=?,reason=?,last_event=? WHERE id=?",
                        (status, epoch, reason, action + "_requested", row["id"]))
        self.db.execute("INSERT INTO event (id,epoch,event,reason,at) VALUES (?,?,?,?,?)",
                        (row["id"], epoch, action + "_requested", reason, now))
        identity = json.loads(self.db.execute("SELECT data FROM identity WHERE id=?", (row["id"],)).fetchone()[0])
        return dict(action=action, identity_id=row["id"], server=row["server"], epoch=epoch, reason=reason, identity=identity)

    def plan(self, server, snapshot, now):
        if server not in self.config["servers"]:
            raise ValueError("unknown server")
        with self.transaction():
            self.clock(now)
            enabled = self.config["enabled"] and bool(self.db.execute("SELECT enabled FROM control WHERE server=?", (server,)).fetchone()[0])
            all_rows = self.states()
            identities = {i["id"]: i for i in self.identities()}
            rows = [r for r in all_rows.values() if r["server"] == server]
            for r in rows:
                if r["status"] == "COOLDOWN" and now >= r["until"]:
                    r["status"] = "OFFLINE"
                if not enabled and r["status"] in ("OFFLINE", "WAITING"):
                    r["status"] = "OFFLINE"
                elif enabled and r["status"] == "OFFLINE":
                    r["status"] = "WAITING"
                    r["until"] = now + self.rng("startup", r["id"], r["epoch"]).randint(*self.config["startup_delay_s"])
                self.db.execute("UPDATE session SET status=?,until=? WHERE id=?", (r["status"], r["until"], r["id"]))
            active = [r for r in rows if r["status"] in ACTIVE]
            observed = self.snapshot(snapshot, now)
            capacity, humans = (0, []) if observed is None else (max(0, min(self.config["max_bots"], observed[0] - self.config["reserved_human_slots"] - len(observed[1]))), observed[1])
            # Unknown population blocks joins, but never overrides an own planned/admin leave.
            due = [r for r in active if (not enabled or
                   (observed is not None and (len(active) > capacity or identities[r["id"]]["nickname"].casefold() in humans)) or
                   (r["status"] == "PLAYING" and now >= r["until"] and
                    sum(a['status'] == 'PLAYING' for a in active) > self.config['min_bots']))
                   and r["status"] != "LEAVING"]
            actions = []
            if due and not any(r["status"] == "LEAVING" for r in all_rows.values()) and now >= self.meta("leave_at"):
                row = min(due, key=lambda r: (r["until"], r["id"]))
                reason = "admin" if not enabled else ("human_capacity" if observed is not None and
                         (len(active) > capacity or identities[row["id"]]["nickname"].casefold() in humans) else "planned")
                actions.append(self.intent(row, "leave", reason, now))
                self.put_meta("leave_at", now + self.config["leave_interval_s"])
            if not enabled or observed is None or len(active) >= capacity or any(r["status"] == "JOINING" for r in all_rows.values()) or now < self.meta("join_at"):
                return actions
            ready = [r for r in rows if r["status"] == "WAITING" and now >= r["until"] and
                     identities[r["id"]]["nickname"].casefold() not in humans and
                     int(now//3600)%24 in identities[r['id']].get('active_hours_utc', range(24))]
            if ready:
                seq = self.meta("join_sequence")
                row = self.rng("selection", server, seq).choices(ready, weights=[identities[r["id"]]["regular_weight"] for r in ready])[0]
                actions.append(self.intent(row, "join", "scheduled", now))
                delay = self.rng("join_gap", server, seq).triangular(self.config["join_interval_s"], self.config["join_interval_s"] * 3, self.config["join_interval_s"])
                self.put_meta("join_at", now + delay)
                self.put_meta("join_sequence", seq + 1)
            return actions

    def record(self, ident, epoch, event, now):
        if type(epoch) is not int or epoch < 1:
            raise ValueError("positive integer session epoch required")
        if event not in ("joined", "left", "crashed", "disconnected"):
            raise ValueError("unknown lifecycle event")
        with self.transaction():
            self.clock(now)
            row = self.db.execute("SELECT * FROM session WHERE id=?", (ident,)).fetchone()
            if row is None or row["epoch"] != epoch:
                return False
            expected = {"joined": ("JOINING",), "left": ("LEAVING",),
                        "crashed": ACTIVE, "disconnected": ACTIVE}[event]
            if row["status"] not in expected:
                return False
            if event == "joined":
                rng = self.rng("duration", ident, epoch)
                bands = next(i for i in self.identities() if i['id']==ident).get('session_bands', self.config['session_bands'])
                band = rng.choices(bands, weights=[b[0] for b in bands])[0]
                status, until, reason = "PLAYING", now + rng.randint(band[1], band[2]), ""
            else:
                status = "COOLDOWN"
                pause = next(i for i in self.identities() if i['id']==ident).get('pause_s', self.config['pause_s'])
                until = now + self.rng("pause", ident, epoch).randint(*pause)
                reason = row["reason"] if event == 'left' and row["status"] == "LEAVING" else event
            self.db.execute("UPDATE session SET status=?,until=?,reason=?,last_event=? WHERE id=?", (status, until, reason, event, ident))
            self.db.execute("INSERT INTO event (id,epoch,event,reason,at) VALUES (?,?,?,?,?)", (ident, epoch, event, reason, now))
            return True
