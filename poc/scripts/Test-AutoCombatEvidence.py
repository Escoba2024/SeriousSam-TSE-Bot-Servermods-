"""Audit completed native combat logs; transport success alone is insufficient."""
import argparse, hashlib, json, re
from pathlib import Path

GROUPS = (0,1,2,2,3,3,4,4,5,5,1,6,7,6,8)

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def rows(text, tag):
    result = {}
    for line in text.splitlines():
        if not line.startswith('[' + tag + '] '):
            continue
        fields = dict(re.findall(r'(\w+)=([^\s]+)', line))
        key = (int(fields['local']), int(fields['tick']))
        if key in result:
            raise AssertionError(f'duplicate {tag} row {key}')
        result[key] = fields
    return result

def audit(root, dll):
    native = root / 'native-2-Combat'
    result = json.loads((native / 'result.json').read_text(encoding='utf-8-sig'))
    diagnostics = json.loads((root / 'diagnostics.json').read_text(encoding='utf-8-sig'))
    telemetry = json.loads((native / 'telemetry.json').read_text(encoding='utf-8-sig'))
    identities = json.loads((root / 'identities-2.json').read_text(encoding='utf-8-sig'))
    require(len(identities)==2 and len({i['guid'] for i in identities})==2 and
            len({i['name'] for i in identities})==2, 'distinct native profiles/GUIDs')
    digest = hashlib.sha256(dll.read_bytes()).hexdigest().upper()
    require(result['sha256'] == digest, 'evidence does not use current candidate')
    for field in ('loaded','alive','serverAlive','crcAccepted','clientCurrentlyJoined',
                  'observerCurrentlyJoined','observerAlive','observerSawBotJoin'):
        require(result[field], f'native join/CRC gate: {field}')
    require(result['crcAcceptedCount'] >= 2 and result['elapsedSeconds'] >= 120, 'bounded native duration/CRC')
    require(diagnostics['passed'] and all(f['restored'] for f in diagnostics['restored']), 'restoration failed')
    require(not any(diagnostics[k] for k in ('ownedProcesses','udpPorts','matchingCrashEvents','crashReports','cleanupErrors')),
            'runtime cleanup/crash gate')
    require(diagnostics['applicationEventsRead'], 'application events not checked')
    require(not telemetry['rejectedSnapshotLines'], 'corrupt snapshot evidence')
    text = (native / 'SeriousSam.log').read_text(encoding='utf-8', errors='replace')
    observer = (native / 'observer-SeriousSam.log').read_text(encoding='utf-8', errors='replace')
    combat, weapons = rows(text,'BotCombat'), rows(text,'BotCombatWeapon')
    driver = {(int(m[1]), int(m[2])): int(m[3]) for m in re.finditer(
        r'\[BotDriver\] bot(\d+) tick=(\d+) [^\n]* fire=(\d+)',text)}
    snapshots = {(int(m[1]),int(m[2])):int(m[3]) for m in re.finditer(
        r'\[BotSnapshot\] tick=(\d+) player=(\d+) [^\n]* buttons=(\d+)',text)}
    records = []
    matched_groups, emitted_groups = set(), set()
    for local in (0,1):
        sequence = sorted((tick,v) for (slot,tick),v in combat.items() if slot==local)
        require(len(sequence)>=600, f'missing combat decisions local {local}')
        targets, ready, attacks, dead, no_target = set(),0,0,0,0
        last_alive, deaths, respawns, first_dead = None,0,0,None
        for tick,v in sequence:
            target, alive = int(v['target']), int(v['alive'])
            if target>=0:
                require(alive==1 and int(v['dm'])==1 and int(v['visible'])>0 and target!=int(v['self']), 'invalid target gate')
                targets.add(target)
            else:
                no_target += 1
                require(int(v['ready'])==0, 'stale ready flag without target')
            if not alive:
                dead += 1
                require(target==-1 and int(v['ready'])==0 and float(v['move'])==0, 'dead combat decision')
            if last_alive is True and not alive:
                deaths += 1
                if first_dead is None: first_dead=tick
            if last_alive is False and alive and first_dead is not None: respawns += 1
            last_alive = bool(alive)
            if int(v['ready']):
                ready += 1
                w = weapons[(local,tick)]
                require(int(w['desired'])==int(w['current'])==int(w['wanted']), 'ready before native desired weapon settled')
                matched_groups.add(int(w['group']))
            if driver.get((local,tick)) and alive:
                attacks += 1
                require(int(v['ready'])==1, 'attack without readiness')
        require(targets and ready and attacks, f'no actual ready target/fire local {local}')
        require(dead and deaths and respawns, f'no death/respawn local {local}')
        # Reacquisition after a real death must come from a fresh living decision.
        require(any(t>first_dead and int(v['alive']) and int(v['target'])>=0 for t,v in sequence), 'no reacquisition after death')
        p = next(p for p in telemetry['players'] if p['player']==local+1)
        require(p['samples']>=600 and p['fireOnSamples'] and p['fireOffSamples'] and p['maximumFrags']>0, 'actual action/frag evidence')
        records.append(dict(local=local,self=local+1,decisions=len(sequence),targets=sorted(targets),ready=ready,
                            attacks=attacks,deadDecisions=dead,deaths=deaths,respawns=respawns,noTargetDecisions=no_target,
                            samples=p['samples'],maximumFrags=p['maximumFrags']))
    pulses = []
    for (slot,tick),w in sorted(weapons.items()):
        desired,group,bits = int(w['desired']),int(w['group']),int(w['buttons'])
        require(1<=desired<=14 and group==GROUPS[desired], 'native group mapping')
        require(bits in (0,group<<14), 'partial/incorrect emitted weapon group')
        if not bits: continue
        emitted_groups.add(group)
        settled = any(s==slot and tick<t<=tick+100 and int(v['desired'])==desired and
                      int(v['wanted'])==desired and int(v['current'])==desired for (s,t),v in weapons.items())
        echoed = any((snapshots.get((t,slot+1),0)>>14)&31 == group for t in range(tick,tick+21))
        pulses.append(dict(local=slot,tick=tick,desired=desired,group=group,settled=settled,nativeEcho=echoed))
    require(pulses and any(p['settled'] and p['nativeEcho'] for p in pulses), 'no emitted native weapon pulse acknowledged and settled')
    kills = [line for line in observer.splitlines() if 'TSE_Bot_PoC_' in line and 'poured lead into' in line]
    require(len(kills)>=3, 'missing independent vanilla observer kill witnesses')
    return dict(passed=True,sha256=digest,nativeSeconds=result['elapsedSeconds'],crcAcceptedCount=result['crcAcceptedCount'],
                players=records,matchedWeaponGroups=sorted(matched_groups),emittedWeaponGroups=sorted(emitted_groups),
                identities=identities,
                nativeRangedWeaponFamiliesExercised=any(g in (3,4,6,7) for g in matched_groups),
                selectionPulses=pulses,observerKills=kills,restoredFiles=len(diagnostics['restored']),
                scope='Stock deathmatch, 2 local bots + vanilla observer; QA permits siblings; all group mappings covered by pure tests; native family coverage is reported, not inferred; bounded run, not hour/navigation qualification')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('root',type=Path)
    parser.add_argument('--dll',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    data=audit(args.root,args.dll)
    args.output.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('AUTO COMBAT EVIDENCE PASS:',args.output)
