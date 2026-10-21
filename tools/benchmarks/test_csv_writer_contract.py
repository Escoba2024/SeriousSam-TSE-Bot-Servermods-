#!/usr/bin/env python3
"""Validate the real C++ watchdog format, including a native CRT and parser roundtrip."""
import ctypes
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import bot_telemetry as bt

class CsvWriterContract(unittest.TestCase):
    def test_real_format_types_and_roundtrip(self):
        candidates = [ROOT / "poc/candidates/p0-nullrender-20261022/BotDriver.cpp"]
        integrated = ROOT / "poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp"
        if integrated.exists():
            candidates.append(integrated)
        for source in candidates:
            with self.subTest(source=source.name):
                text = source.read_text()
                body = text[text.index("static DWORD WINAPI BotTelemetry_Watchdog"):]
                fmt = re.search(r'BotTelemetry_WriteLine\(\s*"([^"]+)"', body).group(1)
                tokens = re.findall(r'%(?:\.\d+)?(?:ll|l)?[duf]', fmt)
                expected = ["%llu"] + ["%ld"] * 12 + ["%.3f"] * 4 + ["%llu"] * 2 + ["%d", "%ld"]
                self.assertEqual(tokens, expected, "21 CSV columns must match their vararg types")
                # Execute exactly the shipped format through the CRT, with distinct
                # sentinels so a field reordering cannot pass a field-count test.
                vals = [ctypes.c_ulonglong(1700000000000)]
                vals += [ctypes.c_long(i) for i in range(1,13)]
                vals += [ctypes.c_double(v) for v in (1.125,2.250,3.375,4.5)]
                vals += [ctypes.c_ulonglong(9001),ctypes.c_ulonglong(9002),ctypes.c_int(2),ctypes.c_long(4)]
                buf = ctypes.create_string_buffer(1024)
                libc = ctypes.CDLL(None)
                n = libc.snprintf(buf,ctypes.c_size_t(len(buf)),fmt.encode(),*vals)
                self.assertGreater(n,0)
                line = buf.value.decode()
                self.assertEqual(line.split(",")[13:17], ["1.125","2.250","3.375","4.500"])
                parsed = bt.parse("#columns," + ",".join(bt.COLUMNS) + "\n" + line + "\n").rows[0]
                self.assertEqual(parsed.noentity,12)
                self.assertEqual(parsed.lock_ms_max,1.125)
                self.assertEqual(parsed.tick_ms_avg,4.5)
                self.assertEqual((parsed.cpu_user_ms,parsed.cpu_kernel_ms,parsed.stall_s,parsed.reason),(9001,9002,2,4))

if __name__ == "__main__":
    unittest.main()
