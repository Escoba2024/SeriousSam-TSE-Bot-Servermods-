"""Fixed existing-Dedicated OFF/ON evidence contract. No process/native calls."""
import os
import re
from pathlib import Path

DEDICATED_SHA='fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0'
BOT_SHA='ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530'
ORIGINAL_SHA='1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'
FIELDS=('invisibility','invulnerability','damage','speed','bomb','unknown')


def checked_flag(flag):
 if type(flag)is not int or flag not in(0,1):raise ValueError('fixed typed flag0/1 required')
 return flag


def options(map_key,duration,diag,flag):
 checked_flag(flag)
 if map_key!='redstation'or type(duration)not in(int,float)or duration!=600 or type(diag)is not int or diag!=0:
  raise ValueError('powerup contrast requires RedStation600s diagnostics0')


def game_sha(role):
 if role in('botA','botB'):return BOT_SHA
 if role=='server':return DEDICATED_SHA
 if role=='vanilla':return ORIGINAL_SHA
 raise ValueError('unknown game module role')


def archive_log(path,raw):
 """Preserve the actual existing read before any new predicate can reject it."""
 with os.fdopen(os.open(Path(path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as output:output.write(raw)


def census(raw,flag):
 checked_flag(flag)
 rows=[line for line in raw.splitlines()if '[DevPowerups]'in line]
 if len(rows)!=3:raise ValueError('one complete unambiguous powerup invocation required')
 pattern=r'\[DevPowerups\] enabled=([01]) phase=(before|after) '+' '.join(k+r'=(\d+)'for k in FIELDS)
 before=re.fullmatch(pattern,rows[0]);removed=re.fullmatch(r'\[DevPowerups\] removed=(\d+)',rows[1]);after=re.fullmatch(pattern,rows[2])
 if not before or not removed or not after:raise ValueError('malformed/negative/reordered powerup census')
 if before[2]!='before'or after[2]!='after'or int(before[1])!=flag or int(after[1])!=flag:
  raise ValueError('effective invocation flag/phase differs')
 b=dict(zip(FIELDS,map(int,before.groups()[2:])));a=dict(zip(FIELDS,map(int,after.groups()[2:])));n=int(removed[1]);affected=b['invisibility']+b['damage']
 if affected==0:raise ValueError('uninformative contrast: no affected map items')
 expected=dict(b)
 if flag:expected.update(invisibility=0,damage=0)
 if a!=expected or n!=(affected if flag else 0):raise ValueError('powerup removal/count preservation differs')
 return dict(flag=flag,before=b,after=a,removed=n,affected_before=affected,
             effective_startup_contrast_observed=True,crc_cause_proven=False,
             later_spawn_filter_proven=False)
