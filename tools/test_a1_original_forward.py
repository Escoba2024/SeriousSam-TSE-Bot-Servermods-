"""Pure new translation rules. No Xlib, process or game calls."""
import copy
import importlib.util
from pathlib import Path
import unittest


def observation(t=1.,x=0.,velocity=0.,index=0):
    actors={r:dict(id=i,pointer=hex(0x10000+i*16),world='0x20000',spawn_clock=1.,health=100.,entity_flags=8,player_flags=1,may_respawn=0,buttons_now=0)for r,i in [('vanilla',5),('botA',6)]}
    frame=dict(started=t-.01,finished=t,identity=dict(server=[11,111],vanilla=[12,112],botA=[13,113],world='0x20000'),actors=actors)
    def row(role,slot):
        a=actors[role]
        return dict(present=True,slot=slot,entity_id=a['id'],entity_pointer=int(a['pointer'],16),world_pointer=0x20000,spawned_tick=1.,health=100.,last_buttons=0,placement=[x if slot==0 else 9.,0.,0.,0.,0.,0.],current_translation_absolute=[velocity,0.,0.],support_pointer=0x30000,game_tick=t,rotation_diagnostic=dict(player_flags=1,relative_view_yaw_deg=0.))
    n=dict(monotonic_started=t-.01,monotonic_finished=t,server_process_identity=[11,111],vanilla_process_identity=[12,112],roles=dict(vanilla=row('vanilla',0),botA=row('botA',1)),successful_read_sequence=dict(index=index),original_replica=row('vanilla',0))
    n['original_replica']['process_identity']=[12,112]
    return dict(native=n,context=frame)

class Rules(unittest.TestCase):
    def setUp(self):
        path=Path(__file__).with_name('a1_original_forward.py')
        if not path.exists():raise AssertionError('missing production forward admission/outcome adapter')
        spec=importlib.util.spec_from_file_location('a1_original_forward',path);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
    def checked(self):
        p=self.m.Frames();a=p.accept(observation(),1.);b=p.accept(observation(1.1,index=1),1.1);p.admit(a,b,1.1,5.);return p,b
    def test_actual_displacement_after_release(self):
        p,b=self.checked();a=p.accept(observation(1.5,x=.1,velocity=.3,index=2),1.5)
        r=p.outcome(b,a,request_finished=1.2,release_finished=1.35,now=1.5,deadline=3.2)
        self.assertEqual(r['server_displacement'],[.1,0.,0.]);self.assertFalse(r['exact_action_ack_proven'])
    def test_velocity_only_does_not_prove_translation(self):
        p,b=self.checked();a=p.accept(observation(1.5,velocity=5.,index=2),1.5)
        self.assertIsNone(p.outcome(b,a,request_finished=1.2,release_finished=1.35,now=1.5,deadline=3.2))
    def test_late_read_fails_before_accept(self):
        p,b=self.checked();a=p.accept(observation(3.19,x=.1,index=2),3.19)
        with self.assertRaisesRegex(ValueError,'ACK deadline'):p.outcome(b,a,request_finished=1.2,release_finished=1.35,now=3.21,deadline=3.2)
    def test_stale_identity_slot_and_life_fail(self):
        for change in ('stale','pid','life','slot'):
            with self.subTest(change=change):
                p,b=self.checked();a=observation(1.5,index=2)
                if change=='stale':a['context']['started']=1.
                if change=='pid':a['context']['identity']['server']=[99,999]
                if change=='life':a['context']['actors']['vanilla']['spawn_clock']=2.
                if change=='slot':a['native']['roles']['vanilla']['slot']=1
                with self.assertRaises(ValueError):p.accept(a,1.5)
    def test_read_budget_includes_initial(self):
        p=self.m.Frames()
        for i in range(16):p.accept(observation(1+i*.01,index=i),1+i*.01)
        with self.assertRaisesRegex(ValueError,'16'):p.accept(observation(2,index=16),2.)
    def test_clock_backward_and_nonfinite_fail(self):
        for field in ('native','position'):
            p,b=self.checked();a=observation(1.5,index=2)
            if field=='native':a['native']['roles']['vanilla']['game_tick']=0.
            else:a['native']['original_replica']['placement'][0]=float('nan')
            with self.assertRaises(ValueError):p.accept(a,1.5)
    def test_admission_needs_reserve_and_stationary_support(self):
        for bad in ('reserve','moving','support'):
            p=self.m.Frames();a=p.accept(observation(),1.);o=observation(1.1,index=1)
            if bad=='moving':o['native']['roles']['vanilla']['current_translation_absolute']=[.21,0.,0.]
            if bad=='support':o['native']['roles']['vanilla']['support_pointer']=0
            b=p.accept(o,1.1)
            with self.assertRaises(ValueError):p.admit(a,b,1.1,3. if bad=='reserve' else 5.)
    def test_explicit_persistent_volume_budget(self):
        self.assertTrue(hasattr(self.m,'volume_budget'),'new persistent budget missing')
        sample=dict(disk_free_bytes=self.m.DISK_MINIMUM,mem_available_bytes=self.m.MEMORY_MINIMUM)
        self.assertEqual(self.m.volume_budget(sample,False)['minimum_disk_bytes'],8816427008)
        for field in sample:
            bad=dict(sample);bad[field]-=1
            with self.assertRaises(ValueError):self.m.volume_budget(bad,False)
        with self.assertRaises(ValueError):self.m.volume_budget(sample,True)
    def test_pre_release_frame_is_not_outcome(self):
        p,b=self.checked();a=p.accept(observation(1.3,x=.1,index=2),1.3)
        self.assertIsNone(p.outcome(b,a,request_finished=1.2,release_finished=1.35,now=1.5,deadline=3.2))

if __name__=='__main__':unittest.main()
