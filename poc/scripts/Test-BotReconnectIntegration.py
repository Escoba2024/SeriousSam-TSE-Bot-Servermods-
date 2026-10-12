"""Exercise the actual SDK reconnect block with a deterministic failed JoinGame.

Only the slow engine/network boundary is doubled. Extracted production code is
compiled, so the test catches a retry that is implemented but never called.
Usage: python this.py GAME_CPP BOTDRIVER_CPP OUTPUT_CPP HEADER_DIRECTORY
"""
import pathlib
import sys

game_path, driver_path, output_path, header_dir = map(pathlib.Path, sys.argv[1:])
game = game_path.read_text(encoding="utf-8")
driver = driver_path.read_text(encoding="utf-8")
loading = game_path.with_name("LoadingHook.cpp").read_text(encoding="utf-8")
block = game.split("  // if server was restarted\n", 1)[1].split("  if (_bStartProfilingNextTime)", 1)[0]

def function(text, signature):
    start = text.index(signature)
    brace = text.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]

new_hook = "BotDriver_HandleReconnect" in block
includes = '#include "bot_reconnect.h"\n' if new_hook else ""
production = ""
if new_hook:
    production = "static botcore::Reconnect _botReconnect;\nstatic CTString _strBotReconnectAddress;\n"
    production += function(driver, "void BotDriver_StopGame(void)") + "\n"
    production += function(driver, "void BotDriver_CancelReconnect(void)") + "\n"
    if "BotDriver_ReconnectAbortRequested" in driver:
        production += function(driver, "static BOOL BotDriver_ReconnectAbortRequested(void)") + "\n"
    production += function(driver, "BOOL BotDriver_HandleReconnect(CGame *pgame)") + "\n"
else:
    production = "void BotDriver_StopGame(void) {}\nvoid BotDriver_CancelReconnect(void) {}\n"
stop_prefix = function(game, "void CGame::StopGame(void)").split("{", 1)[1].split("  // disable computer quickly", 1)[0]
loading_break = loading.split("  // if user presses escape\n", 1)[1].split("#if USECUSTOMTEXT", 1)[0]
production += "\nvoid LoadingBreak(CProgressHookInfo *pphi) {\n" + loading_break + "}\n"

harness = r'''
#include <string>
#include <cstdio>
#include <cstdlib>
#include <atomic>
// Doubled Windows boundary used by the current extracted StopGame hook.
static std::atomic<long> _botNavigationResetRequested{0};
static long InterlockedExchange(std::atomic<long>* value, long desired) {
  return value->exchange(desired);
}
typedef bool BOOL;
struct CTString : std::string {
  using std::string::string;
  CTString(const char *v): std::string(v) {}
  int Length() const { return static_cast<int>(size()); }
  operator const char*() const { return c_str(); }
};
const BOOL TRUE=true, FALSE=false;
static int bot_bEnabled=1;
struct CNetworkSession { explicit CNetworkSession(const CTString&) {} };
struct Network {
  bool server=false, finished=true, disconnected=true;
  BOOL IsServer() { return server; }
  BOOL IsGameFinished() { return finished; }
  BOOL IsDisconnected() { return disconnected; }
} network, *_pNetwork=&network;
struct TimerValue { double value; double GetSeconds() { return value; } };
struct Timer { double now=0; TimerValue GetHighPrecisionTimer() { return {now}; } } timer, *_pTimer=&timer;
static void BotLog(const char*, ...) {}
typedef unsigned long ULONG;
const int VK_ESCAPE=27;
static BOOL _bUserBreakEnabled=TRUE;
static bool escapePressed=false, closePending=false, quitPending=false, stopOnPeek=false, quitDuringDispatch=false, quitAtSystemPeek=false;
void BotDriver_CancelReconnect(void);
static unsigned int GetAsyncKeyState(int) { return escapePressed ? 0x8000 : 0; }
const int WM_QUIT=0x12, WM_CLOSE=0x10, WM_SYSCOMMAND=0x112;
const int PM_NOREMOVE=0, PM_REMOVE=1, SC_CLOSE=0xf060;
struct MSG { void *hwnd; int message; unsigned long wParam; long lParam; };
static int systemMessages=0;
static BOOL PeekMessage(MSG *msg, void*, int first, int, int remove) {
  if(stopOnPeek) { stopOnPeek=false; BotDriver_CancelReconnect(); }
  if(first==WM_SYSCOMMAND && quitAtSystemPeek) { quitAtSystemPeek=false; quitPending=true; }
  // Win32 retrieves WM_QUIT independently of the message filter.
  if(quitPending) {
    msg->hwnd=nullptr; msg->message=WM_QUIT; msg->wParam=7; msg->lParam=0;
    if(remove==PM_REMOVE) quitPending=false;
    return true;
  }
  if(first==WM_SYSCOMMAND && systemMessages>0) {
    msg->hwnd=nullptr; msg->message=WM_SYSCOMMAND;
    msg->wParam=(systemMessages>1 || quitDuringDispatch) ? 0xf020 : SC_CLOSE|3; msg->lParam=0;
    if(remove==PM_REMOVE) --systemMessages;
    return true;
  }
  return first==WM_CLOSE && closePending;
}
static BOOL PostMessage(void*, int, unsigned long, long) { closePending=true; return true; }
static void PostQuitMessage(int) { quitPending=true; }
static void TranslateMessage(MSG*) {}
static void DispatchMessage(MSG*) { if(quitDuringDispatch){quitDuringDispatch=false;quitPending=true;} }
static void Sleep(int ms) { timer.now+=ms/1000.0; }
static char* TRANS(const char *text) { return const_cast<char*>(text); }
struct CProgressHookInfo { float phi_fCompleted; };
void LoadingBreak(CProgressHookInfo*);
void BotDriver_StopGame(void);
void BotDriver_CancelReconnect(void);
struct CGame {
  CTString gam_strJoinAddress="127.0.0.1:25600";
  BOOL gm_bGameOn=true;
  int attempts=0, failures=1;
  bool abortJoin=false;
  bool throwJoin=false;
  bool cancelWait=false, closeWait=false, directCloseWait=false, quitWait=false, stopWait=false;
  bool quitDispatchWait=false, quitPeekWait=false;
  bool runningMode=true;
  void StopGame() { __STOP_HOOK__ gm_bGameOn=false; }
  BOOL JoinGame(const CNetworkSession&) {
    StopGame(); ++attempts;
    if (throwJoin) throw 7;
    if (abortJoin) {
      CProgressHookInfo progress={1};
      escapePressed=true;
      try { LoadingBreak(&progress); } catch (char*) { escapePressed=false; return FALSE; }
    }
    // Reproduce the real boundary: failed join stays stopped, success resumes.
    if (failures-- > 0) {
      if(cancelWait) escapePressed=true;
      if(closeWait) systemMessages=2;
      if(directCloseWait) closePending=true;
      if(quitWait) quitPending=true;
      if(stopWait) stopOnPeek=true;
      if(quitDispatchWait) { systemMessages=1; quitDuringDispatch=true; }
      if(quitPeekWait) quitAtSystemPeek=true;
      return FALSE;
    }
    gm_bGameOn=true; network.finished=false; network.disconnected=false;
    return TRUE;
  }
  void ReconnectPoll();
  void Frame() {
    // The native EXE stops calling GameMainLoop after gameOn becomes false.
    if(!gm_bGameOn) runningMode=false;
    if(runningMode) ReconnectPoll();
  }
};
'''
checks = r'''
static void check(bool v, const char *text) {
  if (!v) { std::fprintf(stderr,"FAIL: %s\n",text); std::exit(1); }
}
int main() {
  CGame game;
  timer.now=0; game.ReconnectPoll();
  timer.now=2; game.ReconnectPoll();
  timer.now=21; game.ReconnectPoll();
  check(game.attempts==2 && game.gm_bGameOn && game.runningMode, "failed JoinGame must recover before native EXE disables GameMainLoop");
  timer.now=50; game.ReconnectPoll();
  check(game.attempts==2, "healthy game must not rejoin");
  network.finished=true; network.disconnected=true;
  timer.now=60; game.ReconnectPoll();
  game.StopGame();
  timer.now=100; game.ReconnectPoll();
  check(game.attempts==2, "explicit StopGame cancels pending map reconnect");
  game.gm_bGameOn=true;
  timer.now=110; game.ReconnectPoll();
  game.gam_strJoinAddress="127.0.0.1:25610"; game.gm_bGameOn=false;
  timer.now=130; game.ReconnectPoll();
  check(game.attempts==2, "target change cancels old pending recovery");
  bot_bEnabled=0; game.gm_bGameOn=true;
  timer.now=140; game.ReconnectPoll();
  check(game.attempts==3 && game.gm_bGameOn, "bot disabled retains original SDK reconnect");
  bot_bEnabled=1; network.finished=true; network.disconnected=true;
  timer.now=150; game.ReconnectPoll();
  game.abortJoin=true;
  timer.now=152; game.ReconnectPoll();
  timer.now=180; game.ReconnectPoll();
  check(game.attempts==4 && !game.gm_bGameOn, "loading-hook user break cancels failed join retry");
  game.abortJoin=false; game.throwJoin=true; game.gm_bGameOn=true;
  timer.now=200; game.ReconnectPoll();
  try { timer.now=202; game.ReconnectPoll(); check(false, "unexpected JoinGame exception must propagate"); }
  catch (int) {}
  game.throwJoin=false; game.gm_bGameOn=true;
  timer.now=210; game.ReconnectPoll();
  timer.now=212; game.ReconnectPoll();
  check(game.attempts==6 && game.gm_bGameOn, "exception must not leave retry permanently in-flight");
  network.finished=true; network.disconnected=true;
  CGame cancel; cancel.cancelWait=true;
  timer.now=300; cancel.Frame(); timer.now=302; cancel.Frame();
  check(cancel.attempts==1 && !cancel.gm_bGameOn, "Escape during backoff cancels without another join");
  escapePressed=false;
  CGame close; close.closeWait=true;
  timer.now=400; close.Frame(); timer.now=402; close.Frame();
  check(close.attempts==1 && !close.gm_bGameOn && closePending, "queued minimize must not hide close; close remains for native message loop");
  closePending=false; systemMessages=0;
  CGame directClose; directClose.directCloseWait=true;
  timer.now=500; directClose.Frame(); timer.now=502; directClose.Frame();
  check(directClose.attempts==1 && closePending, "WM_CLOSE cancels and stays queued");
  closePending=false;
  CGame quit; quit.quitWait=true;
  timer.now=600; quit.Frame(); timer.now=602; quit.Frame();
  check(quit.attempts==1 && quitPending, "WM_QUIT cancels and stays queued");
  quitPending=false;
  CGame stop; stop.stopWait=true;
  timer.now=700; stop.Frame(); timer.now=702; stop.Frame();
  check(stop.attempts==1 && !stop.gm_bGameOn, "Stop during synchronous PeekMessage delivery does not resurrect retry");
  CGame quitRace; quitRace.quitDispatchWait=true;
  timer.now=800; quitRace.Frame(); timer.now=802; quitRace.Frame();
  check(quitRace.attempts==1 && quitPending, "WM_QUIT delivered during system-command dispatch is preserved");
  quitPending=false; systemMessages=0;
  CGame quitPeek; quitPeek.quitPeekWait=true;
  timer.now=900; quitPeek.Frame(); timer.now=902; quitPeek.Frame();
  check(quitPeek.attempts==1 && quitPending, "WM_QUIT retrieved despite system-command filter is preserved");
  std::puts("BOT RECONNECT GAME-HOOK INTEGRATION PASS");
}
'''
checks=checks.replace("game.ReconnectPoll()", "game.Frame()")
checks=checks.replace("game.gm_bGameOn=true;", "game.gm_bGameOn=true; game.runningMode=true;")
output_path.write_text(includes + harness.replace("__STOP_HOOK__", stop_prefix) + production + "\nvoid CGame::ReconnectPoll() {\n" + block + "}\n" + checks, encoding="utf-8")
print(output_path)
