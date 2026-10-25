"""Run the real engine-boundary search branch with native movement stubs."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"poc/candidates/integrated-human-cpu-20261021/BotDriver.cpp"
STUB=r'''
#include <cstdio>
typedef int BOOL;
typedef float FLOAT;
#define FALSE 0
#define TRUE 1
struct Player {float health=100;float GetHealth(){return health;}} self;
Player*player=&self;
struct State {float bs_aHeading=0;}bs;
float humanScanYaw=0.5f,moveFactor=1,humanEscapeForward=-1;
bool deathmatch=true;
void search(){
'''
END=r'''
}
int main(){
 search();
 if(moveFactor!=1 || bs.bs_aHeading!=0.5f){puts("FAIL healthy search never reaches obstacle navigation");return 1;}
 moveFactor=0;search();
 if(moveFactor!=0){puts("FAIL stationary/unarmed input overridden");return 1;}
 humanEscapeForward=0;moveFactor=1;search();
 if(moveFactor!=0){puts("FAIL escape turn must hold forward input");return 1;}
 humanEscapeForward=.9f;moveFactor=1;search();
 if(moveFactor!=.9f){puts("FAIL escape travel ignored");return 1;}
 humanEscapeForward=-1;
 self.health=0;moveFactor=1;search();
 if(moveFactor!=0){puts("FAIL dead movement");return 1;}
 player=nullptr;moveFactor=1;search();
 if(moveFactor!=0){puts("FAIL absent player movement");return 1;}
 player=&self;self.health=100;deathmatch=false;moveFactor=1;search();
 if(moveFactor!=0){puts("FAIL non-deathmatch movement");return 1;}
 puts("HUMAN SEARCH APPLICATION PASS");
}
'''
@unittest.skipUnless(shutil.which("g++"),"g++ unavailable")
class HumanSearchApplication(unittest.TestCase):
    def test_search_feeds_existing_navigation_without_hidden_target(self):
        text=SOURCE.read_text()
        start=text.index("      } else if (bot_bHumanAI) {",text.index("      if (decision.target>=0) {"))
        start=text.index("\n",start)+1
        end=text.index("      } else if (player!=NULL",start)
        block=text[start:end]
        with tempfile.TemporaryDirectory() as d:
            cpp=Path(d)/"search.cpp";exe=Path(d)/"search"
            cpp.write_text(STUB+block+END)
            build=subprocess.run(["g++","-std=c++17",str(cpp),"-o",str(exe)],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run([str(exe)],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
if __name__=="__main__":unittest.main()
