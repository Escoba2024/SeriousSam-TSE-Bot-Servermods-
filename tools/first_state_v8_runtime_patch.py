"""Exact source-only V8 request/cold identity transform; no runtime activation."""
import hashlib

PYTHON_SHA='d2801018afb64702826d9329f082ee314e718ab149f6211983170e4b04a12cd7'
BODY_SHA='abeab90d6a656c53e4acb349313686ead6a81f1b95a463e1dcd2de1262deb4d8'
COMPILED_SHA='f5cc6498598fbd9de77dfc229ad04a4c7b0275be2b0c6541c9a5857b9c144c78'
MARKER="'use strict';\n// G is composed from preserved PE32 bytes. No native function is invoked here.\n"
CREATE='  self.script=self.session.create_script(self.source)\n'
V8_CREATE="  self.script=self.session.create_script(self.source,runtime='v8')\n"
LOAD="  self.script.on('message',message);self.script.load()\n"
PYTHON_ADDITION="""  runtime=self.script.exports_sync.runtimeidentity()
  atomic_json(self.evidence/'observer-runtime-identity.json',{'requested_runtime':'v8','identity':runtime})
  expected={'runtime':'V8','pid':self.context.expected['pid'],'arch':'ia32','pointer_size':4}
  require(type(runtime)is dict and set(runtime)==set(expected)and all(type(runtime[k])is type(v)and runtime[k]==v for k,v in expected.items()),'same observer runtime identity differs')
"""
JS_ANCHOR='rpc.exports={\n'
JS_ADDITION=" runtimeidentity(){return {runtime:Script.runtime,pid:Process.id,arch:Process.arch,pointer_size:Process.pointerSize};},\n"

def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)

def patch_python(text):
    require(digest(text)==PYTHON_SHA,'exact disabled NativePorts parent required')
    require(text.count(CREATE)==text.count(LOAD)==1,'exact one create/load required')
    return text.replace(CREATE,V8_CREATE,1).replace(LOAD,LOAD+PYTHON_ADDITION,1)

def reverse_python(text):
    require(text.count(V8_CREATE)==text.count(LOAD+PYTHON_ADDITION)==1,'exact V8 create/cold identity inverse required')
    result=text.replace(V8_CREATE,CREATE,1).replace(LOAD+PYTHON_ADDITION,LOAD,1)
    require(digest(result)==PYTHON_SHA,'entire NativePorts Python inverse differs')
    return result

def patch_body(text):
    require(digest(text)==BODY_SHA,'exact disabled Observer body required')
    require(text.count(JS_ANCHOR)==1,'exact one rpc exports required')
    return text.replace(JS_ANCHOR,JS_ANCHOR+JS_ADDITION,1)

def reverse_body(text):
    require(text.count(JS_ANCHOR+JS_ADDITION)==1,'exact cold identity RPC inverse required')
    result=text.replace(JS_ANCHOR+JS_ADDITION,JS_ANCHOR,1)
    require(digest(result)==BODY_SHA,'entire Observer body inverse differs')
    return result

def patch_compiled(text):
    require(digest(text)==COMPILED_SHA,'exact disabled compiled Observer required')
    require(text.count(MARKER)==1,'exact compiled body marker required')
    prefix,body=text.split(MARKER,1)
    return prefix+patch_body(MARKER+body)

def reverse_compiled(text):
    require(text.count(MARKER)==1,'exact compiled inverse marker required')
    prefix,body=text.split(MARKER,1)
    result=prefix+reverse_body(MARKER+body)
    require(digest(result)==COMPILED_SHA,'entire compiled/G inverse differs')
    return result
