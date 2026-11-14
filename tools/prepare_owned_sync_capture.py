"""Offline disabled018/Yodeller derivation; never starts a capture or game."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT=Path('/srv/tse-a4-build020-hard-ordered-memory-root-frozen-20261114')
PARENT_SHA='56f4c319551459d5c7a201d82ee75f03641232ec33d29eca7e2f86b71390fb65'
BUILD=Path('/srv/tse-milestone-a-build-018-20261112')
BUILD_SHA='f4212443317b58b04808bd42d084e6a3286e458af2c0dbcfb276aa3bca931c2e'
DLL='6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a'
SOURCE='1802fb3f0720b53feb032abfe2c2a83407bfea6e'
OLD_BUILD=Path('/srv/tse-milestone-a-build-020-20261114')
ADDITIONS=('owned_sync_capture.py','owned_capture_exec.py','prepare_owned_sync_capture.py','test_owned_sync_capture.py','test_prepare_owned_sync_capture.py','analyze_retail_sync_pcap.py','test_analyze_retail_sync_pcap.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(s,old,new):
 if s.count(old)!=1:raise ValueError('nonunique reviewed parent anchor '+old)
 return s.replace(old,new,1)


def transform(s):
 s=once(s,'from host_budget import HostBudget','from host_budget import HostBudget\nfrom owned_sync_capture import OwnedSyncCapture')
 s=once(s,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
 s=once(s,str(OLD_BUILD/'Sources/Game/GameMP.dll'),str(BUILD/'Sources/Game/GameMP.dll'))
 s=once(s,'policy.options(map_key,duration,diag);',"assert map_key=='yodeller' and duration==600 and diag==0,'fixed018/Yodeller600sHard2diag0 protocol'\n policy.options(map_key,duration,diag);")
 s=once(s,"PREFIX=f'ssam-a4-020-hard-root-ordered-{map_key}-20261114'","PREFIX='ssam-own-sync018-yodeller-20261114'")
 s=once(s,"E=BASE/f'a4-020-hard-ordered-{map_key}-","E=BASE/f'own-sync018-yodeller-")
 s=once(s,'records={};display=None','records={};capture=None;display=None')
 anchor="   sample_host('before-release')\n   control('key','Pause',.1)"
 s=once(s,anchor,"""   capture=OwnedSyncCapture(E,{r:{'identity':list(rec['identity']),'unit':unit(r)}for r,rec in records.items()})
   capture.start()
   report['owned_sync_capture']=capture.receipt;save()
   sample_host('before-release')
   control('key','Pause',.1)""")
 s=once(s,'B.isolated_server(server[0]);last_pin=elapsed','B.isolated_server(server[0]);capture.guard();last_pin=elapsed')
 s=once(s,"   if time.monotonic()-host_budget.previous[0]>.05:sample_host('window-end')","""   capture.gameplay_complete()
   report['owned_sync_capture']=capture.close();save()
   if not report['owned_sync_capture'].get('protocol_complete'):report['errors'].append('sampled sync comparison incomplete or differing; no protocol PASS')
   if time.monotonic()-host_budget.previous[0]>.05:sample_host('window-end')""")
 s=once(s,"   was_raising=sys.exc_info()[0] is not None","""   was_raising=sys.exc_info()[0] is not None
   if capture is not None:
    try:report['owned_sync_capture']=capture.close()
    except BaseException as error:
     report['owned_sync_capture']=capture.receipt;report['errors'].append('capture cleanup:'+repr(error))""")
 # Archive executable addon source in the existing private evidence directory.
 s=once(s,"'audit_a4_ordered_memory_v3.py'):","'audit_a4_ordered_memory_v3.py','owned_sync_capture.py','owned_capture_exec.py','analyze_retail_sync_pcap.py'):")
 s=once(s,'Private A4 candidate020 Hard normal gameplay','Private018 own sync protocol, stationary Original, no qualification')
 s=once(s,'A4_NATIVE_OBSERVATION_REQUIRES_FUNCTIONAL_REVIEW','OWN_SAMPLED_SYNC_PROTOCOL_ONLY_REQUIRES_REVIEW')
 s=once(s,'PASS_LIMITED_A4_OBSERVATION_FUNCTIONAL_REVIEW_REQUIRED','PASS_LIMITED_OWN_SAMPLED_SYNC_PROTOCOL_REVIEW_REQUIRED')
 ast.parse(s);return s


def prepare(destination):
 dest=Path(destination).resolve()
 if dest.exists():raise ValueError('fresh destination required; old freezes stay immutable')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('reviewed single-map parent manifest')
 parent=json.loads((PARENT/'source-manifest.json').read_text())
 for p,h in parent['runtime_dependencies'].items():
  if sha(p)!=h:raise ValueError('parent runtime pin '+p)
 for p,h in parent['sources'].items():
  if sha(PARENT/p)!=h:raise ValueError('parent source pin '+p)
 if sha(BUILD/'manifest.json')!=BUILD_SHA:raise ValueError('018 build manifest pin')
 build=json.loads((BUILD/'manifest.json').read_text())
 if not(build['build_ok']is True and build['repo_commit']==SOURCE and build['dll_sha256']==DLL and sha(BUILD/'Sources/Game/GameMP.dll')==DLL):raise ValueError('018 candidate provenance')
 for key,base in [('source_sha256',BUILD/'Sources/Game'),('overlay_sha256',BUILD/'overlay')]:
  for p,h in build[key].items():
   if sha(base/p)!=h:raise ValueError('018 source pin '+p)
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 tools=Path(__file__).resolve().parent
 for name in ADDITIONS:shutil.copy2(tools/name,dest/name)
 old=(PARENT/'run-a4.py').read_text();new=transform(old);(dest/'run-a4.py').write_text(new)
 adapter=(PARENT/'adapter_policy.py').read_text();adapter=once(adapter,parent['candidate']['dll_sha256'],DLL);(dest/'adapter_policy.py').write_text(adapter)
 deps={}
 for p,h in parent['runtime_dependencies'].items():
  q=Path(p)
  if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT)
  elif q.is_relative_to(OLD_BUILD):q=BUILD/q.relative_to(OLD_BUILD)
  deps[str(q)]=sha(q)
 for name in('owned_sync_capture.py','owned_capture_exec.py','analyze_retail_sync_pcap.py'):deps[str(dest/name)]=sha(dest/name)
 for name in('/usr/bin/timeout','/usr/bin/tcpdump','/usr/bin/nsenter','/usr/bin/python3','/usr/bin/python3.12'):deps[name]=sha(name)
 m=json.loads(json.dumps(parent));m['inherited_capture_parent_metadata']={k:m[k]for k in('scope','derivation','root_review','root_freeze','sources','draft_source_sha256')}
 m.update(scope='DISABLED_OWN018_YODELLER_HARD600S_SAMPLED_SYNC_PROTOCOL_ONLY',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False)
 m['candidate']=dict(dll_sha256=DLL,source_commit=SOURCE,build_manifest=str(BUILD/'manifest.json'),build_manifest_sha256=BUILD_SHA)
 m['runtime_dependencies']=dict(sorted(deps.items()))
 m['derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,stationary_original=True,initial_handshake=False,duration_seconds=600,diagnostics=0,hard_difficulty=2,additional_inventory_reads=0,additional_inputs=0,frida_used=False,tc_used=False,independent_review='PENDING')
 m['capture']=dict(seconds=640,max_bytes=67108864,max_packets=250000,interface='lo',game_port=27850,protocol='first_differing_SAMPLED_synccheck_only',source_ports='actual own role FD-inode intersections, before outcomes',rotating_capture=False)
 m['root_review']=dict(approved_for_private_a4=False,reference='PENDING independent review, new Root freeze and preflight')
 m.pop('root_freeze',None)
 (dest/'owned-capture-parent.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='reviewed020singlemap',tofile='disabled018capture')))
 m['sources']={p.name:sha(p)for p in dest.iterdir()if p.is_file()and p.name not in('source-manifest.json','HANDOFF-capture.json')}
 m['draft_source_sha256']={p.name:sha(p)for p in dest.glob('*.py')}
 (dest/'source-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(deps),native_started=False)
 (dest/'HANDOFF-capture.json').write_text(json.dumps(dict(**receipt,qualified=False,runtime_authorized=False,next='independent review; Root freeze then one018/Yodeller600s protocol run, no auto retry'),indent=2)+'\n')
 return receipt


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',required=True,type=Path)
 print(json.dumps(prepare(p.parse_args().destination),indent=2))
