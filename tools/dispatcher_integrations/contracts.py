"""Read-only owner-granted manifest contract. Not a replacement for D0's state machine."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

REPO='Escoba2024/SeriousSam-TSE-Bot-Servermods-'
PREFIX='TSE_DEV_JOB_V1\n'
_SHA=re.compile(r'[0-9a-f]{40}\Z')
_JOB=re.compile(r'[a-z][a-z0-9-]{2,60}\Z')
_SCOPE=re.compile(r'[A-Za-z0-9_./-]+\Z')
TEST=['python3','-B','-m','unittest','discover','-s','tools/notion_bridge','-p','test_*.py']

class AuthorizationError(RuntimeError):pass

def manifest_digest(j):
    return hashlib.sha256(json.dumps(j,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def _require(valid,why):
    if not valid:raise AuthorizationError(why)

@dataclass(frozen=True)
class ApprovedJob:
    issue_number:int
    job_id:str
    revision:int
    base_sha:str
    manifest_hash:str
    identity:str

def authorize_job(issue,policy,now):
    _require(isinstance(issue,dict),'invalid issue')
    _require(type(issue.get('number')) is int and issue['number']>0,'invalid issue number')
    _require(issue.get('state')=='open','issue is not open')
    _require((issue.get('user') or {}).get('login')=='Escoba2024','foreign issue owner')
    url=issue.get('repository_url')
    if url is not None:
        _require(url=='https://api.github.com/repos/'+REPO,'foreign repository')
    body=issue.get('body')
    _require(isinstance(body,str),'invalid manifest body')
    body=body.replace('\r\n','\n')
    _require(body.startswith(PREFIX) and len(body)<=20000,'missing manifest prefix')
    try:j=json.loads(body[len(PREFIX):])
    except ValueError:raise AuthorizationError('invalid manifest JSON') from None
    _require(isinstance(j,dict),'invalid manifest type')
    _require(set(j)=={'id','revision','base_sha','scope','task','tests','priority','depends_on'},'invalid manifest keys')
    _require(isinstance(j['id'],str) and bool(_JOB.fullmatch(j['id'])),'invalid job id')
    _require(type(j['revision']) is int and j['revision']>=1,'invalid revision')
    _require(isinstance(j['base_sha'],str) and bool(_SHA.fullmatch(j['base_sha'])),'invalid pinned base')
    scope=j['scope']
    _require(isinstance(scope,list) and 1<=len(scope)<=12,'invalid scope')
    for entry in scope:
        _require(isinstance(entry,str) and entry.startswith('tools/notion_bridge/')
                 and _SCOPE.fullmatch(entry)
                 and all(p and p not in ('.','..') and not p.startswith('.') for p in entry.split('/')),
                 'invalid scoped path')
    _require(len(set(scope))==len(scope),'duplicate scoped path')
    _require(isinstance(j['task'],str) and 10<=len(j['task'])<=12000,'invalid task')
    _require(type(j['priority']) is int and 0<=j['priority']<=100,'invalid priority')
    deps=j['depends_on']
    _require(isinstance(deps,list) and all(isinstance(v,str) and _JOB.fullmatch(v) and v!=j['id'] for v in deps),'invalid dependencies')
    tests=j['tests']
    _require(isinstance(tests,list) and 1<=len(tests)<=8,'invalid tests')
    _require(all(test in (TEST,TEST+['-v']) for test in tests),'unapproved test command')
    _require(isinstance(policy,dict),'missing owner policy')
    g=policy.get('grants',{}).get(j['id'])
    _require(isinstance(g,dict) and g.get('issue')==issue['number'] and g.get('digest')==manifest_digest(j),
             'no matching owner grant')
    expiry=g.get('expires_at')
    _require(type(expiry) in (int,float) and now<expiry<=now+14400,'expired or overlong owner grant')
    h=manifest_digest(j)
    identity=hashlib.sha256(json.dumps([issue['number'],j['id'],j['revision'],j['base_sha'],h],
                                        separators=(',',':')).encode()).hexdigest()
    return ApprovedJob(issue['number'],j['id'],j['revision'],j['base_sha'],h,identity)

class DeliveryLedger:
    """Durable fail-closed dedupe for candidate handoff, independent of worker SQLite."""
    def __init__(self,path):self.path=Path(path)
    def record_once(self,job):
        if not isinstance(job,ApprovedJob):raise AuthorizationError('unapproved job')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        lock=self.path.with_name(self.path.name+'.lock')
        try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError:raise AuthorizationError('ledger lock occupied') from None
        try:
            os.close(fd)
            try:state=json.loads(self.path.read_text())
            except FileNotFoundError:state={}
            except (ValueError,OSError):raise AuthorizationError('ledger unavailable') from None
            if not isinstance(state,dict):raise AuthorizationError('invalid ledger')
            old=state.get(job.job_id)
            if old is not None:
                if old!=job.identity:raise AuthorizationError('immutable identity drift')
                return False
            state[job.job_id]=job.identity
            temp=None
            try:
                with tempfile.NamedTemporaryFile('w',dir=self.path.parent,encoding='utf-8',delete=False) as stream:
                    temp=stream.name
                    os.chmod(temp,0o600)
                    json.dump(state,stream,sort_keys=True)
                    stream.flush();os.fsync(stream.fileno())
                os.replace(temp,self.path)
            finally:
                if temp and os.path.exists(temp):os.unlink(temp)
            return True
        finally:
            lock.unlink(missing_ok=True)

def status_event(job,status,head_sha,evidence):
    _require(isinstance(job,ApprovedJob),'status needs approved job')
    _require(status in {'QUEUED','RUNNING','BLOCKED','FAILED','REVIEW_READY'},'status needs D0 approval')
    if status=='REVIEW_READY':
        _require(isinstance(head_sha,str) and _SHA.fullmatch(head_sha),'published commit required')
        _require(isinstance(evidence,str) and 1<=len(evidence.strip())<=1000,'verified evidence required')
    return {'schema':'TSE_D1_STATUS_V1','issue_number':job.issue_number,
            'job_id':job.job_id,'revision':job.revision,'identity':job.identity,
            'manifest_hash':job.manifest_hash,'status':status,
            'head_sha':head_sha if isinstance(head_sha,str) and _SHA.fullmatch(head_sha) else None,
            'evidence':evidence if isinstance(evidence,str) and len(evidence)<=1000 else None}
