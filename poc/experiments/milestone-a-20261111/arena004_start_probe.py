from pathlib import Path
import contextlib,fcntl,hashlib,importlib.util,json,os,re,shutil,signal,subprocess,sys,time,datetime
BASE=Path('/srv/tse-milestone-a-evidence-20261111');R=Path('/srv/tse-arena-isolated-20261111');PORT=27850;DISPLAY=':154';DIAG=int(sys.argv[3]);assert DIAG in (0,1);SWAP=int(sys.argv[4]);assert SWAP in (0,1);PREFIX=f'ssam-arena004-early-swap{SWAP}-20261111'
def imp(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
safe=imp('safe','/srv/tse-cecil-gate8-20261109/native048_safe.py');probe=imp('probe',BASE/'session-readonly.py');pauseprobe=imp('pauseprobe','/srv/tse-milestone-a-20261111/tools/probe_retail_pause.py');B=safe.RuntimeBackend(R,PORT)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(value,duration,trial):
 assert trial in (1,2,3)
 E=BASE/f'arena004-early-swap{SWAP}-trial-{trial}-{time.strftime("%H%M%S",time.gmtime())}';E.mkdir();records={};display=None;server=None;cohort=False;bootstrap_original=None
 report={'status':'IN_PROGRESS','spawn':value,'trial':trial,'candidate_tier':trial,'diagnostics_enabled':bool(DIAG),'qualified':False,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'events':[],'errors':[],'swap_cohorts':bool(SWAP)}
 def save():(E/'result.json').write_text(json.dumps(report,indent=2))
 def emit(event,**kw):report['events'].append({'event':event,'elapsed_wall':time.time(),'details':kw});save();print(event,json.dumps(kw),flush=True)
 def unit(role):return PREFIX+'-'+role.lower()+'.service'
 def launch(role):
  nonlocal server
  assert B.pid(unit(role))==0 and B.empty(unit(role));B.quiescent(R/role);records[role]={'identity':None,'closed':False}
  args=['systemd-run','--collect','--unit',unit(role),'--property','PrivateNetwork=yes','--property','User=nobody','--property','Group=nogroup','--property','WorkingDirectory='+str(R/role),'--property','NoNewPrivileges=yes','--property','KillMode=none','--property','SendSIGKILL=no']
  if role!='server':args+=['--property','JoinsNamespaceOf='+unit('server')]
  subprocess.run(args+['/bin/bash',str(R/('launch-'+role+'.sh'))],check=True)
  B.wait(lambda:B.ready(role,unit(role)),45,'own role not ready '+role);identity=B.identity(role,unit(role));records[role]['identity']=identity
  B.wait(lambda:str(R/role/'Bin/GameMP.dll') in (Path('/proc')/str(identity[0])/'maps').read_text(),25,'module absent')
  game=R/role/'Bin/GameMP.dll';st=game.stat();mapped=[r.split() for r in (Path('/proc')/str(identity[0])/'maps').read_text().splitlines() if str(game) in r];assert mapped and all(int(r[4])==st.st_ino and r[-1]==str(game) for r in mapped)
  assert sha(R/role/'Bin/Engine.dll')==probe.ENGINE_SHA and sha(R/role/'Bin/EntitiesMP.dll')=='7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350'
  expected={'server':'1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208','botA':('43908fa08d7cb40c058fd03d455797feae8b40c9be4cf94667aa9ee179b14310' if cohort and SWAP else safe.DLL),'botB':(safe.DLL if SWAP else '43908fa08d7cb40c058fd03d455797feae8b40c9be4cf94667aa9ee179b14310'),'vanilla':'1c41da35b3fc47378c407b770e1bd1dcc2b7e6bf676c140586bc6035461d4208'}[role];assert sha(game)==expected
  if role=='server':server=identity;B.isolated_server(identity[0])
  else:B.same_namespace(identity[0],server[0])
  emit('launched',role=role,identity=identity,game_sha256=expected)
  return identity
 def count(n):B.wait(lambda:B.query(server[0]).get('numplayers')==str(n),100,'count not reached '+str(n))
 def close(role):
  record=records.get(role)
  if not record or record['closed']:return
  identity=record['identity'];assert identity and B.identity(role,unit(role))==identity
  if role=='server':os.kill(identity[0],signal.SIGINT)
  else:assert B.scope['close_window'](identity[0],DISPLAY)>0
  B.wait(lambda:not B.same(identity),35,'normal close timed out');B.wait(lambda:B.empty(unit(role)),30,'own helpers remain');record['closed']=True;emit('closed',role=role)
 def control(kind,val,seconds):
  identity=records['vanilla']['identity'];assert B.identity('vanilla',unit('vanilla'))==identity
  subprocess.run(['python3',str(BASE/'control-pause.py'),'--result',str(E/'control-state.json'),'--'+kind,str(val),'--seconds',str(seconds)],stdout=subprocess.DEVNULL,check=True,timeout=15)
 with (R/'runtime.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   assert shutil.disk_usage('/srv').free>8*2**30
   available=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:')))*1024;assert available>2*2**30,'need measured RAM headroom before9-player probe'
   for role in ('server','botA','botB','vanilla'):B.quiescent(R/role)
   assert not Path('/tmp/.X11-unix/X154').exists() and B.pid(PREFIX+'-display.service')==0
   config=R/'server/Scripts/Dedicated/BotTest/1_begin.ini';text=config.read_text().replace('dev_bRemoveDamageAndInvisibility=1;','');text=re.sub(r'\ngam_tmSpawnInvulnerability=.*?;','',text);config.write_text(text+f'\ngam_tmSpawnInvulnerability=(FLOAT){value};\nser_bClientsMayPause=1;\n')
   startup=R/'server/Scripts/Dedicated_startup.ini';text=startup.read_text().replace('net_iPort=27650','net_iPort=27850').replace('ser_bHeartbeatGameSpy=0','ser_bHeartbeatGameSpy=1').replace('master.333networks.com','127.0.0.1').replace('ser_bEnumeration=0','ser_bEnumeration=1');startup.write_text(text)
   sys.path.insert(0,'/srv/tse-milestone-a-20261111/tools');from qualify_integrated_wine import configure_count;configure_count(R/'botA',1)
   subprocess.run(['systemd-run','--collect','--unit',PREFIX+'-display.service','--property','User=nobody','--property','Group=nogroup','/usr/bin/Xvfb',DISPLAY,'-screen','0','800x600x24','-nolisten','tcp'],check=True)
   B.wait(lambda:Path('/tmp/.X11-unix/X154').exists(),15,'display unavailable');pid=B.pid(PREFIX+'-display.service');display=(pid,int((Path('/proc')/str(pid)/'stat').read_text().split(') ',1)[1].split()[19]));assert int(Path('/tmp/.X154-lock').read_text())==pid
   # Immutable binaries staged only into our quiescent copies.
   shutil.copy2('/srv/tse-cecil-full-build-048-20261109/Sources/Game/GameMP.dll',R/'botA/Bin/GameMP.dll')
   shutil.copy2('/srv/tse-milestone-a-build-004-20261111/Sources/Game/GameMP.dll',R/'botB/Bin/GameMP.dll')
   shutil.copy2(R/'vanilla/Bin/GameMP.dll',R/'server/Bin/GameMP.dll')
   cfg=R/'botB/Scripts/Integrated.ini';raw=cfg.read_text();raw=re.sub(r'bot_bDiagnostics=\d+;',f'bot_bDiagnostics={DIAG};',raw);raw=re.sub(r'\nbot_iArenaTier=.*?;','',raw);cfg.write_text(raw+f'\nbot_iArenaTier={trial};\n')
   for file in [R/'botA/Bin/GameMP.dll',R/'botB/Bin/GameMP.dll',R/'server/Bin/GameMP.dll']:os.chown(file,65534,65534)
   bootstrap_cfg=R/'botA/Scripts/Integrated.ini';bootstrap_original=bootstrap_cfg.read_bytes();bootstrap=bootstrap_original.decode();bootstrap=re.sub(r'bot_(bAutoCombat|bHumanAI|bSupplyNavigation)=\d+;',lambda m:'bot_'+m[1]+'=0;',bootstrap);bootstrap=re.sub(r'\nbot_iArenaTier=.*?;','',bootstrap);bootstrap=re.sub(r'bot_iFireTicks=\d+;','bot_iFireTicks=0;',bootstrap);bootstrap=re.sub(r'bot_fMoveFactor=[^;]+;','bot_fMoveFactor=0;',bootstrap);bootstrap=re.sub(r'bot_fYawSpeed=[^;]+;','bot_fYawSpeed=0;',bootstrap);bootstrap_cfg.write_text(bootstrap)
   launch('server');count(0);launch('botA');count(1)
   bootstrap_state=E/'bootstrap-control-state.json';bootstrap_state.write_text(json.dumps({'status':'OBSERVING','display':DISPLAY,'processes':{'vanilla':{'pid':records['botA']['identity'][0],'cwd':str(R/'botA')}}}))
   subprocess.run(['python3',str(BASE/'control-pause.py'),'--result',str(bootstrap_state),'--key','Pause','--seconds','.1'],check=True,timeout=15)
   B.wait(lambda:pauseprobe.read_pause(server[0],R/'server')['actual_pause']==1,5,'bootstrap normal pause not accepted')
   report['early_pause_native']=pauseprobe.read_pause(server[0],R/'server');emit('early_bootstrap_paused',snapshot=report['early_pause_native'])
   pre=subprocess.run(['nsenter','--target',str(server[0]),'--net','python3','/srv/tse-milestone-a-20261111/tools/external_vanilla_preflight.py','--observer-dir',str(R/'vanilla'),'--manifest',str(R/'retail-manifest.json'),'--server','127.0.0.1','--query-port',str(PORT+1),'--game-port',str(PORT),'--expected-player','Dev-1'],capture_output=True,text=True,timeout=25)
   (E/'preflight.json').write_text(pre.stdout);result=json.loads(pre.stdout);assert pre.returncode==0 and result['canStart'] and result['live']
   vanilla=launch('vanilla');count(2);(E/'control-state.json').write_text(json.dumps({'status':'OBSERVING','display':DISPLAY,'processes':{'vanilla':{'pid':vanilla[0],'cwd':str(R/'vanilla')}}}))
   # Inert bootstrap and unspawned observer preserve map items before barrier.
   close('botA');count(1)
   paused_samples=[]
   for i in range(6):
    paused_samples.append(probe.read(server[0],R/'server'));time.sleep(.3)
   report['pause_before_join']=paused_samples;report['pause_native_before_join']=pauseprobe.read_pause(server[0],R/'server')
   assert len({x['game_tick'] for x in paused_samples[-4:]})==1,'normal pause did not freeze game tick'
   emit('paused_barrier_verified',game_tick=paused_samples[-1]['game_tick'])
   bootstrap_cfg.write_bytes(bootstrap_original);cohort=True
   for physical in ('botA','botB'):
    candidate=(physical=='botA')==bool(SWAP)
    source=Path('/srv/tse-milestone-a-build-004-20261111' if candidate else '/srv/tse-cecil-full-build-048-20261109')/'Sources/Game/GameMP.dll'
    shutil.copy2(source,R/physical/'Bin/GameMP.dll');os.chown(R/physical/'Bin/GameMP.dll',65534,65534)
    cfg=R/physical/'Scripts/Integrated.ini';raw=cfg.read_text();raw=re.sub(r'\nbot_iArenaTier=.*?;','',raw);raw=re.sub(r'bot_bDiagnostics=\d+;',f'bot_bDiagnostics={DIAG if candidate else 0};',raw)
    for key in ('bot_bAutoCombat','bot_bHumanAI','bot_bSupplyNavigation'):raw=re.sub(key+r'=\d+;',key+'=1;',raw)
    if candidate:raw+=f'\nbot_iArenaTier={trial};\n'
    cfg.write_text(raw)
   configure_count(R/'botA',4);configure_count(R/'botB',4)
   order=('botA','botB')
   launch(order[0]);count(5);launch(order[1]);count(9)
   barrier={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}
   report['barrier_before_release']=barrier;report['native_pause_before_release']={role:pauseprobe.read_pause(rec['identity'][0],R/role)for role,rec in records.items()}
   assert len({x['game_tick'] for x in barrier.values()})==1,'paused peer ticks differ'
   assert barrier['server']['game_tick']==paused_samples[-1]['game_tick'],'game advanced while joining'
   control('key','Pause',.1)
   emit('released_barrier',server_tick_before=barrier['server']['game_tick'],player_entities_before=len(barrier['server']['players']))
   report['cohort_order']=order;report['cohort_config_sha256']={role:sha(R/role/'Scripts/Integrated.ini') for role in ('botA','botB')}
   def usage():
    values={}
    for role,rec in records.items():
     stat=(Path('/proc')/str(rec['identity'][0])/'stat').read_text().split(') ',1)[1].split();values[role]={'cpu_ticks':int(stat[11])+int(stat[12]),'rss_pages':int(stat[21])}
    return values
   report['usage_start']=usage();report['clock_ticks']=os.sysconf('SC_CLK_TCK');report['page_bytes']=os.sysconf('SC_PAGE_SIZE')
   start=time.monotonic();lastquery=-100;lastcontrol=0;lastemit=-100;queries=[]
   with (E/'session-health.jsonl').open('w') as stream:
    while time.monotonic()-start<duration:
     elapsed=time.monotonic()-start
     snapshots={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}
     assert all(x['spawn_value']==value for x in snapshots.values()),'actual session spawn differs'
     stream.write(json.dumps({'elapsed':elapsed,'roles':snapshots})+'\n');stream.flush()
     if elapsed-lastquery>=2:
      q=B.query(server[0]);assert q.get('numplayers')=='9' and q.get('mapname')=='Red Station';queries.append({'elapsed':elapsed,'query':q});lastquery=elapsed
     if elapsed-lastcontrol>=12:
      control('button',1,.4);control('key','Up',1);control('key','Left',.3);lastcontrol=elapsed
     if elapsed-lastemit>=30:
      emit('observing',elapsed=elapsed,spawn_values={k:v['spawn_value'] for k,v in snapshots.items()},players=[p['health'] for p in snapshots['server']['players']]);lastemit=elapsed
     time.sleep(.015 if elapsed<2 else .1)
   report['usage_end']=usage();(E/'queries.json').write_text(json.dumps(queries,indent=2));report['observed_seconds']=time.monotonic()-start
   sys.path.insert(0,'/srv/tse-milestone-a-20261111/tools');from analyze_sync_log import analyze
   checks={}
   for role in records:
    log=R/role/('Dedicated_BotTest.log' if role=='server' else 'SeriousSam.log');raw=log.read_text(errors='replace');shutil.copy2(log,E/(role+'.log'));a=analyze(raw);checks[role]={'bad':a['bad_events'],'disconnects':a['disconnect_events']};assert not re.search(r'SYNCBAD|Too many bad syncs|CRC check failed|Access violation|Fatal Error|Cannot join game:|\[CecilInvalidAction\]',raw,re.I)
   report['sync_checks']=checks;assert all(c['bad']==0 and c['disconnects']==0 for c in checks.values());report['status']='PASS_LIMITED_CONTROLLED_WINE_SESSION_FIELD_AND_POPULATION';emit('window_completed',seconds=report['observed_seconds'],checks=checks)
  except BaseException as error:
   report['status']='FAIL';report['errors'].append(repr(error));save();raise
  finally:
   if records.get('vanilla',{}).get('identity') and not records['vanilla']['closed']:
    try:
     before=probe.read(server[0],R/'server')['game_tick'];time.sleep(.4);after=probe.read(server[0],R/'server')['game_tick']
     if before==after:control('key','Pause',.1)
    except BaseException as error:report['errors'].append('unpause cleanup:'+repr(error))
   for role in ('vanilla','botB','botA','server'):
    rec=records.get(role)
    if rec:
     log=R/role/('Dedicated_BotTest.log' if role=='server' else 'SeriousSam.log')
     if log.exists():shutil.copy2(log,E/(role+'-final.log'))
    try:close(role)
    except BaseException as error:report['errors'].append('cleanup '+role+':'+repr(error))
   if display and all(r['closed'] for r in records.values()):
    assert B.same(display);os.kill(display[0],signal.SIGTERM);B.wait(lambda:not B.same(display),15,'display remains')
   if bootstrap_original is not None and all(r['closed'] for r in records.values()):bootstrap_cfg.write_bytes(bootstrap_original)
   report['cleanup']=records;report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
if __name__=='__main__':main(0,float(sys.argv[2]),int(sys.argv[1]))
