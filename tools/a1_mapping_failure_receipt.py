"""Preserve an existing failed comparison only; no process or memory reads."""
import json
import os


def mapping_mismatch(role,identity,module,path,pin,process_rows,actual,signature):
    error=AssertionError()
    error.module_mapping_failure=dict(
        schema='a1-existing-module-mapping-failure-v1',role=role,
        process_identity=list(identity),module=module,module_path=str(path),
        expected_sha256=pin['sha256'],expected_base=pin['base'],
        expected_signature=list(pin['signature']),observed_signature=list(signature),
        expected_mapped_rows=list(pin['mapped_rows']),actual_mapped_rows=list(actual),
        existing_process_maps_rows=list(process_rows),
        read_contract='same existing single proc maps read; no additional process/memory reads',
        comparison='exact selected module rows unequal; original failure retained',
        accepted_new_mapping=False)
    return error


def preserve_mapping_failure(error,path):
    detail=getattr(error,'module_mapping_failure',None)
    if detail is None:
        return
    # The caller supplies its already private owned Evidence directory. O_EXCL
    # never follows an existing link or overwrites a previous failure receipt.
    descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8')as stream:
            descriptor=None
            json.dump(detail,stream,indent=2,allow_nan=False)
            stream.write('\n')
    finally:
        if descriptor is not None:
            os.close(descriptor)
