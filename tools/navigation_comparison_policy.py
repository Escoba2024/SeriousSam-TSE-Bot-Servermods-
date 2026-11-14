"""Closed candidate and profile contracts for the fixed Red Station comparison."""
import re

CANDIDATES = {
 '048': dict(directory='/srv/tse-cecil-full-build-048-20261109',
             manifest_sha256='6df71192b0654667740effc7e80e93e8dc0b2775597d0911e0516ee3e56704cf',
             source_commit='4d04ab4ad190a0f6cd078d96f5416e0eea9e1da0',
             dll_sha256='ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530'),
 '018': dict(directory='/srv/tse-milestone-a-build-018-20261112',
             manifest_sha256='f4212443317b58b04808bd42d084e6a3286e458af2c0dbcfb276aa3bca931c2e',
             source_commit='1802fb3f0720b53feb032abfe2c2a83407bfea6e',
             dll_sha256='6db89204e33dc7d76ecdfed68055d2b75bde4950475793a57101fd0cefcb8e4a'),
 '020': dict(directory='/srv/tse-milestone-a-build-020-20261114',
             manifest_sha256='3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6',
             source_commit='e5f7a65502fbea683014ef8fcc95ecdd2a927b6a',
             dll_sha256='094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0'),
}


def candidate(build):
 if build not in CANDIDATES: raise ValueError('unreviewed comparison candidate')
 return CANDIDATES[build]


def options(map_key, duration, diag, build):
 candidate(build)
 if map_key != 'redstation' or type(duration) not in (int,float) or duration != 600 or type(diag) is not int or diag != 0:
  raise ValueError('comparison requires RedStation600s diagnostics0')


def check_tiers(logs, build):
 candidate(build)
 if set(logs) != {'botA','botB'}: raise ValueError('both actual botgroups required')
 expected=('BOT-Expert-Rifle','5','marksman') if build=='048' else ('DEMON','3','duelist')
 suffix='' if build=='048' else r' model=arena-v1'
 pattern=r'\[BotHuman\] local=([0-3]) profile=(\S+) tier=(\d+) persona=(\S+) seed=(\d+)'+suffix
 receipts={}
 for role,text in logs.items():
  rows=[]
  for line in text.splitlines():
   if not line.startswith('[BotHuman]'):continue
   if re.search(r'fallback|rejected',line,re.I):raise ValueError('profile fallback forbidden')
   # Periodic tick rows are distinct from actual profile-attachment receipts.
   if ' tier=' not in line and ' tick=' in line:continue
   match=re.fullmatch(pattern,line)
   if not match or match.groups()[1:4]!=expected or not 0<int(match[5])<=0xffffffff:
    raise ValueError('wrong or malformed version-bound profile receipt')
   local,name,tier,persona,seed=match.groups()
   rows.append(dict(local=int(local),profile=name,tier=int(tier),persona=persona,seed=int(seed)))
  if not rows or {r['local']for r in rows}!=set(range(4)):raise ValueError('all four actual locals required')
  receipts[role]=rows
 return receipts
