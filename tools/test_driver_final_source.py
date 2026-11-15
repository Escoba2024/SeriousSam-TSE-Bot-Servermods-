"""Exact full-source inverse, conservative format bound and adversarial mutations."""
import ast
import hashlib
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
CAND=ROOT/'poc/candidates/redstation-supply-20261107'

class DriverFinalSourceTests(unittest.TestCase):
    def verifier(self):
        from tools.verify_driver_final_source import verify
        return verify

    def test_exact_whole_driver_and_unchanged_header(self):
        original=self.verifier()((CAND/'BotDriver.cpp').read_text(),(CAND/'BotSupplyNative.h').read_bytes())
        self.assertEqual(hashlib.sha256(original.encode()).hexdigest(),'ebb2c4cc694ebdc1ee8f9e2e1aa88a2cb587afae5adc649bfcae84ff244c6c55')

    def test_gameplay_and_diagnostic_guard_mutants_rejected(self):
        verify=self.verifier();source=(CAND/'BotDriver.cpp').read_text();header=(CAND/'BotSupplyNative.h').read_bytes()
        for before,after in [
            ('(supply.itemGoal&&supply.urgent)','supply.itemGoal'),
            ('supplyActive!=FALSE,\n          botcore::CecilDriverFinalValue','true,\n          botcore::CecilDriverFinalValue'),
            ('pa.pa_ulButtons |= combatSelect|cecilButtons','pa.pa_ulButtons |= combatSelect'),
            ('bs.bs_weaponInput.Poll(bs.bs_iTick,finalWeapon,','bs.bs_weaponInput.Poll(bs.bs_iTick,1,'),
            ('bot_bDiagnostics!=FALSE,bot_bSupplyNavigation!=FALSE','true,bot_bSupplyNavigation!=FALSE'),
            ('if(finalLength>0&&finalLength<(int)sizeof(finalText))','if(finalLength>0)'),
            ('finalDecision.safeAfter[0]=moveFactor','finalDecision.safeAfter[0]=0'),
            ('finalDecision,pa,BotSupplyState(iLP).generation','finalDecision,pa,finalDecision.entryGeneration'),
            ('finalDecision.pollLastButtons,player->m_ulLastButtons','finalDecision.pollLastButtons,0u'),
            ('finalDecision.arbitrationFlags=cecilFlags','finalDecision.arbitrationFlags=0'),
            ('finalDecision.cachedTargetIndex=automatic?bs.bs_iCombatTarget:bot_iTestTarget','finalDecision.cachedTargetIndex=bot_iTestTarget'),
            ('((unsigned)(humanFire!=FALSE)<<7);','((unsigned)(true)<<7);'),
        ]:
            with self.subTest(before=before):
                self.assertEqual(source.count(before),1)
                with self.assertRaises(ValueError):verify(source.replace(before,after,1),header)
        self.assertIn(b'return support>.5;',header)
        with self.assertRaises(ValueError):verify(source,header.replace(b'return support>.5;',b'return support>.3;',1))
        with self.assertRaises(ValueError):verify(source+'\n',header)

    def test_independent_fixed_format_bound_including_NUL(self):
        header=(CAND/'driver_final_decision.h').read_text()
        begin=header.index('return std::snprintf(');end=header.index('d.local,d.tick',begin)
        fmt=''.join(ast.literal_eval(x)for x in re.findall(r'"(?:\\.|[^"\\])*"',header[begin:end]))
        fields=re.findall(r'%(?:\.\d+)?[dug]',fmt)
        literal=re.sub(r'%(?:\.\d+)?[dug]','',fmt)
        widths={'%d':11,'%u':10,'%.9g':26,'%.17g':26}
        bound=len(literal)+1+sum(widths[x]for x in fields)
        self.assertLess(bound,2048)
        self.assertEqual(fields.count('%.17g'),28)
        print('conservative full fixed row bound including NUL=',bound)

if __name__=='__main__':unittest.main()
