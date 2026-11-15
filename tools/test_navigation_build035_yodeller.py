"""Fixed new Yodeller condition; Source-only, no controller/runtime imports."""
import importlib
import importlib.util
import ast
import copy
import unittest

NAME='navigation_build035_yodeller_policy' if importlib.util.find_spec('navigation_build035_yodeller_policy') else 'navigation_build035_trouble_policy'
policy=importlib.import_module(NAME)

class Contract(unittest.TestCase):
    def test_yodeller600_diag0_is_the_only_new_condition(self):
        self.assertIsNone(policy.options('yodeller',600,0,'035'))
    def test_old_condition_and_other_values_rejected(self):
        cases=[('trouble',300,1,'035'),('yodeller',600,0,'036'),('hole',600,0,'035'),('yodeller',300,0,'035'),('yodeller',600,1,'035'),('yodeller',True,0,'035'),('yodeller',float('nan'),0,'035'),('yodeller',float('inf'),0,'035'),('yodeller',600,False,'035')]
        for args in cases:
            with self.subTest(args=args),self.assertRaises(ValueError):policy.options(*args)

class Source(unittest.TestCase):
    def test_current_parent_two_whole_inverses_and_mutations(self):
        import prepare_navigation_build035_yodeller as h
        for name in h.CHANGED:
            raw=h.read(h.PARENT/name).decode();new=h.apply(name,raw)
            self.assertEqual(h.apply(name,new,True),raw)
            for bad in [raw+'\n',new,raw.replace('035','036',1)]:
                with self.subTest(name=name),self.assertRaises(ValueError):h.apply(name,bad)
        text=h.apply('run-a4.py',h.read(h.PARENT/'run-a4.py').decode())
        self.assertIn('RUNTIME_REVIEWED=False',text)
        self.assertIn("hardmap.options(map_key,duration,diag,policy.prepared.catalog()['maps'])",text)
        self.assertIn("choices=('yodeller',)",text)

    def test_actual_candidate_provenance_and_full_closure_not_higher_build(self):
        import prepare_navigation_build035_yodeller as h
        m=h.load(h.prior.BUILD/'manifest.json')
        for key,value in [('repo_commit','0'*40),('repo_tree','0'*40),('dll_sha256','0'*64),('source_count',16),('qualified',True)]:
            bad=copy.deepcopy(m);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):h.prior.validate_build(bad)
        for key in ['source_sha256','overlay_sha256']:
            for mutation in ['missing','hash']:
                bad=copy.deepcopy(m);name=next(iter(bad[key]))
                if mutation=='missing':del bad[key][name]
                else:bad[key][name]='0'*64
                with self.subTest(key=key,mutation=mutation),self.assertRaises(ValueError):h.prior.validate_build(bad)

    def test_asset_binding_mutation_rejected_before_archive(self):
        import prepare_navigation_build035_yodeller as h
        c=h.load(h.PARENT/'map-catalog.json')
        for key,value in [('world_path','wrong.wld'),('nodes',112),('nav_sha256','0'*64)]:
            bad=copy.deepcopy(c);bad['maps']['yodeller'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):h.validate_assets(bad)

    def test_existing_or_parent_destination_rejected_before_any_copy(self):
        import prepare_navigation_build035_yodeller as h
        for p in [h.PARENT,h.PARENT/'never-created-child',h.prior.BUILD/'never-created-child']:
            with self.subTest(path=str(p)),self.assertRaises(ValueError):h.prepare(p)

    def test_actual_prepared_package_keeps_current_safety_and_pins(self):
        import prepare_navigation_build035_yodeller as h
        d=h.DESTINATION;m=h.load(d/'source-manifest.json');parent=h.load(h.PARENT/'source-manifest.json')
        h.verify_pins(m,d)
        self.assertEqual([len(m[k])for k in ['runtime_dependencies','sources','draft_source_sha256']],[160,146,79])
        for name in h.CHANGED:self.assertEqual(h.apply(name,h.read(d/name).decode(),True).encode(),h.read(h.PARENT/name))
        for name in ['transaction.py','strict_backend.py','navigation_comparison_policy.py','map-catalog.json','canonical.ini','a4_ordered_memory_v3.py','audit_a4_ordered_memory_v3.py','host_budget.py']:
            self.assertEqual(h.read(d/name),h.read(h.PARENT/name))
        self.assertEqual(m['candidate'],parent['candidate'])
        self.assertEqual((m['comparison']['map'],m['comparison']['seconds'],m['comparison']['diagnostics']),('yodeller',600,0))
        self.assertEqual(m['map_case']['map_binding'],h.YODELLER)
        self.assertTrue(all(m[k]is False for k in ['runtime_reviewed','runtime_performed','qualified','functional_pass']))
        self.assertEqual(m['runtime_dependencies'][str(d/'transaction.py')],h.TRANSACTION)
        self.assertEqual(m['runtime_dependencies'][str(d/'strict_backend.py')],h.BACKEND)

if __name__=='__main__':unittest.main(verbosity=2)
