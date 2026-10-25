# Offline gate for future native sync captures

This directory defines a **proposed interchange contract**, validates sealed local
artifacts, and compares complete windows. It contains no TSE capture hook, Retail
dump parser, process attachment, network command, or DLL modification. Python
3.10+ standard library only; verified here with Python 3.12.3 on Linux.

`MATCHED_WINDOW` means matching captured bytes/CRC in one declared window.
`DIFFERENT_WINDOW` identifies observed differences. **Both always report
`retail_runtime: NOT_TESTED`**. Neither authenticates native capture, proves the
first divergent simulation tick, establishes root cause, or accepts a release.

## Reproduce

From repository root:

```bash
python3 -B -m unittest discover -s poc/research/native-sync-gates/tests -v
python3 -B poc/research/native-sync-gates/review_pr58.py
python3 -B poc/research/native-sync-gates/make_synthetic_bundle.py /tmp/synthetic-sync-example
python3 -B poc/research/native-sync-gates/capture_gate.py /tmp/synthetic-sync-example/manifest.json
```

Choose an unused example destination: the generator refuses an existing directory.
Its `.fixture` files are plain synthetic text, **not game binaries**. It copies
only its own source as producer provenance. It never emits `source_kind: native`.
The compare command only reads input and emits JSON to stdout:

| Exit | Status | Meaning |
|---|---|---|
| 0 | `MATCHED_WINDOW` | Every required pair validated and matched |
| 3 | `DIFFERENT_WINDOW` | Every required pair validated; at least one domain differs |
| 2 | `BLOCKED` | Any schema, identity, coverage, hash, binding, or artifact failure |

The PR58 review command reads pinned Git object
`df7108ba04cafb120c6a035503fa2f9732a83b0f`, extracts only its Python toolkit
into a temporary directory here, runs its original 29 tests and seven independent
adversarial probes, and removes the temporary copy. It does not fetch or check out
files. Exit 0 means the baseline and all seven documented findings reproduced,
**not that PR58 is suitable as an acceptance gate**. It executes trusted pinned
Python code locally, including test subprocesses; it never launches the game.

## Contract v1

Use `make_synthetic_bundle.py` for a complete machine-readable example. All
manifest, layout, participant, and record keys are strict; unknown keys fail.
Duplicate JSON keys and non-finite numbers fail. Identifiers contain only
`A-Z a-z 0-9 _ . : -`, maximum 128 characters; use pseudonyms, never player names.

An artifact descriptor is exactly `{"path":"relative/file","sha256":"..."}`.
Hashes are lowercase SHA256 of the exact original file bytes. Paths must remain
inside the manifest directory after symlink resolution; absolute paths and `..`
are rejected. Every descriptor is read and hashed. Maximum size is 64 MiB per
artifact/manifest; artifact files must be regular and nonempty. Larger captures
must be sealed as separate windows. Never
commit native bundles, binary copies, player information, or private logs.

| Manifest field | Required interpretation |
|---|---|
| `schema` | Literal `tse-native-sync-capture/v1` |
| `source_kind` | `synthetic` or producer-attested `native` |
| `session_id` | Unique run/session pseudonym shared by both captures |
| `connection_id` | Target player's join epoch; reconnect requires a new bundle |
| `level_id`, `level_epoch` | Map identity and integer load epoch; reload requires a new bundle |
| `map`, `config` | Hash-verified artifact descriptors; config includes the shared comparison settings and role-specific settings inventory |
| `tick_unit` | Literal `engine_tick_index`; no BotDriver counter, wall-clock time, or guessed conversion |
| `window` | Exact `first_sequence`, `last_sequence`, `first_tick`, `tick_step` |
| `layout` | Exact fields described below, with hashed binding evidence |
| `producer` | `id`, `version`, and hashed source/tool `artifact` |
| `participants` | Exactly `server` and `client`, described below |

Sequence increases by one, tick by positive integer `tick_step`. Integers are
nonnegative signed-64-bit values; booleans, strings and floats are rejected.
There must be 1–1,000,000 records per role, exactly covering the window in capture
order. A sampled window with `tick_step > 1` cannot establish intermediate ticks.
Sequence/tick mapping must be proven by the producer's Retail binding evidence;
this tool does not derive it from timestamp text. If the actual Retail capture
cannot provide this mapping, keep the native gate blocked and revise the contract
with tests rather than inventing alignment.

`layout` has exactly these keys:

```json
{
  "id": "synthetic-layout",
  "phase": "before_sync_crc",
  "players": ["slot0"],
  "action_bytes": 2,
  "state_fields": {"session": 2, "entity": 2},
  "binding_status": "synthetic",
  "evidence": {"path": "layout.fixture", "sha256": "..."}
}
```

The lengths above are **synthetic examples**, not Retail layouts. `action_bytes`
is the complete selected action snapshot size for every player slot;
`state_fields` maps each required captured state field to its exact byte length.
No empty list/dictionary, duplicate slot, missing field, extra field, partial byte,
truncated action or truncated state is accepted. `binding_status` is `synthetic`,
`proposed`, or `verified-retail107`; `native` input requires the latter. The
hashed evidence must describe actual binary hashes, runtime module base/RVA,
function signature, byte coverage/endianness, source phase, player identity,
CRC input vs full action snapshot, raw-to-record mapping, and qualification.

**Binding status is attestation by the capture producer, not independent machine
verification of a Retail ABI.** A hash of a false claim is still a false claim.
The tool checks artifact integrity and contract consistency, not the truth of
hook addresses, loaded modules, observation phase, slot ownership or state scope.

Each participant requires distinct `capture_id`, literal `complete: true`,
integer `dropped_records: 0`, a `records` JSONL artifact descriptor, and `binaries`
with exactly `executable`, `engine`, `gamemp`, `entities` descriptors. Actual local
bytes are hashed. Server/client `engine` and `entities` hashes must agree;
executable and GameMP may differ. Matching versions/ABIs are a separate native
qualification requirement. A file hash does not prove it was the module loaded
by a process; preserve runtime module inventory privately.

Each UTF-8 JSONL line is exactly:

```json
{"session_id":"synthetic-session","connection_id":"synthetic-connection","level_epoch":1,"sequence":10,"tick":100,"crc32":"12345678","actions":{"slot0":"0001"},"state":{"session":"0100","entity":"0200"}}
```

`crc32` is eight hex digits without `0x`; actions/state are byte-exact hex strings
in capture byte order. Case is ignored. No floating-point conversion or tolerance
is applied. Actions must represent the same **applied** action set at the same
proven phase on both sides; a client-composed packet and server-applied packet
are different observations and need separate capture/qualification first.

## Results and boundaries

All artifacts and **all records on both sides** are validated before comparing
any pair. A later invalid record blocks even an earlier valid difference. No
intersections, silent overwrite, timestamp rounding, cross-session pooling,
ignored parse error, or partial success is allowed. `BLOCKED` reports the first
issue without paths or input values; repair it and rerun to expose later issues.

Comparison checks CRC, action bytes and state bytes independently. Internal
action/state SHA256 uses sorted-key compact JSON of lowercase hex. These hashes
are local equality helpers, **not the Retail CRC algorithm**. The output binds
the result to manifest and artifact SHA256, reports the number of all compared
pairs, and reports only domains/sequence/tick/JSONL record line of the earliest
observed difference. It deliberately omits raw CRC/action/state values.

`previous_pair_matched` is true only if the first difference follows at least one
matching pair in this declared window. It does not establish what happened before
the window, between sampled ticks, or in uncaptured state fields. Equal CRC with
different captured state is reported as a state difference; different CRC with
equal captured fields indicates an unresolved coverage/semantics question.

The executable native gates, hypotheses and handoff are documented in
[the report](../../../docs/reports/native-sync-gates/2026-10-25-c2-capture-compare.md).
