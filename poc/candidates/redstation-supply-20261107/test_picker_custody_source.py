"""Exact whole-parent inversion and bounded actual-body operation comparisons."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
PINS={'BotSupplyNative.h':'777d196e44d21dc8ac1e5b0cce8fb54247833d7665ef9329ca64f50d97676504','BotDriver.cpp':'7af47d87aaaf4c51ebaca6f65d628cfec3c2544419be07e39b65e52b370eb386'}
def reverse(name,text):
    fixture=json.loads((HERE/'picker_custody_inverse.json').read_text())
    if fixture['parent_sha256']!=PINS:raise ValueError('exact parent pins differ')
    for new,old in reversed(fixture['replacements'][name]):
        if text.count(new)!=1:raise ValueError('unique exact inverse fragment missing')
        text=text.replace(new,old,1)
    if hashlib.sha256(text.encode()).hexdigest()!=PINS[name]:raise ValueError('whole parent bytes differ')
    return text

def operational_source():
    spec=importlib.util.spec_from_file_location('bridge',HERE/'test_cecil_native_bridge.py')
    bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
    # Reuse the actual complete fixture setup, no policy/algorithm mirror.
    helpers=bridge.TESTS[:bridge.TESTS.index('int main(){')]
    block=bridge.TESTS.split(' { // Same unchanged SDK bodies, full ordered stub Engine/collision calls.',1)[1]
    block=block.split(' // Actual current Clear/Nearest guards',1)[0]
    block=block[:block.index('   if(!diag){baseline=values;')]+'''   std::printf("OP %d %d %s\\n",scenario,diag,operationTrace.c_str());
   std::printf("STATE");for(double v:values)std::printf(" %.17g",v);std::printf("\\n");
  }
 }
 return 0;
}'''
    return bridge,helpers+'int main(){'+block

class SourceCustody(unittest.TestCase):
    def test_full_parent_files_and_guards(self):
        for name in PINS:
            self.assertEqual(hashlib.sha256(reverse(name,(HERE/name).read_text()).encode()).hexdigest(),PINS[name])
        native=(HERE/'BotSupplyNative.h').read_text();driver=(HERE/'BotDriver.cpp').read_text()
        for name,text,old,new in [('BotSupplyNative.h',native,'if(d>128)','if(d>129)'),('BotDriver.cpp',driver,'pickerArbitration.Gate(9,supply.urgent)','pickerArbitration.Gate(9,true)')]:
            self.assertIn(old,text)
            with self.assertRaises(ValueError):reverse(name,text.replace(old,new,1))
    def test_actual_parent_current_full_operation_lanes(self):
        bridge,tests=operational_source()
        driver=reverse('BotDriver.cpp',(HERE/'BotDriver.cpp').read_text())
        choice=re.search(r'if\((ready&&[\s\S]*?)\)\{\s*bs\.bs_aHeading=player->m_aLastRotation',driver)[1]
        ownership='\nstatic bool bridgeDriverOwns(bool ready,const SCecilMove& supply,CPlayer* player,bool targetVisible){botcore::CecilDriverFinal finalDecision;return '+choice+';}\n'
        items=(HERE/'BotCecilItems.h').read_text();a=items.index('inline bool BotCecilIsClass(');z=items.index('inline uint32_t BotCecilAmmoNeed',a)
        outcomes=[]
        with tempfile.TemporaryDirectory(prefix='picker-lanes-')as d:
            for label in ('PARENT','CURRENT'):
                source=(HERE/'BotSupplyNative.h').read_text()
                if label=='PARENT':source=reverse('BotSupplyNative.h',source)
                a0=source.index('static void BotSupplyUpdateNavigation(');z0=source.index('static botcore::CecilFrame BotCecilBodyFrame(',a0)
                source=source[:a0]+source[z0:];source='\n'.join(x for x in source.splitlines()if not x.startswith('#'))
                # Source helper fixtures need their existing sparse own trace.
                trace=json.loads((HERE/'fixtures/build019-terminal-111-175.json').read_text())
                poses=','.join('{'+','.join(str(x)+'f'for x in row['position'])+'}'for row in trace['frames'])
                cpp=Path(d)/(label+'.cpp');exe=Path(d)/label
                cpp.write_text('#define EXPECTED_NATIVE_USE 32u\n'+bridge.STUBS+items[a:z]+'\n#define far\n'+source+'\n#undef far\n'+ownership+tests.replace('__TERMINAL019_POSES__',poses))
                subprocess.run(['g++','-std=c++14','-O1','-w','-I',str(HERE),str(cpp),'-o',str(exe)],check=True,timeout=90)
                outcomes.append(subprocess.check_output([str(exe)],text=True,timeout=10))
        self.assertEqual(outcomes[0],outcomes[1],'ordered Engine calls, state/actions/RNG/budget differ from actual full inverse parent')
        lines=outcomes[0].splitlines();ops=[x for x in lines if x.startswith('OP ')]
        self.assertEqual(len(ops),24)
        differences=[scenario for scenario in range(12)if ops[2*scenario].split(' ',3)[3]!=ops[2*scenario+1].split(' ',3)[3]]
        self.assertEqual(differences,[2,4,11]) # Do not remove any call from either lane.
        print('Whole parent/current exact:24 operation lanes; existing DIAG0/1 call differences scenarios',differences,flush=True)

if __name__=='__main__':unittest.main(verbosity=2)
