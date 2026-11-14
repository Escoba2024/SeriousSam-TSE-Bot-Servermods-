"""Bounded ordered read observations. No process, input or native calls."""
import copy
import json
import math

import a4_canonical_native_groups as groups
import audit_a4_ordered_memory_v3 as audit

MAX_ATTEMPTS=100000
MAX_JOURNAL_BYTES=64*1024*1024
declare=groups.declare
require=groups.require


def clock(value):
    require(type(value)in(int,float)and math.isfinite(value)and value>=0,'invalid monotonic read clock')
    return value


def read_contract(contract):
    expected=groups.checked_contract(contract)
    require(groups.digest(contract)==groups.digest(expected),'typed group contract differs')
    return dict(schema='ordered-readonly-memory-v3',group_contract_sha256=groups.digest(contract),
        server_identity=copy.deepcopy(contract['observer_epoch']['server_identity']),
        observer_epoch=copy.deepcopy(contract['observer_epoch']),serial_scope='global_all_inventory_attempts',
        max_attempts=MAX_ATTEMPTS,max_journal_bytes=MAX_JOURNAL_BYTES,
        atomic_snapshot=False,weapon_function_call_proven=False)


def observation_id(contract,group,serial):
    return dict(server_identity=copy.deepcopy(contract['observer_epoch']['server_identity']),
        observer_epoch=copy.deepcopy(contract['observer_epoch']),group=group,read_serial=serial)


def bind_observation(sample,contract,serial,started,ended,phase='gameplay'):
    require('memory_observation'not in sample,'observation already bound')
    require(type(serial)is int and 1<=serial<=MAX_ATTEMPTS,'read serial bound')
    require(clock(ended)>=clock(started),'read end precedes start')
    require(phase in('paused_smoke','gameplay'),'read phase')
    group=sample['native_group_provenance']['name']
    out=copy.deepcopy(sample)
    out['memory_observation']=dict(schema='ordered-readonly-memory-v3',read_serial=serial,
        monotonic_start=started,monotonic_end=ended,phase=phase,
        id=observation_id(contract,group,serial))
    return out


def bind_sample(sample,group,contract,serial,started,ended,phase='gameplay'):
    return bind_observation(groups.bind_sample(sample,group,contract),contract,serial,started,ended,phase)


class AttemptJournal:
    """At most200000 metadata lines/64MiB, no duplicated inventory payloads."""
    def __init__(self,stream):
        self.stream=stream;self.records=[];self.bytes_written=0;self.pending=None;self.last=0;self.last_end=0
    def write(self,row,flush=False):
        data=json.dumps(row,allow_nan=False,separators=(',',':'))+'\n'
        size=len(data.encode())
        require(self.bytes_written+size<=MAX_JOURNAL_BYTES,'attempt journal byte bound')
        self.stream.write(data);self.bytes_written+=size;self.records.append(row)
        if flush:self.stream.flush()
    def begin(self,serial,group,started,phase):
        require(self.pending is None and type(serial)is int and serial==self.last+1
                and serial<=MAX_ATTEMPTS,'attempt sequence/bound')
        require(clock(started)>=self.last_end,'attempt start moved backwards')
        require(group in('botA_actual','botB_actual','vanilla_plus_overlap'),'attempt group')
        require(phase in('paused_smoke','gameplay'),'attempt phase')
        row=dict(kind='begin',read_serial=serial,group=group,phase=phase,monotonic_start=started)
        self.write(row);self.pending=row;self.last=serial
    def end(self,serial,ended,success,error=None):
        require(self.pending is not None and serial==self.pending['read_serial'],'attempt end without begin')
        require(clock(ended)>=self.pending['monotonic_start'],'attempt end moved backwards')
        require(type(success)is bool,'attempt status')
        row=dict(kind='end',read_serial=serial,monotonic_end=ended,status='ok'if success else'error')
        if not success:
            require(isinstance(error,str)and 0<len(error)<=256,'bounded attempt error')
            row['error']=error
        self.write(row,flush=True);self.last_end=ended;self.pending=None


def check_attempts(records,contract):
    require(isinstance(records,list)and len(records)<=MAX_ATTEMPTS*2,'attempt record bound')
    require(sum(len((json.dumps(r,allow_nan=False,separators=(',',':'))+'\n').encode())for r in records)<=MAX_JOURNAL_BYTES,
            'attempt journal byte bound')
    require(len(records)%2==0,'incomplete attempt journal')
    attempts={};last_end=0
    for index in range(0,len(records),2):
        begin,end=records[index:index+2];serial=index//2+1
        require(set(begin)=={'kind','read_serial','group','phase','monotonic_start'},'attempt begin schema')
        require(set(end)==({'kind','read_serial','monotonic_end','status','error'}if end.get('status')=='error'
                          else{'kind','read_serial','monotonic_end','status'}),'attempt end schema')
        require(begin.get('kind')=='begin'and end.get('kind')=='end','attempt pair order')
        require(type(begin.get('read_serial'))is int and begin['read_serial']==serial
                and type(end.get('read_serial'))is int and end['read_serial']==serial,'attempt serial missing/reversed/repeated')
        require(begin.get('group')in contract['groups']and begin.get('phase')in('paused_smoke','gameplay'),'attempt group/phase')
        require(clock(end.get('monotonic_end'))>=clock(begin.get('monotonic_start'))>=last_end,'attempt time order')
        require(end.get('status')in('ok','error'),'attempt success status')
        if end['status']=='error':require(isinstance(end.get('error'),str)and 0<len(end['error'])<=256,'attempt error bound')
        attempts[serial]=(begin,end);last_end=end['monotonic_end']
    return attempts


def validate_all(samples,registry,mapping,identity,contract,records):
    require(isinstance(samples,list)and len(samples)<=MAX_ATTEMPTS,'sample count bound')
    counts=groups.validate_all(samples,registry,mapping,identity,contract)
    require(groups.digest(registry.get('memory_observation_contract'))==groups.digest(read_contract(contract)),
            'registry read contract')
    attempts=check_attempts(records,contract);seen=set();last_serial=0;last_end=0;last_tick=None
    for sample in samples:
        require(groups.digest(sample['observer_epoch'])==groups.digest(contract['observer_epoch'])
                and groups.digest(sample['process_identity'])==groups.digest(list(identity)),
                'typed sample process/epoch differs')
        require(all(type(p.get('slot'))is int and all(type(p.get(k))is int for k in audit.IDENTITY)
                    for p in sample['players']),'typed sample slot/entity identity differs')
        m=sample.get('memory_observation');require(isinstance(m,dict),'missing observation identity')
        serial=m.get('read_serial');require(type(serial)is int and serial>last_serial,'observation sequence repeated/reversed')
        require(serial in attempts,'observation missing attempt')
        begin,end=attempts[serial];group=sample['native_group_provenance']['name']
        require(end['status']=='ok'and begin['phase']=='gameplay','failed/non-gameplay attempt used as evidence')
        expected=dict(schema='ordered-readonly-memory-v3',read_serial=serial,
            monotonic_start=begin['monotonic_start'],monotonic_end=end['monotonic_end'],phase='gameplay',
            id=observation_id(contract,group,serial))
        require(m==expected and groups.digest(m)==groups.digest(expected)
                and begin['group']==group,'observation identity/time/binding differs')
        require(clock(m['monotonic_end'])>=clock(m['monotonic_start'])>=last_end,'observation read time reversed')
        require(last_tick is None or sample['game_tick']>=last_tick,'session clock reversed')
        seen.add(serial);last_serial=serial;last_end=m['monotonic_end'];last_tick=sample['game_tick']
    required={serial for serial,(begin,end)in attempts.items()if begin['phase']=='gameplay'and end['status']=='ok'}
    require(seen==required,'successful gameplay attempt omitted or duplicated')
    return counts,attempts


def apply(result,logs,mapping,samples,registry,identity,contract,records):
    counts,attempts=validate_all(samples,registry,mapping,identity,contract,records)
    selected=[s for s in samples if s['native_group_provenance']['name']in contract['fixed_sources'].values()]
    numbered=[(s['memory_observation']['read_serial'],s)for s in selected]
    expected={p['slot']:p for p in registry['players']};proof={}
    for role in('botA','botB'):
        require(logs[role].count('[CecilLoad]')==1,'ambiguous source map epoch')
        rows=audit.source_rows(logs[role])
        for local,slot in enumerate(mapping[role]):proof[f'{role}:{local}']=audit.slot_evidence(rows,numbered,local,slot,expected[slot])
    missing=[m for m in result['missing_activity']if not m.endswith(':fire_action_rows')]
    for key,detail in proof.items():
        result['slots'][key]['memory_flag_observations']=detail
        if not detail['native_fire_flag_observations_with_same_life_source_growth']:missing.append(key+':native_bound_fire_flag_observations')
        if not detail['actual_useful_inventory_gains']:missing.append(key+':native_bound_useful_pickup_gains')
    result['missing_activity']=missing;result['memory_flag_observer_version']=3
    result['memory_observation_epoch']=copy.deepcopy(registry['native_fire_epoch'])
    result['memory_observation']=dict(raw_samples=len(samples),canonical_samples=len(selected),raw_group_samples=counts,
        fixed_sources=copy.deepcopy(contract['fixed_sources']),attempts=len(attempts),
        failed_attempts=sum(end['status']=='error'for begin,end in attempts.values()),
        atomic_snapshot=False,weapon_function_call_proven=False,
        contract_sha256=groups.digest(read_contract(contract)),journal_max_bytes=MAX_JOURNAL_BYTES,
        claim='native flags in two-equal-read intervals plus same-life source growth; not weapon-function calls')
    return result
