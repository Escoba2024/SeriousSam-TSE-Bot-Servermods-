#!/usr/bin/env python3
"""Count native English Retail death messages, never infer shots from input.

Use ONE complete server log/generation, not concatenated client mirrors.
Unknown players are counted only as counterparts; their names are not exported.
frag_delta is the rule-derived delta, to compare with independent native queries.
"""
import argparse
import json
from pathlib import Path
import re

DECORATION = re.compile(r'\^c[0-9a-fA-F]{6}|\^f[0-9]|\^[bBiIrRoOF]')
KILLS = [(r'(.+) poured lead into (.+)', 'bullet'),
         (r'(.+) blew (.+) away', 'explosive'),
         (r'(.+) smashed (.+) with a cannon', 'cannon'),
         (r'(.+) cut (.+) into pieces', 'melee'),
         (r'(.+) telefragged (.+)', 'telefrag'),
         (r'(.+) nuked (.+)', 'cannon_explosion'),
         (r'(.+) killed (.+)', 'other')]
SELF = ('drowned', 'burst into flames', 'fell into a spike-hole', 'has frozen',
        'dissolved', 'blew himself away', 'has committed suicide')
WORLD = ('was pierced', 'was squashed', 'went over the edge', 'swashed',
         'stood in the sun for too long', 'passed away', 'is missing in action',
         'was telefragged')


def visible(text):
    return DECORATION.sub('', text)


def analyze(log, roster):
    names = {visible(name).casefold(): ident for ident, name in roster.items()}
    if len(names) != len(roster) or not all(names):
        raise ValueError('unique nonempty visible names required')
    players = {ident: dict(kills=0, deaths=0, suicides=0, world_deaths=0,
                          frag_delta=0, kill_types={}) for ident in roster}
    sessions = {ident: dict(epoch=0,observed_join=False,active=False,
                           stats=dict(kills=0,deaths=0,suicides=0,world_deaths=0,frag_delta=0,kill_types={}))
                for ident in roster}
    events = 0;bot_kills=0
    for raw in log.splitlines():
        line = visible(raw.strip())
        if line.endswith(' joined'):
            ident=names.get(line[:-7].casefold())
            if ident is not None:
                s=sessions[ident];s['epoch']+=1;s['observed_join']=s['active']=True
                s['stats']=dict(kills=0,deaths=0,suicides=0,world_deaths=0,frag_delta=0,kill_types={})
            continue
        if line.endswith(' left'):
            ident=names.get(line[:-5].casefold())
            if ident is not None:sessions[ident]['active']=False
            continue
        matched = False
        for suffix, key in [(s, 'suicides') for s in SELF] + [(s, 'world_deaths') for s in WORLD]:
            if not line.endswith(' ' + suffix): continue
            ident = names.get(line[:-len(suffix)-1].casefold())
            if ident is None: continue
            for p in (players[ident],sessions[ident]['stats']):
                p['deaths'] += 1;p[key] += 1;p['frag_delta'] -= 1
            events += 1; matched = True; break
        if matched: continue
        for pattern, kind in KILLS:
            m = re.fullmatch(pattern, line)
            if not m: continue
            killer, victim = (names.get(n.casefold()) for n in m.groups())
            # An unrecognized counterpart may be a real human. No identity export.
            # Reject suffixes/log prose by requiring one exact known endpoint.
            if killer is None and victim is None: continue
            if killer is not None and killer==victim:continue
            if killer is not None and victim is None and not raw.startswith('^o'):
                # Plain fixtures/exports are accepted only for a simple counterpart.
                if not re.fullmatch(r'[A-Za-z0-9_.\[\]-]+', m[2]): continue
            if killer is not None:
                for p in (players[killer],sessions[killer]['stats']):
                    p['kills'] += 1;p['frag_delta'] += 1
                    p['kill_types'][kind] = p['kill_types'].get(kind, 0) + 1
            if victim is not None:
                players[victim]['deaths'] += 1;sessions[victim]['stats']['deaths'] += 1
            if killer is not None and victim is not None:bot_kills+=1
            events += 1; matched = True; break
    return dict(players=players,current_sessions=sessions,bot_vs_bot_kills=bot_kills,
                recognized_deaths=events, shots=None, hits=None,
                damage=None, hit_accuracy=None,
                evidence='native_death_messages; verify frag_delta against queries')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('log', type=Path)
    p.add_argument('roster', type=Path, help='private JSON object: stable ID -> name')
    args = p.parse_args()
    print(json.dumps(analyze(args.log.read_text(errors='replace'),
                             json.loads(args.roster.read_text())), indent=2))


if __name__ == '__main__': main()
