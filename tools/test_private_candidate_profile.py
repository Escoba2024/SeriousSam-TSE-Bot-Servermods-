import importlib,sys,unittest,json,hashlib,tempfile
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'operations'))
try:import private_candidate_profile as profile
except ImportError:profile=None
class PrivateProfileTests(unittest.TestCase):
 def setUp(self):self.assertIsNotNone(profile,'immutable private candidate profile missing')
 def test_rejects_unaccepted_matrix(self):
  with self.assertRaises(ValueError):profile.matrix_stages({'status':'BLOCKED','m1_complete':False,'stages':[]})
 def test_rejects_wrong_or_duplicate_topology(self):
  for roles in ({'botA':'name'},{'gamer-000':'same','gamer-001':'same'}):
   with self.assertRaises(ValueError):profile.role_contract(roles)
 def test_rejects_public_or_legacy_runtime_roots(self):
  for root in ['/srv/tse','/srv/tse-ops-runtime-20261021/x','/srv/tse-ops-m1-20261027/../public']:
   with self.assertRaises(ValueError):profile.validate_location(root,26820,':125')
 def test_valid_private_location_is_exact(self):
  self.assertEqual(profile.validate_location('/srv/tse-ops-m1-20261027/test',26820,':125'),Path('/srv/tse-ops-m1-20261027/test'))
 def test_all_roles_and_local_counts(self):
  identities={f'gamer-{i:03}':f'name{i}' for i in range(8)}
  roles=profile.role_contract(identities)
  self.assertEqual(len(roles),10);self.assertEqual(sum(r.local_players for r in roles if r.kind=='bot'),8)
  self.assertEqual({r.kind for r in roles},{'server','observer','bot'})
 def test_policy_rejects_truncated_source_inventory(self):
  self.assertTrue(hasattr(profile,'validate_policy_inventory'),'exact policy inventory admission missing')
  with self.assertRaises(ValueError):profile.validate_policy_inventory({'candidate_sha256':profile.CANDIDATE,'source_sha256':{},'artifact_sha256':{}})
 def test_loader_rejects_real_read_of_unaccepted_synthetic_matrix(self):
  # Synthetic metadata only; this deliberately never constructs native receipts.
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);matrix=root/'matrix.json';policy=root/'policy.json'
   matrix.write_text(json.dumps({'status':'BLOCKED','m1_complete':False,'stages':[]}));policy.write_text('{}')
   doc={'schema':'M1_PRIVATE_SUPERVISOR_V1','root':'/srv/tse-ops-m1-20261027/test','port':26820,'display':':125',
        'matrix_sha256':profile.sha(matrix),'policy_sha256':profile.sha(policy),'operations_source_sha256':{}}
   path=root/'profile.json';path.write_text(json.dumps(doc))
   config={'root':doc['root'],'port':26820,'display':':125','bots':8,'private_profile':{'path':str(path),'sha256':profile.sha(path)}}
   with patch.object(profile,'EVIDENCE',root):
    with self.assertRaisesRegex(ValueError,'complete private prefilter matrix'):profile.load(config)
 def test_host_namespace_is_rejected(self):
  with patch.object(profile.os,'readlink',return_value='net:[1]'),patch.object(profile.socket,'if_nameindex',return_value=[(1,'lo')]):
   self.assertFalse(profile.isolated_namespace())
 def test_nonloopback_interface_is_rejected(self):
  with patch.object(profile.os,'readlink',side_effect=['net:[2]','net:[1]']),patch.object(profile.socket,'if_nameindex',return_value=[(1,'lo'),(2,'eth0')]):
   self.assertFalse(profile.isolated_namespace())
 def test_result_rejects_other_p1_observer_or_render_configuration(self):
  self.assertTrue(hasattr(profile,'validate_native_profile_result'),'native configuration contract missing')
  for result in [{},{'max_bots':8,'cecil_p1':False},{'max_bots':8,'cecil_p1':True,'observer_fps_cap':20}]:
   with self.assertRaises(ValueError):profile.validate_native_profile_result(result)
 def test_preparation_has_no_unaccepted_profile_fallback(self):
  self.assertTrue(hasattr(profile,'prepare'),'accepted-profile-only preparation missing')
  with self.assertRaises(ValueError):profile.prepare({'root':'/srv/tse-ops-m1-20261027/no-create'})
 def test_live_pin_recheck_rejects_same_size_source_change(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);meta=root/'profile.json';meta.write_text('{}');source=root/'source.py';source.write_text('one')
   obj=profile.PrivateProfile(root=Path('/srv/tse-ops-m1-20261027/test'),port=26820,display=':125',roles=(),
       profile_path=meta,profile_sha256=profile.sha(meta),matrix_sha256='a'*64,policy_sha256='b'*64,
       marker_sha256='c'*64,reference_root=root,prepared_pins=(),evidence_pins=((str(source),profile.sha(source)),),startup_budget_bytes=1)
   obj.verify_pins();source.write_text('two')
   with self.assertRaisesRegex(ValueError,'source drift'):obj.verify_pins()
 def test_profile_is_frozen(self):
  role=profile.Role('gamer-000','bot','name',1)
  with self.assertRaises((AttributeError,TypeError)):role.local_players=4
if __name__=='__main__':unittest.main()
