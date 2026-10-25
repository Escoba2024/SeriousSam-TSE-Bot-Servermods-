#!/usr/bin/env python3
"""Opt-in Hetzner Retail session qualification, never a production supervisor.

Reuses the qualified overlay/profile/WM_DELETE_WINDOW primitives and Human AI.
Default is read-only. --execute creates an isolated network namespace with only
loopback; the outer controller guards the existing public fleet and host reserve.
Raw profiles/logs/SQLite and screenshots must remain private on this host.
"""
import argparse
import ctypes
from dataclasses import replace
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import signal
import sqlite3
import socket
import subprocess
import sys
import tempfile
import time

from bot_sessions import Planner, validate_config, clean_name
from bot_session_runtime import ControllerLock, startup_script, guid_bytes
from bot_session_executor import SessionExecutor, player_names, process_record, probe_process
import qualify_integrated_wine as q

DLL = '7fc94a39c3f5d9516f262d9e4d04a5cf38e6eb5ae3482976c32c952a99d30835'
TEMPLATE = Path('/srv/tse-wine-runtime-20261020/public-eight-20261020-2140')
VANILLA = Path('/srv/tse-wine-runtime-20261020/install/vanilla')
MANIFEST = Path('/srv/tse-integrated-build-20261021-04/manifest.json')
PUBLIC = Path('/srv/tse-integration-public-20261021/eight-115115-z44oq5ua/result.json')


def resource_gate(*, available_mib, disk_free_gib, busy_percent, launch=False):
    return available_mib >= 768+(300 if launch else 0) and disk_free_gib >= 8 and busy_percent < 85


def arm_parent_death(parent_pid):
    def arm():
        libc=ctypes.CDLL(None,use_errno=True)
        if libc.prctl(1,signal.SIGTERM,0,0,0)!=0:
            raise OSError(ctypes.get_errno(),'PR_SET_PDEATHSIG')
        if os.getppid()!=parent_pid:os._exit(125)
    return arm


def host_cpu():
    return list(map(int, Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))


def busy_between(before, after):
    delta = [b-a for a,b in zip(before, after)]
    return 100*(sum(delta)-delta[3]-delta[4])/max(1,sum(delta))


def resources():
    mem = int(re.search(r'^MemAvailable:\s+(\d+)',Path('/proc/meminfo').read_text(),re.M)[1])/1024
    disk = shutil.disk_usage('/srv').free/1024**3
    return mem, disk


def isolated_network():
    # sysfs belongs to the mount namespace and may still list host interfaces.
    # if_nameindex queries the current network namespace through the kernel.
    return (os.readlink('/proc/self/ns/net') != os.readlink('/proc/1/ns/net') and
            {name for _,name in socket.if_nameindex()} == {'lo'})


def runtime_error(log):
    return re.search(q.BAD.pattern + r'|FatalError:', log)


def validate_native_config(config):
    if not config['enabled']:
        raise ValueError('explicitly enabled private session config required')
    if any(i['id'] in {'server','vanilla','home','layers','history'} or i['id'].startswith('prefix-')
           for i in config['identities']):
        raise ValueError('identity ID collides with private resource names')


def observer_symbols(source):
    for name,value in [('sam_bFullScreen',0),('sam_iScreenSizeI',640),('sam_iScreenSizeJ',480),
                       ('sam_iMaxFPSActive',5),('sam_iMaxFPSInactive',5)]:
        source,count=re.subn(r'('+name+r'=\(INDEX\))\d+;',lambda m:m[1]+str(value)+';',source)
        if count!=1:raise ValueError('unrecognized original observer settings')
    return source


def low_memory_symbols(source):
    """Graphics quality only, for private null-render clients. No gameplay knobs."""
    for name,value in [('tex_iNormalSize',6),('tex_iAnimationSize',5),('tex_iEffectSize',5),
                       ('shd_iStaticSize',5),('shd_iDynamicSize',5)]:
        source,count=re.subn(r'('+name+r'=\(INDEX\))\d+;',lambda m:m[1]+str(value)+';',source)
        if count!=1:raise ValueError('unrecognized native texture/shadow settings')
    return source


def runtime_log_gate(transport):
    paths=[game/('Dedicated_BotTest.log' if role=='server' else 'SeriousSam.log')
           for role,game in transport.roles.items()]
    paths+=list((transport.root/'history').glob('*/SeriousSam.log'))
    for path in paths:
        if not path.exists():continue
        if path.stat().st_size>transport.p.config['max_log_mib']*1024**2:raise RuntimeError('private log limit')
        match=runtime_error(q.text(path))
        if match:raise RuntimeError(path.parent.name+' native failure: '+match.group())


def valid_action_report(report):
    return (report.get('verdict')=='ACTIVE_OK' and report.get('lp_median')==1 and
            18<=report.get('tick_hz_median',0)<=22 and report.get('render_skip_total',0)>0 and
            report.get('render_draw_total')==0 and report.get('config',{}).get('nullrender')=='1')


def telemetry_windows(transport, events):
    """Measure only journal-confirmed playing intervals, retaining bad rows."""
    summaries={}
    for ident in transport.identities:
        recordings=[]
        for path in [transport.roles[ident]/'Bin/BotTelemetry.csv']+list(
                (transport.root/'history').glob(ident+'-*/BotTelemetry.csv')):
            if path.exists():recordings.append(q.bt.parse(path.read_text()))
        windows=[]
        for joined in [e for e in events if e['id']==ident and e['event']=='joined']:
            stop=next((e['at'] for e in events if e['id']==ident and e['epoch']==joined['epoch'] and
                       e['event'] in ('leave_requested','crashed','disconnected')),None)
            if stop is None:raise RuntimeError('playing interval was not drained')
            exited=transport.p.db.execute('SELECT observed_at FROM runtime_exit_seen WHERE identity_id=? AND epoch=?',
                                         (ident,joined['epoch'])).fetchone()
            if exited and exited[0] is not None:stop=min(stop,exited[0])
            reports=[]
            for recording in recordings:
                rows=[row for row in recording.rows if
                      (joined['at']+2)*1000<=row.t_ms<=(stop-1)*1000]
                if not rows:continue
                report=q.bt.analyze(replace(recording,rows=rows),expect_bots=1,expect_nullrender=1)
                if not valid_action_report(report):raise RuntimeError(ident+' action telemetry/count/null-render gate')
                reports.append(report)
            if stop-joined['at']>=8 and not reports:raise RuntimeError('missing session telemetry')
            windows.append(dict(epoch=joined['epoch'],playing_s=stop-joined['at'],reports=reports))
        if not any(w['reports'] for w in windows):raise RuntimeError(ident+' has no measured active interval')
        summaries[ident]=windows
    return summaries


def stop_owned(record, process=None, *, allow_force=False):
    """Fallback teardown only; normal session leave uses the window protocol."""
    if probe_process(record) == 'ABSENT':
        if process is not None: process.poll()
        return False
    fd = os.pidfd_open(record['pid'])
    try:
        if probe_process(record) != 'LIVE':
            raise RuntimeError('refuse teardown: process ownership changed')
        signal.pidfd_send_signal(fd, signal.SIGTERM)
        deadline=time.monotonic()+10
        while probe_process(record)=='LIVE' and time.monotonic()<deadline:
            if process is not None:process.poll()
            time.sleep(.1)
        if probe_process(record)=='LIVE':
            if not allow_force:raise RuntimeError('own process did not terminate')
            signal.pidfd_send_signal(fd,signal.SIGKILL)
        if process is not None:process.wait(timeout=10)
        return True
    finally:os.close(fd)


class WineTransport:
    """Private one-player clients. Durable bindings allow executor re-adoption."""
    def __init__(self, root, planner, port, display, cgroup, *, color_probe=False):
        self.root, self.p, self.port, self.display = root, planner, port, display
        self.cgroup=cgroup
        self.color_probe=color_probe
        self.roles={}
        self.procs={}
        self.launched={}
        self.fixed={}
        self.absence={}
        self.query=None
        self.query_valid=False
        self.invalid_since=None
        self.query_at=0
        self.mounts=[]
        self.events=[]
        self.p.db.execute('CREATE TABLE IF NOT EXISTS native_process '
                          '(id TEXT PRIMARY KEY, epoch INTEGER, record TEXT, '
                          'profile_sha TEXT, guid_sha TEXT)')
        self.common=dict(os.environ,HOME=str(root/'home'),WINEARCH='win32',WINEDEBUG='-all',
                         DISPLAY=display,LIBGL_ALWAYS_SOFTWARE='1',GALLIUM_DRIVER='llvmpipe',
                         LP_NUM_THREADS='1',XDG_CACHE_HOME=str(root/'home/cache'))

    def overlay(self, source, role):
        layer=self.root/'layers'/role
        layer.mkdir(parents=True)
        for name in ('upper','work'):(layer/name).mkdir()
        target=self.root/role;target.mkdir()
        subprocess.run(['mount','-t','overlay','overlay','-o',
                        f'lowerdir={source.resolve()},upperdir={layer}/upper,workdir={layer}/work',
                        str(target)],check=True,capture_output=True)
        self.mounts.append(target)
        os.chown(target,65534,65534)
        return target

    def prepare(self):
        home=self.root/'home';home.mkdir();os.chown(home,65534,65534)
        build=json.loads(MANIFEST.read_text());dll=Path(build['candidate'])
        if q.sha(dll)!=DLL:raise RuntimeError('Build04 hash drift')
        self.identities={i['id']:i for i in self.p.identities()}
        for role in ['server','vanilla']+list(self.identities):
            source=VANILLA if role=='vanilla' else TEMPLATE/('server' if role=='server' else 'botA')
            game=self.overlay(source,role);self.roles[role]=game
            self.overlay(TEMPLATE/('prefix-server' if role=='server' else 'prefix-botA'),'prefix-'+role)
            for name,digest in q.PINS.items():
                if name=='GameMP.dll' and role in self.identities:continue
                if q.sha(game/'Bin'/name)!=digest:raise RuntimeError('Retail original hash drift')
            if role in self.identities:
                shutil.copy2(dll,game/'Bin/GameMP.dll')
                q.change_profile_identity(game,self.identities[role],color_probe=self.color_probe,
                                          colors_enabled=self.p.config['colors_enabled'])
                q.configure_count(game,1)
                if self.p.config['low_memory_rendering']:
                    symbols=game/'Scripts/PersistentSymbols.ini'
                    symbols.write_text(low_memory_symbols(symbols.read_text()))
                script=(Path(__file__).resolve().parents[1]/'poc/scripts/Phase1HumanAI.ini').read_text()
                script+='\nbot_bNullRender=1;\nbot_iNullRenderFps=20;\nbot_iTelemetry=1;\nbot_iLogEvery=20;\nbot_bDiagnostics=0;\nbot_bDiag=1;\nsam_iMaxFPSActive=20;\nsam_iMaxFPSInactive=10;\nsam_bPauseOnMinimize=0;\nnet_strLocalHost="";\n'
                script+=f"\nbot_iLogEvery={self.p.config['log_every_ticks']};\nbot_bDiag={int(self.p.config['debug_logging'])};\n"
                script+=startup_script(self.identities[role])
                (game/'Scripts/Session.ini').write_text(script)
                os.chown(game/'Scripts/Session.ini',65534,65534)
            elif role=='server':
                path=game/'Scripts/Dedicated_startup.ini'
                path.write_text(q.dedicated_script(q.text(path),'127.0.0.1',self.port,False)+
                                '\nser_bReportSyncOK=1;\n')
            else:
                q.configure_count(game,1)
                q.change_profile(game/'Players/Player0.plr','Retail_Control')
                symbols=game/'Scripts/PersistentSymbols.ini'
                symbols.write_text(observer_symbols(symbols.read_text()))
                # This is a stationary original-client observer, not a human
                # gameplay/UX benchmark. Cap its software renderer on this host.
                (game/'Scripts/Session.ini').write_text('sam_iMaxFPSActive=5;\nsam_iMaxFPSInactive=5;\nsam_bPauseOnMinimize=0;\n')
                os.chown(game/'Scripts/Session.ini',65534,65534)
            for name in ('Dedicated_BotTest.log','SeriousSam.log','Bin/BotTelemetry.csv'):
                path=game/name
                if path.exists():path.unlink()

    def start(self, role, epoch=0):
        game=self.roles[role]
        prefix=self.root/('prefix-'+role)
        # Archives preserve previous incarnations, including telemetry and Wine logs.
        archive=self.root/'history'/f'{role}-{epoch}'
        for path in (game/'SeriousSam.log',game/'Bin/BotTelemetry.csv',self.root/(role+'-wine.log')):
            if path.exists():
                archive.mkdir(parents=True,exist_ok=True)
                shutil.move(str(path),str(archive/path.name))
        cmd=['wine','Bin/DedicatedServer.exe','BotTest'] if role=='server' else [
            'wine','Bin/SeriousSam.exe','+connect',f'127.0.0.1:{self.port}',
            '+quickjoin','+script','Scripts\\Session.ini']
        def demote():os.setgid(65534);os.setuid(65534)
        with (self.root/(role+'-wine.log')).open('ab') as out:
            proc=subprocess.Popen(cmd,cwd=game,env=dict(self.common,WINEPREFIX=str(prefix)),
                                  stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,
                                  preexec_fn=demote,start_new_session=True)
        self.procs[role]=proc
        record=process_record(proc.pid)
        self.launched[role]=record
        if record['cwd']!=str(game) or record['uid']!=65534 or record['cgroup']!=self.cgroup:
            raise RuntimeError('new process failed ownership binding')
        if role in self.identities:
            self.p.db.execute('INSERT OR REPLACE INTO native_process VALUES (?,?,?,?,?)',
                              (role,epoch,json.dumps(record),q.sha(game/'Players/Player0.plr'),
                               q.sha(game/'Players/Player0.plr.guid')))
        else:self.fixed[role]=record
        return record

    def snapshot(self, now):
        try:
            self.query=q.query(self.port+1)
            names=player_names(self.query)
        except (OSError,RuntimeError,ValueError) as exc:
            self.query_valid=False
            self.absence.clear()
            if self.invalid_since is None:self.invalid_since=now
            with (self.root/'query-uncertain.jsonl').open('a') as out:
                out.write(json.dumps(dict(at=now,error=str(exc),query=self.query))+'\n')
            if now-self.invalid_since>15:raise RuntimeError('query uncertain for more than 15 seconds') from exc
            return None
        self.query_valid=True
        self.invalid_since=None
        self.query_at=now
        for record in self.fixed.values():
            if probe_process(record)!='LIVE':raise RuntimeError('server/original client exited')
        keys={clean_name(n).casefold() for n in names}
        self.current_names=keys
        configured={who['nickname'].casefold() for who in self.identities.values()}
        # Other players never acquire an owned identity from their nickname alone.
        self.humans=[name for name in names if clean_name(name).casefold() not in configured]
        if self.humans not in ([],['Retail_Control']):
            raise RuntimeError('unknown player in isolated namespace; hold')
        return dict(observed_at=now,maxplayers=int(self.query['maxplayers']),human_names=self.humans)

    def observe(self, state, identity, now):
        if not self.query_valid:
            return dict(identity_id=state['id'],epoch=state['epoch'],ownership_verified=False,
                        fresh_query=False,process_alive=False,connected=False,ghost=False,
                        unknown_peers=False,human_conflict=False)
        row=self.p.db.execute('SELECT * FROM native_process WHERE id=?',(state['id'],)).fetchone()
        record=json.loads(row['record']) if row else None
        if state['id'] in self.procs:self.procs[state['id']].poll()
        status=probe_process(record) if record else 'ABSENT'
        bound=not row or (row['epoch']==state['epoch'] and
              row['profile_sha']==q.sha(self.roles[state['id']]/'Players/Player0.plr') and
              row['guid_sha']==q.sha(self.roles[state['id']]/'Players/Player0.plr.guid'))
        # A previous, confirmed absent epoch may precede a new launch.
        if row and row['epoch']<state['epoch'] and status=='ABSENT':bound=True
        if record and row['epoch']==state['epoch']:
            bound = bound and (record['cwd']==str(self.roles[state['id']]) and
                               record['uid']==65534 and record['cgroup']==self.cgroup)
        bound = bound and (self.roles[state['id']]/'Players/Player0.plr.guid').read_bytes()==guid_bytes(identity)
        connected=identity['nickname'].casefold() in self.current_names
        key=(state['id'],state['epoch'])
        absent=status=='ABSENT' and not connected
        self.absence[key]=self.absence.get(key,0)+1 if absent else 0
        if row and status=='LIVE' and row['epoch']!=state['epoch']:bound=False
        logs=q.text(self.roles[state['id']]/'SeriousSam.log')
        native_join='joined' in logs
        return dict(identity_id=state['id'],epoch=state['epoch'],ownership_verified=bound and status!='MISMATCH',
                    fresh_query=0<=now-self.query_at<=5,process_alive=status=='LIVE',
                    connected=connected and native_join,
                    ghost=connected and status!='LIVE',unknown_peers=False,human_conflict=False,
                    owned_exit=bool(row and row['epoch']==state['epoch'] and status=='ABSENT' and bound),
                    verified_absence=self.absence[key]>=3,
                    query_absence_confirmed=self.absence[key]>=3,
                    exit_confirmed=self.absence[key]>=3)

    def launch(self,state,identity):
        if identity['nickname'].casefold() in self.current_names:
            raise RuntimeError('duplicate name or ghost before spawn')
        mem,disk=resources()
        if not resource_gate(available_mib=mem,disk_free_gib=disk,busy_percent=0,launch=True):
            raise RuntimeError(f'HOST_RESOURCE_RESERVE_FOR_NEXT_CLIENT: available_mib={mem:.1f}, required=1068, disk_gib={disk:.2f}')
        record=self.start(state['id'],state['epoch'])
        self.events.append(dict(at=time.time(),event='spawn',id=state['id'],epoch=state['epoch'],record=record))

    def leave(self,state,identity):
        row=self.p.db.execute('SELECT epoch,record FROM native_process WHERE id=?',(state['id'],)).fetchone()
        if not row or row['epoch']!=state['epoch']:raise RuntimeError('wrong leave epoch')
        record=json.loads(row['record'])
        if probe_process(record)!='LIVE':raise RuntimeError('wrong leave process')
        sent=q.close_window(record['pid'],self.display)
        if not sent:raise RuntimeError('own client has no orderly close window')
        self.events.append(dict(at=time.time(),event='WM_DELETE_WINDOW',id=state['id'],epoch=state['epoch'],sent=sent))

    def cleanup(self):
        results=[]
        rows={r['id']:json.loads(r['record']) for r in self.p.db.execute('SELECT * FROM native_process')}
        rows.update(self.launched)
        rows.update(self.fixed)
        foreign=set()
        for role,record in reversed(list(rows.items())):
            forced=False;sent=0;errors=[]
            try:
                status=probe_process(record)
                if status=='LIVE':
                    if role!='server':
                        try:
                            sent=q.close_window(record['pid'],self.display)
                            deadline=time.monotonic()+20
                            while probe_process(record)=='LIVE' and time.monotonic()<deadline:
                                if role in self.procs:self.procs[role].poll()
                                time.sleep(.2)
                        except Exception as exc:errors.append('window close: '+str(exc))
                    if probe_process(record)=='LIVE':forced=stop_owned(record,self.procs.get(role),allow_force=True)
                elif status!='ABSENT':
                    foreign.add(role)
                    errors.append('foreign process on cleanup; no signal sent')
            except Exception as exc:
                foreign.add(role)
                errors.append('process teardown: '+str(exc))
            results.append(dict(role=role,close_sent=sent,signal_fallback=forced,errors=errors))
        # Prefix paths are mounts created and tracked exclusively in this run.
        for role in self.roles:
            if role in foreign:continue
            prefix=self.root/('prefix-'+role)
            errors=[]
            for option in ('-k','-w'):
                try:
                    done=subprocess.run(['runuser','-u','nobody','--','env',f'WINEPREFIX={prefix}',
                                         'wineserver',option],capture_output=True,timeout=15)
                    # No server to signal is allowed; -w must still confirm exit.
                    # Store -k failures privately for diagnostics, not as proof of
                    # a live process when the subsequent wait succeeds.
                    if done.returncode and option=='-w':errors.append('wineserver wait exit '+str(done.returncode))
                    if done.returncode:
                        with (self.root/'prefix-cleanup.jsonl').open('a') as out:
                            out.write(json.dumps(dict(role=role,option=option,exitcode=done.returncode,
                                stderr=done.stderr.decode(errors='replace') if isinstance(done.stderr,bytes) else done.stderr))+'\n')
                except Exception as exc:errors.append('prefix teardown: '+str(exc))
            if errors:results.append(dict(role='prefix-'+role,errors=errors))
        return results


def run_inner(args, config, root):
    if os.readlink('/proc/self/ns/net')==os.readlink('/proc/1/ns/net'):
        raise RuntimeError('private network namespace required')
    subprocess.run(['ip','link','set','lo','up'],check=True)
    if not isolated_network():raise RuntimeError('isolated loopback only required')
    cg=Path('/sys/fs/cgroup')/('tse-sessions-'+str(os.getpid()))
    cg.mkdir();(cg/'cpu.max').write_text('max 100000');(cg/'cgroup.procs').write_text(str(os.getpid()))
    def cgstat():return {k:int(v) for k,v in (line.split() for line in (cg/'cpu.stat').read_text().splitlines())}
    cgstart=cgstat();cgtime=time.monotonic()
    cgroup=Path('/proc/self/cgroup').read_text()
    p=Planner(root/'sessions.db',config)
    transport=WineTransport(root,p,args.port,args.display,cgroup,color_probe=args.color_probe)
    result=dict(status='PREPARING',scope='ISOLATED_NETNS_RETAIL_WINE',dll_sha256=DLL,
                max_bots=config['max_bots'],accelerated=config['accelerated'],cgroup=str(cg),
                original_client=True,colors_enabled=config['colors_enabled'],private_color_probe=args.color_probe,
                low_memory_rendering=config['low_memory_rendering'],
                observer_fps_cap=5,network_namespace=os.readlink('/proc/self/ns/net'))
    def save():
        result['utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
        (root/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    def interrupted(*_):raise KeyboardInterrupt('outer guard stopped test')
    signal.signal(signal.SIGTERM,interrupted)
    xvfb=None;started=None;peak=0
    try:
        transport.prepare()
        with (root/'xvfb.log').open('wb') as out:
            xvfb=subprocess.Popen(['Xvfb',args.display,'-screen','0','640x480x24','-nolisten','tcp','-noreset'],
                                  stdout=out,stderr=subprocess.STDOUT)
        time.sleep(2)
        if xvfb.poll() is not None:raise RuntimeError('display already occupied')
        transport.start('server');time.sleep(8);transport.start('vanilla')
        deadline=time.monotonic()+120
        while True:
            for role in ('server','vanilla'):
                path=transport.roles[role]/('Dedicated_BotTest.log' if role=='server' else 'SeriousSam.log')
                match=runtime_error(q.text(path))
                if match:raise RuntimeError(role+' startup failure: '+match.group())
            try:
                state=q.query(args.port+1)
                if player_names(state)==['Retail_Control']:break
            except (OSError,ValueError,RuntimeError):pass
            if time.monotonic()>deadline:raise RuntimeError('original Retail join timeout')
            time.sleep(2)
        started=time.monotonic();last_reopen=started
        result['status']='MEASURING';save()
        peak=0;samples=0;reopens=0
        with (root/'samples.jsonl').open('w') as out, ControllerLock(root/'sessions.db') as lock:
            executor=SessionExecutor(p,lock,transport)
            while time.monotonic()-started<args.duration:
                now=time.time()
                decisions=executor.tick(config['servers'][0],now)
                active=sum(s['status']=='PLAYING' for s in p.states().values());peak=max(peak,active)
                runtime_log_gate(transport)
                for state in p.states().values():
                    if state['status']=='JOINING':
                        at=p.db.execute("SELECT at FROM event WHERE id=? AND epoch=? AND event='join_requested'",
                                        (state['id'],state['epoch'])).fetchone()[0]
                        if now-at>120:raise RuntimeError('bounded join timeout')
                    if state['status']=='LEAVING':
                        row=p.db.execute('SELECT at FROM runtime_leave_claim WHERE identity_id=? AND epoch=?',
                                         (state['id'],state['epoch'])).fetchone()
                        if row and now-row[0]>45:raise RuntimeError('bounded orderly leave timeout')
                out.write(json.dumps(dict(elapsed_s=time.monotonic()-started,active=active,
                                          population=len(transport.current_names),decisions=decisions))+'\n');out.flush()
                samples+=1
                if time.monotonic()-last_reopen>120:
                    # Reopen the real DB/executor while every native process stays running.
                    p.close();p=Planner(root/'sessions.db',config);transport.p=p
                    executor=SessionExecutor(p,lock,transport)
                    reopens+=1;last_reopen=time.monotonic()
                if samples%10==0:
                    result.update(elapsed_s=time.monotonic()-started,samples=samples,peak_playing=peak)
                    save()
                time.sleep(1)
            # Admin-halt is persistent and produces individually rate-limited leaves.
            p.set_enabled(config['servers'][0],False,time.time())
            deadline=time.monotonic()+120+config['leave_interval_s']*config['max_bots']
            while any(s['status'] in ('JOINING','PLAYING','LEAVING') for s in p.states().values()):
                executor.tick(config['servers'][0],time.time())
                runtime_log_gate(transport)
                if time.monotonic()>deadline:raise RuntimeError('admin drain timeout')
                time.sleep(1)
            events=[dict(r) for r in p.db.execute('SELECT * FROM event')]
            result.update(status='PASS_LIMITED_SESSION_LIFECYCLE',elapsed_s=time.monotonic()-started,
                          measured_s=args.duration,samples=samples,peak_playing=peak,
                          controller_db_reopens=reopens,events=events,
                          process_events=transport.events,all_bots_drained=True,
                          guid_sidecars={i:q.sha(transport.roles[i]/'Players/Player0.plr.guid') for i in transport.identities})
            if peak!=config['max_bots']:raise RuntimeError('did not reach requested simultaneous bots')
            for ident in transport.identities:
                if not any(e['id']==ident and e['event']=='joined' for e in events):
                    raise RuntimeError('identity never joined')
            result['telemetry']=telemetry_windows(transport,events)
            runtime_log_gate(transport)
            cgend=cgstat()
            result['new_throttled_periods']=cgend['nr_throttled']-cgstart['nr_throttled']
            result['cgroup_cpu_core_percent']=(cgend['usage_usec']-cgstart['usage_usec'])/1e4/(time.monotonic()-cgtime)
            result['cgroup_peak_mib']=int((cg/'memory.peak').read_text())/1024**2
            if result['new_throttled_periods']:raise RuntimeError('private cgroup throttled')
        save()
    except BaseException as exc:
        mem,disk=resources()
        result.update(status='FAIL',error=str(exc) or type(exc).__name__,peak_playing=peak,
                      elapsed_s=time.monotonic()-started if started is not None else 0,
                      failure_resources=dict(available_mib=mem,disk_free_gib=disk,
                          cgroup_peak_mib=int((cg/'memory.peak').read_text())/1024**2))
        save()
        raise
    finally:
        cleanup_errors=[]
        try:
            result['cleanup']=transport.cleanup()
            cleanup_errors += [e for row in result['cleanup'] for e in row.get('errors',[])]
        except Exception as exc:cleanup_errors.append('cleanup: '+str(exc))
        finally:
            try:
                if xvfb is not None and xvfb.poll() is None:xvfb.terminate();xvfb.wait(timeout=10)
            except Exception as exc:cleanup_errors.append('display teardown: '+str(exc))
            try:runtime_log_gate(transport)
            except Exception as exc:cleanup_errors.append('final native log gate: '+str(exc))
            result['unmounts']=[]
            for mount in reversed(transport.mounts):
                try:
                    done=subprocess.run(['umount',str(mount)],capture_output=True,text=True,timeout=15)
                    result['unmounts'].append(dict(path=str(mount),exitcode=done.returncode))
                    if done.returncode:cleanup_errors.append('unmount failed: '+str(mount))
                except Exception as exc:cleanup_errors.append('unmount: '+str(exc))
            if cleanup_errors:result.update(status='FAIL',cleanup_errors=cleanup_errors)
            save();p.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--runtime',type=Path,required=True)
    parser.add_argument('--duration',type=int,required=True)
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--color-probe',action='store_true',help='private native markup probe only; production colors stay gated')
    parser.add_argument('--inner',action='store_true',help=argparse.SUPPRESS)
    parser.add_argument('--port',type=int,default=27080)
    parser.add_argument('--display',default=':137')
    args=parser.parse_args()
    config=validate_config(json.loads(args.config.read_text()))
    if len(config['servers'])!=1 or not 1<=config['max_bots']<=8 or len(config['identities'])!=config['max_bots']:
        raise ValueError('one isolated server and 1..8 identities required')
    if not 10<=args.duration<=14400:raise ValueError('duration must be 10..14400 seconds')
    if not args.execute:
        print(json.dumps(dict(status='DRY_RUN_NO_RUNTIME',identities=len(config['identities']))));return
    validate_native_config(config)
    root=args.runtime.resolve()
    if (os.uname().nodename!='ubuntu-4gb-nbg1-2' or os.geteuid()!=0 or
        root.parent!=Path('/srv') or not root.name.startswith('tse-session-qualification-') or
        not 27000<=args.port<=27998 or not re.fullmatch(r':1[3-9][0-9]',args.display)):
        raise RuntimeError('refuse non-private host/path/port/display')
    if args.inner:
        run_inner(args,config,root);return
    # Serialize all session qualifications on this small shared host, even when
    # they use different private runtime directories and network namespaces.
    global_lock=os.fdopen(os.open('/srv/tse-session-qualification.lock',
                                 os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,0o600),'w')
    fcntl.flock(global_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    if root.exists():raise RuntimeError('fresh runtime directory required; never overwrite/adopt unknown run')
    before=json.loads(PUBLIC.read_text())
    public_records={role:process_record(info['pid']) for role,info in before['processes'].items()}
    for role,record in public_records.items():
        if record['cwd']!=before['processes'][role]['cwd'] or record['start_ticks']!=before['processes'][role]['start_ticks']:
            raise RuntimeError('public process baseline changed')
    health=json.loads(Path('/srv/tse-public-health-20261021/health.json').read_text())
    if (health.get('owned_sync_bad')!=0 or not health.get('query_fresh') or
        not health.get('processes_verified') or not health.get('telemetry_fresh')):
        raise RuntimeError('public fleet unhealthy before test')
    expected={n.casefold() for n in q.ROSTER}
    def public_guard():
        if any(probe_process(r)!='LIVE' for r in public_records.values()):raise RuntimeError('public process changed')
        names=player_names(q.query(25601))
        if not expected.issubset({clean_name(n).casefold() for n in names}):raise RuntimeError('public bot disappeared')
        live=json.loads(Path('/srv/tse-public-health-20261021/health.json').read_text())
        if (live.get('owned_sync_bad')!=0 or not live.get('telemetry_fresh') or
            not live.get('query_fresh') or not live.get('processes_verified')):
            raise RuntimeError('public telemetry/sync guard')
    public_guard()
    cpu_before=host_cpu();time.sleep(2);busy=busy_between(cpu_before,host_cpu())
    mem,disk=resources()
    if not resource_gate(available_mib=mem,disk_free_gib=disk,busy_percent=busy):
        raise RuntimeError('insufficient host reserve before qualification')
    root.mkdir(mode=0o755)
    (root/'source-sha256.json').write_text(json.dumps({name:q.sha(Path(__file__).parent/name)
        for name in ('qualify_bot_sessions.py','bot_session_executor.py','bot_session_runtime.py',
                     'bot_sessions.py','qualify_integrated_wine.py')},indent=2))
    with (root/'runtime.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        cmd=['unshare','--net','--',sys.executable,str(Path(__file__).resolve())]+sys.argv[1:]+['--inner']
        with (root/'native.log').open('w') as out:
            child=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,
                                   preexec_fn=arm_parent_death(os.getpid()))
        samples=[];error=None;lastcpu=host_cpu();overload=0
        try:
            while child.poll() is None:
                time.sleep(5)
                current=host_cpu();busy=busy_between(lastcpu,current);lastcpu=current
                mem,disk=resources();public_guard()
                samples.append(dict(at=time.time(),host_busy_percent=busy,available_mib=mem,disk_free_gib=disk))
                (root/'host-guard.json').write_text(json.dumps(dict(status='MONITORING',samples=samples)))
                overload=overload+1 if busy>=85 else 0
                if mem<768 or disk<8 or overload>=3:raise RuntimeError('host reserve gate; stop only own test')
        except BaseException as exc:
            error=str(exc) or type(exc).__name__
            if child.poll() is None:child.send_signal(signal.SIGTERM)
        finally:
            child.wait(timeout=180)
            public_guard()
            (root/'host-guard.json').write_text(json.dumps(dict(status='STOPPED_GUARD' if error else 'FINISHED',
                error=error,child_exitcode=child.returncode,samples=samples,public_processes_unchanged=True),indent=2))
        report=json.loads((root/'result.json').read_text())
        if error or child.returncode or not report['status'].startswith('PASS_'):
            raise RuntimeError(error or 'native child/cleanup failed; see private result.json/native.log')


if __name__=='__main__':main()
