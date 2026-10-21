"""Sampled fire bits alias phased pulses; compile the real cumulative counter."""
import shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp"
@unittest.skipUnless(shutil.which("g++"),"g++ unavailable")
class CombatFireCounter(unittest.TestCase):
    def test_phased_pulses_count_and_respawn_does_not(self):
        text=SOURCE.read_text()
        start=text.index("    // Count emitted combat fire input independently of sampled status logs.")
        end=text.index("    BotTelemetry_Action(iLP);",start)
        block=text[start:end]
        cpp=r"""
#include <cstdio>
struct State {unsigned long bs_ulCombatFireActions=0;}bs;
bool bFire=false,automatic=true,respawnInput=false;
void count(){
"""+block+r"""
}
int main(){
 for(int slot=0;slot<4;++slot){
  bs.bs_ulCombatFireActions=0;
  for(int tick=1;tick<=20;++tick){bFire=((tick+slot*5)%20)<3;count();}
  if(bs.bs_ulCombatFireActions!=3){puts("FAIL phased fire undercount");return 1;}
 }
 bs.bs_ulCombatFireActions=0;respawnInput=true;bFire=true;
 for(int tick=0;tick<20;++tick)count();
 if(bs.bs_ulCombatFireActions){puts("FAIL respawn counted as combat");return 1;}
 respawnInput=false;automatic=false;count();
 if(bs.bs_ulCombatFireActions){puts("FAIL manual test counted as combat");return 1;}
 puts("COMBAT FIRE COUNTER PASS");
}
"""
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"counter.cpp";e=Path(d)/"counter";p.write_text(cpp)
            b=subprocess.run(["g++","-std=c++17",str(p),"-o",str(e)],capture_output=True,text=True)
            self.assertEqual(b.returncode,0,b.stderr)
            run=subprocess.run([str(e)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn("bs.bs_ulCombatFireActions=0;",text)
        self.assertIn("combat_fire_actions=%lu",text)
class ActivityParser(unittest.TestCase):
    def test_unsampled_fire_is_visible_through_counter_delta(self):
        from tools import qualify_integrated_wine as q
        logs="\n".join("[BotDriver] bot0 tick=%d pos=(%d,0,0) heading=0 fire=0 combat_fire_actions=%d"%r for r in [(20,0,10),(40,1,13),(60,2,13)])
        got=q.slot_activity(logs,1)["0"]
        self.assertTrue(got["fired"])
        self.assertTrue(got["moved"])
        self.assertEqual(got["fire_actions_delta"],3)
    def test_sampled_respawn_bit_is_not_combat(self):
        from tools import qualify_integrated_wine as q
        logs="\n".join("[BotDriver] bot0 tick=%d pos=(0,0,0) heading=0 fire=1 combat_fire_actions=10"%t for t in [20,40,60])
        self.assertFalse(q.slot_activity(logs,1)["0"]["fired"])
if __name__=="__main__":unittest.main()
