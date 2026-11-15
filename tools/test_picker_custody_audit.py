"""Typed new031 rows; parser-only portable fixtures, no Runtime imports."""
import unittest
try:from picker_custody_audit import parse
except ModuleNotFoundError:
 from audit_a4_native_fire_observer_v2 import source_rows
 def parse(line):
  rows=source_rows(line)
  return rows[0]if rows else None

BASE='local=0 tick=20 actor=500 generation=2'
DEC='[CecilPickerDecision] '+BASE+' time=1 reason=normal_done gates=(7,7) mapped=(1,1) anchor=(0,0) goal=(-1,3) item=(0,600) search_after=0 attempt=(0,1) deadline=(0,0) budget=(12,8) origin=(chosen,0,1) scan=(20,1,20,19,0,0,0,0,0,4) input=(1,3,3,85,0,inf,65535,1,0,64,64,64,64) source_position=(1,2,3) attempts=1 overflow=0 refresh=(0,0)'
H='(-1,0,0,0,0,0,0)'
ATT='[CecilPickerAttempt] '+BASE+' attempt=0 index=0 item=600 kind=0 weapon=7 snapshot=(2,1,10,2,3) end=committed budget=(12,8) visibility=(0,0,0,0,0) nearest=(chosen,3,1) path=(1,inf) h0=(3,4,6,9,8,1,2) h1='+H+' h2='+H
ORG='[CecilPickerOrigin] '+BASE+' nearest=(chosen,0,1) h0=(0,4,6,12,11,1,2) h1='+H+' h2='+H
ARB='[CecilPickerArbitration] '+BASE+' proposal=(1,7,1,0,0) gates=(255,143) taken=1 submitted=1 action=(1,0,0) rotation=(0,0,0) buttons=0 refresh=(0,0)'

class TypedRows(unittest.TestCase):
 def test_actual_new_rows_not_silently_filtered_by_legacy(self):
  for line,tag in [(DEC,'CecilPickerDecision'),(ORG,'CecilPickerOrigin'),(ATT,'CecilPickerAttempt'),(ARB,'CecilPickerArbitration')]:
   with self.subTest(tag=tag):
    got=parse(line);self.assertIsNotNone(got);self.assertEqual(got['tag'],tag)
 def test_nonfinite_path_and_enemy_are_raw_unknown_not_json_nan(self):
  import json
  got=parse(ATT);self.assertIsNotNone(got)
  self.assertEqual(got['fields']['path'][1],{'raw':'inf','nonfinite':'inf'})
  self.assertEqual(parse(DEC)['fields']['input'][5],{'raw':'inf','nonfinite':'inf'})
  json.dumps(got,allow_nan=False)

 def test_malformed_unknown_bounds_and_faults_fail_closed(self):
  bad=[DEC+' extra=1',DEC.replace('tick=20','tick=NaN'),DEC.replace('time=1','time=inf'),DEC.replace('gates=(7,7)','gates=(1,7)'),DEC.replace('attempts=1','attempts=9'),DEC.replace('overflow=0','overflow=1'),DEC.replace('local=0','local=4'),ATT.replace('path=(1,inf)','path=(1,inf,0)'),ATT.replace('snapshot=(2,1,10,2,3)','snapshot=(2,1,nan,2,3)'),ARB.replace('submitted=1','submitted=0'),'[CecilPickerFault] local=0 tick=20 reason=summary_format',DEC+'x'*1024]
  for row in bad:
   with self.subTest(row=row[:70]),self.assertRaises(ValueError):parse(row)
 def test_probe_unknown_is_not_blocked(self):
  for code in (0,1,2,3,4,5,6):
   values={0:'0,0,0,0,0',1:'1,9,9,0,0',2:'2,2,2,0,0',3:'3,9,8,1,0',4:'4,9,8,1,2',5:'5,9,8,1,2',6:'6,9,8,1,2'}[code]
   r=parse(ATT.replace('visibility=(0,0,0,0,0)','visibility=('+values+')'))
   self.assertEqual(r['fields']['visibility'][0],code)
 def test_strict_batch_denominator_and_duplicate_loss(self):
  from picker_custody_audit import assemble
  rows=[]
  for n,line in enumerate([DEC,ORG,ATT,ARB]):
   r=parse(line);r.update(phase=0,role='botA',line=n+1);rows.append(r)
  self.assertEqual(len(assemble(rows)),1)
  for bad in [rows[1:],rows[:1]+rows[2:],rows[:2]+rows[3:],rows+[rows[0]],rows+[rows[2]]]:
   with self.assertRaises(ValueError):assemble(bad)
  # Missing arbitration is NOT fabricated into a blocked/not-submitted event;
  # its admission requires actual Driver control-flow evidence outside grammar.
  self.assertIsNone(assemble(rows[:3])[0]['arbitration'])
 def test_nonfinite_forms_preserve_exact_text(self):
  for token,kind in [('inf','inf'),('-inf','-inf'),('nan','nan')]:
   self.assertEqual(parse(ATT.replace('path=(1,inf)','path=(1,'+token+')'))['fields']['path'][1],{'raw':token,'nonfinite':kind})


class NativeGeometry(unittest.TestCase):
 def test_nonzero_translation_baseline_is_not_nulltranslation_duration(self):
  from audit_reset031_picker_closed import geometry
  life={'spawn_clock':1}
  rows=[dict(spawn=1,good=True,tick=2,position=[0,0,0],translation=[1,0,0]),dict(spawn=1,good=True,tick=2.1,position=[0,0,0],translation=[0,0,0])]
  self.assertEqual(geometry(rows,life)['exact_position_zero_translation_span'],0)

if __name__=='__main__':unittest.main()
