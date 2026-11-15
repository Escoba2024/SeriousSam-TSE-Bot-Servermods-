"""Offline exact030 NaturalAI fork. Never launches, freezes or enables a gate.

Root invokes prepare only after independent review and storage clearance. The
public tests exercise pure planning and actual parent transformations, not an
unobserved runtime or a large generated fork.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import first_state_natural_ai as N
import first_state_natural_ai_patch as patch
from navigation_build030_skulls_policy import EXPECTED_SOURCES,EXPECTED_OVERLAY

PARENT=Path('/srv/tse-a1-first-state-qjs10-v4-disabled-20261115')
PARENT_SHA='b516240b2c360255b425f3ed40423c21a255ca625c1eb02863307c9c45320368'
BUILD=Path('/srv/tse-milestone-a-build-030-20261115')
BUILD_SHA='89eef08dfce8f2b5f40fba0290e5778bdb42831c7280731ad5cd44c21338a5d3'
SOURCE_COMMIT='7aedcdb21f7180b9abfeed2ea9e8bbbf5553564e'
SOURCE_TREE='e48736240423b15d0d31af8508418b9dae8e1ae3'
ASSETS=Path('/srv/tse-a4-build030-hard-reset-v3-timestamps-disabled-20261115')
CANONICAL_SHA='9f2dfea816c3bd4d3ca0de9f3d09c2e457c208a3b50e5765575c9d0c888e465a'
BASE_CONFIG_SHA='e23c8b6802c4bfbb10079c68ca737b85587391acef79f44452941b8051d40c9a'
SOURCES=('first_state_natural_ai.py','first_state_natural_ai_patch.py','prepare_first_state_natural_ai.py',
         'test_first_state_natural_ai.py','test_first_state_natural_ai_patch.py','test_prepare_first_state_natural_ai.py',
         'navigation_build030_skulls_policy.py')

def digest(data):return hashlib.sha256(data).hexdigest()
def read(path):return N.read_bytes(path,16*1024*1024)
def sha_file(path):
    with os.fdopen(os.open(Path(path).resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as stream:
        before=os.fstat(stream.fileno());h=hashlib.sha256()
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
        after=os.fstat(stream.fileno())
    require(stat.S_ISREG(before.st_mode)and(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_atime_ns)==
            (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_atime_ns),'stable no-atime source read')
    return h.hexdigest()
def load(path):return json.loads(read(path))
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def require(ok,message):
    if not ok:raise ValueError(message)

def changed_sources(sources):
    require(set(sources)==set(patch.PARENT_SHA),'exact three parent sources')
    result={n:patch.transform(n,v.decode()).encode()for n,v in sources.items()}
    require(all(patch.reverse(n,v.decode()).encode()==sources[n]for n,v in result.items()),'whole inverse')
    return result

def active_config(base,canonical):
    require(digest(base)==BASE_CONFIG_SHA and digest(canonical)==CANONICAL_SHA,'exact active script and030canonical')
    for line in (b'sam_iMaxFPSActive=10;\n',b'sam_iMaxFPSInactive=10;\n'):
        require(base.count(line)==1,'one exact original FPS assignment');base=base.replace(line,b'')
    result=base+canonical
    require(digest(result)==N.ACTIVE_CONFIG_SHA,'exact active combined script')
    return result

def repin(pins,old,new,files):
    result={}
    for name,pin in pins.items():
        path=Path(name)
        if path.is_relative_to(old):
            relative=str(path.relative_to(old));require(relative in files,'pinned copied file absent: '+relative)
            name=str(new/relative);pin=digest(files[relative])
        require(name not in result,'duplicate rebased pin');result[name]=pin
    return result

def helper_files(source):
    files={name:read(Path(source)/name)for name in SOURCES}
    # FreshExec starts with method-api, not the Runner's script root. The two
    # imports must resolve identical policy bytes; no sys.path monkeypatch.
    files['method-api/first_state_natural_ai.py']=files['first_state_natural_ai.py']
    return files

def same_gates(before,after):
    expression=rb'^\s*(?:const )?RUNTIME_REVIEWED\s*=\s*(?:True|true|False|false)\b'
    require(re.findall(expression,before,re.M)==re.findall(expression,after,re.M),'exact inherited code gate fingerprint')

def build_pins():
    require(digest(read(BUILD/'manifest.json'))==BUILD_SHA,'exact030 build manifest')
    m=load(BUILD/'manifest.json')
    require(m['build_ok']is True and m['qualified']is False and m['repo_commit']==SOURCE_COMMIT and m['repo_tree']==SOURCE_TREE,
            'exact unqualified030 source provenance')
    require(m['source_sha256']==EXPECTED_SOURCES and m['overlay_sha256']==EXPECTED_OVERLAY and m['dll_sha256']==N.BOT_GAME,
            'full030 source/overlay expected values')
    result={str(BUILD/'manifest.json'):BUILD_SHA,str(N.DLL_SOURCE):N.BOT_GAME}
    for key,sub in (('source_sha256','Sources/Game'),('overlay_sha256','overlay')):
        for name,pin in m[key].items():result[str(BUILD/sub/name)]=pin
    require(len(result)==79 and len(read(N.DLL_SOURCE))==454144,'exact79 build targets and DLL size')
    for path,pin in result.items():require(digest(read(path))==pin,'build target changed: '+path)
    return result

def prepare(destination):
    """Only Root calls this after review/storage clearance. All writes are fresh."""
    dest=Path(destination).resolve();source=Path(__file__).resolve().parent
    require(not dest.exists()and not dest.is_relative_to(PARENT)and not dest.is_relative_to(BUILD),'fresh separate destination')
    require(digest(read(PARENT/'source-manifest.json'))==PARENT_SHA,'exact disabled V4 parent')
    m=load(PARENT/'source-manifest.json')
    require(m['runtime_reviewed']is False and m['native_ready']is False and m['native_qualified']is False,'disabled unqualified parent')
    # Original fixture preflight pins remain byte-for-byte; only active package
    # dependencies are freshly checked, not rebaselined to whatever is present.
    for path,pin in m['runtime_dependencies'].items():require(sha_file(path)==pin,'parent runtime dependency changed: '+path)
    pins=build_pins()
    require(digest(read(N.NAV_SOURCE))==N.NAV_SHA,'exact Red Nav')
    files={str(p.relative_to(PARENT)):read(p)for p in sorted(PARENT.rglob('*'))
           if p.is_file()and '__pycache__'not in p.parts and p.suffix!='.pyc'}
    original_files=dict(files)
    files.update(changed_sources({name:files[name]for name in patch.PARENT_SHA}))
    oldprefix="PREFIX='ssam-a1-first-state-autodrain-disabled-20261115'"
    newprefix="PREFIX='ssam-a1-natural-ai030-disabled-20261115'"
    runner=files['run_dual.py'].decode();require(runner.count(oldprefix)==1,'fixed parent service/evidence namespace')
    files['run_dual.py']=runner.replace(oldprefix,newprefix).encode()
    collector='collector/a1_original_input_collector.py';text=files[collector].decode()
    matches=re.findall(r'^PRIVATE = Path\([^\n]+\)$',text,re.M);require(len(matches)==1,'unused collector private path')
    files[collector]=text.replace(matches[0],f'PRIVATE = Path({str(dest/"collector")!r})').encode()
    files['natural-ai/active.ini']=active_config(files['CecilObserver.ini'],read(ASSETS/'canonical.ini'))
    for name,pin in (('maps.txt',N.MAPS_SHA),('settings.txt',N.SETTINGS_SHA)):
        files['natural-ai/'+name]=read(ASSETS/name);require(digest(files['natural-ai/'+name])==pin,'exact Red supply closure')
    sourcepins={};files.update(helper_files(source))
    for name in SOURCES:
        sourcepins[str(source/name)]=digest(files[name])
    for name,data in files.items():
        if name.endswith('.py'):ast.parse(data.decode())
        if name.endswith(('.py','.js')):
            same_gates(original_files.get(name,b''),data)
    cm=json.loads(files['collector/source-manifest.json']);cm['runtime_reviewed']=False
    cm['source_pins']=repin(cm['source_pins'],PARENT,dest,files)
    files['collector/source-manifest.json']=encoded(cm)
    nm=json.loads(files['method-api/source-manifest.json'])
    nm['runtime_dependencies']=repin(nm['runtime_dependencies'],PARENT,dest,files)
    nm['runtime_dependencies'][str(dest/'first_state_natural_ai.py')]=digest(files['first_state_natural_ai.py'])
    nm['runtime_dependencies'][str(dest/'method-api/first_state_natural_ai.py')]=digest(files['method-api/first_state_natural_ai.py'])
    nm.update(runtime_reviewed=False,qualified=False,native_qualified=False,first_processed_state_proven=False,
              ai_population_adapter=True,registry_actors=2,
              natural_ai_condition={'candidate':'030','ownership':'fresh Source local0 and discovered server entity, before bot label',
                                    'qualified':False,'original_game_rvas_transferred':False})
    files['method-api/source-manifest.json']=encoded(nm)
    m['runtime_dependencies']=repin(m['runtime_dependencies'],PARENT,dest,files)
    m['method_api']={'root':str(dest/'method-api'),'manifest_sha256':digest(files['method-api/source-manifest.json']),'runtime_reviewed':False}
    for name in SOURCES:m['runtime_dependencies'][str(dest/name)]=digest(files[name])
    m['runtime_dependencies'][str(dest/'method-api/first_state_natural_ai.py')]=digest(files['method-api/first_state_natural_ai.py'])
    for name in ('active.ini','maps.txt','settings.txt'):m['runtime_dependencies'][str(dest/'natural-ai'/name)]=digest(files['natural-ai/'+name])
    m['runtime_dependencies'].update(pins);m['runtime_dependencies'][str(N.NAV_SOURCE)]=N.NAV_SHA
    m.update(scope='DISABLED_NATURAL_AI030_TWO_ACTOR_CONDITION_NOT_A1_QUALIFICATION',runtime_reviewed=False,native_ready=False,
             native_qualified=False,first_processed_state_proven=False,prior_control_transfer_authorized=False,
             new_matched_control_required=True)
    m['natural_ai_parent_package']=dict(path=str(PARENT),manifest_sha256=PARENT_SHA)
    m['natural_ai_condition']={'source_pins':sourcepins,'parent_manifest_sha256':PARENT_SHA,'candidate':'030',
        'build_pins':pins,'roles':{'server':'Original','vanilla':'Original victim','botA':'030 AI shooter'},
        'game_actors':2,'os_roles':3,'victim_fps':10,'bot_fps':20,'bot_local_count':1,'bot_profile':7,'tier':3,'persona':'duelist',
        'config_sha256':N.ACTIVE_CONFIG_SHA,'nav_sha256':N.NAV_SHA,'snapshots_before_seal':list(N.TARGETS),
        'inputs':0,'runtime_performed':False,'ownership_native_qualified':False,'first_state_proven':False,
        'bot_victim_proven':False,'prearm_ai_damage_may_abort':True,'earlier_init_left_censored':True,
        'guard_deadline_or_js_changes':False,'fresh_declared_control_and_trace_required':True,
        'control_status':'PASS_LIMITED_UNINSTRUMENTED_NATURAL_AI030_ORIGINAL_VICTIM_ONLY',
        'control_status_literal_only_correction':True}
    files['source-manifest.json']=encoded(m)
    total=sum(map(len,files.values()));available=os.statvfs(dest.parent).f_bavail*os.statvfs(dest.parent).f_frsize
    require(available>=8*1024**3+64*1024**2+total,'8GiB plus64MiB and complete output reserve')
    dest.mkdir(mode=0o700)
    for name,data in files.items():
        path=dest/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:
            f.write(data);f.flush();os.fsync(f.fileno())
    return {'destination':str(dest),'manifest_sha256':digest(files['source-manifest.json']),
            'runtime_pins':len(m['runtime_dependencies']),'nested_pins':len(nm['runtime_dependencies']),
            'collector_pins':len(cm['source_pins']),'build_pins':len(pins),'bytes_written':total,
            'runtime_reviewed':False,'native_ready':False,'qualified':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    print(json.dumps(prepare(parser.parse_args().output),sort_keys=True,indent=2))
