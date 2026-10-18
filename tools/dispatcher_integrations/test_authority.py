import json
import tempfile
import unittest
from pathlib import Path
from contracts import authorize_job, manifest_digest, DeliveryLedger, AuthorizationError, status_event
from github_adapter import GitHubAdapter

SHA='a'*40
NOW=10000
def manifest():
    return {'id':'integration-job','revision':1,'base_sha':SHA,
            'scope':['tools/notion_bridge/README.md'],'task':'Repair exact adapter contract.',
            'tests':[['python3','-B','-m','unittest','discover','-s','tools/notion_bridge','-p','test_*.py']],
            'priority':10,'depends_on':[]}
def issue(j=None,author='Escoba2024',state='open',number=42):
    j=manifest() if j is None else j
    return {'number':number,'state':state,'user':{'login':author},'body':'TSE_DEV_JOB_V1\n'+json.dumps(j)}
def policy(j=None):
    j=manifest() if j is None else j
    return {'grants':{j['id']:{'issue':42,'digest':manifest_digest(j),'expires_at':NOW+3600}}}

class AuthorityTests(unittest.TestCase):
    def test_exact_owner_grant_and_immutable_key(self):
        a=authorize_job(issue(),policy(),NOW)
        self.assertEqual(a.issue_number,42);self.assertEqual(a.base_sha,SHA)
        self.assertEqual(a.manifest_hash,manifest_digest(manifest()))
        self.assertEqual(a.identity,authorize_job(issue(),policy(),NOW).identity)
    def test_foreign_author_closed_or_no_grant_denied(self):
        for i,p in [(issue(author='other'),policy()),(issue(state='closed'),policy()),
                    (issue(),{'grants':{}}),(issue(number=43),policy())]:
            with self.assertRaises(AuthorizationError):authorize_job(i,p,NOW)
    def test_expired_overlong_and_bool_expiry_denied(self):
        for expiry in (NOW-1,NOW+14401,True):
            p=policy();p['grants']['integration-job']['expires_at']=expiry
            with self.assertRaises(AuthorizationError):authorize_job(issue(),p,NOW)
    def test_manifest_edits_and_invalid_scope_denied(self):
        changed=manifest();changed['task']='Altered manifest after grant.'
        with self.assertRaises(AuthorizationError):authorize_job(issue(changed),policy(),NOW)
        for scope in (['tools/notion_bridge/../../out'],['src/other.py'],['tools/notion_bridge/.hidden']):
            j=manifest();j['scope']=scope
            with self.assertRaises(AuthorizationError):authorize_job(issue(j),policy(j),NOW)
    def test_replay_persists_and_drift_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'ledger.json'
            ledger=DeliveryLedger(path);a=authorize_job(issue(),policy(),NOW)
            self.assertTrue(ledger.record_once(a))
            self.assertFalse(DeliveryLedger(path).record_once(a))
            j=manifest();j['revision']=2
            newer=authorize_job(issue(j),policy(j),NOW)
            with self.assertRaises(AuthorizationError):DeliveryLedger(path).record_once(newer)
    def test_status_is_only_preview_and_done_never_minted(self):
        a=authorize_job(issue(),policy(),NOW)
        with self.assertRaises(AuthorizationError):status_event(a,'DONE',SHA,'merged')
        with self.assertRaises(AuthorizationError):status_event(a,'REVIEW_READY','',None)
        preview=status_event(a,'REVIEW_READY',SHA,'test log')
        self.assertEqual(preview['identity'],a.identity)
        self.assertEqual(preview['status'],'REVIEW_READY')
        self.assertNotIn('github_post',preview)
    def test_github_client_reads_only_pinned_issue(self):
        class Client:
            def __init__(self):self.paths=[]
            def get_json(self,p):self.paths.append(p);return issue()
        client=Client()
        adapter=GitHubAdapter(client)
        got=adapter.fetch_approved_issue(42,policy(),NOW)
        self.assertEqual(got.issue_number,42)
        self.assertEqual(client.paths,['/repos/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/42'])
        for n in (0,-1,True,'42'):
            with self.assertRaises(AuthorizationError):adapter.fetch_approved_issue(n,policy(),NOW)
    def test_github_304_cannot_mint_new_job(self):
        class Client:
            def get_json(self,p):return None
        with self.assertRaises(AuthorizationError):GitHubAdapter(Client()).fetch_approved_issue(42,policy(),NOW)
    def test_wrong_issue_number_response_denied(self):
        class Client:
            def get_json(self,p):return issue(number=999)
        with self.assertRaises(AuthorizationError):GitHubAdapter(Client()).fetch_approved_issue(42,policy(),NOW)

if __name__=='__main__':unittest.main()
