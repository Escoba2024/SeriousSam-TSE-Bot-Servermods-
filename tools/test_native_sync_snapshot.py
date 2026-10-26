import unittest
import native_sync_snapshot as n

class SnapshotTests(unittest.TestCase):
    def snapshot(self, tick=1101004800, crc=123, action='00'*40):
        return dict(event='snapshot',tick_bits=tick,sequence=99,level=1,pause=0,extensive=0,crc=crc,actions=[dict(slot=0,kind='last',bytes=action)],components=[])
    def test_divergent_crc_is_not_sync_pass(self):
        result=n.compare_snapshots([self.snapshot()],[self.snapshot(crc=124)])
        self.assertEqual(result['status'],'DIVERGENT')
        self.assertEqual(result['first_difference'],'crc')
    def test_action_bytes_locate_input_divergence_before_crc(self):
        result=n.compare_snapshots([self.snapshot()],[self.snapshot(crc=124,action='01'+'00'*39)])
        self.assertEqual(result['first_difference'],'actions')
    def test_same_tick_different_sequence_does_not_pair(self):
        other=self.snapshot();other['sequence']=100
        self.assertEqual(n.compare_snapshots([self.snapshot()],[other])['status'],'INCOMPLETE')
    def test_no_shared_ticks_does_not_pass(self):
        self.assertEqual(n.compare_snapshots([self.snapshot()],[self.snapshot(tick=1101529088)])['status'],'INCOMPLETE')
    def test_identical_snapshot_is_only_bounded_match(self):
        result=n.compare_snapshots([self.snapshot()],[self.snapshot()])
        self.assertEqual(result['status'],'BOUNDED_SNAPSHOT_MATCH')
        self.assertFalse(result['release_qualified'])
    def test_truncated_action_rejected(self):
        with self.assertRaises(ValueError):n.compare_snapshots([self.snapshot(action='00')],[self.snapshot()])
    def test_conflicting_duplicate_is_not_overwritten(self):
        with self.assertRaises(ValueError):n.compare_snapshots([self.snapshot(),self.snapshot(crc=124)],[self.snapshot()])
    def test_invalid_tick_rejected(self):
        for value in [True,-1,0x7fc00000]:
            with self.subTest(tick=value),self.assertRaises(ValueError):n.compare_snapshots([self.snapshot(tick=value)],[self.snapshot()])

class CaptureGuardTests(unittest.TestCase):
    def inputs(self):
        root='/srv/tse-session-qualification-master-owned'
        report=dict(status='MEASURING',scope='ISOLATED_NETNS_RETAIL_WINE',network_namespace='net:[222]',cgroup='/sys/fs/cgroup/tse-sessions-123')
        proc=dict(pid=123,start_ticks=456,comm='SeriousSam.exe',uid=65534,cwd=root+'/gamer-006',netns='net:[222]',cgroup='0::/tse-sessions-123')
        return root,report,proc,'net:[111]',n.ENGINE_SHA256
    def test_bound_private_client_admitted(self):
        self.assertEqual(n.validate_capture_binding(*self.inputs()),'gamer-006')
    def test_public_namespace_rejected(self):
        args=list(self.inputs());args[3]='net:[222]'
        with self.assertRaises(ValueError):n.validate_capture_binding(*args)
    def test_stale_runtime_rejected(self):
        args=list(self.inputs());args[1]['status']='FAIL'
        with self.assertRaises(ValueError):n.validate_capture_binding(*args)
    def test_wrong_engine_rejected(self):
        args=list(self.inputs());args[4]='0'*64
        with self.assertRaises(ValueError):n.validate_capture_binding(*args)
    def test_other_cgroup_rejected(self):
        args=list(self.inputs());args[2]['cgroup']='0::/other'
        with self.assertRaises(ValueError):n.validate_capture_binding(*args)
    def test_unsafe_hook_entry_rejected(self):
        with self.assertRaises(ValueError):n.approved_entry(0xe34ca,bytes.fromhex('3bd0909090'))
    def test_modified_export_prologue_rejected(self):
        with self.assertRaises(ValueError):n.approved_entry(0xe5b10,bytes.fromhex('e900000000'))
    def test_reviewed_function_entry_admitted(self):
        self.assertTrue(n.approved_entry(0xe5b10,bytes.fromhex('558bec6aff')))

if __name__=='__main__':unittest.main()
