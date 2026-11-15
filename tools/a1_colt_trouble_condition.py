"""Pure NEW LittleTrouble condition; existing roleframe values only.

No runtime/process/clock API, no synthetic spawn, LOS or damage-owner claim.
"""
import copy
import hashlib
import json
import os
import stat
from pathlib import Path
try:from . import a1_original_respawn_policy as P
except ImportError:import a1_original_respawn_policy as P

CONDITION='NORMAL_ORIGINAL_RESPAWN030_COLT_LITTLE_TROUBLE_V1'
OWNERSHIP_PAYLOAD_LIMIT=64*1024**2
MAX_ROLE_READS=1024
STARTUP_REL=Path('server/Scripts/Dedicated/BotTest/1_begin.ini')
STARTUP_SHA='866030fd89efaadf2e7168a528d7d332f53d783a5d076aef9f0c298332e51d8f'
NATIVE_DISK_MINIMUM=8*1024**3+(64+64+512+64)*1024**2
RAM_FIXTURE_DISK_MINIMUM=8*1024**3+128*1024**2
RAM_MEMORY_MINIMUM=(1536+64+512+64+512)*1024**2
RAM_VOLUME_MINIMUM=(64+512+64)*1024**2


def require_disk(directory):
    """Operational reservation, not a guarantee of all possible output sizes."""
    info=os.statvfs(directory);free=info.f_bavail*info.f_frsize
    P.need(free>=NATIVE_DISK_MINIMUM,'8GiB floor +64MiB safety +64MiB ownership +512MiB journal +64MiB case reserve')
    return {'free_bytes':free,'minimum_free_bytes':NATIVE_DISK_MINIMUM,
            'all_1024_receipts_fit_guaranteed':False,'output_upper_bound_proven':False}


def volume_budget(host_sample,ram_mode,ram_free=None):
    """Use the existing HostBudget sample; never reread its CPU/RAM/disk data."""
    P.need(type(ram_mode)is bool and type(host_sample)is dict,'explicit evidence volume mode/sample')
    disk=host_sample.get('disk_free_bytes');memory=host_sample.get('mem_available_bytes')
    P.need(type(disk)is int and disk>=0 and type(memory)is int and memory>=0,'actual typed host byte counters')
    minimum=RAM_FIXTURE_DISK_MINIMUM if ram_mode else NATIVE_DISK_MINIMUM
    P.need(disk>=minimum,'evidence volume fixture disk reservation')
    if ram_mode:
        P.need(memory>=RAM_MEMORY_MINIMUM,'evidence RAM MemAvailable reservation')
        P.need(type(ram_free)is int and ram_free>=RAM_VOLUME_MINIMUM,'evidence RAM volume free reservation')
    return {'mode':'explicit_ram_evidence_only'if ram_mode else'default_disk',
            'fixture_disk_minimum_bytes':minimum,'mem_available_minimum_bytes':RAM_MEMORY_MINIMUM if ram_mode else 1536*1024**2,
            'ram_volume_minimum_bytes':RAM_VOLUME_MINIMUM if ram_mode else None,
            'disk_free_bytes':disk,'mem_available_bytes':memory,'ram_free_bytes':ram_free if ram_mode else None,
            'all_1024_receipts_fit_guaranteed':False,'output_upper_bound_proven':False}


def _mem_available():
    path=Path('/proc/meminfo').resolve(strict=True)
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:data=f.read(65537)
    P.need(len(data)<=65536,'bounded actual MemAvailable source')
    rows=[line.split()for line in data.decode('ascii').splitlines()if line.startswith('MemAvailable:')]
    P.need(len(rows)==1 and len(rows[0])==3 and rows[0][2]=='kB'and rows[0][1].isdigit(),'exact MemAvailable record')
    return int(rows[0][1])*1024


def select_case_base(base,ram_base):
    """Explicit existing owned RAM directory; tools/fixture stay on disk."""
    base=Path(base)
    if ram_base is None:return base,require_disk(base)
    candidate=Path(ram_base);root=Path('/dev/shm')
    P.need(candidate.is_absolute()and candidate!=root and root in candidate.parents,'explicit child of /dev/shm')
    P.need(candidate.resolve(strict=True)==candidate and root.resolve(strict=True)==root,'no RAM path aliases/symlinks')
    st=candidate.stat();parent=root.stat()
    P.need(stat.S_ISDIR(st.st_mode)and st.st_uid==os.geteuid()and stat.S_IMODE(st.st_mode)==0o700 and st.st_dev==parent.st_dev,'owned0700 same RAM volume directory')
    disk=os.statvfs(base);ram=os.statvfs(candidate)
    record=volume_budget({'disk_free_bytes':disk.f_bavail*disk.f_frsize,'mem_available_bytes':_mem_available()},True,ram.f_bavail*ram.f_frsize)
    record['explicit_case_base']=str(candidate)
    return candidate,record


def stage_startup(transaction,root,evidence):
    """One exact map-token change after the existing Scripts snapshot/seal."""
    root=Path(root).resolve(strict=True)
    P.need(transaction.sealed and transaction.root==root,'sealed same-root startup transaction')
    record=transaction.records.get(str(STARTUP_REL),{})
    P.need(record.get('existed')is True and record.get('sha256')==STARTUP_SHA,'exact startup snapshot')
    path=transaction.path(STARTUP_REL)
    with os.fdopen(os.open(path.resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:data=f.read(16385)
    P.need(len(data)<=16384 and hashlib.sha256(data).hexdigest()==STARTUP_SHA,'exact current startup bytes')
    P.need(data.count(b'RedStation.wld')==1,'one normal level token')
    changed=data.replace(b'RedStation.wld',b'DM_LittleTrouble.wld')
    receipt={'schema':'ORIGINAL_COLT_TROUBLE_STARTUP_V1','before_sha256':STARTUP_SHA,
             'after_sha256':hashlib.sha256(changed).hexdigest(),'start_difficulty':3,
             'spawn_invulnerability':0,'spawn_marker_selected':False,'los_proven':False}
    # Exclusive receipt first: duplicate admission cannot silently restage.
    payload=(json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode()
    out=Path(evidence)/'little-trouble-world-staging.json'
    with os.fdopen(os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(payload);f.flush();os.fsync(f.fileno())
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_TRUNC|os.O_NOFOLLOW),'wb')as f:f.write(changed);f.flush();os.fsync(f.fileno())
    with os.fdopen(os.open(path.resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:P.need(f.read(16385)==changed,'startup stage readback')
    return receipt


def role_geometry(native,frame):
    """Archive first-observed placement, not a selected/first spawn marker.

    Original/server clocks and process-local addresses remain separate. Nothing
    here proves visibility; existing pair/context guards still run in caller.
    """
    try:
        P.bound_frame(frame,frame['finished'])
        P.need(native['server_process_identity']==frame['identity']['server'],'geometry server PID/start')
        P.need(set(native['roles'])=={'vanilla','botA'},'geometry exact roles')
        def position(row,role,*,replica=False):
            actor=frame['actors'][role]
            P.need(row['present']is True and type(row['slot'])is int and row['slot']==(0 if role=='vanilla'else 1),'geometry exact slot')
            P.need(row['entity_id']==actor['id']and type(row['entity_id'])is int and P.number(row['spawned_tick'])and P.number(row['health'])and row['spawned_tick']==actor['spawn_clock']and row['health']==actor['health'],'geometry Actor/Life/state')
            for key in('entity_pointer','world_pointer'):
                P.need(type(row[key])is int and 0x10000<=row[key]<=0xffffd000 and row[key]%4==0,'geometry pointer')
            if not replica:
                P.need(row['entity_pointer']==int(actor['pointer'],16)and row['world_pointer']==int(actor['world'],16),'geometry server binding')
            placement=row['placement'];P.need(type(placement)in(list,tuple)and len(placement)==6 and all(P.number(x)for x in placement),'finite existing placement')
            P.need(P.number(row['game_tick'])and row['game_tick']>=0,'geometry native clock')
            return {'entity_id':row['entity_id'],'entity_pointer':row['entity_pointer'],'world_pointer':row['world_pointer'],
                    'spawn_clock':row['spawned_tick'],'placement':list(placement),'game_tick':row['game_tick']}
        server={role:position(row,role)for role,row in native['roles'].items()}
        replica=native['original_replica']
        P.need(replica['process_identity']==native['vanilla_process_identity']==frame['identity']['vanilla'],'geometry Original PID/start')
        original=position(replica,'vanilla',replica=True)
        return {'schema':'ORIGINAL_COLT_TROUBLE_EXISTING_ROLE_GEOMETRY_V1','server_actors':server,
                'original_replica':original,'server_process_identity':copy.deepcopy(native['server_process_identity']),
                'original_process_identity':copy.deepcopy(replica['process_identity']),
                'spawn_marker_proven':False,'los_proven':False,'clock_domains_fused':False}
    except(KeyError,TypeError,OverflowError)as error:
        raise ValueError('LittleTrouble: malformed existing role geometry')from error


def require_hp_drop(first,rows):
    """Actual same-life positive→drop→DEAD_READY; no inferred hit owner."""
    P.bound_frame(first,first['finished'])
    a=first['actors']['vanilla'];P.need(a['health']>0 and a['entity_flags']&8,'actual positive live Original')
    P.need(type(rows)is list and 1<=len(rows)<=MAX_ROLE_READS,'bounded actual admission frames')
    previous=first;drop=None
    for row in rows:
        P.need(type(row)is dict and 'frame'in row and not row.get('error'),'complete admission frame')
        f=row['frame'];P.bound_frame(f,f['finished'],first)
        P.need(f['started']>=previous['started']and f['finished']>=previous['finished'],'ordered admission frames')
        if drop is None and f['actors']['vanilla']['health']<previous['actors']['vanilla']['health']:drop=copy.deepcopy(f)
        previous=f
    a=previous['actors']['vanilla']
    P.need(drop is not None,'actual observed HP decrease required')
    P.need(a['health']<=0 and not a['entity_flags']&8 and a['may_respawn']==2 and not a['buttons_now']&1,'actual observed DEAD_READY')
    return {'schema':'ORIGINAL_COLT_TROUBLE_PREARM_HP_DROP_V1','hp_drop_observed':True,
            'first_drop':drop,'dead_ready':copy.deepcopy(previous),'reads_considered':len(rows),
            'intermediate_positive_drop_observed':drop['actors']['vanilla']['health']>0,
            'damage_owner_proven':False,'los_proven':False,'first_valid_state_damage_proven':False}
