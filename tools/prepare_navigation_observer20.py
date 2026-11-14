"""Fresh disabled common renderer condition; preserve all earlier failed arms."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

from navigation_observer20 import EXPECTED_PATH,BEFORE_SHA256,transform as observer_config

PARENTS={
 '048':(Path('/srv/tse-nav-048-red600-disabled-20261114'),'9d3f27501151176b4641e5521e37b2996e74eda1ed10271798648ee733180a14'),
 '018':(Path('/srv/tse-nav-018-red600-disabled-20261114'),'5acfe55ef475bc9529f87e919539ea38fdd3e4e72aefdad14cc7410f6bd2aa75'),
 '020':(Path('/srv/tse-nav-020-red600-disabled-20261114'),'cbcffaab5964efe82d776938e46187b38de671c69e425d5fdf30b40a5fedae03'),
}
ADDITIONS=('navigation_observer20.py','prepare_navigation_observer20.py','test_navigation_observer20.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(text,old,new):
 if text.count(old)!=1:raise ValueError('unique inherited anchor required')
 return text.replace(old,new,1)


def transform(text,build):
 if build not in PARENTS:raise ValueError('fixed matched arm only')
 text=once(text,'from host_budget import HostBudget\n','from host_budget import HostBudget\nfrom navigation_observer20 import stage as stage_observer20\n')
 text=once(text,'   transaction.seal()\n',"   transaction.seal()\n   report['observer_render_config']=stage_observer20(R/'vanilla/Scripts/CecilObserver.ini')\n")
 text=once(text,f"PREFIX=f'ssam-nav-{build}-hard-ordered-",f"PREFIX=f'ssam-nav20-{build}-hard-ordered-")
 text=once(text,f"E=BASE/f'nav-{build}-hard-ordered-",f"E=BASE/f'nav20-{build}-hard-ordered-")
 ast.parse(text);return text


def prepare(destination,build):
 if build not in PARENTS:raise ValueError('unknown candidate')
 dest=Path(destination).resolve();parent,expected=PARENTS[build]
 if dest.exists():raise ValueError('fresh disabled package required')
 if sha(parent/'source-manifest.json')!=expected:raise ValueError('parent manifest changed')
 m=json.loads((parent/'source-manifest.json').read_text())
 if m['runtime_reviewed']is not False or m['comparison']['arm']!=build:raise ValueError('disabled matched parent only')
 for key,relative in [('runtime_dependencies',False),('sources',True),('draft_source_sha256',True)]:
  for name,h in m[key].items():
   if sha(parent/name if relative else name)!=h:raise ValueError('parent closure changed:'+name)
 after=observer_config(EXPECTED_PATH.read_bytes());old=(parent/'run-a4.py').read_text();new=transform(old,build)
 shutil.copytree(parent,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ADDITIONS:shutil.copy2(Path(__file__).with_name(name),dest/name)
 (dest/'run-a4.py').write_text(new)
 (dest/'observer20-runtime.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='previous-disabled/run-a4.py',tofile='common-observer20/run-a4.py')))
 def mapped(name):
  path=Path(name);return dest/path.relative_to(parent)if path.is_relative_to(parent)else path
 m['runtime_dependencies']={str(mapped(n)):sha(mapped(n))for n in m['runtime_dependencies']}
 m['runtime_dependencies'][str(dest/'navigation_observer20.py')]=sha(dest/'navigation_observer20.py')
 m.update(scope='DISABLED_MATCHED_NAV20_'+build+'_RED600_V3',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['comparison']=dict(m['comparison'],observer_fps=20,observer_startup_before_sha256=BEFORE_SHA256,observer_startup_after_sha256=hashlib.sha256(after).hexdigest(),fps_actual_measured=False,
  parent_manifest_sha256=expected,prior048_result_sha256='543b31cefe6183b7435ceb114e7d6dc570eaa76049944913c2d0539a34beab2c',prior048_status='FAIL_REMAINS_UNCHANGED',cross_condition_samples_combined=False)
 m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,reference='PENDING Root independent review/freeze')
 names=set(m['sources'])|set(ADDITIONS)|{'observer20-runtime.diff'}
 m['sources']={name:sha(dest/name)for name in sorted(names)}
 m['draft_source_sha256']={p.name:sha(p)for p in dest.glob('*.py')}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 receipt=dict(package=str(dest),build=build,manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),native_started=False,qualified=False)
 (dest/'HANDOFF-disabled.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);p.add_argument('--build',choices=tuple(PARENTS),required=True)
 args=p.parse_args();print(json.dumps(prepare(args.destination,args.build)))
