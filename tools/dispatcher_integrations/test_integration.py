"""Cross-adapter integration fixtures: zero external requests."""
import json
import tempfile
import unittest
from pathlib import Path
from api_transport import HTTPSClient, AuthenticationError, RetryDeferred
from contracts import AuthorizationError, DeliveryLedger, status_event
from github_adapter import GitHubAdapter
from notion_adapter import NotionAdapter, observe_status
from test_authority import issue,policy,NOW
from test_notion_adapter import UUID,DB,page

class Response:
    def __init__(self,data,status=200):
        self.status=status;self.headers={};self.data=json.dumps(data).encode()
    def __enter__(self):return self
    def __exit__(self,*a):return False
    def read(self,size=-1):return self.data if size<0 else self.data[:size]

class Router:
    def __init__(self,github=None,notion=None):
        self.github=github;self.notion=notion;self.requests=[]
    def open(self,req,timeout=None):
        self.requests.append(req)
        if req.full_url.startswith('https://api.github.com/'):return Response(self.github)
        if req.full_url.startswith('https://api.notion.com/'):return Response(self.notion)
        raise AssertionError('foreign URL')

class EndToEndContracts(unittest.TestCase):
    def test_public_package_import_from_repo_root(self):
        import subprocess
        import sys
        repo=Path(__file__).resolve().parents[2]
        command='from tools.dispatcher_integrations.github_adapter import GitHubAdapter; from tools.dispatcher_integrations.notion_adapter import NotionAdapter'
        result=subprocess.run([sys.executable,'-B','-c',command],cwd=repo,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
    def sources(self,router,notion_token='NOTION_PRIVATE'):
        github=HTTPSClient('api.github.com',lambda:'GH_PRIVATE',self.root/'github.json',opener=router,now=lambda:NOW)
        notion=HTTPSClient('api.notion.com',lambda:notion_token,self.root/'notion.json',opener=router,now=lambda:NOW)
        return GitHubAdapter(github),NotionAdapter(notion)
    def test_two_readonly_sources_need_root_owner_grant(self):
        router=Router(issue(),page());gh,nt=self.sources(router)
        candidate=nt.fetch_candidate(UUID,DB)
        with self.assertRaises(AuthorizationError):gh.fetch_approved_issue(42,{'grants':{}},NOW)
        self.assertEqual(candidate.status,'Wartet')
        self.assertTrue(all(r.get_method()=='GET' for r in router.requests))
        self.assertEqual(len(router.requests),2)
        self.assertNotIn('NOTION_PRIVATE',(self.root/'notion.json').read_text())
    def test_owner_grant_and_duplicate_observation_do_not_duplicate_delivery(self):
        router=Router(issue(),page());gh,nt=self.sources(router)
        candidate=nt.fetch_candidate(UUID,DB);job=gh.fetch_approved_issue(42,policy(),NOW)
        report=observe_status(candidate,job,UUID,worker_status='QUEUED')
        self.assertEqual(report['effect'],'OBSERVATION_ONLY')
        ledger=DeliveryLedger(self.root/'receipts.json')
        self.assertTrue(ledger.record_once(job))
        self.assertFalse(DeliveryLedger(self.root/'receipts.json').record_once(job))
        self.assertEqual(report['identity'],job.identity)
    def test_notion_complete_cannot_bypass_closed_issue(self):
        router=Router(issue(state='closed'),page('Erledigt'));gh,nt=self.sources(router)
        self.assertEqual(nt.fetch_candidate(UUID,DB).status,'Erledigt')
        with self.assertRaises(AuthorizationError):gh.fetch_approved_issue(42,policy(),NOW)
        self.assertEqual(len(router.requests),2)
    def test_notion_token_missing_does_not_block_valid_github_source(self):
        router=Router(issue(),page());gh,nt=self.sources(router,None)
        with self.assertRaises(AuthenticationError):nt.fetch_candidate(UUID,DB)
        job=gh.fetch_approved_issue(42,policy(),NOW)
        self.assertEqual(job.issue_number,42)
        self.assertEqual(len(router.requests),1)
    def test_status_ready_requires_pinned_commit_evidence(self):
        router=Router(issue(),page());gh,_=self.sources(router)
        job=gh.fetch_approved_issue(42,policy(),NOW)
        with self.assertRaises(AuthorizationError):status_event(job,'REVIEW_READY','bad','fake')
        evidence=status_event(job,'REVIEW_READY','1'*40,'portable test log')
        self.assertNotIn('DONE',evidence.values())

if __name__=='__main__':unittest.main()
