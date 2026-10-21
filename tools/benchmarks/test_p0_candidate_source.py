#!/usr/bin/env python3
"""Static guards for the P0 candidate source (no game, no MSVC required).

These tests cannot prove that the DLL compiles under MSVC or that the bots act
in game. They do prove the properties that the 2026-10-21 failure depended on:

  * the null-render early-out is before tm_csHooks,
  * every timer invocation is counted before the driver's early-out,
  * the ga_csNetwork wait is measured around the lock,
  * SetAction() calls are counted,
  * the CSV header matches the analyser,
  * the A/B profiles differ in exactly one line,
  * the telemetry block parses as C++ (with Win32 stubs, if g++ exists).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAND = ROOT / "poc" / "candidates" / "p0-nullrender-20261022"
RELEASE = ROOT / "poc" / "release" / "gamemp"

sys.path.insert(0, str(ROOT / "tools"))
import bot_telemetry  # noqa: E402


def read(path: Path) -> str:
    return path.read_bytes().decode("latin-1").replace("\r\n", "\n")


class ApplyScriptTests(unittest.TestCase):
    def test_materialises_verified_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "gamemp"
            proc = subprocess.run(
                ["bash", str(CAND / "apply.sh"), str(target)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            for name in ("Game.cpp", "BotDriver.cpp", "BotTelemetry.h"):
                self.assertEqual((target / name).read_bytes(), (CAND / name).read_bytes())
            for source in RELEASE.iterdir():
                if source.name in ("Game.cpp", "BotDriver.cpp", "BotTelemetry.h"):
                    continue
                self.assertEqual((target / source.name).read_bytes(), source.read_bytes(), source.name)

    def test_refuses_existing_target_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "gamemp"
            target.mkdir()
            (target / "keep.txt").write_text("x", encoding="utf-8")
            proc = subprocess.run(
                ["bash", str(CAND / "apply.sh"), str(target)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 4, proc.stderr)
            self.assertTrue((target / "keep.txt").exists())

    def test_pins_release_hashes(self):
        text = read(CAND / "apply.sh")
        self.assertIn("01dfa59857df4953d3a89096cd8049b9ba022f81e388c0dfc52b4826909474b6", text)
        self.assertIn("b5d3290391b2504cce96529155b4072361fed0319a80ad1695707e36a9165c64", text)
        self.assertIn("82c8282d1426177031cdaa3f140fd084c2ddcf51cb74bfd694e49af90e8d0a3d", text)


class GameCppTests(unittest.TestCase):
    def setUp(self):
        self.text = read(CAND / "Game.cpp")

    def test_null_render_is_before_the_render_lock(self):
        bypass = self.text.index("if (bot_bNullRender")
        lock = self.text.index("CTSingleLock slBotRender", bypass)
        self.assertLess(bypass, lock)
        block = self.text[bypass:lock]
        self.assertIn("return;", block)
        self.assertIn("gm_bGameOn", block)
        self.assertIn("!_pNetwork->IsServer()", block)
        self.assertIn('_fnmThumb==""', block)

    def test_bypass_is_counted(self):
        bypass = self.text.index("if (bot_bNullRender")
        block = self.text[bypass:self.text.index("BotTelemetry_Render(0)", bypass)]
        self.assertIn("BotTelemetry_Render(1)", block)
        self.assertLess(bypass, self.text.index("BotTelemetry_Render(0)", bypass))

    def test_render_counter_only_counts_real_frames(self):
        draw = self.text.index("BotTelemetry_Render(0)")
        lock = self.text.index("CTSingleLock slBotRender", draw)
        self.assertLess(draw, lock)

    def test_config_is_written_after_the_startup_script(self):
        script = self.text.index('fnmStartupScript+"\\";");')
        config = self.text.index("BotTelemetry_Config(bot_bNullRender", script)
        self.assertLess(script, config)

    def test_defaults_are_off_and_telemetry_on(self):
        self.assertIn("static INDEX bot_bNullRender = FALSE;", self.text)
        self.assertIn("static INDEX bot_iNullRenderFps = 0;", self.text)

    def test_symbols_are_declared(self):
        for symbol in ("bot_bNullRender", "bot_iNullRenderFps"):
            self.assertIn('_pShell->DeclareSymbol("user INDEX %s;", &%s);' % (symbol, symbol), self.text)

    def test_main_loop_is_counted(self):
        self.assertIn("BotTelemetry_Frame();", self.text)


class BotDriverTests(unittest.TestCase):
    def setUp(self):
        self.text = read(CAND / "BotDriver.cpp")

    def test_timer_is_counted_before_the_early_out(self):
        start = self.text.index("BOOL BotDriver_HandleTimer")
        early_out = self.text.index("if (!bot_bEnabled || pgame==NULL", start)
        self.assertIn("BotDriver_ReportState(BotDriver_InactiveReason", self.text[early_out:early_out + 400])

    def test_ticks_are_counted_once_per_invocation(self):
        start = self.text.index("BOOL BotDriver_HandleTimer")
        early_out = self.text.index("if (!bot_bEnabled || pgame==NULL", start)
        tick = self.text.index("BotTelemetry_Tick(", start)
        self.assertLess(tick, early_out)
        self.assertEqual(self.text.count("BotTelemetry_Tick("), 2)  # definition + call

    def test_active_reason_is_published_once_after_the_loop(self):
        loop_start = self.text.index("for (INDEX iLP=0; iLP<4; iLP++)")
        loop_end = self.text.index("if (bActed)", loop_start)
        active = self.text.index("BotDriver_ReportState(BOT_TM_REASON_ACTIVE", loop_end)
        action = self.text.index("ppls->SetAction(pa);")
        self.assertLess(loop_start, action)
        self.assertLess(action, loop_end)
        self.assertGreater(active, loop_end)
        self.assertEqual(self.text.count("BotDriver_ReportState(BOT_TM_REASON_ACTIVE"), 1)
        segment = self.text[action:action + 300]
        self.assertNotIn("BotDriver_ReportState(", segment)

    def test_lock_wait_is_measured_around_the_world_lock(self):
        begin = self.text.index("BotTelemetry_LockWaitBegin();")
        lock = self.text.index("CTSingleLock slBotWorld", begin)
        end = self.text.index("BotTelemetry_LockWaitEnd();", lock)
        self.assertLess(begin, lock)
        self.assertLess(lock, end)
        self.assertLess(end - lock, 400)

    def test_set_action_is_counted(self):
        call = self.text.index("ppls->SetAction(pa);")
        self.assertIn("BotTelemetry_Action(iLP);", self.text[call:call + 200])

    def test_missing_entity_is_counted(self):
        block = self.text[self.text.index("CPlayer *localInput"):]
        block = block[:block.index("continue;")]
        self.assertIn("BotTelemetry_NoEntity();", block)

    def test_no_local_players_is_a_distinct_reason(self):
        self.assertIn("BOT_TM_REASON_NOLOCAL", self.text)
        self.assertIn("BotDriver_ReportState(BOT_TM_REASON_NOLOCAL", self.text)

    def test_watchdog_uses_no_engine_api(self):
        start = self.text.index("static DWORD WINAPI BotTelemetry_Watchdog")
        end = self.text.index("void BotTelemetry_Start", start)
        body = self.text[start:end]
        for forbidden in ("_pNetwork", "CPrintF", "BotLog", "CTSingleLock", "_pTimer"):
            self.assertNotIn(forbidden, body)

    def test_csv_header_matches_analyser(self):
        match = re.search(r"#columns,(.*?)\);", self.text, re.S)
        self.assertIsNotNone(match)
        blob = re.sub(r'"|\s', "", match.group(1))
        columns = blob.split(",")
        self.assertEqual(columns, bot_telemetry.COLUMNS)

    def test_telemetry_switches_exist(self):
        self.assertIn('_pShell->DeclareSymbol("user INDEX bot_iTelemetry;", &bot_iTelemetry);', self.text)
        self.assertIn(
            '_pShell->DeclareSymbol("user INDEX bot_bTelemetryConsole;", &bot_bTelemetryConsole);',
            self.text,
        )


class ProfileTests(unittest.TestCase):
    def test_ab_profiles_differ_in_exactly_one_line(self):
        a = read(CAND / "profiles" / "ab-A-render.ini").splitlines()
        b = read(CAND / "profiles" / "ab-B-nullrender.ini").splitlines()
        diffs = [(x, y) for x, y in zip(a, b) if x != y]
        self.assertEqual(len(a), len(b))
        self.assertEqual(len(diffs), 1)
        self.assertIn("bot_bNullRender", diffs[0][0])
        self.assertIn("bot_bNullRender", diffs[0][1])

    def test_every_profile_enables_the_driver_and_telemetry(self):
        for path in sorted((CAND / "profiles").glob("*.ini")):
            text = read(path)
            self.assertIn("bot_bEnabled = 1;", text, path.name)
            self.assertIn("bot_iTelemetry = 1;", text, path.name)
            self.assertIn("bot_bNullRender", text, path.name)


STUB = r'''
#include <cstdio>
#include <cstdarg>
#include <cstdlib>
#include <cstring>
typedef long LONG;
typedef long long LONGLONG;
typedef int BOOL;
typedef unsigned long DWORD;
typedef void* HANDLE;
typedef void* LPVOID;
typedef unsigned long long ULONGLONG;
struct LARGE_INTEGER { long long QuadPart; };
struct FILETIME { unsigned long dwLowDateTime, dwHighDateTime; };
struct ULARGE_INTEGER { unsigned long LowPart, HighPart; unsigned long long QuadPart; };
struct CRITICAL_SECTION { int x; };
struct CTimer { float TickQuantum; };
extern CTimer *_pTimer;
typedef int INDEX;
static INDEX bot_bEnabled=0, bot_iLogEvery=40, bot_iTelemetry=1, bot_bTelemetryConsole=0;
static INDEX bot_bDiagnostics=0, bot_iFireTicks=3, bot_bAutoCombat=0, bot_bObstacleAvoidance=0;
static float bot_fYawSpeed=45.0f, bot_fMoveFactor=1.0f, bot_fFirePeriod=1.0f;
#define FALSE 0
#define TRUE 1
#define NULL 0
#define INVALID_HANDLE_VALUE ((HANDLE)(long long)-1)
#define GENERIC_WRITE 0x40000000
#define FILE_SHARE_READ 1
#define FILE_SHARE_WRITE 2
#define CREATE_ALWAYS 2
#define FILE_ATTRIBUTE_NORMAL 0x80
#define THREAD_PRIORITY_LOWEST (-2)
#define WINAPI
#define _snprintf snprintf
static void CPutString(const char *s) { (void)s; }
static void BotLog(const char *format, ...) {
  char buf[2048]; va_list ap; va_start(ap, format);
  vsnprintf(buf, sizeof(buf), format, ap); va_end(ap); CPutString(buf);
}
static BOOL QueryPerformanceFrequency(LARGE_INTEGER *p) { p->QuadPart=1000000; return 1; }
static BOOL QueryPerformanceCounter(LARGE_INTEGER *p) { static long long t=0; t+=1000; p->QuadPart=t; return 1; }
static void GetSystemTimeAsFileTime(FILETIME *p) { p->dwLowDateTime=0; p->dwHighDateTime=0; }
static HANDLE GetCurrentProcess(void) { return 0; }
static BOOL GetProcessTimes(HANDLE, FILETIME*, FILETIME*, FILETIME*k, FILETIME*u) {
  k->dwLowDateTime=0; k->dwHighDateTime=0; u->dwLowDateTime=0; u->dwHighDateTime=0; return 1; }
static HANDLE GetCurrentThread(void) { return 0; }
static BOOL SetThreadPriority(HANDLE,int) { return 1; }
static void Sleep(DWORD) {}
static HANDLE CreateThread(void*, unsigned long, DWORD (WINAPI *)(LPVOID), void*, unsigned long, unsigned long*) { return 0; }
static void InitializeCriticalSection(CRITICAL_SECTION*) {}
static void EnterCriticalSection(CRITICAL_SECTION*) {}
static void LeaveCriticalSection(CRITICAL_SECTION*) {}
static long InterlockedIncrement(volatile LONG *p) { return ++*p; }
static long InterlockedExchange(volatile LONG *p, long v) { long o=*p; *p=v; return o; }
static long InterlockedExchangeAdd(volatile LONG *p, long v) { long o=*p; *p+=v; return o; }
static long InterlockedCompareExchange(volatile LONG *p, long e, long c) { long o=*p; if (o==c) *p=e; return o; }
static DWORD GetModuleFileNameA(void*, char *b, DWORD n) { snprintf(b,n,"C:\\\\game\\\\Bin\\\\SeriousSam.exe"); return 40; }
static HANDLE CreateFileA(const char*, DWORD, DWORD, void*, DWORD, DWORD, void*) { return (HANDLE)1; }
static BOOL WriteFile(HANDLE, const void*, DWORD n, DWORD *written, void*) { *written=n; return 1; }
'''


@unittest.skipUnless(shutil.which("g++"), "g++ not installed")
class TelemetrySyntaxTests(unittest.TestCase):
    def test_telemetry_block_is_valid_cpp(self):
        driver = read(CAND / "BotDriver.cpp")
        start = driver.index("/* P0 evidence telemetry")
        marker = driver.index("void BotTelemetry_PaceFrame", start)
        end = driver.index("/* ------------------------------------------------------------------------ */", marker)
        source = (
            STUB
            + "\n"
            + read(CAND / "BotTelemetry.h")
            + "\n"
            + driver[start:end]
            + "\nint main(void){return 0;}\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "telemetry.cpp"
            path.write_text(source, encoding="utf-8")
            proc = subprocess.run(
                ["g++", "-std=c++11", "-Wall", "-Wextra", "-Wno-unused-parameter", "-fsyntax-only", str(path)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
