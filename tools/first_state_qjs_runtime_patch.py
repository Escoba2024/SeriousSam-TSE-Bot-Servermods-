"""Exact explicit-QJS condition; reuse the pinned cold RPC, never a fallback."""
from tools import first_state_v8_runtime_patch as v8

PYTHON_SHA=v8.PYTHON_SHA
BODY_SHA=v8.BODY_SHA
COMPILED_SHA=v8.COMPILED_SHA
PAIRS=(
    (v8.V8_CREATE,"  self.script=self.session.create_script(self.source,runtime='qjs')\n"),
    ("'requested_runtime':'v8'","'requested_runtime':'qjs'"),
    ("expected={'runtime':'V8'","expected={'runtime':'QJS'"),
)

def patch_python(text):
    result=v8.patch_python(text)
    for old,new in PAIRS:
        v8.require(result.count(old)==1,'exact explicit runtime fragment required')
        result=result.replace(old,new,1)
    return result

def to_v8_python(text):
    result=text
    for old,new in reversed(PAIRS):
        v8.require(result.count(new)==1,'exact QJS runtime inverse required')
        result=result.replace(new,old,1)
    v8.reverse_python(result)  # Validate every unchanged byte, not just fragments.
    return result

def reverse_python(text):
    return v8.reverse_python(to_v8_python(text))

# The cold RPC reports Script.runtime truthfully for either requested engine.
# No engine-dependent change to G, existing RPCs, guards or warm callbacks.
patch_body=v8.patch_body
reverse_body=v8.reverse_body
patch_compiled=v8.patch_compiled
reverse_compiled=v8.reverse_compiled
