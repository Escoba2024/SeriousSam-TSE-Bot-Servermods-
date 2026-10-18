import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import notion_adapter as n

class Adapter(unittest.TestCase):
 def row(self):
  return {'id':'3fc90f11-bec8-812b-a377-fdb1c396fbcd','properties':{'Modus':{'select':{'name':'Code mit Grant'}},'Status':{'status':{'name':'Wartet'}},'GitHub-Grant':{'url':'https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/issues/31'}}}
 def test_mirror_links_to_github_and_never_grants_itself(self):
  self.assertEqual(n.linked_issue(self.row()),31)
  row=self.row();row['properties']['GitHub-Grant']['url']='https://github.com/other/repo/issues/31'
  self.assertIsNone(n.linked_issue(row))
 def test_review_and_runtime_rows_are_not_executable(self):
  for status in ('Gesperrt','Erledigt','Review','Freigabe fehlt'):
   row=self.row();row['properties']['Status']['status']['name']=status
   self.assertIsNone(n.linked_issue(row))
 def test_fixture_reads_and_updates_existing_schema(self):
  rows=[self.row()]
  client=n.NotionClient(token=None,fixture={'results':rows})
  self.assertEqual(client.issue_links(),[31])
  updated=client.report(rows[0]['id'],'REVIEW_READY','https://github.com/Escoba2024/SeriousSam-TSE-Bot-Servermods-/commit/'+'a'*40,1,'')
  self.assertEqual(updated['properties']['Status']['status']['name'],'Review')
  self.assertNotIn('Erledigt',json.dumps(updated))
 def test_no_token_is_explicit_blocker(self):
  with self.assertRaisesRegex(n.NotionUnavailable,'SERVER_TOKEN_MISSING'):n.NotionClient(token=None).issue_links()
 def test_pagination_and_error_reporting_use_api(self):
  first={'results':[self.row()],'has_more':True,'next_cursor':'next'}
  second={'results':[],'has_more':False}
  client=n.NotionClient(token='fixture-token')
  with patch.object(client,'request',side_effect=[first,second]) as request:
   self.assertEqual(client.issue_links(),[31]);self.assertEqual(request.call_args.args[2]['start_cursor'],'next')

if __name__=='__main__':unittest.main()
