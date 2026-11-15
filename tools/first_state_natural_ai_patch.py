"""Exact, reversible three-source NaturalAI030 condition. Never enables a gate."""
import ast
import hashlib

PARENT_SHA={'run_dual.py':'9bbc7b8d567f34367a84fabd0d05d2af964651f1c3151a5d6e7a40a1da099d5c',
            'method-api/native_first_state.py':'8907a3fcf03ec2c48f950ff66fe2f17ca2e58f8da3278d32dee4a4915ec19421',
            'first_state_inputfree_method.py':'6ccbb966634f922e9d63d6191e91fd513fd18541d0e87ab83667c91b810ff0f8'}
DELTAS={
'first_state_inputfree_method.py':[
 ("'PASS_LIMITED_UNINSTRUMENTED_TWO_ORIGINALS_ONLY'","'PASS_LIMITED_UNINSTRUMENTED_NATURAL_AI030_ORIGINAL_VICTIM_ONLY'")],
'run_dual.py':[
 ('import first_state_initial_geometry_patch as IGR','import first_state_initial_geometry_patch as IGR\nimport first_state_natural_ai as NAI'),
 ("pins[role]=B.pin_modules(role,receipt.identity,P.ORIGINALS['GameMP.dll'])","pins[role]=B.pin_modules(role,receipt.identity,NAI.game_sha(role))"),
 ("   transaction.seal()","   NAI.snapshot_targets(transaction)\n   transaction.seal()"),
 ("   for role in ('server','botA'):shutil.copy2(R/'vanilla/Bin/GameMP.dll',R/role/'Bin/GameMP.dll');os.chown(R/role/'Bin/GameMP.dll',65534,65534)",
  "   for role in ('server',):shutil.copy2(R/'vanilla/Bin/GameMP.dll',R/role/'Bin/GameMP.dll');os.chown(R/role/'Bin/GameMP.dll',65534,65534)"),
 ("   for n in (154,155):\n    displays[n]", "   report['natural_ai_staging']=NAI.stage_candidate(transaction,R,DRAFT,E);save()\n   for n in (154,155):\n    displays[n]"),
 ("    return frame\n", "    own_identity('botA')\n    frame['natural_ai_ownership']=NAI.capture_ownership(R,E,frame,records,pins,mapping,entity_ids,report['natural_ai_staging'])\n    own_identity('botA')\n    return frame\n")],
'method-api/native_first_state.py':[
 ('from source_loader import observer_policy','from source_loader import observer_policy\nimport first_state_natural_ai as NAI'),
 ('def build_identity(read,host,bases,registry,epoch):','def build_identity(read,host,bases,registry,epoch,*,actor_roles):'),
 (" g=observer_policy().BINDINGS\n require(set(host)"," g=observer_policy().BINDINGS\n require(actor_roles=={'vanilla':'vanilla','botA':'bot'},'strict proven NaturalAI roles required')\n require(set(host)"),
 ("players.append({'id':row['id'],'pointer':row['pointer'],'role':'vanilla'})","players.append({'id':row['id'],'pointer':row['pointer'],'role':actor_roles[role]})"),
 (' def __init__(self,frame,records,pins,host_guard,evidence):\n  self.host_guard',
  ' def __init__(self,frame,records,pins,host_guard,evidence):\n  self.actor_roles=NAI.roles_from_receipt(frame,records,pins)\n  self.host_guard'),
 ('build_identity(self.read,self.host,self.bases,self.registry,self.evidence.name)',
  'build_identity(self.read,self.host,self.bases,self.registry,self.evidence.name,actor_roles=self.actor_roles)')]
}
COUNTS={('method-api/native_first_state.py',5):3}


def _apply(name,source,reverse=False):
    if name not in DELTAS:raise ValueError('exact three condition sources only')
    pairs=list(enumerate(DELTAS[name]))
    for index,(before,after)in reversed(pairs)if reverse else pairs:
        a,b=(after,before)if reverse else(before,after)
        if source.count(a)!=COUNTS.get((name,index),1):raise ValueError('unique exact NaturalAI fragment required: '+a)
        source=source.replace(a,b)
    ast.parse(source)
    return source


def transform(name,source):
    if hashlib.sha256(source.encode()).hexdigest()!=PARENT_SHA.get(name):raise ValueError('exact disabled V4 parent source required')
    result=_apply(name,source)
    if reverse(name,result)!=source:raise ValueError('NaturalAI whole-source inverse')
    return result


def reverse(name,source):
    result=_apply(name,source,True)
    if hashlib.sha256(result.encode()).hexdigest()!=PARENT_SHA[name]:raise ValueError('NaturalAI whole-source parent hash mismatch')
    return result
