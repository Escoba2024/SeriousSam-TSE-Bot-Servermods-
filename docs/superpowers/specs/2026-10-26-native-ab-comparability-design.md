# Native 1.07 A/B receipt comparability design

Goal: prevent the Cecil P1 four-bot SYNCBAD and passing Build04/Build06 runs being called a causal A/B experiment when binary, harness, configuration, or feature-flag attribution differ. This is a read-only diagnostic prerequisite for ssam.ai Stable Candidate 1.

Approach: compare local retained native `result.json` and `source-sha256.json` metadata, without opening raw game logs, player identifiers, profiles, Wine prefixes, live processes or binaries. Emit only minimal, non-sensitive classifications. Never infer root cause, CRC equality, release qualification, or that absent `cecil_p1` means false. Missing provenance fails closed.

A controlled Cecil toggle comparison requires matching 64-hex DLL SHA256, complete matching harness hashes, same native scope, exactly four requested and observed bots, original client, identical relevant execution settings, and explicit `cecil_p1=false` control / `true` candidate. Elapsed seconds and PASS/FAIL are outcome observations, not comparable inputs or release gates. A controlled toggle merely permits a follow-up causal investigation; still not proof without native action/state/CRC pairing.

Reject truncated/missing/invalid input and non-native runs; differences or missing provenance label `CONFOUNDED`. Output includes non-sensitive reason codes and outcome summaries only. CLI exit 0 = controlled flag comparison receipt preflight; exit 3 = not controlled; exit 2 = invalid inputs. All outputs explicitly say NOT_RELEASE_QUALIFIED.

Alternatives considered: (1) extrapolate from existing long Build04/06 runs (invalid due uncontrolled flags/builds), (2) immediately launch new native runs (risks the protected public two-vCPU server and existing agents), (3) read-only receipt gate then later dedicated owned isolated A/B. Chosen (3) to preserve source and players while supplying a reproducible prerequisite.

Non-goals: new AI features, engine patching, modifying operational resource limits, starting/stopping game services, consuming private native raw logs, automatically approving the release.