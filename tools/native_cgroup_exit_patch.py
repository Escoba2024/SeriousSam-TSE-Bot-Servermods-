"""Exact disabled backend-only patch; no process, service or signal execution."""
import ast
import hashlib

PARENT_SHA='b4d57b35ce54f74185e3d891c17676a374ab3e892e148400a0a6ac712a9a1158'
BEFORE=""" def empty(self,unit):
  p=Path('/sys/fs/cgroup/system.slice')/unit/'cgroup.procs';return not p.exists()or not p.read_text().strip()
"""
AFTER=""" def empty(self,unit):
  p=Path('/sys/fs/cgroup/system.slice')/unit/'cgroup.procs'
  try:return not p.read_text().strip()
  except FileNotFoundError as error:
   if error.filename!=str(p):raise
   return not p.exists()
"""

def digest(source):return hashlib.sha256(source.encode()).hexdigest()

def transform(source):
 if digest(source)!=PARENT_SHA or source.count(BEFORE)!=1:
  raise ValueError('exact full parent backend required')
 result=source.replace(BEFORE,AFTER,1);ast.parse(result);return result

def reverse(source):
 if source.count(AFTER)!=1:raise ValueError('exact new empty method required')
 result=source.replace(AFTER,BEFORE,1)
 if digest(result)!=PARENT_SHA:raise ValueError('whole parent inverse changed')
 ast.parse(result);return result
