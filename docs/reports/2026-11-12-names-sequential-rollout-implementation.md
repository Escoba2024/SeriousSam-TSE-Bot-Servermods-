# Development-first sequential names rollout

## Requirement and scope

The names deployment must verify Development first, then process Red Station,
Yodeller, Skulls, Little Trouble and Hole individually. The earlier global
controller closed all twelve clients before applying its 51-file plan; that
entry is not used by the new private package.

The new `tools/fleet_names_sequential.py` controller reuses the reviewed backend
for canonical files, locks, source/dependency pins, actual native identities,
normal-close acknowledgements, generation-bound logs, write journals and start
invocation receipts. Its constructor still validates the complete immutable
48-assignment/51-write stage. No subset-stage flag relaxes those checks.

This change contains no gameplay/DLL/server mutation and no runtime authority.
Only the root operator can review, freeze and execute the private package.

## One explicit affected instance

The global lock set remains held for the whole operation. Initial preflight
captures all six native/query states, original Dedicated log baselines and the
complete original file backup. Each later input expectation comes from the
same staged before/after hashes. A later snapshot never replaces that baseline.

A fixed completed prefix selects the next instance. Before closing its two
clients, the controller verifies the full mixed fleet again: exact current
native generations, local slots, GUIDs, expected old/new names, fresh public
queries and stage hashes. Every forward stop/write/start also checks the files
and exact recorded generations of the other five running instances. Stop/start
boundaries recheck actual names and query collisions. Only selected clients can
pass the close/start wrappers; the writer additionally requires a selected
mutation phase and the existing global mutable-path boundary.

The selected post-close backup is retained as evidence, then checked against
the known immutable before state. Exactly eight profile changes are applied for
an ordinary instance; Red also receives its two reviewed launcher changes and
roster change. The entire 51-file plan is independently revalidated before
selecting those eight or eleven already-known payloads.

The two clients restart through the original reviewed commands. Both must load
all eight assigned local identities with preserved GUIDs and new recorded native
generations. Their complete new-generation logs and the Dedicated log delta
must pass before the instance receives its durable acceptance receipt. The next
instance cannot start before that receipt exists.

## Mixed names and original duplicates

Original Development/Red identities include cross-server name duplicates. The
initial all-before state is allowed only with those exact original physical
slots, names and GUIDs. The controller checks every planned full-instance
transition before the first stop. Every completed mixed state after Development
must contain 48 globally distinct own visible names; an old name colliding with
a newly assigned name rejects. Foreign players are retained, and fresh foreign
collisions still block the operation.

During the selected instance's two-client stop/start interval, existing old
attachments may remain briefly. They are tied to the exact before/current
native generation and checked separately from the new assigned attachments.
No general duplicate-name or sync-error tolerance was introduced.

## Failure, recovery and resume

The journal uses schema 4 and a separate sequential workflow identifier. It
records the fixed order, accepted prefix, one active instance, phase, attempt,
original and post-close evidence, started/stop identities and exact service
invocations. Source manifest, stage fingerprint, root mapping, boot identity,
reviewed helper hashes and all Dedicated generations remain bound. The original
schema-3 controller retains its existing eligibility checks; only the shared
binding implementation was extracted without changing its checks.

A forward failure halts the rollout. If the selected instance may have been
modified, rollback closes only its recorded/recoverable own generations and
restores its original saved bytes and metadata. Earlier accepted instances keep
their after-state; untouched running instances are neither closed nor rewritten.
Rollback's mutation primitives retain the original global server/helper guards
and exact selected ownership. Any new drift outside the affected instance is
reported during verification, never repaired or adopted by this controller.

Red's original rotation behavior is temporarily bypassed while its old names
restart. Only after those names, GUIDs, fresh generations and logs pass are its
original launcher bytes restored. Failed candidate logs remain archived. A
server sync error remains evidence after names are restored; rollback cannot
erase that error or turn it into a runtime qualification.

Recovery validates the original immutable package/stage and the completed
prefix. An interrupted active instance is rolled back and the controller halts
at an explicit partial state. A subsequent explicit resume rechecks the entire
mixed boundary and continues at the next incomplete instance. A missing durable
InvocationID remains an ownership blocker; a replacement process with matching
names is never adopted. An interrupted rollback can itself be recovered using
its recorded current generations.

A failure before any selected mutation leaves clients running. Failure-report
journal errors do not suppress an otherwise journalable rollback. Persistent
journal/identity/immutable-input failures retain an incomplete result and the
operation/recovery errors. No partial status is a 48-name success.

After the last accepted instance, the controller performs another complete
48-name/GUID/query, source, client-log, Dedicated-delta and exact generation
verification. Only that final check can permit `applied_names_only`. A later
failure retains the accepted receipts and an explicit failed final-verification
status; it does not automatically restart earlier accepted instances.

## Offline evidence

A regression against the previous global transaction reproduced its incorrect
public-first close order. The first 14 sequential scenarios passed after the
new controller was implemented. Two additional failing regressions then exposed
a selection-to-first-close gap; both now pass with mutation-entry revalidation.

The focused sequential suite currently passes **20/20 tests in 61.979 seconds**.
It uses real temporary stage/profile/launcher/backup/journal files and the
existing simulated external process/service/query boundary. The Red fixture
executes actual harmless launch scripts; its rotation marker remains absent.

Covered cases include fixed order and no public mutation before Dev acceptance;
exact 51 total payloads; preserved Dedicated generations; old/new source and
foreign-name collision checks; exact baseline duplicate identities; affected-only
Dev and Red rollback; an interrupted partial Red write after accepted Dev;
interrupted starts and rollback; explicit resume without restarting accepted
instances; an unreceipted-start blocker; malformed completed/active recovery
scope; first-close journal failure; and final 48-generation replacement rejection.

After root's native measurement window ended, the complete current nine-module
suite passed **123/123 tests in 193.285 seconds, exit 0**. This includes the
additional RED-to-GREEN check that explicit resume retains the original 8-GiB
disk-reserve gate before further mutation. All 102 preceding focused tests remain
included. The three private bootstrap boundary tests also passed; the new disabled
package validated with 9 sources, 11 immutable dependencies and 2063 data pins.

Independent root review of the complete controller, entry, shared recovery
extraction and targeted tests found no critical or important findings at this
tested source. The runtime gate remains false. No native acceptance was run by
this implementation worker.

Reproduction from the repository root:

```bash
cd tools
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_gaming_names test_names_staging test_fleet_names_apply_policy test_fleet_names_transaction test_fleet_names_service_policy test_fleet_names_sequential test_native_closed_log_evidence test_gamespy_query test_native_identity_wait -v
```

## Root-owned integration

Review the generic change and new disabled private entry. Preserve old packages,
stages and journals. The new entry dispatches exclusively to the sequential
controller and offers separate recovery and resume modes. Include the new module
and all existing immutable helper dependencies in a newly frozen root-owned
package; changing any source or absolute package path changes its manifest pin.

Repeat current source/native/launch-policy preflight under the existing global
locks. A copied old native preflight receipt is not current proof. The complete
stage remains fixed; any required new stage must preserve the approved stable
assignments and undergo a new explicit source review, never recapture drift to
silently make a failed recovery pass. Root owns actual application, monitoring
updates and independent native/external follow-up. This names-only rollout does
not establish combat, navigation, WAN/browser or milestone acceptance.
