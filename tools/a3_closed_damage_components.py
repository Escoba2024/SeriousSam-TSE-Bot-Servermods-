"""Exact, hash-pinned extraction of existing offline validator blocks.

Only this trusted Python source is compiled, never evidence data/log text.
No legacy analyzer execution or result writes occur here.
"""
import ast
import copy
import hashlib
from pathlib import Path
import types

PARENT=Path('/srv/tse-a3-instruction-probe-root-frozen-20261114')
SOURCE=PARENT/'analyze-direct020.py'
SOURCE_SHA='4187020d0ceda1284bcaac3df9ccf98b251ec25863ae6947bd0aa6d96d33464a'


def tree(path=SOURCE):
 raw=Path(path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError('historical analyzer pin differs')
 return ast.parse(raw)


def blocks(path=SOURCE):
 module=tree(path);body=next(n.body for n in module.body if isinstance(n,ast.FunctionDef)and n.name=='analyze')
 def index(starts):
  found=[i for i,n in enumerate(body)if ast.unparse(n).startswith(starts)]
  if len(found)!=1:raise ValueError('nonunique exact historical block '+starts)
  return found[0]
 life_start=index('def useful(');source_start=index("for candidate_role in ('botA', 'botB'):")
 damage_start=index("f = R['frida_damage']");host_start=index("host = load(");report_start=index('report = dict(')
 matched=body[source_start].body[-1].body[-1].body
 return dict(preconditions=body[:life_start],derive_lives=body[life_start:source_start],
  matched_life=matched,damage=body[damage_start:host_start],host=body[host_start:report_start],condition=body[report_start+1:report_start+3])


SIGNATURES=dict(preconditions=('name','BASE'),derive_lives=('observations','slots','cohorts'),
 matched_life=('life','event','sp','index','events','local'),damage=('P','R','registry','names','cohorts','slots'),host=('P','R'),condition=('P','R','pol','hard','f','report'))
RETURNS=dict(preconditions='locals()',derive_lives='lives',matched_life='life',damage='locals()',host='(host, costs)',condition='report')


def render(path=SOURCE):
 original=tree(path);sections=blocks(path)
 helpers=[copy.deepcopy(n)for n in original.body if isinstance(n,(ast.Import,ast.ImportFrom))or isinstance(n,ast.FunctionDef)and n.name in('load','plain')or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='sha'for t in n.targets)]
 functions=[];witness={}
 for name,nodes in sections.items():
  body=copy.deepcopy(nodes)+[ast.Return(value=ast.parse(RETURNS[name],mode='eval').body)]
  fn=ast.FunctionDef(name=name,args=ast.arguments(posonlyargs=[],args=[ast.arg(arg=n)for n in SIGNATURES[name]],kwonlyargs=[],kw_defaults=[],defaults=[]),body=body,decorator_list=[])
  functions.append(fn);witness[name]=hashlib.sha256('\n'.join(ast.dump(n,include_attributes=False)for n in nodes).encode()).hexdigest()
 result=ast.fix_missing_locations(ast.Module(body=helpers+functions,type_ignores=[]))
 return ast.unparse(result)+'\n',dict(source_sha256=SOURCE_SHA,block_ast_sha256=witness)


def load_components():
 text,witness=render();module=types.ModuleType('a3_exact_closed_component_checks')
 exec(compile(text,'<hash-pinned offline A3 check blocks>','exec'),module.__dict__)
 return module,witness
