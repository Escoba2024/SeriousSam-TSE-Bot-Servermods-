import copy
import importlib.util
from pathlib import Path
import unittest
import json
import sys
import tempfile


def policy():
    p=Path(__file__).with_name('a1_original_respawn_policy.py')
    if not p.exists():return None
    s=importlib.util.spec_from_file_location('new_respawn_policy',p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def frame():
    roles={}
    for role,n in [('vanilla',1),('botA',2)]:
        roles[role]={'id':n,'pointer':hex(0x300000+n*0x1000),'world':'0x100000',
          'entity_flags':0 if role=='vanilla'else 8,'player_flags':1,'spawn_clock':1.,
          'health':0. if role=='vanilla'else 100.,'may_respawn':2,'buttons_now':0}
    return {'started':1.,'finished':1.01,'identity':{'server':[11,12],'vanilla':[21,22],
      'botA':[31,32],'world':'0x100000','session':'0x110000','session_level':0},'actors':roles}


def events():
    out=[];cid=0
    dead={'id':1,'pointer':'0x301000','role':'vanilla','world':'0x100000',
      'spawn_clock':1.,'generation':0,'init_call_id':None,'health':0.,'entity_flags':0,'player_flags':1,
      'initializing':False,'valid_anchor':None}
    live={**dead,'generation':1,'init_call_id':5,'health':100.,'spawn_clock':2.,'entity_flags':8,
      'valid_anchor':{'call_id':5,'kind':'initialize_player','sequence':10,'tick':{'ordinal':1,'call_id':1,'value':2.}}}
    bot={**dead,'id':2,'pointer':'0x302000','role':'bot','health':100.,'entity_flags':8}
    def row(kind,edge,call,parent,player,payload,tick=1):
        e={'row_sequence':len(out)+1,'sequence':len(out)+1,'kind':kind,'edge':edge,'call_id':call,
          'parent_call_id':parent,'thread_id':11,'identity_token':'owned','wall_ms':1000+len(out),
          'tick':{'ordinal':tick,'call_id':1 if tick==1 else 6,'value':float(tick)},
          'player':copy.deepcopy(player),'data':{'scope':'registered'if player else'context','payload':copy.deepcopy(payload)}}
        out.append(e)
    row('process_game_tick','enter',1,None,None,{})
    row('apply_action','enter',2,1,dead,{'buttons':1})
    row('apply_action','leave',2,1,dead,{'buttons':1})
    row('apply_action','enter',3,1,dead,{'buttons':0})
    d={'may_respawn':2,'released_buttons':1,'buttons_now':0}
    row('death_actions','enter',4,3,dead,d)
    end={'chain_bound':True,'apply_action_call_id':3,'death_actions_call_id':4}
    row('end_make_copy','enter',7,4,dead,end);row('end_make_copy','leave',7,4,dead,end)
    row('death_actions','leave',4,3,dead,d);row('apply_action','leave',3,1,dead,{'buttons':0})
    handler={**end,'end_copy_call_id':7}
    row('death_handler','enter',8,1,dead,handler)
    source={**handler,'death_handler_call_id':8}
    row('initialize_player','enter',5,8,dead,{'respawn_source':source})
    row('initialize_player','leave',5,8,live,{'respawn_source':source})
    row('death_handler','leave',8,1,live,handler);row('process_game_tick','leave',1,None,None,{})
    row('process_game_tick','enter',6,None,None,{},2)
    row('apply_action','enter',9,6,live,{'buttons':0},2);row('apply_action','leave',9,6,live,{'buttons':0},2)
    for base,before,after in [(10,100.,80.),(20,80.,0.)]:
        v={**live,'health':before};v2={**live,'health':after}
        row('fire_colt','enter',base,6,bot,{},2)
        row('fire_one_bullet','enter',base+1,base,bot,{'chain_bound':True,'colt_call_id':base},2)
        row('prepare_bullet','enter',base+2,base+1,bot,{'chain_bound':True,'one_call_id':base+1},2)
        row('prepare_bullet','leave',base+2,base+1,bot,{'chain_bound':True,'one_call_id':base+1},2)
        row('launch_bullet','enter',base+3,base+1,bot,{'chain_bound':True},2)
        row('cast_ray','enter',base+4,base+3,None,{'chain_bound':True,'launch_call_id':base+3,'origin_pointer':bot['pointer']},2)
        row('cast_ray','leave',base+4,base+3,None,{'chain_bound':True,'launch_call_id':base+3,'origin_pointer':bot['pointer']},2)
        row('inflict_direct_damage','enter',base+5,base+3,None,{'chain_bound':True,'cast_call_id':base+4,'inflictor':bot},2)
        payload={'chain_bound':True,'inflictor':bot,'direct_call_id':base+5,'cast_call_id':base+4,'launch_call_id':base+3,'overlap':False}
        row('receive_damage','enter',base+6,base+5,v,payload,2)
        row('receive_damage','leave',base+6,base+5,v2,payload,2)
        row('inflict_direct_damage','leave',base+5,base+3,None,{'chain_bound':True,'cast_call_id':base+4,'inflictor':bot},2)
        row('launch_bullet','leave',base+3,base+1,bot,{'chain_bound':True},2)
        row('fire_one_bullet','leave',base+1,base,bot,{'chain_bound':True,'colt_call_id':base},2)
        row('fire_colt','leave',base,6,bot,{},2)
    row('process_game_tick','leave',6,None,None,{},2)
    return out


class RespawnPolicy(unittest.TestCase):
    def setUp(self):
        self.p=policy();self.assertIsNotNone(self.p,'new strict DEAD_READY/respawn policy is missing')

    def test_real_dead_readiness_returns_exact_pin_and_requires_reserve(self):
        f=frame();pin=self.p.dead_ready(f,now=1.02,deadline=20.)
        self.assertEqual(pin['actors'],f['actors'])
        with self.assertRaises(ValueError):self.p.dead_ready(f,now=1.02,deadline=3.)

    def test_false_readiness_identity_clock_and_bool_never_admit(self):
        for key,value in [('health',1.),('health',True),('may_respawn',1),('may_respawn',True),('buttons_now',1),('entity_flags',8),('entity_flags',4),('entity_flags',0x20000),('id',True),('pointer','0x0')]:
            f=frame();f['actors']['vanilla'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):self.p.dead_ready(f,now=1.02,deadline=20.)
        for mutation in ['stale','backward','world','life','pid','botdeath']:
            f=frame();pin=self.p.dead_ready(f,now=1.02,deadline=20.)
            if mutation=='stale':f['started']=.1
            elif mutation=='backward':f['finished']=.9
            elif mutation=='world':f['actors']['vanilla']['world']='0x200000'
            elif mutation=='life':f['actors']['vanilla']['spawn_clock']=2.
            elif mutation=='pid':f['identity']['server'][0]=99
            else:f['actors']['botA']['health']=0.
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):self.p.dead_ready(f,now=1.02,deadline=20.,expected=pin)

    def test_complete_actual_row_shape_respawn_first_tick_normal_fatal(self):
        es=events();result=self.p.complete_chain(es,cutoff=len(es),dead_pin=self.p.dead_ready(frame(),now=1.02,deadline=20.),row_floor=0)
        self.assertEqual(result['status'],'LIMITED_BOUND_ORIGINAL_RESPAWN_COLT_EXAMPLES_ONLY')
        self.assertEqual(result['normal_damage_calls'],[16]);self.assertEqual(result['fatal_damage_calls'],[26])
        self.assertFalse(result['a1_accepted'])
        self.assertFalse(result['first_valid_state_damage_proven'])
        self.assertEqual(result['first_damage']['call_id'],16)
        self.assertEqual(result['first_damage']['native_tick'],2.)
        self.assertEqual(result['init']['call_id'],5)
        self.assertEqual(result['valid_anchor']['call_id'],5)

    def test_original_direct_callback_has_no_player_snapshot(self):
        es=events()
        # Actual observer_body.js:383-397 binds owner/victim in payload, not f.player.
        for e in es:
            if e['kind']=='inflict_direct_damage':
                e['data']['payload']['inflictor']=copy.deepcopy(next(x['data']['payload']['inflictor']for x in es if x['kind']=='receive_damage'))
                e['player']=None
        result=self.p.complete_chain(es,cutoff=len(es),dead_pin=self.p.dead_ready(frame(),now=1.02,deadline=20.),row_floor=0)
        self.assertEqual(result['normal_damage_calls'],[16])

    def test_actual_original_callback_model_complete_colt_respawn_chain(self):
        sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
        from tools import test_first_state_registered_damage_patch as fixture
        path=Path('/srv/tse-a1-first-state-respawn-completion-20261112/successor/tests/respawn_fixture.js')
        source=fixture.read(path).replace(b"const B=require('../../initial-static-bindings.json');",b"const B=require('./observer_harness').G;")
        old=b' const packet=x.api.drain();x.api.stop();const end=x.api.drain();'
        self.assertEqual(source.count(old),1)
        source=source.replace(old,b""" const observations=[x.api.drain()];const second=x.startTick(8);
 x.call('apply_action',player,[0x720000,['f',1]]);
 for(const hp of [80,60,40,20,0]){x.shot({duringReceive({f}){f(player+0xcc,hp);}});observations.push(x.api.drain());}
 x.leave(second);const packet=x.api.drain();x.api.stop();x.api.finishstop();const end=x.api.drain();""")
        source=source.replace(b'return{x,packet,end,delivery,',b'return{observations,x,packet,end,delivery,')
        ps=json.loads(fixture.ActualRegisteredScope().run_js("""
const {scenario}=require('./tests/respawn_fixture');
const r=scenario({config:{players:[{id:565,pointer:'0x300000',role:'vanilla'},{id:566,pointer:'0x310000',role:'bot'}]},beforeCopy({x,player}){x.u(0x720024,1);x.call('apply_action',player,[0x720000,['f',1]]);x.u(0x720024,0);}});
console.log(JSON.stringify(r.observations.concat([r.packet,r.end])));
""",extra={'tests/respawn_fixture.js':source}))
        from tools.test_first_state_registered_damage_policy import policy as load_policy
        parent=Path('/srv/tse-a1-registered-first-state-damage-v1-v3-disabled-20261115/method-api/vendor/observer')
        with tempfile.TemporaryDirectory(prefix='respawn-policy-')as td:
            root=Path(td);(root/'bindings').mkdir()
            for rel in('observer_policy.py','event-schema.json','bindings/original-bindings.json'):
                (root/rel).write_bytes(fixture.read(parent/rel))
            strict=load_policy(root);trace=strict.TraceValidator(ps[0]['identity'])
            for packet in ps:trace.consume(packet)
            self.assertEqual(len(trace.events),sum(len(p['events'])for p in ps))
        es=[e for p in ps for e in p['events']]
        down=next(e for e in es if e['kind']=='apply_action'and e['edge']=='enter'and e['data']['payload']['buttons']==1)
        bot=next(e['player']for e in es if e['kind']=='fire_colt')
        result=self.p.complete_chain(es,cutoff=len(es),dead_pin={'actors':{'vanilla':down['player'],'botA':bot}},row_floor=down['row_sequence']-1)
        self.assertEqual(len(result['normal_damage_calls']),4)
        self.assertEqual(len(result['fatal_damage_calls']),1)

    def test_missing_chain_owner_life_leave_cutoff_and_first_tick_fail(self):
        for mutation in ['init','respawnfalse','owner','victimlife','leave','normal','fatal','tick','cutoff','down','release','dead_damage']:
            es=events();cut=len(es)
            if mutation=='init':es=[e for e in es if e['kind']!='initialize_player']
            elif mutation=='respawnfalse':next(e for e in es if e['kind']=='initialize_player')['data']['payload']['respawn_source']['chain_bound']=False
            elif mutation=='owner':next(e for e in es if e['kind']=='receive_damage')['data']['payload']['inflictor']['id']=9
            elif mutation=='victimlife':next(e for e in es if e['kind']=='receive_damage')['player']['generation']=9
            elif mutation=='leave':es=[e for e in es if not(e['call_id']==26 and e['edge']=='leave')]
            elif mutation=='normal':next(e for e in es if e['call_id']==16 and e['edge']=='leave')['player']['health']=100.
            elif mutation=='fatal':next(e for e in es if e['call_id']==26 and e['edge']=='leave')['player']['health']=1.
            elif mutation=='tick':es=[e for e in es if e['kind']!='process_game_tick' or e['call_id']!=6]
            elif mutation=='cutoff':cut=20
            elif mutation=='down':next(e for e in es if e['kind']=='apply_action')['data']['payload']['buttons']=0
            elif mutation=='release':next(e for e in es if e['kind']=='death_actions')['data']['payload']['released_buttons']=0
            elif mutation=='dead_damage':
                for e in es:
                    if e['call_id']==16:e['player']['health']=-1. if e['edge']=='enter'else -2.
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):self.p.complete_chain(es,cutoff=cut,dead_pin=self.p.dead_ready(frame(),now=1.02,deadline=20.),row_floor=0)


if __name__=='__main__':unittest.main()
