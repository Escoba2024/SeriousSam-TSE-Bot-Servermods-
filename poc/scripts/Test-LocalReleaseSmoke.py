"""Sparse production-profile smoke; it never qualifies a 20-Hz/hour AI stream."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

spec=importlib.util.spec_from_file_location('fleet_ai',Path(__file__).with_name('Test-FleetAIEvidence.py'))
fleet=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fleet)
require=fleet.require


def assert_production_startup(startup):
    canonical=Path(__file__).with_name('LocalBotRelease.ini')
    require(hashlib.sha256(startup.read_bytes()).digest()==hashlib.sha256(canonical.read_bytes()).digest(),'expected exact canonical production startup')


def assert_navigation(n):
    alive,active,phase=(int(n[key]) for key in ('alive','active','phase'))
    delta,forward=float(n['delta']),float(n['forward'])
    rays=[float(n[key]) for key in ('front','left','right')]
    require(all(math.isfinite(v) for v in (delta,forward,*rays)) and abs(delta)<=2.251 and 0<=forward<=1 and all(0<=v<=3 for v in rays),'sparse native action bounds')
    require(not active or (alive and not int(n['hold']) and phase in (1,2)),'invalid sparse active recovery')
    require(not(active and phase==1) or forward==0,'sparse turn also advances')
    return fleet.position(n)


def audit_sparse_stream(path, expected_slots=4, min_samples=100):
    start, slots=0,{}
    with path.open('rb') as stream:
        while True:
            offset=stream.tell()
            raw=stream.readline()
            if not raw: break
            match=fleet.REGISTER.match(raw.decode('utf-8',errors='replace').strip())
            if match:
                slot,player=int(match[1]),int(match[2])
                if slot==0: start,slots=offset,{}
                require(slot not in slots,'duplicate sparse native registration')
                slots[slot]=(player,match[3])
    require(set(slots)==set(range(expected_slots)) and len({p for p,_ in slots.values()})==expected_slots,'incomplete sparse native registrations')
    states={slot:dict(tick=None,frame={},positions=set(),samples=0,ready=0,first=None,last=None,trailing=0) for slot in slots}

    def flush(slot, final=False):
        state=states[slot]
        frame=state['frame']
        if not frame: return
        complete=all(tag in frame for tag in ('BotNavigation','BotCombat','BotDriver'))
        if final and not complete:
            state['trailing']=1
            return
        require(complete,'missing matching sparse native decision/submitted action')
        n,c,d=(frame[tag] for tag in ('BotNavigation','BotCombat','BotDriver'))
        require(int(c['self'])==slots[slot][0],'wrong sparse native self')
        alive,active,phase=(int(n[key]) for key in ('alive','active','phase'))
        require(alive==int(c['alive']),'sparse navigation/combat life mismatch')
        if int(d['fire']) and alive:
            require(not active and int(c['ready']),'sparse attack without readiness')
            w=frame.get('BotCombatWeapon')
            require(w is not None and int(w['current'])==int(w['wanted'])==int(w['desired'])==int(c['weapon']),'sparse attack without native weapon acknowledgement')
        p=fleet.position(n)
        if len(state['positions'])<11: state['positions'].add(p)
        state['ready']+=bool(alive and int(c['ready']))
        state['samples']+=1
        if state['first'] is None: state['first']=state['tick']
        state['last']=state['tick']

    with path.open('rb') as stream:
        stream.seek(start)
        for raw in stream:
            row=fleet.record(raw.decode('utf-8',errors='replace').strip())
            if row is None: continue
            tag,tick,slot,fields=row
            require(tag!='BotSnapshot','production diagnostics profile unexpectedly emits full snapshots')
            require(slot in states,'unregistered sparse native local slot')
            if tag=='BotCombat':
                require(int(fields['self'])==slots[slot][0],'wrong sparse native self')
                require(int(fields['target']) not in {p for p,_ in slots.values()},'production selected a local target')
                fleet.assert_combat_bounds(fields)
            elif tag=='BotNavigation': assert_navigation(fields)
            if tick%20: continue
            state=states[slot]
            if state['tick']!=tick:
                flush(slot)
                require(state['tick'] is None or tick==state['tick']+20,'missing sparse periodic native sample')
                state['tick'],state['frame']=tick,{}
            require(tag not in state['frame'],'duplicate sparse native row')
            state['frame'][tag]=fields
    result=[]
    for slot,state in states.items():
        flush(slot,final=True)
        require(state['samples']>=min_samples,'insufficient sparse native samples')
        require(len(state['positions'])>10,'missing sparse native movement')
        require(state['ready'],'missing living native combat readiness')
        result.append(dict(localSlot=slot,player=slots[slot][0],name=slots[slot][1],completeSamples=state['samples'],firstTick=state['first'],lastTick=state['last'],trailingIncompleteSamples=state['trailing'],distinctNativePositionsAtLeast=len(state['positions']),livingReadySamples=state['ready']))
    return result


def audit(root,dll,startup):
    assert_production_startup(startup)
    result=fleet.audit_runtime(root,dll,startup)
    require(result['nativeJoinOnly'],'production smoke requires explicitly labelled native join-only mode')
    require(result['lifecycle'],'production release smoke requires the native lifecycle')
    clients=[dict(client=name,players=audit_sparse_stream(root/'retail'/f'{name}-SeriousSam.log')) for name in ('TSE-BotClient','TSE-BotClient2')]
    require({p['name'] for c in clients for p in c['players']}=={p['name'] for p in result['identities']},'sparse decisions differ from eight native identities')
    result.update(clients=clients,scope='Exact low-log production startup native smoke: eight real players, life cycle, sparse valid decisions/actions, sibling exclusion, native movement/combat, resources, cleanup and preservation. No 20-Hz continuity, per-bot wall-completion or hour qualification claim.')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('root',type=Path)
    parser.add_argument('--dll',type=Path,required=True)
    parser.add_argument('--startup',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.root,args.dll,args.startup)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PRODUCTION PROFILE NATIVE SMOKE PASS:',args.output)
