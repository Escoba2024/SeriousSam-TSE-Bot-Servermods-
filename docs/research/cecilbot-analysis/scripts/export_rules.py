#!/usr/bin/env python3
"""GPL-2.0-only. Export original Cecil weapon rules, no game side effects."""
import argparse,csv,json,re
from pathlib import Path
PIN='953b477e53fdc5a5d84c8ae8d759c84fdf6c973c'
def extract(reference):
 src=(reference/'Sources/Bots/Logic/BotWeapons.cpp').read_text()
 rows=[]
 for mode,body in re.findall(r'_abw(\w+)Weapons\[CT_BOT_WEAPONS\] = \{(.*?)\n\};',src,re.S):
  for order,(vals,num) in enumerate(re.findall(r'\{\s*(WEAPON_[^}]+)\}, // (\d+)',body)):
   v=[x.strip() for x in vals.split(',')]
   row=dict(mode=mode,table_order=order,weapon=v[0],weapon_id=int(num))
   for k,x in zip(['min_distance','max_distance','damage_rating','accuracy','strafe','special','shot_frequency'],v[1:]):
    row[k]=float({'NO_SPEC':'0','NO_FREQ':'-1'}.get(x,x).rstrip('f'))
   row['source_literals']=','.join(v);rows.append(row)
 if len(rows)!=30 or {r['mode'] for r in rows}!={'Deathmatch','Cooperative'}:raise ValueError('Expected two pinned 15-row tables')
 for mode in ('Deathmatch','Cooperative'):
  if {r['weapon_id'] for r in rows if r['mode']==mode}!=set(range(15)):raise ValueError('Weapon IDs incomplete')
 return rows
def main():
 p=argparse.ArgumentParser();p.add_argument('reference',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
 rows=extract(a.reference)
 a.output.mkdir(parents=True,exist_ok=False)
 obj=dict(source_commit=PIN,source_path='Sources/Bots/Logic/BotWeapons.cpp',semantics='Damage values are AI scoring constants, not verified game damage. Table order is not selection priority: BotWeapons compares scores.',rows=rows)
 (a.output/'weapons.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
 with (a.output/'weapons.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('Exported 30 weapon rows')
if __name__=='__main__':main()
