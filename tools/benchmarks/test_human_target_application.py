"""Compile the real driver's target-application branch against small engine stubs.
Covers vanished opponents and frozen last-seen distance at the engine boundary.
Run only outside CPU qualification windows.
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp"
STUB=r'''
#include <cmath>
#include <cstdio>
#include <stdexcept>
#include "bot_combat.h"
#include "bot_weapon_input.h"
typedef int INDEX;
typedef int BOOL;
typedef float FLOAT;
typedef unsigned long ULONG;
#define FALSE 0
#define TRUE 1
struct V {
 float a[3]={0,0,0};
 float operator()(int i)const{return a[i-1];}
 V operator-(const V&o)const{V d;for(int i=0;i<3;i++)d.a[i]=a[i]-o.a[i];return d;}
 float Length()const{return std::sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2]);}
};
struct Placement {V pl_PositionVector;};
struct Weapons {
 int m_iWantedWeapon=2,m_iCurrentWeapon=2;
 int m_iBullets=10,m_iShells=10,m_iNapalm=10,m_iElectricity=10,m_iSniperBullets=10;
};
struct Player {V m_aLastRotation;ULONG m_ulLastButtons=0;Weapons w;Weapons*GetPlayerWeapons(){return &w;}};
Player self,other;Player *player=&self,*target=nullptr,*liveTarget=nullptr;
struct CEntity {static void*GetPlayerEntity(int){return liveTarget;}};
typedef Player CPlayer;typedef Weapons CPlayerWeapons;
int eyeReads=0;
Placement BotCombatEye(Player*p){++eyeReads;if(!p)throw std::runtime_error("null target dereference");Placement out;if(p==&other)out.pl_PositionVector.a[0]=1000;return out;}
void BotLog(const char*,...){}
int bot_iLogEvery=0,bot_bHumanAI=1,iLP=0;
struct State {FLOAT bs_aHeading=0,bs_aPitch=0;int bs_iTick=100;botcore::CombatWeaponInput bs_weaponInput;}bs;
botcore::CombatDecision decision={1,2,0,0,0,true};
FLOAT moveFactor=0,humanTargetDistance=30;BOOL testAimReady=FALSE,combatHold=FALSE;
INDEX combatWeapon=0;ULONG combatSelect=0;
void apply() {
'''
END=r'''
}
int main(){
 try{
  liveTarget=nullptr;apply();
  if(eyeReads!=0 || testAimReady || combatHold){std::puts("FAIL vanished target/memory boundary");return 1;}
  liveTarget=&other;eyeReads=0;humanTargetDistance=3;combatHold=FALSE;apply();
  if(eyeReads!=0 || !combatHold){std::puts("FAIL live hidden target distance leaked");return 1;}
 }catch(const std::exception&e){std::printf("FAIL %s\n",e.what());return 1;}
 std::puts("TARGET APPLICATION PASS");return 0;
}
'''
@unittest.skipUnless(shutil.which("g++"),"g++ unavailable")
class HumanTargetApplication(unittest.TestCase):
    def test_uses_memory_without_dereferencing_vanished_or_hidden_target(self):
        text=SOURCE.read_text()
        start=text.index("      if (decision.target>=0) {")
        end=text.index("      } else if (bot_bHumanAI)",start)
        block=text[start:end]+"\n}\n"
        with tempfile.TemporaryDirectory() as d:
            cpp=Path(d)/"application.cpp";exe=Path(d)/"application"
            cpp.write_text(STUB+block+END)
            build=subprocess.run(["g++","-std=c++17","-I"+str(ROOT/"poc/botcore"),str(cpp),"-o",str(exe)],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run([str(exe)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
if __name__=="__main__":unittest.main()
