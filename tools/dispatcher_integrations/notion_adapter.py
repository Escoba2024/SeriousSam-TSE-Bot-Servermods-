"""Notion read-only observations, never execution grants or D0 transitions."""
from dataclasses import dataclass
import datetime as dt
import re
if __package__:
    from .contracts import ApprovedJob, AuthorizationError
else:
    from contracts import ApprovedJob, AuthorizationError

_UUID=re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z')
_STATES={'Wartet':'NOTION_WAITING','Freigabe fehlt':'NOTION_NO_GRANT',
         'Gesperrt':'NOTION_BLOCKED','Läuft':'NOTION_RUNNING',
         'Review':'NOTION_REVIEW','Erledigt':'NOTION_REPORTED_COMPLETE'}

class NotionError(RuntimeError):pass

@dataclass(frozen=True)
class NotionCandidate:
    page_id:str
    data_source_id:str
    status:str
    edited_at:dt.datetime

def _date(value):
    try:
        if not isinstance(value,str):raise ValueError
        date=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
        if date.tzinfo is None or date.utcoffset() is None:raise ValueError
        return date.astimezone(dt.timezone.utc)
    except (TypeError,ValueError,OverflowError):
        raise NotionError('missing or invalid notion revision') from None

class NotionAdapter:
    def __init__(self,client):self.client=client
    def fetch_candidate(self,page_id,expected_source_id):
        if (not isinstance(page_id,str) or not _UUID.fullmatch(page_id)
                or not isinstance(expected_source_id,str) or not _UUID.fullmatch(expected_source_id)):
            raise NotionError('invalid pinned notion identifiers')
        data=self.client.get_json('/v1/pages/'+page_id,extra_headers={'Notion-Version':'2022-06-28'})
        if not isinstance(data,dict):raise NotionError('missing or stale notion snapshot')
        parent=data.get('parent') or {}
        if (data.get('object')!='page' or data.get('id')!=page_id
                or not isinstance(parent,dict) or parent.get('type')!='data_source_id'
                or parent.get('data_source_id')!=expected_source_id):
            raise NotionError('foreign notion page or data source')
        fields=data.get('properties') or {}
        raw=fields.get('Status') or {}
        value=(raw.get('status') or {}).get('name') if isinstance(raw,dict) else None
        if value not in _STATES:raise NotionError('invalid notion status')
        return NotionCandidate(page_id,expected_source_id,value,_date(data.get('last_edited_time')))

def observe_status(candidate,approved,expected_page_id,*,worker_status,known_edit_time=None):
    if not isinstance(approved,ApprovedJob):raise AuthorizationError('GitHub owner grant required')
    if not isinstance(candidate,NotionCandidate) or candidate.page_id!=expected_page_id:
        raise AuthorizationError('notion page mismatch')
    if worker_status not in ('QUEUED','RUNNING','BLOCKED','FAILED','REVIEW_READY','DONE'):
        raise NotionError('invalid actual worker status')
    if known_edit_time is not None:
        if not isinstance(known_edit_time,dt.datetime) or known_edit_time.tzinfo is None:
            raise NotionError('invalid known revision')
        if candidate.edited_at<known_edit_time:
            raise NotionError('outdated notion status revision')
    effect=('STALE_NOTION_REQUIRES_REVIEW'
            if candidate.status=='Wartet' and worker_status in ('REVIEW_READY','DONE')
            else 'OBSERVATION_ONLY')
    return {'identity':approved.identity,'notion_page_id':candidate.page_id,
            'source_revision':candidate.edited_at.isoformat(),'observed_status':_STATES[candidate.status],
            'worker_status_observed':worker_status,'effect':effect}
