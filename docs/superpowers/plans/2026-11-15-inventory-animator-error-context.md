# Inventory animator error context plan

**Claim:** only new `tools/retail_inventory_animator_context_patch.py`, its portable test, this plan and own report. Existing isolated audit WT; no frozen-package/Root/fixture writes.

**Authority:** Root's closed QJS10-V2 control diagnostic task. Actual traceback reaches the outer `tools/retail_inventory_readonly.py:148`; no MethodWindow/worker/trace started. Animator value was not archived and remains unknown.

**Design:** replace only the error-message argument of the existing exact animator guard. Include already-read unsigned animator value, slot, entity pointer/ID, world and original snapshot tick. Keep guard AST, read order/count, exception class, retries, defaults, other errors and snapshot bytes unchanged. Whole-source hash/inverse fail closed for any other parent or foreign edit.

**Source:** active outer reader SHA `b5627e91094594d0e1a0fae52ef8dc36be33f416436b92d0286396d37b31463a`. Nested legacy reader SHA `97c88ac52c7dbcc04f0f974194fc82ae5ce8e1fc31c6f956e6efb9547dd649db` is a different source and remains byte-identical. Parent imports RuntimeRoot.tools reader explicitly; this transform must reject the nested source rather than blindly patch both. Only the active local outer dependency needs repinning, plus future helper provenance; ancestor/nested dependency hashes stay unchanged.

- [x] Actual fake-reader snapshot RED: old error lacks exact sampled context; retain log0600. Five actual failed assertions for sampled values0/1/0xfffc/0x10001/0xffffffff.
- [x] Minimal one-argument exact-source transform and inverse; GREEN valid/invalid pointer, unchanged other errors and identical read traces.
- [x] Static guard-AST/whole-source inverse/unsupported-parent mutations; no mirror suite or runtime.
- [x] Private source/pin/RED/GREEN receipt, sanitized report and source commit; Root alone reviews/applies next diagnostic package.

No package generation, Native/Frida/X/process/locks/memory or Raw replay. A null pointer is not assumed transient and is not accepted. This is a future diagnostic prerequisite, no readiness or fix claim.

Verification: four focused tests passed0.078s. Actual `snapshot` AST and original EvidenceError/require/unpack helpers execute against fake bytes; no replacement snapshot or live API. Invalid samples read the animator once before rejecting; valid two-pass snapshots read it twice exactly as before. Eight remaining error branches preserve message/read order. Entire-reader inverse pins all other bytes. No delegation; final Root review separate.
