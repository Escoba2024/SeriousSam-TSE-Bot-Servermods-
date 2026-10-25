"""Explicit Red Station configuration for fresh owned overlays; no binary patch."""
import random
import re
VALUES={'gam_iStartDifficulty':2,'gam_bInfiniteAmmo':1,'gam_iBlood':3,'gam_bGibs':0}
def symbols(source):
 for key,value in VALUES.items():
  source,count=re.subn(r'('+key+r'=\(INDEX\))-?\d+;',lambda m:m[1]+str(value)+';',source)
  if count!=1:raise ValueError('missing/ambiguous native symbol: '+key)
 return source
def server_begin():
 return ('gam_strSessionName="ssam.ai | Red Station | Human Bots";\n'
         'gam_ctMaxPlayers=16;\ngam_iStartMode=2;\ngam_iStartDifficulty=2;\n'
         'ded_strLevel="Levels\\\\LevelsMP\\\\Deathmatch\\\\RedStation.wld";\n'
         'gam_iFragLimit=0;\ngam_iTimeLimit=0;\ngam_bInfiniteAmmo=1;\ngam_iBlood=3;\ngam_bGibs=0;\n')
MOTD = "Welcome to ssam.ai | TSE Classic 1.07 | RED STATION | #SamIsBack | Play fair and have fun!"
ANNOUNCEMENT = "[ssam.ai] RED STATION - classic 1.07 deathmatch. Respect other players. #SamIsBack"

def server_startup(base):
 """Append retail console commands only for the dedicated server overlay."""
 if 'tmp_ai[9]' in base:
  raise ValueError('duplicate ssam.ai announcement installation')
 # The clock is in seconds, and the slot-based guard avoids per-tick chat spam.
 # Reset on a new match (tick < 1) to permit announcements on next rotation.
 shell = ('if(cmd_tmTick<1){tmp_ai[9]=-1;}'
          'if((INDEX)cmd_tmTick>=300 && '
          '((INDEX)cmd_tmTick/(INDEX)300)!=tmp_ai[9]){'
          'tmp_ai[9]=(INDEX)cmd_tmTick/(INDEX)300;'
          'Say(\\\"'+ANNOUNCEMENT+'\\\");}\\n')
 return (base+'\nser_strMOTD="'+MOTD+'";\n'
         'tmp_ai[9]=(INDEX)-1;\n'
         'cmd_cmdOnTick=cmd_cmdOnTick+"'+shell+'";\n')

def roster(identities,seed):
 if type(seed) is not int or not isinstance(identities,list) or len(identities)<8:raise ValueError('seed and at least eight identities required')
 names=[];seen=set()
 for who in identities:
  n=who.get('nickname');rgb=who.get('color')
  if not isinstance(n,str) or not re.fullmatch(r'[A-Za-z0-9 ._\[\]-]{1,18}',n) or n!=n.strip() or not any(c.isalnum() for c in n):raise ValueError('unsafe native nickname')
  if n.casefold() in seen:raise ValueError('duplicate native nickname')
  if not isinstance(rgb,str) or not re.fullmatch(r'[0-9a-fA-F]{6}',rgb):raise ValueError('invalid native color')
  seen.add(n.casefold());names.append('BOT-^c'+rgb.upper()+n+'^r')
 return random.Random(seed).sample(names,8)
def configure_overlay(game,role):
 if not game.is_mount():raise RuntimeError('fresh overlay required')
 p=game/'Scripts/PersistentSymbols.ini';p.write_text(symbols(p.read_text()))
 if role=='server':
  (game/'Scripts/Dedicated/BotTest/1_begin.ini').write_text(server_begin())
  startup=game/'Scripts/Dedicated_startup.ini'
  startup.write_text(server_startup(startup.read_text()))
