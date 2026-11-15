"""Finalize an existing RAM audit only; no Native stream access."""
import hashlib
from pathlib import Path

def close_receipt(C,worker):
    root=Path(__file__).parents[1];g=C['G']
    names=['audit_yodeller035_closed.py','yodeller035_kill_tokens.py','yodeller035_ram_detail.py','yodeller035_close.py','test_yodeller035_closed_reader.py','test_yodeller035_kill_tokens.py','test_yodeller035_ram_detail.py']
    proof={}
    paths=[root/'tools'/n for n in names]+[root/'docs/reports/2026-11-15-build035-yodeller-closed-functional-audit.md',root/'docs/superpowers/plans/2026-11-15-build035-yodeller-closed-audit.md']
    paths+=sorted((root/'.codex/evidence/yodeller035').glob('*.log'))
    paths+=[Path('/srv/tse-sdk-20261021/Sources/Includes/Engine107/Engine/Entities/PlayerCharacter.h'),Path('/srv/tse-sdk-20261021/Sources/Includes/Engine107/Engine/Classes/PlayerEntity.h'),Path('/srv/tse-milestone-a-20261111/tools/gamespy_query.py')]
    for p in paths:
        raw=C['read'](p);proof[str(p)]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    outputs={}
    for p in sorted(C['OUT'].iterdir()):
        if p.is_file():
            with C['opened'](p)as f:raw=f.read(8*2**20+1)
            if len(raw)>8*2**20:raise ValueError('bounded derived verification')
            outputs[p.name]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    value=dict(status='FINAL_AUTHOR_CLOSED_OBSERVATION_AUDIT_ONLY',qualified=False,a4_pass=False,source_and_proof_pins=proof,artifact_pins=outputs,input_pins=g['pins'],input_bytes=g['sizes'],actual_accounted_input_bytes=g['read_bytes'],one_analytic_raw_pass=True,old_raw_replays=0,all_raw_handles_closed=True,worker=worker,retained_checkpoints=['ram-context-detail.json','final-yodeller035-receipt.json'],canonical_detail='ram-context-detail-v2.json',single_parent_reader_whole_inverse=True,source_clocks_not_native_clocks=True,kill_decoration_rule_implementation_unproven=True)
    return C['save']('final-author-closure.json',value)
