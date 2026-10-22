#!/usr/bin/env python3
"""Fail-closed, *offline* adapter primitives for future Retail 1.07 one-player clients.

No game start/kill, writes to retail profiles, or supervisor operations occur here.
Native profile layout is specific to the observed PLC4 fixture and must be
requalified before an on-disk overlay is ever written.
"""
import fcntl
import os
from pathlib import Path
import re
import sqlite3
import stat
import struct
import uuid

from bot_sessions import VISIBLE_CAP

MAX_TEMPLATE_BYTES = 4096
GUID_BYTES = 16


def _identity(identity):
    if not isinstance(identity, dict):
        raise ValueError("identity object required")
    name = identity.get("nickname")
    if (not isinstance(name, str) or not 1 <= len(name) <= VISIBLE_CAP
            or not re.fullmatch(r"[A-Za-z0-9 ._\[\]-]+", name)
            or name.strip() != name or not any(ch.isalnum() for ch in name)):
        raise ValueError("unqualified or dangerous native nickname")
    # RGB remains inactive unless the caller explicitly enables qualified markup.
    if type(identity.get("profile")) is not int or not 0 <= identity["profile"] <= 7:
        raise ValueError("invalid original Human-KI roster index")
    seed = identity.get("gameplay_seed")
    if type(seed) is not int or not 1 <= seed < 2**31:
        raise ValueError("invalid BotDriver seed")
    guid = identity.get("guid")
    if not isinstance(guid, str) or not re.fullmatch(r"[0-9a-f]{32}", guid):
        raise ValueError("invalid stable GUID")
    parsed = uuid.UUID(hex=guid)
    if parsed.version != 5:
        raise ValueError("expected deterministic UUIDv5")
    return name.encode("ascii"), parsed.bytes


def guid_bytes(identity):
    return _identity(identity)[1]


def profile_bytes(template, identity, *, color_probe=False, colors_enabled=False):
    """Return new profile bytes; caller must also write guid_bytes to .plr.guid.

    The observed Retail PLC4 layout is signature + u32 name bytes + name +
    4-byte appearance/metadata header + 16-byte raw GUID + remaining appearance.
    Unlike old tooling, no random GUID is allocated on each login.
    """
    name, new_guid = _identity(identity)
    if type(color_probe) is not bool:
        raise ValueError("explicit boolean color_probe required")
    if type(colors_enabled) is not bool:
        raise ValueError('explicit boolean colors_enabled required')
    if color_probe or (colors_enabled and identity.get('color') is not None):
        rgb = identity.get("color")
        if not isinstance(rgb, str) or not re.fullmatch(r"[0-9a-fA-F]{6}", rgb):
            raise ValueError("validated RGB required for native color markup")
        name = b"^c" + rgb.upper().encode("ascii") + name + b"^r"
        if len(name) > 32:
            raise ValueError("decorated native name exceeds qualified 32-byte policy cap")
    if not isinstance(template, bytes) or not 32 <= len(template) <= MAX_TEMPLATE_BYTES:
        raise ValueError("invalid PLC4 template size")
    if template[:4] != b"PLC4":
        raise ValueError("unsupported player profile signature")
    old_len = struct.unpack_from("<I", template, 4)[0]
    if not 1 <= old_len <= 255:
        raise ValueError("invalid template name length")
    old_guid_offset = 12 + old_len
    if old_guid_offset + GUID_BYTES + 4 > len(template):
        raise ValueError("incomplete PLC4 template")
    old_guid = template[old_guid_offset:old_guid_offset + GUID_BYTES]
    if template.count(old_guid) != 1 or old_guid == new_guid:
        raise ValueError("ambiguous or reused template GUID")
    return (b"PLC4" + struct.pack("<I", len(name)) + name
            + template[8 + old_len:old_guid_offset] + new_guid
            + template[old_guid_offset + GUID_BYTES:])


def startup_script(identity):
    """Safe one-slot overrides appended after the known-qualified base startup INI.

    Only preexisting integrated BotDriver user symbols, no arbitrary input text.
    The engine must still be run with exactly one player per isolated Wine client.
    """
    _identity(identity)
    return ("bot_bHumanAI=1;\n"
            "bot_iRosterOffset=0;\n"
            f"bot_iProfile0={identity['profile']};\n"
            f"bot_iProfileSeed={identity['gameplay_seed']};\n")


class ControllerLock:
    """One executor for a canonical SQLite database; kernel unlocks on exit.

    Symlink aliases of an SQLite file use the same lock. Never steal by age.
    This is a file lock, not a native game/process ownership check.
    """
    def __init__(self, database):
        self.database = Path(os.path.realpath(os.fspath(database)))
        self.lock_path = self.database.with_name(self.database.name + ".runtime.lock")
        self.fd = None

    def __enter__(self):
        if self.fd is not None:
            raise RuntimeError("controller lock already entered")
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        if (not self.database.is_file() or os.stat(self.database).st_nlink != 1):
            raise RuntimeError("initialized, single-linked SQLite DB required")
        fd = os.open(self.lock_path, flags, 0o600)
        try:
            if (not stat.S_ISREG(os.fstat(fd).st_mode) or os.fstat(fd).st_nlink != 1
                    or stat.S_IMODE(os.fstat(fd).st_mode) & 0o077):
                raise RuntimeError("unsafe controller lock file")
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, RuntimeError) as exc:
            os.close(fd)
            raise RuntimeError("another controller owns this DB, or lock is unsafe") from exc
        self.fd = fd
        return self

    def __exit__(self, *_exc):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None

    def claim_launch(self, identity_id, epoch):
        """Consume a JOINING epoch once, on disk, BEFORE creating any process.

        If an attempt crashes after this commit, never implicitly retry it:
        a separate native reconciliation and explicit operator recovery is needed.
        """
        if self.fd is None:
            raise RuntimeError("controller lock is not held")
        if (not isinstance(identity_id, str) or
                not re.fullmatch(r"[a-z0-9_-]{1,40}", identity_id) or
                type(epoch) is not int or epoch < 1):
            raise ValueError("invalid launch identity/epoch")
        with sqlite3.connect(self.database, timeout=5, isolation_level=None) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                row = db.execute("SELECT epoch,status FROM session WHERE id=?",
                                 (identity_id,)).fetchone()
                if row is None or row != (epoch, "JOINING"):
                    db.execute("ROLLBACK")
                    return False
                db.execute("CREATE TABLE IF NOT EXISTS runtime_launch_claim "
                           "(identity_id TEXT, epoch INTEGER, PRIMARY KEY(identity_id,epoch))")
                if db.execute("SELECT 1 FROM runtime_launch_claim WHERE identity_id=? AND epoch=?",
                              (identity_id, epoch)).fetchone():
                    db.execute("ROLLBACK")
                    return False
                db.execute("INSERT INTO runtime_launch_claim VALUES (?,?)", (identity_id, epoch))
                db.execute("COMMIT")
                return True
            except BaseException:
                db.execute("ROLLBACK")
                raise


def reconcile(state, observation):
    """Pure proposed action, not a process signal or Planner.record() call.

    observation comes ONLY from an independently validated owner/PID/start/CWD/
    cgroup probe and fresh server query. Missing, stale or unknown -> quarantine.
    "claim_launch" requires the caller to atomically call ControllerLock.claim_launch
    before any process start. A failed/spent epoch must NEVER retry automatically.
    """
    if not isinstance(state, dict) or state.get("status") not in {
        "OFFLINE", "WAITING", "COOLDOWN", "JOINING", "PLAYING", "LEAVING"
    }:
        return "quarantine"
    if not isinstance(observation, dict):
        return "quarantine"
    if (not isinstance(state.get("id"), str) or type(state.get("epoch")) is not int
            or state["epoch"] < 0 or observation.get("identity_id") != state["id"]
            or type(observation.get("epoch")) is not int or observation["epoch"] != state["epoch"]):
        return "quarantine"
    required = ("ownership_verified", "fresh_query", "process_alive", "connected",
                "ghost", "unknown_peers", "human_conflict")
    if any(type(observation.get(k)) is not bool for k in required):
        return "quarantine"
    if (not observation["ownership_verified"] or not observation["fresh_query"]
            or observation["ghost"] or observation["unknown_peers"]
            or observation["human_conflict"]):
        return "quarantine"
    alive, connected = observation["process_alive"], observation["connected"]
    status = state["status"]
    if status in ("OFFLINE", "WAITING", "COOLDOWN"):
        return "idle" if not alive and not connected else "quarantine"
    if status == "JOINING":
        if alive and connected:
            return "ack_join"
        if alive and not connected:
            return "wait_join"
        if not alive and not connected and observation.get("verified_absence") is True:
            return "claim_launch"
        return "quarantine"
    if status == "PLAYING":
        if alive and connected:
            return "healthy"
        if not alive and not connected and observation.get("exit_confirmed") is True:
            return "record_crash"
        return "quarantine"
    if status == "LEAVING":
        if not alive and not connected and observation.get("query_absence_confirmed") is True:
            return "ack_left"
        if alive:
            return "graceful_leave"
        return "quarantine"
    return "quarantine"
