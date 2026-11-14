"""Reproducible DISABLED A1 fork; never loads Xlib or starts a native role."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
from a1_passive_xrecord import method_fingerprints
import shutil

PARENT=Path('/srv/tse-a1-release-deadline-root-frozen-20261114')
PARENT_SHA='2665517067a491e00607c7e4f88d5c3585739c66896f24c26b25eff672b7d136'
CORE_PARENT=Path('/srv/tse-own-xrecord-core-method-root-frozen-20261114')
CORE_SHA='43d38e727666d171bc9c6d021d4af018c60fe0279583c6636949d246e0f549ec'
CORE_FILES=('xrecord_core_method.py','xrecord_core_native.py','xrecord_core_worker.py','xrecord_core_process.py')
ADDITIONS=('a1_passive_xrecord.py','a1_passive_xrecord_worker.py','a1_passive_xrecord_evidence.py','prepare_a1_passive_xrecord.py','test_a1_passive_xrecord.py','test_a1_passive_xrecord_worker.py','test_a1_passive_xrecord_evidence.py','test_prepare_a1_passive_xrecord.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def once(text,old,new):
 if text.count(old)!=1:raise ValueError('exact prospective A1 source anchor differs:'+old[:100])
 return text.replace(old,new,1)


def transform_runner(source):
 source=once(source,'from a1_mapping_failure_receipt import preserve_mapping_failure','from a1_mapping_failure_receipt import preserve_mapping_failure\nfrom a1_passive_xrecord import PassiveRecorder,instrument_transport,require_method_qualification')
 source=once(source,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
 source=once(source,"PREFIX='ssam-a1-release-deadline-root-20261114'","PREFIX='ssam-a1-passive-xrecord-disabled-20261114'")
 source=once(source,"E=BASE/('a1-release-deadline-'","E=BASE/('a1-passive-xrecord-'")
 source=once(source,"assert mode in ('instrumented-trace','uninstrumented-control'),'fixed diagnostic mode'","assert mode=='instrumented-trace','fixed passive instrumented diagnostic mode'")
 source=once(source," assert manifest['runtime_reviewed'] is True,'frozen runtime review receipt required'"," assert manifest['runtime_reviewed'] is True,'frozen runtime review receipt required'\n require_method_qualification(manifest['passive_xrecord'])")
 source=once(source,'collector=None;input_scope=InputScope()','collector=None;passive=None;input_scope=InputScope()')
 source=once(source,'    endpoints[role]=Endpoint(pin,t,',"    if role=='vanilla':instrument_transport(t)\n    endpoints[role]=Endpoint(pin,t,")
 source=once(source,"    def traced_before_press():\n     if mode=='instrumented-trace':collector.before_input(control=control,pixels=trace_pixels)","    def traced_before_press():\n     assert passive is not None,'passive recorder binding required before input'\n     passive.before_input()\n     if mode=='instrumented-trace':collector.before_input(control=control,pixels=trace_pixels)")
 source=once(source,'    nonlocal collector\n','    nonlocal collector,passive\n')
 anchor="    collector=WorkerProxy.start(config_path);report['collector_arm']=collector.arm();save()"
 addition="""    collector=WorkerProxy.start(config_path);report['collector_arm']=collector.arm();save()
    display_guard(154);dr=displays[154];dp=Path('/proc')/str(dr['identity'][0])
    passive_scope=dict(manifest['passive_xrecord'])
    passive_scope['current_display_owner']={'identity':dr['identity'],'unit':display_unit(154),
     'argv':[v.decode()for v in (dp/'cmdline').read_bytes().rstrip(b'\\0').split(b'\\0')],
     'socket_pin':dr['socket_pin']}
    passive=PassiveRecorder.start(E,{'passive_xrecord':passive_scope},config,endpoints['vanilla'].transport)
    report['passive_xrecord_arm']=passive.arm();save()"""
 source=once(source,anchor,addition)
 source=once(source,'   # Parent never enters Frida:',"   if passive is not None:\n    try:report['passive_xrecord']=passive.close(report.get('input_phase_timings',[]))\n    except BaseException as error:report['errors'].append('passive recorder cleanup:'+repr(error))\n   # Parent never enters Frida:")
 source=once(source,"report['trace_evidence_complete']=trace_complete(report,verdict)","report['trace_evidence_complete']=trace_complete(report,verdict) and report.get('passive_xrecord',{}).get('status')=='PASS_PASSIVE_XRECORD_DIAGNOSTIC_ONLY'")
 source=once(source,"choices=('instrumented-trace','uninstrumented-control')","choices=('instrumented-trace',)")
 ast.parse(source);return source




def prepare(destination):
 dest=Path(destination).resolve();source=Path(__file__).resolve().parent
 if dest.exists():raise ValueError('fresh disabled destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA or sha(CORE_PARENT/'source-manifest.json')!=CORE_SHA:raise ValueError('reviewed parent/core manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text());cm=json.loads((PARENT/'collector/source-manifest.json').read_text())
 for p,h in m['runtime_dependencies'].items():
  if sha(p)!=h:raise ValueError('A1 parent dependency changed')
 corem=json.loads((CORE_PARENT/'source-manifest.json').read_text())
 for name in CORE_FILES:
  if sha(CORE_PARENT/name)!=corem['files'][name]:raise ValueError('method qualified core source changed')
 old=(PARENT/'run_dual.py').read_text();new=transform_runner(old)
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 (dest/'run_dual.py').write_text(new)
 for name in ADDITIONS:shutil.copy2(source/name,dest/name)
 (dest/'passive-core').mkdir()
 for name in CORE_FILES:shutil.copy2(CORE_PARENT/name,dest/'passive-core'/name)
 worker=(dest/'a1_input_worker.py').read_text();(dest/'a1_input_worker.py').write_text(once(worker,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False'))
 collector=(dest/'collector/a1_original_input_collector.py').read_text();collector=once(collector,'RUNTIME_REVIEWED = True','RUNTIME_REVIEWED = False');collector=once(collector,str(PARENT/'collector'),str(dest/'collector'))
 (dest/'collector/a1_original_input_collector.py').write_text(collector)
 def mapped(p):q=Path(p);return dest/q.relative_to(PARENT)if q.is_relative_to(PARENT)else q
 def repin(pins):return{str(mapped(p)):sha(mapped(p))for p in pins}
 def write(p,data):p.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')
 cm['runtime_reviewed']=False;cm['source_pins']=repin(cm['source_pins']);write(dest/'collector/source-manifest.json',cm)
 m.update(schema='DISABLED_A1_PASSIVE_XRECORD_V1',runtime_reviewed=False,runtime_performed=False,gate='DISABLED_REVIEW_SEPARATE_METHOD_ROOT_FREEZE_REQUIRED',collector_source=str(dest/'collector/a1_original_input_collector.py'))
 m['runtime_dependencies']=repin(m['runtime_dependencies'])
 for name in ADDITIONS[:3]:m['runtime_dependencies'][str(dest/name)]=sha(dest/name)
 for name in CORE_FILES:m['runtime_dependencies'][str(dest/'passive-core'/name)]=sha(dest/'passive-core'/name)
 m['diagnostic_source_sha256']={p:sha(dest/p)for p in m['diagnostic_source_sha256']}
 for name in ADDITIONS:m['diagnostic_source_sha256'][name]=sha(dest/name)
 m['passive_xrecord']=dict(parent_manifest_sha256=PARENT_SHA,core_parent_manifest_sha256=CORE_SHA,core_native_result_sha256='f0c3acc94c3c75a7ae0b648e24aa64d098cbf5a2ac4b81cff5be9aa8775ab470',binding_qualification=None,method_fingerprints=method_fingerprints(source,CORE_PARENT),native_performed=False,qualified=False,retail_qualified=False,a1_pass=False,gain_fixed=False,display=':154',trace_seconds_max=15,records_max=1024,raw_bytes_max=16384,total_bytes_max=2097152,emissions_max=96,unchanged_cp_ack_gain_eps_input_release=True)
 write(dest/'source-manifest.json',m)
 (dest/'passive-xrecord-runner.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='reviewed-A1/run_dual.py',tofile='disabled-passive/run_dual.py')))
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),diagnostic_pins=len(m['diagnostic_source_sha256']),collector_pins=len(cm['source_pins']),core_pins=len(CORE_FILES),runtime_reviewed=False,binding_method_qualified=False,native_performed=False)
 write(dest/'PASSIVE-HANDOFF.json',receipt);return receipt

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);print(json.dumps(prepare(p.parse_args().destination),indent=2))
