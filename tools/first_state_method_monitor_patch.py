"""Exact input-free method-monitor delta; old preparation monitor untouched."""
import hashlib

RUNNER_SHA='609e998870bc49c30fc27fe053c254f955536d4227783897a8bca339a9f15d16'
HELPER_SHA='6ec98fa31f2280285a0fb41d0afc5bf0b51e9efe2ba005efb3642aba32e131e2'
PERIODIC=""" def periodic():
  nonlocal last_host,last_query
  now=time.monotonic()
  if now-last_host>=1:
   host('window')
   for r in P.ROLES:
    text=(R/r/('Dedicated_BotTest.log'if r=='server'else'SeriousSam.log')).read_text(errors='replace')
    assert not BAD.search(text),'runtime log failure:'+r
   for r in P.ROLES:own_identity(r)
   for n in (154,155):display_guard(n)
   for r,wid in method_windows.items():assert window(r)==wid,'own window identity changed'
   if collector is not None:collector.drain()
   last_host=now
  if now-last_query>=1:query(2);last_query=now
  sample()
"""
METHOD_PERIODIC=PERIODIC.replace(' def periodic():',' def method_periodic():',1).replace('  sample()\n','',1)
COVERAGE=" report['native_summary_scope']='JOIN_PREARM_ONLY';report['active_inventory_geometry_fixed_life_qualified']=False;report['new_matched_control_required']=True\n"
CHANGES=[("PREFIX='ssam-a1-first-state-getter-boundary-disabled-20261115'","PREFIX='ssam-a1-first-state-method-monitor-disabled-20261115'"),
 ("E=BASE/('a1-first-state-getter-boundary-disabled-'+arm+'-'","E=BASE/('a1-first-state-method-monitor-disabled-'+arm+'-'"),
 (PERIODIC,PERIODIC+METHOD_PERIODIC),('unit=unit,periodic=periodic,save=save,','unit=unit,periodic=method_periodic,save=save,'),
 (' def save():',COVERAGE+' def save():')]
OLD_COMMENT='self.periodic()  # unchanged owned host/query/paired inventory guards'
NEW_COMMENT='self.periodic()  # dedicated input-free host/roster monitor; no active legacy inventory'


def digest(text):return hashlib.sha256(text.encode()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)
def apply(text,pairs):
    for old,new in pairs:
        require(text.count(old)==1,'exact monitor source anchor differs');text=text.replace(old,new,1)
    return text
def patch_runner(text):
    require(digest(text)==RUNNER_SHA,'immutable runner pin differs');return apply(text,CHANGES)
def reverse_runner(text):
    result=apply(text,[(new,old)for old,new in reversed(CHANGES)])
    require(digest(result)==RUNNER_SHA,'entire method-monitor runner inverse differs');return result
def patch_helper(text):
    require(digest(text)==HELPER_SHA,'immutable MethodWindow helper differs');return apply(text,[(OLD_COMMENT,NEW_COMMENT)])
def reverse_helper(text):
    result=apply(text,[(NEW_COMMENT,OLD_COMMENT)]);require(digest(result)==HELPER_SHA,'entire helper inverse differs');return result
