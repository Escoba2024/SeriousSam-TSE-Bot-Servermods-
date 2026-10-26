import copy
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import unittest
import m1_duration_acceptance as m

class DurationGateTests(unittest.TestCase):
    def fixture(self):
        result=dict(status='PASS_LIMITED_SESSION_LIFECYCLE',scope='ISOLATED_NETNS_RETAIL_WINE',runtime_root='/srv/tse-session-qualification-master-m1-fixture',cleanup_observed_complete=True,cgroup='/sys/fs/cgroup/tse-sessions-123',network_namespace='net:[222]',elapsed_s=3700,utc='1970-01-01T01:01:40Z',dll_sha256='a'*64,max_bots=1,peak_playing=1,original_client=True,sync_scan_complete=True,sync_bad=0,measured_s=3720,all_bots_drained=True,new_throttled_periods=0,cleanup=[dict(role=x,errors=[]) for x in ['server','vanilla','gamer-000']],unmounts=[dict(path='/srv/tse-session-qualification-master-m1-fixture/'+prefix+role,exitcode=0) for role in ['server','vanilla','gamer-000'] for prefix in ['','prefix-']],telemetry={'gamer-000':[dict(playing_s=3700,reports=[dict(verdict='ACTIVE_OK',exit_code=0,tick_hz_median=20)])]})
        guard=dict(status='FINISHED',child_exitcode=0,samples=[dict(at=i,available_mib=1500,disk_free_gib=8.5,host_busy_percent=20) for i in range(0,3711,5)])
        samples=[dict(elapsed_s=i,active=1,population=2,decisions=[dict(id='gamer-000',action='healthy')],processes={x:dict(start_ticks=j+1,pss_mib=100) for j,x in enumerate(['server','vanilla','gamer-000'])}) for i in range(3601)]
        return result,guard,samples
    def verdict(self,parts):return m.evaluate_stage(*parts,bots=1,required_s=3600,dll_sha256='a'*64)
    def test_complete_continuous_receipt_accepted_but_not_release(self):
        got=self.verdict(self.fixture());self.assertEqual(got['status'],'DURATION_RECEIPTS_ACCEPTED');self.assertFalse(got['m1_complete'])
    def test_wall_clock_without_continuous_population_is_rejected(self):
        p=self.fixture();p[2][1800]['active']=0
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_unobserved_gap_cannot_count_as_stability(self):
        p=self.fixture();p[2][1700:1800]=[]
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_replaced_process_generation_resets_interval(self):
        p=self.fixture()
        for row in p[2][1800:]:row['processes']['gamer-000']['start_ticks']=999
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_unknown_player_is_not_full_bot_population(self):
        p=self.fixture();p[2][1800]['population']=3
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_guard_pressure_rejects_even_successful_result(self):
        p=self.fixture();p[1]['samples'][0]['disk_free_gib']=7.99
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_cleanup_failure_rejects(self):
        p=self.fixture();p[0]['unmounts'][0]['exitcode']=1
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_wrong_candidate_rejects(self):
        p=self.fixture();p[0]['dll_sha256']='b'*64
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_missing_native_telemetry_rejects(self):
        p=self.fixture();p[0]['telemetry']={}
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_short_playing_window_rejects(self):
        p=self.fixture();p[0]['telemetry']['gamer-000'][0]['playing_s']=3500
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_nonmonotonic_sample_is_rejected(self):
        p=self.fixture();p[2][1800]['elapsed_s']=0
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_unrelated_process_identity_rejects(self):
        p=self.fixture()
        for row in p[2]:row['processes']['unrelated']=row['processes'].pop('gamer-000')
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_unrelated_decision_identity_rejects(self):
        p=self.fixture()
        for row in p[2]:row['decisions'][0]['id']='other'
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_empty_cleanup_rows_reject(self):
        p=self.fixture();p[0]['cleanup']=[{},{},{}]
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_duplicate_unmount_receipts_reject(self):
        p=self.fixture();p[0]['unmounts']=[p[0]['unmounts'][0]]*6
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_observed_live_or_mounted_resources_reject(self):
        p=self.fixture();p[0]['cleanup_observed_complete']=False
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_single_guard_sample_cannot_cover_duration(self):
        p=self.fixture();p[1]['samples']=p[1]['samples'][:1]
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_foreign_time_window_guard_rejects(self):
        p=self.fixture()
        for row in p[1]['samples']:row['at']+=10000
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_missing_final_guard_observation_rejects(self):
        p=self.fixture();p[1]['samples']=p[1]['samples'][:-10]
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def matrix_fixture(self,bots,seconds):
        result,guard,_=self.fixture();root=result['runtime_root'];ids=['gamer-%03d'%i for i in range(bots)];roles=['server','vanilla']+ids
        result.update(max_bots=bots,peak_playing=bots,measured_s=seconds+100,elapsed_s=seconds+100,utc=datetime.fromtimestamp(seconds+100,timezone.utc).isoformat(),cleanup=[dict(role=x,errors=[]) for x in roles],unmounts=[dict(path=root+'/'+prefix+role,exitcode=0) for role in roles for prefix in ['','prefix-']],telemetry={i:[dict(playing_s=seconds+90,reports=[dict(verdict='ACTIVE_OK',exit_code=0,tick_hz_median=20)])] for i in ids})
        guard['samples']=[dict(at=i,available_mib=1500,disk_free_gib=8.5,host_busy_percent=20) for i in range(0,seconds+111,5)]
        samples=[dict(elapsed_s=i,active=bots,population=bots+1,decisions=[dict(id=x,action='healthy') for x in ids],processes={x:dict(start_ticks=j+1,pss_mib=100) for j,x in enumerate(roles)}) for i in range(0,seconds+1,2)]
        return result,guard,samples
    def test_four_and_eight_native_duration_boundaries(self):
        for bots,seconds in [(4,3600),(8,7200)]:
            with self.subTest(bots=bots):
                parts=self.matrix_fixture(bots,seconds)
                self.assertEqual(m.evaluate_stage(*parts,bots=bots,required_s=seconds,dll_sha256='a'*64)['status'],'DURATION_RECEIPTS_ACCEPTED')
                parts[2].pop()
                self.assertEqual(m.evaluate_stage(*parts,bots=bots,required_s=seconds,dll_sha256='a'*64)['status'],'REJECTED')
    def test_runtime_wrapper_rejects_actual_source_inventory_drift(self):
        with tempfile.TemporaryDirectory(prefix='tse-session-qualification-master-m1-test-',dir='/srv') as d:
            root=Path(d);(root/'source-sha256.json').write_text(json.dumps({'qualify_bot_sessions.py':'a'*64}))
            with self.assertRaisesRegex(ValueError,'NATIVE_PRODUCER_SOURCE_DRIFT'):
                m.evaluate_runtime(root,bots=1,required_s=3600,dll_sha256='a'*64,harness_sha256={'qualify_bot_sessions.py':'b'*64})
    def test_samples_outside_native_run_reject(self):
        p=self.fixture()
        for row in p[2]:row['elapsed_s']+=100000
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_incomplete_sync_scan_rejects(self):
        p=self.fixture();p[0]['sync_scan_complete']=False
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_observed_sync_warning_rejects(self):
        p=self.fixture();p[0]['sync_bad']=1
        self.assertEqual(self.verdict(p)['status'],'REJECTED')
    def test_stale_guard_does_not_authorize_acceptance(self):
        p=self.fixture();p[1]['status']='MONITORING'
        self.assertEqual(self.verdict(p)['status'],'REJECTED')

if __name__=='__main__':unittest.main()
