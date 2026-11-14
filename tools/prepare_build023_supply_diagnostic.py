"""Derive exactly one DISABLED180s/diag1 Build023 observation; never runtime."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import prepare_navigation_build023 as build023

PARENT=Path('/srv/tse-nav20-023-red600-disabled-20261114')
PARENT_SHA='51d72a2cf233ff87d2f0cac0d3ad2a532f6f287e6ef62bd154b43e6e4ba8e5e8'
CHANGED=('run-a4.py','adapter_policy.py')
ADDITIONS=('build023_supply_diagnostic_policy.py','prepare_build023_supply_diagnostic.py','test_build023_supply_diagnostic.py')
DELTAS={
 'run-a4.py':[
  ('import a4_hard_map_policy as hardmap','import a4_hard_map_policy as hardmap\nimport build023_supply_diagnostic_policy as diagnostic'),
  ("hardmap.options(map_key,duration,diag,policy.prepared.catalog()['maps'])","diagnostic.hard_options(map_key,duration,diag,policy.prepared.catalog()['maps'])"),
  ("PREFIX=f'ssam-nav20-023-hard-ordered-","PREFIX=f'ssam-supply023-diag1-180-"),
  ("E=BASE/f'nav20-023-hard-ordered-","E=BASE/f'supply023-diag1-180-"),
  ('PRIVATE A4 023 HARD','PRIVATE SUPPLY023 DIAG1 HARD'),
  ('A4_NATIVE_OBSERVATION_REQUIRES_FUNCTIONAL_REVIEW','SUPPLY_DIAGNOSTIC_ONLY_NO_QUALIFICATION'),
  ('PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED','PASS_LIMITED_SUPPLY_DIAGNOSTIC_OBSERVATION_ONLY'),
  ('Private A4 candidate023 Hard normal gameplay; offline review gate.','Private supply diagnostic Build023 Hard180s diag1; offline review gate.'),
  ('type=float,default=600','type=float,default=180'),
  ('type=int,choices=(0,1),default=0','type=int,choices=(1,),default=1')],
 'adapter_policy.py':[('from navigation_comparison_policy import options as validate','from build023_supply_diagnostic_policy import options as validate')]
}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def apply(name,text,reverse=False):
 if name not in DELTAS:raise ValueError('fixed diagnostic source only')
 if not reverse and any(after in text for before,after in DELTAS[name]):raise ValueError('already or partly diagnostic source')
 pairs=reversed(DELTAS[name])if reverse else DELTAS[name]
 for before,after in pairs:
  if reverse:before,after=after,before
  if text.count(before)!=1:raise ValueError('unique exact diagnostic anchor required: '+before)
  text=text.replace(before,after,1)
 ast.parse(text);return text


def transform(name,text):return apply(name,text)
def reverse(name,text):return apply(name,text,True)


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh disabled diagnostic destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact disabled023 parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text())
 if m['runtime_reviewed']is not False or m['comparison']['arm']!='023' or m['comparison']['seconds']!=600 or m['comparison']['diagnostics']!=0:
  raise ValueError('fixed600 diag0 disabled023 parent required')
 for key,base in [('runtime_dependencies',Path('/')),('sources',PARENT),('draft_source_sha256',PARENT)]:
  for name,h in m[key].items():
   if sha(base/name)!=h:raise ValueError('parent source pin changed: '+name)
 build023.validate_build()
 if sha(Path(build023.__file__))!=m['sources']['prepare_navigation_build023.py']:
  raise ValueError('existing023 build validator source differs')
 changed={name:transform(name,(PARENT/name).read_text())for name in CHANGED}
 for name,text in changed.items():
  if reverse(name,text).encode()!=(PARENT/name).read_bytes():raise ValueError('diagnostic reverse bytes differ')
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 for name,text in changed.items():
  (dest/name).write_text(text)
  (dest/(name+'.supply-diag1.diff')).write_text(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),text.splitlines(True),fromfile='disabled023-600-diag0/'+name,tofile='disabled023-180-diag1/'+name)))
 deps={}
 for name,h in m['runtime_dependencies'].items():
  path=Path(name)
  if path.is_relative_to(PARENT):path=dest/path.relative_to(PARENT);h=sha(path)
  deps[str(path)]=h
 deps[str(dest/'build023_supply_diagnostic_policy.py')]=sha(dest/'build023_supply_diagnostic_policy.py')
 m['runtime_dependencies']=deps
 m.update(scope='DISABLED_BUILD023_SUPPLY_DIAGNOSTIC180_DIAG1',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['supply_diagnostic_parent_comparison']=m['comparison']
 m['comparison']=dict(m['comparison'],seconds=180,diagnostics=1,parent_manifest_sha256=PARENT_SHA,profile_semantics='SAME_BUILD_DIFFERENT_DIAGNOSTIC_CONDITION_NO_COMPARISON')
 m['diagnostic']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,single_window_seconds=180,diagnostics=1,build='023',automatic_retry=False,automatic_sequence=False,native_started=False,purpose='observe existing BotCecilSupplyDiagUnavailable readReason/metadata in new own cases; no reproduction of previous103s life assumed',unavailable_log_rate_limit='at most one per second per local; suppressed details remain UNKNOWN',missing_or_ambiguous_reason='UNKNOWN',identity_binding='role/local to actualOwnslot; Sourcegeneration/item to State/Goal/GoalEnd/WPO and same native life/world/epoch; item entity is not bot entity',comparison_claim='different condition: Diagnostics1 adds existing reads/format/logging; no comparison/budget/A4/strength/sync qualification',thresholds_changed=False,new_readers_or_gameplay=False)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_supply_diagnostic=False,reference='PENDING independent Root review/freeze; exactly one180s diag1 window')
 names=set(m['sources'])|set(ADDITIONS)|{name+'.supply-diag1.diff'for name in CHANGED}
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={name.name:sha(name)for name in sorted(dest.glob('*.py'))}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),runtime_reviewed=False,qualified=False,native_started=False)
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(parser.parse_args().destination),indent=2))
