"""Offline closed damage component audit; never a Legacy/full A3 report."""
import argparse
import hashlib
import json
from pathlib import Path

from a3_closed_damage_components import PARENT,load_components
from a3_partial_inventory import reconcile_local,validate_memory_order

PINS={
 'a3_direct_controller_policy.py':'6d2334c15fe504d8dbcb4921f5583d87ce4e05492a1e328625897a64094a0ed2',
 'controller_policy.py':'585c3ce20e5c0635369b01e8992fadd143b55563828712cf1dea2be47cdedd43',
 'a3_direct_tiers.py':'190751a04f07df2968046fe478c3398c356f1990cc2e37f07a90bb2ad4af5a74',
 'stability_hard_rules.py':'9e255659101eee27b6d4dcf285129a52488db29cab021ff380c290f2d34d7472',
 'source-manifest.json':'272d04e3f82f270ecf52241da8fc66a2f516e7f9657215af08703044e6aad6a7',
 'controller-source.py':'f9cb4c4991d101e096787c5ccd5ee26a552b0a34dc8f43e600e7f75f07a7433a',
 'original_damage_worker.py':'806d4c33a3db0f5c208ee235319850513715c6144ed30912e95cf554e38b677c',
 'original_damage_collector.py':'a6ddad52fdc5bbb906d91df303a1ac78ef1b0f66a78a9346fec0f62ac51a422d'}
HOOK_PINS=dict(hook_source_sha256='9939fde5643075f698e3ff3b80c2f46d2b7cf5932106c2e81440590e23a0576a',host_source_sha256='db411bb6757abdc6e6b0ca124f948234fff656a71d8ec7659bb4322cbc18caa8',guard_source_sha256='3f7142734eb26eb5d6277671b04299bbd0d167be085da14082726feff95274bf')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def audit_window(path):
 p=Path(path).resolve(strict=True)
 if not p.is_dir():raise ValueError('closed evidence directory required')
 for name,pin in PINS.items():
  if sha(p/name)!=pin:raise ValueError('closed source pin differs: '+name)
 raw_result=json.loads((p/'result.json').read_text());roles={'server','botA','botB','vanilla'}
 if set(raw_result['cleanup'])!=roles or set(raw_result['post_close_logs']['logs'])!=roles:raise ValueError('exact four closed roles and log entries required')
 checks,witness=load_components();context=checks.preconditions(p.name,p.parent)
 r=context['R'];f=r['frida_damage']
 if r['controller_sha256']!=PINS['controller-source.py']:raise ValueError('recorded controller differs')
 if not r['observed_seconds']>=120:raise ValueError('full120s observed window required')
 if not all(f[k]==pin for k,pin in HOOK_PINS.items()):raise ValueError('recorded damage observer differs')
 if f['version']!='17.26.2':raise ValueError('recorded Frida version differs')
 damage=checks.damage(p,r,context['registry'],context['names'],context['cohorts'],context['slots'])
 host,costs=checks.host(p,r)
 condition=checks.condition(p,r,context['pol'],context['hard'],f,dict(initial_reference_sha256=sha(p/'initial-reference.json')))
 inventory_error=None;locals_out=[];lives=None
 try:
  validate_memory_order(context['observations'])
  lives=checks.derive_lives(context['observations'],context['slots'],context['cohorts'])
  for role in('botA','botB'):
   text=(p/(role+'.log')).read_text()
   for local in range(4):locals_out.append(reconcile_local([x for x in lives if x['role']==role and x['local']==local],text,role,local,checks))
 except (AssertionError,ValueError)as error:inventory_error=str(error)
 unknown=[x for row in locals_out for x in row['unobserved']]
 status='FAIL_INVENTORY_RECONCILIATION'if inventory_error else'PARTIAL_INVENTORY_REPORT'if unknown else'CLOSED_DAMAGE_COMPONENT_ONLY'
 inputs=set(PINS)|{'result.json','inventory.jsonl','first-spawn-observations.json','neutral-spawn-observations.json','pending-phase-errors.json','initial-reference.json','session-health.jsonl','frida-damage.jsonl','damage-cohort-registry.json','damage-attribution.json','server.log','botA.log','botB.log','queries.json','host-resources.json','botA-cohort.ini','botB-cohort.ini','candidate.ini','public.ini'}|{role+'-closed.log'for role in('server','botA','botB','vanilla')}
 return dict(schema='SSAM_A3_CLOSED_DAMAGE_COMPONENT_V1',status=status,qualified=False,a3_accepted=False,tier_strength_accepted=False,closed_compare_eligible=False,runtime_performed_by_this_audit=False,
  source_window=dict(name=p.name,native_status=r['status'],observed_seconds=r['observed_seconds'],pair=r['direct_pair'],role_tiers=r['role_tiers'],swap=bool(r['swap_cohorts'])),
  checked_condition=condition['direct_condition'],checked_condition_hash=condition['direct_condition_sha256'],
  preserved_checks=dict(closed_roles=4,initial_replay_exact=True,all_nine_initial_reference_match=True,cohort_configs_reproduced=True,actual_slot_mapping=context['mapping'],hard_sessions_and_queries=True,server_pid_and_registry_binding=True,original_bodies_restored=True,host_violations=0),
  damage_component=dict(full_existing_checks_passed=True,records=len(damage['records']),partition=dict(damage['counts']),by_source=dict(damage['damage']),matrix=dict(damage['matrix']),pair_calls=dict(damage['pairs']),same_spawn_tick_health_decreases=damage['same_tick'],server_kills=len(damage['kills']),server_kill_pairs_equal_all_lethal_records=True,full_recorded_coverage=True,first_processed_state_proven=False),
  inventory_component=dict(status='FAIL_INVENTORY_RECONCILIATION'if inventory_error else'PARTIAL'if unknown else'COMPLETE_EXISTING_OBSERVATIONS',error=inventory_error,rows=context['nrows'],locals=locals_out,observed_bot_lives=None if lives is None else sum(x['role']in('botA','botB')for x in lives),reconciliation_complete=not bool(inventory_error),unknown_source_lives=len(unknown),unobserved=unknown,unknowns_in_life_denominator=False,complete_supply_statistics_claimed=False),
  host=host['summary'],costs=costs,provenance=dict(extraction=witness,inputs_sha256={name:sha(p/name)for name in sorted(inputs)},auditor_sha256=sha(__file__),new_tool_sources_sha256={name:sha(Path(__file__).resolve().parent/name)for name in('a3_closed_damage_components.py','a3_partial_inventory.py','audit_a3_closed_damage_partial.py')}))


def write_report(path,output):
 report=audit_window(path);out=Path(output)
 # Existing artifacts/results cannot be overwritten, including old FAILs.
 with out.open('x')as stream:json.dump(report,stream,indent=2,allow_nan=False);stream.write('\n')
 return report


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('window',type=Path);parser.add_argument('--output',required=True,type=Path)
 args=parser.parse_args();report=write_report(args.window,args.output)
 print(json.dumps(dict(status=report['status'],report=str(args.output),records=report['damage_component']['records'],unknown_source_lives=report['inventory_component']['unknown_source_lives'],a3_accepted=False)))
 if report['status'].startswith('FAIL'):raise SystemExit(1)
