#!/usr/bin/env python3
"""A00 bounded, read-only PR dispatcher using GitHub-mirrored Notion jobs.
No direct Notion API access, write-enabled Codex, GitHub POST, or TSE runtime.
"""
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request
import urllib.error

REPO = "Escoba2024/SeriousSam-TSE-Bot-Servermods-"
PREFIX = "NOTION_BRIDGE_JOB_V1\n"
# Only a fresh, owner-authored terminal event may invalidate an earlier WAIT.
TERMINAL_STATES = frozenset({"Gesperrt", "Freigabe fehlt", "Review", "Läuft", "Erledigt"})
EVENT_STATES = TERMINAL_STATES | {"Wartet"}
ROOT = Path("/var/lib/tse-agent-control")
CODEX = "/opt/tse-agent-control/toolchain/codex/bin/codex"
NODE_PATH = "/opt/tse-agent-control/toolchain/node-v24.22.0-linux-x64/bin"
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
QUOTA = re.compile(r"usage limit|quota exceeded|429 too many requests", re.I)
SANDBOX_ERROR = re.compile(r"bwrap:|sandbox.*(?:failure|blocked)|operation not permitted", re.I)

def classify_codex_result(returncode, stdout, stderr):
    """Do not interpret quoted model/source text as an actual provider error."""
    output = (stdout or "") + "\n" + (stderr or "")
    if returncode == 0:
        return "REVIEW_READY" if len(output.strip()) > 100 else "REVIEW_FAILED"
    provider_errors = stderr or ""
    if QUOTA.search(provider_errors):
        return "BLOCKED_QUOTA"
    if SANDBOX_ERROR.search(provider_errors):
        return "BLOCKED_SANDBOX"
    return "REVIEW_FAILED"

def skip_completed_review(old, job, current_sha):
    """Dedupe only an identical authorized event against an identical PR revision."""
    return (old.get("status") == "REVIEW_READY"
            and old.get("head_sha") == current_sha
            and old.get("github_comment_id") == job.get("github_comment_id"))

def utcnow():
    return dt.datetime.now(dt.timezone.utc)

def parse_time(v):
    try:
        t = dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
        return t if t.tzinfo else None
    except (AttributeError, TypeError, ValueError):
        return None

def parse_comment(c, current=None, *, allowed_states=("Wartet",)):
    """Accept a fresh owner-authored fixed-action mirror event for the given states."""
    current = current or utcnow()
    if not isinstance(c, dict) or (c.get("user") or {}).get("login") != "Escoba2024":
        return None
    body = c.get("body")
    if not isinstance(body, str) or not body.startswith(PREFIX) or len(body) > 2500:
        return None
    try:
        d = json.loads(body[len(PREFIX):])
    except ValueError:
        return None
    if not isinstance(d, dict) or set(d) != {"source","notion_page_id","job_id","pr_number","kind","mode","status"}:
        return None
    if not (d["source"] == "notion_mcp_bridge" and d["kind"] == "pr_readonly_review"
            and d["mode"] == "Read-only Codex" and d["status"] in allowed_states):
        return None
    if not isinstance(d["notion_page_id"], str) or not UUID.fullmatch(d["notion_page_id"]):
        return None
    if type(d["job_id"]) is not int or not 1 <= d["job_id"] <= 1000000:
        return None
    if type(d["pr_number"]) is not int or not 1 <= d["pr_number"] <= 10000:
        return None
    created = parse_time(c.get("created_at"))
    if not created or not 0 <= (current-created).total_seconds() <= 7200:
        return None
    return {**d, "github_comment_id": c.get("id"), "github_comment_url": c.get("html_url","")}

def queue_from_comments(comments, current=None):
    latest = {}
    for c in comments:
        # Terminal events compete with WAIT events by GitHub ID.
        job = parse_comment(c, current, allowed_states=EVENT_STATES)
        if job is not None and type(job["github_comment_id"]) is int:
            k = job["notion_page_id"]
            if k not in latest or job["github_comment_id"] > latest[k]["github_comment_id"]:
                latest[k] = job
    return sorted((event for event in latest.values() if event["status"] == "Wartet"),
                  key=lambda j: j["github_comment_id"])

def github_json(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "User-Agent":"TSE-Notion-ReadonlyBridge/1.0",
        "Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response), response.headers.get("Link","")

def comments():
    rows = []
    for page in range(1, 21):
        a, link = github_json(f"/repos/{REPO}/issues/18/comments?per_page=100&page={page}")
        if not isinstance(a, list):
            raise ValueError("invalid comments response")
        rows += a
        if 'rel="next"' not in link:
            return rows
    raise ValueError("comment pagination cap")

def run(argv, *, cwd=None, limit=40, stdin=None):
    env = {**os.environ,
           "PATH": NODE_PATH + ":" + os.environ.get("PATH", ""),
           "HOME": str(ROOT),
           "GIT_TERMINAL_PROMPT":"0", "GIT_ASKPASS":"echo"}
    return subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True,
                          text=True, errors="replace", timeout=limit, env=env)

def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name+".tmp")
    tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n")
    os.replace(tmp,path)

def read_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}

def review(job):
    pr, _ = github_json(f"/repos/{REPO}/pulls/{job['pr_number']}")
    sha = (pr.get("head") or {}).get("sha","")
    head_repo = ((pr.get("head") or {}).get("repo") or {}).get("full_name")
    if pr.get("state") != "open" or not SHA.fullmatch(sha) or head_repo != REPO:
        return {"status":"BLOCKED_PR_ORIGIN_OR_SHA"}
    # Must not compete with existing 30-minute Codex review worker.
    shared = ROOT/"state"/"codex"/"worker.lock"
    with shared.open("a+") as l:
        try: fcntl.flock(l.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: return {"status":"DEFERRED_CODEX_BUSY"}
        w = ROOT/"notion-dispatch"/"worktrees"/("pr"+str(job["pr_number"])+"-"+sha[:16])
        if not w.exists():
            w.mkdir(parents=True,mode=0o700)
            commands = [
                ["git","init","-q"],
                ["git","fetch","-q","--no-tags","--depth=1",
                 "https://github.com/"+REPO+".git",f"refs/pull/{job['pr_number']}/head"],
                ["git","checkout","-q","--detach","FETCH_HEAD"]]
            for cmd in commands:
                p = run(cmd,cwd=w,limit=90)
                if p.returncode: return {"status":"BLOCKED_GIT_FETCH","detail":p.stderr[-150:]}
        checked = run(["git","rev-parse","HEAD"],cwd=w)
        if checked.returncode or checked.stdout.strip() != sha:
            return {"status":"BLOCKED_SHA_MISMATCH"}
        sandbox = run([CODEX,"--sandbox","read-only","sandbox","--",
                       "/usr/bin/python3","-c","print('SANDBOX_READ_OK')"],cwd=w)
        if sandbox.returncode or sandbox.stdout.strip() != "SANDBOX_READ_OK":
            return {"status":"BLOCKED_SANDBOX"}
        prompt = (
            f"READ-ONLY source/security review of exact checked-out PR #{job['pr_number']} "
            f"at {sha}. Identify substantive bugs and security regressions specific to the "
            "changed code: authority checks, path/symlink traversal, untrusted input, "
            "stale state, cancellation and retries, subprocess and credential limits. "
            "Examine relevant actual source; no edits, tests, downloads, pushes, merges "
            "or game runtime. Findings require concrete file/line evidence. Distinguish "
            "unrun tests from proven tests. Report NO_CONFIRMED_FINDINGS otherwise.")
        p = run([CODEX,"exec","--sandbox","read-only","--cd",str(w),
                 "--ignore-user-config","-"],cwd=w,stdin=prompt,limit=480)
        output = (p.stdout or "")+"\n"+(p.stderr or "")
        logs = ROOT/"notion-dispatch"/"logs"
        logs.mkdir(parents=True,exist_ok=True)
        log = logs/f"job{job['job_id']}-pr{job['pr_number']}-{sha[:12]}.log"
        log.write_text(output[-50000:],encoding="utf-8")
        status = classify_codex_result(p.returncode, p.stdout, p.stderr)
        return {"status":status,"head_sha":sha,"exit_code":p.returncode,"log_file":str(log)}

def main():
    dispatch = ROOT/"notion-dispatch"
    dispatch.mkdir(parents=True,exist_ok=True)
    with (dispatch/"dispatcher.lock").open("a+") as l:
        try: fcntl.flock(l.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print("SAFE_SKIP_ALREADY_RUNNING")
            return
        state_file = ROOT/"state"/"notion-dispatch-latest.json"
        previous = read_json(state_file)
        history = previous.get("jobs",{})
        if not isinstance(history,dict): history={}
        record={"at":utcnow().isoformat(),"mode":"GITHUB_MIRROR_READONLY",
                "direct_notion_api":False,"code_writes_enabled":False,
                "github_write_enabled":False,"jobs":history}
        try:
            jobs = queue_from_comments(comments())
            record["queue_ready_count"] = len(jobs)
            record["source_status"] = "GITHUB_BRIDGE_READY"
            record["result"] = "NO_READY_JOBS"
            for job in jobs:
                key=job["notion_page_id"]+":pr:"+str(job["pr_number"])
                old=history.get(key,{})
                if old.get("status") == "REVIEW_READY":
                    current_pr, _ = github_json(f"/repos/{REPO}/pulls/{job['pr_number']}")
                    current_sha = ((current_pr.get("head") or {}).get("sha") or "")
                    if SHA.fullmatch(current_sha) and skip_completed_review(old, job, current_sha):
                        continue
                retry=parse_time(old.get("retry_after"))
                if retry and utcnow()<retry: continue
                entry={**job,"attempted_at":utcnow().isoformat()}
                try:
                    entry.update(review(job))
                except (OSError,RuntimeError,ValueError,subprocess.TimeoutExpired) as exc:
                    entry.update({"status":"REVIEW_FAILED","reason":type(exc).__name__})
                if entry["status"] != "REVIEW_READY":
                    entry["retry_after"]=(utcnow()+dt.timedelta(hours=1)).isoformat()
                history[key]=entry
                record["result"]="PROCESSED_ONE"
                break
            else:
                if jobs: record["result"]="IDLE_DONE_OR_COOLDOWN"
        except (OSError,ValueError,urllib.error.URLError,TimeoutError) as exc:
            record["result"]="BLOCKED_SOURCE"
            record["error_type"]=type(exc).__name__
        atomic_json(state_file,record)
        print(record["result"]+" jobs="+str(record.get("queue_ready_count","?")))

if __name__=="__main__":
    main()
