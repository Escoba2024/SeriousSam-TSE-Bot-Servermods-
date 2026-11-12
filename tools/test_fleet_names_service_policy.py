"""Lossless systemctl-show fixtures, shaped like the observed two-row output."""
import unittest
from fleet_names_service_policy import parse_service_policy


WAIT = ("{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 /fixture/hole/wait-server.py ; "
        "ignore_errors=no ; start_time=[Wed 2026-11-11 21:21:15 UTC] ; "
        "stop_time=[Wed 2026-11-11 21:21:15 UTC] ; pid=1201 ; code=exited ; status=0 }")
SLEEP = ("{ path=/bin/sleep ; argv[]=/bin/sleep 20 ; ignore_errors=no ; "
         "start_time=[Wed 2026-11-11 21:21:15 UTC] ; stop_time=[Wed 2026-11-11 21:21:35 UTC] ; "
         "pid=1202 ; code=exited ; status=0 }")
START = ("{ path=/bin/bash ; argv[]=/bin/bash /fixture/hole/launch-botB.sh ; "
         "ignore_errors=no ; start_time=[Wed 2026-11-11 21:21:35 UTC] ; "
         "stop_time=[n/a] ; pid=1203 ; code=(null) ; status=0/0 }")
STOP = ("{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 /fixture/graceful.py botB $MAINPID ; "
        "ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }")


class ServicePolicy(unittest.TestCase):
    def test_actual_repeated_row_shape_preserves_first_wait_and_second_sleep(self):
        raw = ("ExecStartPre="+WAIT+"\nExecStartPre="+SLEEP+"\nExecStart="+START+
               "\nFragmentPath=/fixture/systemd/botb.service\nDropInPaths=\n")
        parsed = parse_service_policy(raw)
        self.assertEqual(parsed["ExecStartPre"], [
            {"path": "/usr/bin/python3", "argv": "/usr/bin/python3 /fixture/hole/wait-server.py", "ignore_errors": "no"},
            {"path": "/bin/sleep", "argv": "/bin/sleep 20", "ignore_errors": "no"}])
        self.assertEqual(parsed["ExecStart"], [
            {"path": "/bin/bash", "argv": "/bin/bash /fixture/hole/launch-botB.sh", "ignore_errors": "no"}])
        self.assertEqual(parsed["ExecStop"], [])

    def test_same_row_multiple_commands_keeps_order(self):
        parsed = parse_service_policy("ExecStartPre="+WAIT+" "+SLEEP+"\n")
        self.assertEqual([c["path"] for c in parsed["ExecStartPre"]], ["/usr/bin/python3", "/bin/sleep"])

    def test_execstop_commands_are_not_dropped(self):
        parsed = parse_service_policy("ExecStop="+STOP+"\nExecStop="+STOP+"\n")
        self.assertEqual(len(parsed["ExecStop"]), 2)
        self.assertEqual(parsed["ExecStop"][0]["argv"], "/usr/bin/python3 /fixture/graceful.py botB $MAINPID")

    def test_volatile_times_and_pid_do_not_look_like_configuration_drift(self):
        raw = "ExecStartPre="+WAIT+"\nExecStart="+START+"\nExecStop="+STOP
        newer = raw.replace("pid=1201", "pid=7777").replace("pid=0", "pid=9911").replace(
            "start_time=[n/a]", "start_time=[Thu 2026-11-12 08:00:00 UTC]").replace(
            "status=0/0", "status=0")
        self.assertEqual(parse_service_policy(raw), parse_service_policy(newer))
        changed = newer.replace("graceful.py botB $MAINPID", "other.py botB $MAINPID")
        self.assertNotEqual(parse_service_policy(raw), parse_service_policy(changed))

    def test_duplicate_scalar_policy_cannot_hide_an_earlier_value(self):
        for value in ("KillMode=none\nKillMode=control-group", "SendSIGKILL=no\nSendSIGKILL=yes"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "duplicate"):
                    parse_service_policy(value)

    def test_unparsed_command_fragments_and_unknown_rows_reject(self):
        for value in ("ExecStartPre="+WAIT+" ignored text",
                      "ExecStartPre=unparsed command",
                      "ExecStartPre="+WAIT.replace("ignore_errors=no", "ignore_errors=unknown"),
                      "ExecStartPre="+WAIT.replace("pid=1201", "unreviewed=1"),
                      "Unexpected=yes", "missing equals"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_service_policy(value)

    def test_empty_properties_and_missing_optional_exec_lists_are_explicit(self):
        parsed = parse_service_policy("ExecStartPre=\nExecStop=\nKillMode=control-group\n")
        self.assertEqual(parsed["ExecStartPre"], [])
        self.assertEqual(parsed["ExecStop"], [])
        self.assertEqual(parsed["KillMode"], "control-group")

    def test_changed_order_or_ignore_error_policy_remains_visible(self):
        original = parse_service_policy("ExecStartPre="+WAIT+"\nExecStartPre="+SLEEP)
        reversed_order = parse_service_policy("ExecStartPre="+SLEEP+"\nExecStartPre="+WAIT)
        ignored = parse_service_policy("ExecStartPre="+WAIT.replace("ignore_errors=no", "ignore_errors=yes")+"\nExecStartPre="+SLEEP)
        self.assertNotEqual(original, reversed_order)
        self.assertNotEqual(original, ignored)


if __name__ == "__main__":
    unittest.main()
