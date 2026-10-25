"""Execute the existing Planner via an owner-verifying transport.

This module creates no processes by itself. A native transport must independently
bind PID/start/CWD/cgroup, query freshness and epoch before reporting observations.
The fixed-population PR46 supervisor must never manage these same clients.
"""
from pathlib import Path
import os
import re

from bot_sessions import clean_name
from bot_session_runtime import reconcile


def process_record(pid):
    root = Path('/proc') / str(pid)
    before = (root / 'stat').read_text().rsplit(') ', 1)[1].split()
    record = dict(pid=pid, start_ticks=int(before[19]),
                  cwd=os.path.realpath(root / 'cwd'),
                  cgroup=(root / 'cgroup').read_text(), uid=root.stat().st_uid)
    after = (root / 'stat').read_text().rsplit(') ', 1)[1].split()
    if before[19] != after[19] or after[0] == 'Z':
        raise ProcessLookupError('process changed while binding ownership')
    return record


def probe_process(record):
    try:
        current = process_record(record['pid'])
        return 'LIVE' if current == record else 'MISMATCH'
    except (FileNotFoundError, ProcessLookupError):
        return 'ABSENT'
    except (OSError, KeyError, ValueError):
        return 'MISMATCH'


def player_names(query):
    """Validate a full Retail query, whose player indices may retain holes."""
    if not isinstance(query, dict) or query.get('gamever') != '1.07' or query.get('activemod'):
        raise ValueError('not an unmodified Retail 1.07 query')
    try:
        count, maximum = int(query['numplayers']), int(query['maxplayers'])
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError('invalid query population') from exc
    if not 0 <= count <= maximum <= 16:
        raise ValueError('invalid population bounds')
    slots = {key for key in query if re.fullmatch(r'player_\d+', key)}
    # Native Retail preserves entity/player indices after a leave. numplayers
    # counts entries, not the greatest retained slot. Verified with live 1.07.
    if (len(slots) != count or any(not re.fullmatch(r'player_(0|[1-9]\d*)',key) or
                                 int(key[7:])>=16 for key in slots)):
        raise ValueError('incomplete or extra player slots')
    names = [query[key] for key in sorted(slots,key=lambda key:int(key[7:]))]
    normalized = [clean_name(name).casefold() for name in names]
    if len(set(normalized)) != count:
        raise ValueError('ambiguous visible player names')
    return names


class SessionExecutor:
    """One executor, durable at-most-once spawn/close claims per session epoch.

    A crash between a claim and its external side effect quarantines that epoch;
    it never infers permission to launch/close again. Native recovery must prove
    which process exists. Planned leave is acknowledged only after query absence.
    """
    def __init__(self, planner, controller_lock, transport):
        database = Path(planner.db.execute('PRAGMA database_list').fetchone()[2]).resolve()
        if controller_lock.fd is None or database != controller_lock.database:
            raise RuntimeError('held controller lock for the same database required')
        self.planner, self.lock, self.transport = planner, controller_lock, transport
        planner.db.execute('CREATE TABLE IF NOT EXISTS runtime_leave_claim '
                           '(identity_id TEXT, epoch INTEGER, at REAL, '
                           'PRIMARY KEY(identity_id,epoch))')
        planner.db.execute('CREATE TABLE IF NOT EXISTS runtime_exit_seen '
                           '(identity_id TEXT, epoch INTEGER, observed_at REAL, PRIMARY KEY(identity_id,epoch))')
        if 'observed_at' not in {r[1] for r in planner.db.execute('PRAGMA table_info(runtime_exit_seen)')}:
            planner.db.execute('ALTER TABLE runtime_exit_seen ADD COLUMN observed_at REAL')

    def tick(self, server, now):
        if self.lock.fd is None:
            raise RuntimeError('controller lock released')
        p = self.planner
        snapshot = self.transport.snapshot(now)
        p.plan(server, snapshot, now)
        identities = {i['id']: i for i in p.identities()}
        decisions = []
        for state in p.states().values():
            if state['server'] != server:
                continue
            who = identities[state['id']]
            observation = self.transport.observe(state, who, now)
            action = reconcile(state, observation)
            leave_claim = p.db.execute('SELECT 1 FROM runtime_leave_claim WHERE identity_id=? AND epoch=?',
                                       (state['id'],state['epoch'])).fetchone()
            # Remember a proved own process exit while its server slot is still
            # a ghost. A later session deadline must not relabel this as a leave.
            if (isinstance(observation,dict) and observation.get('owned_exit') is True and
                observation.get('ownership_verified') is True and observation.get('fresh_query') is True and
                observation.get('process_alive') is False and observation.get('identity_id')==state['id'] and
                type(observation.get('epoch')) is int and observation['epoch']==state['epoch'] and
                state['status'] in ('JOINING','PLAYING','LEAVING') and not leave_claim):
                p.db.execute('INSERT OR IGNORE INTO runtime_exit_seen (identity_id,epoch,observed_at) VALUES (?,?,?)',
                             (state['id'],state['epoch'],now))
            exit_seen = p.db.execute('SELECT 1 FROM runtime_exit_seen WHERE identity_id=? AND epoch=?',
                                     (state['id'],state['epoch'])).fetchone()
            if (action in ('ack_left','claim_launch') and exit_seen and
                    observation.get('exit_confirmed') is True):
                action='record_crash'
            if action == 'claim_launch':
                if self.lock.claim_launch(state['id'], state['epoch']):
                    self.transport.launch(state, who)
                    action = 'launched'
                else:
                    action = 'spent_launch_claim'
            elif action == 'graceful_leave':
                with p.transaction():
                    claimed = p.db.execute('INSERT OR IGNORE INTO runtime_leave_claim VALUES (?,?,?)',
                                           (state['id'], state['epoch'], now)).rowcount == 1
                if claimed:
                    self.transport.leave(state, who)
                    action = 'leave_sent'
                else:
                    action = 'wait_leave'
            else:
                event = {'ack_join': 'joined', 'ack_left': 'left', 'record_crash': 'crashed'}.get(action)
                if event and not p.record(state['id'], state['epoch'], event, now):
                    raise RuntimeError('lifecycle epoch changed during acknowledgement')
            decisions.append(dict(id=state['id'], epoch=state['epoch'], action=action))
        return decisions
