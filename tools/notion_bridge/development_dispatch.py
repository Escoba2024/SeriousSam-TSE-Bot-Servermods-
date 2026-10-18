#!/usr/bin/env python3
"""Single bounded development worker. GitHub content requires a local owner grant.
Model tools cannot read credentials/state or write Git metadata. No automatic merge.
"""
import argparse
import contextlib
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import sqlite3
import stat
import subprocess
import time
import urllib.error
import urllib.request

REPO='Escoba2024/SeriousSam-TSE-Bot-Servermods-'
PREFIX='TSE_DEV_JOB_V1\n'
BASE=Path('/var/lib/tse-agent-control')
CODEX='/opt/tse-agent-control/toolchain/codex/bin/codex'
NODE='/opt/tse-agent-control/toolchain/node-v24.22.0-linux-x64/bin'
STATES={'QUEUED','RUNNING','BLOCKED','FAILED','REVIEW_READY','DONE'}
SCHEMA={'type':'object','properties':{'status':{'type':'string','enum':['implemented','blocked']},'summary':{'type':'string'},'tests':{'type':'array','items':{'type':'string'}}},'required':['status','summary','tests'],'additionalProperties':False}

class Blocked(RuntimeError):pass
class Transient(RuntimeError):pass
class GitHubRateLimited(Transient):
    def __init__(self,reset_at):
        self.reset_at=reset_at
        super().__init__('GITHUB_RATE_LIMIT')

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def valid_path(p):
    return (isinstance(p,str) and p.startswith('tools/notion_bridge/')
            and re.fullmatch(r'[A-Za-z0-9_./-]+',p) and all(x not in ('','..','.') and not x.startswith('.') for x in p.split('/')))

def authorize(issue,policy,now):
    if issue.get('state')!='open':raise Blocked('CANCELLED_OR_CLOSED')
    if (issue.get('user') or {}).get('login')!='Escoba2024':raise Blocked('FOREIGN_AUTHOR')
    body=issue.get('body','')
    if isinstance(body,str):body=body.replace('\r\n','\n')
    if not isinstance(body,str) or not body.startswith(PREFIX) or len(body)>20000:raise Blocked('INVALID_MANIFEST')
    try:j=json.loads(body[len(PREFIX):])
    except ValueError:raise Blocked('INVALID_JSON')
    keys={'id','revision','base_sha','scope','task','tests','priority','depends_on'}
    if not isinstance(j,dict) or set(j)!=keys:raise Blocked('INVALID_KEYS')
    if not isinstance(j['id'],str) or not re.fullmatch(r'[a-z][a-z0-9-]{2,60}',j['id']):raise Blocked('INVALID_ID')
    if type(j['revision']) is not int or j['revision']<1:raise Blocked('INVALID_REVISION')
    if not isinstance(j['base_sha'],str) or not re.fullmatch('[0-9a-f]{40}',j['base_sha']):raise Blocked('INVALID_BASE')
    if not isinstance(j['scope'],list) or not 1<=len(j['scope'])<=12 or not all(valid_path(p) for p in j['scope']) or len(set(j['scope']))!=len(j['scope']):raise Blocked('INVALID_SCOPE')
    if not isinstance(j['task'],str) or not 10<=len(j['task'])<=12000:raise Blocked('INVALID_TASK')
    if type(j['priority']) is not int or not 0<=j['priority']<=100:raise Blocked('INVALID_PRIORITY')
    if not isinstance(j['depends_on'],list) or not all(isinstance(x,str) and re.fullmatch('[a-z][a-z0-9-]{2,60}',x) and x!=j['id'] for x in j['depends_on']):raise Blocked('INVALID_DEPENDENCY')
    tests=j['tests']
    if not isinstance(tests,list) or not 1<=len(tests)<=8:raise Blocked('INVALID_TESTS')
    for argv in tests:
        if not isinstance(argv,list) or not argv or argv[0]!='python3' or not all(isinstance(x,str) and len(x)<300 for x in argv):raise Blocked('INVALID_TESTS')
        expected=['python3','-B','-m','unittest','discover','-s','tools/notion_bridge','-p','test_*.py']
        if argv not in (expected,expected+['-v']):raise Blocked('INVALID_TESTS')
    g=policy.get('grants',{}).get(j['id'],{})
    if g.get('issue')!=issue.get('number') or g.get('digest')!=digest(j):raise Blocked('NO_MATCHING_OWNER_GRANT')
    if type(g.get('expires_at')) not in (int,float) or not now<g['expires_at']<=now+4*3600:raise Blocked('EXPIRED_OR_OVERLONG_GRANT')
    return j

def command(argv,*,cwd=None,timeout=120,env=None):
    e={**os.environ,'PATH':NODE+':/usr/local/bin:/usr/bin:/bin','HOME':str(BASE),'PYTHONDONTWRITEBYTECODE':'1','GIT_TERMINAL_PROMPT':'0','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_ASKPASS':'/bin/false'}
    if env:e.update(env)
    return subprocess.run(argv,cwd=cwd,env=e,timeout=timeout,capture_output=True,text=True,errors='replace')

def git(cwd,*args):
    p=command(['git','-c','core.hooksPath=/dev/null','-C',str(cwd),*args])
    if p.returncode:raise Transient('GIT_'+args[0]+': '+p.stderr[-300:])
    return p.stdout

def ensure_checkout(path,remote,sha,branch):
    if path.is_symlink():raise Blocked('CHECKOUT_SYMLINK')
    path.mkdir(parents=True,exist_ok=True,mode=0o700)
    if not (path/'.git').exists():
        if any(path.iterdir()):raise Blocked('UNOWNED_CHECKOUT_CONTENT')
        git(path,'init','-q')
    if (path/'.git').is_symlink() or not (path/'.git').is_dir():raise Blocked('INVALID_GIT_DIRECTORY')
    head=command(['git','-C',str(path),'rev-parse','--verify','HEAD'])
    if head.returncode:
        # A failed initial fetch leaves an empty repository, which is safe to retry.
        if any(x.name!='.git' for x in path.iterdir()):raise Blocked('INCOMPLETE_CHECKOUT_WITH_FILES')
        git(path,'fetch','--no-tags',remote,sha)
        git(path,'cat-file','-e',sha+'^{commit}')
        git(path,'checkout','-q','-b',branch,sha)
    elif head.stdout.strip()!=sha:
        raise Blocked('CHECKOUT_HEAD_DRIFT')
    if git(path,'status','--porcelain=v1','--untracked-files=all').strip():raise Blocked('CHECKOUT_DIRTY')
    git(path,'config','user.name','TSE Dispatcher')
    git(path,'config','user.email','dispatcher@users.noreply.github.com')

def snapshot(root):
    result={}
    if root.is_symlink() or root.resolve()!=root.absolute():raise Blocked('ROOT_SYMLINK')
    for base,dirs,files in os.walk(root,followlinks=False):
        if Path(base)==root and '.git' in dirs:dirs.remove('.git')
        for name in dirs+files:
            p=Path(base)/name;s=p.lstat();rel=p.relative_to(root).as_posix()
            if stat.S_ISLNK(s.st_mode) or getattr(s,'st_file_attributes',0)&0x400:raise Blocked('LINK_OR_REPARSE: '+rel)
            if stat.S_ISDIR(s.st_mode):continue
            if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1:raise Blocked('SPECIAL_OR_HARDLINK: '+rel)
            result[rel]=(hashlib.sha256(p.read_bytes()).hexdigest(),stat.S_IMODE(s.st_mode))
    return result

def check_objects(root):
    for line in git(root,'ls-files','--stage','-z').split('\0'):
        if line and (line.split(' ',1)[0] not in ('100644','100755') or line.split('\t',1)[0].split()[-1]!='0'):
            raise Blocked('GIT_SPECIAL_OBJECT_OR_UNMERGED')
    for line in git(root,'ls-tree','-r','HEAD').splitlines():
        if line.split(' ',1)[0] not in ('100644','100755'):raise Blocked('BASE_SPECIAL_OBJECT')

def check_scope(root,before,scope):
    check_objects(root);after=snapshot(root)
    changed=sorted(p for p in before.keys()|after.keys() if before.get(p)!=after.get(p))
    if any(p not in scope for p in changed):raise Blocked('OUT_OF_SCOPE: '+','.join(p for p in changed if p not in scope))
    staged=git(root,'diff','--cached','--name-only','-z').split('\0')
    if any(p and p not in scope for p in staged):raise Blocked('INDEX_OUT_OF_SCOPE')
    return changed

def open_db(path):
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path);db.row_factory=sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL')
    db.executescript('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, digest TEXT, manifest TEXT, issue INTEGER, status TEXT, attempts INTEGER DEFAULT 0, next_at REAL DEFAULT 0, updated REAL, reason TEXT DEFAULT "", result TEXT DEFAULT "{}"); CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, job_id TEXT, at REAL, status TEXT, reason TEXT); CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY,value TEXT);')
    return db

def job_row(db,id):
    r=db.execute('SELECT * FROM jobs WHERE id=?',(id,)).fetchone()
    if r is None:return None
    j=dict(r);j['manifest']=json.loads(j['manifest']);j['result']=json.loads(j['result']);return j

def accept(db,j,issue,now):
    old=job_row(db,j['id'])
    if old:
        if old['digest']!=digest(j):raise Blocked('IMMUTABLE_JOB_REVISION_DRIFT')
        return
    with db:
        db.execute('INSERT INTO jobs(id,digest,manifest,issue,status,updated) VALUES(?,?,?,?,?,?)',(j['id'],digest(j),json.dumps(j),issue,'QUEUED',now))
        db.execute('INSERT INTO events(job_id,at,status,reason) VALUES(?,?,?,?)',(j['id'],now,'QUEUED','AUTHORIZED'))

def transition(db,id,status,now,reason='',result=None):
    if status not in STATES:raise ValueError('invalid state')
    if status=='DONE':raise Blocked('DONE_REQUIRES_SEPARATE_INTEGRATION_ACCEPTANCE')
    with db:
        if result is None:db.execute('UPDATE jobs SET status=?,updated=?,reason=? WHERE id=?',(status,now,reason,id))
        else:db.execute('UPDATE jobs SET status=?,updated=?,reason=?,result=? WHERE id=?',(status,now,reason,json.dumps(result),id))
        db.execute('INSERT INTO events(job_id,at,status,reason) VALUES(?,?,?,?)',(id,now,status,reason))

def mark_done(db,id,policy,integrated,now):
    row=job_row(db,id)
    acceptance=policy.get('integration_acceptance',{}).get(id,{})
    if not row or row['status']!='REVIEW_READY' or not integrated:raise Blocked('INTEGRATION_NOT_VERIFIED')
    if acceptance.get('commit')!=row['result'].get('commit') or acceptance.get('digest')!=row['digest'] or not acceptance.get('evidence'):raise Blocked('INTEGRATION_ACCEPTANCE_MISSING')
    with db:
        db.execute('UPDATE jobs SET status="DONE",updated=? WHERE id=?',(now,id))
        db.execute('INSERT INTO events(job_id,at,status,reason) VALUES(?,?,?,?)',(id,now,'DONE','OWNER_ACCEPTED_AND_IN_MAIN'))

def ready(db,now):
    rows=[job_row(db,r['id']) for r in db.execute('SELECT id FROM jobs WHERE status="QUEUED" AND next_at<=? ORDER BY updated,id',(now,))]
    rows.sort(key=lambda r:(-r['manifest']['priority'],r['updated'],r['id']))
    return [r for r in rows if all((job_row(db,k) or {}).get('status') in ('REVIEW_READY','DONE') for k in r['manifest']['depends_on'])]

def retry(db,id,reason,now,policy):
    r=job_row(db,id);attempts=r['attempts']
    if attempts>=policy.get('max_attempts',3):status='FAILED'
    else:status='QUEUED'
    delay=max(3600,policy.get('backoff_seconds',60)) if reason=='QUOTA' else min(3600,policy.get('backoff_seconds',60)*2**max(0,attempts-1))
    with db:db.execute('UPDATE jobs SET next_at=? WHERE id=?',(now+delay,id))
    transition(db,id,status,now,reason)
    if reason=='QUOTA':
        with db:db.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)',('cooldown',str(now+delay)))

def cooldown(db):
    r=db.execute("SELECT value FROM meta WHERE key='cooldown'").fetchone()
    return float(r[0]) if r else 0

def fresh_policy(policy):
    if '_path' not in policy:return policy
    path=Path(policy['_path'])
    if path.is_symlink():raise Blocked('POLICY_SYMLINK')
    value=json.loads(path.read_text());value['_path']=str(path)
    return value

def recheck(row,policy):
    value=fresh_policy(policy)
    j=authorize(fetch_issue(row['issue']),value,time.time())
    if digest(j)!=row['digest']:raise Blocked('SOURCE_REVISION_DRIFT')
    return value

def published_ref_matches(output,sha):
    words=output.split()
    return len(words)==2 and words[0]==sha

def tests_passed(code,stdout,stderr):
    output=(stdout or '')+'\n'+(stderr or '')
    counts=re.findall(r'^Ran ([1-9][0-9]*) tests? in ',output,re.M)
    ok=re.search(r'^OK(?: \(skipped=([0-9]+)\))?\s*$',output,re.M)
    return code==0 and len(counts)==1 and ok is not None and int(ok[1] or 0)<int(counts[0])

def enable_subreaper():
    if ctypes.CDLL(None,use_errno=True).prctl(36,1,0,0,0)!=0:raise Blocked('SUBREAPER_UNAVAILABLE')

def descendants():
    parents={}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            data=(p/'stat').read_text();parents[int(p.name)]=int(data[data.rfind(')')+2:].split()[1])
        except (OSError,ValueError,IndexError):continue
    owned={os.getpid()};changed=True
    while changed:
        before=len(owned);owned.update(pid for pid,ppid in parents.items() if ppid in owned);changed=len(owned)!=before
    return owned-{os.getpid()}

def cleanup_children(baseline):
    # Subreaper adopts even setsid children of this coordinator's worker.
    for sig in (signal.SIGTERM,signal.SIGKILL):
        for pid in descendants()-baseline:
            try:os.kill(pid,sig)
            except ProcessLookupError:pass
        deadline=time.monotonic()+0.3
        while time.monotonic()<deadline:
            for pid in descendants()-baseline:
                try:os.waitpid(pid,os.WNOHANG)
                except (ChildProcessError,ProcessLookupError):pass
            if not descendants()-baseline:return
            time.sleep(0.02)
    if descendants()-baseline:raise Blocked('WORKER_CHILDREN_STILL_ALIVE')

def occupied(db):
    rows=[job_row(db,r['id']) for r in db.execute('SELECT id FROM jobs WHERE status IN ("RUNNING","BLOCKED")')]
    return any(identity_alive(r['result']) or r['result'].get('recovery_required',False) for r in rows)

def process_identity(pid):
    try:
        data=Path(f'/proc/{pid}/stat').read_text();tail=data[data.rfind(')')+2:].split()
        return {'pid':pid,'start_ticks':tail[19],'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    except (OSError,IndexError):return {}

def identity_alive(result):
    if not result.get('pid'):return False
    return all(process_identity(result['pid']).get(k)==result.get(k) for k in ('pid','start_ticks','boot_id'))

def recover(db,now):
    for row in list(db.execute('SELECT id FROM jobs WHERE status="RUNNING"')):
        r=job_row(db,row['id'])
        if identity_alive(r['result']):continue
        transition(db,r['id'],'BLOCKED',now,'RECOVERY_INSPECTION_REQUIRED',result=r['result']|{'recovery_required':r['result'].get('phase') in ('MODEL','TEST')})

def classify_failure(code,stdout,stderr):
    if code==0:return 'OK'
    if re.search(r'usage limit|quota exceeded|429 too many requests',stderr or '',re.I):return 'QUOTA'
    if re.search(r'bwrap:|operation not permitted|sandbox.*(?:failure|blocked)',stderr or '',re.I):return 'SANDBOX'
    return 'WORKER_FAILED'

def permissions(root,scope,scratch):
    fs={':minimal':'read','/opt/tse-agent-control/toolchain':'read',str(root):'read',str(root/'.git'):'read',str(scratch):'write'}
    parents={root/p.parent for p in map(PurePosixPath,scope)}
    # Codex 0.163 treats write roots as directories. Protect existing siblings;
    # the inventory gate rejects any new unapproved files before commit/publish.
    for parent in parents:
        fs[str(parent)]='write'
        for p in parent.rglob('*'):
            if p.is_file() and p.relative_to(root).as_posix() not in scope:
                fs[str(p)]='read'
    values={'default_permissions':'dispatch','permissions.dispatch.filesystem':fs,'permissions.dispatch.network.enabled':False,'approval_policy':'never','features.multi_agent':False,'web_search':'disabled','shell_environment_policy.inherit':'none','shell_environment_policy.set':{'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':str(scratch),'TMPDIR':str(scratch),'PYTHONDONTWRITEBYTECODE':'1'},'project_doc_max_bytes':0}
    # Config override accepts TOML inline tables, not JSON objects.
    def toml(v):
        if isinstance(v,dict):return '{'+','.join(json.dumps(k)+'='+toml(x) for k,x in v.items())+'}'
        return json.dumps(v)
    return [x for k,v in values.items() for x in ('-c',k+'='+toml(v))]

def sandbox(root,scope,scratch,argv,timeout=300):
    enable_subreaper();baseline=set(descendants())
    try:return command([CODEX,*permissions(root,scope,scratch),'sandbox','-P','dispatch','-C',str(root),'--',*argv],cwd=root,timeout=timeout)
    finally:cleanup_children(baseline)

def fetch_issue(number):
    request=urllib.request.Request(f'https://api.github.com/repos/{REPO}/issues/{number}',headers={'User-Agent':'TSE-Development-Dispatcher/1.0','Accept':'application/vnd.github+json'})
    try:
        with urllib.request.urlopen(request,timeout=25) as response:return json.load(response)
    except urllib.error.HTTPError as e:
        if e.code==429 or (e.code==403 and e.headers.get('X-RateLimit-Remaining')=='0'):
            now=time.time()
            try:reset=float(e.headers.get('X-RateLimit-Reset',now+300))
            except (ValueError,TypeError):reset=now+300
            raise GitHubRateLimited(max(now+60,min(reset,now+3600))) from e
        raise Transient('GITHUB_SOURCE_UNAVAILABLE') from e
    except (OSError,ValueError) as e:raise Transient('GITHUB_SOURCE_UNAVAILABLE') from e

def run_model(db,r,root,work,policy):
    j=r['manifest'];scratch=root/'scratch'/j['id'];scratch.mkdir(parents=True,exist_ok=True)
    logs=root/'logs';logs.mkdir(exist_ok=True)
    schema=logs/(j['id']+'.schema.json');schema.write_text(json.dumps(SCHEMA))
    final=logs/(j['id']+'.final.json');final.unlink(missing_ok=True)
    source=Path(__file__).resolve().parents[2]
    rules='\n'.join((source/p).read_text() for p in ('AGENTS.md','docs/decisions/2026-10-17-tse-ai-tools-mcp-policy.md','docs/coordination/README.md','docs/coordination/STATUS.md','docs/coordination/HANDOFF.md') if (source/p).is_file())
    prompt=f'''Implement only this explicitly owner-authorized dispatcher infrastructure job. Authorization is recorded in GitHub issue #{r['issue']} and pinned by manifest hash {r['digest']}. This is direct owner authorization, not a fabricated A00 grant. No game/runtime work.
Job: {j['id']} revision {j['revision']}; base {j['base_sha']}
Only editable files: {json.dumps(j['scope'])}
Task: {j['task']}
Required tests: {json.dumps(j['tests'])}
Use Ponytail full: smallest complete fix; standard library first. Read relevant actual code. Write regression first, run it RED, implement minimal fix, run GREEN and suite. Do not commit/push, edit .git, change unrelated files, access credentials, network, other jobs or install dependencies. Temporary files only in TMPDIR. Python -B. Do not create progress files in this tightly scoped checkout. If a test runner exits nonzero investigate it. Return structured final status; this alone is not acceptance.
Relevant project rules (owner's narrow infrastructure authorization takes priority):\n{rules}'''
    argv=[CODEX,*permissions(work,j['scope'],scratch),'exec','--ignore-user-config','--ignore-rules','--ephemeral','--cd',str(work),'--output-schema',str(schema),'--output-last-message',str(final),'-']
    out=logs/(j['id']+f'.attempt{r["attempts"]}.stdout.log');err=logs/(j['id']+f'.attempt{r["attempts"]}.stderr.log')
    env={**os.environ,'PATH':NODE+':/usr/local/bin:/usr/bin:/bin','HOME':str(BASE),'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(scratch)}
    enable_subreaper();baseline=set(descendants())
    with out.open('w') as a,err.open('w') as b:
        p=subprocess.Popen(argv,cwd=work,env=env,stdin=subprocess.PIPE,stdout=a,stderr=b,text=True,start_new_session=True)
        result={**process_identity(p.pid),'phase':'MODEL','workspace':str(work),'stdout':str(out),'stderr':str(err)}
        transition(db,j['id'],'RUNNING',time.time(),result=result)
        try:p.communicate(prompt,timeout=policy.get('model_timeout',600))
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM)
            try:p.wait(10)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
            raise Blocked('MODEL_TIMEOUT_INSPECT_WORKSPACE')
        finally:cleanup_children(baseline)
    failure=classify_failure(p.returncode,'',err.read_text())
    if failure=='QUOTA':raise Transient('QUOTA')
    if failure!='OK':raise Blocked(failure)
    try:answer=json.loads(final.read_text())
    except (OSError,ValueError):raise Blocked('MISSING_STRUCTURED_COMPLETION')
    if answer.get('status')!='implemented' or not answer.get('summary'):raise Blocked('MODEL_REPORTED_BLOCKED')
    return result|{'exit_code':p.returncode,'model_summary':answer['summary'],'phase':'TEST'}

def execute(db,r,root,policy):
    j=r['manifest'];id=j['id'];work=root/'worktrees'/id
    branch='agent/A03/'+id+'-r'+str(j['revision'])
    now=time.time()
    with db:db.execute('UPDATE jobs SET attempts=attempts+1 WHERE id=?',(id,))
    r=job_row(db,id)
    old=r['result']
    try:
        policy=recheck(r,policy)
        if old.get('phase')=='PUBLISH' and old.get('commit'):
            result=old
        else:
            transition(db,id,'RUNNING',now,result={**process_identity(os.getpid()),'phase':'FETCH','workspace':str(work)})
            ensure_checkout(work,'https://github.com/'+REPO+'.git',j['base_sha'],branch)
            before=snapshot(work);check_objects(work)
            scratch=root/'scratch'/id;scratch.mkdir(parents=True,exist_ok=True)
            # Real preflight proves command confinement before spending model tokens.
            probe=sandbox(work,j['scope'],scratch,['python3','-B','-c',"print('DISPATCH_SANDBOX_OK')"])
            if probe.returncode or probe.stdout.strip()!='DISPATCH_SANDBOX_OK':raise Blocked('SANDBOX_PREFLIGHT_FAILED')
            result=run_model(db,r,root,work,policy)
            result['model_identity']={k:result[k] for k in ('pid','start_ticks','boot_id')}
            result.update(process_identity(os.getpid()))
            transition(db,id,'RUNNING',time.time(),result=result)
            policy=recheck(r,policy)
            changed=check_scope(work,before,j['scope'])
            if not changed:raise Blocked('NO_CODE_CHANGE')
            test_results=[]
            for n,argv in enumerate(j['tests']):
                p=sandbox(work,j['scope'],scratch,argv,timeout=policy.get('test_timeout',300))
                logfile=root/'logs'/(id+f'.test{n}.log');logfile.write_text(p.stdout+'\n'+p.stderr)
                test_results.append({'argv':argv,'exit_code':p.returncode,'log':str(logfile)})
                if not tests_passed(p.returncode,p.stdout,p.stderr):raise Blocked('TEST_FAILED_OR_EMPTY: '+str(n))
            check_scope(work,before,j['scope'])
            if git(work,'rev-parse','HEAD').strip()!=j['base_sha']:raise Blocked('MODEL_CHANGED_HEAD')
            git(work,'diff','--check')
            git(work,'add','--',*changed);check_scope(work,before,j['scope'])
            git(work,'commit','-m',f'dispatch({id}): '+result['model_summary'].splitlines()[0][:100])
            commit=git(work,'rev-parse','HEAD').strip()
            actual=git(work,'diff-tree','--no-commit-id','--name-only','-r','-z',commit).strip('\0').split('\0')
            if set(actual)!=set(changed):raise Blocked('COMMIT_SCOPE_MISMATCH')
            if git(work,'status','--porcelain=v1','--untracked-files=all').strip():raise Blocked('POSTCOMMIT_DIRTY')
            bundle=root/'logs'/(id+'.bundle');git(work,'bundle','create',str(bundle),'HEAD')
            result.update({'phase':'PUBLISH','commit':commit,'branch':branch,'changed':changed,'tests':test_results,'bundle':str(bundle),'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest()})
            transition(db,id,'RUNNING',time.time(),result=result)
        policy=recheck(r,policy)
        key=Path(policy.get('publish_key','/nonexistent'))
        if not key.is_file():raise Blocked('PUBLISH_CREDENTIAL_MISSING_COMMIT_PRESERVED')
        ssh='ssh -i '+str(key)+' -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile='+str(Path(policy['known_hosts']))
        p=command(['git','-c','core.hooksPath=/dev/null','push','git@github.com:'+REPO+'.git',result['commit']+':refs/heads/'+branch],cwd=work,env={'GIT_SSH_COMMAND':ssh})
        if p.returncode:raise Transient('PUBLISH_NETWORK')
        remote=command(['git','ls-remote','git@github.com:'+REPO+'.git','refs/heads/'+branch],cwd=work,env={'GIT_SSH_COMMAND':ssh})
        if remote.returncode or not published_ref_matches(remote.stdout,result['commit']):raise Transient('PUBLISH_VERIFY')
        result['phase']='COMPLETE';result['published_at']=time.time();result['commit_url']='https://github.com/'+REPO+'/commit/'+result['commit']
        transition(db,id,'REVIEW_READY',time.time(),result=result)
    except Transient as e:
        # Only pre-model source/fetch and post-test publishing are automatically retried.
        retry(db,id,'QUOTA' if str(e)=='QUOTA' else str(e).split(':')[0],time.time(),policy)
    except (Blocked,OSError,ValueError,subprocess.TimeoutExpired) as e:
        transition(db,id,'BLOCKED',time.time(),str(e)[:300])

def poll(db,root,policy):
    policy=fresh_policy(policy)
    now=time.time()
    recover(db,now)
    rate_row=db.execute("SELECT value FROM meta WHERE key='github_rate_limit_until'").fetchone()
    rate_until=float(rate_row[0]) if rate_row else 0
    if rate_until>now:
        with db:db.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)',('source_errors',json.dumps({'github_api':'GITHUB_RATE_LIMIT_UNTIL_'+str(int(rate_until))})))
        return
    authorized=set();source_errors={}
    for id,g in policy.get('grants',{}).items():
        prior=job_row(db,id)
        if prior and prior['status'] in ('REVIEW_READY','DONE','FAILED'):
            continue
        try:
            raw=fetch_issue(g['issue']);j=authorize(raw,policy,time.time())
            if j['id']!=id:raise Blocked('GRANT_ID_MISMATCH')
            accept(db,j,g['issue'],time.time());authorized.add(id)
        except GitHubRateLimited as e:
            with db:db.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)',('github_rate_limit_until',str(e.reset_at)))
            source_errors[id]='GITHUB_RATE_LIMIT_UNTIL_'+str(int(e.reset_at))
            break
        except Transient as e:
            source_errors[id]=str(e);continue
        except Blocked as e:
            source_errors[id]=str(e)
            if job_row(db,id) and job_row(db,id)['status'] not in ('REVIEW_READY','DONE','FAILED'):
                transition(db,id,'BLOCKED',time.time(),str(e))
    with db:db.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)',('source_errors',json.dumps(source_errors)))
    # A live orphan blocks all model work, even in a different scope.
    if occupied(db):return
    for _ in range(min(4,policy.get('jobs_per_poll',4))):
        if cooldown(db)>time.time():break
        candidates=[r for r in ready(db,time.time()) if r['id'] in authorized]
        if not candidates:break
        execute(db,candidates[0],root,policy)
        if occupied(db):break

def sync_notion(db,policy):
    from notion_adapter import NotionClient,NotionUnavailable,ISSUE
    token_path=Path(policy.get('notion_token_file','/etc/tse-dispatch/notion-token'))
    if not token_path.is_file():return 'BLOCKED_SERVER_TOKEN_MISSING'
    client=NotionClient(token=token_path.read_text().strip())
    try:
        client.issue_links()
        for row in client.rows:
            url=row.get('properties',{}).get('GitHub-Grant',{}).get('url') or ''
            match=ISSUE.fullmatch(url)
            if not match:continue
            record=db.execute('SELECT id FROM jobs WHERE issue=?',(int(match[1]),)).fetchone()
            if record:
                r=job_row(db,record['id'])
                client.report(row['id'],r['status'],r['result'].get('commit_url',''),r['attempts'],r['reason'])
        return 'LIVE_READ_WRITE_OK'
    except NotionUnavailable as e:return str(e)

def status(db,root,notion_status='BLOCKED_SERVER_TOKEN_MISSING',write=True):
    jobs=[{**{k:r[k] for k in ('id','issue','digest','status','attempts','next_at','updated','reason','result')},'base_sha':r['manifest']['base_sha'],'scope':r['manifest']['scope']} for x in db.execute('SELECT id FROM jobs ORDER BY id') for r in [job_row(db,x['id'])]]
    value={'at':time.time(),'mode':'GITHUB_OWNER_GRANTED_DEVELOPMENT','worker_limit':1,'direct_notion_api':notion_status=='LIVE_READ_WRITE_OK','notion_status':notion_status,'cooldown_until':cooldown(db),'source_errors':json.loads((db.execute("SELECT value FROM meta WHERE key='source_errors'").fetchone() or ['{}'])[0]),'jobs':jobs}
    if write:
        p=root/'status.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n');tmp.replace(p)
    return value

def read_status(root):
    path=root/'jobs.sqlite'
    if not path.is_file():return {'mode':'NOT_INITIALIZED','jobs':[]}
    with contextlib.closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        return status(db,root,write=False)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--policy',default='/etc/tse-dispatch/policy.json');parser.add_argument('--root',default=str(BASE/'development'));parser.add_argument('--status',action='store_true');parser.add_argument('--accept-integrated');args=parser.parse_args()
    root=Path(args.root)
    if args.status:
        print(json.dumps(read_status(root),indent=2));return
    root.mkdir(parents=True,exist_ok=True)
    with (BASE/'notion-dispatch/dispatcher.lock').open('a+') as lock, (BASE/'state/codex/worker.lock').open('a+') as worker:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(worker,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:print('SAFE_SKIP_ALREADY_RUNNING');return
        policy=fresh_policy({'_path':args.policy})
        with contextlib.closing(open_db(root/'jobs.sqlite')) as db:
            if args.accept_integrated:
                row=job_row(db,args.accept_integrated)
                if not row or row['status']!='REVIEW_READY':raise Blocked('NO_REVIEW_READY_JOB')
                request=urllib.request.Request('https://api.github.com/repos/'+REPO+'/compare/'+row['result']['commit']+'...main',headers={'User-Agent':'TSE-Development-Dispatcher/1.0'})
                with urllib.request.urlopen(request,timeout=25) as response:comparison=json.load(response)
                mark_done(db,row['id'],fresh_policy(policy),comparison.get('status') in ('ahead','identical'),time.time())
            else:poll(db,root,policy)
            value=status(db,root,sync_notion(db,policy))
            # Keep at most seven days of small logs; job bundles and structured results persist.
            for log in (root/'logs').glob('*.log'):
                if log.stat().st_mtime<time.time()-7*86400:log.unlink()
            print(' '.join(j['id']+'='+j['status'] for j in value['jobs']) or 'IDLE_NO_AUTHORIZED_JOBS')

if __name__=='__main__':main()
