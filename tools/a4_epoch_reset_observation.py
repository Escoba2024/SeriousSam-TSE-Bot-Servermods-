"""Pure per-reset bridge to the reviewed ordered-memory observer; no native access."""
import copy
import time
import a4_reset_ordered_memory_v3 as v3


def require(condition, message):
 if not condition:raise ValueError(message)


def reset_receipt(registry, contract):
 """Cross-bind the existing real8→9 confirmation, never infer resets from pointers."""
 epoch=contract['observer_epoch'];phase=epoch['phase']
 ids=registry.get('persistent_identities')
 require(isinstance(ids,dict)and set(ids)=={'server','botA','botB'},'persistent three-role epoch identities')
 require(all(isinstance(v,list)and len(v)==2 and all(type(n)is int and n>0 for n in v)for v in ids.values())
         and len({v[0]for v in ids.values()})==3,'positive distinct persistent epoch identities')
 require(ids['server']==epoch['server_identity'],'registry server epoch differs')
 begins=registry.get('round_begin_order')
 require(isinstance(begins,list)and all(type(n)is int for n in begins)
         and begins==list(range(1,phase+2)),'actual registry begin order differs')
 if phase==0:
  require(all(v==0 for v in epoch['log_offsets'].values()),'initial source offsets must be zero')
  return dict(phase=0,persistent_identities=copy.deepcopy(ids),observer_epoch=copy.deepcopy(epoch),
              actual_begin_order=copy.deepcopy(begins),first_simulation_state_proven=False)
 r=registry.get('reset_epoch_receipt');require(isinstance(r,dict),'missing actual early reset receipt')
 require(r.get('state')=='REGISTRY_CONFIRMED'and r.get('registry_confirmed')is True,'early8→late9 not confirmed')
 require(type(r.get('phase'))is int and r['phase']==phase and r.get('epoch')==epoch
         and r.get('identities')==ids,'early reset process/phase epoch differs')
 mapping=contract['actual_slot_mapping']
 require(r.get('mapping')==mapping and r.get('begin_order')==list(range(1,phase+2)),
         'actual reset mapping/begin order differs')
 for role in ('server','botA','botB'):
  old=r.get('scan_offsets',{}).get(role);new=r.get('log_offsets',{}).get(role)
  require(type(old)is int and type(new)is int and 0<=old<=new and new==epoch['log_offsets'][role],
          'reset source offset bounds differ')
 anchor=r.get('anchor_server',{});tick=anchor.get('game_tick');prior=r.get('prior_end_tick')
 require(type(tick)in(int,float)and type(prior)in(int,float)
         and 0<=tick<prior and prior>=120,'actual reset native clock anchor missing')
 expected={p['slot']:p for p in registry['players']};slots=set(mapping['botA']+mapping['botB'])
 bindings=r.get('bindings',{});entities=r.get('entity_ids',{})
 require(set(bindings)=={str(s)for s in slots},'incomplete early eight bindings')
 anchors=anchor.get('players',[])
 require(len(anchors)==8 and {p['slot']for p in anchors}==slots,'anchor is not actual eight-bot roster')
 for p in anchors:
  slot=p['slot'];row=expected[slot]
  require(p['entity_pointer']==row['entity_pointer'],'early server pointer differs')
  require(bindings[str(slot)]==[row[k]for k in ('entity_id','entity_pointer','world_pointer')]
          and entities.get(slot,entities.get(str(slot)))==row['entity_id'],'early/late entity/world differs')
 require(type(r.get('accepted_samples'))is int and r['accepted_samples']>=2,'missing accepted early bot reads')
 return dict(phase=phase,persistent_identities=copy.deepcopy(ids),observer_epoch=copy.deepcopy(epoch),
             actual_begin_order=list(r['begin_order']),prior_end_tick=prior,anchor_tick=tick,
             source_scan_offsets=copy.deepcopy(r['scan_offsets']),confirmed_early_eight_bindings=copy.deepcopy(bindings),
             first_simulation_state_proven=False)


class PhaseReads:
 def __init__(self,phase,mapping,server_identity,offsets,stream,clock=time.perf_counter):
  self.contract=v3.groups.declare(mapping,server_identity,offsets,phase)
  self.journal=v3.AttemptJournal(stream);self.clock=clock;self.registry=None;self.finished=False
 def sample(self,reader,slots,group,phase='gameplay'):
  require(not self.finished,'read after finalized phase')
  require(group in self.contract['groups']and list(slots)==self.contract['groups'][group],'actual epoch group slots differ')
  serial=self.journal.last+1;began=self.clock();self.journal.begin(serial,group,began,phase)
  try:sample=reader(slots)
  except BaseException as error:
   self.journal.end(serial,self.clock(),False,repr(error)[:256]);raise
  ended=self.clock();self.journal.end(serial,ended,True)
  return v3.bind_sample(sample,group,self.contract,serial,began,ended,phase)
 def bind_registry(self,registry):
  require(self.registry is None,'registry already bound')
  require(type(registry.get('phase'))is int and registry['phase']==self.contract['observer_epoch']['phase']
          and registry.get('actual_slot_mapping')==self.contract['actual_slot_mapping'],
          'registry phase/physical mapping differs')
  registry.update(native_fire_epoch=copy.deepcopy(self.contract['observer_epoch']),
                  native_group_contract=copy.deepcopy(self.contract),
                  memory_observation_contract=v3.read_contract(self.contract))
  registry['reset_observation_proof']=reset_receipt(registry,self.contract)
  self.registry=copy.deepcopy(registry)
 def apply(self,result,logs,mapping,samples,registry,identity):
  require(not self.finished and self.registry is not None and registry==self.registry,'missing/changed epoch registry')
  result=v3.apply(result,logs,mapping,samples,registry,identity,self.contract,self.journal.records)
  result['reset_observation_proof']=copy.deepcopy(registry['reset_observation_proof'])
  result.update(qualified=False,functional_pass=False,first_simulation_state_proven=False)
  self.finished=True
  return result


def validate_sequence(results,persistent):
 require(len(results)==3,'three completed reset phases required')
 previous=None
 for phase,result in enumerate(results):
  proof=result.get('reset_observation_proof',{});epoch=proof.get('observer_epoch',{})
  require(type(result.get('phase'))is int and result['phase']==phase and proof.get('phase')==phase,
          'phase sequence missing/repeated/reversed')
  require(proof.get('persistent_identities')==persistent and epoch.get('server_identity')==persistent['server'],
          'persistent reset process changed')
  require(proof.get('actual_begin_order')==list(range(1,phase+2)),'actual round begin sequence differs')
  require(len(result.get('slots',{}))==8,'eight bot slotphases required')
  offsets=epoch.get('log_offsets',{})
  require(set(offsets)=={'server','botA','botB'},'three source offsets required')
  if previous is not None:
   require(all(offsets[r]>previous[r]for r in offsets),'source epoch did not advance')
  previous=offsets
 return dict(completed_phases=3,bot_slotphases=24,actual_resets=2,
             first_simulation_state_proven=False,qualified=False,functional_pass=False)
