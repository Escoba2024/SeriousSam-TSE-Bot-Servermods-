"""Actual transformed verifier/handler under file-read stubs; no native access."""
import ast
import json
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
import tempfile
import unittest


PARENT=Path('/srv/tse-a1-instruction-probe-root-frozen-20261114')


class MappingReceiptTests(unittest.TestCase):
 def verifier(self,*,different=False,signature_bad=False,identity_bad=False):
  import prepare_a1_mapping_failure_receipt as builder
  import a1_mapping_failure_receipt as receipt
  calls=[];path='/fixture/vanilla/Bin/Engine.dll'
  expected=['60000000-60001000 r-xp 00000000 08:01 123 '+path]
  actual=[expected[0].replace('r-xp','rwxp')]if different else list(expected)
  class FakePath:
   def __init__(self,value):self.value=PurePosixPath(value)
   def __truediv__(self,part):return FakePath(self.value/str(part))
   def __str__(self):return str(self.value)
   def __eq__(self,other):return isinstance(other,FakePath)and self.value==other.value
   def resolve(self,strict=False):return self
   def stat(self):
    calls.append(('stat',str(self)))
    return SimpleNamespace(st_dev=1,st_ino=123,st_size=4096,st_mtime_ns=4,st_ctime_ns=6 if signature_bad else 5)
   def read_text(self):
    calls.append(('read',str(self)))
    if str(self)!='/proc/321/maps':raise AssertionError('new read outside existing maps')
    return '\n'.join(actual+['70000000-70001000 r--p 00000000 08:01 999 /unrelated'])+'\n'
  source=builder.transform_backend((PARENT/'strict_backend.py').read_text())
  tree=ast.parse(source);method=next(n for c in tree.body if isinstance(c,ast.ClassDef)for n in c.body if isinstance(n,ast.FunctionDef)and n.name=='verify_modules')
  scope=dict(Path=FakePath,mapping_mismatch=receipt.mapping_mismatch)
  exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),'actual-verify','exec'),scope)
  self.backend=SimpleNamespace(root=FakePath('/fixture'),same=lambda identity:not identity_bad)
  self.call=lambda:scope['verify_modules'](self.backend,'vanilla',(321,654),{'Engine.dll':dict(signature=(1,123,4096,4,5),mapped_rows=expected,base=0x60000000,sha256='a'*64)})
  return calls,expected,actual

 def identity_handler(self,error,evidence):
  import prepare_a1_mapping_failure_receipt as builder
  from a1_mapping_failure_receipt import preserve_mapping_failure
  source=builder.transform_runner((PARENT/'run_dual.py').read_text())
  tree=ast.parse(source);method=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='own_identity')
  def fail(*args):raise error
  scope=dict(records={'vanilla':{'identity':[321,654]}},pins={'vanilla':{}},B=SimpleNamespace(identity=lambda *a:(321,654),verify_modules=fail),unit=lambda role:'owned-unit',E=evidence,preserve_mapping_failure=preserve_mapping_failure)
  exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),'actual-own-identity','exec'),scope)
  return lambda:scope['own_identity']('vanilla')

 def test_equal_rows_keep_success_and_exact_existing_read_count(self):
  calls,_,_=self.verifier();self.assertIsNone(self.call())
  self.assertEqual(calls,[('read','/proc/321/maps'),('stat','/fixture/vanilla/Bin/Engine.dll')])

 def test_unequal_rows_still_fail_and_handler_persists_same_read_values(self):
  calls,expected,actual=self.verifier(different=True)
  with self.assertRaises(AssertionError)as caught:self.call()
  error=caught.exception;detail=error.module_mapping_failure
  self.assertEqual(detail['expected_mapped_rows'],expected);self.assertEqual(detail['actual_mapped_rows'],actual)
  self.assertEqual(detail['process_identity'],[321,654]);self.assertEqual(detail['role'],'vanilla')
  self.assertEqual(detail['module'],'Engine.dll');self.assertEqual(detail['module_path'],'/fixture/vanilla/Bin/Engine.dll')
  self.assertEqual(detail['observed_signature'],[1,123,4096,4,5]);self.assertEqual(detail['expected_signature'],detail['observed_signature'])
  self.assertEqual(calls,[('read','/proc/321/maps'),('stat','/fixture/vanilla/Bin/Engine.dll')])
  with tempfile.TemporaryDirectory()as directory:
   with self.assertRaises(AssertionError)as forwarded:self.identity_handler(error,Path(directory))()
   self.assertIs(forwarded.exception,error)
   file=Path(directory)/'module-mapping-failure.json'
   self.assertEqual(json.loads(file.read_text()),detail);self.assertEqual(file.stat().st_mode&0o777,0o600)

 def test_identity_and_signature_failures_are_not_reclassified(self):
  for options in (dict(identity_bad=True),dict(signature_bad=True)):
   with self.subTest(options=options):
    self.verifier(**options)
    with self.assertRaises(AssertionError)as caught:self.call()
    self.assertFalse(hasattr(caught.exception,'module_mapping_failure'))
    with tempfile.TemporaryDirectory()as directory:
     with self.assertRaises(AssertionError)as forwarded:self.identity_handler(caught.exception,Path(directory))()
     self.assertIs(forwarded.exception,caught.exception);self.assertEqual(list(Path(directory).iterdir()),[])

 def test_receipt_write_error_stays_failure_and_original_cause_survives(self):
  self.verifier(different=True)
  with self.assertRaises(AssertionError)as caught:self.call()
  with tempfile.TemporaryDirectory()as directory:
   with self.assertRaises(OSError)as failed:self.identity_handler(caught.exception,Path(directory)/'absent')()
   self.assertIs(failed.exception.__context__,caught.exception)

 def test_existing_receipt_is_never_overwritten(self):
  from a1_mapping_failure_receipt import preserve_mapping_failure
  self.verifier(different=True)
  with self.assertRaises(AssertionError)as caught:self.call()
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'module-mapping-failure.json';path.write_text('retained')
   with self.assertRaises(FileExistsError):preserve_mapping_failure(caught.exception,path)
   self.assertEqual(path.read_text(),'retained')


if __name__=='__main__':unittest.main()
