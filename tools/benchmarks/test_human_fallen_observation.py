"""Run the real adapter's death observation without inventing an origin pose."""
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class FallenObservation(unittest.TestCase):
    def test_lethal_damage_uses_actual_pose_and_health(self):
        source=(ROOT/'poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp').read_text()
        start=source.index('          botcore::WorldView fallen;')
        end=source.index('          moveFactor=0.0f;',start)
        block=source[start:end]
        fixture=r'''
#include "bot_human.h"
#include <cassert>
#include <cmath>
#define FALSE 0
struct V {double values[3];double operator()(int i)const{return values[i-1];}};
struct CPlacement3D {V pl_PositionVector;};
struct Player {double GetHealth(){return -50;}} self,*player=&self;
CPlacement3D BotCombatEye(Player*){return {{{10,2,-20}}};}
botcore::WorldView captured;
struct Capture {void BeginTick(const botcore::WorldView&w){captured=w;}} human;
struct {int bs_iTick=70;}bs;
void observe(){
'''+block+r'''
}
int main(){
 observe();assert(!captured.alive && captured.tick==70);
 assert(captured.health==-50 && captured.pose.x==10 && captured.pose.y==2 && captured.pose.z==-20);
 player=nullptr;observe();assert(!std::isfinite(captured.pose.x));
}
'''
        with tempfile.TemporaryDirectory() as d:
            cpp=Path(d)/'fallen.cpp';exe=Path(d)/'fallen';cpp.write_text(fixture)
            build=subprocess.run(['g++','-std=c++17','-I'+str(ROOT/'poc/botcore'),str(cpp),'-o',str(exe)],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run([str(exe)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
