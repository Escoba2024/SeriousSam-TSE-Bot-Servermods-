"""Pure exact-source cgroup exit patch for the two reviewed A1 backends.

Does not import a runtime backend, inspect live cgroups or execute services.
"""
import ast
import hashlib

PARENT_SHAS = frozenset({
    'fb759339e7de8b31dd0fc490a0f3152be78a00d9e13f0ecb39443bc7cf7f8c1c',
    '13394a9cb3a69d081f9071861d36a5663367995e4b62c00738d6c4e869ef121a',
})
BEFORE = """ def empty(self,unit):
  p=Path('/sys/fs/cgroup/system.slice')/unit/'cgroup.procs';return not p.exists()or not p.read_text().strip()
"""
AFTER = """ def empty(self,unit):
  p=Path('/sys/fs/cgroup/system.slice')/unit/'cgroup.procs'
  try:return not p.read_text().strip()
  except FileNotFoundError as error:
   if error.filename!=str(p):raise
   return not p.exists()
"""

def digest(source):
    return hashlib.sha256(source.encode()).hexdigest()

def transform(source):
    if digest(source) not in PARENT_SHAS or source.count(BEFORE) != 1:
        raise ValueError('exact full A1 parent backend required')
    result = source.replace(BEFORE, AFTER, 1)
    ast.parse(result)
    return result

def reverse(source):
    if source.count(AFTER) != 1:
        raise ValueError('exact patched empty method required')
    result = source.replace(AFTER, BEFORE, 1)
    if digest(result) not in PARENT_SHAS:
        raise ValueError('whole A1 parent inverse changed')
    ast.parse(result)
    return result
