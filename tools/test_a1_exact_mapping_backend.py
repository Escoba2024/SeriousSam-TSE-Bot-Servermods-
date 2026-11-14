"""Actual new backend method with the existing single-read file stubs."""
import ast
import copy
from pathlib import Path,PurePosixPath
from types import SimpleNamespace
import unittest


class ExactBackendTests(unittest.TestCase):
 def call(self,*,split=True,change=None,identity=True,signature=True):
  try:
   import prepare_a1_exact_mapping_coverage as builder
   from mapped_rows import canonical_mapped_rows
  except ImportError:self.fail('missing exact existing-helper backend adaptation')
  from a1_mapping_failure_receipt import mapping_mismatch
  path='/fixture/vanilla/Bin/Engine.dll';calls=[]
  expected=['1000-5000 r-xp 0 08:01 123 '+path]
  actual=['1000-2000 r-xp 0 08:01 123 '+path,'2000-5000 r-xp 1000 08:01 123 '+path]if split else list(expected)
  if change=='permission':actual[0]=actual[0].replace('r-xp','rwxp')
  if change=='offset':actual[1]=actual[1].replace(' 1000 ',' 2000 ')
  if change=='missing':actual.pop()
  if change=='invalid':actual[0]=actual[0].replace('r-xp','r-zp')
  class StubPath:
   def __init__(self,p):self.value=PurePosixPath(p)
   def __str__(self):return str(self.value)
   def __truediv__(self,p):return StubPath(self.value/str(p))
   def __eq__(self,p):return isinstance(p,StubPath)and self.value==p.value
   def resolve(self,strict=False):return self
   def stat(self):
    calls.append('stat')
    return SimpleNamespace(st_dev=1,st_ino=123,st_size=4096,st_mtime_ns=4,st_ctime_ns=5 if signature else 6)
   def read_text(self):
    calls.append(('read',str(self)))
    if str(self)!='/proc/321/maps':raise AssertionError('additional process read')
    return '\n'.join(actual)
  def same(value):calls.append(('identity',value));return identity
  pins={'Engine.dll':dict(signature=(1,123,4096,4,5),mapped_rows=expected,sha256='a'*64,base=0x1000)}
  saved=copy.deepcopy(pins)
  source=builder.transform_backend((builder.PARENT/'strict_backend.py').read_text())
  method=next(n for n in ast.walk(ast.parse(source))if isinstance(n,ast.FunctionDef)and n.name=='verify_modules')
  env=dict(Path=StubPath,canonical_mapped_rows=canonical_mapped_rows,mapping_mismatch=mapping_mismatch)
  exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),'actual-existing-read-backend','exec'),env)
  error=None
  try:env['verify_modules'](SimpleNamespace(root=StubPath('/fixture'),same=same),'vanilla',(321,654),pins)
  except BaseException as err:error=err
  self.assertEqual(pins,saved,'original pins mutated/rebased')
  return calls,error,expected,actual

 def test_actual_backend_accepts_only_partition_change_with_unchanged_reads_and_pins(self):
  for split in(False,True):
   calls,error,_,_=self.call(split=split);self.assertIsNone(error)
   self.assertEqual(calls,[('identity',(321,654)),('read','/proc/321/maps'),'stat'])

 def test_actual_backend_retains_failure_receipt_for_every_real_or_invalid_change(self):
  for change in('permission','offset','missing','invalid'):
   with self.subTest(change=change):
    calls,error,expected,actual=self.call(change=change)
    self.assertIsInstance(error,AssertionError)
    self.assertEqual(error.module_mapping_failure['expected_mapped_rows'],expected)
    self.assertEqual(error.module_mapping_failure['actual_mapped_rows'],actual)
    self.assertFalse(error.module_mapping_failure['accepted_new_mapping'])
    self.assertEqual(calls,[('identity',(321,654)),('read','/proc/321/maps'),'stat'])

 def test_pid_and_signature_guards_fail_without_reclassification_or_extra_reads(self):
  for options in(dict(identity=False),dict(signature=False)):
   with self.subTest(options=options):
    calls,error,_,_=self.call(**options);self.assertIsInstance(error,AssertionError)
    self.assertFalse(hasattr(error,'module_mapping_failure'))
    self.assertEqual(calls,[('identity',(321,654))]if options.get('identity')is False else[('identity',(321,654)),('read','/proc/321/maps'),'stat'])


if __name__=='__main__':unittest.main()
