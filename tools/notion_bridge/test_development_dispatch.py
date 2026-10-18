import copy
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import development_dispatch as d

NOW=1800000000
SHA='a'*40

def manifest(**kw):
    return dict(id='accept-1',revision=1,base_sha=SHA,scope=['tools/notion_bridge/example.py'],task='Implement a bounded infrastructure fix.',tests=[['python3','-B','-m','unittest','discover','-s','tools/notion_bridge','-p','test_*.py']],priority=10,depends_on=[],**kw)

def issue(job=None,**kw):
    return dict(number=31,state='open',user={'login':'Escoba2024'},body=d.PREFIX+json.dumps(job or manifest()),**kw)

def policy(job=None):
    j=job or manifest()
    return {'grants':{j['id']:{'issue':31,'digest':d.digest(j),'expires_at':NOW+3600}},'max_attempts':3,'backoff_seconds':60}

class Authorization(unittest.TestCase):
    def test_exact_owner_revision_is_authorized(self):
        self.assertEqual(d.authorize(issue(),policy(),NOW)['id'],'accept-1')
    def test_foreign_author_fails(self):
        i=issue();i['user']['login']='outsider'
        with self.assertRaises(d.Blocked):d.authorize(i,policy(),NOW)
    def test_changed_task_revokes_hash(self):
        j=manifest();j['task']='Different work'
        with self.assertRaises(d.Blocked):d.authorize(issue(j),policy(),NOW)
    def test_expired_grant_fails_but_old_issue_does_not(self):
        self.assertEqual(d.authorize(issue(),policy(),NOW)['revision'],1)
        with self.assertRaises(d.Blocked):d.authorize(issue(),policy(),NOW+3601)
    def test_closed_issue_cancels(self):
        i=issue();i['state']='closed'
        with self.assertRaisesRegex(d.Blocked,'CANCEL'):d.authorize(i,policy(),NOW)
    def test_unsafe_scope_and_shell_tests_fail(self):
        for scope in [['../escape'],['poc/GameMP.dll'],['tools/notion_bridge/../bad'],['tools/notion_bridge/.env'],['tools/notion_bridge/a:b']]:
            j=manifest();j['scope']=scope
            with self.subTest(scope=scope),self.assertRaises(d.Blocked):d.authorize(issue(j),policy(j),NOW)
        j=manifest();j['tests']=['sh -c injected']
        with self.assertRaises(d.Blocked):d.authorize(issue(j),policy(j),NOW)

class Checkout(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.source=self.root/'source';self.source.mkdir()
        self.git(self.source,'init','-q');self.git(self.source,'config','user.email','test@example.invalid');self.git(self.source,'config','user.name','Test')
        (self.source/'tools/notion_bridge').mkdir(parents=True)
        (self.source/'tools/notion_bridge/example.py').write_text('value=1\n')
        (self.source/'.gitignore').write_text('ignored\n')
        self.git(self.source,'add','.');self.git(self.source,'commit','-qm','base')
        self.sha=self.git(self.source,'rev-parse','HEAD').strip()
        self.dest=self.root/'job'
    def git(self,cwd,*args):
        return subprocess.check_output(['git','-C',str(cwd),*args],text=True,stderr=subprocess.STDOUT)
    def prepare(self):
        d.ensure_checkout(self.dest,str(self.source),self.sha,'agent/A03/test')
    def test_interrupted_empty_checkout_recovers_with_real_git(self):
        self.dest.mkdir();self.prepare()
        self.assertEqual(self.git(self.dest,'rev-parse','HEAD').strip(),self.sha)
    def test_failed_fetch_then_valid_remote_recovers(self):
        with self.assertRaises(d.Transient):d.ensure_checkout(self.dest,str(self.root/'missing'),self.sha,'agent/A03/test')
        self.prepare();self.assertEqual(self.git(self.dest,'rev-parse','HEAD').strip(),self.sha)
    def test_foreign_content_is_never_overwritten(self):
        self.dest.mkdir();(self.dest/'unowned').write_text('preserve')
        with self.assertRaises(d.Blocked):self.prepare()
        self.assertEqual((self.dest/'unowned').read_text(),'preserve')
    def test_ignored_untracked_out_of_scope_and_links_rejected(self):
        self.prepare();before=d.snapshot(self.dest)
        for name in ['ignored','untracked']:
            p=self.dest/name;p.write_text('bad')
            with self.assertRaises(d.Blocked):d.check_scope(self.dest,before,['tools/notion_bridge/example.py'])
            p.unlink()
        link=self.dest/'tools/notion_bridge/link';link.symlink_to('/etc/passwd')
        with self.assertRaises(d.Blocked):d.snapshot(self.dest)
        link.unlink()
        self.git(self.dest,'update-index','--add','--cacheinfo','160000,'+self.sha+',module')
        with self.assertRaises(d.Blocked):d.check_scope(self.dest,before,['tools/notion_bridge/example.py'])
    def test_only_approved_regular_changes_accepted(self):
        self.prepare();before=d.snapshot(self.dest)
        (self.dest/'tools/notion_bridge/example.py').write_text('value=2\n')
        self.assertEqual(d.check_scope(self.dest,before,['tools/notion_bridge/example.py']),['tools/notion_bridge/example.py'])
    def test_hardlink_rejected(self):
        self.prepare();os.link(self.dest/'tools/notion_bridge/example.py',self.dest/'hardlink')
        with self.assertRaises(d.Blocked):d.snapshot(self.dest)

class Persistence(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.db=d.open_db(self.root/'jobs.sqlite')
        self.addCleanup(self.db.close)
    def test_dedupe_preserves_completed_result_after_reopen(self):
        j=manifest();d.accept(self.db,j,31,NOW);d.transition(self.db,j['id'],'REVIEW_READY',NOW,result={'commit':SHA})
        d.accept(self.db,j,31,NOW+10)
        self.assertEqual(d.job_row(self.db,j['id'])['status'],'REVIEW_READY')
        other=d.open_db(self.root/'jobs.sqlite')
        try:self.assertEqual(d.job_row(other,j['id'])['result']['commit'],SHA)
        finally:other.close()
    def test_drift_cannot_replace_existing_revision(self):
        j=manifest();d.accept(self.db,j,31,NOW);j['task']='changed'
        with self.assertRaises(d.Blocked):d.accept(self.db,j,31,NOW)
    def test_backoff_blocks_until_due_without_losing_job(self):
        d.accept(self.db,manifest(),31,NOW)
        d.retry(self.db,'accept-1','NETWORK',NOW,policy())
        self.assertEqual(d.ready(self.db,NOW+59),[])
        self.assertEqual([j['id'] for j in d.ready(self.db,NOW+60)],['accept-1'])
    def test_retries_are_bounded_and_quota_waits(self):
        d.accept(self.db,manifest(),31,NOW)
        for n in range(3):
            self.db.execute('UPDATE jobs SET attempts=? WHERE id=?',(n+1,'accept-1'));self.db.commit()
            d.retry(self.db,'accept-1','NETWORK',NOW,policy())
        self.assertEqual(d.job_row(self.db,'accept-1')['status'],'FAILED')
        self.assertEqual(d.classify_failure(1,'','Error: quota exceeded'),'QUOTA')
        self.assertEqual(d.classify_failure(0,'quoted quota exceeded',''),'OK')
    def test_blocked_job_does_not_prevent_independent_job(self):
        d.accept(self.db,manifest(),31,NOW);d.transition(self.db,'accept-1','BLOCKED',NOW,reason='NO_GRANT')
        j=manifest();j['id']='accept-2';d.accept(self.db,j,32,NOW)
        self.assertEqual([j['id'] for j in d.ready(self.db,NOW)],['accept-2'])
    def test_crashed_dirty_worker_is_explicitly_blocked(self):
        d.accept(self.db,manifest(),31,NOW);d.transition(self.db,'accept-1','RUNNING',NOW,result={'pid':99999999,'boot_id':'old','start_ticks':'0','phase':'MODEL'})
        d.recover(self.db,NOW)
        self.assertEqual(d.job_row(self.db,'accept-1')['status'],'BLOCKED')
        self.assertIn('RECOVERY',d.job_row(self.db,'accept-1')['reason'])
    def test_live_worker_identity_is_not_relaunched(self):
        d.accept(self.db,manifest(),31,NOW);d.transition(self.db,'accept-1','RUNNING',NOW,result={**d.process_identity(os.getpid()),'phase':'MODEL'})
        d.recover(self.db,NOW)
        self.assertEqual(d.job_row(self.db,'accept-1')['status'],'RUNNING')
    def test_done_requires_explicit_acceptance(self):
        d.accept(self.db,manifest(),31,NOW)
        with self.assertRaises(d.Blocked):d.transition(self.db,'accept-1','DONE',NOW)



class PollingAndQuota(unittest.TestCase):
    setUp=Persistence.setUp
    def test_terminal_jobs_do_not_refetch_or_relaunch(self):
        j=manifest();d.accept(self.db,j,31,NOW)
        d.transition(self.db,j['id'],'REVIEW_READY',NOW,result={'commit':SHA})
        with patch.object(d.time,'time',return_value=NOW),patch.object(d,'fetch_issue',side_effect=AssertionError('terminal job refetched')),patch.object(d,'execute') as execute:
            d.poll(self.db,self.root,policy())
            execute.assert_not_called()
        record=d.job_row(self.db,j['id'])
        self.assertEqual(record['status'],'REVIEW_READY')
        self.assertEqual(record['attempts'],0)

    def test_one_poll_executes_second_job_without_restart(self):
        one=manifest();two=manifest();two['id']='accept-2';two['depends_on']=['accept-1']
        p=policy();p['grants']['accept-2']={'issue':32,'digest':d.digest(two),'expires_at':NOW+3600}
        issues={31:issue(one),32:{**issue(two),'number':32}}
        seen=[]
        def execute(db,row,root,policy):
            seen.append(row['id']);d.transition(db,row['id'],'REVIEW_READY',NOW,result={'commit':SHA})
        with patch.object(d.time,'time',return_value=NOW),patch.object(d,'fetch_issue',side_effect=lambda number:issues[number]),patch.object(d,'execute',side_effect=execute):
            d.poll(self.db,self.root,p);d.poll(self.db,self.root,p)
        self.assertEqual(seen,['accept-1','accept-2'])
    def test_github_403_rate_limit_is_persisted_and_avoids_refetch(self):
        err=d.urllib.error.HTTPError('https://api.github.com/issue/31',403,'rate limit',
            {'X-RateLimit-Remaining':'0','X-RateLimit-Reset':str(NOW+900)},None)
        with patch.object(d.time,'time',return_value=NOW),patch.object(d.urllib.request,'urlopen',side_effect=err),patch.object(d,'execute') as execute:
            d.poll(self.db,self.root,policy())
            execute.assert_not_called()
        saved=self.db.execute("SELECT value FROM meta WHERE key='github_rate_limit_until'").fetchone()
        self.assertIsNotNone(saved,'HTTP 403 quota reset must persist across invocations')
        self.assertGreaterEqual(float(saved[0]),NOW+900)
        with patch.object(d.time,'time',return_value=NOW+10),patch.object(d,'fetch_issue',side_effect=AssertionError('fetched during cooldown')):
            d.poll(self.db,self.root,policy())

    def test_systemd_timer_respects_unauthenticated_rate_budget(self):
        timer=(Path(__file__).parent/'systemd'/'tse-notion-bridge.timer').read_text()
        self.assertIn('OnUnitInactiveSec=300s',timer)

    def test_quota_pauses_all_models_but_preserves_queue(self):
        d.accept(self.db,manifest(),31,NOW)
        d.retry(self.db,'accept-1','QUOTA',NOW,policy())
        self.assertGreaterEqual(d.cooldown(self.db),NOW+3600)
    def test_publish_phase_can_be_retried_without_model(self):
        d.accept(self.db,manifest(),31,NOW)
        d.transition(self.db,'accept-1','RUNNING',NOW,result={'phase':'PUBLISH','commit':SHA})
        d.retry(self.db,'accept-1','PUBLISH_NETWORK',NOW,policy())
        self.assertEqual(d.job_row(self.db,'accept-1')['result']['commit'],SHA)

class FreshPolicy(unittest.TestCase):
 def test_reload_detects_disk_revocation(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'policy.json';p.write_text(json.dumps({'grants':{}}))
   self.assertEqual(d.fresh_policy({'_path':str(p),'grants':{'old':1}})['grants'],{})
 def test_empty_remote_ref_is_failed_verification(self):
  self.assertFalse(d.published_ref_matches('',SHA))
  self.assertFalse(d.published_ref_matches('b'*40+'\trefs/heads/job',SHA))
  self.assertTrue(d.published_ref_matches(SHA+'\trefs/heads/job',SHA))
 def test_status_never_creates_missing_state(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'missing'
   self.assertEqual(d.read_status(root)['jobs'],[])
   self.assertFalse(root.exists())
 def test_status_does_not_modify_database_or_create_status_file(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);db=d.open_db(root/'jobs.sqlite');d.accept(db,manifest(),31,NOW);db.close()
   before=(root/'jobs.sqlite').read_bytes()
   self.assertEqual(d.read_status(root)['jobs'][0]['id'],'accept-1')
   self.assertEqual((root/'jobs.sqlite').read_bytes(),before)
   self.assertFalse((root/'status.json').exists())

class ReviewRegressions(unittest.TestCase):
 setUp=Persistence.setUp
 def test_revoked_live_orphan_prevents_second_model(self):
  one=manifest();two=manifest();two['id']='accept-2'
  p=policy(two);p['grants'][one['id']]={'issue':31,'digest':d.digest(one),'expires_at':NOW-1}
  p['grants'][two['id']]['issue']=32
  d.accept(self.db,one,31,NOW)
  d.transition(self.db,one['id'],'RUNNING',NOW,result={**d.process_identity(os.getpid()),'phase':'MODEL'})
  with patch.object(d.time,'time',return_value=NOW),patch.object(d,'fetch_issue',side_effect=lambda n:issue(one) if n==31 else {**issue(two),'number':32}),patch.object(d,'execute') as execute:
   d.poll(self.db,self.root,p)
   execute.assert_not_called()
 def test_bad_scope_is_blocked_not_uncaught_type_error(self):
  j=manifest();j['scope']=[{}]
  with self.assertRaises(d.Blocked):d.authorize(issue(j),policy(j),NOW)
 def test_fake_python_test_runner_is_rejected(self):
  j=manifest();j['tests']=[['python3','-B','-c','pass','unittest']]
  with self.assertRaises(d.Blocked):d.authorize(issue(j),policy(j),NOW)
 def test_zero_tests_and_all_skipped_are_not_acceptance(self):
  self.assertFalse(d.tests_passed(0,'','Ran 0 tests in 0.01s\n\nOK\n'))
  self.assertFalse(d.tests_passed(0,'','Ran 3 tests in 0.01s\n\nOK (skipped=3)\n'))
  self.assertTrue(d.tests_passed(0,'','Ran 3 tests in 0.01s\n\nOK\n'))
 def test_detached_term_ignoring_child_is_reaped(self):
  d.enable_subreaper();baseline=set(d.descendants())
  code="import os,signal,time; p=os.fork(); (os._exit(0) if p else None); os.setsid(); signal.signal(signal.SIGTERM,signal.SIG_IGN); print(os.getpid(),flush=True); time.sleep(30)"
  p=subprocess.Popen(['python3','-c',code],stdout=subprocess.PIPE,text=True)
  child=int(p.stdout.readline());p.wait();p.stdout.close()
  identity=d.process_identity(child)
  self.assertTrue(identity)
  d.cleanup_children(baseline)
  self.assertFalse(d.identity_alive(identity))



class Completion(unittest.TestCase):
 setUp=Persistence.setUp
 def test_review_ready_does_not_become_done_without_integration_acceptance(self):
  j=manifest();d.accept(self.db,j,31,NOW);d.transition(self.db,j['id'],'REVIEW_READY',NOW,result={'commit':SHA,'tests':[{'exit_code':0}]})
  with self.assertRaises(d.Blocked):d.mark_done(self.db,j['id'],{},True,NOW)
  p={'integration_acceptance':{j['id']:{'commit':SHA,'digest':d.digest(j),'evidence':['reviewed-and-integrated']}}}
  with self.assertRaises(d.Blocked):d.mark_done(self.db,j['id'],p,False,NOW)
  d.mark_done(self.db,j['id'],p,True,NOW)
  self.assertEqual(d.job_row(self.db,j['id'])['status'],'DONE')



class SandboxCleanup(unittest.TestCase):
 def test_test_runner_detached_children_are_reaped(self):
  d.enable_subreaper();baseline=set(d.descendants());identities=[]
  def external_command(*args,**kw):
   code="import os,signal,time; p=os.fork(); (os._exit(0) if p else None); os.setsid(); signal.signal(signal.SIGTERM,signal.SIG_IGN); print(os.getpid(),flush=True); time.sleep(30)"
   p=subprocess.Popen(['python3','-c',code],stdout=subprocess.PIPE,text=True)
   child=int(p.stdout.readline());p.wait();p.stdout.close();identities.append(d.process_identity(child))
   return subprocess.CompletedProcess([],0,'','Ran 1 test in 0.1s\n\nOK\n')
  try:
   with tempfile.TemporaryDirectory() as tmp,patch.object(d,'command',side_effect=external_command):
    root=Path(tmp);d.sandbox(root,[],root,['python3','-B','-m','unittest'])
   self.assertFalse(d.identity_alive(identities[0]))
  finally:d.cleanup_children(baseline)



class StickyRecovery(unittest.TestCase):
 setUp=Persistence.setUp
 def test_expired_grant_cannot_erase_uninspected_recovery_lock(self):
  one=manifest();two=manifest();two['id']='accept-2'
  p=policy(two);p['grants'][one['id']]={'issue':31,'digest':d.digest(one),'expires_at':NOW-1};p['grants'][two['id']]['issue']=32
  d.accept(self.db,one,31,NOW);d.transition(self.db,one['id'],'RUNNING',NOW,result={'pid':99999999,'start_ticks':'0','boot_id':'old','phase':'MODEL'})
  with patch.object(d.time,'time',return_value=NOW),patch.object(d,'fetch_issue',side_effect=lambda n:issue(one) if n==31 else {**issue(two),'number':32}),patch.object(d,'execute') as execute:
   d.poll(self.db,self.root,p);execute.assert_not_called()

class WindowsGitHubManifest(unittest.TestCase):
 def test_github_crlf_body_preserves_exact_manifest_digest(self):
  i=issue();i['body']=i['body'].replace('\n','\r\n')
  self.assertEqual(d.digest(d.authorize(i,policy(),NOW)),d.digest(manifest()))

if __name__=='__main__':unittest.main()
