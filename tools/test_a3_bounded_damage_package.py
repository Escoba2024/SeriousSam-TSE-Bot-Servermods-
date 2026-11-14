"""Static private-package integration invariants; no native operations."""
import ast
import json
import os
from pathlib import Path
import unittest
import types

PACKAGE=os.environ.get('TSE_A3_BOUNDED_PACKAGE')


@unittest.skipUnless(PACKAGE,'explicit disabled bounded-worker source package required')
class BoundedPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(PACKAGE);cls.manifest=json.loads((cls.root/'source-manifest.json').read_text())
        cls.parent=Path(cls.manifest['worker_derivation']['parent'])
        cls.source=(cls.root/'run-a3-direct020.py').read_text();cls.original=(cls.parent/'run-a3-direct020.py').read_text()

    def test_all_three_runtime_gates_and_manifest_disabled(self):
        for name in ('run-a3-direct020.py','original_damage_worker.py','original_damage_collector.py'):
            tree=ast.parse((self.root/name).read_text())
            flags=[n.value.value for n in tree.body if isinstance(n,ast.Assign)and
                   any(isinstance(t,ast.Name)and t.id=='RUNTIME_REVIEWED'for t in n.targets)]
            self.assertEqual(flags,[False])
        self.assertIs(self.manifest['runtime_reviewed'],False);self.assertIs(self.manifest['qualified'],False)

    def test_no_frida_import_rpc_or_session_in_role_owning_parent(self):
        tree=ast.parse(self.source)
        imports=[n.module for n in ast.walk(tree)if isinstance(n,ast.ImportFrom)]
        imports.extend(alias.name for n in ast.walk(tree)if isinstance(n,ast.Import)for alias in n.names)
        self.assertFalse(any(v and v.startswith('frida')for v in imports))
        self.assertNotIn('exports_sync',self.source);self.assertNotIn('frida_session',self.source)
        self.assertNotIn('frida_script',self.source)
        self.assertIn('damage_worker.arm()',self.source);self.assertIn('damage_worker.drain()',self.source)
        self.assertIn('damage_worker.close()',self.source)

    def test_reap_is_after_normal_game_close_and_quiescence_before_restore(self):
        begin=self.source.index("   for role in ('vanilla','botB','botA','server'):")
        close=self.source.index('try:close(role)',begin)
        quiescent=self.source.index('if normally_closed:whole_quiescent()',close)
        reap=self.source.index('damage_worker.finish(roles_closed=normally_closed)',quiescent)
        restore=self.source.index('transaction.restore()',reap)
        self.assertLess(close,quiescent);self.assertLess(quiescent,reap);self.assertLess(reap,restore)
        self.assertIn("normally_closed=set(records)=={'server','botA','botB','vanilla'}and all(r.get('closed')is True",self.source)

    def test_packet_validation_and_physical_damage_bounds_unchanged(self):
        def block(source):
            start=source.index('     previous=len(all_damage_records)')
            end=source.index("'passive hook read/queue/detach failure'",start)+len("'passive hook read/queue/detach failure'")
            return source[start:end]
        self.assertEqual(block(self.original),block(self.source))
        for name in self.manifest['direct_tiers']['same_damage_host_restore_files']:
            self.assertEqual((self.root/name).read_bytes(),(self.parent/name).read_bytes())
        self.assertNotIn('frozen-v2/damage_readonly.js',self.manifest['direct_tiers']['same_damage_host_restore_files'])
        for fragment in ("'max_records':64","'max_calls':1024","'ttl_ms':125000","'binding_ms':2000","'binding_calls':256"):
            self.assertIn(fragment,self.source)

    def test_worker_lifecycle_uses_same_single_packet_denominator_and_original_coverage(self):
        self.assertIn("for packet in result.get('packets',[]):accept_trace_packet(packet)",self.source)
        self.assertIn('guard_module.coverage(f,',self.source)
        self.assertIn('trace_reasons(f,server[0])',self.source)
        self.assertIn('damage.additional_trace_reasons(f)',self.source)
        self.assertIn("assert result.get('closed')is True and result.get('idle_verified')is True and result.get('original_bytes_verified')is True",self.source)

    def close_fixture(self,*,identity=None,pid=17,ready=True,empty=True,quiescent_error=False,changed_identity=False):
        events=[];record=dict(identity=identity,closed=False)
        def own_identity(role,unit):return(18,92)if changed_identity else(17,91)
        def quiescent(root):
            events.append('quiescent')
            if quiescent_error:raise RuntimeError('own root occupied')
        def wait(predicate,seconds,message):
            events.append(('wait',seconds));self.assertTrue(predicate(),message)
        backend=types.SimpleNamespace(pid=lambda unit:pid,empty=lambda unit:empty,ready=lambda role,unit:ready,
            identity=own_identity,quiescent=quiescent,same=lambda identity:False,wait=wait,
            scope=dict(close_window=lambda pid,display:(events.append('normal_window_close')or 1)))
        os_stub=types.SimpleNamespace(kill=lambda pid,sig:events.append(('signal',sig)))
        node=next(n for n in ast.walk(ast.parse(self.source))if isinstance(n,ast.FunctionDef)and n.name=='close')
        env=dict(records=dict(botA=record),B=backend,R=Path('/synthetic-fixture'),unit=lambda role:'own-'+role,
                 os=os_stub,signal=types.SimpleNamespace(SIGINT=2),DISPLAY='synthetic',emit=lambda *a,**k:events.append(a[0]))
        exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-a3-normal-close','exec'),env)
        return env['close'],record,events

    def test_partial_ready_start_acquires_fresh_strict_identity_then_closes_normally(self):
        close,record,events=self.close_fixture()
        close('botA');self.assertTrue(record['closed']);self.assertEqual(record['identity'],(17,91))
        self.assertTrue(record['started']);self.assertIn('normal_window_close',events)
        self.assertEqual([x for x in events if isinstance(x,tuple)],[('wait',35),('wait',30)])

    def test_partial_unstarted_empty_unit_requires_actual_root_quiescence(self):
        close,record,events=self.close_fixture(pid=0)
        close('botA');self.assertTrue(record['closed']);self.assertFalse(record['started'])
        self.assertIsNone(record['identity']);self.assertIn('quiescent',events);self.assertNotIn('normal_window_close',events)
        close,record,events=self.close_fixture(pid=0,quiescent_error=True)
        with self.assertRaises(RuntimeError):close('botA')
        self.assertFalse(record['closed']);self.assertNotIn('normal_window_close',events)

    def test_partial_unknown_notready_or_nonempty_never_forces_or_marks_closed(self):
        for kwargs in [dict(ready=False),dict(pid=0,empty=False,ready=False)]:
            close,record,events=self.close_fixture(**kwargs)
            with self.assertRaises(AssertionError):close('botA')
            self.assertFalse(record['closed']);self.assertNotIn('normal_window_close',events)

    def test_existing_changed_identity_is_never_reassigned_or_signalled(self):
        close,record,events=self.close_fixture(identity=(17,91),changed_identity=True)
        with self.assertRaises(AssertionError):close('botA')
        self.assertEqual(record['identity'],(17,91));self.assertFalse(record['closed'])
        self.assertNotIn('normal_window_close',events)


if __name__=='__main__':unittest.main()
