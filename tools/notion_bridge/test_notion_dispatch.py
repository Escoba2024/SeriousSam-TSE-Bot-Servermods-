import datetime as dt
import json
import unittest
from notion_dispatch import parse_comment,queue_from_comments
T=dt.datetime(2026,10,17,9,0,tzinfo=dt.timezone.utc)
D={"source":"notion_mcp_bridge","notion_page_id":"3fc90f11-bec8-818d-9c36-f344c353d454","job_id":3,"pr_number":28,"kind":"pr_readonly_review","mode":"Read-only Codex","status":"Wartet"}
def c(d=None,**extras):
 a={"user":{"login":"Escoba2024"},"body":"NOTION_BRIDGE_JOB_V1\\n".replace("\\n","\n")+json.dumps(d if d is not None else D),"created_at":"2026-10-17T08:58:00Z","id":5}
 a.update(extras)
 return a
class SafeBridge(unittest.TestCase):
 def test_allow(self):self.assertEqual(parse_comment(c(),T)["pr_number"],28)
 def test_other_author(self):self.assertIsNone(parse_comment(c(user={"login":"stranger"}),T))
 def test_expired(self):self.assertIsNone(parse_comment(c(created_at="2026-10-17T01:00:00Z"),T))
 def test_future(self):self.assertIsNone(parse_comment(c(created_at="2026-10-17T10:00:00Z"),T))
 def test_no_code_writes(self):self.assertIsNone(parse_comment(c({**D,"mode":"Code mit Grant"}),T))
 def test_no_blocked(self):self.assertIsNone(parse_comment(c({**D,"status":"Gesperrt"}),T))
 def test_no_injected_extra(self):self.assertIsNone(parse_comment(c({**D,"shell":"rm"}),T))
 def test_no_traversal(self):self.assertIsNone(parse_comment(c({**D,"notion_page_id":"../tmp"}),T))
 def test_no_boolean_pr(self):self.assertIsNone(parse_comment(c({**D,"pr_number":True}),T))
 def test_dedupe(self):self.assertEqual(queue_from_comments([c(id=5),c(id=9)],T)[0]["github_comment_id"],9)
 def test_no_nonqueued(self):self.assertEqual(queue_from_comments([c({**D,"status":"Review"})],T),[])
 def test_newer_review_cancels_wait(self):
  self.assertEqual(queue_from_comments([c(id=5),c({**D,"status":"Review"},id=9)],T),[])
 def test_all_terminal_statuses_cancel_wait(self):
  for terminal in ("Gesperrt","Freigabe fehlt","Läuft","Review","Erledigt"):
   with self.subTest(terminal=terminal):
    self.assertEqual(queue_from_comments([c(id=5),c({**D,"status":terminal},id=9)],T),[])
 def test_newer_wait_reopens_after_cancellation(self):
  jobs=queue_from_comments([c(id=5),c({**D,"status":"Gesperrt"},id=7),c(id=9)],T)
  self.assertEqual([x["github_comment_id"] for x in jobs],[9])
 def test_untrusted_cancellation_cannot_override_owner_wait(self):
  jobs=queue_from_comments([c(id=5),c({**D,"status":"Review"},id=9,user={"login":"outsider"})],T)
  self.assertEqual([x["github_comment_id"] for x in jobs],[5])
 def test_malformed_cancellation_cannot_override_owner_wait(self):
  jobs=queue_from_comments([c(id=5),c({**D,"status":"Review","command":"run"},id=9)],T)
  self.assertEqual([x["github_comment_id"] for x in jobs],[5])
 def test_no_invalid_json(self):self.assertIsNone(parse_comment(c(body="NOTION_BRIDGE_JOB_V1\\n{"),T))
if __name__=="__main__":unittest.main()
