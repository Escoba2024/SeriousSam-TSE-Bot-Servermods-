import unittest
import json, tempfile
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
import qualify_cecil_live as monitor
from qualify_cecil_live import parse_state,summarize,BAD,GATES,memory_stats

class NativeEvidenceTests(unittest.TestCase):
    def row(self,pos="1.0,2.0,3.0",tick=20,shots=2):
        return parse_state("[CecilState] local=0 tick="+str(tick)+" ready=1 alive=1 shots="+str(shots)+" pickups=1 deaths=2 respawns=3 vis=1 nav=0 rays=4 owned=131 current=8 wanted=8 goal_entity=0 pos=("+pos+")")
    def test_state_and_activity_require_actual_progress(self):
        first=self.row();last=self.row("2.0,2.0,3.0",40,5)
        result=summarize([first,last])
        self.assertEqual((result["positions"],result["shots_delta"],result["ticks"]),(2,3,20))
        self.assertEqual(summarize([first,first])["positions"],1)
    def test_bad_or_unrelated_evidence_not_silently_accepted(self):
        self.assertIsNone(parse_state("[BotDriver] unrelated"))
        with self.assertRaises(ValueError):self.row("nan,0,0")
        with self.assertRaises(KeyError):parse_state("[CecilState] local=0")
        self.assertIsNotNone(BAD.search("[CecilLoad] rejected=map content CRC mismatch"))
        self.assertIsNotNone(BAD.search("[CecilInvalidAction] local=0 rejected=nonfinite"))
    def test_crlf_state_values_are_not_polluted(self):
        row=parse_state("[CecilState] local=0 tick=20 ready=1 alive=1 shots=0 pickups=0 deaths=0 respawns=1 vis=0 nav=1 rays=2 owned=3 current=1 wanted=1 goal_entity=0 pos=(0,0,0) gravity=(0,1,0)\r")
        self.assertEqual(row["gravity"],"(0,1,0)")
    def test_memory_sample_distinguishes_absent_and_used_swap(self):
        self.assertEqual(memory_stats("MemAvailable: 200 kB\nSwapTotal: 100 kB\nSwapFree: 75 kB")['swap_used_kib'],25)
        self.assertEqual(memory_stats("MemAvailable: 200 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB")['swap_total_kib'],0)
        with self.assertRaises(AssertionError):memory_stats("MemAvailable: 200 kB\nSwapTotal: 0 kB\nSwapFree: 1 kB")
    def test_gate_durations_not_short_smokes(self):
        self.assertEqual(GATES,{1:3600,4:3600,8:7200})

class NativeFailurePersistenceTests(unittest.TestCase):
    def observe(self,initial_bot="",initial_server="",fresh_bot="",fresh_server="",query_failure=False):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);runtime=base/"runtime";proc=base/"proc";output=base/"output"
            for role,pid in (("server",101),("botA",102)):
                root=runtime/role;root.mkdir(parents=True)
                log=root/("Dedicated_BotTest.log" if role=="server" else "SeriousSam.log")
                log.write_text(initial_server if role=="server" else initial_bot)
                fake=proc/str(pid);fake.mkdir(parents=True);(fake/"cwd").symlink_to(root,target_is_directory=True)
                fields=["0"]*22;fields[19]="99";fields[11]=fields[12]="1"
                (fake/"stat").write_text(str(pid)+" (game) "+" ".join(fields))
                (fake/"status").write_text("VmRSS: 1024 kB\n")
                if role!="server":
                    (root/"Bin").mkdir();dll=root/"Bin/GameMP.dll";dll.write_bytes(b"fixture")
                    (fake/"maps").write_text(str(dll))
            digest=monitor.sha(runtime/"botA/Bin/GameMP.dll")
            (proc/"stat").write_text("cpu 1 1 1 10 0 0 0 0\n")
            (proc/"meminfo").write_text("MemAvailable: 1000 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\n")
            def path(*args):
                value=Path(*args)
                return proc/value.relative_to("/proc") if value==Path("/proc") or Path("/proc") in value.parents else value
            def query(*args,**kwargs):
                for role,name,text in (("botA","SeriousSam.log",fresh_bot),("server","Dedicated_BotTest.log",fresh_server)):
                    with (runtime/role/name).open("a") as f:f.write(text)
                if query_failure:raise RuntimeError("UDP timeout")
                return {"mapname":"fixture","numplayers":"0"}
            argv=["qualify", "--runtime",str(runtime),"--unit-prefix","fixture","--port","25650","--bots","1","--duration","60","--dll-sha256",digest,"--output",str(output)]
            with patch.object(monitor,"Path",side_effect=path),patch.object(monitor.subprocess,"check_output",side_effect=lambda args,**kw:"101" if "-server.service" in args[2] else "102"),patch.object(monitor,"query",side_effect=query),patch.object(monitor.time,"monotonic",return_value=1),patch("sys.argv",argv),patch("builtins.print"):
                with self.assertRaises(Exception):monitor.main()
            return json.loads((output/"report.json").read_text())
    def test_missing_population_retains_fresh_syncbad(self):
        result=self.observe(fresh_bot="SYNCBAD count=10\nToo many bad syncs\n")
        self.assertEqual(result["status"],"FAILED")
        self.assertEqual([e["role"] for e in result["errors"]],["botA","botA"])
        self.assertEqual(result["failure"],"native log error")
    def test_initial_fresh_bot_log_bad_fails(self):
        result=self.observe(initial_bot="startup\nSYNCBAD count=1\n")
        self.assertEqual(result["status"],"FAILED")
        self.assertEqual(len(result["errors"]),1)
        self.assertIn("SYNCBAD",result["errors"][0]["line"])
    def test_initial_partial_bot_error_is_not_ignored(self):
        result=self.observe(initial_bot="SYNCBAD count=1")
        self.assertEqual(len(result["errors"]),1)
        self.assertEqual(result["failure"],"native log error")
    def test_fresh_partial_error_survives_query_failure(self):
        result=self.observe(fresh_bot="Too many bad syncs",query_failure=True)
        self.assertEqual(len(result["errors"]),1)
        self.assertEqual(result["failure"],"native log error")
    def test_old_server_error_does_not_become_fresh(self):
        result=self.observe(initial_server="old session SYNCBAD count=10\n")
        self.assertEqual(result["errors"],[])
        self.assertEqual(result["failure"],"expected bot population missing")
    def test_new_server_error_is_retained(self):
        result=self.observe(initial_server="old session SYNCBAD\n",fresh_server="new SYNCBAD count=1\n")
        self.assertEqual(len(result["errors"]),1)
        self.assertEqual(result["errors"][0]["role"],"server")
        self.assertIn("new SYNCBAD",result["errors"][0]["line"])

class NativeWindowCoverageTests(unittest.TestCase):
    """Exercise main with real logs/reports and synthetic process/time/UDP boundaries."""
    def observe(self, emit=lambda t: True, change_query=lambda t, q: None):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);runtime=base/"runtime";proc=base/"proc";output=base/"output"
            for role,pid in (("server",101),("botA",102)):
                root=runtime/role;root.mkdir(parents=True)
                (root/("Dedicated_BotTest.log" if role=="server" else "SeriousSam.log")).write_text("")
                fake=proc/str(pid);fake.mkdir(parents=True);(fake/"cwd").symlink_to(root,target_is_directory=True)
                fields=["0"]*22;fields[19]="99";fields[11]=fields[12]="1"
                (fake/"stat").write_text(str(pid)+" (game) "+" ".join(fields))
                (fake/"status").write_text("VmRSS: 1024 kB\n")
                if role!="server":
                    (root/"Bin").mkdir();dll=root/"Bin/GameMP.dll";dll.write_bytes(b"fixture")
                    (fake/"maps").write_text(str(dll))
            (proc/"meminfo").write_text("MemAvailable: 1000 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\n")
            digest=monitor.sha(runtime/"botA/Bin/GameMP.dll");clock=[0.0]
            def path(*args):
                value=Path(*args)
                return proc/value.relative_to("/proc") if value==Path("/proc") or Path("/proc") in value.parents else value
            def query(*args,**kwargs):
                t=clock[0]
                if emit(t):
                    row=("[CecilState] local=0 tick=%d ready=1 alive=1 shots=%d pickups=1 deaths=0 respawns=0 "
                         "vis=1 nav=0 rays=4 owned=3 current=1 wanted=1 goal_entity=0 pos=(%.1f,0,0)\n")%(20+20*t,t,t)
                    with (runtime/"botA/SeriousSam.log").open("a") as f:f.write(row)
                q={"gamename":"serioussamse","gamever":"1.07","hostport":"25650","mapname":"Red Station",
                   "numplayers":"1","player_0":"Dev-1","frags_0":"0"}
                change_query(t,q)
                return q
            argv=["qualify","--runtime",str(runtime),"--unit-prefix","fixture","--port","25650","--bots","1",
                  "--duration","60","--dll-sha256",digest,"--output",str(output)]
            failure=None
            with ExitStack() as stack:
                for context in (patch.object(monitor,"Path",side_effect=path),
                                patch.object(monitor.subprocess,"check_output",side_effect=lambda args,**kw:"101" if "-server.service" in args[2] else "102"),
                                patch.object(monitor,"query",side_effect=query),
                                patch.object(monitor,"host_cpu",side_effect=lambda:(1000+clock[0]*100,400+clock[0]*40)),
                                patch.object(monitor.shutil,"disk_usage",return_value=type("Disk",(),{"free":16*2**30})()),
                                patch.object(monitor.time,"monotonic",side_effect=lambda:clock[0]),
                                patch.object(monitor.time,"sleep",side_effect=lambda dt:clock.__setitem__(0,clock[0]+dt)),
                                patch("sys.argv",argv),patch("builtins.print")):
                    stack.enter_context(context)
                try:monitor.main()
                except Exception as exc:failure=exc
            return json.loads((output/"report.json").read_text()),failure

    def test_continuous_native_samples_complete_observation(self):
        result,failure=self.observe()
        self.assertIsNone(failure)
        self.assertEqual(result["status"],"DURATION_ACTIVITY_SYNC_PASS_BEHAVIOR_REVIEW_REQUIRED")

    def test_missing_tail_fails_while_native_process_stays_alive(self):
        result,failure=self.observe(emit=lambda t:t<48)
        self.assertIsNotNone(failure)
        self.assertEqual(result["status"],"FAILED")
        self.assertIn("telemetry",result["failure"])

    def test_late_first_sample_or_internal_gap_cannot_be_hidden(self):
        for emit in (lambda t:t>=6,lambda t:not 20<=t<=25):
            with self.subTest(emit=emit):
                result,failure=self.observe(emit=emit)
                self.assertIsNotNone(failure)
                self.assertIn("telemetry",result["failure"])

    def test_extra_player_invalidates_controlled_population(self):
        def extra(t,q):
            if t==10:q.update(numplayers="2",player_1="External")
        result,failure=self.observe(change_query=extra)
        self.assertIsNotNone(failure)
        self.assertIn("population",result["failure"])

    def test_wrong_query_identity_or_map_change_invalidates_scenario(self):
        for field,value in (("gamename","other"),("gamever","1.10"),("hostport","25600"),("mapname","Yodeller")):
            def change(t,q):
                if t==10:q[field]=value
            with self.subTest(field=field):
                result,failure=self.observe(change_query=change)
                self.assertIsNotNone(failure)
                self.assertIn("query",result["failure"])

if __name__=="__main__":unittest.main()
