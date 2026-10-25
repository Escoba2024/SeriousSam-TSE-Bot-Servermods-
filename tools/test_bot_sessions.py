"""Portable policy tests. No games, signals, ports or production configuration."""
import copy
from pathlib import Path
import tempfile
import unittest
import bot_sessions as b

def config():
    return {
        "enabled": True, "pool_id": "test-pool", "seed": 173,
        "accelerated": True, "max_bots": 2, "reserved_human_slots": 2,
        "join_interval_s": 3, "leave_interval_s": 5,
        "startup_delay_s": [0, 0], "pause_s": [30, 40],
        "session_bands": [[1, 20, 20]], "servers": ["one", "two"],
        "identities": [
            {"id": "mika", "nickname": "^c80D8FFMika^r", "profile": 0, "regular_weight": 3},
            {"id": "nox", "nickname": "Nox7", "profile": 7},
            {"id": "lea", "nickname": "[AG] Lea", "profile": 3},
            {"id": "kai", "nickname": "Kai", "profile": 4},
            {"id": "jo", "nickname": "Jo", "profile": 2},
            {"id": "fen", "nickname": "Fen", "profile": 5},
        ],
    }

def snap(now, humans=(), slots=16):
    return {"observed_at": now, "maxplayers": slots, "human_names": list(humans)}

class Names(unittest.TestCase):
    def test_plain_identity_accepts_22_visible_characters_and_rejects_longer_names(self):
        c=config();c['identities']=[dict(id='boundary',nickname='A'*22,profile=0)]
        self.assertEqual(b.validate_config(c)['identities'][0]['nickname'],'A'*22)
        for length in (23,24,25,300):
            c['identities'][0]['nickname']='A'*length
            with self.subTest(length=length),self.assertRaises(ValueError):
                b.validate_config(c)
    def test_longer_human_query_names_keep_distinct_keys_and_reserved_slots(self):
        c=config();c['servers']=['one'];c['max_bots']=1
        c['identities']=[dict(id='boundary',nickname='A'*22,profile=0)]
        human='A'*22+'XY'
        with tempfile.TemporaryDirectory() as d:
            p=b.Planner(Path(d)/'human.db',c)
            try:
                # A human's 24-character name is not shortened to an owned
                # 22-character alias; the human still consumes a reserved slot.
                self.assertEqual(p.snapshot(snap(100,[human],slots=3),100),(3,[human.lower()]))
                self.assertEqual(p.plan('one',snap(100,[human],slots=3),100),[])
                actions=p.plan('one',snap(101,[human],slots=4),101)
                self.assertEqual([a['identity_id'] for a in actions],['boundary'])
            finally:p.close()
    def test_strafe_scale_is_explicit_bounded_native_probe(self):
        self.assertEqual(b.validate_config(dict(config(),strafe_scale=.5))['strafe_scale'],.5)
        for value in [True,-.01,1.01,float('nan'),'0.5']:
            with self.subTest(value=value),self.assertRaises(ValueError):
                b.validate_config(dict(config(),strafe_scale=value))
    def test_individual_time_patterns_and_utc_login_window(self):
        c=config();c['servers']=['one'];c['max_bots']=1
        c['identities']=[dict(id='night',nickname='Nightjar',profile=6,
                              session_bands=[[1,40,40]],pause_s=[70,70],active_hours_utc=[22,23])]
        with tempfile.TemporaryDirectory() as d:
            p=b.Planner(str(Path(d)/'times.db'),c)
            self.assertEqual(p.plan('one',snap(3600),3600), [])
            now=22*3600
            action=p.plan('one',snap(now),now)[0]
            p.record('night',action['epoch'],'joined',now)
            self.assertEqual(p.states()['night']['until'],now+40)
            p.plan('one',snap(now+40),now+40)
            p.record('night',action['epoch'],'left',now+41)
            self.assertEqual(p.states()['night']['until'],now+111)
            p.close()
        for field,value in [('active_hours_utc',[24]),('active_hours_utc',[True]),('active_hours_utc',[[2]]),
                            ('session_bands',[[1,0,1]]),('pause_s',[0,1])]:
            with self.subTest(field=field),self.assertRaises(ValueError):
                b.validate_config(dict(c,identities=[dict(c['identities'][0],**{field:value})]))
    def test_native_name_is_persistent_and_must_match_visible_identity(self):
        c = config(); c['colors_enabled'] = True
        c['identities'][0]['native_name'] = '^b^c80D8FFMika^B^r'
        with tempfile.TemporaryDirectory() as d:
            p = b.Planner(str(Path(d)/'native.db'), c)
            self.assertEqual(next(i for i in p.identities() if i['id']=='mika')['native_name'], '^b^c80D8FFMika^B^r')
            p.close()
        for value in ['^c80D8FFOther^r', '^bMika', '^xMika^r', 'Mika;Quit()']:
            c['identities'][0]['native_name'] = value
            with self.subTest(value=value), self.assertRaises(ValueError): b.validate_config(c)
    def test_central_logging_options_are_typed_and_bounded(self):
        c=dict(config(),debug_logging=True,log_every_ticks=50,max_log_mib=4)
        self.assertEqual(b.validate_config(c)['log_every_ticks'],50)
        for key,value in [('debug_logging','yes'),('log_every_ticks',True),
                          ('log_every_ticks',0),('max_log_mib',129)]:
            with self.subTest(key=key),self.assertRaises(ValueError):
                b.validate_config(dict(c,**{key:value}))
    def test_low_memory_rendering_is_explicit_boolean(self):
        self.assertTrue(b.validate_config(dict(config(),low_memory_rendering=True))['low_memory_rendering'])
        with self.assertRaises(ValueError):b.validate_config(dict(config(),low_memory_rendering='true'))
    def test_readable_safe_names(self):
        self.assertEqual(b.clean_name("^c80D8FFMika^r\n\x00"), "Mika")
        self.assertEqual(b.clean_name('  [AG]  Lea;/"\\\\  '), "[AG] Lea")
        self.assertLessEqual(len(b.clean_name("A" * 300)), b.VISIBLE_CAP)
    def test_no_empty_identity(self):
        with self.assertRaises(ValueError): b.clean_name("\x00^r")
    def test_effects_do_not_become_visible_letters_or_hide_collisions(self):
        self.assertEqual(b.clean_name('^b^i^f3Raven^F^I^B^r'), 'Raven')
        c=config();c['identities'][1]['nickname']='^bMika^B^r'
        with self.assertRaises(ValueError):b.validate_config(c)
    def test_visible_casefolded_collisions(self):
        c = config()
        c["identities"][1]["nickname"] = "^cFF0000mIKA^r"
        with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
            b.Planner(Path(d)/"state.db", c)
    def test_native_qualified_colors_are_opt_in_and_decorated_name_is_bounded(self):
        c=config();c['identities'][0]['color']='80D8FF'
        self.assertFalse(b.validate_config(c)['colors_enabled'])
        c['colors_enabled']=True
        self.assertTrue(b.validate_config(c)['colors_enabled'])
        c['identities'][0]['nickname']='A'*23
        with self.assertRaises(ValueError):b.validate_config(c)

class Sessions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/"state.db"
        self.c = config()
        # Tests use one server unless checking cross-server assignment.
        self.c["servers"] = ["one"]
        self.p = b.Planner(self.path, self.c)
    def tearDown(self):
        self.p.close(); self.tmp.cleanup()
    def join(self, now=100):
        actions = self.p.plan("one", snap(now), now)
        joins = [a for a in actions if a["action"] == "join"]
        self.assertEqual(len(joins), 1)
        return joins[0]
    def ack_join(self, a, now=100):
        self.assertTrue(self.p.record(a["identity_id"], a["epoch"], "joined", now))
    def test_defaults_are_disabled(self):
        c = config(); del c["enabled"]
        with tempfile.TemporaryDirectory() as d:
            p = b.Planner(Path(d)/"state.db", c)
            self.assertEqual(p.plan("one", snap(100), 100), [])
            p.close()
    def test_minimum_population_defers_only_planned_leave(self):
        c=config();c['servers']=['one'];c['min_bots']=1;c['max_bots']=1
        with tempfile.TemporaryDirectory() as d:
            p=b.Planner(Path(d)/'minimum.db',c)
            try:
                action=p.plan('one',snap(100),100)[0]
                p.record(action['identity_id'],action['epoch'],'joined',100)
                self.assertEqual(p.plan('one',snap(125),125),[])
                self.assertEqual(p.states()[action['identity_id']]['status'],'PLAYING')
                p.set_enabled('one',False,126)
                leave=p.plan('one',snap(126),126)
                self.assertEqual([(x['action'],x['reason']) for x in leave],[('leave','admin')])
            finally:p.close()
    def test_minimum_population_cannot_exceed_maximum(self):
        c=config();c['min_bots']=3
        with self.assertRaises(ValueError):b.validate_config(c)
    def test_identity_guid_seed_survive_restart(self):
        before = self.p.identities()
        self.p.close(); self.p = b.Planner(self.path, self.c)
        self.assertEqual(before, self.p.identities())
        self.assertEqual(len({x["guid"] for x in before}), len(before))
        self.assertEqual(len({x["gameplay_seed"] for x in before}), len(before))
    def test_identity_mutation_is_rejected(self):
        c = copy.deepcopy(self.c); c["identities"][0]["profile"] = 7
        with self.assertRaises(ValueError): b.Planner(self.path, c)
    def test_weighted_normal_session_defaults(self):
        c = self.p.config
        # Accelerated tests do not pretend to establish normal-time stability.
        self.assertEqual(b.DEFAULT_BANDS, [[0.15,300,900], [0.55,900,2700],
                                          [0.25,2700,5400], [0.05,5400,9000]])
        with self.assertRaises(ValueError):
            b.validate_config(dict(self.c, accelerated=False))
        self.assertTrue(c["accelerated"])
    def test_join_rate_and_pending_limit(self):
        a = self.join()
        self.ack_join(a, 100)
        self.assertEqual(self.p.plan("one", snap(101), 101), [])
        # A second controller cannot reserve another joining slot at the same time.
        second = self.p.plan("one", snap(109), 109)
        self.assertEqual(len(second), 1)
        self.assertEqual(self.p.plan("one", snap(110), 110), [])
        self.ack_join(second[0], 110)
        self.assertEqual(self.p.plan("one", snap(110), 110), [])
        self.assertEqual(self.p.plan("one", snap(111), 111), [])
    def test_restart_does_not_repeat_inflight_join(self):
        a = self.join()
        self.p.close(); self.p = b.Planner(self.path, self.c)
        self.assertEqual(self.p.plan("one", snap(110), 110), [])
        self.assertEqual(self.p.states()[a["identity_id"]]["status"], "JOINING")
    def test_normal_session_end_and_real_pause(self):
        a = self.join(); self.ack_join(a)
        leaves = self.p.plan("one", snap(120), 120)
        leave = next(x for x in leaves if x["action"] == "leave")
        self.assertEqual(leave["identity_id"], a["identity_id"])
        self.assertEqual(leave["reason"], "planned")
        self.assertTrue(self.p.record(a["identity_id"], a["epoch"], "left", 121))
        state = self.p.states()[a["identity_id"]]
        self.assertEqual(state["status"], "COOLDOWN")
        self.assertGreaterEqual(state["until"], 151)
        self.p.plan("one", snap(130), 130)
        self.assertEqual(self.p.states()[a["identity_id"]]["status"], "COOLDOWN")
    def test_leaving_restart_is_not_a_missing_slot(self):
        a = self.join(); self.ack_join(a)
        self.p.plan("one", snap(120), 120)
        self.p.close(); self.p = b.Planner(self.path, self.c)
        actions = self.p.plan("one", snap(121), 121)
        self.assertFalse(any(x["identity_id"] == a["identity_id"] for x in actions))
        self.assertEqual(self.p.states()[a["identity_id"]]["status"], "LEAVING")
    def test_crash_and_connection_loss_have_distinct_causes(self):
        a = self.join()
        self.p.record(a["identity_id"], a["epoch"], "crashed", 101)
        self.assertEqual(self.p.states()[a["identity_id"]]["reason"], "crashed")
        other = self.join(110); self.ack_join(other, 110)
        self.p.record(other["identity_id"], other["epoch"], "disconnected", 111)
        self.assertEqual(self.p.states()[other["identity_id"]]["reason"], "disconnected")
    def test_old_ack_cannot_mutate_new_session(self):
        a = self.join()
        self.assertFalse(self.p.record(a["identity_id"], a["epoch"] + 1, "joined", 101))
        self.assertEqual(self.p.states()[a["identity_id"]]["status"], "JOINING")
    def test_duplicate_ack_is_ignored(self):
        a = self.join(); self.ack_join(a)
        self.assertFalse(self.p.record(a["identity_id"], a["epoch"], "joined", 101))
        self.assertEqual(self.p.states()[a["identity_id"]]["until"], 120)
    def test_human_reserve_and_bounded_eviction(self):
        a = self.join(); self.ack_join(a)
        second = self.join(110); self.ack_join(second, 110)
        actions = self.p.plan("one", snap(111, ("Human",), 4), 111)
        self.assertEqual([x["reason"] for x in actions], ["human_capacity"])
        self.assertEqual(self.p.plan("one", snap(112, ("Human", "Other"), 4), 112), [])
    def test_human_name_is_never_taken(self):
        names = [i["nickname"].upper() for i in self.p.identities()]
        self.assertEqual(self.p.plan("one", snap(100, names, 16), 100), [])
    def test_stale_or_malformed_snapshot_blocks_join(self):
        for s in [snap(50), None, {}, snap(100, (), 0), snap(100, (), True),
                  dict(snap(100), human_names=["Human", "human"])]:
            self.assertEqual(self.p.plan("one", s, 100), [])
    def test_admin_off_persists_and_does_not_restart(self):
        a = self.join(); self.ack_join(a)
        self.p.set_enabled("one", False, 101)
        action = self.p.plan("one", snap(101), 101)[0]
        self.assertEqual(action["reason"], "admin")
        self.p.record(a["identity_id"], a["epoch"], "left", 102)
        self.p.close(); self.p = b.Planner(self.path, self.c)
        self.assertEqual(self.p.plan("one", snap(999), 999), [])
    def test_two_controllers_serialize_one_intent(self):
        a = self.join()
        other = b.Planner(self.path, self.c)
        try:
            self.assertEqual(other.plan("one", snap(100), 100), [])
            self.assertEqual(other.states()[a["identity_id"]]["status"], "JOINING")
        finally: other.close()
    def test_server_assignment_is_stable_and_exclusive(self):
        self.p.close()
        self.path = Path(self.tmp.name)/"multi.db"
        self.c["servers"] = ["one", "two"]
        self.p = b.Planner(self.path, self.c)
        ids = [self.p.plan(s, snap(100), 100) for s in self.c["servers"]]
        flat = [x["identity_id"] for actions in ids for x in actions]
        self.assertEqual(len(flat), len(set(flat)))
        self.assertEqual(set(x["server"] for x in self.p.states().values()), {"one", "two"})
    def test_reproducible_across_independent_databases(self):
        other = b.Planner(Path(self.tmp.name)/"other.db", self.c)
        try:
            for t in (100, 110, 120, 130):
                one = self.p.plan("one", snap(t), t)
                two = other.plan("one", snap(t), t)
                self.assertEqual(one, two)
                for action in one:
                    event = "joined" if action["action"] == "join" else "left"
                    self.p.record(action["identity_id"], action["epoch"], event, t)
                    other.record(action["identity_id"], action["epoch"], event, t)
        finally: other.close()
    def test_bad_config_never_creates_database(self):
        for change in ({"max_bots": -1}, {"seed": True}, {"pause_s": [0, 4]},
                       {"session_bands": [[0, 1, 2]]}, {"servers": ["one", "one"]},
                       {"join_interval_s": float("nan")},
                       {"session_bands": [[1e308, 1, 2], [1e308, 3, 4]]},
                       {"reserve_human_slots": 5}):
            c = dict(self.c, **change); path = Path(self.tmp.name)/"bad.db"
            with self.assertRaises(ValueError): b.Planner(path, c)
            self.assertFalse(path.exists())
    def test_clock_rollback_is_rejected(self):
        self.join()
        with self.assertRaises(ValueError): self.p.plan("one", snap(90), 90)


    def test_actual_concurrent_controllers_emit_one_join(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        barrier = Barrier(2)
        def run(_):
            planner = b.Planner(self.path, self.c)
            try:
                barrier.wait(timeout=5)
                return planner.plan("one", snap(100), 100)
            finally:
                planner.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(run, (0, 1)))
        self.assertEqual(sum(len(x) for x in results), 1)
        self.assertEqual(sum(r["status"] == "JOINING" for r in self.p.states().values()), 1)

    def test_unknown_human_decoration_holds_new_joins(self):
        self.assertEqual(self.p.plan("one", snap(100, ("^bMika",)), 100), [])

    def test_event_token_requires_integer_epoch(self):
        a = self.join()
        for epoch in (True, 1.0, "1", -1):
            with self.assertRaises(ValueError):
                self.p.record(a["identity_id"], epoch, "joined", 100)

    def test_timing_changes_do_not_change_identity(self):
        before = self.p.identities()
        c = dict(self.c, join_interval_s=25)
        other = b.Planner(self.path, c)
        try:
            self.assertEqual(other.identities(), before)
        finally:
            other.close()

    def test_normal_defaults_produce_mixed_durations_and_minimum_pause(self):
        c = config()
        c.update(servers=["one"], accelerated=False, identities=c["identities"][:1],
                 pause_s=[900, 900], startup_delay_s=[0, 0])
        del c["session_bands"]
        p = b.Planner(":memory:", c)
        durations, now = [], 100
        try:
            for _ in range(200):
                action = p.plan("one", snap(now), now)[0]
                ident, epoch = action["identity_id"], action["epoch"]
                p.record(ident, epoch, "joined", now)
                end = p.states()[ident]["until"]
                durations.append(end - now)
                self.assertEqual(p.plan("one", snap(end), end)[0]["reason"], "planned")
                p.record(ident, epoch, "left", end)
                now = p.states()[ident]["until"]
                self.assertEqual(now - end, 900)
            middle = sum(1200 <= d <= 5400 for d in durations)
            self.assertGreater(middle, 140)
            self.assertLess(middle, 180)
            self.assertTrue(any(d < 1200 for d in durations))
            self.assertTrue(any(d > 5400 for d in durations))
        finally:
            p.close()

if __name__ == "__main__":
    unittest.main()
