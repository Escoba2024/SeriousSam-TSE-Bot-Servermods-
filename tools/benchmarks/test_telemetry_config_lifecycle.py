"""Exercise the real config writer before/after a late command-line script."""
from pathlib import Path
import shutil,subprocess,tempfile,unittest
ROOT=Path(__file__).resolve().parents[2]
CAND=ROOT/"poc/candidates/integrated-human-cpu-20261021"
STUB=r'''
#include <cstdio>
#include <cstdarg>
#include <string>
int bot_bEnabled=0,bot_iLogEvery=40,bot_iTelemetry=1;
struct Timer {float TickQuantum=.05f;} timer;
Timer* _pTimer=&timer;
int rows=0;std::string last;
void BotTelemetry_WriteLine(const char*fmt,...){char line[1024];va_list ap;va_start(ap,fmt);vsnprintf(line,sizeof line,fmt,ap);va_end(ap);last=line;++rows;}
void BotLog(const char*,...){}
'''
MAIN=r'''
int main(){
 BotTelemetry_Config(0,0,0);
 bot_bEnabled=1;bot_iLogEvery=20;
 BotTelemetry_Config(1,20,0);
 BotTelemetry_Config(1,20,0);
 if(rows!=2 || last.find("nullrender=1")==std::string::npos || last.find("bot_enabled=1")==std::string::npos){std::printf("FAIL rows=%d last=%s\n",rows,last.c_str());return 1;}
 return 0;
}
'''
@unittest.skipUnless(shutil.which("g++"),"g++ unavailable")
class ConfigLifecycle(unittest.TestCase):
 def test_late_script_refresh_and_unchanged_config_is_not_spammed(self):
  driver=(CAND/"BotDriver.cpp").read_text()
  block=driver[driver.index("void BotTelemetry_Config("):driver.index("void BotTelemetry_Note(")]
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/"test.cpp";exe=Path(d)/"test";source.write_text(STUB+block+MAIN)
   p=subprocess.run(["g++","-std=c++17",str(source),"-o",str(exe)],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stderr)
   p=subprocess.run([str(exe)],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stdout+p.stderr)
  game=(CAND/"Game.cpp").read_text();start=game.index("void CGame::GameMainLoop(")
  self.assertIn("BotTelemetry_Config(bot_bNullRender",game[start:start+500])
if __name__=="__main__":unittest.main()
