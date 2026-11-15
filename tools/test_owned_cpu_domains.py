"""Bounded FakeFS only: no real /proc, cgroup, thread, child or Frida."""
import importlib.util
import json
from pathlib import Path
import types
import unittest

TOOL=Path(__file__).with_name('owned_cpu_domains.py')
PROC='/proc/123/stat';GROUP='/sys/fs/cgroup/system.slice/own.service'

def proc(utime=10,stime=5,start=77,pid=123):
    fields=['S']+['0']*19
    fields[11:15]=[str(utime),str(stime),'9000000','8000000'];fields[19]=str(start)
    return str(pid)+' (name ) with spaces) '+' '.join(fields)+'\n'
class FS:
    def __init__(self,reads=None,inodes=None):
        self.reads=reads or{PROC:[proc(),proc(11)],GROUP+'/cpu.stat':['usage_usec 250000\nuser_usec 200000\n']}
        self.inodes=inodes or[(1,9),(1,9)];self.calls=[]
    def read(self,p):
        self.calls.append(('read',str(p)));v=self.reads[str(p)];v=v.pop(0)if isinstance(v,list)else v
        if isinstance(v,BaseException):raise v
        return v
    def stat(self,p):
        self.calls.append(('stat',str(p)));v=self.inodes.pop(0)
        if isinstance(v,BaseException):raise v
        return types.SimpleNamespace(st_dev=v[0],st_ino=v[1])

class OwnCPU(unittest.TestCase):
    def setUp(self):
        self.assertTrue(TOOL.is_file(),'passive CPU source-only API not implemented')
        spec=importlib.util.spec_from_file_location('own_cpu',TOOL);self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
    def sample(self,fs=None,times=(1.,1.1),epoch='run',**kwargs):
        fs=FS()if fs is None else fs;clock=iter(times)
        return self.m.sample(epoch,{'server':(123,77)},{'unit':GROUP},100,read=fs.read,stat=fs.stat,clock=lambda:next(clock),**kwargs)
    def test_valid_ranges_separate_domains_no_child_times_or_total(self):
        fs=FS();a=self.sample(fs);b=self.sample(FS({PROC:[proc(20,7),proc(21,8)],GROUP+'/cpu.stat':['usage_usec 750000\n']}),times=(2.,2.1))
        self.assertEqual(a['status'],'VALID');self.assertEqual(a['processes']['server']['counter'],16)
        d=self.m.delta(a,b);p=d['processes']['server'];g=d['cgroups']['unit']
        self.assertAlmostEqual(p['cpu_seconds'],.13);self.assertAlmostEqual(g['cpu_seconds'],.5)
        self.assertAlmostEqual(d['elapsed_range'][0],.9);self.assertAlmostEqual(d['elapsed_range'][1],1.1)
        self.assertAlmostEqual(p['core_equivalent_range'][0],.13/1.1);self.assertAlmostEqual(p['core_equivalent_range'][1],.13/.9)
        self.assertNotIn('total',d);self.assertNotIn('host_cpu_percent',d)
        self.assertEqual(fs.calls,[('read',PROC),('read',PROC),('stat',GROUP),('read',GROUP+'/cpu.stat'),('stat',GROUP)])
    def test_pid_reuse_wrong_pid_and_missing_end_are_unknown_never_zero(self):
        good=self.sample()
        for end in(proc(start=78),proc(pid=124),FileNotFoundError('gone')):
            with self.subTest(end=str(end)):
                bad=self.sample(FS({PROC:[proc(),end],GROUP+'/cpu.stat':['usage_usec 5\n']}),times=(2.,2.1))
                r=bad['processes']['server'];self.assertEqual(r['status'],'UNKNOWN');self.assertNotIn('counter',r)
                delta=self.m.delta(good,bad)['processes']['server'];self.assertEqual(delta['status'],'UNKNOWN');self.assertNotIn('cpu_seconds',delta)
                self.assertTrue(r['raw']);json.dumps(bad,allow_nan=False)
    def test_cgroup_recreated_within_or_across_samples_and_missing_end(self):
        a=self.sample()
        for fs in(FS(inodes=[(1,9),(1,10)]),FS(inodes=[(1,10),(1,10)]),FS(inodes=[(1,9),FileNotFoundError('gone')])):
            with self.subTest():
                b=self.sample(fs,times=(2.,2.1));d=self.m.delta(a,b)['cgroups']['unit']
                self.assertEqual(d['status'],'UNKNOWN');self.assertNotIn('cpu_seconds',d)
                self.assertEqual(self.m.delta(a,b)['processes']['server']['status'],'VALID')
    def test_time_epoch_hz_and_counter_regression_no_fallback(self):
        a=self.sample()
        for times in((float('nan'),2.),(2.,float('inf')),(2.,1.)):
            with self.subTest(times=times):
                bad=self.sample(times=times);self.assertEqual(bad['status'],'UNKNOWN');json.dumps(bad,allow_nan=False)
                self.assertEqual(self.m.delta(a,bad)['status'],'UNKNOWN')
        for b in(self.sample(times=(1.05,1.15)),self.sample(times=(2.,2.1),epoch='other'),self.sample(FS({PROC:[proc(1,1),proc(1,1)],GROUP+'/cpu.stat':['usage_usec 1\n']}),times=(2.,2.1))):
            with self.subTest():self.assertEqual(self.m.delta(a,b)['status'],'UNKNOWN')
        b=self.sample(times=(2.,2.1));b['clock_hz']=200;self.assertEqual(self.m.delta(a,b)['status'],'UNKNOWN')
    def test_malformed_and_read_errors_archivable_with_raw(self):
        for data in(proc(-1),proc().replace(' 77\n',' 0\n'),'short',OSError(5,'EIO'), 'x'*16385):
            with self.subTest(data=str(data)[:60]):
                fs=FS({PROC:[data,proc()],GROUP+'/cpu.stat':['usage_usec 2\nusage_usec 3\n']})
                row=self.sample(fs);self.assertEqual(row['processes']['server']['status'],'UNKNOWN');self.assertEqual(row['cgroups']['unit']['status'],'UNKNOWN')
                self.assertTrue(row['errors']);json.dumps(row,allow_nan=False)
    def test_cgroup_identity_types_and_ranges_are_failclosed(self):
        for identity in [(None,9),(True,9),(-1,9),(2**64,9),(1,None),(1,True),(1,0),(1,-9),(1,2**64)]:
            with self.subTest(identity=identity):
                row=self.sample(FS(inodes=[identity,identity]))
                self.assertEqual(row['cgroups']['unit']['status'],'UNKNOWN')
                self.assertNotIn('counter',row['cgroups']['unit'])
                self.assertEqual(row['processes']['server']['status'],'VALID')

    def test_invalid_caller_sources_do_not_read_or_discover(self):
        for processes,groups,hz in [({'x':(True,77)},{'g':GROUP},100),({'x':(123,0)},{'g':GROUP},100),({'x':(123,77)},{'g':'/other/path'},100),({'x':(123,77)},{'g':GROUP+'/../other'},100),({'x':(123,77)},{'g':GROUP},0)]:
            fs=FS()
            with self.subTest(),self.assertRaises(ValueError):self.m.sample('run',processes,groups,hz,read=fs.read,stat=fs.stat,clock=lambda:1.)
            self.assertEqual(fs.calls,[])

if __name__=='__main__':unittest.main()
