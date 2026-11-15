"""Portable tests of actual production receipt, no Retail/ABI qualification."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
CAND=ROOT/'poc/candidates/redstation-supply-20261107'

class DriverFinalTests(unittest.TestCase):
    def test_actual_receipt_and_fixed_format(self):
        self.assertTrue((CAND/'driver_final_decision.h').is_file(), 'production receipt missing')
        cpp=r'''
#include "driver_final_decision.h"
#include <cassert>
#include <cmath>
#include <cstring>
#include <limits>
struct Move {bool active=true,ownsMovement=false,itemGoal=true,urgent=true,followGoal=false,useControl=false,flightGoal=false,activeFlight=false;
 int itemKind=2;double forward=.3,strafe=-.2,up=0,yaw_delta=7,pitch_delta=-3;unsigned flags=16,buttons=32;};
struct Vec {double v[3];double operator()(int i)const{return v[i-1];}};
struct Action {Vec pa_vTranslation{{1,2,3}},pa_aRotation{{4,5,6}},pa_aViewRotation{{7,8,9}};unsigned pa_ulButtons=0x123;};
int main(){
 using namespace botcore;
 assert(!CecilDriverFinalDue(false,true,true,20));
 assert(!CecilDriverFinalDue(true,false,true,20));
 assert(!CecilDriverFinalDue(true,true,false,20));
 assert(!CecilDriverFinalDue(true,true,true,19));
 assert(CecilDriverFinalDue(true,true,true,20));
 CecilDriverFinal d;CecilDriverFinalBegin(d,true,2,20,555,3,9);
 assert(d.admitted&&d.actor==555&&d.entryGeneration==3&&d.baselineMapPin==9);
 assert(!d.actualCurrentMapKnown&&!d.SameLife());
 assert(!d.supplyBlockEntered&&!d.ready);
 Move m;CecilDriverFinalSupply(d,true,m,3,555);
 assert(d.supplyBlockEntered&&d.ready&&d.supplyCalled);
 assert(d.proposalValid&&d.proposalBits==13&&d.proposal[0]==.3&&d.proposal[4]==-3);
 assert(d.proposalKind==2&&d.proposalFlags==16&&d.proposalButtons==32);
 m.active=m.ownsMovement=m.itemGoal=m.urgent=m.followGoal=m.useControl=m.flightGoal=m.activeFlight=true;
 CecilDriverFinalSupply(d,true,m,3,555);assert(d.proposalBits==255);
 assert(CecilDriverFinalPresence(d,true));assert(d.weaponsEvaluated&&d.weaponsPresent);
 assert(!CecilDriverFinalPresence(d,false));assert(d.weaponsEvaluated&&!d.weaponsPresent);
 d.safeCalled=false;d.safeStatus=17; // stale status must not become fresh
 Action a;CecilDriverFinalSubmit(d,a,3,555);
 assert(d.submitted&&d.SameLife());
 for(int i=0;i<3;++i){assert(d.translation[i]==i+1);assert(d.rotation[i]==i+4);assert(d.view[i]==i+7);}
 assert(d.buttons==0x123&&!d.safeCalled);
 char out[2048];int n=CecilDriverFinalFormat(out,sizeof(out),d);
 assert(n>0&&n<2048&&out[n]==0&&out[n-1]=='\n');
 assert(std::strstr(out,"[CecilDriverFinalV1]")&&std::strstr(out,"map_known=0"));
 assert(std::strstr(out,"safe=(0,")&&std::strstr(out,"life_link=1"));
 d.exitGeneration=4;assert(!d.SameLife());
 n=CecilDriverFinalFormat(out,sizeof(out),d);assert(std::strstr(out,"life_link=0"));
 d.rotation[0]=std::nextafter(1.0,2.0);
 n=CecilDriverFinalFormat(out,sizeof(out),d);assert(std::strstr(out,"rot=(1.0000000000000002,"));
 d.exitGeneration=3;d.exitActor=666;assert(!d.SameLife());
 CecilDriverFinal off;CecilDriverFinalBegin(off,false,1,20,77,2,1);
 CecilDriverFinalSupply(off,true,m,2,77);CecilDriverFinalSubmit(off,a,2,77);
 assert(!off.proposalValid&&!off.submitted);
 assert(CecilDriverFinalFormat(out,sizeof(out),off)==0);
 CecilDriverFinal missing;CecilDriverFinalBegin(missing,true,1,20,77,2,1);
 assert(!missing.supplyBlockEntered&&!missing.ready&&!missing.supplyCalled);
 CecilDriverFinalSupply(missing,false,m,2,77);assert(missing.supplyBlockEntered&&!missing.ready&&!missing.supplyCalled&&!missing.proposalValid);
 assert(!missing.SameLife());
 int reads=0;auto actualButtons=[&](){++reads;return 0x8001u;};
 auto passed=CecilDriverFinalValue(d,d.pollLastButtons,actualButtons());
 assert(reads==1&&passed==0x8001u&&d.pollLastButtons==passed);
 d.local=std::numeric_limits<int>::min();d.tick=std::numeric_limits<int>::min();d.baselineMapPin=std::numeric_limits<int>::min();
 d.actor=d.entryGeneration=d.exitGeneration=d.exitActor=~0u;
 d.proposalBits=d.proposalFlags=d.proposalButtons=d.modeBits=d.combatSelect=d.cecilButtons=d.buttons=~0u;
 d.preSupplyModeBits=d.arbitrationFlags=d.pollLastButtons=~0u;d.cachedTargetIndex=std::numeric_limits<int>::min();
 d.supplyCalled=d.proposalValid=d.weaponsEvaluated=d.weaponsPresent=true;
 d.supplyBlockEntered=d.ready=true;
 d.weaponPolled=d.travelKnife=d.firePolled=d.safeCalled=d.safeReacquire=d.safeCombat=true;
 d.proposalKind=d.preWeapon=d.finalWeapon=d.fireCurrent=d.fireWanted=d.pollWanted=d.safeStatus=std::numeric_limits<int>::min();
 for(double& x:d.proposal)x=-std::numeric_limits<double>::max();
 for(double& x:d.arbitration)x=-std::numeric_limits<double>::max();
 for(double& x:d.safeArgs)x=-std::numeric_limits<double>::max();
 for(double& x:d.safeAfter)x=-std::numeric_limits<double>::max();
 for(double& x:d.translation)x=-std::numeric_limits<double>::max();
 for(double& x:d.rotation)x=-std::numeric_limits<double>::max();
 for(double& x:d.view)x=-std::numeric_limits<double>::max();
 n=CecilDriverFinalFormat(out,sizeof(out),d);assert(n>0&&n<2048&&out[n]==0);
 // snprintf must report truncation; callers must never submit a truncated row.
 char small[8];assert(CecilDriverFinalFormat(small,sizeof(small),d)>=8);
 std::printf("PASS production receipt extreme bytes=%d\n",n);
}
'''
        with tempfile.TemporaryDirectory(prefix='driver-final-')as tmp:
            p=Path(tmp);(p/'test.cpp').write_text(cpp)
            subprocess.run(['g++','-std=c++14','-Wall','-Wextra','-Werror','-Wformat=2','-I',str(CAND),str(p/'test.cpp'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True)

if __name__=='__main__':unittest.main()
