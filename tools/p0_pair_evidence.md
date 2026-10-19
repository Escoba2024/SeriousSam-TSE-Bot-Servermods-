# P0-PAIR offline evidence manifest checker (schema 1)

`p0_pair_evidence.py` checks the integrity and consistency of a **private archived
manifest and its referenced dumps**. Python 3 stdlib only. It neither starts nor
attaches to games, modifies evidence, reads installed modules, nor imports the
branch-only comparator. All tests use temporary fake text and declared module
hashes; no synthetic file is a Retail runtime artifact.

```text
python3 -B tools/p0_pair_evidence.py --root /absolute/private/archive \
  --manifest manifest.json --pins retail-pins.json \
  --pins-sha256 INDEPENDENTLY_VERIFIED_PIN_FILE_SHA256
python3 -B -m unittest discover -s tools -p 'test_p0_pair_evidence.py' -v
```

The pin-file SHA256 is an independent operator trust anchor. Do not derive it
from the untrusted evidence package and immediately treat that as authorization.
Deliver the trusted pin file and its digest through the existing verified host
handoff. The file must be copied byte-for-byte under the evidence root; JSON
reformatting changes its digest. Neither it nor the manifest is a digital signature.

## Input and path rules

Schema 1 is deliberately small, strict and separate from the richer runtime
sidecars in the P0 plan. Unknown keys, missing keys, duplicate JSON keys at any
depth, invalid JSON, NaN/Infinity and wrong types fail closed. Each JSON file is
UTF-8, at most 1 MiB. Integers must be JSON integers, not booleans or float values.
All strings/hashes below are private input and are never echoed in reports.

`--root` is the explicitly authorized, quiescent private archive, not a running
game installation. All input names, including manifest and pins, must be relative
POSIX-style paths below it. Empty components, `.`, `..`, backslashes, drive/ADS
colons and absolute file paths are rejected. Snapshot paths must be unique.
Every root/path component is opened without following symlinks. Only regular,
single-hardlink files may be read; FIFOs, devices and directories cannot be
snapshots. Symlinks are rejected even if they point back inside the root.

Safe access requires POSIX `dir_fd`, `O_NOFOLLOW` and `O_DIRECTORY` (verified on
Linux/Python 3.12). Windows currently returns `UNSUPPORTED_SAFE_FILE_ACCESS`:
export the private evidence archive to an authorized Linux offline location;
do not weaken path checks or copy Retail executables for this validator.
Descriptor-relative opens protect against parent-link swaps; size/mtime/ctime
and byte count are rechecked on the opened file. This is not an authenticated
filesystem snapshot, a defense against a privileged attacker, or a custody
guarantee after validation. Freeze the archive and revalidate before consuming it.

## Independent module pins

The pin JSON has exactly these keys; angle-bracket values are placeholders and
intentionally invalid until replaced by verified hashes:

```json
{
  "schema_version": 1,
  "retail_version": "1.07",
  "client_kind": "vanilla",
  "modules": {
    "server": {
      "DedicatedServer.exe": "<trusted SHA256>",
      "Engine.dll": "B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F",
      "EntitiesMP.dll": "<trusted SHA256>",
      "GameMP.dll": "1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208"
    },
    "client": {
      "SeriousSam.exe": "<trusted SHA256>",
      "Engine.dll": "B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F",
      "EntitiesMP.dll": "<trusted SHA256>",
      "GameMP.dll": "1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208"
    }
  }
}
```

For `client_kind: "bot61dc"`, only the client's GameMP pin becomes
`61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9`.
Known Engine and GameMP pins are additionally hardcoded: supplying a different
trusted-file digest cannot redefine them. EXE and Entities pins come from the
operator's independently qualified Retail manifest; this tool does not invent
original hashes. All SHA256 strings are exactly 64 hex digits, case-insensitive.
These are **checks on declared module metadata against trusted pins**, not hashes
of running/loaded modules. Actual role/install/module provenance remains a host gate.

Sources: repository README and Retail sync report, plus
`ccc4c46321a99d496a078aab390f4731f24a64f8:docs/reports/2026-10-17-retail107-native-syncdump.md`.
That report proves a static One-shot dump path, not a native capture qualification.

## Evidence manifest

Top-level keys (all required, no others):

| Key | Type and rule |
|---|---|
| `schema_version` | Integer `1`. |
| `retail_version` | String `"1.07"`. |
| `client_kind` | `"vanilla"` or `"bot61dc"`, matching trusted pins. |
| `run_id`, `mapepoch` | Nonempty printable strings, no outer whitespace, at most 128 characters each. One run and map epoch per manifest. |
| `map_sha256` | 64-digit hex map hash, a host declaration (map file is not opened). |
| `modules` | Exactly the two role dictionaries from the pin schema; all four hashes per role must match the independent pins. |
| `snapshots` | List of 2–256 entries, 1–128 per role. At least one exact pair; no missing counterpart. |

Each snapshot entry has exactly these required keys:

| Key | Type and rule |
|---|---|
| `role` | `"server"` or `"client"`. |
| `run_id`, `mapepoch` | Must equal manifest values. |
| `path` | Unique root-relative path, e.g. `server/capture-001.txt`. |
| `sha256`, `size` | SHA256 of original raw file bytes and positive integer byte count; both verified. Maximum 8 MiB/file, 32 MiB/role. |
| `encoding` | `"utf-8"`, `"utf-8-sig"` or `"cp1252"`; strict decoding, no replacement characters inserted. |
| `level`, `sequence` | Nonnegative integers, exactly matching raw headers. All pairs must be in a single level. |
| `tick` | Nonnegative decimal **string**, at most 128 characters, plain digits with optional fractional part, no exponent/comma/NaN. Exactly matches raw value using `Decimal`, never float rounding. |
| `crc` | `"0x"` followed by exactly eight hex digits, exactly matching raw header. |
| `complete` | Boolean `true`: host declaration of complete capture. |
| `truncated` | Boolean `false`: no reported truncation. |
| `writer_closed` | Boolean `true`: host attests capture was finalized before archiving. |
| `dropped_records` | Integer `0`, not boolean. |

For example, a **snapshot-entry schema illustration, not runtime evidence**:

```json
{
  "role": "server", "run_id": "example-run", "mapepoch": "example-map-epoch",
  "path": "server/capture-001.txt", "sha256": "<SHA256 of original bytes>",
  "size": 123, "encoding": "utf-8", "level": 1, "sequence": 1689,
  "tick": "83.40", "crc": "0x12345678", "complete": true,
  "truncated": false, "writer_closed": true, "dropped_records": 0
}
```

Assemble the full manifest from the documented top-level fields, exact modules
object, and server/client entry list. Create no new metadata inside raw dumps.
Capture method, PID/start time, UTC events, binary/backup preservation, actual
sampling interval and native completion evidence remain separate private runtime
sidecars, reviewed by the host; they are not accepted as arbitrary extra schema keys.

## Raw text and pairing

Require one and only one valid header each for `CRC: 0x........`, `Level: N`,
`Sequence: N`, `Tick: D.D`. A second header (including a malformed second header)
is invalid, so concatenated dumps cannot be passed as one. At least one nonempty,
nonseparator state line must follow the final metadata header; NUL bytes and
missing final LF are rejected. CRLF bytes are preserved for the hash. Headers
are case-sensitive as in the pinned comparator; unknown native formats fail
closed rather than being repaired. All raw values must agree with the manifest.

Index each role by exact `(level, sequence, Decimal(tick))`. Duplicate identity,
multiple levels, missing role or unequal role key sets fail. `83.40` equals
`83.400`; `83.40000000000000000001` does not. Order and filenames do not pair
snapshots. A CRC difference between correctly paired original files is valid
capture metadata and is counted; it does not produce a metadata error.

## Reports and limits of the result

Exit **0**: `status: "VALIDATED_CAPTURE_METADATA"`, `paired_snapshots` and
`crc_differing_pairs`. Exit **2**: `status: "INVALID_EVIDENCE_MANIFEST"` and one
fixed public `reason` code. Invalid CLI arguments also produce redacted JSON;
no private exception text, arguments or traceback goes to stderr. `--help` is
ordinary public help. Reports omit input paths, IDs, epochs, raw text, hashes,
CRCs, players and individual tick values. Keep even aggregate reports private
until host review. No output files are created by the tool.

Every result explicitly contains:

```json
{
  "native_sync": "NOT_ASSESSED",
  "first_divergent_tick": "NOT_DETERMINED",
  "capture_authenticity": "NOT_ASSESSED",
  "continuous_tick_coverage": "NOT_ASSESSED"
}
```

**Completeness cannot be established from an unknown native footer.** Hash/size
mismatches, reported drops/open writer/truncation, malformed or missing headers,
empty state and unterminated text are rejected. However, a truncated state body
ending at a complete line, with its hash/size regenerated and `complete=true`
falsely declared, is indistinguishable here from a full archived body. Likewise,
the manifest cannot prove files are native or that role/run/map claims are true.
Schema validation is not `CAPTURE_QUALIFIED`; host completion/provenance and
preservation evidence are still mandatory. We deliberately do not fabricate
a Retail footer or infer full state coverage from a few printed fields.

Sparse, identically incomplete sampling on both sides can satisfy exact pairing.
No tick continuity, actual first divergence, CRC algorithm/ABI, state-field cause,
sync stability, native Join, WAN/Wine or 24h acceptance follows. This checker
counts paired CRC differences; use the separately pinned comparator for a
redacted state-text comparison. It does not recompute the engine CRC.
