#!/usr/bin/env python3
"""Summarize sampled native observations; never grant gameplay/M2 acceptance.

BotWeapon.ammo is the Colt magazine, even when another weapon is current.
Input counters are not shots. Alive after death needs roster/session correlation
before it can establish respawn. Raw logs remain private.
"""
import argparse
import json
import math
from pathlib import Path
import re

SNAPSHOT=re.compile(r'\[BotSnapshot\] tick=(\d+) player=(\d+) entity=(\d+) pos=\(([^)]+)\) yaw=(\S+) health=(\S+) buttons=(\d+) \\frags_(\d+)\\(-?\d+)$')
WEAPON=re.compile(r'\[BotWeapon\] tick=(\d+) .*? weapon=(\d+) wanted=(\d+) available=(\d+) ammo=(-?\d+) firing=(\d+)')

def analyze(text):
    result=dict(full_m2_acceptance=False,incomplete_final_line=bool(text and not text.endswith('\n')),
                actors={},emitted_fire_input_max=0,sampled_colt_clip_decrease=0,
                observed_current_weapons=[],nonmonotonic_samples=0,invalid_samples=0)
    actors={};previous_weapon=None;weapons=set()
    lines=text.splitlines()
    if result['incomplete_final_line']:lines=lines[:-1]
    for line in lines:
        fire=re.search(r'\[BotDriver\].* combat_fire_actions=(\d+)',line)
        if fire:result['emitted_fire_input_max']=max(result['emitted_fire_input_max'],int(fire[1]))
        match=SNAPSHOT.search(line)
        if match:
            tick,slot,entity=int(match[1]),match[2],int(match[3])
            try:values=[float(v) for v in match[4].split(',')]+[float(match[5]),float(match[6])]
            except ValueError:result['invalid_samples']+=1;actors.pop(slot,None);continue
            if len(values)!=5 or not all(math.isfinite(v) for v in values) or match[2]!=match[8]:
                result['invalid_samples']+=1;actors.pop(slot,None);continue
            health=values[-1];frags=int(match[9]);old=actors.get(slot)
            summary=result['actors'].setdefault(slot,dict(samples=0,observed_health_loss=0.0,
                deaths=0,alive_after_death=0,frag_increments=0,entity_changes=0,min_health=health,max_health=health))
            summary['samples']+=1;summary['min_health']=min(summary['min_health'],health);summary['max_health']=max(summary['max_health'],health)
            if old and tick<=old['tick']:
                result['nonmonotonic_samples']+=1;old=None
            if old:
                if old['health']<=0<health:summary['alive_after_death']+=1
                if old['entity']==entity:
                    summary['observed_health_loss']+=max(0,old['health']-health)
                    summary['deaths']+=int(old['health']>0>=health)
                    summary['frag_increments']+=max(0,frags-old['frags'])
                else:summary['entity_changes']+=1
            actors[slot]=dict(tick=tick,entity=entity,health=health,frags=frags)
        elif '[BotSnapshot]' in line:
            result['invalid_samples']+=1;actors.clear()
        match=WEAPON.search(line)
        if match:
            tick,weapon,ammo=int(match[1]),int(match[2]),int(match[5]);weapons.add(weapon)
            if previous_weapon and tick<=previous_weapon[0]:
                result['nonmonotonic_samples']+=1;previous_weapon=None
            if previous_weapon and weapon==previous_weapon[1]==2 and 0<=ammo<=6 and 0<=previous_weapon[2]<=6:
                result['sampled_colt_clip_decrease']+=max(0,previous_weapon[2]-ammo)
            previous_weapon=(tick,weapon,ammo)
    result['observed_current_weapons']=sorted(weapons)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('log',type=Path)
    args=parser.parse_args();print(json.dumps(analyze(args.log.read_text(errors='replace')),indent=2))
