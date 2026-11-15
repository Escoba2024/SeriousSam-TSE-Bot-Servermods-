"""Current disabled035 Trouble300/D1 -> one disabled035 Yodeller600/D0."""
import argparse,ast,copy,difflib,json,os,struct,zipfile,zlib
from pathlib import Path
import prepare_navigation_build035_trouble as prior
from prepare_navigation_build031_hole import inventory,verify_pins,write
from prepare_navigation_build030_skulls import read,sha,load,opened

PARENT=Path('/srv/tse-nav20-035-trouble300-diag1-disabled-20261115')
PARENT_SHA='4116f85a964b36ff93adad98dce9c728aa8464148558b3bbe78346db0c3dfd76'
DESTINATION=Path('/srv/tse-nav20-035-yodeller600-diag0-disabled-v2-20261115')
CATALOG_SHA='11fc9080480dfa23cf0fc1f117a486b8f785daefbdeeb53dce26797c644018c3'
TRANSACTION='d6c76f6f1263a3c719b1200442b6e6b1a8d9e23506b6d5f3e71b23a095b41978'
BACKEND='51c25f2fcf6232bbc4bd4e05d08762f6edae9e97ab7a2064f4d9a9f860e884cb'
YODELLER=dict(query_name='Yodeller',world_path='Levels\\LevelsMP\\Deathmatch\\Yodeller.wld',world_sha256='80c318868ceace921cd35feaf8002e3ebc25aef3e93cf8bad220816a510b28ef',world_crc32='b3c8ceeb',nav_path='Scripts/Cecil/Yodeller_FC72665B.nav',nav_sha256='adc56723662da0107dd777bfaacb78f5561bf43bc43da476b82af300436d5c41',nav_crc32='a4a7950c',cecil_path_hash='fc72665b',nodes=111,private_nav_source='/srv/tse-cecil-full-private-assets-20261107/Yodeller_FC72665B.nav')
CHANGED=('run-a4.py','adapter_policy.py','a4_hard_map_policy.py')
ADDITIONS=('prepare_navigation_build035_yodeller.py','navigation_build035_yodeller_policy.py')
DELTAS={
 'run-a4.py':[("PREFIX=f'ssam-nav20-035-trouble300-diag1-hard-ordered-","PREFIX=f'ssam-nav20-035-yodeller600-diag0-hard-ordered-"),
  ("E=BASE/f'nav20-035-trouble300-diag1-hard-ordered-","E=BASE/f'nav20-035-yodeller600-diag0-hard-ordered-"),
  ('PRIVATE A4 035 HARD DIAGNOSTIC','PRIVATE A4 035 HARD YODELLER OBSERVATION'),
  ('Private candidate035 LittleTrouble300 diagnostic observation only','Private candidate035 Yodeller600 observation only'),
  ("choices=('trouble',)","choices=('yodeller',)"),
  ("parser.add_argument('--seconds',type=float,default=300)","parser.add_argument('--seconds',type=float,default=600)"),
  ("parser.add_argument('--diagnostics',type=int,choices=(1,),default=1)","parser.add_argument('--diagnostics',type=int,choices=(0,),default=0)")],
 'adapter_policy.py':[('from navigation_build035_trouble_policy import options as validate','from navigation_build035_yodeller_policy import options as validate')],
 'a4_hard_map_policy.py':[("need(map_key in catalog,'existing allowlisted map required')","need(map_key=='yodeller'and map_key in catalog,'fixed Yodeller in existing catalog required')"),
  ("duration==300,'fixed300s diagnostic window'","duration==600,'fixed600s Yodeller window'"),
  ("diag==1,'fixed diagnostics1'","diag==0,'fixed diagnostics0'")],
}

def apply(name,text,reverse=False):
    if name not in DELTAS:raise ValueError('three exact changed Sources only')
    original=read(PARENT/name).decode()
    if not reverse and text!=original:raise ValueError('whole exact current035 Parent Source required')
    for a,b in (reversed(DELTAS[name])if reverse else DELTAS[name]):
        if reverse:a,b=b,a
        if text.count(a)!=1 or(not reverse and b in text):raise ValueError('unique exact retarget anchor required')
        text=text.replace(a,b,1)
    ast.parse(text)
    if reverse and text!=original:raise ValueError('whole Source inverse differs')
    return text

def validate_parent():
    if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('exact current035 Parent manifest required')
    m=load(PARENT/'source-manifest.json');c=m['comparison'];p=m['map_case']
    if (any(m[k]is not False for k in ['runtime_reviewed','runtime_performed','qualified','functional_pass'])or
        (c['arm'],c['order'],c['map'],c['seconds'],c['diagnostics'],c['hard_difficulty'],c['observer_fps'])!=('035',['035'],'trouble',300,1,2,20)or
        (p['map'],p['seconds'],p['diagnostics'],p['bot_count'],p['bot_tier'],p['original_observer_fps'])!=('trouble',300,1,8,3,20)or
        any(x[k]is not False for x in (c,p)for k in ['automatic_retry','automatic_sequence','native_started'])or
        sha(PARENT/'transaction.py')!=TRANSACTION or sha(PARENT/'strict_backend.py')!=BACKEND or
        sha(PARENT/'map-catalog.json')!=CATALOG_SHA):raise ValueError('current Parent conditions/safety bytes required')
    verify_pins(m,PARENT);pins=prior.validate_build(load(prior.BUILD/'manifest.json'))
    if {p:h for p,h in m['runtime_dependencies'].items()if Path(p).is_relative_to(prior.BUILD)}!=pins:raise ValueError('all81 same035 hashVALUES required')
    if m['candidate']['dll_sha256']!=prior.DLL_SHA or m['candidate']['build_manifest_sha256']!=prior.BUILD_SHA:raise ValueError('same actual035 candidate required')
    return m,pins

def validate_assets(c):
    if c['maps']['yodeller']!=YODELLER:raise ValueError('exact Yodeller binding required')
    with opened(c['archive_readonly_source'])as source,zipfile.ZipFile(source)as z:world=z.read(YODELLER['world_path'].replace('\\','/'))
    nav=read(YODELLER['private_nav_source'])
    for raw,kind in [(world,'world'),(nav,'nav')]:
        import hashlib
        if hashlib.sha256(raw).hexdigest()!=YODELLER[kind+'_sha256']or f'{zlib.crc32(raw):08x}'!=YODELLER[kind+'_crc32']:raise ValueError('selected Yodeller asset mismatch')
    if struct.unpack_from('<4s4i',nav)[0:2]!=(b'BNMV',6)or struct.unpack_from('<i',nav,16)[0]!=111:raise ValueError('selected Nav header/nodes')
    return dict(map='yodeller',world_sha256=YODELLER['world_sha256'],nav_sha256=YODELLER['nav_sha256'],nodes=111,loaded_world_proven=False,archive_full_hash_recomputed=False)

def prepare(destination=DESTINATION):
    dest=Path(destination).resolve()
    if dest.exists()or any(dest.is_relative_to(p)for p in [PARENT,prior.BUILD]):raise ValueError('fresh independent disabled package required')
    m,pins=validate_parent();assets=validate_assets(load(PARENT/'map-catalog.json'));before=inventory(PARENT)
    changed={n:apply(n,read(PARENT/n).decode())for n in CHANGED}
    if any(apply(n,t,True).encode()!=read(PARENT/n)for n,t in changed.items()):raise ValueError('whole three-source inverse')
    if 'RUNTIME_REVIEWED=False'not in changed['run-a4.py']:raise ValueError('author Gate must remainFalse')
    additions={n:read(Path(__file__).with_name(n))for n in ADDITIONS}
    diffs={n+'.035yodeller.diff':''.join(difflib.unified_diff(read(PARENT/n).decode().splitlines(True),t.splitlines(True),fromfile='current035Trouble300D1/'+n,tofile='disabled035Yodeller600D0/'+n)).encode()for n,t in changed.items()}
    bound=sum((PARENT/n).stat().st_size for n in before)+sum(map(len,additions.values()))+sum(map(len,diffs.values()))+2**20
    v=os.statvfs(dest.parent)
    if v.f_bavail*v.f_frsize<2**33+2**26+bound:raise ValueError('8GiB+64MiB+bounded-copy reserve')
    dest.mkdir(mode=0o700)
    for n in before:
        if n not in ['source-manifest.json','HANDOFF-disabled.json']:write(dest/n,changed[n].encode()if n in changed else read(PARENT/n))
    for n,b in (additions|diffs).items():write(dest/n,b)
    deps={}
    for p,h in m['runtime_dependencies'].items():
        q=Path(p)
        if q.is_relative_to(PARENT):q=dest/q.relative_to(PARENT);h=sha(q)
        deps[str(q)]=h
    for n in ADDITIONS:deps[str(dest/n)]=sha(dest/n)
    inherited={k:copy.deepcopy(m[k])for k in ['comparison','map_case','root_review','observation_contract']}
    m['inherited_build035_trouble_condition_metadata']=dict(scope='HISTORICAL_CONDITION_ONLY_NOT_RUNTIME_ADMISSION',**inherited)
    m.update(scope='DISABLED_SINGLE_BUILD035_YODELLER600_DIAG0_WITH_NS_TIMESTAMP_RESTORE',runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,runtime_dependencies=deps)
    m['comparison']=dict(inherited['comparison'],map='yodeller',seconds=600,diagnostics=0,parent_manifest_sha256=PARENT_SHA,profile_semantics='MAP_FUNCTION_OBSERVATION_ONLY_NO_COMPARISON')
    m['map_case']=dict(inherited['map_case'],map='yodeller',map_binding=YODELLER,parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,seconds=600,diagnostics=0,assets=assets,scope='current candidate map observation only; special transitions and functional qualification require separate closed audit')
    m['observation_contract']=dict(inherited['observation_contract'],seconds=600,new_condition=True)
    m['build035_yodeller_derivation']=dict(parent=str(PARENT),parent_manifest_sha256=PARENT_SHA,explicit_delta=dict(map=['trouble','yodeller'],seconds=[300,600],diagnostics=[1,0]),build_targets_unchanged=pins,whole_three_source_inverse=True,automatic_retry=False,automatic_sequence=False,native_started=False,historical024_asset_reference_manifest='60186c5f4a572ddc5b59a22b210edafcee6a4b7b875ebfe49067cd4456c16778',current_timestamp_and_backend_preserved=True,options_correction='Actual second production hardmap options fixed300D1; v2 explicitly Yodeller600D0; old failedD/F preserved')
    m['root_review']=dict(approved_for_private_a4=False,approved_for_private_nav_comparison=False,approved_for_private_supply_diagnostic=False,reference='PENDING Root review/freeze for one035Yodeller600diag0 condition')
    m['sources']={n:sha(dest/n)for n in sorted(set(m['sources'])|set(ADDITIONS)|set(diffs))}
    m['draft_source_sha256']={p.name:sha(p)for p in sorted(dest.glob('*.py'))}
    write(dest/'source-manifest.json',(json.dumps(m,indent=2)+'\n').encode());verify_pins(m,dest)
    if inventory(PARENT)!=before:raise ValueError('immutable Parent changed')
    equal={n:h for n,h in before.items()if n not in ['source-manifest.json','HANDOFF-disabled.json']and n not in CHANGED}
    if any(sha(dest/n)!=h for n,h in equal.items()):raise ValueError('other Parent bytes differ')
    if {p:h for p,h in deps.items()if Path(p).is_relative_to(prior.BUILD)}!=pins:raise ValueError('81actual035 pins changed')
    result=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),controller_sha256=sha(dest/'run-a4.py'),parent_manifest_sha256=PARENT_SHA,build='035',map='yodeller',seconds=600,diagnostics=0,runtime_pins=len(deps),source_pins=len(m['sources']),python_pins=len(m['draft_source_sha256']),build_pins=81,other_parent_files_byte_equal=len(equal),whole_three_source_inverse=True,runtime_reviewed=False,runtime_performed=False,qualified=False,functional_pass=False,automatic_retry=False,automatic_sequence=False)
    write(dest/'HANDOFF-disabled.json',(json.dumps(result,indent=2)+'\n').encode())
    if sum(p.stat().st_size for p in dest.rglob('*')if p.is_file())>bound:raise ValueError('bounded copy size exceeded')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,default=DESTINATION)
    print(json.dumps(prepare(p.parse_args().destination),indent=2))
