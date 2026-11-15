"""Derive one fresh DISABLED normal-mouse pitch-feedback fork. Never runs it."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil

PARENT=Path('/srv/tse-a1-xres-lifecycle-root-frozen-20261115')
PARENT_SHA='e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c'
CORE_FILES=('xrecord_core_method.py','xrecord_core_native.py','xrecord_core_worker.py','xrecord_core_process.py')
COPIES=('a1_pitch_feedback.py','prepare_a1_pitch_feedback.py','test_a1_pitch_feedback.py','test_prepare_a1_pitch_feedback.py')
GATES=('a1_input_worker.py','a1_passive_xrecord.py','a1_passive_xrecord_worker.py','a1_xres_attribution.py','a1_xres_attribution_worker.py','collector/a1_original_input_collector.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def once(text,old,new):
 if text.count(old)!=1:raise ValueError('exact pitch feedback derivation anchor changed: '+old)
 return text.replace(old,new,1)


def replace_function(text,name,replacement):
 matches=[n for n in ast.walk(ast.parse(text))if isinstance(n,ast.FunctionDef)and n.name==name]
 if len(matches)!=1:raise ValueError('unique pitch feedback function anchor required: '+name)
 node=matches[0];lines=text.splitlines(True)
 return ''.join(lines[:node.lineno-1])+replacement+'\n'+''.join(lines[node.end_lineno:])


def transform(text):
 text=once(text,"from a1_xres_attribution import PassiveRecorder,instrument_transport,require_method_qualification", "from a1_passive_xrecord import instrument_transport,prepare_xtest_transport\nimport a1_pitch_feedback as PF")
 text=once(text,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
 text=once(text,"PREFIX='ssam-a1-xres-lifecycle-root-20261115'","PREFIX='ssam-a1-pitch-feedback-disabled-20261115'")
 text=once(text,"def main(duration=30,mode='instrumented-trace'):","def main(duration=90,mode='pitch-feedback'):")
 text=once(text,"assert mode=='instrumented-trace','fixed passive instrumented diagnostic mode'","assert mode=='pitch-feedback','fixed normal mouse pitch-feedback diagnostic mode'")
 text=once(text," require_method_qualification(manifest['passive_xrecord'])\n",'')
 text=once(text,"E=BASE/('a1-xres-lifecycle-root-'","E=BASE/('a1-pitch-feedback-'")
 text=once(text,'input_scope=InputScope()','input_scope=PF.FeedbackScope()')
 text=once(text,"'scope':'OWN_ORIGINAL_INHERITED_CALIBRATION_AIM_NO_FIRE'","'scope':'OWN_ORIGINAL_BOUNDED_PITCH_FEEDBACK_RETURN_NO_FIRE'")
 text=once(text,"'collector_requested':mode=='instrumented-trace'","'collector_requested':False")
 text=once(text,"    assert mode=='uninstrumented-control'or collector is not None,'no input before collector complete binding'", "    assert mode=='pitch-feedback'and collector is None,'pitch scope has no collector'")
 text=once(text,"     if mode=='instrumented-trace':collector.before_input(control=control,pixels=trace_pixels)\n",'')
 text=replace_function(text,'trace_preparation',"""   def trace_preparation():
    nonlocal passive
    assert collector is None and mode=='pitch-feedback','normal mouse only entry required'
    import ctypes as c
    transport=endpoints['vanilla'].transport
    # Same public counter ABI as the parent's qualified controller_gc, without
    # invoking an unused GC/resource getter or any extra native metadata read.
    transport.x.XNextRequest.argtypes=[c.c_void_p];transport.x.XNextRequest.restype=c.c_ulong
    report['pitch_transport_preparation']=prepare_xtest_transport(transport)
    passive=PF.FeedbackJournal(transport)
    transport._passive_xrecord_proxy.observer=passive
    save()
    return PF.run(native_roles,bounded_step,time.monotonic,time.sleep,report['shooter_preparation'],started=started,runner_deadline=started+duration)""")
 text=once(text,"assert report['shooter_preparation']['status']=='TRACE_ONLY_NO_FIRE','trace-only preparation not completed'", "assert report['shooter_preparation']['status']=='PASS_LIMITED_NATIVE_ACK_PITCH_FEEDBACK_RETURN_ONLY','pitch feedback not completed'")
 text=once(text,"try:report['passive_xrecord']=passive.close(report.get('input_phase_timings',[]))", "try:report['pitch_journal']=passive.close(E)")
 text=once(text,"if report['status']=='CLEANUP_PENDING':report['status']='TRACE_ONLY_NO_FIRE'if mode=='instrumented-trace'else'CONTROL_ONLY_NO_FIRE'", "if report['status']=='CLEANUP_PENDING':report['status']='PASS_LIMITED_NATIVE_ACK_PITCH_FEEDBACK_RETURN_ONLY'")
 text=once(text,"report['trace_evidence_complete']=trace_complete(report,verdict) and report.get('passive_xrecord',{}).get('status')=='PASS_PASSIVE_XRECORD_DIAGNOSTIC_ONLY'", "report['trace_evidence_complete']=False\n   report['pitch_feedback_evidence_complete']=PF.journal_complete(report,verdict)")
 text=once(text,"if not report['trace_evidence_complete']:report['status']='FAIL'", "if not report['pitch_feedback_evidence_complete']:report['status']='FAIL'")
 text=once(text,"if not report['trace_evidence_complete']:raise RuntimeError('trace-only evidence incomplete; see '+str(E/'result.json'))", "if not report['pitch_feedback_evidence_complete']:raise RuntimeError('pitch-only evidence incomplete; see '+str(E/'result.json'))")
 text=once(text,"description='Disabled own Original passive trace, inherited calibration/aim, no fire; Root freeze required'", "description='Disabled own Original bounded mouse pitch feedback, no fire; Root freeze required'")
 text=once(text,"choices=('instrumented-trace',),default='instrumented-trace'", "choices=('pitch-feedback',),default='pitch-feedback'")
 return text


def prepare(destination):
 dest=Path(destination).resolve();source=Path(__file__).resolve().parent
 if dest.exists():raise ValueError('fresh disabled pitch feedback destination required')
 if sha(PARENT/'source-manifest.json')!=PARENT_SHA:raise ValueError('qualified full parent manifest changed')
 m=json.loads((PARENT/'source-manifest.json').read_text());cm=json.loads((PARENT/'collector/source-manifest.json').read_text())
 for pins,base in((m['runtime_dependencies'],Path('/')),(m['diagnostic_source_sha256'],PARENT),(cm['source_pins'],Path('/'))):
  for path,h in pins.items():
   if sha(base/path)!=h:raise ValueError('full parent source pin changed: '+path)
 shutil.copytree(PARENT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));dest.chmod(0o700)
 for name in COPIES:shutil.copy2(source/name,dest/name)
 (dest/'run_dual.py').write_text(transform((PARENT/'run_dual.py').read_text()))
 collector=dest/'collector/a1_original_input_collector.py'
 collector.write_text(once(collector.read_text(),str(PARENT/'collector'),str(dest/'collector')))
 for name in GATES:
  p=dest/name;text=p.read_text();text,count=re.subn(r'(?m)^(RUNTIME_REVIEWED\s*=\s*)True\s*$',r'\g<1>False',text)
  if count not in(0,1)or not re.search(r'(?m)^RUNTIME_REVIEWED\s*=\s*False\s*$',text):raise ValueError('disabled inherited gate missing: '+name)
  p.write_text(text)
 for name in CORE_FILES:
  if (dest/'passive-core'/name).read_bytes()!=(PARENT/'passive-core'/name).read_bytes():raise ValueError('immutable qualified Core changed: '+name)
 def mapped(path):
  p=Path(path);return dest/p.relative_to(PARENT)if p.is_relative_to(PARENT)else p
 def repin(pins):return{str(mapped(p)):sha(mapped(p))for p in pins}
 def write(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
 cm['runtime_reviewed']=False;cm['source_pins']=repin(cm['source_pins']);write(dest/'collector/source-manifest.json',cm)
 m.update(schema='DISABLED_ORIGINAL_NATIVE_ACK_PITCH_FEEDBACK_V1',runtime_reviewed=False,runtime_performed=False,gate='DISABLED_PITCH_FEEDBACK_SOURCE_AND_RUNTIME_REVIEW_REQUIRED',collector_source=str(collector))
 m['runtime_dependencies']=repin(m['runtime_dependencies'])
 for name in COPIES[:2]:m['runtime_dependencies'][str(dest/name)]=sha(dest/name)
 m['diagnostic_source_sha256']={name:sha(dest/name)for name in m['diagnostic_source_sha256']}
 for name in COPIES:m['diagnostic_source_sha256'][name]=sha(dest/name)
 m['pitch_feedback']=dict(parent_manifest_sha256=PARENT_SHA,mode='pitch-feedback',initial_vertical_pixels=12,corrective_vertical_pixels=[-1,1],seconds_per_action=.1,max_hold_seconds=.35,max_actions=48,max_attempts=96,ack_seconds=2,active_seconds=20,cp_seconds=85,runner_seconds=90,input_reserve_seconds=2.35,return_boundary_deg=.75,eps=.001,frida_armed=False,record_armed=False,xres_armed=False,gain_proven=False,normal_route_or_fire=False,qualified=False,native_performed=False,automatic_retry=False)
 write(dest/'source-manifest.json',m)
 changed=('run_dual.py',*GATES)
 (dest/'pitch-feedback-source.diff').write_text(''.join(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),(dest/name).read_text().splitlines(True),fromfile='full-parent/'+name,tofile='disabled-pitch-feedback/'+name))for name in changed))
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),diagnostic_pins=len(m['diagnostic_source_sha256']),collector_pins=len(cm['source_pins']),runtime_reviewed=False,native_performed=False,qualified=False)
 write(dest/'PITCH-FEEDBACK-HANDOFF.json',receipt)
 for p in dest.rglob('*'):
  if p.is_file():p.chmod(0o600)
 return receipt


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(parser.parse_args().destination),indent=2))
