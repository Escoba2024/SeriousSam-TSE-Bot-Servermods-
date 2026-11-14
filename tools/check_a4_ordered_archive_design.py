"""CLOSED archive design model only: retrospective IDs and synthetic times.

Old archives lack real per-attempt serial/start/end records. This tool cannot
qualify that missing provenance and never requalifies their historical FAIL.
"""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import a4_ordered_memory_v3 as v3


def sha(path):
 with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def check(root):
 root=Path(root);names=('inventory.jsonl','registry.json','result.json','botA-closed.log','botB-closed.log')
 before={name:sha(root/name)for name in names}
 registry=json.loads((root/'registry.json').read_text());mapping=registry['actual_slot_mapping'];epoch=registry['native_fire_epoch'];identity=epoch['server_identity']
 contract=v3.declare(mapping,identity,epoch['log_offsets'])
 if epoch!=contract['observer_epoch']:raise ValueError('historical epoch differs')
 if registry.get('native_group_contract',contract)!=contract:raise ValueError('historical group contract differs')
 registry['native_group_contract']=contract;registry['memory_observation_contract']=v3.read_contract(contract)
 samples=[];paused=0;journal=v3.AttemptJournal(io.StringIO())
 with(root/'inventory.jsonl').open()as stream:
  for serial,text in enumerate(stream,1):
   e=json.loads(text);s=e['snapshot'];group=e['group'];phase='gameplay'if'elapsed'in e else'paused_smoke'
   if phase=='paused_smoke'and e.get('phase')!='paused_smoke':raise ValueError('unknown archived phase')
   start=serial*.01;end=start+.001
   journal.begin(serial,group,start,phase);journal.end(serial,end,True)
   # These are explicit model intervals, NEVER claimed as historical timestamps.
   if s.get('observer_epoch')not in(None,epoch):raise ValueError('historical observation epoch differs')
   if 'native_group_provenance'in s:
    bound=v3.bind_observation(s,contract,serial,start,end,phase)
   else:
    s=copy.deepcopy(s);s.pop('observer_epoch',None)
    bound=v3.bind_sample(s,group,contract,serial,start,end,phase)
   if phase=='gameplay':samples.append(bound)
   else:paused+=1
 result=dict(missing_activity=[],slots={f'{r}:{i}':dict(fire_action_rows=0)for r in('botA','botB')for i in range(4)},qualified=False,functional_pass=False)
 logs={r:(root/(r+'-closed.log')).read_text(errors='replace')for r in('botA','botB')}
 proof=v3.apply(result,logs,mapping,samples,registry,identity,contract,journal.records)
 if {name:sha(root/name)for name in names}!=before:raise ValueError('closed sources changed')
 return dict(scope='OFFLINE_DESIGN_MODEL_NOT_NATIVE_QUALIFICATION',historical_status='FAIL',qualified=False,functional_pass=False,
   retrospective_serials_and_synthetic_intervals=True,real_historical_attempt_provenance_unavailable=True,
   other_legacy_gates_requalified=False,source_hashes=before,source_files_unchanged=True,
   model_source_sha256={n:sha(Path(__file__).with_name(n))for n in('a4_ordered_memory_v3.py','audit_a4_ordered_memory_v3.py','check_a4_ordered_archive_design.py')},
   paused_samples_not_gameplay_evidence=paused,observation=proof['memory_observation'],missing_flag_evidence=proof['missing_activity'],
   slots={k:{field:d['memory_flag_observations'][field]for field in('native_fire_flag_observations_with_same_life_source_growth','actual_useful_inventory_gains')}for k,d in proof['slots'].items()})


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--closed-window',type=Path,required=True);p.add_argument('--new-output',type=Path,required=True);args=p.parse_args()
 out=check(args.closed_window)
 with args.new_output.open('x')as stream:stream.write(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2))
