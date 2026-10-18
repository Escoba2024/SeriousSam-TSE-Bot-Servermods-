import datetime as dt
import tempfile
import unittest
from pathlib import Path
from notion_adapter import NotionAdapter, NotionError, observe_status
from contracts import ApprovedJob, AuthorizationError
from api_transport import HTTPSClient, AuthenticationError

UUID='3fc90f11-bec8-812b-a377-fdb1c396fbcd'
DB='8719ec1b-4ffb-4de7-8193-dd43842ebc68'
STAMP='2026-10-17T14:42:28Z'
def page(status='Wartet',parent=DB,edited=STAMP):
    return {'object':'page','id':UUID,'parent':{'type':'data_source_id','data_source_id':parent},
            'last_edited_time':edited,'properties':{'Status':{'type':'status','status':{'name':status}}}}
def job():
    return ApprovedJob(42,'integration-job',1,'a'*40,'b'*64,'c'*64)

class FakeClient:
    def __init__(self,result):self.result=result;self.calls=[]
    def get_json(self,path,**kw):self.calls.append((path,kw));return self.result

class NotionTests(unittest.TestCase):
    def test_valid_readonly_page_observation(self):
        c=FakeClient(page())
        candidate=NotionAdapter(c).fetch_candidate(UUID,DB)
        self.assertEqual(candidate.status,'Wartet')
        self.assertEqual(c.calls,[('/v1/pages/'+UUID,{'extra_headers':{'Notion-Version':'2022-06-28'}})])
        out=observe_status(candidate,job(),UUID,worker_status='QUEUED')
        self.assertEqual(out['effect'],'OBSERVATION_ONLY')
        self.assertEqual(out['identity'],job().identity)
    def test_notion_done_never_means_worker_done(self):
        candidate=NotionAdapter(FakeClient(page('Erledigt'))).fetch_candidate(UUID,DB)
        out=observe_status(candidate,job(),UUID,worker_status='REVIEW_READY')
        self.assertNotEqual(out['observed_status'],'DONE')
        self.assertNotIn('DONE',out.values())
    def test_stale_notions_wait_cannot_resubmit_ready_job(self):
        candidate=NotionAdapter(FakeClient(page())).fetch_candidate(UUID,DB)
        out=observe_status(candidate,job(),UUID,worker_status='REVIEW_READY')
        self.assertEqual(out['effect'],'STALE_NOTION_REQUIRES_REVIEW')
    def test_foreign_parent_and_invalid_status_rejected(self):
        for value in (page(parent='f'*36),page(status='Start now'),page(edited='not-a-date')):
            with self.assertRaises(NotionError):NotionAdapter(FakeClient(value)).fetch_candidate(UUID,DB)
    def test_cross_page_observation_denied(self):
        candidate=NotionAdapter(FakeClient(page())).fetch_candidate(UUID,DB)
        with self.assertRaises(AuthorizationError):observe_status(candidate,job(),'1'*36,worker_status='QUEUED')
    def test_unconditional_not_modified_fails_closed(self):
        with self.assertRaises(NotionError):NotionAdapter(FakeClient(None)).fetch_candidate(UUID,DB)
    def test_invalid_page_id_denied_before_http(self):
        c=FakeClient(page())
        with self.assertRaises(NotionError):NotionAdapter(c).fetch_candidate('../x',DB)
        self.assertFalse(c.calls)
    def test_missing_notion_token_fails_closed_no_network(self):
        class Opener:
            def open(self,*a,**k):raise AssertionError('network should not run')
        with tempfile.TemporaryDirectory() as tmp:
            client=HTTPSClient('api.notion.com',lambda:None,Path(tmp)/'state.json',opener=Opener())
            with self.assertRaises(AuthenticationError):NotionAdapter(client).fetch_candidate(UUID,DB)
    def test_stale_event_timestamp_denied(self):
        candidate=NotionAdapter(FakeClient(page())).fetch_candidate(UUID,DB)
        with self.assertRaises(NotionError):
            observe_status(candidate,job(),UUID,worker_status='QUEUED',known_edit_time=dt.datetime(2026,10,18,tzinfo=dt.timezone.utc))
    def test_cannot_report_done_based_on_notion_only(self):
        candidate=NotionAdapter(FakeClient(page('Erledigt'))).fetch_candidate(UUID,DB)
        self.assertEqual(observe_status(candidate,job(),UUID,worker_status='QUEUED')['effect'],'OBSERVATION_ONLY')

if __name__=='__main__':unittest.main()
