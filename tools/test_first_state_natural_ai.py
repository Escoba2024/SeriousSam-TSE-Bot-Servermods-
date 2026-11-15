"""Portable policy/staging fixtures only; no process/ABI/display operations."""
import copy
import hashlib
import importlib.util
import os
from pathlib import Path
import struct
import tempfile
import types
import unittest
try:
    import first_state_natural_ai as N
except ImportError:
    N=None

ORIGINAL='1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'
BOT='bf70585708cb5cc0d0d62416b641c1df758c90b8cdbd062a04dccecca2a29412'
ENGINE='b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f'
ENTITIES='7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350'

def gms():
    data=bytearray(60);data[:8]=b'GAMEV012';data[12:25]=b'TCP/IP Client'
    struct.pack_into('<4i',data,33,0,-1,-1,-1);struct.pack_into('<i',data,49,0)
    return bytes(data)

def raw_log():
    return ('[CecilLoad] policy=cecil-human-v1 schema=1 world=Levels\\LevelsMP\\Deathmatch\\RedStation.wld ready=1 nodes=193 map_crc=ff3776e0 nav_crc=e4571656\n'
            '[BotHuman] local=0 profile=BOT-DEMON tier=3 persona=duelist seed=123 model=arena-v1\n'
            '[BotDriver] local player 0 (player index 1) is now bot-driven: SyntheticOwnFixture\n'
            '[CecilSpawn] local=0 tick=1 entity=102 generation=1 respawns=1 pos=(0.000,0.000,0.000)\n'
            '[BotP0] state=ACTIVE local_players=1 bot_bEnabled=1 game_on=1\n')

def fixture():
    records={r:{'identity':[i,100+i]}for r,i in [('server',10),('vanilla',20),('botA',30)]}
    pins={r:{name:{'sha256':pin}for name,pin in [('Engine.dll',ENGINE),('EntitiesMP.dll',ENTITIES),('GameMP.dll',BOT if r=='botA'else ORIGINAL)]}for r in records}
    frame={'roles':{'vanilla':{'entity_id':101,'entity_pointer':0x20000,'world_pointer':0x30000},'botA':{'entity_id':102,'entity_pointer':0x40000,'world_pointer':0x30000}},'server_process_identity':[10,110]}
    proof={'schema':'NATURAL_AI030_SOURCE_OWNERSHIP_V1','bot_identity':[30,130], 'server_identity':[10,110],
           'mapping':{'vanilla':0,'botA':1},'entity_ids':{'0':101,'1':102},'gms_hex':gms().hex(),
           'log_text':raw_log(),'log_epoch':{'cleared_before_launch':True,'original_sha256':hashlib.sha256(b'old fixture log').hexdigest(),'empty_sha256':hashlib.sha256(b'').hexdigest()},
           'staged':{'dll_sha256':BOT,'config_sha256':'CONFIG_PIN','nav_sha256':'70e2839587b0f14c024ef978579133e84eed594a3cbbd0fa1f1db98d99aa37c6'}}
    frame['natural_ai_ownership']=proof
    return frame,records,pins

class PolicyTests(unittest.TestCase):
    def test_actual_worker_json_roundtrip_preserves_ownership(self):
        import json
        frame,records,pins=fixture();frame['natural_ai_ownership']['staged']['config_sha256']=N.ACTIVE_CONFIG_SHA
        transferred=json.loads(json.dumps({'frame':frame,'records':records,'pins':pins}))
        try:roles=N.roles_from_receipt(transferred['frame'],transferred['records'],transferred['pins'])
        except ValueError as error:self.fail('same ownership rejected after actual JSON IPC: '+str(error))
        self.assertEqual(roles,{'vanilla':'vanilla','botA':'bot'})
    def test_bot_role_uses_exact_candidate_not_parent_original(self):
        actual=ORIGINAL if N is None else N.game_sha('botA')
        self.assertEqual(actual,BOT)
        self.assertEqual(N.game_sha('server'),ORIGINAL)
        self.assertEqual(N.game_sha('vanilla'),ORIGINAL)
        with self.assertRaises(ValueError):N.game_sha('botB')

    def test_positive_source_ownership_before_label(self):
        self.assertIsNotNone(N)
        f,r,p=fixture();f['natural_ai_ownership']['staged']['config_sha256']=N.ACTIVE_CONFIG_SHA
        self.assertEqual(N.roles_from_receipt(f,r,p),{'vanilla':'vanilla','botA':'bot'})

    def test_ownership_false_positives_fail(self):
        self.assertIsNotNone(N)
        f,r,p=fixture();f['natural_ai_ownership']['staged']['config_sha256']=N.ACTIVE_CONFIG_SHA
        changes=[lambda f,r,p:f.pop('natural_ai_ownership'),
                 lambda f,r,p:f['natural_ai_ownership']['log_epoch'].update(cleared_before_launch=False),
                 lambda f,r,p:f['natural_ai_ownership'].update(log_text=''),
                 lambda f,r,p:f['natural_ai_ownership'].update(log_text=raw_log().replace('local=0','local=1')),
                 lambda f,r,p:f['natural_ai_ownership'].update(log_text=raw_log().replace('player index 1','player index 0')),
                 lambda f,r,p:f['natural_ai_ownership'].update(log_text=raw_log().replace('entity=102','entity=999')),
                 lambda f,r,p:f['natural_ai_ownership'].update(log_text=raw_log().replace('local_players=1','local_players=2')),
                 lambda f,r,p:f['natural_ai_ownership'].update(log_text=raw_log().replace('ready=1','ready=0')),
                 lambda f,r,p:f['natural_ai_ownership'].update(log_text=raw_log().replace('tier=3','tier=1')),
                 lambda f,r,p:f['natural_ai_ownership']['mapping'].update(botA=2),
                 lambda f,r,p:f['natural_ai_ownership']['entity_ids'].update({'1':999}),
                 lambda f,r,p:f['natural_ai_ownership']['entity_ids'].update({'01':102}),
                 lambda f,r,p:f['natural_ai_ownership']['entity_ids'].update({1:102}),
                 lambda f,r,p:f['natural_ai_ownership'].update(bot_identity=[31,130]),
                 lambda f,r,p:r.update(botB={'identity':[40,140]}),
                 lambda f,r,p:p['botA']['GameMP.dll'].update(sha256=ORIGINAL),
                 lambda f,r,p:p['server']['GameMP.dll'].update(sha256=BOT),
                 lambda f,r,p:p['vanilla']['GameMP.dll'].update(sha256=BOT),
                 lambda f,r,p:p['botA']['Engine.dll'].update(sha256='0'*64),
                 lambda f,r,p:p['botA']['EntitiesMP.dll'].update(sha256='0'*64)]
        for change in changes:
            with self.subTest(change=change):
                a,b,c=copy.deepcopy((f,r,p));change(a,b,c)
                with self.assertRaises(ValueError):N.roles_from_receipt(a,b,c)

if __name__=='__main__':unittest.main()
