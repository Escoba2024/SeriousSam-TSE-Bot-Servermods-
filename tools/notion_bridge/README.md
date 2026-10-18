# Hetzner development dispatcher

One Linux worker runs owner-authorized infrastructure jobs. GitHub issues contain the exact manifest; `/etc/tse-dispatch/policy.json`, owned by the administrator, approves its canonical SHA256, issue number and a lease of at most four hours. This is direct owner authorization, not an invented A00 grant. No arbitrary comment becomes executable. Scope is currently restricted to `tools/notion_bridge/` and exact regular file names. No game, retail, merge or production runtime action is supported.

The existing service and timer names are reused. Do not install a second dispatcher. `tsecontrol` owns state, credentials and isolated job repositories; installed source and policy are root-owned. The CLI control plane uses its existing ChatGPT login. Model commands get minimal runtime reads, read-only checkout/Git metadata, writable approved parent directories, read-only existing siblings and a private scratch directory. Codex 0.163 cannot mount exact file write roots reliably; newly created unapproved files are rejected by the complete filesystem inventory before commit or publishing. Ignored/untracked files, symlinks, hardlinks, special files, reparse points and Gitlinks are checked. All tests also run under this sandbox, without command network access. Credentials, other jobs and service state remain outside its readable roots. The existing PR28 scope checker is not enabled or trusted by this worker.

## State and recovery

`/var/lib/tse-agent-control/development/jobs.sqlite` stores immutable jobs and an append-only transition ledger. `QUEUED`, `RUNNING`, `BLOCKED`, `FAILED`, `REVIEW_READY`, `DONE` are distinct. A tested published commit is `REVIEW_READY`; it is never automatically declared integrated. `--accept-integrated JOB_ID` requires separate administrator policy `integration_acceptance[JOB_ID]` with exact commit, manifest digest and evidence, plus a live GitHub comparison proving the commit is in main. It does not merge anything. A single nonblocking OS lock, shared with the old dispatcher, prevents duplicate or overlapping workers. Each attempt is recorded before launch. Dependencies wait for completed implementation, and blocked independent jobs do not stop the queue.

An interrupted model attempt is checked by Linux boot ID, PID and process start ticks. A matching live child prevents any new model launch. An ended child leaves `BLOCKED / RECOVERY_INSPECTION_REQUIRED`; the workspace is preserved for inspection. No blind reset or destructive retry. Ambiguous MODEL/TEST recovery blocks all new model starts until explicit process inspection. Linux subreaper cleanup covers both model and test descendants, including detached process groups; systemd KillMode=control-group covers service termination. Fetch initialization is retryable only in an empty owned repository. Tested commits awaiting a failed network push retain their commit and resume publication without another model execution. Generic network faults back off 60/120/240 seconds with three attempts by default. A real quota failure pauses every model for at least an hour. Jobs and their evidence remain after lease expiry, quota pauses and reboot; an expired lease blocks execution until explicitly renewed.

A repository-only SSH deploy key lets the trusted coordinator push unique job branches. Model commands cannot read that key. Publication never force-pushes or merges. Bundles, exact commits, test commands, exit codes and results persist in the job log directory. Draft PRs can be created by an authenticated administrator from these branches; no GitHub API token is installed on the VPS. This avoids claiming automated PR creation.

## Operations

```sh
systemctl status tse-notion-bridge.timer tse-notion-bridge.service
python3 -B /opt/tse-agent-control/notion-bridge/tools/notion_bridge/development_dispatch.py --status
systemctl stop tse-notion-bridge.timer
systemctl stop tse-notion-bridge.service
systemctl start tse-notion-bridge.timer
systemctl start --no-block tse-notion-bridge.service
journalctl -u tse-notion-bridge.service -n 50 --no-pager
```

Run `--status` as `tsecontrol`, with `HOME=/var/lib/tse-agent-control`, or as the administrator. Read-only SQL can inspect `jobs` and `events`. Before resuming a blocked job, stop the timer, take a SQLite backup, verify recorded process identity and actual Git status including ignored files, review its workspace and code, renew the exact manifest grant and queue only that verified job. Do not delete results or existing worktrees. An accepted/published job is not requeued by polling; use a new permanent job ID for new work.

Logs ending `.log` expire after seven days; commits, bundles, SQLite records and structured results persist. Journald limits are configured at installation. Timeout, memory and CPU limits are in the systemd service. No extra server or paid service is required. Revoke the deploy key in repository settings when this temporary infrastructure is retired.

## Notion

The existing data source is `8719ec1b-4ffb-4de7-8193-dd43842ebc68`, TSE Agenten-Auftragswarteschlange. The optional adapter reads `Code mit Grant` rows linked to GitHub issues and mirrors worker results into the existing status/evidence fields. It cannot grant a job or change its manifest. Configure a separately authorized Notion integration token at `/etc/tse-dispatch/notion-token`, readable only by root and the service group, and share the data source with that integration. The ChatGPT connector is not a server API credential. Without that file, GitHub operation continues and status explicitly reports `BLOCKED_SERVER_TOKEN_MISSING`. Fixture tests are not a live Notion integration acceptance.

API implementation follows [Notion data source query](https://developers.notion.com/reference/query-a-data-source) and [page update](https://developers.notion.com/reference/patch-page); sandbox configuration follows [official OpenAI permissions documentation](https://developers.openai.com/codex/permissions). Actual confinement must be tested on the installed CLI before enabling jobs.

## Rollback

Stop the timer and service; verify the service cgroup contains no worker. Keep SQLite and job directories. The first backup is `/opt/tse-agent-control/backups/20261018-development/` and records original source SHA `58d2affda29b5c4d38dbfdefb5749b5694eba1d8`, old units, prior status and boot ID. Restore those units and the known original source checkout through a separate root-owned release directory, then `systemctl daemon-reload` and start the old timer. Never reset a job checkout or restore old status over the current ledger. The old dispatcher only reviews PRs; rolling back removes code-job execution. Review and revoke the new deploy key if it is no longer required.

## Validation

Run on Linux: `python3 -B -m unittest discover -s tools/notion_bridge -p 'test_*.py' -v`. Scope tests use real temporary Git repositories; quota, source failure and cancellation tests are simulations. Live acceptance evidence is documented separately after actual model jobs and reboot. These checks make no claim about Retail/Wine/game-server correctness.
