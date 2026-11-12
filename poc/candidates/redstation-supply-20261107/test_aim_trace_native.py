"""Compile the exact passive native log block; no Retail process or ABI claim."""
import pathlib,subprocess,tempfile,unittest
P=pathlib.Path(__file__).parent
class NativeTrace(unittest.TestCase):
 def test_actual_block_formats_and_no_state_writes(self):
  s=(P/'BotDriver.cpp').read_text()
  self.assertIn('aimTraceEnabled=bot_bDiagnostics && bot_iLogEvery>0 && bs.bs_iTick%bot_iLogEvery==0',s)
  block=s[s.index('    if(aimTraceCaptured && player){'):s.index('    if(bot_bDiagnostics&&bot_bSupplyNavigation&&player)')]
  self.assertNotIn('GetPlayerWeapons',block);self.assertNotIn('GetPlayerEntity',block)
  code=r'''
#include "bot_human.h"
#include <cassert>
#include <cstdarg>
#include <cstdio>
#include <cstring>
using ULONG=unsigned long;
struct V{float a[3]={1,2,3};float operator()(int i)const{return a[i-1];}};
struct PL{V pl_OrientationAngle;};
struct Player{ULONG en_ulID=123;PL en_plPlacement,en_plViewpoint;V m_aLastRotation,m_aLocalRotation;};
struct Supply{unsigned generation=4;}supply;
const Supply& BotSupplyState(int){return supply;}
struct State{int bs_iTick=10;float bs_aHeading=4,bs_aPitch=5;}bs;
struct PA{V pa_aRotation;ULONG pa_ulButtons=1;}pa;
int logs=0;
void BotLog(const char* fmt,...) __attribute__((format(printf,1,2)));
void BotLog(const char* fmt,...){char buf[2048];va_list args;va_start(args,fmt);int n=vsnprintf(buf,sizeof(buf),fmt,args);va_end(args);assert(n>0&&n<int(sizeof(buf)));++logs;}
int main(){
 Player p,other;Player* player=&p;Player* localInput=&other;
 botcore::HumanAimTrace aimTrace;botcore::BotCommand aimTraceCommand;
 V aimInputBefore,aimPacketBefore;int iLP=0,entityId=123,supplyActive=1,cecilFloorStatus=2,aimCurrent=2,aimWanted=2;
 const ULONG BOT_PLACT_FIRE=1;
 Player before=p,beforeOther=other;PA beforePa=pa;State beforeBs=bs;
 for(int pass=0;pass<3;++pass){bool aimTraceCaptured=pass!=0;
'''+block+r'''
 assert(logs==pass*2);assert(!memcmp(&before,&p,sizeof(p)));assert(!memcmp(&beforeOther,&other,sizeof(other)));assert(!memcmp(&beforePa,&pa,sizeof(pa)));assert(!memcmp(&beforeBs,&bs,sizeof(bs)));
 }
 puts("native passive trace block PASS");
}
'''
  with tempfile.TemporaryDirectory()as tmp:
   src=pathlib.Path(tmp)/'test.cpp';exe=pathlib.Path(tmp)/'test';src.write_text(code)
   subprocess.run(['g++','-std=c++14','-O1','-Werror=format','-fsanitize=address,undefined','-I',str(P),'-I',str(P.parents[1]/'botcore'),str(src),'-o',str(exe)],check=True)
   subprocess.run([str(exe)],check=True)
if __name__=='__main__':unittest.main()
