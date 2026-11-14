"""Fresh exec-only capture setup. No game launch, gameplay or process hooks."""
import hashlib
import json
import os
from pathlib import Path
import resource
import sys

from owned_sync_capture import MAX_BYTES,capture_argv,exclusive_json,need,observe_roles,read_start

RUNTIME_REVIEWED=False


def main(path):
 need(RUNTIME_REVIEWED,'disabled capture exec helper')
 path=Path(path);need(path.is_absolute()and path.resolve(strict=True)==path,'exact private config path')
 st=path.stat();need(st.st_mode&0o777==0o600 and st.st_nlink==1,'private single-link config')
 config=json.loads(path.read_text())
 for p,h in config['source_pins'].items():need(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,'frozen setup source changed')
 need(observe_roles(config['registry'])==config['binding'],'roles changed before capture exec')
 owner=Path(config['owner_path']);need(owner.parent==path.parent and owner.name=='owned-sync-owner.json','owner path')
 pid=os.getpid();parent=os.getppid()
 exclusive_json(owner,dict(identity=[pid,read_start(pid)],supervisor_identity=[parent,read_start(parent)],pgrp=os.getpgrp(),setup_only=True))
 resource.setrlimit(resource.RLIMIT_FSIZE,(MAX_BYTES,MAX_BYTES))
 args=capture_argv(config['registry']['server']['identity'][0])
 os.execv(args[0],args)


if __name__=='__main__':
 need(len(sys.argv)==2,'one exact configuration required');main(sys.argv[1])
