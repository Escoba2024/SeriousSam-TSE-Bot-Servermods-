"""Exact source-only timestamp extension; frozen transactions stay unchanged."""
import ast
import hashlib
import os

PARENT_SHA='6fd1825b1bfda8713b8669f01ea3ab4cb5747c2084c338575fb0b0dbbf5c5dfb'
PAIRS=[
 ("self.records[key]={'existed':True,'backup':str(backup),'sha256':digest,'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid}",
  "self.records[key]={'existed':True,'backup':str(backup),'sha256':digest,'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid,'atime_ns':st.st_atime_ns,'mtime_ns':st.st_mtime_ns}"),
 ("     restored[relative]=record['sha256']",
  "     os.utime(p,ns=(record['atime_ns'],record['mtime_ns']))\n     times=p.stat()\n     if (times.st_atime_ns,times.st_mtime_ns)!=(record['atime_ns'],record['mtime_ns']):raise ValueError('restored timestamps differ')\n     restored[relative]=record['sha256']"),
]

def digest(source):return hashlib.sha256(source.encode()).hexdigest()

def transform(source):
 if digest(source)!=PARENT_SHA:raise ValueError('exact full parent transaction required')
 for before,after in PAIRS:
  if source.count(before)!=1:raise ValueError('exact unique timestamp source anchor required')
  source=source.replace(before,after,1)
 ast.parse(source);return source

def reverse(source):
 for before,after in reversed(PAIRS):
  if source.count(after)!=1:raise ValueError('exact unique timestamp inverse required')
  source=source.replace(after,before,1)
 if digest(source)!=PARENT_SHA:raise ValueError('whole parent transaction inverse differs')
 ast.parse(source);return source


def read_bytes_noatime(path):
 """Independent verification must not undo the restored access timestamp."""
 flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_NOATIME
 with os.fdopen(os.open(path,flags),'rb')as stream:return stream.read()
