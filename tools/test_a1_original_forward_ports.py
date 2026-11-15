"""Actual new production ports with C-call-shaped fakes; no Xlib loading."""
import ctypes
import importlib.util
from pathlib import Path
import sys
import unittest
import a1_original_forward as F

PARENT=Path('/srv/tse-a1-original-colt-trouble030-v3-disabled-20261115')
def rp():
    old=list(sys.path);sys.path.insert(0,str(PARENT))
    try:
        s=importlib.util.spec_from_file_location('rp_forward_fixture',PARENT/'a1_colt_trouble_method.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    finally:sys.path[:]=old

class Port:
    def __init__(self,pin=None,guard=lambda:None):
        self.guard=guard;self.d=1;self.c=ctypes;self.keys={'forward':25};self.bits=bytearray(32);self.calls=[];self.syncs=0
        self.x=self;self.t=self
    def XTestFakeKeyEvent(self,d,key,down,delay):
        self.calls.append(down)
        if down:self.bits[key//8]|=1<<(key%8)
        else:self.bits[key//8]&=~(1<<(key%8))
        return 1
    def XSync(self,*args):self.syncs+=1
    def XQueryKeymap(self,d,array):
        for i,b in enumerate(self.bits):array[i]=bytes([b])
        return 1

class Endpoint:
    def __init__(self,t):self.transport=t;self.releases=0
    def verify(self):pass
    def check_focus(self):pass
    def neutral(self,controls):pass
    def down(self,control,submit=None):return self.transport.event(control,True,submit=submit)
    def up(self,control):self.releases+=1;return self.transport.event(control,False)
    def released(self,c):
        if any(self.transport.bits):raise ValueError('held')

class Ports(unittest.TestCase):
    def test_production_forward_symbols_exist(self):
        self.assertTrue(hasattr(F,'forward_pulse'),'new production pulse is missing')
        self.assertTrue(hasattr(F,'make_transport_class'),'normal Key transport adapter missing')
    def setup_port(self,clock):
        self.assertTrue(hasattr(F,'make_transport_class'),'normal Key transport adapter missing')
        j=rp().FireJournal(clock);T=F.make_transport_class(Port);t=T(journal=j);return j,t,Endpoint(t)
    def test_one_keydown_up_and_flush(self):
        state=[1.]
        def sleep(v):state[0]+=v
        j,t,e=self.setup_port(lambda:state[0]);r={}
        F.forward_pulse(e,clock=lambda:state[0],sleep=sleep,before_press=lambda:None,observe=lambda:None,deadline=5.,receipt=r)
        self.assertEqual(t.calls,[1,0]);self.assertEqual(t.syncs,2);self.assertEqual(e.releases,1);self.assertFalse(any(t.bits));self.assertEqual(len(j.attempts),2)
    def test_actual_down_then_metadata_error_still_up_flush_and_neutral(self):
        state=[1.];j,t,e=self.setup_port(lambda:float('nan')if state[0]<0 else state[0]);original=t.XTestFakeKeyEvent
        def call(*args):
            result=original(*args)
            if args[2]:state[0]=-1.
            return result
        t.XTestFakeKeyEvent=call;r={}
        with self.assertRaises(ValueError):F.forward_pulse(e,clock=lambda:1.,sleep=lambda _:None,before_press=lambda:None,observe=lambda:None,deadline=5.,receipt=r)
        self.assertEqual(t.calls,[1,0]);self.assertEqual(t.syncs,2);self.assertEqual(e.releases,1);self.assertFalse(any(t.bits));self.assertTrue(j.failed);self.assertEqual(r['status'],'FAIL')
    def test_actual_endpoint_preserves_down_and_neutral_keymaps(self):
        self.assertTrue(hasattr(F,'make_endpoint_class'),'keymap-preserving endpoint missing')
        j,t,e=self.setup_port(lambda:1.)
        class Base:
            def __init__(self):self.transport=t
            def down(self,c,submit=None):return t.event(c,True,submit=submit)
            def up(self,c):return t.event(c,False)
            def released(self,c):
                if any(t.bits):raise ValueError('held')
        endpoint=F.make_endpoint_class(Base)();endpoint.down('forward');endpoint.up('forward');endpoint.released('forward')
        self.assertEqual([r['down']for r in j.keymaps],[True,False]);self.assertEqual(j.keymaps[-1]['bitmap_hex'],'00'*32)
    def test_no_press_without_reserve(self):
        j,t,e=self.setup_port(lambda:1.);r={}
        with self.assertRaises(ValueError):F.forward_pulse(e,clock=lambda:1.,sleep=lambda _:None,before_press=lambda:None,observe=lambda:None,deadline=3.,receipt=r)
        self.assertEqual(t.calls,[])
    def test_other_key_denied(self):
        j,t,e=self.setup_port(lambda:1.)
        with self.assertRaises(ValueError):t.event('backward',True)
        self.assertEqual(t.calls,[])
    def test_failed_up_keeps_failure_and_neutrality_attempt(self):
        state=[1.];j,t,e=self.setup_port(lambda:state[0]);original=t.XTestFakeKeyEvent
        def call(*args):
            result=original(*args)
            if not args[2]:raise ValueError('actual up returned error')
            return result
        t.XTestFakeKeyEvent=call;r={}
        with self.assertRaisesRegex(ValueError,'actual up'):F.forward_pulse(e,clock=lambda:state[0],sleep=lambda v:state.__setitem__(0,state[0]+v),before_press=lambda:None,observe=lambda:None,deadline=5.,receipt=r)
        self.assertEqual(t.calls,[1,0]);self.assertEqual(t.syncs,2);self.assertFalse(any(t.bits));self.assertEqual(r['status'],'FAIL')

if __name__=='__main__':unittest.main()
