#!/usr/bin/env python3
"""Unit tests for tools/gamespy_query.py using a local fake UDP server."""
import json
import socket
import tempfile
import threading
import unittest
from pathlib import Path

import gamespy_query

STATUS = ("\\gamename\\serioussamse\\gamever\\1.07\\hostport\\25600\\mapname\\Yodeller"
          "\\gametype\\Deathmatch\\numplayers\\3\\maxplayers\\16\\hostname\\Alpha-Gaming"
          "\\password\\0\\player_0\\HetznerFleetA_1\\frags_0\\4"
          "\\player_1\\HetznerFleetA_2\\frags_1\\9"
          "\\player_2\\HetznerFleetB_1\\frags_2\\2")

MIXED = STATUS.replace("\\player_2\\HetznerFleetB_1", "\\player_2\\Human")


class FakeServer(threading.Thread):
    def __init__(self, reply=STATUS, port=0):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))
        self.port = self.sock.getsockname()[1]
        self.reply = reply
        self.received = []
        self._stopped = threading.Event()

    def run(self):
        self.sock.settimeout(0.2)
        while not self._stopped.is_set():
            try:
                payload, peer = self.sock.recvfrom(2048)
            except socket.timeout:
                continue
            self.received.append(payload)
            if self.reply is not None:
                self.sock.sendto(self.reply.encode("latin-1"), peer)

    def stop(self):
        self._stopped.set()
        self.join(timeout=2)
        self.sock.close()


class ParseTests(unittest.TestCase):
    def test_parse_and_names(self):
        response = gamespy_query.parse_response(STATUS)
        self.assertEqual(response["numplayers"], "3")
        self.assertEqual(gamespy_query.player_names(response),
                         ["HetznerFleetA_1", "HetznerFleetA_2", "HetznerFleetB_1"])

    def test_summary_and_expectations(self):
        summary = gamespy_query.summarize(gamespy_query.parse_response(STATUS))
        self.assertEqual(summary["numplayers"], 3)
        self.assertEqual(summary["maxplayers"], 16)
        self.assertEqual(gamespy_query.check_expectations(summary, 3, "HetznerFleet"), [])
        self.assertTrue(gamespy_query.check_expectations(summary, 9))
        mixed = gamespy_query.summarize(gamespy_query.parse_response(MIXED))
        self.assertTrue(gamespy_query.check_expectations(mixed, 3, "HetznerFleet"))
        self.assertEqual(gamespy_query.check_expectations(mixed, 3, None), [])

    def test_bad_address(self):
        with self.assertRaises(gamespy_query.QueryError):
            gamespy_query.parse_hostport("no-port")


class LiveLoopbackTests(unittest.TestCase):
    def test_query_roundtrip(self):
        server = FakeServer()
        server.start()
        try:
            response = gamespy_query.query("127.0.0.1", server.port, timeout=1.0)
        finally:
            server.stop()
        self.assertEqual(response["hostname"], "Alpha-Gaming")
        self.assertEqual(server.received[0], b"\\status\\")

    def test_cli_watch_and_expectations(self):
        server = FakeServer()
        server.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "query.jsonl"
                code = gamespy_query.main([
                    "127.0.0.1:%d" % server.port, "\\status\\",
                    "--count", "2", "--interval", "0.05",
                    "--jsonl", str(out), "--expect-players", "3",
                    "--expect-prefix", "HetznerFleet"])
                self.assertEqual(code, 0)
                rows = [json.loads(line) for line in out.read_text().splitlines()]
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]["summary"]["numplayers"], 3)

                bad = gamespy_query.main([
                    "127.0.0.1:%d" % server.port, "\\status\\",
                    "--count", "1", "--expect-players", "9"])
                self.assertEqual(bad, gamespy_query.EXIT_FAIL)
        finally:
            server.stop()

    def test_timeout_is_failure(self):
        # A bound socket that never answers.
        server = FakeServer(reply=None)
        server.start()
        try:
            code = gamespy_query.main([
                "127.0.0.1:%d" % server.port, "\\status\\",
                "--count", "1", "--timeout", "0.2"])
        finally:
            server.stop()
        self.assertEqual(code, gamespy_query.EXIT_FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
