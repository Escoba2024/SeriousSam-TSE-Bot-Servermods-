"""Focused offline policy/adapter tests; no process or game launch."""
import ast
import copy
import importlib.util
import os
from pathlib import Path
import struct
import sys
import tempfile
import types
import unittest

import a4_hard_map_policy as hardmap

class HardMapTests(unittest.TestCase):
 def setUp(self):
  self.mapping=dict(botA=[0,1,2,3],botB=[4,5,6,7],vanilla=[8])
  self.rows=[dict(slot=i,present=True,entity_id=100+i,entity_pointer=65536+i*4096,world_pointer=999999)for i in range(9)]
 def test_fixed_options(self):
  hardmap.options('redstation',600,0,{'redstation':{}})
  for args in [('redstation',120,0),('redstation',600,1),('unknown',600,0),('redstation',float('nan'),0)]:
   with self.assertRaises(ValueError):hardmap.options(*args,{'redstation':{}})
 def test_registry_reuses_current_nine_tuple_and_binds_epoch(self):
  def original(phase,rows):return dict(phase=phase,players=copy.deepcopy(rows),qualification=False)
  r=hardmap.registry(original,self.rows,self.mapping,[17,91])
  self.assertEqual(r['phase'],0);self.assertEqual(r['actual_slot_mapping'],self.mapping)
  self.assertEqual(r['native_fire_epoch'],dict(phase=0,server_identity=[17,91],log_offsets=dict(server=0,botA=0,botB=0)))
  self.rows[0]['entity_id']=77;self.assertEqual(r['players'][0]['entity_id'],100)
 def test_registry_rejects_wrong_mapping_and_missing_native_binding(self):
  def original(phase,rows):return dict(phase=phase,players=copy.deepcopy(rows))
  for mutation in ['overlap','entity','world','missing','pointer']:
   rows=copy.deepcopy(self.rows);mapping=copy.deepcopy(self.mapping)
   if mutation=='overlap':mapping['botB'][0]=0
   if mutation=='entity':rows[1]['entity_id']=rows[0]['entity_id']
   if mutation=='world':rows[1]['world_pointer']+=4
   if mutation=='missing':rows.pop()
   if mutation=='pointer':rows[1]['entity_pointer']=rows[0]['entity_pointer']
   with self.assertRaises(ValueError):hardmap.registry(original,rows,mapping,[17,91])
 def test_bound_session_rejects_wrong_rules_and_missing_bytes(self):
  import stability_hard_rules as rules
  raw=bytearray(156)
  for key,(fmt,offset)in rules.FIELDS.items():struct.pack_into(fmt,raw,offset,rules.EXPECTED[key])
  self.assertTrue(rules.validate_session(dict(session156_hex=raw.hex())))
  struct.pack_into('<i',raw,0x1c,3)
  with self.assertRaises(ValueError):rules.validate_session(dict(session156_hex=raw.hex()))
  with self.assertRaises(ValueError):rules.validate_session({})
  with self.assertRaises(ValueError):rules.validate_query(dict(difficulty='Serious'))

 def test_startup_transport_timeout_is_not_a_difficulty_verdict(self):
  import stability_hard_rules as rules
  self.assertFalse(hardmap.startup_count({},0,rules.validate_query))
  self.assertTrue(hardmap.startup_count(dict(difficulty='Hard',numplayers='0'),0,rules.validate_query))
  self.assertFalse(hardmap.startup_count(dict(difficulty='Hard',numplayers='1'),0,rules.validate_query))
 def test_startup_valid_wrong_or_missing_difficulty_never_becomes_ready(self):
  import stability_hard_rules as rules
  for query in [dict(difficulty='Serious',numplayers='0'),dict(numplayers='0'),dict(difficulty='Hard',numplayers='0x0')]:
   if query.get('difficulty')=='Hard':self.assertFalse(hardmap.startup_count(query,0,rules.validate_query))
   else:
    with self.assertRaises(ValueError):hardmap.startup_count(query,0,rules.validate_query)
  for query in [None,[],False]:
   with self.assertRaises(ValueError):hardmap.startup_count(query,0,rules.validate_query)

@unittest.skipUnless(os.environ.get('TSE_HARD_MAP_PACKAGE'),'explicit disabled package required')
class AdapterTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.root=Path(os.environ['TSE_HARD_MAP_PACKAGE']);cls.source=(cls.root/'run-a4.py').read_text()
 def function(self,name):
  node=next(n for n in ast.walk(ast.parse(self.source))if isinstance(n,ast.FunctionDef)and n.name==name)
  return ast.get_source_segment(self.source,node)
 def test_no_frida_and_disabled_fixed_protocol(self):
  self.assertIn('RUNTIME_REVIEWED=False',self.source);self.assertNotIn('frida',self.source.lower())
  self.assertIn('hardmap.options(map_key,duration,diag',self.source)
  self.assertIn('default=600',self.source)
 def test_reader_calls_rates_and_host_transaction_unchanged(self):
  parent=Path('/srv/tse-combat-a4-build013-preflight-draft-20261112/run-a4.py').read_text()
  def calls(s):
   return sorted(ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(s))if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and(n.func.value.id,n.func.attr)in{('probe','read'),('inventory','sample'),('time','sleep')})
  self.assertEqual(calls(parent),calls(self.source))
  self.assertIn('gam_iStartDifficulty=2;',self.source)
  self.assertLess(self.source.index('transaction.seal()'),self.source.index('gam_iStartDifficulty=2;'))
 def test_partialstart_uses_only_strict_ready_identity(self):
  code=self.function('close');events=[];record=dict(identity=None,closed=False)
  identity=(17,91)
  b=types.SimpleNamespace(ready=lambda role,unit:True,identity=lambda role,unit:identity,same=lambda identity:False,empty=lambda unit:True,wait=lambda predicate,timeout,msg:self.assertTrue(predicate()),scope={'close_window':lambda pid,display:events.append(('close',pid))or 1})
  env=dict(records={'botA':record},B=b,unit=lambda r:r,DISPLAY=':154',emit=lambda *a,**k:None,signal=types.SimpleNamespace(SIGINT=2),os=types.SimpleNamespace(kill=lambda *a:events.append(('kill',a))))
  exec(code,env);env['close']('botA');self.assertTrue(record['closed']);self.assertEqual(events,[('close',17)])
  record.update(identity=None,closed=False);b.ready=lambda *a:False;events.clear()
  with self.assertRaises(AssertionError):env['close']('botA')
  self.assertEqual(events,[])
 def test_existing_native_reads_are_each_hard_checked(self):
  self.assertEqual(self.source.count('hard_rules.validate_session('),4)
  self.assertEqual(self.source.count('hard_rules.validate_query('),2)
  code=self.function('joined_entities_frozen')
  class Rules:
   def validate_session(self,snapshot):
    if snapshot.get('difficulty')!=2:raise ValueError('wrong actual Hard')
  env=dict(records={'server':{'identity':[17,91]}},probe=types.SimpleNamespace(read=lambda *args:{'difficulty':3}),R=self.root,hard_rules=Rules())
  exec(code,env)
  with self.assertRaises(ValueError):env['joined_entities_frozen']()
 def test_partialstart_never_closes_changed_identity(self):
  identity=[17,91];record=dict(identity=identity,closed=False);events=[]
  b=types.SimpleNamespace(identity=lambda *args:[18,92],scope={'close_window':lambda *args:events.append('BAD')})
  env=dict(records={'botA':record},B=b,unit=lambda r:r,DISPLAY=':154')
  exec(self.function('close'),env)
  with self.assertRaises(AssertionError):env['close']('botA')
  self.assertEqual(events,[])
 def test_fire_wrapper_is_authoritative_and_registry_required(self):
  self.assertIn('native_fire.apply(',self.source);self.assertIn('hardmap.registry(',self.source)
  self.assertIn('native_fire.bind_sample(sampled,0,server,log_offsets)',self.source)
  self.assertIn("assert native_registry is not None",self.source)

 def test_startup_archives_empty_then_hard_without_accepting_wrong_status(self):
  import json
  import stability_hard_rules as rules
  with tempfile.TemporaryDirectory()as td:
   replies=iter([{},dict(difficulty='Hard',numplayers='0')]);observed=[]
   def wait(predicate,seconds,message):
    for unused in range(2):
     value=predicate();observed.append(value)
     if value:return
    raise AssertionError('not ready')
   env=dict(B=types.SimpleNamespace(query=lambda pid:next(replies),wait=wait),server=[17,91],E=Path(td),json=json,time=types.SimpleNamespace(monotonic=lambda:123),hardmap=hardmap,hard_rules=rules)
   exec(self.function('count'),env);env['count'](0)
   self.assertEqual(observed,[False,True])
   packets=[json.loads(l)for l in(Path(td)/'startup-query-attempts.jsonl').read_text().splitlines()]
   self.assertEqual([p['query']for p in packets],[{},dict(difficulty='Hard',numplayers='0')])
   env['B'].query=lambda pid:dict(difficulty='Serious',numplayers='0')
   with self.assertRaises(ValueError):env['count'](0)
   self.assertEqual(json.loads((Path(td)/'startup-query-attempts.jsonl').read_text().splitlines()[-1])['query']['difficulty'],'Serious')

if __name__=='__main__':unittest.main()
