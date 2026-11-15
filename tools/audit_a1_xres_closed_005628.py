"""Read only the closed005628 archive; no display/process/input/native calls.

Writes one new private O_EXCL receipt. Replays pinned pure decoders/auditors;
does not import a controller, worker or runtime adapter.
"""
import argparse
import collections
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import sys

EVIDENCE=Path('/srv/tse-milestone-a-evidence-20261111/a1-xres-lifecycle-root-20261115-005628')
SOURCE=Path('/srv/tse-a1-xres-lifecycle-root-frozen-20261115')
RESULT_SHA='3e4398c98b2518b4dc44882243d4218d4f3f4678b8a1d36f0c34accaf6035e35'
MANIFEST_SHA='e9cb52a1135ea3046570fdaaac6e2f37ac2117535b8d4c312239f39d7cbec90c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pure(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def read(directory=EVIDENCE,source=SOURCE):
 e=Path(directory);s=Path(source)
 load=lambda n:json.loads((e/n).read_bytes())
 lines=lambda n:[json.loads(line)for line in(e/n).read_bytes().splitlines()]
 assert sha(e/'result.json')==RESULT_SHA and sha(s/'source-manifest.json')==MANIFEST_SHA
 r=load('result.json');manifest=load('source-manifest.json')
 assert r['status']=='FAIL'and r['errors']==["ValueError('opposite pitch gain does not reproduce')"]
 assert (e/'source-manifest.json').read_bytes()==(s/'source-manifest.json').read_bytes()
 for name in('controller-source.py','rotation_diagnostics.py','colt_preparation.py','shooter_policy.py'):
  assert(e/name).read_bytes()==(s/('run_dual.py'if name=='controller-source.py'else name)).read_bytes()
 sources=('a1_xres_attribution_evidence.py','xres_pid_method.py','a1_passive_xrecord_evidence.py','a1_passive_xrecord.py','a1_xres_attribution.py','a1_xres_attribution_worker.py','passive-core/xrecord_core_method.py','passive-core/xrecord_core_native.py','passive-core/xrecord_core_process.py','passive-core/xrecord_core_worker.py','collector/a1_original_input_collector.py','collector/a1_original_input_readonly.js','collector/original-input-guards.json')
 for name in sources:
  path=s/name;assert manifest['runtime_dependencies'][str(path)]==sha(path)
 rows=lines('passive-xrecord/record-raw.jsonl');emissions=load('passive-xrecord/controller-emissions.json');attempts=load('passive-xrecord/controller-emission-attempts.json');native=load('passive-xrecord/recorder-native-close.json');metadata=load('passive-xrecord/xres-attribution.json')
 core=pure('closed005628_core',s/'passive-core/xrecord_core_method.py');trace=core.CoreTrace(xtest_opcode=r['passive_xrecord_arm']['xtest_opcode'])
 for index,row in enumerate(rows):
  assert row['callback_serial']==index+1
  decoded=trace.accept(**{k:row[k]for k in('category','client_base','client_sequence','server_time','client_swapped')},wire=bytes.fromhex(row['wire_hex']))
  assert decoded=={k:v for k,v in row.items()if k not in('callback_serial','received_monotonic')}
 assert len(rows)==310 and not trace.pending and trace.unsupported==4
 evidence=pure('closed005628_evidence',s/'a1_passive_xrecord_evidence.py')
 audited=evidence.audit_trace(e/'passive-xrecord',emissions,r['passive_xrecord_arm'],native,r['input_phase_timings'])
 assert audited==r['passive_xrecord']['evidence'] and len(emissions)==len(attempts)==8 and len(r['input_phase_timings'])==6
 sys.path.insert(0,str(s)) # Only the pinned pure xres_pid_method dependency.
 attribution=pure('closed005628_attribution',s/'a1_xres_attribution_evidence.py')
 attributed=attribution.attribute(rows,metadata['snapshots'],metadata['expected'],native)
 assert attributed==r['passive_xrecord']['xres_attribution']
 side=native['xres_evidence'];assert side['path']=='xres-attribution.json'and side['bytes']==(e/'passive-xrecord/xres-attribution.json').stat().st_size and side['sha256']==sha(e/'passive-xrecord/xres-attribution.json')
 assert native['xres_summary']['free_counts']==metadata['free_counts']==dict(client_arrays_allocated=2,client_arrays_freed=2,id_arrays_allocated=28,id_arrays_freed=28)
 original=set(attributed['original_bases']);changed=set(attributed['lifecycle_changed_bases']);controller=r['passive_xrecord_arm']['bindings']['controller_transport']
 def alias(base):return'CONTROL_OR_DEVICE'if base==0 else'OWN_CONTROLLER_CONNECTION'if base==controller else'CURRENT_OWN_ORIGINAL_CONNECTION'if base in original else'LIFECYCLE_CHANGED_UNKNOWN'if base in changed else'UNKNOWN'
 wire=[]
 for row in rows:
  item=dict(row,connection_class=alias(row['client_base']));raw=bytes.fromhex(row['wire_hex']);endian='>'if row['client_swapped']else'<'
  if row['kind']=='query_pointer_request':item['query_window']=struct.unpack_from(endian+'I',raw,4)[0]
  if row['kind']=='query_pointer_reply':item.update(root_window=struct.unpack_from(endian+'I',raw,8)[0],child_window=struct.unpack_from(endian+'I',raw,12)[0],window_coordinates=list(struct.unpack_from(endian+'hh',raw,20)),same_screen=bool(raw[1]))
  if row['kind']=='warp_request':item.update(zip(('src_window','dst_window','src_x','src_y','src_width','src_height','dst_x_raw','dst_y_raw'),struct.unpack_from(endian+'IIhhHHhh',raw,4)))
  if row['kind']in('device_motion','delivered_motion'):item.update(zip(('root_window','event_window','child_window'),struct.unpack_from(('<'if row['client_base']==0 else endian)+'III',raw,8)))
  if row['kind']=='unsupported':item['adapter_typed_noncursor']=evidence.xtest(row,r['passive_xrecord_arm']['xtest_opcode'])
  wire.append(item)
 clients=[dict(client_base=base,connection_class=alias(base),kind_counts=dict(collections.Counter(v['kind']for v in rows if v['client_base']==base)),snapshot_base_pids=[[q['ids'][0]['pid']for q in snap['queries']if q['requested_kind']=='base'and q['requested_xid']==base]for snap in metadata['snapshots']])for base in sorted({row['client_base']for row in rows})]
 emission_bindings=[]
 for event in emissions:
  before,after=event['sequence_interval'];matches=[v for v in wire if v['client_base']==controller and before<=v['client_sequence']<after and evidence.xtest(v,r['passive_xrecord_arm']['xtest_opcode'])is not None]
  assert after-before==1 and len(matches)==1
  emission_bindings.append(dict(emission=event,wire_callback_serial=matches[0]['callback_serial'],wire=matches[0],sequence_binding='exact same controller Xclient and actual sequence interval; no clock equation'))
 envelopes=lines('original-input-trace.jsonl');records=[v for env in envelopes for v in env.get('packet',{}).get('records',[])]
 assert[v['sequence']for v in records]==list(range(1,279))
 inputs=[v for v in records if v['kind']=='input'];actions=[v for v in records if v['kind']=='action'];action_by_input={v['input_id']:v for v in actions}
 assert len(inputs)==len(actions)==len(action_by_input)==139 and len({v['thread']for v in records})==1 and{v['id']for v in inputs}==set(action_by_input)
 input_timeline=[]
 for i,env in enumerate(envelopes):
  for v in env.get('packet',{}).get('records',[]):
   if v['kind']!='input':continue
   a=action_by_input[v['id']]
   assert a['sequence']==v['sequence']+1 and a['id']==v['id']+1 and a['thread']==v['thread']
   assert a['entity_local_accumulator_after']-a['entity_local_accumulator_before']==a['raw_action_yaw']==-v['engine_x']
   assert a['action_yaw']==a['entity_local_accumulator_after']and a['entered_ms']<=a['compose_entered_ms']<=a['left_ms']
   assert v['cursor']['ok']is True and v['recenter']['ok']is True and v['engine_x']==v['cursor']['raw_dx']*.25 and v['engine_y']==-v['cursor']['raw_dy']*.25
   input_timeline.append(dict(envelope_index=i,host_drain_monotonic=env['host_monotonic'],input=v,action=a))
 nonzero=[v for v in input_timeline if v['input']['cursor']['raw_dx']or v['input']['cursor']['raw_dy']]
 assert[v['input']['id']for v in nonzero]==[55,139,223,257,259]
 profiles=collections.Counter(json.dumps(v['profile'],sort_keys=True)for v in records)
 packets=[env['packet']for env in envelopes if'packet'in env];final=packets[-1]
 assert final['calls']==278 and final['faults']==final['dropped']==final['in_flight']==final['game_state_writes']==0 and final['completed_sequences']==139 and final['restored']is True
 physical=[]
 for i,pair in enumerate(lines('rotation-pairs.jsonl')):
  item=dict(index=i,monotonic_started=pair['monotonic_started'],monotonic_finished=pair['monotonic_finished'])
  for role in('server','vanilla'):
   v=pair[role];item[role]={k:v[k]for k in('slot','entity_id','entity_pointer','world_pointer','spawned_tick','game_tick','process_identity','placement','rotation_diagnostic','colt_preparation','last_buttons','current_translation_absolute')}
  physical.append(item)
 assert len(physical)==59
 for role in('server','vanilla'):
  assert len({(v[role]['slot'],v[role]['entity_id'],v[role]['entity_pointer'],v[role]['world_pointer'],v[role]['spawned_tick'],tuple(v[role]['process_identity']))for v in physical})==1
  assert all(b[role]['game_tick']>=a[role]['game_tick']for a,b in zip(physical,physical[1:]))
 pitch=r['shooter_preparation']['pitch_calibration']['impulses'];assert len(pitch)==2
 def levels(frame):
  return {source:dict(game_tick=frame[source]['vanilla']['game_tick'],received_pitch=frame[source]['vanilla']['colt_preparation']['last_action_pitch_deg'],local_pitch=frame[source]['vanilla']['colt_preparation']['local_action_pitch_deg'],view_pitch=frame[source]['vanilla']['colt_preparation']['viewpoint'][4],body_placement=frame[source]['vanilla']['placement'],identity={k:frame[source]['vanilla'][k]for k in('slot','entity_id','entity_pointer','world_pointer','spawned_tick')})for source in('roles','client_roles')}
 pitch_summary=[]
 for event in pitch:
  pitch_summary.append(dict(pixels=event['pixels'],request_finished=event['request_finished'],pre_emission_checked_at=event['pre_emission_checked_at'],before=levels(event['pre_emission_frame']),after_input=levels(event['after_input_frame']),ack=levels(event['axis_ack']['frame']),ack_started=event['axis_ack']['frame']['monotonic_started'],ack_finished=event['axis_ack']['frame']['monotonic_finished'],axis_ack={k:v for k,v in event['axis_ack'].items()if k!='frame'}))
 assert[p['axis_ack']['gain_deg_per_pixel']for p in pitch]==[-.25,-.5]
 last_motion=next(v for v in wire if v['kind']=='xtest_relative_motion'and v['dy']==-12);last_window=[v for v in wire if v['callback_serial']>=last_motion['callback_serial']]
 windows=[]
 for motion in[v for v in wire if v['kind']=='xtest_relative_motion']:
  following=next((v['callback_serial']for v in wire if v['kind']=='xtest_relative_motion'and v['callback_serial']>motion['callback_serial']),len(rows)+1)
  windows.append(dict(motion=motion,until_callback_exclusive=following,wire_rows=[v for v in wire if motion['callback_serial']<=v['callback_serial']<following],scope='actual RECORD callback order only; not a per-GetCursorPos association'))
 last_warps=[v for v in last_window if v['kind']=='warp_request'];assert len(last_warps)==1
 last_original_replies=[v for v in last_window if v['kind']=='query_pointer_reply'and v['client_base']in original]
 assert[(v['root_x'],v['root_y'])for v in last_original_replies]==[(400,301)]+[(400,313)]*6
 assert all((v['root_x'],v['root_y'])==(400,313)for v in last_original_replies if v['callback_serial']>last_warps[0]['callback_serial'])
 assert last_warps[0]['server_time']-last_original_replies[0]['server_time']==50
 rd=r['shooter_preparation']['rotation_diagnostic']
 artifacts=('result.json','source-manifest.json','controller-source.py','rotation_diagnostics.py','colt_preparation.py','shooter_policy.py','original-input-trace.jsonl','rotation-pairs.jsonl','rotation-read-attempts.jsonl','controls-effective.json','collector-config.json','passive-xrecord/config.json','passive-xrecord/record-raw.jsonl','passive-xrecord/controller-emissions.json','passive-xrecord/controller-emission-attempts.json','passive-xrecord/recorder-native-close.json','passive-xrecord/xres-attribution.json','passive-xrecord/recorder-bound.json')
 return dict(status='CLOSED_NOFIRE_PITCH_GAIN_FAIL_UNCHANGED',evidence=str(e),source_root=str(s),result_sha256=RESULT_SHA,source_manifest_sha256=MANIFEST_SHA,artifact_sha256={n:sha(e/n)for n in artifacts},source_sha256={n:sha(s/n)for n in sources},reader_sha256=sha(__file__),archived_sources_equal_frozen=True,errors=r['errors'],all_phase_timings=r['input_phase_timings'],all_actual_emissions=emissions,all_actual_attempts=attempts,emission_wire_bindings=emission_bindings,wire_replay=dict(records=310,bytes=(e/'passive-xrecord/record-raw.jsonl').stat().st_size,wire_derived_exact=True,pending_queries=0,core_unknown=4,adapter_typed_noncursor_xtest=4,unknowns_unchanged=True,audit=audited),xres_replay=attributed,xres_full_metadata=metadata,current_connection_classes=clients,full_wire_timeline=wire,wire_motion_windows=windows,last_negative_pitch_wire=last_window,input_action_counts=dict(envelopes=len(envelopes),inputs=139,actions=139,complete_pairs=139,nonzero=5,zero=134,threads=1),full_input_action_timeline=input_timeline,nonzero_input_actions=nonzero,profiles=[dict(profile=json.loads(k),records=n)for k,n in profiles.items()],trace_final_packet={k:v for k,v in final.items()if k!='records'},original_byte_receipt=envelopes[-1],all_native_physical_pairs=physical,native_rotation_observations=rd['observations'],yaw_calibration=rd['calibration'],pitch_calibration_full=pitch,pitch_summary=pitch_summary,controls_effective=load('controls-effective.json')['sample'],clock_contract=dict(controller='parent monotonic receipts; compared only to native-read interval receipts in same archive',record='Xserver server_time/event_time and per-client sequence; recorder monotonic is callback receipt, not execution',js='collector Date.now entered/compose/left; batch host drain is a delivery bound only',game='independent actual server/client game_tick, each process/life/world verified',no_cross_clock_equation_interpolation_or_direct_js_wire_sequence_tag=True),conclusions=dict(horizontal_requested_action_gains=[-.25,-.25],horizontal_requested_body_gains=rd['calibration']['body_yaw_degrees_per_pixel_raw'],vertical_requested_native_ack_gains=[-.25,-.5],vertical_engine_values=[-3,3,3],vertical_cursor_reads=[12,-12,-12],two_negative_pitch_reads_js_gap_ms=47,negative_pitch_wire_requests=1,negative_pitch_server_query_replies_301=1,negative_pitch_server_warps_to_313=1,negative_pitch_postwarp_replies_313=6,server_query_to_warp_milliseconds=50,warp_connection_current_original_pid_proven=True,warp_to_exact_js_recenter_invocation_proven=False,postwarp_stale_xserver_reply_observed=False,wine_cache_or_queued_recenter_cause_proven=False,raw_pitch_compose_observed=False,pitch_body_rotation='Original viewpoint pitch at both native endpoints; fixed body placement is separate',historical_u_attributed=False,input_once_proven=False,extra_controller_xtest_observed=False,no_fix_gate_gain_tolerance_or_timing_change=True),cleanup=dict(collector=r['collector_cleanup'],recorder=r['passive_xrecord']['child'],native=r['passive_xrecord']['native'],parent_result_restoration=r['restoration'],root_independent_restore_not_repeated_by_this_reader=True),native_started_by_reader=False,tests_started_by_reader=False)


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args();report=read()
 raw=(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
 with os.fdopen(os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb')as out:out.write(raw)
 print(json.dumps(dict(receipt=str(args.output),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),status=report['status'],counts=report['input_action_counts'])))
