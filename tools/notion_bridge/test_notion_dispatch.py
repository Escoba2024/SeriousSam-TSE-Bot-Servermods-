import datetime as dt
import json
import unittest
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import notion_dispatch as dispatcher
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

def review_json(summary="Review complete"):
 return json.dumps({"status":"reviewed","summary":summary,"findings":[]})

VALID_OUTPUT = review_json()
class DispatcherOutcomeRegressions(unittest.TestCase):
 def test_complete_review_ready(self):
  self.assertEqual(classify_codex_result(0,VALID_OUTPUT,""),"REVIEW_READY")
 def test_quoted_quota_regex_not_provider_failure(self):
  self.assertEqual(classify_codex_result(0,review_json("QUOTA = re.compile('usage limit')"),""),"REVIEW_READY")
 def test_quoted_sandbox_regex_not_provider_failure(self):
  self.assertEqual(classify_codex_result(0,review_json("SANDBOX_ERROR = re.compile('bwrap:')"),""),"REVIEW_READY")
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
 def test_invalid_final_results_fail_closed(self):
  valid=json.loads(VALID_OUTPUT)
  cases=["arbitrary review prose "*20, "{", "[]", "null"]
  for field in valid:
   cases.append(json.dumps({k:v for k,v in valid.items() if k!=field}))
  for field,values in {"status":[None,True,"done"],"summary":[None,42,[],"","  "],"findings":[None,{},"none"]}.items():
   cases.extend(json.dumps({**valid,field:value}) for value in values)
  cases.append(json.dumps({**valid,"extra":True}))
  for output in cases:
   with self.subTest(output=output):
    self.assertEqual(classify_codex_result(0,output,""),"REVIEW_FAILED")
 def test_stderr_only_success_fails(self):
  for stderr in ("diagnostic "*30,VALID_OUTPUT):
   self.assertEqual(classify_codex_result(0,"",stderr),"REVIEW_FAILED")
 def test_review_uses_only_fresh_final_artifact(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   (root/"state/codex").mkdir(parents=True)
   sha="a"*40
   checkout=root/"notion-dispatch/worktrees"/("pr28-"+sha[:16])
   checkout.mkdir(parents=True)
   pr={"state":"open","head":{"sha":sha,"repo":{"full_name":dispatcher.REPO}},"base":{"sha":"b"*40,"repo":{"full_name":dispatcher.REPO}}}
   final_paths=[]
   mode=["valid"]
   def fake_run(argv,**kwargs):
    if argv[0]=="git": return SimpleNamespace(returncode=0,stdout=sha,stderr="")
    if "exec" not in argv: return SimpleNamespace(returncode=0,stdout="SANDBOX_READ_OK",stderr="")
    self.assertIn("--output-schema",argv)
    schema=json.loads(Path(argv[argv.index("--output-schema")+1]).read_text())
    self.assertEqual(set(schema["required"]),{"status","summary","findings"})
    self.assertIs(schema["additionalProperties"],False)
    final=Path(argv[argv.index("--output-last-message")+1])
    self.assertFalse(final.is_relative_to(checkout))
    self.assertFalse(final.exists())
    final_paths.append(final)
    if mode[0]=="valid": final.write_text(VALID_OUTPUT)
    return SimpleNamespace(returncode=0,stdout=VALID_OUTPUT,stderr="diagnostic "*30)
   with patch.object(dispatcher,"ROOT",root), patch.object(dispatcher,"github_json",return_value=(pr,"")), patch.object(dispatcher,"prepare_review_checkout",return_value=None), patch.object(dispatcher,"run",side_effect=fake_run):
    self.assertEqual(dispatcher.review(D)["status"],"REVIEW_READY")
    self.assertTrue(final_paths[0].exists())
    mode[0]="missing"
    self.assertEqual(dispatcher.review(D)["status"],"REVIEW_FAILED")
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
