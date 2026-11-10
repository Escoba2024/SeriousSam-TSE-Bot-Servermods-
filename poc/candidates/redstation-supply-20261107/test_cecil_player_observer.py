#!/usr/bin/env python3
"""Compile the actual bounded read-only player observer, not a native runtime proof."""
from pathlib import Path
import subprocess,tempfile

PREFIX=r'''
#include <cstdio>
#include <cstdarg>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <string>
using INDEX=int;using ULONG=unsigned long;
const int ENF_DELETED=1;
struct V {float v[3]={};float operator()(int i)const{return v[i-1];}};
struct CWorld{} world,foreign;
struct CEntity {CWorld* en_pwoWorld=&world;ULONG en_ulID=10,flags=0;unsigned GetFlags()const{return flags;}};
struct Stack {INDEX sa_UsedCount=0,sa_Count=0;long* sa_Array=nullptr;};
struct CPlayer:CEntity {Stack en_stslStateStack;CEntity* m_penCamera=nullptr;CEntity* m_penActionMarker=nullptr;
 ULONG m_ulFlags=513,m_ulLastButtons=0;V en_vDesiredTranslationRelative,en_vCurrentTranslationAbsolute;
 CWorld* GetWorld(){return en_pwoWorld;}}; // Actual SDK107 accessor is nonconst.
struct CPlayerAction {V pa_vTranslation,pa_aRotation;ULONG pa_ulButtons=0;};
struct Network {double GetGameTime()const{return 123.5;}}network,*_pNetwork=&network;
std::string output;int logs=0,checks=0,failures=0;
void BotLog(const char* format,...){char b[2048];va_list a;va_start(a,format);vsnprintf(b,sizeof b,format,a);va_end(a);output=b;++logs;}
void check(bool ok,const char* label){++checks;if(!ok){++failures;std::printf("FAIL %s\n",label);}}
'''
TEST=r'''
int main(){
 CPlayer p;CPlayerAction a;a.pa_vTranslation.v[2]=-10;long states[2]={0x01910001,0x01910020};
 p.en_stslStateStack={2,2,states};CEntity cam;cam.en_ulID=99;p.m_penCamera=&cam;
 CPlayer before;std::memcpy(&before,&p,sizeof p);const auto input=a;BotPlayerObserverTelemetry(&p,2,2200,8,a);
 check(logs==1,"stationary native player with actual composed input emits one bounded snapshot");
 check(output.find("camera_present=1 camera=99 camera_valid=1")!=std::string::npos,"existing camera identity is explicit");
 check(output.find("states_valid=1 count=2 states=01910001,01910020")!=std::string::npos,"actual bounded player state IDs survive");
 check(!std::memcmp(&p,&before,sizeof p)&&!std::memcmp(&a,&input,sizeof a),"observer changes no player/action bytes");
 long wide[16];for(long& v:wide)v=-1;p.en_stslStateStack={16,16,wide};BotPlayerObserverTelemetry(&p,2,2200,8,a);
 check(output.find("states_valid=1 count=16 states=ffffffff,ffffffff")!=std::string::npos,"full sixteen-state stack stays bounded to native32bit IDs on64bit fixtures");
 p.en_stslStateStack={17,17,reinterpret_cast<long*>(1)};BotPlayerObserverTelemetry(&p,2,2220,8,a);
 check(output.find("states_valid=0 count=17 states=")!=std::string::npos,"oversized stack is reported without reading invalid memory");
 p.en_stslStateStack={1,0,reinterpret_cast<long*>(1)};BotPlayerObserverTelemetry(&p,2,2240,8,a);
 check(output.find("states_valid=0")!=std::string::npos,"capacity smaller than used count cannot authorize array reads");
 p.en_stslStateStack={1,1,nullptr};BotPlayerObserverTelemetry(&p,2,2260,8,a);
 check(output.find("states_valid=0")!=std::string::npos,"missing stack storage is invalid");
 cam.en_pwoWorld=&foreign;BotPlayerObserverTelemetry(&p,2,2280,8,a);
 check(output.find("camera_present=1 camera=0 camera_valid=0")!=std::string::npos,"foreign camera is not read as a valid local identity");
 cam.en_pwoWorld=&world;cam.flags=ENF_DELETED;BotPlayerObserverTelemetry(&p,2,2300,8,a);
 check(output.find("camera_present=1 camera=0 camera_valid=0")!=std::string::npos,"deleted camera remains distinguished from null");
 const int saved=logs;p.en_vCurrentTranslationAbsolute.v[0]=1;BotPlayerObserverTelemetry(&p,2,2320,8,a);
 check(logs==saved,"normally moving player generates no extra diagnostic row");
 p.en_vCurrentTranslationAbsolute.v[0]=0;a.pa_vTranslation.v[2]=0;BotPlayerObserverTelemetry(&p,2,2340,8,a);
 check(logs==saved,"neutral requested input is not diagnosed as a stalled action");
 a.pa_vTranslation.v[2]=-10;p.flags=ENF_DELETED;BotPlayerObserverTelemetry(&p,2,2360,8,a);
 check(logs==saved,"deleted player cannot generate observations");
 p.flags=0;BotPlayerObserverTelemetry(&p,-1,2380,8,a);BotPlayerObserverTelemetry(nullptr,0,2380,8,a);
 check(logs==saved,"invalid local/player are rejected");
 std::printf("player observer: %d checks, %d failures\n",checks,failures);return failures?1:0;
}
'''
def main():
    source=Path(__file__).with_name('BotDriver.cpp').read_text()
    start='// BEGIN CECIL PLAYER OBSERVER';end='// END CECIL PLAYER OBSERVER'
    if start not in source:raise AssertionError('bounded player observer absent')
    block=source.split(start,1)[1].split(end,1)[0]
    assert source.count('BotPlayerObserverTelemetry(player,iLP,bs.bs_iTick,state.generation,pa);')==1
    hook=source.index('BotPlayerObserverTelemetry(player,iLP,bs.bs_iTick,state.generation,pa);')
    assert source.rfind('if(bot_bSupplyNavigation&&player&&bs.bs_iTick%20==0)',0,hook)>source.index('ppls->SetAction(pa);')
    with tempfile.TemporaryDirectory(prefix='cecil-player-observer-')as tmp:
        cpp=Path(tmp)/'test.cpp';exe=Path(tmp)/'test';cpp.write_text(PREFIX+block+TEST)
        subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(cpp),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
if __name__=='__main__':main()
