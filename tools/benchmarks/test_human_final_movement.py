"""Execute the adapter's last movement gate after obstacle overrides."""
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FinalMovement(unittest.TestCase):
    def test_final_gate_checks_both_headings_and_keeps_aim_fire(self):
        text = (ROOT / 'poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp').read_text()
        start = text.index('    } else { bs.bs_navigation.Reset(); bs.bs_navPlayer=NULL; }')
        start = text.index('\n', start) + 1
        end = text.index('    // 2) fire decision', start)
        block = text[start:end]
        fixture = r'''
#include <cassert>
#include <algorithm>
#include <cmath>
typedef float FLOAT;
struct V { float v[3]; float operator()(int i) const {return v[i-1];} };
struct CPlacement3D { V pl_PositionVector, pl_OrientationAngle; };
struct Player {V m_aLastRotation={{20,0,0}};float GetHealth(){return 25;}} self,*player=&self;
CPlacement3D BotCombatEye(Player*){return {{{10,2,-20}},{{90,0,0}}};}
template<class T>T Clamp(T x,T a,T b){return std::min(b,std::max(a,x));}
namespace botcore {
struct HumanBotPolicy {
  bool deny_observed=false,deny_intended=false;int calls=0;
  bool AllowFinalMovement(double x,double y,double z,double yaw,double f,double s){
    assert(x==10 && y==2 && z==-20 && f==.9f && s==.25f);++calls;
    assert(yaw==90 || yaw==120);
    return !(yaw==90?deny_observed:deny_intended);
  }
};
}
botcore::HumanBotPolicy policy;
botcore::HumanBotPolicy &BotHumanPolicy(int){return policy;}
template<class...Args>void BotLog(const char*,Args...){}
struct {float bs_aHeading=50;int bs_iTick=20;}bs;
int bot_bHumanAI=1,automatic=1,combatDeathmatch=1,iLP=0,bot_iLogEvery=20;
float humanStrafe=.5f,bot_fStrafeScale=.5f,moveFactor=.9f;
bool humanFire=true,testAimReady=true;
void final_gate(){
''' + block + r'''
}
int main(){
  policy.deny_observed=true;final_gate();
  assert(moveFactor==0 && humanStrafe==0 && humanFire && testAimReady && bs.bs_aHeading==50);
  policy.deny_observed=false;policy.deny_intended=true;
  moveFactor=.9f;humanStrafe=.5f;policy.calls=0;final_gate();
  assert(policy.calls==2 && moveFactor==0 && humanStrafe==0 && humanFire && testAimReady);
  policy.deny_intended=false;moveFactor=.9f;humanStrafe=.5f;final_gate();
  assert(moveFactor==.9f && humanStrafe==.5f);
  bot_bHumanAI=0;policy.deny_observed=true;policy.calls=0;final_gate();
  assert(moveFactor==.9f && humanStrafe==.5f && policy.calls==0);
}
'''
        with tempfile.TemporaryDirectory() as directory:
            cpp = Path(directory) / 'final.cpp'
            exe = Path(directory) / 'final'
            cpp.write_text(fixture)
            build = subprocess.run(['g++', '-std=c++17', str(cpp), '-o', str(exe)], capture_output=True, text=True)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(exe)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
