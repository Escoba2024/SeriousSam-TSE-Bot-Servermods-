"""Offline sealed-transaction and pre-input fail-closed checks; no game access."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

try:
    import a1_nosmooth_intervention as N
except ImportError:
    N = None


class EffectiveGateTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(N, 'sealed nosmooth intervention missing')

    def good(self):
        return dict(local_slot=0, profile=0, global_smooth=0,
                    axes={a:dict(smooth=0, effective_smooth=0) for a in ('x','y')},
                    raw_reads=[dict(address=0x30000, raw_hex='00000000')])

    def execute(self, snapshot):
        report = {'status':'IN_PROGRESS'}
        calls = []
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'controls-effective.json'
            def sample(reader, *, local_slot):
                calls.append(('sample', local_slot))
                return copy.deepcopy(snapshot)
            result = N.run_after_verified_controls(None, report, p, lambda:None,
                lambda:calls.append(('input',)) or 'calibration', sample=sample)
            return report, calls, json.loads(p.read_text()), result

    def test_one_valid_effective_sample_is_journalled_before_calibration(self):
        report, calls, journal, result = self.execute(self.good())
        self.assertEqual(calls, [('sample',0),('input',)])
        self.assertEqual(journal['status'], 'OBSERVED')
        self.assertEqual(journal['sample']['raw_reads'], self.good()['raw_reads'])
        self.assertEqual(result, 'calibration')

    def test_wrong_active_profile_or_each_smoothing_flag_fails_before_input(self):
        for mutation in ('profile','global','axis','effective'):
            observation = self.good()
            if mutation=='profile': observation['profile']=1
            elif mutation=='global': observation['global_smooth']=1
            elif mutation=='axis': observation['axes']['x']['smooth']=1
            else: observation['axes']['y']['effective_smooth']=1
            report = {'status':'IN_PROGRESS'}; inputs = []
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as d:
                p = Path(d)/'controls-effective.json'
                with self.assertRaises(ValueError):
                    N.run_after_verified_controls(None,report,p,lambda:None,
                        lambda:inputs.append(True),sample=lambda *a,**k:copy.deepcopy(observation))
                self.assertFalse(inputs)
                self.assertEqual(report['status'],'FAIL')
                journal=json.loads(p.read_text())
                self.assertEqual(journal['status'],'FAIL')
                self.assertEqual(journal['sample'],observation)
                # A later favorable observation may never clear the failed run.
                with self.assertRaises(ValueError):
                    N.run_after_verified_controls(None,report,p,lambda:None,
                        lambda:inputs.append(True),sample=lambda *a,**k:self.good())
                self.assertFalse(inputs)
                self.assertEqual(json.loads(p.read_text()),journal)

    def test_reader_failure_preserves_raw_evidence_without_input(self):
        report={'status':'IN_PROGRESS'};inputs=[]
        def bad(*args,**kwargs):
            error=ValueError('torn effective controls')
            error.raw_reads=[{'raw_hex':'01'}]
            raise error
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'controls-effective.json'
            with self.assertRaises(ValueError):
                N.run_after_verified_controls(None,report,p,lambda:None,
                    lambda:inputs.append(True),sample=bad)
            self.assertFalse(inputs)
            self.assertEqual(json.loads(p.read_text())['raw_reads'],[{'raw_hex':'01'}])
            self.assertEqual(report['status'],'FAIL')

    def test_result_journal_failure_withholds_all_calibration_input(self):
        report={'status':'IN_PROGRESS'};inputs=[]
        def cannot_save():
            raise OSError('result journal unavailable')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'controls-effective.json'
            with self.assertRaises(OSError):
                N.run_after_verified_controls(None,report,p,cannot_save,
                    lambda:inputs.append(True),sample=lambda *a,**k:self.good())
            self.assertFalse(inputs)
            self.assertEqual(report['status'],'FAIL')
            self.assertEqual(json.loads(p.read_text())['status'],'FAIL')
            self.assertEqual(json.loads(p.read_text())['sample'],self.good())


@unittest.skipUnless(os.environ.get('TSE_A1_PACKAGE'), 'requires private exact original profile and transaction source')
class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(N)
        root=Path(os.environ['TSE_A1_PACKAGE'])
        source=root/'transaction.py'
        spec=importlib.util.spec_from_file_location('nosmooth_fixture_transaction',source)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.Transaction=module.FileTransaction
        self.original=Path('/srv/tse-a1-settled-input-private-20261114/Controls0-before.ctl').read_bytes()

    def fixture(self,d):
        root=Path(d)/'fixture';out=Path(d)/'evidence';out.mkdir()
        for role in ('vanilla','botA'):
            path=root/role/'Controls/Controls0.ctl';path.parent.mkdir(parents=True);path.write_bytes(self.original);path.chmod(0o640)
        tx=self.Transaction(root,out,lambda:None)
        for role in ('vanilla','botA'):tx.snapshot_tree(role+'/Controls')
        return root,out,tx

    def test_only_sealed_vanilla_profile_changes_and_restore_recovers_hash_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root,out,tx=self.fixture(d)
            with self.assertRaises(ValueError):N.install(tx,out)
            tx.seal();receipt=N.install(tx,out)
            self.assertFalse(receipt['effective_runtime_observed'])
            self.assertNotEqual((root/N.RELATIVE).read_bytes(),self.original)
            self.assertEqual((root/'botA/Controls/Controls0.ctl').read_bytes(),self.original)
            self.assertEqual((root/N.RELATIVE).stat().st_mode&0o777,0o640)
            self.assertTrue(tx.restore()['restored'])
            self.assertEqual((root/N.RELATIVE).read_bytes(),self.original)
            self.assertEqual((root/N.RELATIVE).stat().st_mode&0o777,0o640)

    def test_changed_hash_or_metadata_is_rejected_without_installation(self):
        for change in ('hash','mode'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as d:
                root,out,tx=self.fixture(d);tx.seal();path=root/N.RELATIVE
                if change=='hash':path.write_bytes(self.original+b'// drift\n')
                else:path.chmod(0o600)
                before=path.read_bytes()
                with self.assertRaises(ValueError):N.install(tx,out)
                self.assertEqual(path.read_bytes(),before)


if __name__=='__main__':unittest.main()
