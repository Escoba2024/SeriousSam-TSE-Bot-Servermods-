"""Prepare one fresh DISABLED role-exact powerup server module adapter."""
import argparse
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import shutil

import prepare_powerup_contrast as baseline
from powerup_contrast_policy import checked_flag

PARENTS={
 0:(Path('/srv/tse-powerup-off0-048-red600-disabled-20261115'),'bb2e57f00a7647bbd7a3ba885f95f6aa01155e4d233121650715addbb8b99ce2'),
 1:(Path('/srv/tse-powerup-on1-048-red600-disabled-20261115'),'93a6a113d05fa57a4e570ac644cd840054456d4f8439608e1915a413e21abfec')}
CHANGED=('run-a4.py','a4_canonical_native_groups.py')
ADDITIONS=('powerup_server_module_policy.py','prepare_powerup_server_modules.py','test_powerup_server_module_policy.py','test_prepare_powerup_server_modules.py')
SERVER_CORE='powerup_server_native_fire.py'
CORE_DELTAS=[('import audit_a4_native_fire_observer_v2 as audit','import audit_a4_native_fire_observer_v2 as audit\nimport powerup_server_module_policy as server_modules'),
 ("    require(sample.get('hashes') == ORIGINAL_HASHES, 'sample Original module hashes')","    server_modules.check_sample_hashes(sample, 'server', server_identity)")]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def deltas(name,flag):
 checked_flag(flag)
 if name=='a4_canonical_native_groups.py':return[('import a4_fire_observer_v2 as core','import powerup_server_native_fire as core')]
 if name!='run-a4.py':raise ValueError('fixed runner and group import sources only')
 return[
  ('import a4_fire_observer_v2 as native_fire','import powerup_server_native_fire as native_fire\nimport powerup_server_module_policy as server_modules'),
  (f"PREFIX=f'ssam-powerup-048-offon{flag}-{{map_key}}-20261115'",f"PREFIX=f'ssam-powerup-048-offon{flag}-modulev2-{{map_key}}-20261115'"),
  (f"E=BASE/f'powerup-048-offon{flag}-",f"E=BASE/f'powerup-048-offon{flag}-modulev2-"),
  ("'a4_fire_observer_v2.py','audit_a4_native_fire_observer_v2.py'","'a4_fire_observer_v2.py','powerup_server_native_fire.py','powerup_server_module_policy.py','audit_a4_native_fire_observer_v2.py'"),
  ("     assert snap['all_selected_present'];snap=canonical_groups.bind_sample(snap,group,native_group_contract,read_serial,sample_start,sample_end,'paused_smoke');",
   "     if read_serial==1:server_modules.archive_first_sample(E/'first-unbound-server-inventory.jsonl',snap,read_serial=read_serial,group=group,phase='paused_smoke',server_identity=server,started=sample_start,ended=sample_end)\n     assert snap['all_selected_present'];snap=canonical_groups.bind_sample(snap,group,native_group_contract,read_serial,sample_start,sample_end,'paused_smoke');")]


def exact(text,pairs,reverse=False):
 for before,after in(reversed(pairs)if reverse else pairs):
  if reverse:before,after=after,before
  if text.count(before)!=1:raise ValueError('unique exact source anchor required: '+before)
  text=text.replace(before,after,1)
 ast.parse(text);return text


def transform(name,text,flag):return exact(text,deltas(name,flag))
def reverse(name,text,flag):return exact(text,deltas(name,flag),True)
def server_core(text):return exact(text,CORE_DELTAS)
def reverse_core(text):return exact(text,CORE_DELTAS,True)


def validate_parent_manifest(m,flag):
 checked_flag(flag);c=m['powerup_contrast'];comparison=m['comparison']
 if(any(m[k]is not False for k in('runtime_reviewed','runtime_performed','qualified','functional_pass'))
    or c['flag']!=flag or type(c['flag'])is not int or c['dedicated_sha256']!=baseline.DEDICATED_SHA
    or c['bot_sha256']!=baseline.BOT_SHA or c['closure_targets']!=81
    or comparison['arm']!=f'OFFON{flag}'or comparison['map']!='redstation'or comparison['seconds']!=600
    or comparison['diagnostics']!=0 or comparison['hard_difficulty']!=2 or comparison['observer_fps']!=20
    or comparison['automatic_retry']is not False or comparison['automatic_sequence']is not False):
  raise ValueError('exact disabled powerup flag parent conditions required')


def validate_parent(flag):
 checked_flag(flag);parent,want=PARENTS[flag]
 if sha(parent/'source-manifest.json')!=want:raise ValueError('parent manifest changed')
 m=json.loads((parent/'source-manifest.json').read_text());validate_parent_manifest(m,flag)
 for group,base in[('runtime_dependencies',Path('/')),('sources',parent),('draft_source_sha256',parent)]:
  for name,h in m[group].items():
   if sha(base/name)!=h:raise ValueError('parent source/dependency changed: '+name)
 return m


def prepare(destination,flag):
 checked_flag(flag);parent,parent_sha=PARENTS[flag];dest=Path(destination).resolve()
 protected=[p[0]for p in PARENTS.values()]+[baseline.PARENT,baseline.BUILD,baseline.OVERLAY,Path('/srv/tse-arena-isolated-20261111')]
 if dest.exists()or any(dest.is_relative_to(p)for p in protected):raise ValueError('fresh independent non-runtime destination required')
 m=validate_parent(flag);dedicated=baseline.validate_dedicated()
 originals={name:(parent/name).read_text()for name in CHANGED}
 changed={name:transform(name,text,flag)for name,text in originals.items()}
 for name,text in changed.items():
  if reverse(name,text,flag)!=originals[name]:raise ValueError('whole parent inverse differs')
 original_core=(parent/'a4_fire_observer_v2.py').read_text();adapted=server_core(original_core)
 if reverse_core(adapted)!=original_core:raise ValueError('whole original V2 copy inverse differs')
 shutil.copytree(parent,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 for name,text in changed.items():(dest/name).write_text(text)
 (dest/SERVER_CORE).write_text(adapted)
 diffs=[]
 for name,before,after in [(name,originals[name],changed[name])for name in CHANGED]+[(SERVER_CORE,original_core,adapted)]:
  target=name+'.modulev2.diff';diffs.append(target)
  (dest/target).write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='disabled-parent/'+name,tofile='disabled-server-module-v2/'+name)))
 deps={}
 for name,h in m['runtime_dependencies'].items():
  path=Path(name)
  if path.is_relative_to(parent):path=dest/path.relative_to(parent);h=sha(path)
  deps[str(path)]=h
 for name in('powerup_server_module_policy.py',SERVER_CORE):deps[str(dest/name)]=sha(dest/name)
 if {p:h for p,h in deps.items()if p in dedicated}!=dedicated:raise ValueError('dedicated81 closure changed')
 m['runtime_dependencies']=deps
 m.update(scope='DISABLED_EXISTING_DEDICATED_ROLE_EXACT_MODULE_V2_CONTRAST_ONLY',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['powerup_server_module_adapter']=dict(parent=str(parent),parent_manifest_sha256=parent_sha,role='server',game_sha256=baseline.DEDICATED_SHA,original_v2_retained_byte_identical=True,server_core=SERVER_CORE,server_core_inverse_sha256=sha(parent/'a4_fire_observer_v2.py'),changed_parent_sources=list(CHANGED),original_reader_unchanged=True,original_engine_entities_unchanged=True,bot_vanilla_guards_unchanged=True,schema_queue_life_clock_thresholds_unchanged=True,first_raw=dict(filename='first-unbound-server-inventory.jsonl',read_serial=1,group='botA_actual',phase='paused_smoke',max_bytes=65536,mode='0600/O_EXCL/O_APPEND',before_bind=True,later_prebind_failures_preserved=False,extra_io='one paused bounded write; unchanged host/startup budgets apply'),old061540_fail_preserved=True,native_started=False)
 names=set(m['sources'])|set(ADDITIONS)|{SERVER_CORE}|set(diffs)
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={path.name:sha(path)for path in sorted(dest.glob('*.py'))}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),flag=flag,manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),server_core_sha256=sha(dest/SERVER_CORE),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),dedicated_closure_pins=81,native_started=False,runtime_reviewed=False,qualified=False,functional_pass=False)
 (dest/'HANDOFF-disabled-modulev2.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);p.add_argument('--flag',type=int,choices=(0,1),required=True)
 args=p.parse_args();print(json.dumps(prepare(args.destination,args.flag),indent=2))
