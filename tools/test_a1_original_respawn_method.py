import importlib.util
from pathlib import Path
import unittest
import copy
import os
import types
import tempfile


def module():
    p=Path(__file__).with_name('a1_original_respawn_method.py')
    if not p.exists():return None
    s=importlib.util.spec_from_file_location('new_respawn_method',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


class Clock:
    def __init__(self):self.t=1.
    def __call__(self):return self.t
    def sleep(self,n):self.t+=n


def replica(frame):
    a=frame['actors']['vanilla']
    row={'slot':0,'present':True,'entity_id':a['id'],'spawned_tick':a['spawn_clock'],
         'health':a['health'],'last_buttons':a['buttons_now'],
         'process_identity':frame['identity']['vanilla']}
    return {'original_replica':row,'roles':{'vanilla':dict(row)},
            'vanilla_process_identity':frame['identity']['vanilla']}


class OwnershipReadBounds(unittest.TestCase):
    def setUp(self):
        self.m=module();self.assertTrue(hasattr(self.m,'OwnershipReads'),'bounded fresh ownership-read adapter absent')
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.evidence=Path(self.tmp.name);self.clock=Clock()
        self.reads=self.m.OwnershipReads(self.evidence,self.clock,85.)

    def capture(self,path):
        data=b'{"actual":"fresh"}\n'
        with os.fdopen(os.open(path/'natural-ai-ownership.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(data)
        return {'fresh':str(path)}

    def test_serial_cap_includes_initial_and_prohibits_1025_before_callback(self):
        calls=[]
        self.reads.attempts=[{}]*1023
        self.reads.read(lambda p:(calls.append(str(p)),self.capture(p))[1])
        with self.assertRaisesRegex(ValueError,'1024'):self.reads.read(lambda p:calls.append('bad'))
        self.assertEqual(len(calls),1);self.assertTrue(self.reads.failed)
        self.assertEqual(len(self.reads.attempts),1024)

    def test_aggregate_cap_reserves_actual_old_single_receipt_max_before_read(self):
        self.assertEqual(self.m.OWNERSHIP_RECEIPT_LIMIT,1536*1024)
        self.assertEqual(self.m.OWNERSHIP_TOTAL_LIMIT,2*self.m.OWNERSHIP_RECEIPT_LIMIT)
        self.reads.payload_bytes=self.m.OWNERSHIP_RECEIPT_LIMIT+1;calls=[]
        with self.assertRaisesRegex(ValueError,'payload budget'):self.reads.read(lambda p:calls.append(p))
        self.assertFalse(calls);self.assertFalse(self.reads.attempts)

    def test_pre_and_post_real_absolute_deadline_fail_no_reset(self):
        self.clock.t=85.;calls=[]
        with self.assertRaisesRegex(ValueError,'deadline'):self.reads.read(lambda p:calls.append(p))
        self.assertFalse(calls)
        self.reads=self.m.OwnershipReads(self.evidence,self.clock,85.);self.clock.t=84.
        def late(p):value=self.capture(p);self.clock.t=85.;return value
        with self.assertRaisesRegex(ValueError,'deadline'):self.reads.read(late)
        self.assertTrue(self.reads.failed);self.assertEqual(len(self.reads.attempts),1)
        self.assertGreater(self.reads.payload_bytes,0)

    def test_capture_primary_exception_retained_with_missing_evidence_secondary(self):
        primary=OSError('actual ownership read failed')
        def bad(p):raise primary
        with self.assertRaises(OSError)as result:self.reads.read(bad)
        self.assertIs(result.exception,primary);self.assertTrue(self.reads.failed)
        self.assertTrue(self.reads.attempts[0]['custody_errors'])
        with self.assertRaisesRegex(ValueError,'sticky'):self.reads.read(self.capture)

    def test_missing_receipt_permissions_and_preexisting_namespace_fail_closed(self):
        with self.assertRaises(FileNotFoundError):self.reads.read(lambda p:{})
        self.reads=self.m.OwnershipReads(self.evidence,self.clock,85.)
        with self.assertRaises(FileExistsError):self.reads.read(self.capture)
        self.assertTrue(self.reads.failed)

    def test_after_validation_failure_actual_receipt_remains_accounted(self):
        def bad(p):self.capture(p);raise ValueError('real role/hash guard')
        with self.assertRaisesRegex(ValueError,'real role/hash guard'):self.reads.read(bad)
        row=self.reads.attempts[0];self.assertEqual(row['status'],'FAIL')
        self.assertGreater(self.reads.payload_bytes,0);self.assertEqual(row['payload_bytes'],self.reads.payload_bytes)
        self.assertEqual((self.evidence/row['receipt']).stat().st_mode&0o777,0o600)


class NormalFire(unittest.TestCase):
    def setUp(self):
        self.m=module();self.assertIsNotNone(self.m,'separate normal-fire method is missing')

    def port(self,clock,*,down_error=False,up_error=False,slow=False):
        m=self.m
        class Endpoint:
            def __init__(self):self.calls=[];self.held=False
            def verify(self):self.calls.append('verify')
            def check_focus(self):self.calls.append('focus')
            def neutral(self,controls):self.calls.append('neutral');self.test_neutral()
            def test_neutral(self):
                if self.held:raise ValueError('not neutral')
            def down(self,c,*,submit):
                def native():
                    self.calls.append('native-down');self.held=True
                    if down_error:raise ValueError('actual Down native exception')
                    return 1
                return submit(native)
            def up(self,c):
                self.calls.append('native-up');self.held=False
                if up_error:raise ValueError('actual Up metadata exception')
            def released(self,c):self.calls.append('released');self.test_neutral()
        return Endpoint()

    def test_actual_down_up_release_and_measured_hold(self):
        c=Clock();e=self.port(c);r={};observed=[]
        self.m.fire_pulse(e,clock=c,sleep=c.sleep,before_press=lambda:None,observe=lambda:observed.append(c()),deadline=20.,receipt=r)
        self.assertEqual(e.calls.count('native-down'),1);self.assertEqual(e.calls.count('native-up'),1)
        self.assertEqual(e.calls.count('released'),1);self.assertTrue(observed)
        self.assertLessEqual(r['input_to_release_seconds'],.35);self.assertGreaterEqual(r['held_seconds'],.1)
        self.assertFalse(r['native_respawn_proven'])

    def test_partial_down_and_up_metadata_failure_still_attempt_release_neutral(self):
        for d,u in[(True,False),(False,True)]:
            c=Clock();e=self.port(c,down_error=d,up_error=u);r={}
            with self.subTest(down=d,up=u),self.assertRaises(ValueError):self.m.fire_pulse(e,clock=c,sleep=c.sleep,before_press=lambda:None,observe=lambda:None,deadline=20.,receipt=r)
            self.assertEqual(e.calls.count('native-up'),1);self.assertEqual(e.calls.count('released'),1)
            self.assertEqual(r['status'],'FAIL')

    def test_focus_before_press_deadline_overrun_and_clock_fail_closed(self):
        for mode in['focus','reserve','slow','backward']:
            c=Clock();e=self.port(c);r={}
            def observe():c.t+=.4 if mode=='slow'else -1. if mode=='backward'else 0.
            def before():
                if mode=='focus':raise ValueError('actual focus drift')
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.m.fire_pulse(e,clock=c,sleep=c.sleep,before_press=before,observe=observe,deadline=2. if mode=='reserve' else 20.,receipt=r)
            if mode in('focus','reserve'):self.assertNotIn('native-down',e.calls)
            else:self.assertEqual(e.calls.count('native-up'),1)

    def test_journal_preserves_real_native_exception_and_up_after_sticky(self):
        c=Clock();j=self.m.FireJournal(c);called=[]
        def down():called.append('down');raise OSError('real C down error')
        with self.assertRaisesRegex(OSError,'real C down error'):j.invoke(down,True)
        self.assertEqual(j.invoke(lambda:called.append('up')or 1,False),1)
        self.assertEqual(called,['down','up']);self.assertTrue(j.failed)
        self.assertTrue(j.attempts[0]['native_invoked']);self.assertEqual(len(j.attempts),2)

    def test_journal_limit_and_first_clock_failure_release_are_real(self):
        c=Clock();j=self.m.FireJournal(c);j.attempts=[{}for _ in range(96)];calls=[]
        with self.assertRaises(ValueError):j.invoke(lambda:calls.append(1),True)
        self.assertFalse(calls)
        j=self.m.FireJournal(lambda:(_ for _ in()).throw(ValueError('clock')))
        with self.assertRaises(ValueError):j.invoke(lambda:calls.append('down'),True)
        with self.assertRaises(ValueError):j.invoke(lambda:calls.append('up')or 1,False)
        self.assertEqual(calls,['up']);self.assertEqual(len(j.attempts),2)

    def control_case(self,scenario='normal'):
        self.assertTrue(callable(getattr(self.m,'make_window_class',None)),'new explicit Window factory missing')
        p=Path('/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115/first_state_inputfree_method.py').resolve(strict=True)
        with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:s=f.read()
        legacy=types.ModuleType('actual_old_inputfree');legacy.__file__=str(p);exec(compile(s,str(p),'exec'),legacy.__dict__)
        from test_a1_original_respawn_policy import frame
        c=Clock();endpoint=self.port(c);j=self.m.FireJournal(c);e=endpoint
        original_down=e.down;original_up=e.up
        e.down=lambda control,submit:original_down(control,submit=lambda fn,*args:submit(lambda:j.invoke(fn,True)))
        def up(control):
            result=j.invoke(lambda:original_up(control)or 1,False);e.reborn=True;return result
        e.up=up;e.reborn=False
        class Context:
            def __init__(self):self.dead=False;self.closed=False
            def require_original_regions(self):return {'test_only':'no native qualification'}
            def input_frame(self,_):
                f=frame();f['started']=f['finished']=c()
                a=f['actors']['vanilla']
                if not self.dead:a.update(health=100.,entity_flags=0 if scenario=='not_live'else 8,may_respawn=0)
                elif e.reborn:
                    a.update(health=100.,entity_flags=8,spawn_clock=2.,may_respawn=0)
                    if scenario=='world':f['identity']['world']='0x200000'
                    if scenario=='shooter':f['actors']['botA']['spawn_clock']=3.
                a['buttons_now']=int(e.held and scenario!='missing_down')
                return f
            def close(self):self.closed=True
        context=Context()
        with tempfile.TemporaryDirectory(prefix='respawn-window-')as td:
            w=self.m.make_window_class(legacy)(mode='control',api_root=Path(td),arena=td,evidence=td,parent_started=0.,
                frame={},records={r:{}for r in('server','vanilla','botA')},pins={},own_identity=lambda r:None,
                unit=lambda r:r,periodic=lambda:setattr(context,'dead',scenario!='no_death'),save=lambda:None,record={},
                clock=c,sleep=c.sleep,read_roles=lambda:replica(context.input_frame({})),endpoint=e,journal=j,context_factory=lambda w:context)
            if scenario!='normal':
                with self.assertRaises(ValueError):w.run()
                w.finish_before_roles();self.assertFalse(w.record.get('observation_complete',False))
                self.assertLess(c(),85.);self.assertLessEqual(e.calls.count('native-down'),1)
                self.assertEqual(e.calls.count('native-up'),e.calls.count('native-down'))
                self.assertTrue(Path(td,'respawn-native-attempts.json').exists())
                if scenario=='no_death':self.assertNotIn('native-down',e.calls)
                return
            w.run();self.assertEqual(w.record['input_emissions'],2)
            self.assertTrue(w.record['fire_program']['server_down_observed']);self.assertTrue(w.record['fire_program']['server_release_respawn_observed'])
            self.assertGreaterEqual(w.record['observed_seconds'],10.)
            self.assertFalse(w.record['first_processed_state_proven']);w.finish_before_roles()
            self.assertTrue(context.closed);w.finish_after_roles_closed(roles_closed=True)
            self.assertEqual(e.calls.count('native-down'),1);self.assertEqual(e.calls.count('native-up'),1)

    def test_actual_legacy_control_loop_new_dead_pulse_not_inputfree_pass(self):
        self.control_case()

    def test_legal_death_required_and_actual_down_or_life_drift_is_fatal(self):
        for scenario in('not_live','no_death','missing_down','world','shooter'):
            with self.subTest(scenario=scenario):self.control_case(scenario)

    def test_native_context_and_original_guard_ast_extraction_is_exact(self):
        self.assertTrue(callable(getattr(self.m,'context_sources',None)),'pinned context extraction missing')
        root=Path('/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115/method-api')
        value=self.m.context_sources(root)
        self.assertEqual(value['functions'],['NativeBindingError','require','sha','canonical','assert_identity','build_identity','NativeContext'])
        self.assertTrue(value['whole_ast_equal']);self.assertEqual(value['regions'],38)

    def test_actual_transport_always_flushes_after_native_metadata_failure(self):
        self.assertTrue(callable(getattr(self.m,'make_transport_class',None)),'normal XTest passthrough missing')
        calls=[]
        class Base:
            def __init__(self):
                self.d=99;self.guard=lambda:calls.append('guard')
                self.x=types.SimpleNamespace(XSync=lambda *a:calls.append('sync'))
                self.t=types.SimpleNamespace(XTestFakeButtonEvent=lambda *a:calls.append(('native',a))or 1)
        j=self.m.FireJournal(lambda:(_ for _ in()).throw(ValueError('counter clock')))
        t=self.m.make_transport_class(Base)(journal=j)
        with self.assertRaises(ValueError):t.event('fire',False)
        self.assertEqual(calls[-1],'sync');self.assertEqual(len([x for x in calls if isinstance(x,tuple)]),1)

    def test_invalid_clock_raw_metadata_stays_strict_json(self):
        import json
        j=self.m.FireJournal(lambda:float('nan'));calls=[]
        with self.assertRaises(ValueError):j.invoke(lambda:calls.append('down')or 1,True)
        with self.assertRaises(ValueError):j.invoke(lambda:calls.append('up')or 1,False)
        self.assertEqual(calls,['up']);json.dumps(j.attempts,allow_nan=False)

    def test_new_control_status_never_uses_old_inputfree_or_false_restore(self):
        self.assertTrue(callable(getattr(self.m,'candidate_status',None)),'separate honest condition status missing')
        attempts=[{'down':d,'accepted':True,'native_invoked':True,'return':1}for d in(True,False)]
        regions={str(i):{}for i in range(38)}
        record={'condition':'NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_COLT_V1','observation_complete':True,
          'observed_seconds':10.,'input_emissions':2,'before_roles_cleanup_complete':True,
          'after_roles_cleanup_complete':True,'worker_created':False,'native_attempts':attempts,
          'original_regions_before_preparation':regions,'original_regions_after_control':regions,
          'fire_program':{'status':'RELEASED_TRANSPORT_ONLY','server_down_observed':True,'server_release_respawn_observed':True}}
        report={'status':'CLEANUP_PENDING','errors':[],'units_closed_verified':True,
          'cleanup':{r:{'closed':True}for r in('server','vanilla','botA')},'restoration':{'restored':True},'post_close_logs':{'accepted':True}}
        w=types.SimpleNamespace(record=record,mode='control',proxy=None)
        self.assertEqual(self.m.candidate_status(report,w),'PASS_LIMITED_NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_CONTROL_ONLY')
        for field,value in [('input_emissions',0),('condition','legacy'),('native_attempt_archive_error','disk'),('worker_created',True),('original_regions_after_control',{})]:
            previous=copy.deepcopy(record);record[field]=value
            self.assertEqual(self.m.candidate_status(report,w),'FAIL');record.clear();record.update(previous)
        record['fire_program']['server_down_observed']=False
        self.assertEqual(self.m.candidate_status(report,w),'FAIL')

    def test_actual_original_replica_cannot_be_other_pid_slot_life_or_fire_state(self):
        from test_a1_original_respawn_policy import frame
        self.assertTrue(callable(getattr(self.m,'bind_replica',None)),'actual Original replica binding missing')
        f=frame();n=replica(f);self.m.bind_replica(n,f)
        for field,value in [('slot',1),('slot',True),('present',False),('entity_id',2),
                            ('spawned_tick',2.),('health',100.),('last_buttons',1),('process_identity',[88,99])]:
            bad=copy.deepcopy(n);bad['original_replica'][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.m.bind_replica(bad,f)
        with self.assertRaises(ValueError):self.m.bind_replica({},f)

    def test_explicit_namespace_and_failed_attempts_never_mutate_legacy(self):
        self.assertTrue(callable(getattr(self.m,'bind',None)),'explicit new method namespace missing')
        self.assertTrue(callable(getattr(self.m,'publish_attempts',None)),'actual failure attempts not published')
        class Base:pass
        legacy=types.SimpleNamespace(MethodWindow=Base,candidate_status='old');before=dict(vars(legacy))
        current=self.m.bind(legacy);self.assertTrue(issubclass(current.MethodWindow,Base))
        self.assertEqual(vars(legacy),before);self.assertIs(current.candidate_status,self.m.candidate_status)
        report={'input_emissions':0};w=types.SimpleNamespace(record={},journal=types.SimpleNamespace(attempts=[{'native_invoked':True,'down':True,'accepted':False}]))
        self.m.publish_attempts(report,w);self.assertEqual(report['input_emissions'],1)
        self.assertEqual(report['native_input_attempts'],w.journal.attempts)
        self.assertIsNot(report['native_input_attempts'],w.journal.attempts)
        self.assertIs(report.get('normal_route_or_fire'),True)
        self.assertIs(report.get('completed_input_program'),False)

    def test_actual_sample_fresh_but_finished_after_ack_deadline_is_fatal(self):
        from test_a1_original_respawn_policy import frame
        c=Clock();dead=frame()
        def live():
            f=frame();f['started']=f['finished']=c()
            f['actors']['vanilla'].update(health=100.,entity_flags=8,spawn_clock=2.)
            return f
        class Context:
            def input_frame(self,native):
                started=c();c.t+=.02;f=live();f['started']=started;return f
        w=object.__new__(self.m.make_window_class(types.SimpleNamespace(MethodWindow=object)))
        w.now=c;w.sleep=c.sleep;w.context=Context();w.prep_context=None;w.record={'readiness_reads':[],'fire_program':{}}
        w.read_roles=lambda:replica(live());w.original_periodic=lambda:setattr(c,'t',c()+1.99)
        w.input_deadline=20.;w.dead_pin=dead;w.down_seen=True;w.observer=None
        with self.assertRaisesRegex(ValueError,'ACK.*deadline|late.*ACK'):w._ack()
        self.assertEqual(len(w.record['readiness_reads']),1)
        self.assertLess(w.record['readiness_reads'][0]['frame']['finished']-w.record['readiness_reads'][0]['frame']['started'],.2)
        self.assertNotIn('server_release_respawn_observed',w.record['fire_program'])


if __name__=='__main__':unittest.main()
