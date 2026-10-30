"""Original private Retail duel scene; no game memory or binary changes."""
from pathlib import Path
import re

LEVEL=r'Levels\\LevelsMP\\Deathmatch\\DM_LittleTrouble.wld'

def symbols(source):
    result,count=re.subn(r'(gam_bInfiniteAmmo=\(INDEX\))-?\d+;',r'\g<1>0;',source)
    if count!=1:raise ValueError('missing/ambiguous original infinite-ammo symbol')
    return result

def server_begin():
    return ('gam_strSessionName="M2 private combat QA";\ngam_ctMaxPlayers=16;\n'
            'gam_iStartMode=2;\ngam_iStartDifficulty=2;\n'
            'ded_strLevel="'+LEVEL+'";\n'
            'gam_iFragLimit=0;\ngam_iTimeLimit=0;\ngam_bInfiniteAmmo=0;\n')

def controls_for_probe(source):
    # Preserve the engine's original Pressed/Released statements. Only ordinary
    # per-user bindings change in the original test opponent's private copy.
    mapping={'ctl_bMoveForward':'W','ctl_bMoveBackward':'S',
             'ctl_bTurnLeft':'Arrow Left','ctl_bTurnRight':'Arrow Right',
             'ctl_bTurnUp':'Arrow Up','ctl_bTurnDown':'Arrow Down',
             'ctl_bMoveLeft':'A','ctl_bMoveRight':'D'}
    blocks=re.split(r'(?m)^Button\s*\n',source);counts={key:0 for key in mapping}
    for i,part in enumerate(blocks):
        for command,key in mapping.items():
            if not re.search(r'Pressed:\s*'+re.escape(command)+r'\s*=\s*1;',part):continue
            counts[command]+=1
            for which,value in [('Key1',key if counts[command]==1 else 'None'),('Key2','None')]:
                part,n=re.subn(r'(?m)^(\s*'+which+r':\s*)[^\n]+$',lambda m:m[1]+value,part)
                if n!=1:raise ValueError('unrecognized control binding block')
        blocks[i]=part
    if any(n not in ((1,2) if cmd in ('ctl_bMoveLeft','ctl_bMoveRight') else (1,)) for cmd,n in counts.items()):
        raise ValueError('missing/duplicate original control action')
    result='Button\n'.join(blocks)
    for key in ('Arrow Left','Arrow Right','Arrow Up','Arrow Down'):
        if len(re.findall(r'(?m)^\s*Key[12]:\s*'+key+r'\s*$',result))!=1:
            raise ValueError('ambiguous reserved probe key')
    return result

def keyboard_look(source):
    # X11 focus/pointer placement must not add unintended mouse camera motion
    # to a keyboard calibration. Only our original opponent's copied controls.
    for axis,mouse in (('look u/d','mouse Y'),('turn l/r','mouse X')):
        source,count=re.subn(r'(?m)^(Axis "'+axis+r'" )"'+mouse+r'"',r'\g<1>"None"',source)
        if count!=1:raise ValueError('missing/ambiguous original mouse look axis')
    return source

def configure_overlay(game,role):
    game=Path(game)
    if (not game.is_mount() or game.parent.parent!=Path('/srv') or
        not game.parent.name.startswith('tse-session-qualification-m2-')):
        raise RuntimeError('fresh owned private M2 overlay required')
    path=game/'Scripts/PersistentSymbols.ini';path.write_text(symbols(path.read_text()))
    if role=='server':
        (game/'Scripts/Dedicated/BotTest/1_begin.ini').write_text(server_begin())
    elif role=='vanilla':
        path=game/'Controls/Controls0.ctl';path.write_text(keyboard_look(controls_for_probe(path.read_text())))
        # Ordinary graphics/input settings on our own original opponent, not a
        # workload limit change. Its renderer remains subject to the host guard.
        path=game/'Scripts/Session.ini';path.write_text(
            'sam_iMaxFPSActive=20;\nsam_iMaxFPSInactive=20;\nsam_bPauseOnMinimize=0;\n')
        path=game/'Scripts/PersistentSymbols.ini';text=path.read_text()
        for key,value in [('sam_iScreenSizeI',320),('sam_iScreenSizeJ',240),
                          ('sam_iMaxFPSActive',20),('sam_iMaxFPSInactive',20)]:
            text,n=re.subn(r'('+key+r'=\(INDEX\))\d+;',lambda m:m[1]+str(value)+';',text)
            if n!=1:raise ValueError('unrecognized original observer settings')
        path.write_text(text)
