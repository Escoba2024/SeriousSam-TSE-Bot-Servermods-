import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from api_transport import HTTPSClient, AuthenticationError, ProtocolError, RetryDeferred, RetryExhausted

class Response:
    def __init__(self, status=200, body=b'{"ok":true}', headers=None):
        self.status=status; self.body=body; self.headers=headers or {}
    def __enter__(self):return self
    def __exit__(self,*a):return False
    def read(self,size=-1):return self.body if size<0 else self.body[:size]

class Fake:
    def __init__(self,*answers):self.answers=list(answers);self.requests=[]
    def open(self,req,timeout=0):
        self.requests.append(req);v=self.answers.pop(0)
        if isinstance(v,Exception):raise v
        return v

def err(code,headers=None):
    return HTTPError('https://api.github.com/a',code,'failure',headers or {},None)

class HTTPTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.state=Path(t.name)/'http.json';self.now=1000.
    def client(self,op,token='SECRET'):
        return HTTPSClient('api.github.com',lambda:token,self.state,opener=op,now=lambda:self.now)
    def test_etag_and_304(self):
        op=Fake(Response(headers={'ETag':'"e1"'}),Response(304,b''))
        c=self.client(op);self.assertEqual(c.get_json('/repos/x/issues/1'),{'ok':True})
        self.assertIsNone(c.get_json('/repos/x/issues/1'))
        self.assertEqual(op.requests[0].get_header('Authorization'),'Bearer SECRET')
        self.assertEqual(op.requests[1].get_header('If-none-match'),'"e1"')
        self.assertNotIn('SECRET',self.state.read_text())
    def test_missing_token_fails_closed(self):
        op=Fake()
        with self.assertRaises(AuthenticationError):self.client(op,'').get_json('/a')
        self.assertFalse(op.requests)
    def test_foreign_hosts_and_redirect_rejected(self):
        op=Fake(Response(302,headers={'Location':'https://evil.example/'}));c=self.client(op)
        for path in ('https://evil.example/','//evil.example/','/../x','/%2e%2e/x'):
            with self.assertRaises(ProtocolError):c.get_json(path)
        with self.assertRaises(ProtocolError):c.get_json('/a')
        self.assertEqual(len(op.requests),1)
    def test_401_and_normal_403_do_not_retry(self):
        for n in (401,403):
            op=Fake(err(n))
            with self.assertRaises(AuthenticationError):self.client(op).get_json('/a')
            self.assertEqual(len(op.requests),1)
    def test_403_limited_persistent_cooldown(self):
        with self.assertRaises(RetryDeferred):self.client(Fake(err(403,{'X-RateLimit-Remaining':'0','X-RateLimit-Reset':'1300'}))).get_json('/a')
        op=Fake(Response())
        with self.assertRaises(RetryDeferred):self.client(op).get_json('/a')
        self.assertFalse(op.requests)
        self.now=1301
        self.assertEqual(self.client(op).get_json('/a'),{'ok':True})
    def test_429_capped_retry_after(self):
        with self.assertRaises(RetryDeferred) as e:self.client(Fake(err(429,{'Retry-After':'99999'}))).get_json('/a')
        self.assertLessEqual(e.exception.retry_at,4600)
    def test_503_exhausts_bounded_retry(self):
        for n in range(3):
            with self.assertRaises(RetryDeferred):self.client(Fake(err(503))).get_json('/a')
            self.now=json.loads(self.state.read_text())['cooldown_until']+1
        with self.assertRaises(RetryExhausted):self.client(Fake()).get_json('/a')
    def test_network_error_deferred_and_token_not_leaked(self):
        with self.assertRaises(RetryDeferred) as e:self.client(Fake(URLError('connection reset'))).get_json('/a')
        self.assertNotIn('SECRET',str(e.exception))
    def test_retry_after_http_date_is_honored(self):
        from email.utils import formatdate
        delayed=formatdate(1400,usegmt=True)
        with self.assertRaises(RetryDeferred) as e:
            self.client(Fake(err(429,{'Retry-After':delayed}))).get_json('/a')
        self.assertGreaterEqual(e.exception.retry_at,1400)
    def test_304_success_clears_prior_transient_failure(self):
        with self.assertRaises(RetryDeferred):self.client(Fake(err(503))).get_json('/a')
        self.now=json.loads(self.state.read_text())['cooldown_until']+1
        self.assertIsNone(self.client(Fake(Response(304,b''))).get_json('/a'))
        self.assertEqual(json.loads(self.state.read_text())['failures'],0)
    def test_invalid_json_rejected(self):
        with self.assertRaises(ProtocolError):self.client(Fake(Response(body=b'bad-json'))).get_json('/a')

if __name__=='__main__':unittest.main()
