"""Optional Notion mirror of GitHub jobs; never an authorization source."""
import json
import re
import urllib.error
import urllib.request

DATA_SOURCE='8719ec1b-4ffb-4de7-8193-dd43842ebc68'
ISSUE=re.compile(r'https://github\.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/([1-9][0-9]*)\Z')
class NotionUnavailable(RuntimeError):pass

def linked_issue(row):
    p=row.get('properties',{})
    if (p.get('Modus',{}).get('select') or {}).get('name')!='Code mit Grant':return None
    if (p.get('Status',{}).get('status') or {}).get('name')!='Wartet':return None
    m=ISSUE.fullmatch(p.get('GitHub-Grant',{}).get('url') or '')
    return int(m[1]) if m else None

class NotionClient:
    def __init__(self,token=None,fixture=None):
        self.token=token;self.fixture=fixture;self.rows=[]
    def request(self,method,path,body):
        if not self.token:raise NotionUnavailable('NOTION_SERVER_TOKEN_MISSING')
        req=urllib.request.Request('https://api.notion.com/v1/'+path,data=json.dumps(body).encode(),method=method,headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json','Notion-Version':'2025-09-03'})
        try:
            with urllib.request.urlopen(req,timeout=20) as response:return json.load(response)
        except urllib.error.HTTPError as e:raise NotionUnavailable('NOTION_HTTP_'+str(e.code)) from None
        except (OSError,ValueError):raise NotionUnavailable('NOTION_UNAVAILABLE') from None
    def issue_links(self):
        if self.fixture is not None:self.rows=self.fixture['results']
        else:
            self.rows=[];body={'page_size':100}
            for _ in range(20):
                data=self.request('POST','data_sources/'+DATA_SOURCE+'/query',body)
                self.rows+=data['results']
                if not data.get('has_more'):break
                if not data.get('next_cursor'):raise NotionUnavailable('NOTION_MALFORMED_PAGINATION')
                body['start_cursor']=data['next_cursor']
            else:raise NotionUnavailable('NOTION_PAGINATION_CAP')
        return sorted({n for row in self.rows if (n:=linked_issue(row)) is not None})
    def report(self,page_id,state,evidence,attempts,error):
        if not re.fullmatch(r'[0-9a-f-]{36}',page_id):raise NotionUnavailable('INVALID_PAGE_ID')
        statuses={'QUEUED':'Wartet','RUNNING':'Läuft','BLOCKED':'Gesperrt','FAILED':'Gesperrt','REVIEW_READY':'Review','DONE':'Erledigt'}
        properties={'Status':{'status':{'name':statuses[state]}},'Wiederholungen':{'number':attempts},'Letzter Fehler':{'rich_text':[{'text':{'content':error[:1000]}}]},'Letzter Nachweis':{'url':evidence or None}}
        value={'properties':properties}
        if self.fixture is not None:return value
        return self.request('PATCH','pages/'+page_id,value)
