"""Compile the driver's real ammo adapter against pinned weapon-field stubs."""
import shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp"
@unittest.skipUnless(shutil.which("g++"),"g++ unavailable")
class FullAmmoAdapter(unittest.TestCase):
    def test_all_finite_reserves_gate_usable_weapon_mask(self):
        text=SOURCE.read_text()
        if "static uint32_t BotCombatUsableWeapons(" in text:
            start=text.index("static uint32_t BotCombatUsableWeapons(")
            end=text.index("static BOOL BotCombatVisible(",start)
            real=text[start:end]
        else:
            # Compile the pre-fix adapter exactly as used by the human branch.
            start=text.index("          const botcore::AmmoInfo humanAmmo=")
            end=text.index("          world.current_weapon=",start)
            real="static uint32_t BotCombatUsableWeapons(CPlayerWeapons* hw){struct {uint32_t usable_weapons;} world;\n"+text[start:end]+"return world.usable_weapons;}\n"
        cpp=r"""
#include <cstdint>
#include <cstdio>
#include "bot_combat.h"
struct CPlayerWeapons{
 uint32_t m_iAvailableWeapons=0x3fff;
 int m_iBullets=0,m_iShells=0,m_iNapalm=0,m_iElectricity=0,m_iSniperBullets=0;
 int m_iRockets=0,m_iGrenades=0,m_iIronBalls=0;
};
"""+real+r"""
int main(){
 CPlayerWeapons w;
 if(BotCombatUsableWeapons(&w)!=((1u<<0)|(1u<<1)|(1u<<2)|(1u<<9))){puts("FAIL empty finite weapons selected");return 1;}
 w.m_iBullets=w.m_iNapalm=w.m_iElectricity=w.m_iSniperBullets=1;w.m_iShells=2;
 w.m_iRockets=w.m_iGrenades=w.m_iIronBalls=1;
 if(BotCombatUsableWeapons(&w)!=0x3fff){puts("FAIL loaded weapon lost");return 1;}
 w.m_iRockets=0;if(BotCombatUsableWeapons(&w)!=(0x3fff&~(1u<<7)))return 1;
 w.m_iRockets=1;w.m_iGrenades=0;if(BotCombatUsableWeapons(&w)!=(0x3fff&~(1u<<8)))return 1;
 w.m_iGrenades=1;w.m_iIronBalls=0;if(BotCombatUsableWeapons(&w)!=(0x3fff&~(1u<<13)))return 1;
 puts("FULL AMMO ADAPTER PASS");
}
"""
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"ammo.cpp";e=Path(d)/"ammo";p.write_text(cpp)
            build=subprocess.run(["g++","-std=c++17","-I"+str(ROOT/"poc/botcore"),str(p),"-o",str(e)],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run([str(e)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn("world.usable_weapons=BotCombatUsableWeapons(hw);",text)
        self.assertIn("BotCombatUsableWeapons(weapons),",text)
if __name__=="__main__":unittest.main()
