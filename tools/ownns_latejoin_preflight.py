"""Private OwnNS eight-bot evidence policy. Importing performs no IO.

This is deliberately not an external Vanilla preflight and has no canStart API.
The owning controller gathers fresh guarded observations under its actual flock.
"""
import math
import re
from stability_hard_rules import validate_session

PROTOCOL='PRIVATE_OWNNS_018_EIGHT_THEN_ORIGINAL_SLOT8_V1'
THREE_ROLES=('server','botA','botB')
CANDIDATE='6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a'
FRESH_SECONDS=1. # Existing host cadence, a separate prestart expiry, not a gameplay gap tolerance.
ORIGINALS={
 'SeriousSam.exe':'9f8f9a0b8fd718616036ed2c3584904e2dfd58e49515bf4c8ecc45175d02cc53',
 'GameMP.dll':'1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208',
 'Engine.dll':'b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f',
 'EntitiesMP.dll':'7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350'}


def require(condition,message):
 if not condition:raise ValueError('OwnNS latejoin: '+message)


def finite(value):
 return type(value)in(int,float)and math.isfinite(value)


def validate_three_binding(rows):
 require(set(rows)==set(THREE_ROLES),'exact three prejoin roles')
 for role,row in rows.items():
  require(type(row['identity'])is list and len(row['identity'])==2 and all(type(x)is int and x>0 for x in row['identity']),'PID/start bounds')
  require(type(row['namespace'])is int and row['namespace']>0,'namespace bounds')
  require(type(row['unit'])is str and row['unit'].endswith('.service'),'own unit')
 require(len({r['identity'][0]for r in rows.values()})==3,'duplicate role PID')
 require(len({r['unit']for r in rows.values()})==3,'duplicate role unit')
 require(len({r['namespace']for r in rows.values()})==1,'role namespace mismatch')
 require(sorted(p for p,i in rows['server']['ports'])==[27850,27851],'exact server ports')
 for role in ('botA','botB'):require(len(rows[role]['ports'])==1,'one owned client socket')
 pairs=[p for row in rows.values()for p in row['ports']]
 require(all(len(pair)==2 and all(type(x)is int for x in pair)and 1<=pair[0]<=65535 and pair[1]>0 for pair in pairs),'socket identity bounds')
 require(len({p for p,i in pairs})==len(pairs)and len({i for p,i in pairs})==len(pairs),'shared socket ownership')
 return {role:rows[role]['ports'][0][0]for role in ('botA','botB')}


def validate_query(query,names,map_name,count=8):
 expected=dict(gamename='serioussamse',gamever='1.07',hostport='27850',numplayers=str(count),maxplayers='9',dedicatedserver='yes',activemod='',difficulty='Hard',mapname=map_name)
 require(all(query.get(k)==v for k,v in expected.items()),'query map/version/Hard/population/port differs')
 players={k:v for k,v in query.items()if re.fullmatch(r'player_\d+',k)}
 require(set(players)=={'player_'+str(i)for i in range(count)},'exact query player rows')
 require(len(names)==count and len(set(players.values()))==count and set(players.values())==set(names),'private roster differs')
 return players


def validate_frames(frames,bindings,slots,window):
 roles=tuple(bindings)
 require(len(frames)==2,'two current native observations required')
 for frame in frames:
  require(set(frame)==set(roles),'native role set')
  for role,sample in frame.items():
   identity=bindings[role]['identity']
   require(sample['process_identity_before']==identity==sample['process_identity_after'],'frame PID/start differs from role binding')
   require(sample['hashes']=={'Engine.dll':ORIGINALS['Engine.dll'],'EntitiesMP.dll':ORIGINALS['EntitiesMP.dll'],'GameMP.dll':CANDIDATE if role in('botA','botB')else ORIGINALS['GameMP.dll']},'frame loaded module hashes differ')
   a,b=sample['read_interval'];require(finite(a)and finite(b)and window[0]<=a<=b<=window[1],'frame outside current observation window')
   validate_session(sample)
   require(finite(sample['game_tick']),'finite native clock')
   actual=[p['slot']for p in sample['players']]
   require(all(type(s)is int for s in actual)and len(actual)==len(slots)and set(actual)==set(slots),'exact native global slots')
   require(all(type(p['entity_pointer'])is int and p['entity_pointer']>0x10000 for p in sample['players']),'native entity pointer')
   pairs=[[p['slot'],p['entity_pointer']]for p in sample['players']]
   require(sample['slot_binding_before']==pairs==sample['slot_binding_after'],'native slot/entity changed during frame')
 for role in roles:require(frames[1][role]['game_tick']>frames[0][role]['game_tick'],'native game did not advance')


def validate_prestart(evidence,*,expected_names,now):
 require(evidence['protocol']==PROTOCOL,'private protocol only')
 require(evidence['lock_held']is True and evidence['vanilla_quiescent']is True,'exclusive lock/vanilla quiescence required')
 start,end=evidence['window'];require(finite(start)and finite(end)and start<=end,'observation window')
 deadline=evidence['deadline'];require(finite(now)and finite(deadline)and end<=now<deadline<=end+FRESH_SECONDS,'stale or future private prestart check')
 before=evidence['binding_before'];validate_three_binding(before)
 require(before==evidence['binding_after'],'prejoin role rebaseline forbidden')
 require(type(evidence['host_namespace'])is int and before['server']['namespace']!=evidence['host_namespace'],'host namespace forbidden')
 require(evidence['mapping']=={'botA':[0,1,2,3],'botB':[4,5,6,7]},'exact local-to-global mapping')
 validate_query(evidence['query'],expected_names,evidence['map_name'])
 validate_frames(evidence['frames'],before,range(8),evidence['window'])
 require(set(evidence['pauses'])==set(THREE_ROLES)and all(type(v)is int and v==0 for v in evidence['pauses'].values()),'native pause must be zero')
 require(evidence['original_hashes']==ORIGINALS,'four unchanged Original files')
 r=evidence['resources'];cpu=r['cpu_busy_percent']
 require(finite(cpu)and 0<=cpu<=75,'measured host CPU delta required within75%')
 require(type(r['mem_available_bytes'])is int and r['mem_available_bytes']>=1610612736,'available memory below1.5GiB')
 require(type(r['disk_free_bytes'])is int and r['disk_free_bytes']>=8589934592,'free disk below8GiB')
 return dict(protocol=PROTOCOL,status='PRIVATE_EIGHT_READY_AT_CHECK_TIME',qualified=False,functional_pass=False,a4_accepted=False,atomic_snapshot_proven=False,global_slots=list(range(8)),window=[start,end])
