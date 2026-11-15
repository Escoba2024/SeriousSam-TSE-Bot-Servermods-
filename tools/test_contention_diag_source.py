"""Source inverse and actual printf-bound checks for passive owner receipts."""
import ast
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from verify_contention_diag_source import BASE_HEADER_SHA256, verify
from verify_driver_final_source import verify as verify_driver_final

ROOT=Path(__file__).resolve().parents[1]
HEADER=ROOT/'poc/candidates/redstation-supply-20261107/BotSupplyNative.h'

class ContentionSourceTests(unittest.TestCase):
    def test_whole_header_inverse_and_driver_unchanged(self):
        self.assertEqual(hashlib.sha256(verify(HEADER.read_text()).encode()).hexdigest(),BASE_HEADER_SHA256)
        driver=HEADER.with_name('BotDriver.cpp')
        self.assertEqual(hashlib.sha256(verify_driver_final(driver.read_text(),HEADER.read_bytes()).encode()).hexdigest(),'ebb2c4cc694ebdc1ee8f9e2e1aa88a2cb587afae5adc649bfcae84ff244c6c55')

    def test_gameplay_guard_and_diagnostic_receipt_mutations_rejected(self):
        source=HEADER.read_text()
        for old,new in [('observedAt-claim.seen>.250001','observedAt-claim.seen>.5'),
                        ('claim.localTime-claim.progress>=5','claim.localTime-claim.progress>=6'),
                        ('claim.cost+1>=cost','claim.cost+0>=cost'),
                        ('attempt<8&&_botRayBudget>2','attempt<9&&_botRayBudget>2'),
                        ('bestContested&&!contested','!bestContested&&contested'),
                        ('receipt->entity=claim.entity','receipt->entity=peer.entity'),
                        ('bestReceipt=candidateReceipt','bestReceipt=SCecilSupplyClaimReceipt()')]:
            with self.subTest(old=old):
                self.assertEqual(source.count(old),1)
                with self.assertRaises(ValueError):verify(source.replace(old,new,1))
        with self.assertRaises(ValueError):verify(source+'\n'+source[source.index('// Scalar receipt'):source.index('static bool BotCecilNearerLocalSupply(')])

    def test_actual_formats_extreme_values_and_conservative_bounds(self):
        self.assertIsNotNone(shutil.which('g++'),'required portable compiler')
        source=HEADER.read_text();program=['#include <cstdio>','#include <climits>','#include <limits>','int main(){char out[2048];int n;']
        pattern=r'%(?:\.\d+)?(?:l[du]|[diufg])'
        for name in ('Candidate','Selection'):
            token=re.search(r'BotLog\(("\[CecilSupplyDiag'+name+r'\].*?")',source).group(1)
            fmt=ast.literal_eval(token);fields=re.findall(pattern,fmt)
            bound=len(re.sub(pattern,'',fmt))+1
            args=[]
            for field in fields:
                if field=='%lu':arg='ULONG_MAX';width=20
                elif field=='%ld':arg='LONG_MIN';width=20
                elif field=='%u':arg='UINT_MAX';width=10
                elif field in ('%d','%i'):arg='INT_MIN';width=11
                elif field.endswith('g'):arg='-std::numeric_limits<double>::max()';width=26
                else:arg='-std::numeric_limits<double>::max()';width=319
                args.append(arg);bound+=width
            self.assertLess(bound,2048,(name,bound))
            program+=['n=std::snprintf(out,sizeof(out),'+token+','+','.join(args)+');',
                      'if(n<0||n>=2048||out[n-1]!=\'\\n\')return 1;',
                      'std::printf("'+name+' extreme bytes=%d conservative_bound_including_NUL='+str(bound)+'\\n",n);']
        program+=['return 0;}']
        with tempfile.TemporaryDirectory(prefix='contention-format-')as d:
            p=Path(d);(p/'format.cpp').write_text('\n'.join(program))
            subprocess.run(['g++','-std=c++14','-Wall','-Wextra','-Werror','-Wformat=2',str(p/'format.cpp'),'-o',str(p/'format')],check=True)
            subprocess.run([str(p/'format')],check=True)

if __name__=='__main__':unittest.main()
