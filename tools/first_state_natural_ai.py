"""Exact NaturalAI030 role policy and passive Source ownership. No native ABI calls.

This new condition is disabled by the parent Runner gate. Positive Source facts
identify a client role, never a first-state/damage/complete ABI qualification.
"""
import hashlib
import re
import struct
import json
import os
from pathlib import Path

ORIGINAL_GAME='1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'
BOT_GAME='bf70585708cb5cc0d0d62416b641c1df758c90b8cdbd062a04dccecca2a29412'
ENGINE='b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f'
ENTITIES='7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350'
ACTIVE_CONFIG_SHA='9bd131be6123dd8bde705be92fcd866f2aae431a995ba0328bcfb0110e4f6053'
NAV_SHA='70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6'
DLL_SOURCE=Path('/srv/tse-milestone-a-build-030-20261115/Sources/Game/GameMP.dll')
NAV_SOURCE=Path('/srv/tse-cecil-full-private-assets-20261107/RedStation_5AF1A276.nav')
TARGETS=('botA/Bin/GameMP.dll','botA/Scripts/CecilObserver.ini',
         'botA/Scripts/Cecil/RedStation_5AF1A276.nav','botA/Scripts/Cecil/maps.txt',
         'botA/Scripts/Cecil/settings.txt','botA/SeriousSam.log')
MAPS_SHA='a98c865c4b4aee3adc8a10b79dfd3bcc011d20df1a339921271d243921ee9c78'
SETTINGS_SHA='997ba93194bb1ae76632819184effdbb5e894636ccf57940beca4b09ba6b287a'


def require(ok,message):
    if not ok:raise ValueError('NaturalAI030: '+message)


def game_sha(role):
    require(role in ('server','vanilla','botA'),'exact three roles')
    return BOT_GAME if role=='botA'else ORIGINAL_GAME


def exact_pins(records,pins):
    require(set(records)==set(pins)=={'server','vanilla','botA'},'exact three owned OS roles')
    identities=[]
    for role in records:
        pair=records[role]['identity']
        require(type(pair)in(list,tuple)and len(pair)==2 and all(type(x)is int and x>1 for x in pair),'PID/start pin')
        identities.append(tuple(pair))
        require(set(pins[role])=={'Engine.dll','EntitiesMP.dll','GameMP.dll'},'exact role modules')
        expected={'Engine.dll':ENGINE,'EntitiesMP.dll':ENTITIES,'GameMP.dll':game_sha(role)}
        require({n:p['sha256']for n,p in pins[role].items()}==expected,'strict per-role module hashes')
    require(len(set(identities))==3,'distinct owned processes')


def validate_gms(data):
    require(type(data)is bytes and len(data)>=53 and data[:8]==b'GAMEV012'and data[12:25]==b'TCP/IP Client','actual client GameV012')
    require(struct.unpack_from('<4i',data,33)==(0,-1,-1,-1)and struct.unpack_from('<i',data,49)==(0,),'exact local0 only')


def read_bytes(path,limit=1024*1024):
    path=Path(path).resolve(strict=True)
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as stream:
        require(os.fstat(stream.fileno()).st_size<=limit,'bounded source file')
        data=stream.read(limit+1)
    require(len(data)<=limit,'bounded source file grew')
    return data


def private_json(path,value):
    data=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    require(len(data)<=1536*1024,'bounded private custody receipt')
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())


def snapshot_targets(transaction):
    require(not transaction.sealed,'snapshot before seal only')
    for relative in TARGETS:
        path=transaction.path(relative)
        require(path.parent.is_dir(),'existing target parent required; no new directories')
        transaction.snapshot_file(relative)


def stage_candidate(transaction,root,draft,evidence):
    root=Path(root).resolve(strict=True);draft=Path(draft).resolve(strict=True)
    require(transaction.sealed and transaction.root==root,'same sealed transaction required')
    require(all(name in transaction.records for name in TARGETS),'every target snapshotted')
    payloads=(read_bytes(DLL_SOURCE),read_bytes(draft/'natural-ai/active.ini'),read_bytes(NAV_SOURCE),
              read_bytes(draft/'natural-ai/maps.txt'),read_bytes(draft/'natural-ai/settings.txt'),b'')
    hashes=(BOT_GAME,ACTIVE_CONFIG_SHA,NAV_SHA,MAPS_SHA,SETTINGS_SHA,hashlib.sha256(b'').hexdigest())
    require(all(hashlib.sha256(data).hexdigest()==expected for data,expected in zip(payloads,hashes)),'exact030 active config/Nav/settings/DLL closure')
    paths=[transaction.path(name)for name in TARGETS]
    require(all(p.parent.is_dir()for p in paths),'existing target parent required')
    log=transaction.records[TARGETS[-1]]
    result={'schema':'NATURAL_AI030_STAGING_V1','qualified':False,
            'staged':{'dll_sha256':BOT_GAME,'config_sha256':ACTIVE_CONFIG_SHA,'nav_sha256':NAV_SHA},
            'file_hashes':dict(zip(TARGETS,hashes)),
            'log_epoch':{'cleared_before_launch':True,'empty_sha256':hashes[-1],
                         'original_sha256':log['sha256']if log['existed']else hashes[-1]}}
    # All payloads and target paths are checked before the first write. Any
    # write/receipt failure still enters the inherited transaction finally.
    for path,data in zip(paths,payloads):
        path.write_bytes(data);os.chown(path,65534,65534)
        require(hashlib.sha256(read_bytes(path)).hexdigest()==hashlib.sha256(data).hexdigest(),'staged readback')
    private_json(Path(evidence)/'natural-ai-staging.json',result)
    return result


def capture_ownership(root,evidence,frame,records,pins,mapping,entity_ids,staging):
    root=Path(root).resolve(strict=True)
    require(staging['schema']=='NATURAL_AI030_STAGING_V1','actual staging receipt')
    actual={key:hashlib.sha256(read_bytes(root/name)).hexdigest()for key,name in
            (('dll_sha256',TARGETS[0]),('config_sha256',TARGETS[1]),('nav_sha256',TARGETS[2]))}
    require(actual==staging['staged'],'active staged files changed')
    for relative,expected in ((TARGETS[3],MAPS_SHA),(TARGETS[4],SETTINGS_SHA)):
        require(hashlib.sha256(read_bytes(root/relative)).hexdigest()==expected,'active maps/settings changed')
    log=read_bytes(root/TARGETS[-1],65536);gms=read_bytes(root/'botA/Data/SeriousSam.gms',4096)
    require(set(entity_ids)==set(mapping.values())and all(type(k)is int for k in entity_ids),'actual discovered entity slot keys')
    proof={'schema':'NATURAL_AI030_SOURCE_OWNERSHIP_V1','bot_identity':list(records['botA']['identity']),
           'server_identity':list(records['server']['identity']),'mapping':dict(mapping),'entity_ids':{str(k):v for k,v in entity_ids.items()},
           'gms_hex':gms.hex(),'log_epoch':dict(staging['log_epoch']),'staged':actual,
           'log_text':log.decode('latin1').replace('\r\n','\n'),'raw_log_sha256':hashlib.sha256(log).hexdigest()}
    # No retry or ABI fallback. Source guard failure still preserves the same
    # bounded evidence privately; labels are assigned only by the pure validator.
    candidate=dict(frame,natural_ai_ownership=proof)
    try:roles_from_receipt(candidate,records,pins)
    finally:private_json(Path(evidence)/'natural-ai-ownership.json',proof)
    return proof


def roles_from_receipt(frame,records,pins):
    """Revalidate raw Source/GMS evidence before assigning any bot registry label."""
    try:
        exact_pins(records,pins)
        require(set(frame['roles'])=={'vanilla','botA'},'exact two server actors')
        q=frame['natural_ai_ownership']
        require(q['schema']=='NATURAL_AI030_SOURCE_OWNERSHIP_V1','ownership schema')
        require(q['bot_identity']==list(records['botA']['identity'])and q['server_identity']==list(records['server']['identity']),'receipt process identity')
        require(frame['server_process_identity']==list(records['server']['identity']),'frame server identity')
        mapping=q['mapping'];raw_ids=q['entity_ids']
        require(set(mapping)=={'vanilla','botA'}and len(set(mapping.values()))==2 and all(type(x)is int and 0<=x<16 for x in mapping.values()),'exclusive actual join mapping')
        require(set(raw_ids)=={str(k)for k in mapping.values()},'canonical JSON entity slot keys')
        ids={int(k):v for k,v in raw_ids.items()}
        require(set(ids)==set(mapping.values())and all(type(x)is int and x>0 for x in ids.values()),'actual two entity pins')
        for role,slot in mapping.items():
            row=frame['roles'][role]
            require(type(row['entity_id'])is int and row['entity_id']==ids[slot],'server actor ID')
            require(all(type(row[k])is int and 0x10000<=row[k]<=0xffffffff and row[k]%4==0 for k in ('entity_pointer','world_pointer')),'server actor pointers')
        require(len({r['entity_id']for r in frame['roles'].values()})==2 and len({r['entity_pointer']for r in frame['roles'].values()})==2,'distinct actual actors')
        require(len({r['world_pointer']for r in frame['roles'].values()})==1,'same server world')
        validate_gms(bytes.fromhex(q['gms_hex']))
        epoch=q['log_epoch'];require(epoch['cleared_before_launch']is True and epoch['empty_sha256']==hashlib.sha256(b'').hexdigest(),'fresh transacted logepoch')
        require(re.fullmatch('[0-9a-f]{64}',epoch['original_sha256'])is not None,'original log backup pin')
        require(q['staged']=={'dll_sha256':BOT_GAME,'config_sha256':ACTIVE_CONFIG_SHA,'nav_sha256':NAV_SHA},'actual staged condition')
        text=q['log_text'];require(type(text)is str and 0<len(text.encode())<=1024*1024,'bounded actual Source log')
        drivers=re.findall(r'^\[BotDriver\] local player (\d+) \(player index (\d+)\) is now bot-driven: [^\r\n]*$',text,re.M)
        require(drivers==[('0',str(mapping['botA']))],'actual local0 source/player-index binding')
        state=re.findall(r'^\[BotP0\] state=(\w+) local_players=(\d+) bot_bEnabled=(\d+) game_on=(\d+)$',text,re.M)
        require(state and state[-1]==('ACTIVE','1','1','1'),'actual single local active state')
        spawn=re.findall(r'^\[CecilSpawn\] local=(\d+) tick=\d+ entity=(\d+) generation=\d+ respawns=\d+ pos=\([^\r\n]+\)$',text,re.M)
        states=re.findall(r'^\[CecilState\] local=(\d+) tick=\d+ policy=cecil-human-v1 ready=1 entity=(\d+) ',text,re.M)
        require(spawn or states,'positive actual Source actor observation')
        require(all(a=='0'and int(b)==ids[mapping['botA']]for a,b in spawn+states),'Source actor/local ambiguity')
        loads=re.findall(r'^\[CecilLoad\] policy=cecil-human-v1 schema=1 world=([^\r\n]+) ready=(\d+) nodes=(\d+) map_crc=([0-9a-f]{8}) nav_crc=([0-9a-f]{8})$',text,re.M)
        require(loads and loads[-1]==('Levels\\LevelsMP\\Deathmatch\\RedStation.wld','1','193','ff3776e0','e4571656'),'actual Red Nav loaded')
        profiles=re.findall(r'^\[BotHuman\] local=0 profile=[^\r\n]+ tier=(\d+) persona=(\w+) seed=(\d+) model=arena-v1$',text,re.M)
        require(profiles and profiles[-1][0:2]==('3','duelist'),'effective local0 combat profile')
        return {'vanilla':'vanilla','botA':'bot'}
    except (KeyError,TypeError,OverflowError,struct.error)as error:
        raise ValueError('NaturalAI030: malformed ownership evidence')from error
