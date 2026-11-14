"""One immutable three-role capture, then one real Original admission.

Importing performs no runtime IO. The physical capture and normal cleanup are
the existing OwnedSyncCapture implementation; only explicit staged bindings and
prospective storage-observation epochs differ. The Retail decoder is unchanged.
"""
import copy
import hashlib
import io
from pathlib import Path
import struct
import time

import owned_sync_capture as base
from owned_sync_capture import exclusive_json,need,observe_roles
from ownns_latejoin_preflight import PROTOCOL,THREE_ROLES,validate_three_binding

RUNTIME_REVIEWED=False
ADMISSION_SECONDS=base.MAX_SECONDS-600-10


def observe_three_roles(registry):
 need(set(registry)==set(THREE_ROLES),'exact private prejoin registry')
 rows=base._observe_roles(registry,THREE_ROLES)
 validate_three_binding(rows)
 return rows


def complete_boundary(raw):
 need(len(raw)>=24 and len(raw)<base.MAX_BYTES,'bounded classic PCAP required')
 magic,major,minor,zone,accuracy,snaplen,network=struct.unpack('<IHHIIII',raw[:24])
 need((magic,major,minor,snaplen,network)==(0xa1b2c3d4,2,4,262144,1),'exact PCAP format')
 offset=24;records=0
 while offset+16<=len(raw):
  sec,micro,size,original=struct.unpack_from('<IIII',raw,offset)
  need(micro<1000000 and 14<=size<=snaplen and size==original,'invalid PCAP record')
  if offset+16+size>len(raw):break
  offset+=16+size;records+=1
  need(records<base.MAX_PACKETS,'packet cap reached')
 return dict(offset=offset,observed_bytes=len(raw),pending_bytes=len(raw)-offset)


def phase_bytes(raw,start,end):
 need(type(start)is int and type(end)is int and 24<=start<=end<=len(raw),'fixed epoch offsets')
 need(complete_boundary(raw[:start])['offset']==start and complete_boundary(raw[:end])['offset']==end,'epoch must end on complete records')
 return raw[:24]+raw[start:end]


class OwnedLatejoinCapture(base.OwnedSyncCapture):
 def __init__(self,evidence,registry):
  need(set(registry)==set(THREE_ROLES),'only three real roles before Original launch')
  super().__init__(evidence,copy.deepcopy(registry))
  self.stage='THREE_ROLES';self.initial_binding=None;self.original_unit=None
  self.post_started=None;self.post_start=None;self.post_end=None
  self.receipt.update(scope=PROTOCOL,a4_accepted=False,latejoin_stage=self.stage,storage_epoch_not_atomic_engine_time=True)
 def observe_binding(self):return observe_roles(self.registry)if self.stage=='FOUR_ROLES'else observe_three_roles(self.registry)
 def binding_ports(self,rows):return base.validate_role_ports(rows)if self.stage=='FOUR_ROLES'else validate_three_binding(rows)
 def setup_helper(self):return Path(__file__).resolve().parent/'owned_latejoin_capture_exec.py'
 def setup_config(self):
  source=Path(__file__).resolve().parent
  files=('owned_latejoin_capture_exec.py','owned_latejoin_capture.py','ownns_latejoin_preflight.py','owned_sync_capture.py','stability_hard_rules.py')
  return dict(protocol=PROTOCOL,registry=self.registry,binding=self.before,owner_path=str(self.owner_path),source_pins={str(source/n):hashlib.sha256((source/n).read_bytes()).hexdigest()for n in files})
 def start(self):
  need(RUNTIME_REVIEWED,'disabled latejoin capture')
  super().start();self.initial_binding=copy.deepcopy(self.before)
  self.receipt['immutable_prejoin_binding']=self.initial_binding;self.save()
 def admission_remaining(self):
  need(self.started is not None,'capture not started')
  remaining=self.started+ADMISSION_SECONDS-time.monotonic()
  need(remaining>0,'Original admission exceeded30s budget')
  return remaining
 def begin_admission(self,unit):
  need(self.stage=='THREE_ROLES','exactly one Original launch admission')
  need(type(unit)is str and unit.endswith('.service')and unit not in {s['unit']for s in self.registry.values()},'new own Original unit')
  self.admission_remaining();self.guard()
  self.original_unit=unit;self.stage='ADMITTING'
  self.receipt.update(latejoin_stage=self.stage,original_launch_gate_monotonic=time.monotonic(),capture_ready_before_original_launch=True)
  self.save()
 def admit(self,spec):
  need(self.stage=='ADMITTING','one Original admission after capture readiness')
  self.admission_remaining();self.guard()
  need(spec['unit']==self.original_unit,'Original unit differs from predeclared launch')
  registry=copy.deepcopy(self.registry);registry['vanilla']=copy.deepcopy(spec)
  after=observe_roles(registry);base.validate_role_ports(after)
  need({r:after[r]for r in THREE_ROLES}==self.before,'old role binding changed during admission')
  need(after['vanilla']['identity']==spec['identity']and after['vanilla']['unit']==spec['unit'],'Original observed identity mismatch')
  self.admission_remaining()
  receipt=dict(protocol=PROTOCOL,old_binding=copy.deepcopy(self.before),new_role=after['vanilla'],admitted_monotonic=time.monotonic())
  exclusive_json(self.evidence/'owned-sync-admission.json',receipt)
  self.registry=registry;self.before=after;self.ports=base.validate_role_ports(after);self.stage='FOUR_ROLES'
  self.receipt.update(latejoin_stage=self.stage,admission=receipt,role_ports=self.ports);self.save()
 def mark_postjoin_start(self):
  need(self.stage=='FOUR_ROLES'and self.post_start is None,'admitted fresh postjoin epoch required')
  self.admission_remaining();self.guard()
  raw=self.pcap.read_bytes();boundary=complete_boundary(raw)
  self.post_start=boundary['offset'];self.post_started=time.monotonic()
  need(self.post_started<self.started+ADMISSION_SECONDS,'postjoin epoch exceeds admission budget')
  self.receipt['postjoin_start']=dict(**boundary,monotonic=self.post_started,chosen_before_decoder=True);self.save()
 def gameplay_complete(self):
  need(self.stage=='FOUR_ROLES'and self.post_started is not None,'Original never admitted')
  need(time.monotonic()-self.post_started>=600,'full600s postjoin epoch required')
  self.guard();boundary=complete_boundary(self.pcap.read_bytes());self.post_end=boundary['offset']
  self.receipt['postjoin_end']=dict(**boundary,monotonic=time.monotonic(),chosen_before_decoder=True)
  super().gameplay_complete()
 def run_audits(self):
  from analyze_retail_sync_pcap import analyze
  raw=self.pcap.read_bytes();complete_boundary(raw)
  if self.stage!='FOUR_ROLES':
   self.receipt['pair_audits']={'A_B':analyze(io.BytesIO(raw),[self.ports['botA'],self.ports['botB']],27850)}
   self.receipt['missing_pairs']=['A_Original','B_Original']
   raise ValueError('Original never admitted; three-role evidence retained')
  self.receipt['pair_audits']=base.audit_pairs(self.pcap,self.ports,analyze)
  need(not any(v['differing_pairs']or v['duplicate_conflicts']or v['fragmented_packets']for v in self.receipt['pair_audits'].values()),'full capture differs/conflicts/fragments; join observations never discarded')
  need(self.post_start is not None and self.post_end is not None,'missing prospectively fixed600s epoch')
  phase=phase_bytes(raw,self.post_start,self.post_end)
  self.receipt['postjoin_view_sha256']=hashlib.sha256(phase).hexdigest()
  self.receipt['postjoin_pair_audits']={name:analyze(io.BytesIO(phase),[self.ports[a],self.ports[b]],27850)for name,a,b in [('A_B','botA','botB'),('A_Original','botA','vanilla'),('B_Original','botB','vanilla')]}
  need(all(v['paired_checks']>0 for v in self.receipt['postjoin_pair_audits'].values()),'missing postjoin pair observations')
 def comparison_complete(self):
  reports=self.receipt.get('postjoin_pair_audits',{})
  return set(reports)=={'A_B','A_Original','B_Original'}and all(v['status']=='MATCHING_SAMPLED_SYNCCHECKS_ONLY'for v in reports.values())
