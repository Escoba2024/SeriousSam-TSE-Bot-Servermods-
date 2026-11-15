"""Whole033 inverse and actual full SDK operation lanes for passive custody."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
PARENT='49229af92892fe030f74b7a09815647c90ec0572f4a1065c1ed20fc4f0590b3d'
DRIVER='1c081af07169c96b3158307135d0c2b495ea91ce6e957a690a90363d90e914ff'
def reverse(text):
    data=json.loads((HERE/'transit_history_custody_inverse.json').read_text())
    if data['parent_sha256']!=PARENT:raise ValueError('parent pin')
    for new,old in reversed(data['replacements']):
        if text.count(new)!=1:raise ValueError('nonunique inverse')
        text=text.replace(new,old,1)
    if hashlib.sha256(text.encode()).hexdigest()!=PARENT:raise ValueError('whole033 parent differs')
    return text

class TransitCustodySource(unittest.TestCase):
    def test_whole033_inverse_and_real_guard_mutation(self):
        source=(HERE/'BotSupplyNative.h').read_text()
        self.assertEqual(hashlib.sha256(reverse(source).encode()).hexdigest(),PARENT)
        for old,new in [('std::fabs(vertical)<=3','std::fabs(vertical)<=3.1'),('now-since+1e-9>=10','now-since+1e-9>=11')]:
            self.assertIn(old,source)
            with self.assertRaises(ValueError):reverse(source.replace(old,new,1))
        self.assertEqual(hashlib.sha256((HERE/'BotDriver.cpp').read_bytes()).hexdigest(),DRIVER)

    def test_fixed_stack_format_conservative_bound(self):
        source=(HERE/'BotSupplyNative.h').read_text()
        row=re.search(r'"(\[CecilItemTransitHistory\] event=%s[^"\n]+)',source)[1].replace(r'\n','\n')
        widths={'%s':32,'%u':10,'%lu':20,'%d':11,'%ld':20,'%p':18,'%.9g':17}
        parts=re.split(r'(%\.9g|%lu|%ld|%s|%u|%d|%p)',row)
        self.assertTrue(all('%'not in part or part in widths for part in parts))
        bound=sum(widths.get(part,len(part))for part in parts)
        self.assertLess(bound,1024)
        helper=source[source.index('static void BotCecilTransitHistoryRow'):source.index('// One mapped-weapon attempt')]
        for forbidden in ('GetWorld','GetHealth','GetGameTime','BotSupplyClear','PhysicalCast','new ','malloc','_pTimer'):
            self.assertNotIn(forbidden,helper)
        print('Transit formatter conservative bound',bound,'bytes + NUL <1024',flush=True)

    def test_actual_parent_current_full24_operation_lanes(self):
        spec=importlib.util.spec_from_file_location('picker_source',HERE/'test_picker_custody_source.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        bridge,tests=module.operational_source()
        driver=(HERE/'BotDriver.cpp').read_text()
        choice=re.search(r'if\((pickerArbitration\.Gate\(0,ready\)[\s\S]*?)\)\{\s*pickerArbitration\.taken=true;[^\n]*\n\s*bs\.bs_aHeading=player->m_aLastRotation',driver)[1]
        proposal=re.search(r'      pickerArbitration\.Supply\([^\n]+',driver)[0].strip()
        ownership='\nstatic bool bridgeDriverOwns(bool ready,const SCecilMove& supply,CPlayer* player,bool targetVisible){botcore::CecilDriverFinal finalDecision;botcore::CecilPickerArbitration pickerArbitration(bot_bDiagnostics);return '+choice+';}\n'
        ownership+='\nstatic bool bridgeDriverProposalKnown(bool ready,const SCecilMove& supply){botcore::CecilPickerArbitration pickerArbitration(true);'+proposal+'\nreturn pickerArbitration.proposalKnown;}\n'
        ownership+='\nstatic bool bridgeDriverCustody(bool ready,const SCecilMove& supply,CPlayer* player,bool targetVisible,botcore::CecilPickerArbitration& pickerArbitration){botcore::CecilDriverFinal finalDecision;return '+choice+';}\n'
        items=(HERE/'BotCecilItems.h').read_text();a=items.index('inline bool BotCecilIsClass(');z=items.index('inline uint32_t BotCecilAmmoNeed',a)
        trace=json.loads((HERE/'fixtures/build019-terminal-111-175.json').read_text())
        poses=','.join('{'+','.join(str(x)+'f'for x in row['position'])+'}'for row in trace['frames'])
        outcomes=[]
        with tempfile.TemporaryDirectory(prefix='transit-custody-lanes-')as d:
            for label in ('PARENT','CURRENT'):
                source=(HERE/'BotSupplyNative.h').read_text()
                if label=='PARENT':source=reverse(source)
                a0=source.index('static void BotSupplyUpdateNavigation(');z0=source.index('static botcore::CecilFrame BotCecilBodyFrame(',a0)
                source=source[:a0]+source[z0:];source='\n'.join(line for line in source.splitlines()if not line.startswith('#'))
                cpp=Path(d)/(label+'.cpp');exe=Path(d)/label
                cpp.write_text('#define EXPECTED_NATIVE_USE 32u\n'+bridge.STUBS+items[a:z]+'\n#define far\n'+source+'\n#undef far\n'+ownership+tests.replace('__TERMINAL019_POSES__',poses))
                subprocess.run(['g++','-std=c++14','-O1','-w','-I',str(HERE),str(cpp),'-o',str(exe)],check=True,timeout=90)
                outcomes.append(subprocess.check_output([str(exe)],text=True,timeout=10))
        self.assertEqual(outcomes[0],outcomes[1],'full ordered state/actions/RNG/queries/budgets must match each parent lane exactly')
        ops=[line for line in outcomes[0].splitlines()if line.startswith('OP ')]
        self.assertEqual(len(ops),24)
        differences=[i for i in range(12)if ops[2*i].split(' ',3)[3]!=ops[2*i+1].split(' ',3)[3]]
        self.assertEqual(differences,[2,4,11]) # Existing parent GetGameTime differences are preserved, not filtered.
        print('Whole033/current exact24 lanes; inherited DIAG0/1 GetGameTime differences',differences,flush=True)

if __name__=='__main__':unittest.main(verbosity=2)
