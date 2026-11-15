"""Real archived snapshot function with a fake byte reader; no process access."""
import ast
import hashlib
import importlib.util
import math
import os
from pathlib import Path
import struct
import unittest

PARENT=Path('/srv/tse-a1-first-state-qjs10-v2-root-frozen-20261115/tools/retail_inventory_readonly.py')
SHA='b5627e91094594d0e1a0fae52ef8dc36be33f416436b92d0286396d37b31463a'


def read(path):
 with os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'r')as f:return f.read()


def source():
 text=read(PARENT)
 if hashlib.sha256(text.encode()).hexdigest()!=SHA:raise AssertionError('exact active reader fixture required')
 return text


def transformed(text):
 # Before production helper exists this executes the actual old snapshot branch.
 if importlib.util.find_spec('retail_inventory_animator_context_patch')is None:return text
 from retail_inventory_animator_context_patch import transform
 return transform(text)


def namespace(text):
 tree=ast.parse(text);names={'EvidenceError','require','unpack','snapshot'}
 nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names]
 if len(nodes)!=4:raise AssertionError('exact production snapshot and error helpers')
 ns={'struct':struct,'math':math};exec(compile(ast.Module(body=nodes,type_ignores=[]),'actual-inventory-snapshot','exec'),ns);return ns


class Memory:
 engine=0x100000;entities=0x200000;network=0x300000;session=0x310000;table=0x320000
 entity=0x330000;world=0x340000;animator=0x350000;slot=4;entity_id=321;tick=12.5
 def __init__(self,animator=None):
  self.data={};self.calls=[];self.read_count={};self.short=None;self.tear=False
  self.put(self.engine+0x20d6a4,'I',self.network);self.put(self.network+0x20,'I',self.session)
  self.put(self.session+4,'I',self.table);self.put(self.session+0x4c,'f',self.tick)
  self.put(self.table+136*self.slot,'II',1,self.entity);self.put(self.entity+4,'II',3,0)
  self.put(self.entity+0x1c,'I',self.entity_id);self.put(self.entity+0x8c,'I',self.world)
  self.put(self.entity+0xcc,'f',100);self.put(self.entity+0xc14,'f',2.5)
  self.put(self.entity+0x388,'I',self.animator if animator is None else animator)
  self.put(self.animator+0x1c,'I',654);self.put(self.animator+0x8c,'I',self.world)
  self.put(self.animator+0xec,'I',self.entity)
 def put(self,address,fmt,*values):
  for i,value in enumerate(struct.pack('<'+fmt,*values)):self.data[address+i]=value
 def read(self,address,size):
  self.calls.append((address,size));self.read_count[address]=self.read_count.get(address,0)+1
  if self.short==address:return b''
  if self.tear and address==self.entity+0xcc and self.read_count[address]>1:return struct.pack('<f',99)
  return bytes(self.data.get(address+i,0)for i in range(size))


def sample(ns,memory):
 return ns['snapshot'](memory.read,memory.engine,(4,5,6,7),rotation_diagnostics=True,colt_preparation=True,entities_base=memory.entities)


class AnimatorContext(unittest.TestCase):
 def test_actual_invalid_branch_reports_exact_sampled_values_without_extra_read(self):
  old=namespace(source());new=namespace(transformed(source()))
  for value in (0,1,0xfffc,0x10001,0xffffffff):
   with self.subTest(animator=value):
    before,after=Memory(value),Memory(value)
    with self.assertRaises(old['EvidenceError'])as original:sample(old,before)
    with self.assertRaises(new['EvidenceError'])as changed:sample(new,after)
    self.assertEqual(str(original.exception),'invalid animator pointer')
    self.assertEqual(str(changed.exception),f'invalid animator pointer animator=0x{value:08x} slot=4 entity=0x00330000 entity_id=321 world=0x00340000 snapshot_tick=12.5')
    self.assertEqual(after.calls,before.calls)
    self.assertEqual(after.read_count[after.entity+0x388],1)
    self.assertEqual(type(original.exception).__name__,type(changed.exception).__name__)

 def test_valid_snapshot_and_two_pass_read_trace_unchanged(self):
  a,b=Memory(),Memory();old=namespace(source());new=namespace(transformed(source()))
  self.assertEqual(sample(old,a),sample(new,b));self.assertEqual(a.calls,b.calls)
  self.assertEqual(b.read_count[b.entity+0x388],2)

 def test_remaining_errors_and_read_traces_unchanged(self):
  old=namespace(source());new=namespace(transformed(source()))
  def support(m):m.put(m.entity+0x11c,'I',0x10001)
  def deleted(m):m.put(m.entity+0x10,'I',4)
  def owner(m):m.put(m.animator+0xec,'I',m.entity+4)
  def world(m):m.put(m.animator+0x8c,'I',m.world+4)
  def bounds(m):m.put(m.entity+0x388,'I',0xfffffffc)
  def short(m):m.short=m.entity+0x388
  def tear(m):m.tear=True
  def nonfinite(m):m.put(m.session+0x4c,'f',float('nan'))
  for mutate,message in ((support,'invalid support pointer'),(deleted,'deleted player'),(owner,'animator owner/world/deletion mismatch'),(world,'animator owner/world/deletion mismatch'),(bounds,'bad read bounds'),(short,'short read'),(tear,'state changed during read'),(nonfinite,'nonfinite state')):
   with self.subTest(error=message):
    a,b=Memory(),Memory();mutate(a);mutate(b)
    with self.assertRaises(old['EvidenceError'])as x:sample(old,a)
    with self.assertRaises(new['EvidenceError'])as y:sample(new,b)
    self.assertEqual(str(x.exception),message);self.assertEqual(str(y.exception),message);self.assertEqual(a.calls,b.calls)

 def test_entire_source_inverse_guard_ast_and_foreign_mutations(self):
  from retail_inventory_animator_context_patch import transform,reverse
  old=source();new=transform(old);self.assertEqual(reverse(new),old)
  def guard(text):
   return next(n for n in ast.walk(ast.parse(text))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='require'and any(isinstance(c,ast.Name)and c.id=='animator'for c in ast.walk(n.args[0])))
  a,b=guard(old),guard(new);self.assertEqual(ast.dump(a.args[0]),ast.dump(b.args[0]));self.assertEqual(len(a.args),len(b.args))
  for variant in (old+'\n',old.replace('animator >= 0x10000','animator >= 0'),new):
   with self.assertRaises(ValueError):transform(variant)
  for variant in (new+'\n',new.replace('animator >= 0x10000','animator >= 0')):
   with self.assertRaises(ValueError):reverse(variant)
  with self.assertRaises(ValueError):transform(read(PARENT.parents[1]/'method-api/vendor/colt/tools/retail_inventory_readonly.py'))


if __name__=='__main__':unittest.main()
