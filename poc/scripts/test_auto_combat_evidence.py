"""Negative fixtures derived from a real accepted run; never changes runtime files."""
import importlib.util, json, re, shutil, sys, tempfile, unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('combat_audit',Path(__file__).with_name('Test-AutoCombatEvidence.py'))
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
source=Path(sys.argv[1]).resolve(); dll=Path(sys.argv[2]).resolve()
sys.argv=sys.argv[:1]

class AuditChecks(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        for name in ('diagnostics.json','identities-2.json'):
            shutil.copyfile(source/name,self.root/name)
        target=self.root/'native-2-Combat'; target.mkdir()
        for name in ('result.json','telemetry.json','SeriousSam.log','observer-SeriousSam.log'):
            shutil.copyfile(source/'native-2-Combat'/name,target/name)
        self.log=target/'SeriousSam.log'
    def tearDown(self): self.temp.cleanup()
    def test_real_evidence(self): self.assertTrue(module.audit(self.root,dll)['passed'])
    def test_missing_combat_is_not_transport_pass(self):
        self.log.write_text('\n'.join(l for l in self.log.read_text().splitlines() if not l.startswith('[BotCombat]')))
        with self.assertRaisesRegex(AssertionError,'missing combat'): module.audit(self.root,dll)
    def test_unsettled_weapon_cannot_be_ready(self):
        self.log.write_text(re.sub(r'(\[BotCombatWeapon\][^\n]* current=)\d+',r'\g<1>14',self.log.read_text()))
        with self.assertRaisesRegex(AssertionError,'before native desired'): module.audit(self.root,dll)
    def test_wrong_group_rejected(self):
        self.log.write_text(re.sub(r'(\[BotCombatWeapon\][^\n]* group=)\d+',r'\g<1>5',self.log.read_text()))
        with self.assertRaisesRegex(AssertionError,'group mapping'): module.audit(self.root,dll)
    def test_wrong_candidate_hash_rejected(self):
        path=self.root/'native-2-Combat/result.json'; data=json.loads(path.read_text(encoding='utf-8-sig'))
        data['sha256']='0'*64; path.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError,'current candidate'): module.audit(self.root,dll)
    def test_duplicate_guids_rejected(self):
        path=self.root/'identities-2.json'; data=json.loads(path.read_text(encoding='utf-8-sig'))
        data[1]['guid']=data[0]['guid']; path.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError,'distinct native'): module.audit(self.root,dll)
unittest.main()
