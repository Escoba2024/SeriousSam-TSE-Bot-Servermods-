import datetime as dt
import json
import unittest
from notion_dispatch import parse_comment,queue_from_comments,classify_codex_result,skip_completed_review
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

LONG_OUTPUT = "Completed review with a clear review conclusion and evidence. " * 3
class DispatcherOutcomeRegressions(unittest.TestCase):
 def test_complete_review_ready(self):
  self.assertEqual(classify_codex_result(0,LONG_OUTPUT,""),"REVIEW_READY")
 def test_quoted_quota_regex_not_provider_failure(self):
  self.assertEqual(classify_codex_result(0,LONG_OUTPUT+" QUOTA = re.compile('usage limit')",""),"REVIEW_READY")
 def test_quoted_sandbox_regex_not_provider_failure(self):
  self.assertEqual(classify_codex_result(0,LONG_OUTPUT+" SANDBOX_ERROR = re.compile('bwrap:')",""),"REVIEW_READY")
 def test_short_success_not_accepted(self):
  self.assertEqual(classify_codex_result(0,"ok",""),"REVIEW_FAILED")
 def test_failed_cli_actual_quota_on_stderr(self):
  self.assertEqual(classify_codex_result(1,"","Error: quota exceeded"),"BLOCKED_QUOTA")
 def test_failed_cli_actual_sandbox_on_stderr(self):
  self.assertEqual(classify_codex_result(1,"","Error: bwrap: operation not permitted"),"BLOCKED_SANDBOX")
 def test_nonzero_stdout_quote_not_blocked_quota(self):
  self.assertEqual(classify_codex_result(1,"source: QUOTA = re.compile('usage limit')","unknown CLI error"),"REVIEW_FAILED")
 def test_unclassified_failure(self):
  self.assertEqual(classify_codex_result(1,"","other failure"),"REVIEW_FAILED")
 def test_missing_output_fails_closed(self):
  self.assertEqual(classify_codex_result(0,None,None),"REVIEW_FAILED")
 def test_ready_exact_sha_and_event_is_deduplicated(self):
  self.assertTrue(skip_completed_review({"status":"REVIEW_READY","head_sha":"a"*40,"github_comment_id":123},{"github_comment_id":123},"a"*40))
 def test_ready_new_sha_rechecks(self):
  self.assertFalse(skip_completed_review({"status":"REVIEW_READY","head_sha":"a"*40,"github_comment_id":123},{"github_comment_id":123},"b"*40))
 def test_ready_new_event_rechecks(self):
  self.assertFalse(skip_completed_review({"status":"REVIEW_READY","head_sha":"a"*40,"github_comment_id":123},{"github_comment_id":124},"a"*40))
 def test_ready_missing_sha_rechecks(self):
  self.assertFalse(skip_completed_review({"status":"REVIEW_READY","github_comment_id":123},{"github_comment_id":123},"a"*40))
 def test_not_ready_is_not_deduplicated(self):
  self.assertFalse(skip_completed_review({"status":"REVIEW_FAILED","head_sha":"a"*40,"github_comment_id":123},{"github_comment_id":123},"a"*40))

if __name__=="__main__":unittest.main()
