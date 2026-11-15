"""Create one fresh DISABLED keyboard-only Original geometry qualification fork.

This builder never imports or executes its generated controller.  The retained
passive/Frida libraries are inherited dependencies, with their gates disabled;
the keyboard entry path neither creates those workers nor arms a recorder.
"""
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
COPIES=('a1_keyboard_input.py','a1_keyboard_geometry.py','prepare_a1_keyboard_qualification.py','test_a1_keyboard_input.py','test_a1_keyboard_geometry.py','test_prepare_a1_keyboard_qualification.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(text,old,new):
 if text.count(old)!=1:raise ValueError('exact keyboard derivation anchor changed: '+old)
 return text.replace(old,new,1)


def replace_function(text,name,replacement):
 matches=[n for n in ast.walk(ast.parse(text))if isinstance(n,ast.FunctionDef)and n.name==name]
 if len(matches)!=1:raise ValueError('unique keyboard function anchor required: '+name)
 node=matches[0];lines=text.splitlines(True)
 return ''.join(lines[:node.lineno-1])+replacement+'\n'+''.join(lines[node.end_lineno:])


def transform(text):
 text=once(text,"from a1_xres_attribution import PassiveRecorder,instrument_transport,require_method_qualification", "from a1_passive_xrecord import instrument_transport,prepare_xtest_transport\nfrom a1_keyboard_input import KeyboardTransport,KeyboardEndpoint,KeyboardJournal,install as install_keyboard,keyboard_journal_complete\nimport a1_keyboard_geometry as KG")
 text=once(text,'RUNTIME_REVIEWED=True','RUNTIME_REVIEWED=False')
 text=once(text,"PREFIX='ssam-a1-xres-lifecycle-root-20261115'","PREFIX='ssam-a1-keyboard-disabled-20261115'")
 text=once(text,"def main(duration=30,mode='instrumented-trace'):","def main(duration=90,mode='keyboard-qualification'):")
 text=once(text,"assert mode=='instrumented-trace','fixed passive instrumented diagnostic mode'","assert mode=='keyboard-qualification','fixed keyboard-only qualification mode'")
 text=once(text," require_method_qualification(manifest['passive_xrecord'])\n",'')
 text=once(text,"E=BASE/('a1-xres-lifecycle-root-'","E=BASE/('a1-keyboard-qualification-'")
 text=once(text,'input_scope=InputScope()','input_scope=KG.KeyboardScope()')
 text=once(text,"'scope':'OWN_ORIGINAL_INHERITED_CALIBRATION_AIM_NO_FIRE'","'scope':'OWN_ORIGINAL_SIX_KEYBOARD_ACTION_GEOMETRY_NO_FIRE'")
 text=once(text,"'collector_requested':mode=='instrumented-trace'","'collector_requested':False")
 text=once(text,"   report['controls_input_profile']=NIP.install(transaction,E);save()", "   report['controls_input_profile']=NIP.install(transaction,E);save()\n   report['keyboard_controls_profile']=install_keyboard(transaction,E);save()")
 text=once(text,"    t=X11Transport(pin,lambda n=number:display_guard(n))", "    t=(KeyboardTransport if role=='vanilla'else X11Transport)(pin,lambda n=number:display_guard(n))")
 text=once(text,"    endpoints[role]=Endpoint(pin,t,lambda r=role:own_identity(r),lambda n=number:display_guard(n))", "    endpoints[role]=(KeyboardEndpoint if role=='vanilla'else Endpoint)(pin,t,lambda r=role:own_identity(r),lambda n=number:display_guard(n))")
 text=once(text,'    trace_pixels=input_scope.admit(role,control,seconds,pixels)', "    assert pixels is None,'keyboard qualification never accepts pixels'\n    trace_pixels=None;input_scope.admit(role,control,seconds)")
 text=once(text,"    assert mode=='uninstrumented-control'or collector is not None,'no input before collector complete binding'", "    assert mode=='keyboard-qualification'and collector is None,'keyboard scope has no collector'")
 text=once(text,"     if mode=='instrumented-trace':collector.before_input(control=control,pixels=trace_pixels)\n",'')
 text=replace_function(text,'trace_preparation',"""   def trace_preparation():
    nonlocal passive
    assert collector is None and mode=='keyboard-qualification','keyboard-only entry required'
    transport=endpoints['vanilla'].transport
    report['keyboard_transport_preparation']=prepare_xtest_transport(transport)
    passive=KeyboardJournal(transport)
    transport._passive_xrecord_proxy.observer=passive
    report['keyboard_keycodes']={control:transport.keys[control]for control in ('yaw_left','yaw_right','pitch_up','pitch_down','forward')}
    save()
    return KG.run(native_roles,bounded_step,time.monotonic,time.sleep,report['shooter_preparation'],started=started)""")
 text=once(text,"assert report['shooter_preparation']['status']=='TRACE_ONLY_NO_FIRE','trace-only preparation not completed'", "assert report['shooter_preparation']['status']=='PASS_LIMITED_ORIGINAL_KEYBOARD_GEOMETRY_ONLY','keyboard preparation not completed'")
 text=once(text,"try:report['passive_xrecord']=passive.close(report.get('input_phase_timings',[]))", "try:report['keyboard_journal']=passive.close(E)")
 text=once(text,"if report['status']=='CLEANUP_PENDING':report['status']='TRACE_ONLY_NO_FIRE'if mode=='instrumented-trace'else'CONTROL_ONLY_NO_FIRE'", "if report['status']=='CLEANUP_PENDING':report['status']='PASS_LIMITED_ORIGINAL_KEYBOARD_GEOMETRY_ONLY'")
 text=once(text,"report['trace_evidence_complete']=trace_complete(report,verdict) and report.get('passive_xrecord',{}).get('status')=='PASS_PASSIVE_XRECORD_DIAGNOSTIC_ONLY'", "report['trace_evidence_complete']=False\n   report['keyboard_evidence_complete']=keyboard_journal_complete(report,verdict)")
 text=once(text,"if not report['trace_evidence_complete']:report['status']='FAIL'", "if not report['keyboard_evidence_complete']:report['status']='FAIL'")
 text=once(text,"if not report['trace_evidence_complete']:raise RuntimeError('trace-only evidence incomplete; see '+str(E/'result.json'))", "if not report['keyboard_evidence_complete']:raise RuntimeError('keyboard-only evidence incomplete; see '+str(E/'result.json'))")
 text=once(text,"description='Disabled own Original passive trace, inherited calibration/aim, no fire; Root freeze required'", "description='Disabled own Original six keyboard actions and geometry, no fire; Root freeze required'")
 text=once(text,"choices=('instrumented-trace',),default='instrumented-trace'", "choices=('keyboard-qualification',),default='keyboard-qualification'")
 return text


def prepare(destination):
 dest=Path(destination).resolve();source=Path(__file__).resolve().parent
 if dest.exists():raise ValueError('fresh disabled keyboard destination required')
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
 gates=('a1_input_worker.py','a1_passive_xrecord.py','a1_passive_xrecord_worker.py','a1_xres_attribution.py','a1_xres_attribution_worker.py','collector/a1_original_input_collector.py')
 for name in gates:
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
 m.update(schema='DISABLED_ORIGINAL_KEYBOARD_GEOMETRY_QUALIFICATION_V1',runtime_reviewed=False,runtime_performed=False,gate='DISABLED_KEYBOARD_SOURCE_AND_RUNTIME_REVIEW_REQUIRED',collector_source=str(collector))
 m['runtime_dependencies']=repin(m['runtime_dependencies'])
 for name in COPIES[:3]:m['runtime_dependencies'][str(dest/name)]=sha(dest/name)
 m['diagnostic_source_sha256']={name:sha(dest/name)for name in m['diagnostic_source_sha256']}
 for name in COPIES:m['diagnostic_source_sha256'][name]=sha(dest/name)
 m['keyboard_qualification']=dict(parent_manifest_sha256=PARENT_SHA,mode='keyboard-qualification',actions=6,key_calls=12,controls=['yaw_left','forward','yaw_right','forward','pitch_up','pitch_down'],seconds_per_action=.1,max_hold_seconds=.35,max_actions=48,max_attempts=96,ack_seconds=2,cp_seconds=85,runner_seconds=90,eps=.001,frida_armed=False,record_armed=False,wire_proven=False,mouse_gain_proven=False,normal_route_or_fire=False,qualified=False,native_performed=False,automatic_retry=False)
 write(dest/'source-manifest.json',m)
 changed=('run_dual.py',*gates)
 (dest/'keyboard-source.diff').write_text(''.join(''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),(dest/name).read_text().splitlines(True),fromfile='full-parent/'+name,tofile='disabled-keyboard/'+name))for name in changed))
 receipt=dict(package=str(dest),manifest_sha256=sha(dest/'source-manifest.json'),runtime_pins=len(m['runtime_dependencies']),diagnostic_pins=len(m['diagnostic_source_sha256']),collector_pins=len(cm['source_pins']),runtime_reviewed=False,native_performed=False,qualified=False)
 write(dest/'KEYBOARD-QUALIFICATION-HANDOFF.json',receipt)
 for p in dest.rglob('*'):
  if p.is_file():p.chmod(0o600)
 return receipt


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--destination',type=Path,required=True)
 print(json.dumps(prepare(parser.parse_args().destination),indent=2))
