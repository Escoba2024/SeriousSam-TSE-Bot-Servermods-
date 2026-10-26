import unittest
import m1_recovery_gate as m

class RecoveryGateTests(unittest.TestCase):
    def sample(self):
        return dict(runtime='/srv/tse-session-qualification-master-m1-server-fault-a-20261026',scope='ISOLATED_NETNS_RETAIL_WINE',candidate_sha256='a'*64,expected_candidate_sha256='a'*64,source_intact=True,config_intact=True,duration_matrix_accepted=True,originals_intact=True,host_busy_percent=20,public_disabled=True,known_players_only=True,owned_fault=True,server_identity_verified=True,server_absent=True,cleanup_complete=True,sync_scan_complete=True,sync_bad=0,guard_finished=True,guard_error=None,child_exitcode=1,failure='query uncertain for more than 15 seconds',available_mib=1500,disk_free_gib=8.5,attempts=[],fault_at=1000,finished_at=1100,now=1130)
    def test_owned_injected_failure_can_restart_once_after_cleanup(self):
        self.assertEqual(m.decide_recovery(self.sample())['action'],'RESTART_ONE_PRIVATE_GENERATION')
    def test_unqualified_matrix_never_authorizes_restart(self):
        s=self.sample();s['duration_matrix_accepted']=False
        self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_unknown_player_blocks_recovery(self):
        s=self.sample();s['known_players_only']=False
        self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_sync_warning_never_becomes_retry(self):
        s=self.sample();s['sync_bad']=1
        self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_missing_log_scan_blocks(self):
        s=self.sample();s['sync_scan_complete']=False
        self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_pid_identity_uncertainty_blocks(self):
        s=self.sample();s['server_identity_verified']=False
        self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_cleanup_uncertainty_blocks(self):
        s=self.sample();s['cleanup_complete']=False
        self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_unowned_failure_cannot_authorize_restart(self):
        s=self.sample();s['owned_fault']=False
        self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_native_candidate_or_source_drift_blocks(self):
        for field,value in [('candidate_sha256','b'*64),('source_intact',False),('config_intact',False)]:
            s=self.sample();s[field]=value
            with self.subTest(field=field):self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_resource_pressure_blocks(self):
        for field,value in [('available_mib',767),('disk_free_gib',7.99),('guard_error','reserve failed')]:
            s=self.sample();s[field]=value
            with self.subTest(field=field):self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_second_restart_blocked(self):
        s=self.sample();s['attempts']=[1000]
        self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_missing_or_short_cooldown_blocks(self):
        for now in [1099,1129,float('nan')]:
            s=self.sample();s['now']=now
            with self.subTest(now=now):self.assertEqual(m.decide_recovery(s)['action'],'HOLD')
    def test_public_or_other_failure_blocks(self):
        for field,value in [('runtime','/srv/public'),('public_disabled',False),('failure','CRC check failed')]:
            s=self.sample();s[field]=value
            with self.subTest(field=field):self.assertEqual(m.decide_recovery(s)['action'],'HOLD')

if __name__=='__main__':unittest.main()
