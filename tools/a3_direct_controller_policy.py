"""Thin private-package adapter; inherited policy owns all initial/restore rules."""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
def local(name):
    spec=importlib.util.spec_from_file_location('direct_'+name+'_'+str(id(HERE)),HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

inherited=local('controller_policy')
direct=local('a3_direct_tiers')
CANDIDATE_SHA='094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0'
PUBLIC_SHA=inherited.PUBLIC_SHA  # Retained unused artifact pin; never deployed.
INERT_KEYS=inherited.INERT_KEYS
InitialObservations=inherited.InitialObservations
assignments=inherited.assignments
bootstrap=inherited.bootstrap
checked_bytes=inherited.checked_bytes
require=inherited.require
slot_mapping=inherited.slot_mapping

def cohort(role,lower,swap,diag):
    raw=direct.configuration(inherited.load_source('candidate'),role,lower,swap,diag)
    tier=direct.tiers(lower,swap)[role]
    return dict(candidate=True,tier=tier,tier_name=direct.NAMES[tier],
                config=raw,config_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                config_base_sha256=hashlib.sha256(direct.without_tier(raw).encode()).hexdigest(),
                game_sha256=CANDIDATE_SHA)

def build_direct_registry(damage,rows,mapping,cohorts):
    return direct.registry(damage.build_registry,rows,mapping,cohorts)

def hard_server_template(raw):
    """Change only an existing literal difficulty2/3 to2; reject other rules drift."""
    import re
    expected={'gam_iFragLimit':'0','gam_iTimeLimit':'0','gam_bInfiniteAmmo':'1',
              'gam_iBlood':'3','gam_bGibs':'0'}
    for key,value in expected.items():
        matches=list(re.finditer(r'(?m)^[ \t]*'+key+r'[ \t]*=[ \t]*([^;\r\n]+);[ \t]*$',raw))
        require(len(matches)==1 and matches[0][1].strip()==value,'unexpected existing Hard-template rule '+key)
    matches=list(re.finditer(r'(?m)^([ \t]*gam_iStartDifficulty[ \t]*=[ \t]*)([^;\r\n]+)(;[ \t]*)$',raw))
    require(len(matches)==1 and matches[0][2].strip()in('2','3'),'one existing difficulty2/3 required')
    match=matches[0]
    return raw[:match.start(2)]+'2'+raw[match.end(2):]

def check_actual_tiers(logs,cohorts):
    import re
    result={}
    for role in ('botA','botB'):
        rows=re.findall(r'^\[BotHuman\] local=(\d+) profile=(\S+) tier=(\d+) persona=(\S+) seed=(\d+) model=arena-v1\s*$',logs[role],re.M)
        require(rows and {int(r[0])for r in rows}==set(range(4)),'all actual local profiles required')
        require(all(name==cohorts[role]['tier_name']and int(tier)==cohorts[role]['tier']and persona=='duelist'
                    for local,name,tier,persona,seed in rows),'actual role tier mismatch')
        result[role]=[dict(local=int(i),profile=name,tier=int(tier),persona=persona,seed=int(seed))
                      for i,name,tier,persona,seed in rows]
    return result
