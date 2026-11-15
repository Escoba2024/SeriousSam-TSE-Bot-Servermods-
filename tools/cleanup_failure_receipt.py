"""Private bounded current-exception receipt; only the cleanup close-except calls it."""
import ast
import errno
import json
import os
from pathlib import Path
import stat
import traceback

ROLES=('vanilla','botB','botA','server')
MAX_BYTES=65536
MAX_FRAMES=32

class CleanupFailureReceipt:
 def __init__(self,path):
  self.path=Path(path);self.roles=set();self.signature=None;self.length=0;self.failed=False
 def record(self,role,error):
  if role not in ROLES or role in self.roles or len(self.roles)>=4:raise ValueError('one receipt per four own cleanup roles')
  if self.failed:raise ValueError('cleanup receipt previously failed')
  self.roles.add(role)
  fd=None
  try:
   frames=0;tb=error.__traceback__
   while tb is not None and frames<=MAX_FRAMES:frames+=1;tb=tb.tb_next
   if frames>MAX_FRAMES:raise ValueError('cleanup traceback exceeds explicit32-frame bound')
   number=getattr(error,'errno',None);filename=getattr(error,'filename',None)
   if number is not None and type(number)is not int:raise ValueError('invalid exception errno')
   if filename is not None and type(filename)is not str:raise ValueError('invalid exception filename')
   text=''.join(traceback.format_exception(type(error),error,error.__traceback__,chain=False))
   row=dict(role=role,exception_type=type(error).__module__+'.'+type(error).__qualname__,errno=number,
     filename=filename,traceback=text,traceback_frames=frames,current_exception_only=True)
   payload=(json.dumps(row,ensure_ascii=True,separators=(',',':'))+'\n').encode('ascii')
   if len(payload)>MAX_BYTES:raise ValueError('cleanup receipt exceeds64KiB; not truncated')
   flags=os.O_WRONLY|os.O_APPEND|os.O_NOFOLLOW|os.O_CLOEXEC
   if self.signature is None:flags|=os.O_CREAT|os.O_EXCL
   fd=os.open(self.path,flags,0o600);info=os.fstat(fd)
   signature=(info.st_dev,info.st_ino,info.st_mode,info.st_uid,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns)
   if (not stat.S_ISREG(info.st_mode)or stat.S_IMODE(info.st_mode)!=0o600 or info.st_uid!=os.geteuid()
       or info.st_nlink!=1 or info.st_size!=self.length):raise ValueError('private cleanup receipt metadata changed')
   if self.signature is not None and signature!=self.signature:raise ValueError('cleanup receipt identity/content metadata changed')
   written=os.write(fd,payload)
   if written!=len(payload):raise OSError(errno.EIO,'partial cleanup receipt write')
   self.length+=written;info=os.fstat(fd)
   if info.st_size!=self.length:raise ValueError('cleanup receipt size changed during write')
   self.signature=(info.st_dev,info.st_ino,info.st_mode,info.st_uid,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns)
  except BaseException:
   self.failed=True;raise
  finally:
   if fd is not None:os.close(fd)

PAIRS=[
 ('from host_budget import HostBudget\n','from host_budget import HostBudget\nfrom cleanup_failure_receipt import CleanupFailureReceipt\n'),
 (" def save():(E/'result.json').write_text(json.dumps(report,indent=2))\n", " cleanup_failures=CleanupFailureReceipt(E/'cleanup-close-failures-private.jsonl')\n def save():(E/'result.json').write_text(json.dumps(report,indent=2))\n"),
 ("    except BaseException as error:report['errors'].append('cleanup '+role+':'+repr(error))\n",
  "    except BaseException as error:\n     report['errors'].append('cleanup '+role+':'+repr(error))\n     try:cleanup_failures.record(role,error)\n     except BaseException as archive_error:report['errors'].append('cleanup exception receipt '+role+':'+repr(archive_error))\n"),
]

def transform_controller(source):
 for old,new in PAIRS:
  if new in source or source.count(old)!=1:raise ValueError('exact unique cleanup source anchor required')
  source=source.replace(old,new,1)
 ast.parse(source);return source

def reverse_controller(source):
 for old,new in reversed(PAIRS):
  if source.count(new)!=1:raise ValueError('exact unique cleanup receipt inverse required')
  source=source.replace(new,old,1)
 ast.parse(source);return source
