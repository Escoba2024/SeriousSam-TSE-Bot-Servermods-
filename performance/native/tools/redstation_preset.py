"""Explicit Red Station configuration for fresh owned overlays; no binary patch."""
import random
import re
from gaming_names import validate_native
VALUES={'gam_iStartDifficulty':2,'gam_bInfiniteAmmo':1,'gam_iBlood':3,'gam_bGibs':0}
def symbols(source):
 for key,value in VALUES.items():
  source,count=re.subn(r'('+key+r'=\(INDEX\))-?\d+;',lambda m:m[1]+str(value)+';',source)
  if count!=1:raise ValueError('missing/ambiguous native symbol: '+key)
 return source
def server_begin():
 return ('gam_strSessionName="Alpha-Gaming | Red Station | Human Bots";\n'
         'gam_ctMaxPlayers=16;\ngam_iStartMode=2;\ngam_iStartDifficulty=2;\n'
         'ded_strLevel="Levels\\\\LevelsMP\\\\Deathmatch\\\\RedStation.wld";\n'
         'gam_iFragLimit=0;\ngam_iTimeLimit=0;\ngam_bInfiniteAmmo=1;\ngam_iBlood=3;\ngam_bGibs=0;\n')
def roster(identities,seed):
 if type(seed) is not int or not isinstance(identities,list) or len(identities)<8:raise ValueError('seed and at least eight identities required')
 names=[];seen=set()
 for who in identities:
  n=who.get('nickname');rgb=who.get('color')
  if not isinstance(n,str) or not re.fullmatch(r'[A-Za-z0-9 ._\[\]-]{1,22}',n) or n!=n.strip() or not any(c.isalnum() for c in n):raise ValueError('unsafe native nickname')
  if n.casefold() in seen:raise ValueError('duplicate native nickname')
  if 'native_name' in who:
   native=who['native_name']
   if validate_native(native)!=n:raise ValueError('native and visible identity differ')
  else:
   if not isinstance(rgb,str) or not re.fullmatch(r'[0-9a-fA-F]{6}',rgb):raise ValueError('invalid native color')
   native='^c'+rgb.upper()+n+'^r';validate_native(native)
  seen.add(n.casefold());names.append(native)
 return random.Random(seed).sample(names,8)
def configure_overlay(game,role):
 if not game.is_mount():raise RuntimeError('fresh overlay required')
 p=game/'Scripts/PersistentSymbols.ini';p.write_text(symbols(p.read_text()))
 if role=='server':(game/'Scripts/Dedicated/BotTest/1_begin.ini').write_text(server_begin())
