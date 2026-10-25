"""Planner/executor contract tests. Simulated transport; no native qualification."""
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys

from bot_sessions import Planner
from bot_session_runtime import ControllerLock
import bot_session_executor as exe


def config(count=2):
    return dict(enabled=True, accelerated=True, pool_id="executor-tests", seed=23,
                max_bots=count, reserved_human_slots=2, join_interval_s=1,
                leave_interval_s=2, startup_delay_s=[0, 0], pause_s=[8, 12],
                session_bands=[[1, 10, 15]], servers=["test"],
                identities=[dict(id=f"p{i}", nickname=f"Player{i}", profile=i)
                            for i in range(count)])


class Transport:
    """Explicit in-memory game simulation at the external transport boundary."""
    def __init__(self):
        self.live = {}
        self.epochs = {}
        self.names = set()
        self.launches = []
        self.leaves = []
        self.uncertain = False
        self.fail_spawn = False

    def snapshot(self, now):
        return dict(observed_at=now, maxplayers=16, human_names=[])

    def observe(self, state, identity, now):
        alive = state['id'] in self.live
        return dict(identity_id=state['id'], epoch=state['epoch'],
                    ownership_verified=not self.uncertain, fresh_query=True,
                    process_alive=alive, connected=state['id'] in self.names,
                    ghost=not alive and state['id'] in self.names,
                    unknown_peers=False, human_conflict=False,
                    verified_absence=not alive and state['id'] not in self.names,
                    query_absence_confirmed=not alive and state['id'] not in self.names,
                    exit_confirmed=not alive and state['id'] not in self.names)
        # A durable native process record is stronger than a spent spawn claim.

    def launch(self, state, identity):
        self.launches.append((state['id'], state['epoch'], identity['guid']))
        if self.fail_spawn:
            raise OSError('uncertain spawn result')
        self.live[state['id']] = state['epoch']
        self.epochs[state['id']] = state['epoch']
        self.names.add(state['id'])

    def leave(self, state, identity):
        self.leaves.append((state['id'], state['epoch']))
        self.live.pop(state['id'], None)
        # Native peers may retain the slot after process exit; test controls query.


class ExecutorContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'sessions.db'
        self.p = Planner(self.db, config())
        self.lock = ControllerLock(self.db).__enter__()
        self.transport = Transport()
        self.e = exe.SessionExecutor(self.p, self.lock, self.transport)

    def tearDown(self):
        self.lock.__exit__()
        self.p.close()
        self.temp.cleanup()

    def tick(self, now):
        return self.e.tick('test', now)

    def test_independent_sessions_and_guid_rejoin(self):
        for t in range(100, 170):
            self.transport.names.intersection_update(self.transport.live)
            self.tick(t)
        events = list(self.p.db.execute('SELECT id,epoch,event,at FROM event'))
        self.assertEqual({x['id'] for x in events if x['event']=='joined'}, {'p0','p1'})
        self.assertTrue(any(x['event']=='left' for x in events))
        self.assertTrue(any(epoch>1 for _,epoch,_ in self.transport.launches))
        for ident in ('p0','p1'):
            self.assertEqual(len({guid for who,_,guid in self.transport.launches if who==ident}),1)
        join_times = [r['at'] for r in events if r['event']=='join_requested']
        self.assertTrue(all(b-a>=1 for a,b in zip(join_times,join_times[1:])))
        self.assertTrue(all(len([r for r in events if r['event']=='leave_requested' and r['at']==t])<=1
                            for t in range(100,170)))

    def test_admin_drain_waits_for_native_join_before_consuming_close_claim(self):
        self.tick(100)
        ident=self.transport.launches[0][0]
        self.transport.names.clear()  # process is alive, still loading the map
        self.p.set_enabled('test',False,101)
        self.tick(101)
        self.assertEqual(self.transport.leaves, [])
        self.assertEqual(list(self.p.db.execute('SELECT * FROM runtime_leave_claim')), [])
        self.assertEqual(self.p.states()[ident]['status'], 'LEAVING')
        self.transport.names.add(ident)  # native join + query now proved by transport
        self.tick(102)
        self.assertEqual(self.transport.leaves, [(ident,1)])
        self.transport.names.clear()
        self.tick(103)
        self.assertEqual(self.p.states()[ident]['status'], 'COOLDOWN')

    def test_crash_ghost_outlives_session_deadline_without_becoming_planned_leave(self):
        self.tick(100);self.tick(101)
        ident=self.transport.launches[0][0]
        self.transport.live.pop(ident)
        original=self.transport.observe
        def observed(state,who,now):
            data=original(state,who,now)
            data['owned_exit']=self.transport.epochs.get(state['id'])==state['epoch'] and state['id'] not in self.transport.live
            return data
        self.transport.observe=observed
        self.tick(110);self.tick(130)
        self.assertEqual(self.p.db.execute('SELECT observed_at FROM runtime_exit_seen WHERE identity_id=?',(ident,)).fetchone()[0],110)
        self.assertNotEqual(self.p.states()[ident]['status'],'COOLDOWN')
        self.transport.names.discard(ident)
        self.tick(131)
        state=self.p.states()[ident]
        self.assertEqual((state['status'],state['reason'],state['last_event']),('COOLDOWN','crashed','crashed'))
        events=[r['event'] for r in self.p.db.execute('SELECT event FROM event WHERE id=?',(ident,))]
        self.assertIn('crashed',events)
        self.assertNotIn('left',events)

    def test_regular_leave_waits_for_ghost_absence(self):
        self.tick(100); self.tick(101)
        ident = self.transport.launches[0][0]
        self.p.set_enabled('test',False,102)
        self.tick(102); self.tick(103)
        self.assertEqual(self.p.states()[ident]['status'],'LEAVING')
        self.assertEqual(len(self.transport.leaves),1)
        self.transport.names.clear()
        self.tick(104)
        self.assertEqual(self.p.states()[ident]['status'],'COOLDOWN')
        self.assertEqual(self.p.states()[ident]['reason'],'admin')

    def test_uncertain_spawn_never_retries_after_executor_restart(self):
        self.transport.fail_spawn=True
        with self.assertRaises(OSError): self.tick(100)
        self.e=exe.SessionExecutor(self.p,self.lock,self.transport)
        self.tick(101);self.tick(102)
        self.assertEqual(len(self.transport.launches),1)
        self.assertEqual(sum(r['status']=='JOINING' for r in self.p.states().values()),1)

    def test_unknown_owner_never_launches_or_closes(self):
        self.transport.uncertain=True
        for now in range(100,110):self.tick(now)
        self.assertEqual(self.transport.launches,[])
        self.assertEqual(self.transport.leaves,[])

    def test_leave_sent_once_across_restart(self):
        self.tick(100); self.tick(101)
        self.p.set_enabled('test',False,102)
        self.tick(102)
        self.e=exe.SessionExecutor(self.p,self.lock,self.transport)
        self.tick(103)
        self.assertEqual(len(self.transport.leaves),1)

    def test_complete_query_rejects_truncated_duplicates_and_color_collisions(self):
        good=dict(gamever='1.07',numplayers='2',maxplayers='16',player_0='Mika',player_1='Lea')
        self.assertEqual(exe.player_names(good),['Mika','Lea'])
        for bad in [dict(good,numplayers='3'), dict(good,player_1='mika'),
                    dict(good,player_1='^cFFFFFFMika^r'),dict(good,gamever='1.10'),
                    dict(good,activemod='x'),dict(good,player_2='Extra')]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):exe.player_names(bad)
    def test_real_retail_query_keeps_sparse_slots_after_departure(self):
        query=dict(gamever='1.07',numplayers='4',maxplayers='16',
                   player_0='Retail_Control',player_2='Nox7',player_3='[AG] Lea',player_4='Kai')
        self.assertEqual(exe.player_names(query),['Retail_Control','Nox7','[AG] Lea','Kai'])
        for bad in [dict(query,player_16='Invalid'),dict(query,player_02='DuplicateIndex'),
                    dict(query,numplayers='3')]:
            with self.assertRaises(ValueError):exe.player_names(bad)


class NativeOwnership(unittest.TestCase):
    def test_real_child_binding_rejects_wrong_start_cwd_cgroup_and_exit(self):
        with tempfile.TemporaryDirectory() as root:
            child=subprocess.Popen([sys.executable,'-c','input()'],cwd=root,
                                   stdin=subprocess.PIPE,text=True)
            try:
                record=exe.process_record(child.pid)
                self.assertEqual(exe.probe_process(record),'LIVE')
                for key,bad in [('start_ticks',record['start_ticks']+1),
                                ('cwd','/not/owned'),('cgroup','foreign'),('uid',-1)]:
                    self.assertEqual(exe.probe_process(dict(record,**{key:bad})),'MISMATCH')
                child.communicate('\n',timeout=3)
                self.assertEqual(exe.probe_process(record),'ABSENT')
            finally:
                if child.poll() is None:child.kill();child.wait()
                if child.stdin:child.stdin.close()


if __name__=='__main__':unittest.main()
