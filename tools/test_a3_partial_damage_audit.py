"""Offline semantic/adversarial cases; no game, worker or hook startup."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PARENT=Path('/srv/tse-a3-instruction-probe-root-frozen-20261114')


class ExtractedChecksTests(unittest.TestCase):
 def test_exact_pinned_blocks_are_preserved_in_generated_function_bodies(self):
  import a3_closed_damage_components as b
  generated,witness=b.render()
  self.assertEqual(witness['source_sha256'],'4187020d0ceda1284bcaac3df9ccf98b251ec25863ae6947bd0aa6d96d33464a')
  parsed=ast.parse(generated)
  # Independent pinned source-line spans, not the production extractor's
  # own selection function: a missing assertion must fail this witness.
  historical=next(n for n in ast.parse((PARENT/'analyze-direct020.py').read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name=='analyze')
  ranges=dict(preconditions=(9,49),derive_lives=(50,62),damage=(81,114),host=(115,116),condition=(118,119))
  reference={name:[n for n in historical.body if lo<=n.lineno and n.end_lineno<=hi]for name,(lo,hi)in ranges.items()}
  reference['matched_life']=next(n.body for n in ast.walk(historical)if isinstance(n,ast.For)and n.lineno==71)
  for name,nodes in reference.items():
   fn=next(x for x in parsed.body if isinstance(x,ast.FunctionDef)and x.name==name)
   self.assertEqual([ast.dump(x,include_attributes=False)for x in fn.body[:-1]],[ast.dump(x,include_attributes=False)for x in nodes],name)
  self.assertIn('assert killpairs == lethal',generated)
 def test_changed_historical_source_is_rejected_before_extraction(self):
  import a3_closed_damage_components as b
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'source.py';path.write_text((PARENT/'analyze-direct020.py').read_text()+'\n')
   with self.assertRaisesRegex(ValueError,'historical analyzer pin'):b.render(path)


def life(*,serial=1,dead=True,useful=False):
 return dict(role='botA',local=0,slot=0,entity_id=100,life=serial,spawn_clock=float(serial),right_censored=not dead,corpse_only=False,first_useful_owned_age=0.1 if useful else None,first_inventory_line=serial,last_inventory_line=serial)


def source(*,terminal=True):
 lines=['[CecilSpawn] local=0 tick=10 entity=100 generation=6 respawns=1']
 lines+=['[CecilDeath] local=0 tick=20 entity=100 generation=6 deaths=1']
 if terminal:lines+=['[CecilSpawn] local=0 tick=30 entity=100 generation=7 respawns=2']
 return '\n'.join(lines)+'\n'


class PartialInventoryTests(unittest.TestCase):
 def reconcile(self,lives=None,text=None):
  import a3_partial_inventory as m
  return m.reconcile_local([life()]if lives is None else lives,source()if text is None else text,'botA',0)
 def test_exact_unobserved_open_suffix_is_unknown_and_not_a_life_denominator(self):
  result=self.reconcile()
  self.assertEqual(result['status'],'PARTIAL_INVENTORY_REPORT')
  self.assertEqual(result['observed_lives'],1);self.assertEqual(result['unknown_source_lives'],1)
  self.assertEqual(result['unobserved'][0]['source_generation'],7)
  for field in('server_spawn_clock','window_membership','useful_weapon_outcome','observed_seconds'):self.assertIsNone(result['unobserved'][0][field])
  self.assertFalse(result['unobserved'][0]['included_in_life_denominator'])
 def test_complete_existing_life_observations_remain_component_only(self):
  out=self.reconcile(text=source(terminal=False))
  self.assertEqual(out['status'],'COMPLETE_EXISTING_INVENTORY_OBSERVATIONS');self.assertEqual(out['unobserved'],[])
 def test_missing_inner_life_is_not_an_allowed_suffix(self):
  text=source()+'[CecilDeath] local=0 tick=40 entity=100 generation=7 deaths=2\n[CecilSpawn] local=0 tick=50 entity=100 generation=8 respawns=3\n'
  with self.assertRaises(ValueError):self.reconcile(text=text)
 def test_terminal_dead_cycle_is_not_an_unobserved_open_suffix(self):
  with self.assertRaises(ValueError):self.reconcile(text=source()+'[CecilDeath] local=0 tick=40 entity=100 generation=7 deaths=2\n')
 def test_source_generation_gap_entity_change_counter_or_tick_reversal_fails(self):
  for old,new in [('generation=7','generation=8'),('tick=30','tick=9'),('respawns=2','respawns=3'),('tick=30 entity=100','tick=30 entity=101'),('deaths=1','deaths=2')]:
   with self.subTest(change=(old,new)),self.assertRaises(ValueError):self.reconcile(text=source().replace(old,new))
 def test_missing_observed_death_or_pickup_mismatch_fails(self):
  with self.assertRaises(ValueError):self.reconcile(lives=[life(dead=False)])
  with self.assertRaises(ValueError):self.reconcile(lives=[life(useful=True)])
 def test_unmatched_source_death_duplicate_spawn_or_state_counter_fails(self):
  for tail in ['[CecilDeath] local=0 tick=40 entity=100 generation=8 deaths=2\n','[CecilSpawn] local=0 tick=31 entity=100 generation=7 respawns=2\n','[CecilState] local=0 tick=32 entity=100 generation=7 deaths=0 respawns=2\n']:
   with self.subTest(tail=tail),self.assertRaises(ValueError):self.reconcile(text=source()+tail)
 def test_source_event_for_unmapped_local_cannot_be_silently_ignored(self):
  with self.assertRaises(ValueError):self.reconcile(text=source()+'[CecilSpawn] local=4 tick=31 entity=999 generation=7 respawns=2\n')


class ClosedComponentAuditTests(unittest.TestCase):
 def test_full_existing_damage_checks_work_without_inventing_terminal_inventory(self):
  from a3_partial_damage_test_fixture import make_window
  import audit_a3_closed_damage_partial as a
  with tempfile.TemporaryDirectory()as directory:
   out=a.audit_window(make_window(directory))
  self.assertEqual(out['status'],'PARTIAL_INVENTORY_REPORT');self.assertEqual(out['damage_component']['records'],1)
  self.assertEqual(out['damage_component']['partition']['known_foreign'],1)
  self.assertEqual(out['damage_component']['matrix']['MITTEL -> STARK']['lethal_calls'],1)
  self.assertEqual(out['inventory_component']['observed_bot_lives'],8);self.assertEqual(out['inventory_component']['unknown_source_lives'],1)
  self.assertFalse(out['qualified']);self.assertFalse(out['a3_accepted']);self.assertFalse(out['tier_strength_accepted']);self.assertFalse(out['closed_compare_eligible'])
  self.assertNotIn('damage',out);self.assertNotIn('direct_condition_sha256',out);self.assertNotIn('lives',out)
  self.assertEqual(set(out['provenance']['new_tool_sources_sha256']),{'a3_closed_damage_components.py','a3_partial_inventory.py','audit_a3_closed_damage_partial.py'})
  spec=importlib.util.spec_from_file_location('old_compare',PARENT/'a3_compare_direct_closed.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
  with self.assertRaises((KeyError,ValueError)):old.compare_reports([out,out])
 def test_report_writer_cannot_overwrite_existing_historical_artifact(self):
  from a3_partial_damage_test_fixture import make_window
  import audit_a3_closed_damage_partial as a
  with tempfile.TemporaryDirectory()as directory:
   p=make_window(directory);old=(p/'result.json').read_bytes()
   with self.assertRaises(FileExistsError):a.write_report(p,p/'result.json')
   self.assertEqual((p/'result.json').read_bytes(),old)
 def test_a_claim_of_four_closed_roles_requires_all_four_actual_closed_log_entries(self):
  from a3_partial_damage_test_fixture import make_window
  import audit_a3_closed_damage_partial as a
  with tempfile.TemporaryDirectory()as directory:
   p=make_window(directory);r=json.loads((p/'result.json').read_text());del r['post_close_logs']['logs']['botA'];(p/'result.json').write_text(json.dumps(r))
   with self.assertRaisesRegex(ValueError,'exact four closed roles and log entries'):a.audit_window(p)
 def test_failed_inventory_reconciliation_keeps_a_separately_checked_damage_component(self):
  from a3_partial_damage_test_fixture import make_window
  import audit_a3_closed_damage_partial as a
  with tempfile.TemporaryDirectory()as directory:
   p=make_window(directory)
   with(p/'botB.log').open('a')as stream:stream.write('[CecilDeath] local=0 entity=104 generation=7 tick=40 deaths=2\n')
   out=a.audit_window(p)
  self.assertEqual(out['status'],'FAIL_INVENTORY_RECONCILIATION');self.assertTrue(out['damage_component']['full_existing_checks_passed']);self.assertFalse(out['closed_compare_eligible'])
 def test_existing_checks_reject_mutated_evidence_before_any_partial_acceptance(self):
  from a3_partial_damage_test_fixture import make_window
  import audit_a3_closed_damage_partial as a
  changes=[('result.json',lambda x:x['restoration'].update(restored=False)),('result.json',lambda x:x['cleanup']['botA'].update(closed=False)),('result.json',lambda x:x['frida_damage'].update(original_damage_restored=False)),('result.json',lambda x:x['frida_damage'].update(dropped=1)),('result.json',lambda x:x['frida_damage']['coverage'].update(entire_gameplay_window_covered=False)),('damage-cohort-registry.json',lambda x:x['104'].update(pointer='0x9999')),('queries.json',lambda x:x[0]['query'].update(difficulty='Serious')),('initial-reference.json',lambda x:x['0']['placement'].__setitem__(0,999)),('damage-attribution.json',lambda x:x['known_foreign']['MITTEL'].update(lethal_calls=0)),('host-resources.json',lambda x:x['samples'][0]['violations'].append('CPU'))]
  for name,mutate in changes:
   with self.subTest(file=name,mutation=changes.index((name,mutate))),tempfile.TemporaryDirectory()as directory:
    p=make_window(directory);value=json.loads((p/name).read_text());mutate(value);(p/name).write_text(json.dumps(value))
    with self.assertRaises((AssertionError,ValueError)):a.audit_window(p)
 def test_native_damage_life_sequence_time_and_serverkill_tampering_fails(self):
  from a3_partial_damage_test_fixture import make_window
  import audit_a3_closed_damage_partial as a
  for field in('sequence','spawn','tick','pointer','window','serverkill','nan'):
   with self.subTest(field=field),tempfile.TemporaryDirectory()as directory:
    p=make_window(directory);d=json.loads((p/'frida-damage.jsonl').read_text());record=d['records'][0]
    if field=='sequence':record['sequence']=2
    elif field=='spawn':record['after']['spawn_clock']=.5
    elif field=='tick':record['after']['current_tick']=2.
    elif field=='pointer':record['player_pointer']='0x999'
    elif field=='window':record['entered_ms']=-10.
    elif field=='nan':record['before']['health']=float('nan')
    else:(p/'server.log').write_text('')
    (p/'frida-damage.jsonl').write_text(json.dumps(d)+'\n')
    with self.assertRaises((AssertionError,ValueError)):a.audit_window(p)
 def test_inventory_raw_pid_slot_and_clock_reversal_remain_fail_closed(self):
  from a3_partial_damage_test_fixture import make_window
  import audit_a3_closed_damage_partial as a
  for field in('pid','slot','reversal'):
   with self.subTest(field=field),tempfile.TemporaryDirectory()as directory:
    p=make_window(directory);rows=[json.loads(x)for x in(p/'inventory.jsonl').read_text().splitlines()]
    if field=='pid':rows[1]['snapshot']['process_identity'][0]+=1
    elif field=='slot':rows[1]['snapshot']['players'][4]['slot']=3
    else:
     # A complete extra observed source-like life followed by an old clock
     # is an internal return; no suffix exception may cover it.
     rows.append(copy.deepcopy(rows[1]));rows[1]['snapshot']['players'][4]['spawned_tick']=.5
    (p/'inventory.jsonl').write_text(''.join(json.dumps(x)+'\n'for x in rows))
    if field=='reversal':self.assertEqual(a.audit_window(p)['status'],'FAIL_INVENTORY_RECONCILIATION')
    else:
     with self.assertRaises((AssertionError,ValueError)):a.audit_window(p)


if __name__=='__main__':unittest.main()
