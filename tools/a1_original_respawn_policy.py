"""Pure predicates for one NEW normal Original respawn/Colt condition.

The unchanged registered TraceValidator is mandatory before complete_chain;
these predicates add example requirements, never replace its raw/ABI guards.
"""
import copy
import math

CONDITION='NORMAL_ORIGINAL_RESPAWN_FIXEDTARGET030_COLT_V1'
FIRE=1


def need(ok,message):
    if not ok:raise ValueError('Original respawn: '+message)


def number(value):return type(value)in(int,float)and math.isfinite(value)


def actor_key(a):
    need(type(a)is dict,'actor object')
    need(type(a.get('id'))is int and 0<a['id']<=0x7fffffff,'actor ID')
    for k in('pointer','world'):
        value=a.get(k)
        need(type(value)is str and value.startswith('0x'),'actor pointer shape')
        try:n=int(value,16)
        except ValueError:raise ValueError('Original respawn: pointer hex')from None
        need(0x10000<=n<=0xffffd000 and n%4==0,'actor pointer bounds')
    need(number(a.get('spawn_clock'))and a['spawn_clock']>0,'spawn clock')
    return a['id'],a['pointer'],a['world'],a['spawn_clock']


def bound_frame(frame,now,expected=None):
    need(type(frame)is dict and number(now),'frame/clock')
    a,b=frame.get('started'),frame.get('finished')
    need(number(a)and number(b)and 0<=a<=b<=now and now-a<=.2,'fresh .2s frame')
    need(set(frame.get('actors',{}))=={'vanilla','botA'},'exact actors')
    identity=frame.get('identity');need(type(identity)is dict,'identity')
    for role in('server','vanilla','botA'):
        v=identity.get(role);need(type(v)is list and len(v)==2 and all(type(x)is int and x>1 for x in v),'PID/start')
    need(len({tuple(identity[r])for r in('server','vanilla','botA')})==3,'distinct OS roles')
    keys={r:actor_key(a)for r,a in frame['actors'].items()}
    need(keys['vanilla'][0]!=keys['botA'][0]and keys['vanilla'][1]!=keys['botA'][1]
         and keys['vanilla'][2]==keys['botA'][2]==identity.get('world'),'distinct actors/same World')
    for a in frame['actors'].values():
        need(number(a.get('health')),'health')
        for k in('entity_flags','player_flags','may_respawn','buttons_now'):
            need(type(a.get(k))is int and 0<=a[k]<2**32,'exact state integer')
        need(not a['entity_flags']&(4|0x20000)and a['player_flags']&1 and not a['player_flags']&0x100,'deleted/predictor/uninitialized')
    need(frame['actors']['botA']['health']>0,'shooter alive')
    if expected is not None:
        need(identity==expected['identity'],'bound process/session/world changed')
        need(all(keys[r]==actor_key(expected['actors'][r])for r in keys),'bound Actor/World/Life changed')
    return frame


def dead_ready(frame,*,now,deadline,expected=None):
    need(number(deadline)and number(now)and deadline-now>=2.35,'2.35s input reserve')
    bound_frame(frame,now,expected)
    a=frame['actors']['vanilla']
    need(a['health']<=0 and not a['entity_flags']&8,'actual dead Original')
    need(a['may_respawn']==2 and not a['buttons_now']&FIRE,'actual MayRespawn2/neutral Fire')
    return copy.deepcopy(frame)


def complete_chain(events,*,cutoff,dead_pin,row_floor):
    """Only positive rows <=S; no host/JS/native clock conversion.

    Input transport/Control ACK is validated separately. row_floor is the actual
    last consumed full-row count immediately before the single Down admission.
    """
    need(type(cutoff)is int and type(row_floor)is int and 0<=row_floor<cutoff<=len(events),'exact positive S/floor')
    es=events[:cutoff];calls={}
    for e in es:
        need(type(e['row_sequence'])is int and e['row_sequence']<=cutoff,'real row domain')
        payload=e['data']['payload'];need(e['data']['scope']!='unregistered','unknown relevant owner')
        need(payload.get('chain_bound')is not False,'explicit unbound chain')
        rs=payload.get('respawn_source')
        need(not(type(rs)is dict and rs.get('chain_bound')is False),'unbound respawn')
        pair=calls.setdefault(e['call_id'],{});need(e['edge']not in pair,'duplicate edge');pair[e['edge']]=e
    def pair(cid,kind):
        p=calls.get(cid,{})
        need(set(p)=={'enter','leave'}and all(x['kind']==kind for x in p.values()),'complete '+kind)
        return p['enter'],p['leave']
    def player(e,role,key):
        a=e.get('player');need(a is not None and a['role']==role and actor_key(a)[:3]==key[:3],'bound '+role)
        return a
    original=actor_key(dead_pin['actors']['vanilla']);bot=actor_key(dead_pin['actors']['botA'])
    inits=[e for e in es if e['kind']=='initialize_player'and e['edge']=='leave'and
           e.get('player',{}).get('role')=='vanilla'and e['row_sequence']>row_floor]
    need(len(inits)==1,'exact one observed Original Init after input floor')
    init=inits[0];before,after=pair(init['call_id'],'initialize_player')
    old=player(before,'vanilla',original);fresh=player(after,'vanilla',original)
    need(actor_key(old)==original and old['health']<=0 and fresh['health']>0,'dead→live actual Init')
    need(type(fresh['generation'])is int and fresh['generation']==old['generation']+1
         and fresh['init_call_id']==init['call_id']and not fresh['initializing'],'Init generation')
    anchor=fresh.get('valid_anchor');need(type(anchor)is dict and anchor['call_id']==init['call_id'],'real first valid anchor')
    source=after['data']['payload'].get('respawn_source');need(type(source)is dict and source.get('chain_bound')is True,'actual normal respawn source')
    h,_=pair(source['death_handler_call_id'],'death_handler')
    end,_=pair(source['end_copy_call_id'],'end_make_copy')
    death,_=pair(source['death_actions_call_id'],'death_actions')
    action,_=pair(source['apply_action_call_id'],'apply_action')
    need(init['parent_call_id']==h['call_id']and end['parent_call_id']==death['call_id']
         and death['parent_call_id']==action['call_id'],'real respawn parents')
    for e in(h,end,death,action):player(e,'vanilla',original)
    need(h['data']['payload'].get('chain_bound')is True and end['data']['payload'].get('chain_bound')is True,'bound death/copy')
    d=death['data']['payload']
    need(d['may_respawn']==2 and d['released_buttons']&FIRE and not d['buttons_now']&FIRE,'actual released Fire/readiness')
    down=[e for e in es if e['kind']=='apply_action'and e['edge']=='enter'and e.get('player')and
          e['player']['role']=='vanilla'and row_floor<e['row_sequence']<action['row_sequence']and e['data']['payload']['buttons']&FIRE]
    need(down and actor_key(down[-1]['player'])==original,'actual bound server Fire Down')
    ticks=[]
    for e in es:
        if e['kind']!='process_game_tick'or e['edge']!='enter'or e['row_sequence']<=init['row_sequence']:continue
        _,leave=pair(e['call_id'],'process_game_tick')
        candidates=[x for x in es if e['row_sequence']<x['row_sequence']<leave['row_sequence']and x.get('player')and x['player']['role']=='vanilla'and x['player']['init_call_id']==init['call_id']and x['player']['valid_anchor']==anchor]
        if candidates:ticks.append(e)
    need(ticks,'actual post-Init first valid GameTick')
    first=ticks[0];normal=[];fatal=[]
    for e in es:
        if e['kind']!='receive_damage'or e['edge']!='enter':continue
        a,b=pair(e['call_id'],'receive_damage');v=player(a,'vanilla',original);w=player(b,'vanilla',original)
        need(a['row_sequence']>first['row_sequence']and actor_key(v)==actor_key(fresh)==actor_key(w)
             and v['generation']==fresh['generation']==w['generation']and v['init_call_id']==fresh['init_call_id']==w['init_call_id'],'post-Init victim life')
        q=a['data']['payload'];owner=q.get('inflictor')
        need(type(owner)is dict and owner['role']=='bot'and actor_key(owner)==bot,'actual Bot030 inflictor')
        need(q.get('chain_bound')is True and b['data']['payload'].get('chain_bound')is True and not q.get('overlap'),'bound Receive Enter/Leave')
        direct,_=pair(q['direct_call_id'],'inflict_direct_damage')
        cast,_=pair(q['cast_call_id'],calls[q['cast_call_id']]['enter']['kind'])
        launch,_=pair(q['launch_call_id'],'launch_bullet')
        need(cast['kind']in('cast_ray','continue_cast')and a['parent_call_id']==direct['call_id']
             and direct['parent_call_id']==launch['call_id']and cast['parent_call_id']==launch['call_id'],'real damage parents')
        one,one_leave=pair(launch['parent_call_id'],'fire_one_bullet')
        colt,_=pair(one['parent_call_id'],'fire_colt')
        prepared=[x for x in es if x['kind']=='prepare_bullet'and x['edge']=='enter'and x['parent_call_id']==one['call_id']]
        need(len(prepared)==1,'exact PrepareBullet');pair(prepared[0]['call_id'],'prepare_bullet')
        need(actor_key(direct['data']['payload']['inflictor'])==bot
             and direct['data']['payload']['inflictor']['role']=='bot'
             and cast['data']['payload']['origin_pointer']==bot[1],'actual Direct/Cast owner payload')
        for x in(launch,one,colt,prepared[0]):player(x,'bot',bot)
        need(number(v['health'])and number(w['health'])and v['health']>0 and v['health']>w['health'],'actual live HP loss')
        (fatal if v['health']>0>=w['health']else normal).append(a['call_id'])
    need(normal and fatal,'both actual normal and fatal Colt damage examples INCOMPLETE')
    return {'status':'LIMITED_BOUND_ORIGINAL_RESPAWN_COLT_EXAMPLES_ONLY','a1_accepted':False,
      'qualified':False,'init_call_id':init['call_id'],'first_valid_game_tick_call':first['call_id'],
      'normal_damage_calls':normal,'fatal_damage_calls':fatal,'row_floor':row_floor,'positive_cutoff':cutoff}
