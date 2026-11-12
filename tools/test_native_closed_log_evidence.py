import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from native_closed_log_evidence import archive_closed_role_logs

class ClosedLogs(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.roles=('server','botA','botB','vanilla')
        self.roots={r:self.root/r for r in self.roles}
        for p in self.roots.values():p.mkdir()
        self.sources={r:self.roots[r]/('Dedicated_BotTest.log' if r=='server' else 'SeriousSam.log')for r in self.roles}
        self.archives={r:self.root/(r+'-final.log')for r in self.roles}
        self.cleanup={r:{'closed':True}for r in self.roles}
        for p in self.sources.values():p.write_text('Started original role\nnormal renderer cleanup\n')
    def run_audit(self,**kw):
        args=dict(role_roots=self.roots,source_logs=self.sources,archive_logs=self.archives,cleanup=self.cleanup,expected_roles=self.roles)
        args.update(kw);return archive_closed_role_logs(**args)
    def test_normal_close_archives_exact_bytes_without_runtime(self):
        r=self.run_audit();self.assertTrue(r.accepted,r.reasons);self.assertEqual(r.reasons,())
        self.assertEqual(set(r.logs),set(self.roles))
        for role in self.roles:
            data=self.sources[role].read_bytes();self.assertEqual(self.archives[role].read_bytes(),data)
            self.assertEqual(r.logs[role]['sha256'],hashlib.sha256(data).hexdigest())
    def test_syncbad_and_kick_added_during_close_are_in_final_evidence(self):
        # The previous window scan was clean; normal close appends a real late
        # sync/kick before the caller reports closed=True and invokes this gate.
        self.assertNotIn('SYNCBAD',self.sources['botA'].read_text())
        self.sources['botA'].write_text(self.sources['botA'].read_text()+"SYNCBAD: Client 'private-name', Sequence 17 Tick 20.00 - bad 10\nDisconnected: Too many bad syncs\n")
        r=self.run_audit();self.assertFalse(r.accepted);self.assertIn('log_events:botA',r.reasons)
        self.assertEqual(r.logs['botA']['events']['bad_sync'],[3]);self.assertEqual(r.logs['botA']['events']['sync_disconnect'],[4])
        self.assertIn(b'Too many bad syncs',self.archives['botA'].read_bytes())
        self.assertNotIn('private-name',str(r.logs),'summary cannot expose player names')
    def test_crash_invalid_action_and_crc_failures(self):
        for role,text in zip(self.roles,['Access violation at address 1','Fatal Error: broken','[CecilInvalidAction] bad','CRC check failed']):self.sources[role].write_text(text+'\n')
        r=self.run_audit();self.assertFalse(r.accepted);self.assertEqual(set(r.reasons),{'log_events:'+x for x in self.roles})
    def test_missing_log_does_not_use_stale_archive(self):
        self.sources['server'].unlink();self.archives['server'].write_text('old clean evidence\n')
        r=self.run_audit();self.assertFalse(r.accepted);self.assertTrue(any('server' in x for x in r.reasons));self.assertEqual(self.archives['server'].read_text(),'old clean evidence\n')
    def test_not_closed_never_reads_or_copies_that_role(self):
        self.cleanup['botA']['closed']=False;self.sources['botA'].unlink()
        r=self.run_audit();self.assertIn('not_normally_closed:botA',r.reasons);self.assertNotIn('botA',r.logs);self.assertFalse(self.archives['botA'].exists())
        self.assertEqual(set(r.logs),set(self.roles)-{'botA'})
    def test_truthy_close_string_is_not_attestation(self):
        self.cleanup['server']['closed']='true';self.assertIn('not_normally_closed:server',self.run_audit().reasons)
    def test_missing_or_unknown_roles_reject_before_copy(self):
        for mapping in ['role_roots','source_logs','archive_logs','cleanup']:
            with self.subTest(mapping=mapping):
                original={'role_roots':self.roots,'source_logs':self.sources,'archive_logs':self.archives,'cleanup':self.cleanup}[mapping]
                bad=dict(original);bad['unexpected']=bad.pop('botA')
                r=self.run_audit(**{mapping:bad});self.assertFalse(r.accepted);self.assertFalse(any(p.exists()for p in self.archives.values()))
    def test_swapped_role_source_and_root_cannot_pass(self):
        sources=dict(self.sources);sources['botA'],sources['botB']=sources['botB'],sources['botA']
        r=self.run_audit(source_logs=sources);self.assertFalse(r.accepted);self.assertIn('wrong_role_log:botA',r.reasons)
    def test_swapped_role_roots_cannot_rebind_wrong_log(self):
        roots=dict(self.roots);roots['botA'],roots['botB']=roots['botB'],roots['botA']
        self.assertFalse(self.run_audit(role_roots=roots).accepted)
    def test_aliasing_and_source_overwrite_fail_closed(self):
        archives=dict(self.archives);archives['botA']=self.sources['botA']
        before=self.sources['botA'].read_bytes();r=self.run_audit(archive_logs=archives)
        self.assertFalse(r.accepted);self.assertEqual(self.sources['botA'].read_bytes(),before)
    def test_copy_failure_and_existing_destination_do_not_pass(self):
        self.archives['botA'].mkdir();r=self.run_audit();self.assertFalse(r.accepted);self.assertIn('archive_failed:botA:FileExistsError',r.reasons)
    def test_empty_and_oversized_logs_fail(self):
        self.sources['server'].write_bytes(b'');self.sources['botA'].write_bytes(b'x'*33)
        r=self.run_audit(max_log_bytes=32);self.assertFalse(r.accepted);self.assertIn('empty_log:server',r.reasons);self.assertIn('log_too_large:botA',r.reasons)
    def test_symlink_to_other_role_is_wrong_evidence(self):
        self.sources['botA'].unlink();self.sources['botA'].symlink_to(self.sources['botB']);r=self.run_audit();self.assertFalse(r.accepted);self.assertIn('wrong_role_log:botA',r.reasons)
    def test_duplicate_role_log_hardlink_cannot_pass(self):
        self.sources['botB'].unlink();os.link(self.sources['botA'],self.sources['botB'])
        r=self.run_audit();self.assertFalse(r.accepted);self.assertIn('duplicate_role_log:botB',r.reasons)
    def test_generic_disconnect_is_recorded_but_normal_close_is_not_sync_kick(self):
        self.sources['vanilla'].write_text('Disconnected normally\nrenderer cleanup\n');r=self.run_audit();self.assertTrue(r.accepted)
    def test_invalid_roles_cannot_vacuously_pass(self):
        for roles in [(),('server','server'),'server']:
            with self.subTest(roles=roles):self.assertFalse(self.run_audit(expected_roles=roles).accepted)

if __name__=='__main__':unittest.main()
