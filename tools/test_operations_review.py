import os,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'operations'))
import fleet_health as h
import fleet_supervisor as v
class ReviewTests(unittest.TestCase):
 def test_reader_handles_do_not_block_verified_archiving(self):
  import gzip
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'log';p.write_bytes(b'closed generation')
   with p.open('rb') as reader:
    try:rows=v.archive_closed([p],Path(d)/'archives')
    except RuntimeError as e:self.fail('read-only handle blocked closed-generation archive: '+str(e))
    self.assertEqual(reader.read(),b'closed generation');self.assertEqual(gzip.decompress(Path(rows[0]['archive']).read_bytes()),b'closed generation')
 def test_clock_rollback_fails_closed_for_retry_budget(self):
  self.assertFalse(v.retry_allowed({'attempts':[101]},100),'future persisted attempt must hold recovery')
 def test_unknown_retail_window_blocks_display_teardown(self):
  self.assertTrue(hasattr(v,'validate_window_owners'),'display ownership guard missing')
  v.validate_window_owners([1,2],{1,2})
  with self.assertRaises(RuntimeError):v.validate_window_owners([1,3],{1,2})
  with self.assertRaises(RuntimeError):v.validate_window_owners([None],{1,2})
 def test_expected_local_count_must_match_not_just_be_nonzero(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'telemetry';p.write_text('#columns,t_ms,ticks,actions,renderdraw,lp,gameon,enabled,stall_s\n1000000,20,20,0,1,1,1,0\n')
   try:answer=h.telemetry_valid(p,now=1000,expected_local=4)
   except TypeError:self.fail('expected local-player validation missing')
   self.assertFalse(answer)
   self.assertTrue(h.telemetry_valid(p,now=1000,expected_local=1))
 def test_sync_scan_is_bounded_incremental_and_rotation_aware(self):
  self.assertTrue(hasattr(h,'sync_counts'),'bounded sync scanner missing')
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'log';p.write_bytes(b'SYNCBAD: Client \'127.0.0.1\', bad 1\nSYNCBAD: Client \'external-fixture\', bad 1\n')
   a=h.sync_counts(p,max_bytes=20);self.assertFalse(a['complete'])
   for _ in range(20):
    a=h.sync_counts(p,max_bytes=20)
    if a['complete']:break
   self.assertTrue(a['complete']);self.assertEqual((a['owned'],a['external']),(1,1));self.assertEqual(h.sync_counts(p)['owned'],1)
   with p.open('ab') as out:out.write(b"SYNCBAD: Client '127.0.0.1'")
   self.assertEqual(h.sync_counts(p)['owned'],1)
   with p.open('ab') as out:out.write(b', bad 2\n')
   self.assertEqual(h.sync_counts(p)['owned'],2)
   p.unlink();p.write_text("SYNCBAD: Client 'external-fixture', bad 1\n")
   a=h.sync_counts(p);self.assertEqual((a['owned'],a['external']),(0,1))
 def test_cgroup_throttle_and_oom_alerts_block_recovery(self):
  import test_fleet_operations as fixtures
  s=fixtures.HealthTests().snapshot();s['cgroup_issues']=['CGROUP_THROTTLED'];r=h.assess(s);self.assertFalse(r['safe_recovery']);self.assertIn('CGROUP_THROTTLED',r['alerts'])
  s=fixtures.HealthTests().snapshot();s['cgroup_issues']=['CGROUP_OOM'];self.assertFalse(h.assess(s)['safe_recovery'])
 def test_real_log_threshold_includes_wine_and_xvfb_outputs(self):
  self.assertTrue(hasattr(h,'logs_over_limit'),'log file threshold helper missing')
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);r={'processes':{'server':{},'botA':{}},'log_limit_bytes':65536}
   (root/'xvfb.log').write_bytes(b'x'*65537);self.assertTrue(h.logs_over_limit(root,r));(root/'xvfb.log').unlink()
   (root/'server-wine.log').write_bytes(b'x'*65537);self.assertTrue(h.logs_over_limit(root,r))
 def test_log_limit_range_is_validated(self):
  self.assertTrue(hasattr(v,'validate_log_limit'),'validated log maintenance threshold missing')
  self.assertEqual(v.validate_log_limit({}),32*1024**2);self.assertEqual(v.validate_log_limit({'log_limit_bytes':65536}),65536)
  for bad in [0,65535,True,64*1024**2]:
   with self.assertRaises(ValueError):v.validate_log_limit({'log_limit_bytes':bad})
if __name__=='__main__':unittest.main()
