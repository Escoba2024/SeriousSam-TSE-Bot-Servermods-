"""Strict read-only HTTPS transport; no credential, data or state is logged."""
import json
from email.utils import parsedate_to_datetime
import os
from pathlib import Path
import re
import tempfile
import time
from urllib import error, parse, request

class AuthenticationError(RuntimeError): pass
class ProtocolError(RuntimeError): pass
class RetryExhausted(RuntimeError): pass
class RetryDeferred(RuntimeError):
    def __init__(self, retry_at):
        self.retry_at=retry_at
        super().__init__('API retry deferred until %.0f' % retry_at)

class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def _header(headers,key):
    if headers is None:return None
    try:
        value=headers.get(key)
        if value is not None:return str(value)
    except AttributeError:pass
    for k,v in dict(headers).items():
        if k.lower()==key.lower():return str(v)
    return None

class HTTPSClient:
    """Inject opener/clock for offline tests. One request per invocation.

    Retries are time-based across caller polls, never immediate busy loops.
    """
    def __init__(self,host,token_provider,state_path,*,opener=None,now=None,max_failures=3):
        if host not in ('api.github.com','api.notion.com'):
            raise ProtocolError('unapproved API host')
        if not callable(token_provider) or not 1<=max_failures<=10:
            raise ProtocolError('invalid client configuration')
        self.host=host
        self.token_provider=token_provider
        self.state_path=Path(state_path)
        self.opener=opener or request.build_opener(_NoRedirect())
        self.now=now or time.time
        self.max_failures=max_failures

    def _state(self):
        try:
            raw=json.loads(self.state_path.read_text(encoding='utf-8'))
        except FileNotFoundError:return {'cooldown_until':0,'failures':0,'etags':{}}
        except (OSError,ValueError) as exc:raise ProtocolError('invalid local cooldown file') from None
        if (not isinstance(raw,dict) or type(raw.get('failures')) is not int
                or raw['failures']<0 or type(raw.get('cooldown_until')) not in (int,float)
                or not isinstance(raw.get('etags'),dict)):
            raise ProtocolError('invalid local cooldown shape')
        return raw

    def _save(self,value):
        self.state_path.parent.mkdir(parents=True,exist_ok=True)
        name=None
        try:
            with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=self.state_path.parent,
                                              prefix='.api-',delete=False) as stream:
                name=stream.name
                os.chmod(name,0o600)
                json.dump(value,stream,sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name,self.state_path)
        finally:
            if name and os.path.exists(name):os.unlink(name)

    def _defer(self,state,status,headers):
        now=float(self.now())
        failures=state['failures']+1
        state['failures']=failures
        if failures>self.max_failures:
            self._save(state)
            raise RetryExhausted('bounded API retry budget exceeded')
        delay=min(3600,2**(failures-1)*30)
        after=_header(headers,'Retry-After')
        if after and after.isdigit():delay=max(delay,min(3600,int(after)))
        elif after:
            try:
                target=parsedate_to_datetime(after).timestamp()
                delay=max(delay,min(3600,max(0,target-now)))
            except (TypeError,ValueError,OverflowError):pass
        reset=_header(headers,'X-RateLimit-Reset')
        if reset and reset.isdigit() and status in (403,429):
            delay=max(delay,min(3600,max(0,int(reset)-now)))
        state['cooldown_until']=now+max(1,delay)
        self._save(state)
        raise RetryDeferred(state['cooldown_until'])

    @staticmethod
    def _safe_path(path):
        if not isinstance(path,str) or not path.startswith('/') or path.startswith('//'):
            raise ProtocolError('invalid API path')
        parsed=parse.urlsplit(path)
        if parsed.scheme or parsed.netloc or parsed.fragment or re.search(r'[\\\x00-\x1f]',path):
            raise ProtocolError('invalid API URL')
        segments=parse.unquote(parsed.path).split('/')
        if any(s in ('..','.') for s in segments):
            raise ProtocolError('API path traversal')
        return path

    def _not_modified(self,state):
        state['failures']=0
        state['cooldown_until']=0
        self._save(state)
        return None

    def get_json(self,path,*,extra_headers=None):
        path=self._safe_path(path)
        state=self._state()
        if state['failures']>=self.max_failures:
            raise RetryExhausted('bounded API retry budget exceeded')
        if self.now()<state['cooldown_until']:
            raise RetryDeferred(state['cooldown_until'])
        try:token=self.token_provider()
        except Exception:raise AuthenticationError('API credential unavailable') from None
        if not isinstance(token,str) or not token.strip() or re.search(r'[\r\n]',token):
            raise AuthenticationError('API credential unavailable')
        headers={'Authorization':'Bearer '+token,'User-Agent':'TSE-D1-Adapter/1.0',
                 'Accept':'application/json'}
        if path in state['etags']:headers['If-None-Match']=state['etags'][path]
        for key,value in (extra_headers or {}).items():
            if key!='Notion-Version' or not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):
                raise ProtocolError('unapproved extra header')
            headers[key]=value
        req=request.Request('https://'+self.host+path,headers=headers,method='GET')
        try:
            with self.opener.open(req,timeout=20) as result:
                code=result.status
                if code==304:return self._not_modified(state)
                if code!=200:raise ProtocolError('unexpected HTTP status')
                data=result.read(2_000_001)
                if len(data)>2_000_000:raise ProtocolError('oversized API response')
                try:parsed=json.loads(data)
                except (ValueError,UnicodeError):raise ProtocolError('invalid JSON API response') from None
                if not isinstance(parsed,(dict,list)):raise ProtocolError('invalid response shape')
                etag=_header(result.headers,'ETag')
                if etag and len(etag)<200 and '\n' not in etag:
                    state['etags'][path]=etag
                state['failures']=0
                state['cooldown_until']=0
                self._save(state)
                return parsed
        except error.HTTPError as exc:
            if exc.code==304:return self._not_modified(state)
            if exc.code in (401,403) and (exc.code==401 or _header(exc.headers,'X-RateLimit-Remaining')!='0'):
                raise AuthenticationError('API permission denied') from None
            if exc.code in (429,403) or 500<=exc.code<600:
                self._defer(state,exc.code,exc.headers)
            raise ProtocolError('unexpected HTTP error') from None
        except error.URLError:
            self._defer(state,503,None)
