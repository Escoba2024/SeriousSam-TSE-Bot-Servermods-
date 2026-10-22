"""Native harness safety contract; native games are only tested explicitly."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import os
import sqlite3
import time
from types import SimpleNamespace
from unittest.mock import patch

import qualify_bot_sessions as native
from test_bot_session_executor import config
from bot_session_executor import process_record
from bot_sessions import Planner


class QualificationSafety(unittest.TestCase):
    def test_action_report_rejects_wrong_local_count_or_drawn_frames(self):
        report=dict(verdict='ACTIVE_OK',lp_median=1,tick_hz_median=20,
                    render_skip_total=500,render_draw_total=0,config={'nullrender':'1'})
        self.assertTrue(native.valid_action_report(report))
        for changed in [dict(lp_median=4),dict(render_draw_total=1),dict(tick_hz_median=40),
                        dict(config={'nullrender':'0'}),dict(render_skip_total=0)]:
            self.assertFalse(native.valid_action_report(dict(report,**changed)))
    def test_low_memory_symbols_preserve_network_and_gameplay_configuration(self):
        source='\n'.join('persistent extern user INDEX '+key+'=(INDEX)9;' for key in
                         ['tex_iNormalSize','tex_iAnimationSize','tex_iEffectSize','shd_iStaticSize','shd_iDynamicSize'])
        source+='\nnet_iPort=27080;\nbot_iProfileSeed=77;\n'
        lowered=native.low_memory_symbols(source)
        self.assertIn('tex_iNormalSize=(INDEX)6;',lowered)
        self.assertIn('shd_iDynamicSize=(INDEX)5;',lowered)
        self.assertIn('net_iPort=27080;\nbot_iProfileSeed=77;',lowered)
        with self.assertRaises(ValueError):native.low_memory_symbols('unknown native layout')
    def test_inconsistent_transition_query_holds_without_spawning(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=Planner(root/'db',config(1))
            t=native.WineTransport(root,p,27080,':137','fixture cgroup')
            t.identities={i['id']:i for i in p.identities()}
            bad=dict(gamever='1.07',numplayers='1',maxplayers='16',player_0='Retail_Control',player_1='Player0')
            good=dict(gamever='1.07',numplayers='1',maxplayers='16',player_0='Retail_Control')
            try:
                t.absence={'fixture':2}
                with patch.object(native.q,'query',return_value=bad):
                    self.assertIsNone(t.snapshot(100))
                    self.assertFalse(t.query_valid)
                    self.assertEqual(t.absence,{})
                    with self.assertRaises(RuntimeError):t.snapshot(116)
                with patch.object(native.q,'query',return_value=good):
                    self.assertEqual(t.snapshot(117)['human_names'],['Retail_Control'])
                    self.assertTrue(t.query_valid)
            finally:p.close()

    def test_no_wineserver_kill_target_is_not_an_incomplete_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=Planner(root/'db',config(1))
            t=native.WineTransport(root,p,27080,':137','fixture cgroup');t.roles={'p0':root/'p0'}
            done=[subprocess.CompletedProcess([],1,stderr=b'no running server'),
                  subprocess.CompletedProcess([],0,stderr=b'')]
            try:
                with patch.object(native.subprocess,'run',side_effect=done):result=t.cleanup()
                self.assertFalse(any(row.get('errors') for row in result))
            finally:p.close()
    def test_log_gate_checks_archived_epochs_and_current_drain(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);game=root/'p0';game.mkdir()
            current=game/'SeriousSam.log';current.write_text('joined\n')
            archive=root/'history/p0-2';archive.mkdir(parents=True)
            old=archive/'SeriousSam.log';old.write_text('SYNCBAD: prior epoch\n')
            t=SimpleNamespace(root=root,roles={'p0':game},p=SimpleNamespace(config={'max_log_mib':32}))
            with self.assertRaises(RuntimeError):native.runtime_log_gate(t)
            old.write_text('normal prior epoch\n')
            current.write_text('Too many bad syncs\n')
            with self.assertRaises(RuntimeError):native.runtime_log_gate(t)

    def test_cleanup_window_error_still_stops_all_own_processes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=Planner(root/'db',config(1))
            t=native.WineTransport(root,p,27080,':137','fixture cgroup')
            children=[subprocess.Popen([sys.executable,'-c','input()'],cwd=root,
                                       stdin=subprocess.PIPE,text=True) for _ in range(2)]
            t.fixed={role:process_record(child.pid) for role,child in zip(('server','vanilla'),children)}
            t.procs=dict(zip(('server','vanilla'),children))
            try:
                with patch.object(native.q,'close_window',side_effect=OSError('own X display failed')):
                    result=t.cleanup()
                self.assertTrue(all(c.poll() is not None for c in children))
                self.assertEqual({r['role'] for r in result},{'server','vanilla'})
                self.assertTrue(next(r for r in result if r['role']=='vanilla')['errors'])
            finally:
                for child in children:
                    if child.poll() is None:child.terminate();child.wait(timeout=3)
                    child.stdin.close()
                p.close()
    def test_original_observer_caps_persistent_render_settings(self):
        source=('persistent extern INDEX sam_bFullScreen=(INDEX)1;\n'
                'persistent extern INDEX sam_iScreenSizeI=(INDEX)1920;\n'
                'persistent extern INDEX sam_iScreenSizeJ=(INDEX)1080;\n'
                'persistent extern user INDEX sam_iMaxFPSActive=(INDEX)500;\n'
                'persistent extern user INDEX sam_iMaxFPSInactive=(INDEX)10;\n')
        value=native.observer_symbols(source)
        self.assertIn('sam_bFullScreen=(INDEX)0;',value)
        self.assertIn('sam_iScreenSizeI=(INDEX)640;',value)
        self.assertIn('sam_iScreenSizeJ=(INDEX)480;',value)
        self.assertIn('sam_iMaxFPSActive=(INDEX)5;',value)
        self.assertIn('sam_iMaxFPSInactive=(INDEX)5;',value)
        with self.assertRaises(ValueError):native.observer_symbols('unknown layout')
    def test_native_child_exits_if_outer_guard_dies(self):
        with tempfile.TemporaryDirectory() as root:
            record=Path(root)/'child.json'
            program=('import os,subprocess,sys,time,json\n'
                     'from qualify_bot_sessions import arm_parent_death\n'
                     f'p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"],preexec_fn=arm_parent_death(os.getpid()))\n'
                     f'open({str(record)!r},"w").write(json.dumps({{"pid":p.pid}}))\n'
                     'time.sleep(30)\n')
            parent=subprocess.Popen([sys.executable,'-c',program],cwd=Path(native.__file__).parent,
                                    stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
            try:
                deadline=time.monotonic()+3
                while not record.exists() and parent.poll() is None and time.monotonic()<deadline:time.sleep(.02)
                if not record.exists():
                    _,err=parent.communicate(timeout=3)
                    self.fail('guarded child did not start: '+err)
                child=json.loads(record.read_text())['pid']
                binding=process_record(child)
                parent.terminate();parent.wait(timeout=3)
                deadline=time.monotonic()+3
                while native.probe_process(binding)=='LIVE' and time.monotonic()<deadline:time.sleep(.02)
                self.assertEqual(native.probe_process(binding),'ABSENT')
            finally:
                if parent.poll() is None:parent.terminate();parent.wait(timeout=3)
                parent.stderr.close()
    def test_disabled_config_never_starts_native_runtime(self):
        with self.assertRaises(ValueError):
            native.validate_native_config(dict(config(),enabled=False))
    def test_fatal_display_error_detected_before_population_timeout(self):
        self.assertTrue(native.runtime_error('FatalError:\nCannot set display mode!'))
        self.assertTrue(native.runtime_error('SYNCBAD: Client test'))
        self.assertFalse(native.runtime_error('ALL OK: Dedicated server is now running!'))
    def test_unshared_network_detected_using_namespace_interfaces(self):
        result=subprocess.run(['unshare','--net','--',sys.executable,'-c',
                               'import qualify_bot_sessions as n; print(n.isolated_network())'],
                              cwd=Path(native.__file__).parent,capture_output=True,text=True,timeout=5)
        if 'Operation not permitted' in result.stderr:self.skipTest('network namespace unavailable')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'True')
    def test_default_reads_config_but_creates_no_runtime(self):
        with tempfile.TemporaryDirectory() as root:
            source=Path(root)/'config.json';source.write_text(json.dumps(config()))
            runtime=Path(root)/'runtime'
            result=subprocess.run([sys.executable,native.__file__,'--config',str(source),
                                   '--runtime',str(runtime),'--duration','60'],
                                  capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'],'DRY_RUN_NO_RUNTIME')
            self.assertFalse(runtime.exists())

    def test_execute_refuses_production_path_before_creating_files(self):
        with tempfile.TemporaryDirectory() as root:
            source=Path(root)/'config.json';source.write_text(json.dumps(config()))
            runtime=Path(root)/'production'
            result=subprocess.run([sys.executable,native.__file__,'--config',str(source),
                                   '--runtime',str(runtime),'--duration','60','--execute'],
                                  capture_output=True,text=True,timeout=5)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(runtime.exists())

    def test_eight_bot_config_and_minimum_host_reserve(self):
        self.assertTrue(native.resource_gate(available_mib=1000,disk_free_gib=10,busy_percent=60))
        for args in [dict(available_mib=700,disk_free_gib=10,busy_percent=60),
                     dict(available_mib=1000,disk_free_gib=7,busy_percent=60),
                     dict(available_mib=1000,disk_free_gib=10,busy_percent=90)]:
            self.assertFalse(native.resource_gate(**args))
    def test_another_client_requires_memory_beyond_emergency_reserve(self):
        self.assertFalse(native.resource_gate(available_mib=1000,disk_free_gib=10,busy_percent=60,launch=True))
        self.assertTrue(native.resource_gate(available_mib=1100,disk_free_gib=10,busy_percent=60,launch=True))

    def test_live_foreign_process_cannot_be_adopted_as_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);game=root/'p0';(game/'Players').mkdir(parents=True)
            (game/'Players/Player0.plr').write_bytes(b'fixture')
            (game/'Players/Player0.plr.guid').write_bytes(b'x'*16)
            p=Planner(root/'db',config(1))
            t=native.WineTransport(root,p,27080,':137','private cgroup')
            t.roles={'p0':game};t.current_names=set();t.query_at=100;t.query_valid=True
            child=subprocess.Popen([sys.executable,'-c','input()'],cwd=root,
                                   stdin=subprocess.PIPE,text=True)
            try:
                p.db.execute('INSERT INTO native_process VALUES (?,?,?,?,?)',
                             ('p0',1,json.dumps(process_record(child.pid)),
                              native.q.sha(game/'Players/Player0.plr'),
                              native.q.sha(game/'Players/Player0.plr.guid')))
                state=dict(id='p0',epoch=1,status='PLAYING')
                observed=t.observe(state,p.identities()[0],100)
                self.assertFalse(observed['ownership_verified'])
            finally:
                child.communicate('\n',timeout=3);p.close()
