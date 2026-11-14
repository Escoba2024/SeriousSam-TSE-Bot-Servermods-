"""Offline source preparation only. Does not import or execute any controller."""
from pathlib import Path
import argparse, ast, difflib, hashlib, json, shutil

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--parent',type=Path,required=True)
parser.add_argument('--analysis-parent',type=Path,required=True)
parser.add_argument('--destination',type=Path,required=True)
parser.add_argument('--build',type=Path,required=True)
parser.add_argument('--hard-rules',type=Path,required=True)
args=parser.parse_args()
parent=args.parent.resolve();analysis_parent=args.analysis_parent.resolve()
dest=args.destination.resolve();build=args.build.resolve()
repo=Path(__file__).resolve().parent.parent
if dest.exists():raise SystemExit('destination must be new; closed packages are immutable')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((parent/'source-manifest.json').read_text())
assert sha(parent/'source-manifest.json')=='412755b8bc5d2c962321f1bfeaeb6ad51efc43af0c3a8c659d2631c1145f9e69','original frozen A3 parent manifest'
for relative,expected in old['sources'].items():
 assert sha(parent/relative)==expected,('changed original parent source',relative)
assert sha(analysis_parent/'analyze.py')=='19663824866785e7f377de019c9b8adc1e4e08c533801e412cbfb25da25c8705','original closed damage analyzer'
assert sha(analysis_parent/'behavior.py')=='10a9872b7ab23f4e9b5848b1d20a40dfa0de5c709cefea18d9b4f7a164dc4be9','original behavior analyzer'
assert sha(build/'manifest.json')=='3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6','exact Build020 manifest'
assert sha(args.hard_rules)=='9e255659101eee27b6d4dcf285129a52488db29cab021ff380c290f2d34d7472','exact inherited Hard native/query policy'
assert sha(build/'Sources/Game/GameMP.dll')=='094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0','exact Build020 DLL'
shutil.copytree(parent,dest,ignore=shutil.ignore_patterns('__pycache__','run-a3-damage018.py','*.log'))
shutil.copy2(args.hard_rules,dest/'stability_hard_rules.py')
early_manifest=json.loads((dest/'source-manifest.json').read_text());early_manifest['runtime_reviewed']=False;early_manifest['qualified']=False;(dest/'source-manifest.json').write_text(json.dumps(early_manifest,indent=2)+'\n')
for name in ['a3_direct_tiers.py','a3_direct_controller_policy.py','a3_compare_direct_closed.py','test_a3_direct_tiers.py','test_a3_direct_adapter.py','test_a3_direct_behavior.py','test_a3_direct_compare_closed.py','test_a3_direct_closed_fixture.py']:
 shutil.copy2(repo/'tools'/name,dest/name)
original=(parent/'run-a3-damage018.py').read_text();s=original
changes={
 'import controller_policy as policy':'import a3_direct_controller_policy as policy',
 'import a3_damage_policy as damage':'import a3_damage_policy as damage\nimport stability_hard_rules as hard_rules',
 'RUNTIME_REVIEWED=True':'RUNTIME_REVIEWED=False',
 'build-018-20261112/Sources/Game/GameMP.dll':'build-020-20261114/Sources/Game/GameMP.dll',
 "assert value==0":"assert value==0 and duration==120 and diag==0 and instrumentation==1,'fixed direct-tier120s instrumented diagnostics0 protocol'",
 "PREFIX=f'ssam-arena018public-initialcapture-swap{SWAP}-20261112'":"PREFIX=f'ssam-direct020-hard-pair{trial}{trial+1}-swap{SWAP}-20261114'",
 "E=BASE/f'arena018public-initialcapture-swap{SWAP}-trial-{trial}-{time.strftime(\"%H%M%S\",time.gmtime())}'":"E=BASE/f'direct020-hard-pair{trial}{trial+1}-swap{SWAP}-{time.strftime(\"%Y%m%d-%H%M%S\",time.gmtime())}'",
 "'candidate_tier':trial":"'pair_lower_tier':trial,'direct_pair':[trial,trial+1],'role_tiers':{r:c['tier']for r,c in cohorts.items()}",
 "('public.ini','candidate.ini','initial-reference.json','source-manifest.json','controller_policy.py')":"('public.ini','candidate.ini','initial-reference.json','source-manifest.json','controller_policy.py','a3_direct_controller_policy.py','a3_direct_tiers.py','stability_hard_rules.py')",
 "text=config.read_text().replace('dev_bRemoveDamageAndInvisibility=1;','')":"text=policy.hard_server_template(config.read_text()).replace('dev_bRemoveDamageAndInvisibility=1;','')",
 "barrier={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}":"barrier={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}\n   for snapshot in barrier.values():hard_rules.validate_session(snapshot)",
 "snapshots={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}":"snapshots={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}\n     for snapshot in snapshots.values():hard_rules.validate_session(snapshot)",
 "queries.append({'elapsed':elapsed,'query':q})":"hard_rules.validate_query(q);queries.append({'elapsed':elapsed,'query':q})",
 'attribution_registry=damage.build_registry(owned_rows,mapping,cohorts)':'attribution_registry=policy.build_direct_registry(damage,owned_rows,mapping,cohorts)',
 "report['baseline']=f'actual public7fc HumanAI0 AutoCombat1 pinned config; candidate018 tier{trial}'":"report['baseline']=f'direct Build020 Hard2 tier{trial} versus tier{trial+1}; identical canonical config except ArenaTier';report['actual_role_profiles']=policy.check_actual_tiers({r:(R/r/'SeriousSam.log').read_text(errors='replace')for r in ('botA','botB')},cohorts)",
 "description='Private owned-fixture public7fc versus018 damage comparison; runtime only when explicitly invoked.'":"description='Disabled direct Build020 adjacent-tier comparison; Root freeze required.'",
 "parser.add_argument('tier',type=int,choices=(1,2,3))":"parser.add_argument('tier',type=int,choices=(1,2))"}
for a,b in changes.items():
 expected=2 if a.startswith("('public.ini'")else 1
 assert s.count(a)==expected,(a,s.count(a));s=s.replace(a,b)
ast.parse(s);(dest/'run-a3-direct020.py').write_text(s)
back=s
for a,b in reversed(list(changes.items())):back=back.replace(b,a)
assert back==original
(dest/'direct-controller.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='build018/run-a3-damage018.py',tofile='direct020/run-a3-direct020.py')))
# Generalize only the existing candidate-only lifecycle block and labels.
a=(analysis_parent/'analyze.py').read_text();start=a.index(" candidate_role=next(role for role in ('botA','botB')if cohorts[role]=='candidate');")
end=a.index(' summary={}',start);block=a[start:end];block=block[block.index("text=(P/(candidate_role+'.log'))"):]
a=a[:start]+" for candidate_role in ('botA','botB'):\n"+'  '+block.splitlines()[0]+'\n'+''.join(' '+line+'\n'for line in block.splitlines()[1:])+a[end:]
a=a.replace("P/'controller_policy.py'","P/'a3_direct_controller_policy.py'")
a=a.replace("('candidate'if R['cohort_policy'][role]['candidate']else'public')","R['cohort_policy'][role]['tier_name']")
a=a.replace("R['candidate_tier']","R['pair_lower_tier']")
a=a.replace("for cohort in ('public','candidate','vanilla'):","for cohort in tuple(cohorts[r]for r in ('botA','botB'))+('vanilla',):")
a=a.replace(" cohorts={role:R['cohort_policy'][role]['tier_name']for role in ('botA','botB')};cohorts['vanilla']='vanilla'"," cohorts={role:R['cohort_policy'][role]['tier_name']for role in ('botA','botB')};cohorts['vanilla']='vanilla'\n assert pol.check_actual_tiers({r:(P/(r+'.log')).read_text()for r in ('botA','botB')},R['cohort_policy'])==R['actual_role_profiles']")
# Bind the archived role metadata to the independently reproduced direct config.
a=a.replace("assert c['config_sha256']==R['cohort_policy'][role]['config_sha256']", "assert c['config_sha256']==R['cohort_policy'][role]['config_sha256']\n  assert all(c[k]==R['cohort_policy'][role][k]for k in ('candidate','tier','tier_name','game_sha256','config_base_sha256'))")
a=a.replace(" mapping=pol.slot_mapping"," hard_spec=importlib.util.spec_from_file_location('hard_'+name,P/'stability_hard_rules.py');hard=importlib.util.module_from_spec(hard_spec);hard_spec.loader.exec_module(hard)\n for sample in R['barrier_before_release'].values():hard.validate_session(sample)\n for line in (P/'session-health.jsonl').read_text().splitlines():\n  for sample in json.loads(line)['roles'].values():hard.validate_session(sample)\n mapping=pol.slot_mapping")
a=a.replace(" for q in Q:"," for q in Q:\n  hard.validate_query(q['query'])")
# Keep inherited closed-log/damage/restore proofs and output actual pair metadata.
a=a.replace("tier=R['pair_lower_tier'],swap=", "pair=R['direct_pair'],role_tiers=R['role_tiers'],swap=")
a=a.replace("  lives.append(life)","  life['left_censored_first_useful_observation']=bool(alive and useful(alive[0]));lives.append(life)")
a=a.replace(" (OUT/(name+'.json')).write_text", " report['direct_condition']={'dll_sha256':pol.CANDIDATE_SHA,'config_base_sha256':R['cohort_policy']['botA']['config_base_sha256'],'initial_reference_sha256':report['initial_reference_sha256'],'world_crc32':f['world_crc32'],'cecil_path_hash':f['cecil_path_hash'],'controller_sha256':sha(P/'controller-source.py'),'duration_seconds':120,'host_budget':json.loads((P/'source-manifest.json').read_text())['host_budget'],'native_rules':hard.EXPECTED,'hard_rules_sha256':sha(P/'stability_hard_rules.py')}\n report['direct_condition_sha256']=hashlib.sha256(json.dumps(report['direct_condition'],sort_keys=True,separators=(',',':')).encode()).hexdigest()\n report['native_hard_rules_verified']=True\n report['tier_strength_accepted']=False\n (OUT/(name+'.json')).write_text")
ast.parse(a);(dest/'analyze-direct020.py').write_text(a)
# Existing behavior metrics, now executed independently for both actual roles.
b=(analysis_parent/'behavior.py').read_text().replace('def inspect(name):','def inspect_role(name,role):')
b=b.replace(";role=next(r for r,v in R['cohort_policy'].items()if v['candidate']);mapping=",';mapping=')
b=b.replace("'tier':R['candidate_tier'],'candidate_role':role", "'tier':R['cohort_policy'][role]['tier'],'physical_role':role")
b=b.replace("name+'-behavior.json'","name+'-'+role+'-behavior.json'")
old_tail="if __name__=='__main__':\n import sys\n for name in sys.argv[1:]:inspect(name)\n"
assert b.endswith(old_tail)
b=b[:-len(old_tail)]+"def inspect(name):\n output={role:inspect_role(name,role)for role in ('botA','botB')}\n (D/(name+'-both-behavior.json')).write_text(json.dumps(output,indent=2)+'\\n')\n return output\n"+old_tail
ast.parse(b);(dest/'behavior-direct020.py').write_text(b)
for name,old_text,new_text in [('analyze-direct020.py',(analysis_parent/'analyze.py').read_text(),a),('behavior-direct020.py',(analysis_parent/'behavior.py').read_text(),b)]:
 (dest/(name+'.diff')).write_text(''.join(difflib.unified_diff(old_text.splitlines(True),new_text.splitlines(True),fromfile='build018/'+name,tofile='direct020/'+name)))
# All immutable hook/host/restore sources stay byte-identical; no native checks.
unchanged=['damage_policy.py','a3_damage_policy.py','host_budget.py','transaction.py','strict_backend.py']
unchanged += [str(p.relative_to(parent))for p in(parent/'frozen-v2').rglob('*')if p.is_file()and'__pycache__'not in p.parts]
assert all((dest/n).read_bytes()==(parent/n).read_bytes()for n in unchanged)
m=json.loads(json.dumps(old));newdeps={}
for path,h in old['runtime_dependencies'].items():
 q=Path(path)
 if q.is_relative_to(parent):
  rel=q.relative_to(parent);q=dest/rel
  if q.name=='run-a3-damage018.py':q=dest/'run-a3-direct020.py'
  h=sha(q)
 if '/tse-milestone-a-build-018-20261112/'in str(q):
  q=Path(str(q).replace('tse-milestone-a-build-018-20261112','tse-milestone-a-build-020-20261114'));h=sha(q)
 newdeps[str(q)]=h
for n in ['a3_direct_tiers.py','a3_direct_controller_policy.py','stability_hard_rules.py']:newdeps[str(dest/n)]=sha(dest/n)
manifest=json.loads((build/'manifest.json').read_text())
m.update(runtime_dependencies=newdeps,runtime_reviewed=False,qualified=False,
 scope='DISABLED_DIRECT_BUILD020_ADJACENT_TIERS_OFFLINE_PREPARATION',
 candidate={'build_manifest':str(build/'manifest.json'),'build_manifest_sha256':sha(build/'manifest.json'),
 'dll_sha256':manifest['dll_sha256'],'source_commit':manifest['repo_commit']})
m['external_runtime_pin_note']='Fresh verification pending for this direct-tier package; historical qualification is not inherited.'
m['external_runtime_pins_reverified']=False;m['external_runtime_pins_verified_utc']=None
m['root_review']='PENDING independent direct020 review; historical parent approval is not inherited'
m['author_offline_verification']={'pure_policy_tests_passed':8,'controller_and_analyzer_tests_pending':True}
m['direct_tiers']={'parent_manifest_sha256':sha(parent/'source-manifest.json'),'parent_source':str(parent),
 'selected_windows':[[1,0],[1,1],[2,0],[2,1]],'duration_seconds':120,'difficulty':2,'hard_rules_sha256':sha(args.hard_rules),'diagnostics':0,'instrumentation':1,
 'automatic_series':False,'automatic_retry':False,'runtime_authorized':False,
 'source_preparation_only':True,'inherited_external_pins_fresh_check_pending':True,
 'new_controller_analyzer_tests_pending':True,'same_damage_host_restore_files':unchanged}
m['sources']={str(p.relative_to(dest)):sha(p)for p in dest.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.name!='source-manifest.json'}
(dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
(dest/'RUNPLAN-disabled.json').write_text(json.dumps({'runtime_allowed':False,'automatic_series':False,
 'automatic_retry':False,'candidate':m['candidate'],'individual_windows':[[1,0],[1,1],[2,0],[2,1]],
 'command_after_root_review_only':'python3 run-a3-direct020.py --instrumentation 1 LOWER_TIER 120 0 SWAP',
 'closed_analysis_commands':['python3 analyze-direct020.py WINDOW','python3 behavior-direct020.py WINDOW','python3 a3_compare_direct_closed.py SWAP0_WINDOW SWAP1_WINDOW'],'open':['fresh external pins','focused new controller/analyzer tests','independent review','Root freeze/preflight/native']},indent=2)+'\n')
(dest/'HANDOFF.json').write_text(json.dumps({'status':'DISABLED_UNTESTED_ADAPTER_ANALYZERS',
 'pure_policy_test_count':8,'pure_policy_passed':True,'native_started':False,
 'controller_tests_pending':True,'no_strength_or_runtime_qualification':True,
 'parent_unchanged':str(parent),'next':'Root frees resources; verify new adaptation offline then independent review and exact freeze.'},indent=2)+'\n')
m['sources']={str(p.relative_to(dest)):sha(p)for p in dest.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.name!='source-manifest.json'}
(dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'package':str(dest),'manifest_sha256':sha(dest/'source-manifest.json'),
 'runtime_gate':False,'native_started':False,'source_preparation_only':True}))
