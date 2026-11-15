"""Pure bounded Source grammar only; no evidence/runtime imports."""
import ast,importlib.util,re,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent

def parse(line):
 p=HERE/'transit_history_custody_audit.py'
 if p.exists():
  spec=importlib.util.spec_from_file_location('history_new',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m.parse(line)
 # Actual old lexical reader silently retains strings and last duplicate value.
 tree=ast.parse((HERE/'audit_hole031_closed.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='token')
 env={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-old-token','exec'),env)
 fields=env['token'](line);return {'fields':fields,'world_value':fields.get('world')}

def row(**changes):
 values=dict(event='ARM',reason='first_entry',coverage='bounded',serial='1',entity='1900',entity_known='1',generation='3',item='220',goal='2',attempt='1',deadline='21',world_known='1',world='00ABCDEF',map_known='1',map='7',source='0',hop='1',edges='1',cached_last='1.05',cached_since='1.05',event_time_known='1',time='1.05',accepted_known='0',accepted='-1',current_point_known='0',current_point='-1',clock='source')
 values.update(changes);return '[CecilItemTransitHistory] '+' '.join(k+'='+str(v)for k,v in values.items())

class SourceGrammar(unittest.TestCase):
 def test_real_old_lexer_does_not_type_msvc_world(self):
  self.assertEqual(parse(row())['world_value'],0xabcdef)
 def test_duplicate_keys_fail_before_custody(self):
  with self.assertRaises(ValueError):parse(row()+' serial=2')
 def test_overwide_pointer_is_not_ia32_world(self):
  with self.assertRaises(ValueError):parse(row(world='0x100000000'))
class Lifecycle(unittest.TestCase):
 def module(self):
  import transit_history_custody_audit as m;return m
 def event(self,line=1,role='botA',**fields):
  value=parse(row(**fields));value.update(line=line,role=role);return value
 def test_pointer_knownbit_and_null_spellings(self):
  for text in ['00ABCDEF','0xabcdef']:
   self.assertEqual(parse(row(world=text))['world_value'],0xabcdef)
  raw=row(event='UNADMITTED',reason='eligibility_false',world_known='0',world='(nil)',map_known='0',map='-1',edges='0',cached_last='-1',cached_since='-1',accepted_known='1',accepted='0',current_point_known='1',current_point='0')
  self.assertIsNone(parse(raw)['world_value']);self.assertEqual(parse(raw)['fields']['world'],'(nil)')
  with self.assertRaises(ValueError):parse(raw.replace('world=(nil)','world=00ABCDEF'))
 def test_schema_flags_width_time_strict(self):
  for bad in [row()+' extra=0',row(entity_known=0),row(accepted_known=0,accepted=1),row(time='nan'),row(serial=1024),row(event_time_known=0,time=1),row(generation=2**32),row(edges=9)]:
   with self.subTest(bad=bad),self.assertRaises(ValueError):parse(bad)
 def test_unadmitted_nonfinite_inputs_are_raw_not_json_nan(self):
  raw=row(event='UNADMITTED',reason='eligibility_false',world_known=0,world='00000000',map_known=0,map=-1,edges=0,cached_last=-1,cached_since=-1,accepted_known=1,accepted=0,current_point_known=1,current_point=0,attempt='nan',deadline='inf')
  value=parse(raw);self.assertFalse(value['numeric']['attempt']['finite']);self.assertEqual(value['numeric']['deadline']['raw'],'inf')
  with self.assertRaises(ValueError):parse(row(attempt='nan'))
 def test_serial_gap_duplicate_reverse_and_process_separation(self):
  m=self.module()
  for last in [1,3]:
   rows=[self.event(),self.event(line=2,event='DISARM',reason='gap',serial=last)]
   self.assertEqual(m.assemble(rows)['status'],'FAIL_INCOMPLETE')
  self.assertEqual(m.assemble([self.event(role='botA'),self.event(role='botB')])['status'],'OBSERVED_BOUNDED_CUSTODY')
 def test_unadmitted_new_ss_interleaves_old_disarm(self):
  rows=[self.event(),self.event(line=2,event='UNADMITTED',reason='eligibility_false',serial=2,item=221,goal=3,attempt=2,deadline=22,world_known=0,world='(nil)',map_known=0,map=-1,edges=0,cached_last=-1,cached_since=-1,accepted_known=1,accepted=0,current_point_known=1,current_point=0),self.event(line=3,event='DISARM',reason='eligibility_false',serial=3),self.event(line=4,event='END',reason='goal_clear',serial=4,event_time_known=0,time=0)]
  value=self.module().assemble(rows);self.assertEqual(value['status'],'OBSERVED_BOUNDED_CUSTODY');self.assertEqual(len(value['unadmitted']),1);self.assertEqual(value['open_admitted_domains'],0)
 def test_domain_end_without_disarm_and_same_ss_different_world(self):
  rows=[self.event(),self.event(line=2,event='END',reason='domain_changed',serial=2),self.event(line=3,serial=3,world='00BBCDEF')]
  value=self.module().assemble(rows);self.assertEqual(value['status'],'OBSERVED_BOUNDED_CUSTODY');self.assertEqual(len(value['domains']),2)
  self.assertEqual(value['open_admitted_domains'],1)
 def test_missing_arm_and_repeated_domain_event_fail(self):
  for rows in [[self.event(event='DISARM',reason='gap')],[self.event(),self.event(line=2,serial=2)]]:
   self.assertEqual(self.module().assemble(rows)['status'],'FAIL_INCOMPLETE')
 def test_cap_format_and_empty_are_never_success(self):
  m=self.module();self.assertEqual(m.assemble([])['status'],'UNEXERCISED')
  for event,reason,serial in [('CAP_REACHED','row_limit',1024),('FORMAT_FAULT','format_bounds',1)]:
   value=m.parse(f'[CecilItemTransitHistory] event={event} reason={reason} coverage=incomplete serial={serial}');value.update(role='botA',line=1)
   self.assertEqual(m.assemble([value])['status'],'FAIL_INCOMPLETE')
 def test_line_and_two_process_count_bound(self):
  with self.assertRaises(ValueError):parse(row(reason='x'*1024))
  with self.assertRaises(ValueError):self.module().assemble([self.event()]*2049)

if __name__=='__main__':unittest.main(verbosity=2)
