"""Pure single-map binding around the already reviewed native-fire V2 policy."""
import copy

def need(value,message):
 if not value:raise ValueError('Hard map: '+message)

def options(map_key,duration,diag,catalog):
 need(map_key in catalog,'existing allowlisted map required')
 need(type(duration)in(int,float)and duration==600,'fixed600s functional window')
 need(type(diag)is int and diag==0,'fixed diagnostics0')

def registry(original,rows,mapping,server_identity):
 """Use existing V2 registry builder; independently validate its input binding."""
 need(set(mapping)=={'botA','botB','vanilla'},'physical roles')
 need(all(type(mapping[r])is list and len(mapping[r])==n and all(type(s)is int for s in mapping[r])
          for r,n in [('botA',4),('botB',4),('vanilla',1)]),'mapping dimensions')
 slots=mapping['botA']+mapping['botB']+mapping['vanilla']
 need(len(set(slots))==9 and set(slots)==set(range(9)),'exclusive nine slots')
 need(len(rows)==9 and {r.get('slot')for r in rows}==set(range(9))and
      all(r.get('present')is True for r in rows),'actual native nine-player roster')
 for key in ('entity_id','entity_pointer'):
  need(all(type(r.get(key))is int and r[key]>=1 for r in rows)and
       len({r[key]for r in rows})==9,'unique native '+key)
 need(len({r.get('world_pointer')for r in rows})==1 and
      type(rows[0].get('world_pointer'))is int and rows[0]['world_pointer']>=0x10000,'same current world')
 need(len(server_identity)==2 and all(type(i)is int and i>0 for i in server_identity),'server PID/start')
 out=original(0,rows)
 need(out.get('phase')==0 and out.get('players')==rows,'original registry return changed')
 out['actual_slot_mapping']=copy.deepcopy(mapping)
 out['native_fire_epoch']=dict(phase=0,server_identity=list(server_identity),
                               log_offsets=dict(server=0,botA=0,botB=0))
 return out
